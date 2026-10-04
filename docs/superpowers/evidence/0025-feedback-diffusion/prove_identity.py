"""F1/F7 integration proof and line-compare's own baseline check."""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from measure import EVIDENCE, REPO, SCRATCH, measure

CANDIDATE = sys.argv[1] if len(sys.argv) > 1 else "final"

names = (EVIDENCE / "set24.txt").read_text().splitlines()
jobs = [(name,worker,w,h,ref) for name in names for worker in ["baseline",CANDIDATE]
        for w,h,ref in [(1024,768,(1024,768)),(960,540,(1024,768))]]
with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(lambda x:measure(x[0],x[1],x[2],x[3],reference=x[4]),jobs))
checks = []
for name in names:
    for w,h in [(1024,768),(960,540)]:
        runs = [r for r in results if r["preset"]==name and r["config"]["width"]==w]
        identical = len(runs)==2 and runs[0]["frame_hashes"]==runs[1]["frame_hashes"]
        unstable = False
        candidate_unstable = False
        repeat_hashes = {}
        if not identical and all(r["status"]=="success" for r in runs):
            for run in runs:
                again=measure(name,run["worker"],w,h,repeat=1)
                repeat_hashes[run["worker"]]=again["sha256"]
                changed = again["frame_hashes"]!=run["frame_hashes"]
                if run["worker"] == "baseline": unstable = changed
                else: candidate_unstable = changed
        checks.append({"preset":name,"size":[w,h],"statuses":[r["status"] for r in runs],
                       "identical":identical,"baseline_nondeterministic":unstable,
                       "candidate_nondeterministic":candidate_unstable,
                       "repeat_hashes":repeat_hashes})
(EVIDENCE/f"f1-direct-{CANDIDATE}.json").write_text(json.dumps(checks,indent=2)+"\n")
assert all((c["identical"] or c["baseline_nondeterministic"]) and c["statuses"]==["success","success"] for c in checks), checks
print("F1 reference/below-reference:",sum(c["identical"] for c in checks),"byte-identical pairs; unstable:",
      [c["preset"] for c in checks if c["baseline_nondeterministic"]],flush=True)
for worker in ["baseline",CANDIDATE]:
    info=json.loads((EVIDENCE/f"worker-{worker}.json").read_text())
    args=[sys.executable,"-m","preset_lab","line-compare","--repo",str(REPO),
          "--worker",info["exe"],"--work",str(SCRATCH/f"line-compare-{worker}"),
          "--preset-list",str(EVIDENCE/"set24.txt"),"--concurrency","4"]
    if worker==CANDIDATE:
        args += ["--baseline",str(SCRATCH/"line-compare-baseline/report.json")]
    log=EVIDENCE/f"line-compare-{worker}.log"
    with log.open("w") as output:subprocess.run(args,check=True,stdout=output,stderr=subprocess.STDOUT)
    report=json.loads((SCRATCH/f"line-compare-{worker}/report.json").read_text())
    (EVIDENCE/f"line-compare-{worker}.json").write_text(json.dumps(report,indent=2)+"\n")
    print(worker,report["summary"],flush=True)
acid="Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk"
a=measure(acid,"baseline",2364,1330)
b=measure(acid,"compile-failure",2364,1330)
proof={"status":b["status"],"frames":b["frames"],"baseline_sha256":a["sha256"],
       "failure_sha256":b["sha256"],"identical":a["frame_hashes"]==b["frame_hashes"],
       "min_luma":b.get("min_luma"),"diagnostic":Path(b["diagnostics"]).read_text()}
(EVIDENCE/"f7-fallback.json").write_text(json.dumps(proof,indent=2)+"\n")
assert proof["identical"] and "diffusion disabled" in proof["diagnostic"],proof
print("F7 real compile failure: full-frame hashes identical to baseline",flush=True)
