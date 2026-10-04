from pathlib import Path
import json
from dataclasses import asdict
from preset_lab.build_worker import build_worker,prepare_engine
REPO=Path(__file__).resolve().parents[5];own=REPO/"build/diffusion/acid-diagnosis";repo=own/"repo-rawwrap";patches=repo/"tools/projectm-patches";patches.mkdir(parents=True,exist_ok=True)
source=repo/"third_party";source.mkdir(exist_ok=True);link=source/"projectm"
if not link.exists():link.symlink_to(REPO/"third_party/projectm",target_is_directory=True)
for p in (REPO/"build/diffusion/repo-point-separated/tools/projectm-patches").glob("*.patch"):
 s=p.read_text()
 if p.name=="0026-research-point-separated.patch":
  s=s.replace("const bool point = !name.empty() && (name[0] == 'p' || name[0] == 'P');", "const bool point = (!name.empty() && (name[0] == 'p' || name[0] == 'P')) || name == \"fw_main\";")
  s=s.replace("(sampler_p[cw]_main)","(sampler_p[cw]_main|sampler_fw_main)")
 (patches/p.name).write_text(s)
work=own/"work-rawwrap";exe=build_worker(repo,work);snapshot,identity=prepare_engine(repo,work)
result={"exe":str(exe),"snapshot":str(snapshot),"identity":asdict(identity)}
(Path(__file__).resolve().parent/"worker-rawwrap.json").write_text(json.dumps(result,indent=2)+"\n");print(result,flush=True)
