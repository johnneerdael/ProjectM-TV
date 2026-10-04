import sys,json,os
from pathlib import Path
import cv2,numpy as np
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE))
import measure as m
m.EVIDENCE=Path(__file__).resolve().parent;m.SCRATCH=m.REPO/"build/diffusion/acid-diagnosis"
repeat=int(sys.argv[3]) if len(sys.argv)>3 else 0
label=sys.argv[1];w,h=map(int,sys.argv[2].split("x"));ref=(0,0) if h==665 else (1024,768)
info={"fed":("Fed - quadratrail.milk","noise-corrected-expanded-12s-report.json"),"royal":("$$$ Royal - Mashup (191).milk","set24-corrected-12s-report.json")}
name,report=info[label];target=f"phase-beta-{label}-{h}-12s";log=m.EVIDENCE/(target+"-routing.csv");log.unlink(missing_ok=True);os.environ["PROJECTM_RAW_ROUTE_LOG"]=str(log)
r=m.measure(f"{label}-diagnosis-phase-beta.milk","phase-beta-p1",w,h,ref,seconds=12,repeat=repeat,preset_root=m.EVIDENCE)
reference=json.loads((BASE/report).read_text())["presets"][name]["runs"]["authored"]
r["original"]=name;r["luma_ratio"]=r["luma"]/reference["luma"];r["img_err"]=float(np.mean([np.abs(cv2.imread(str(Path(r["output"])/f"frame-{i}.png")).astype(np.float32)-cv2.imread(str(Path(reference["output"])/f"frame-{i}.png")).astype(np.float32)).mean()/255 for i in range(5)]))
if h==665:
 original=json.loads((Path(reference["output"])/"metrics.json").read_text());r["authored_byte_identical"]=r["frame_hashes"]==original["frame_hashes"];r["strict_F1_pass"]=r["authored_byte_identical"]
r["routing_checked"]=log.exists() and len(log.read_text().splitlines())>=2;r["shader_compile_success"]="Successfully compiled warp shader" in Path(r["diagnostics"]).read_text();assert r["routing_checked"] and r["shader_compile_success"]
(m.EVIDENCE/(target+".json")).write_text(json.dumps(r,indent=2)+"\n");print({k:r[k] for k in ["status","img_err","luma_ratio","centre_rgb","routing_checked","shader_compile_success","authored_byte_identical"] if k in r},flush=True);assert r["status"]=="success"
