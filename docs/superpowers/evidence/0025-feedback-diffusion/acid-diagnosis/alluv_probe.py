import sys, json, hashlib
from pathlib import Path
import cv2,numpy as np
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE))
import measure as m
m.EVIDENCE=Path(__file__).resolve().parent
m.SCRATCH=m.REPO/"build/diffusion/acid-diagnosis"
PRESET="acid-diagnosis-all-uv-rawlinear.milk"
seconds=int(sys.argv[1]); results=[]
reference=json.loads((BASE/f"noise-corrected-expanded-{seconds}s-report.json").read_text())["presets"]["Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk"]["runs"]["authored"]
def compare(r):
 a=[cv2.imread(str(Path(reference["output"])/f"frame-{i}.png")).astype(np.float32)/255 for i in range(5)]
 b=[cv2.imread(str(Path(r["output"])/f"frame-{i}.png")).astype(np.float32)/255 for i in range(5)]
 r["img_err"]=float(np.mean([np.abs(x-y).mean() for x,y in zip(a,b)]));r["luma_ratio"]=r["luma"]/reference["luma"]
 return r
for worker,w,h,ref in [("baseline",1182,665,(0,0)),("rawwrap",2364,1330,(1024,768)),("rawwrap",3840,2160,(1024,768))]:
 r=compare(m.measure(PRESET,worker,w,h,ref,seconds=seconds,preset_root=m.EVIDENCE));results.append(r);(m.EVIDENCE/f"alluv-probe-{seconds}s.json").write_text(json.dumps(results,indent=2)+"\n");print(worker,w,h,{k:r[k] for k in ["status","img_err","luma_ratio","centre_rgb"]},flush=True)
