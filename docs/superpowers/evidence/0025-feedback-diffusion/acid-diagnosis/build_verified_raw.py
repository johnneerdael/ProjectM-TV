from pathlib import Path
import json,difflib,sys
from dataclasses import asdict
from preset_lab.build_worker import build_worker,prepare_engine
REPO=Path(__file__).resolve().parents[5];E=Path(__file__).resolve().parent;own=REPO/"build/diffusion/acid-diagnosis";tag="verified-raw-p1" if len(sys.argv)>1 and sys.argv[1]=="p1" else "verified-raw-v3";repo=own/("repo-"+tag);patches=repo/"tools/projectm-patches";patches.mkdir(parents=True,exist_ok=True)
source=repo/"third_party";source.mkdir(exist_ok=True);link=source/"projectm"
if not link.exists():link.symlink_to(REPO/"third_party/projectm",target_is_directory=True)
for p in (own/"repo-rawwrap/tools/projectm-patches").glob("*.patch"):
 text=p.read_text()
 if tag=="verified-raw-p1" and p.name=="0025-feedback-diffusion-compensation.patch":
  needle="const bool diffuseAtOutput = m_feedbackDiffusion.Active() && !motionVectorsDrawn;";assert text.count(needle)==1;text=text.replace(needle,"const bool diffuseAtOutput = false; // Research P1: identical source routing, sharp composite.")
 (patches/p.name).write_text(text)
snapshot=Path(json.loads((E/"worker-rawwrap.json").read_text())["snapshot"]);name="src/libprojectM/MilkdropPreset/PerPixelMesh.cpp";before=(snapshot/name).read_text();after=before
start=after.index('    presetState.mainTexture.lock()->Bind(0);');end=after.index('    glBindVertexArray(m_vaoID);',start)
block=after[start:end];after=after[:start]+"    if (!m_warpShader) {\n"+block+"    }\n\n"+after[end:]
anchor='    glDrawElements(GL_TRIANGLES, triangleCount * 3, GL_UNSIGNED_INT, nullptr);';assert after.count(anchor)==1;after=after.replace(anchor,(E/"routing_checks.cpp").read_text()+anchor)
after='#define MILKDROP_PRESET_DEBUG\n#include <cstdio>\n#include <cstdlib>\n#include <stdexcept>\n'+after
text=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name,tofile='b/'+name));(patches/"0030-research-preserve-raw-descriptors.patch").write_text(text);(E/"verified-raw-routing.patch").write_text(text)
work=own/("work-"+tag);exe=build_worker(repo,work);snapshot,identity=prepare_engine(repo,work);result={"exe":str(exe),"snapshot":str(snapshot),"identity":asdict(identity)};(E/("worker-"+tag+".json")).write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
