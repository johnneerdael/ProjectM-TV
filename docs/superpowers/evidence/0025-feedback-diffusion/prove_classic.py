"""Direct classic/reference-zero full-frame identity, independent of image metrics."""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from measure import EVIDENCE, measure

CANDIDATE=sys.argv[1] if len(sys.argv)>1 else "production"

def run(name):
    a=measure(name,"baseline",1182,665,reference=(0,0))
    b=measure(name,CANDIDATE,1182,665,reference=(0,0))
    identical=a["frame_hashes"]==b["frame_hashes"]
    unstable=False
    if not identical:
        repeat=measure(name,"baseline",1182,665,reference=(0,0),repeat=1)
        unstable=a["frame_hashes"]!=repeat["frame_hashes"]
    row={"preset":name,"identical":identical,"baseline_nondeterministic":unstable,
         "baseline_sha256":a["sha256"],"candidate_sha256":b["sha256"],
         "statuses":[a["status"],b["status"]],"identity":b["identity"]}
    assert row["statuses"]==["success","success"] and (identical or unstable),row
    return row

with ThreadPoolExecutor(max_workers=3) as pool:
    rows=list(pool.map(run,(EVIDENCE/"set24.txt").read_text().splitlines()))
(EVIDENCE/f"f1-classic-{CANDIDATE}.json").write_text(json.dumps(rows,indent=2)+"\n")
print(sum(r["identical"] for r in rows),"byte-identical classic pairs; baseline unstable:",
      [r["preset"] for r in rows if r["baseline_nondeterministic"]],flush=True)
