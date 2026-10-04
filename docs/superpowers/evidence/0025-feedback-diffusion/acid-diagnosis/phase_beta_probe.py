import sys,json,os
from pathlib import Path
import cv2,numpy as np
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE))
import measure as m
m.EVIDENCE=Path(__file__).resolve().parent;m.SCRATCH=m.REPO/"build/diffusion/acid-diagnosis"
worker="phase-beta-p1"
w,h=map(int,sys.argv[1].split("x"));ref=(0,0) if h==665 else (1024,768);seconds=int(sys.argv[2]) if len(sys.argv)>2 else 12
label=f"phase-beta-p1-{h}-{seconds}s";log=m.EVIDENCE/(label+"-routing.csv");log.unlink(missing_ok=True);os.environ["PROJECTM_RAW_ROUTE_LOG"]=str(log)
r=m.measure("acid-diagnosis-phase-beta.milk",worker,w,h,ref,seconds=seconds,preset_root=m.EVIDENCE)
reference=json.loads((BASE/f"noise-corrected-expanded-{seconds}s-report.json").read_text())["presets"]["Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk"]["runs"]["authored"]
r["luma_ratio"]=r["luma"]/reference["luma"];r["img_err"]=float(np.mean([np.abs(cv2.imread(str(Path(r["output"])/f"frame-{i}.png")).astype(np.float32)-cv2.imread(str(Path(reference["output"])/f"frame-{i}.png")).astype(np.float32)).mean()/255 for i in range(5)]))
if h==665:
 original=json.loads((Path(reference["output"])/"metrics.json").read_text());r["authored_byte_identical"]=r["frame_hashes"]==original["frame_hashes"];assert r["authored_byte_identical"]
r["routing_checked"]=log.exists() and len(log.read_text().splitlines())>=4;r["shader_compile_success"]="Successfully compiled warp shader" in Path(r["diagnostics"]).read_text();assert r["routing_checked"] and r["shader_compile_success"]
(m.EVIDENCE/(label+".json")).write_text(json.dumps(r,indent=2)+"\n");print({k:r[k] for k in ["status","img_err","luma_ratio","centre_rgb","routing_checked","shader_compile_success","authored_byte_identical"] if k in r},flush=True);assert r["status"]=="success"
