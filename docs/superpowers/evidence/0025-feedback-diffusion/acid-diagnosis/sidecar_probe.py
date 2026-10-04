import sys,json,os
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE))
import measure as m
m.EVIDENCE=Path(__file__).resolve().parent;m.SCRATCH=m.REPO/"build/diffusion/acid-diagnosis"
worker=sys.argv[1];w,h=map(int,sys.argv[2].split("x"));ref=(0,0) if h==665 else (1024,768)
log=m.EVIDENCE/f"sidecar-{worker}-{h}.csv"
os.environ["PROJECTM_ACID_DIAG_LOG"]=str(log)
log.unlink(missing_ok=True)
r=m.measure("acid-diagnosis-original.milk",worker,w,h,ref,seconds=12,preset_root=m.EVIDENCE)
reference=json.loads((BASE/"noise-corrected-expanded-12s-report.json").read_text())["presets"]["Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk"]["runs"]
name="authored" if h==665 else f"{worker.split('-')[0]}-{h}"
original=json.loads((Path(reference[name]["output"])/"metrics.json").read_text())
r["primary_byte_identical"]=r["frame_hashes"]==original["frame_hashes"];r["primary_reference"]=reference[name]["output"];r["diagnostic_rows"]=len(log.read_text().splitlines()) if log.exists() else 0
(m.EVIDENCE/f"sidecar-{worker}-{h}.json").write_text(json.dumps(r,indent=2)+"\n")
print({k:r[k] for k in ["status","primary_byte_identical","diagnostic_rows","luma","centre_rgb"]},flush=True)
assert r["status"]=="success" and r["primary_byte_identical"] and r["diagnostic_rows"]>0
