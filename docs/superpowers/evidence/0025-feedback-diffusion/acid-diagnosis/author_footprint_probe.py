import sys,json,os
from pathlib import Path
import cv2,numpy as np
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE))
import measure as m
m.EVIDENCE=Path(__file__).resolve().parent;m.SCRATCH=m.REPO/"build/diffusion/acid-diagnosis"
seconds=int(sys.argv[1]);w,h=map(int,sys.argv[2].split("x"));control=len(sys.argv)>3 and sys.argv[3]=="control"
ref=(0,0) if h==665 and not control else (1024,768)
label=f"author-footprint-v3-{h}-{seconds}s"+("-control" if control else "")
log=m.EVIDENCE/(label+".csv");os.environ["PROJECTM_ACID_DIAG_LOG"]=str(log);os.environ["PROJECTM_ACID_DIAG_GRID"]="256"
for p in [log,Path(str(log)+".weighted")]:p.unlink(missing_ok=True)
preset="acid-diagnosis-author-footprint-v3.milk"
r=m.measure(preset,"author-footprint-v2",w,h,ref,seconds=seconds,preset_root=m.EVIDENCE)
reference=json.loads((BASE/f"noise-corrected-expanded-{seconds}s-report.json").read_text())["presets"]["Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk"]["runs"]["authored"]
original=json.loads((Path(reference["output"])/"metrics.json").read_text())
r["luma_ratio"]=r["luma"]/reference["luma"]
r["img_err"]=float(np.mean([np.abs(cv2.imread(str(Path(r["output"])/f"frame-{i}.png")).astype(np.float32)-cv2.imread(str(Path(reference["output"])/f"frame-{i}.png")).astype(np.float32)).mean()/255 for i in range(5)]))
if control:
 c=m.measure(preset,"baseline",w,h,ref,seconds=seconds,preset_root=m.EVIDENCE);r["control_byte_identical"]=r["frame_hashes"]==c["frame_hashes"];assert r["control_byte_identical"]
if ref==(0,0):r["authored_byte_identical"]=r["frame_hashes"]==original["frame_hashes"];assert r["authored_byte_identical"]
r["diagnostic_rows"]=len(log.read_text().splitlines()) if log.exists() else 0
(m.EVIDENCE/(label+".json")).write_text(json.dumps(r,indent=2)+"\n");print({k:r[k] for k in ["status","img_err","luma_ratio","centre_rgb","diagnostic_rows","authored_byte_identical","control_byte_identical"] if k in r},flush=True);assert r["status"]=="success" and r["diagnostic_rows"]>0
