"""Exercise real compile failure with and without motion-vector injection."""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from measure import EVIDENCE, measure

names=["Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk",
       "$$$ Royal - Mashup (103).milk",
       "suksma - penattrition - geiss crossfire shaders nz+.milk"]

def run(job):
    name,w,h=job
    a=measure(name,"baseline",w,h)
    b=measure(name,"compile-failure",w,h)
    diagnostic=Path(b["diagnostics"]).read_text()
    row={"preset":name,"size":[w,h],"status":b["status"],"frames":b["frames"],
         "baseline_sha256":a["sha256"],"fallback_sha256":b["sha256"],
         "identical":a["frame_hashes"]==b["frame_hashes"],"min_luma":b.get("min_luma"),
         "identity":b["identity"],"diagnostic":diagnostic}
    assert row["identical"] and row["status"]=="success" and row["frames"]==240
    assert "diffusion disabled" in diagnostic and row["min_luma"]>0
    print(name,[w,h],"240 byte-identical fallback frames",flush=True)
    return row

with ThreadPoolExecutor(max_workers=3) as pool:
    rows=list(pool.map(run,[(n,w,h) for n in names for w,h in [(2364,1330),(3840,2160)]]))
(EVIDENCE/f"f7-{sys.argv[1] if len(sys.argv)>1 else 'production'}-suite.json").write_text(json.dumps(rows,indent=2)+"\n")
