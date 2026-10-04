from pathlib import Path
import json,sys
from dataclasses import asdict
from preset_lab.build_worker import build_worker,prepare_engine
REPO=Path(__file__).resolve().parents[5];own=REPO/"build/diffusion/acid-diagnosis";gain=sys.argv[1];tag="variance-"+gain.replace(".","");repo=own/("repo-"+tag);patches=repo/"tools/projectm-patches";patches.mkdir(parents=True,exist_ok=True)
source=repo/"third_party";source.mkdir(exist_ok=True);link=source/"projectm"
if not link.exists():link.symlink_to(REPO/"third_party/projectm",target_is_directory=True)
for p in (REPO/"build/diffusion/repo-corrected/tools/projectm-patches").glob("*.patch"):
 s=p.read_text()
 if p.name=="0025-feedback-diffusion-compensation.patch":
  needle="return (scale * scale - 1.0f) / 6.0f;";assert s.count(needle)==1;s=s.replace(needle,"return "+gain+"f * (scale * scale - 1.0f) / 6.0f;")
 (patches/p.name).write_text(s)
work=own/("work-"+tag);exe=build_worker(repo,work);snapshot,identity=prepare_engine(repo,work)
result={"exe":str(exe),"snapshot":str(snapshot),"identity":asdict(identity)}
(Path(__file__).resolve().parent/("worker-"+tag+".json")).write_text(json.dumps(result,indent=2)+"\n");print(result,flush=True)
