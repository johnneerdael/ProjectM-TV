from pathlib import Path
import json,difflib
from dataclasses import asdict
from preset_lab.build_worker import build_worker,prepare_engine
REPO=Path(__file__).resolve().parents[5];E=Path(__file__).resolve().parent;own=REPO/"build/diffusion/acid-diagnosis";tag="phase-beta-p1";repo=own/("repo-"+tag);patches=repo/"tools/projectm-patches";patches.mkdir(parents=True,exist_ok=True)
source=repo/"third_party";source.mkdir(exist_ok=True);link=source/"projectm"
if not link.exists():link.symlink_to(REPO/"third_party/projectm",target_is_directory=True)
for p in (own/"repo-verified-raw-p1/tools/projectm-patches").glob("*.patch"):(patches/p.name).write_text(p.read_text())
snapshot=Path(json.loads((E/"worker-rawwrap.json").read_text())["snapshot"]);name="src/libprojectM/MilkdropPreset/MilkdropShader.cpp";before=(snapshot/name).read_text();anchor='    m_shader.SetUniformFloat4("_c8",';assert before.count(anchor)==1
after=before.replace(anchor,'    const float labScale=LineScale(presetState.renderContext.viewportSizeX,presetState.renderContext.viewportSizeY,presetState.renderContext.lineReferenceWidth,presetState.renderContext.lineReferenceHeight);\n    m_shader.SetUniformFloat4("projectm_lab_source_dims", {float(presetState.renderContext.viewportSizeX),float(presetState.renderContext.viewportSizeY),labScale>1.0f?1.0f:0.0f,labScale>1.0f?std::min((labScale*labScale-1.0f)/6.0f,1.9f):0.0f});\n'+anchor)
text=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name,tofile='b/'+name));(patches/"0031-research-phase-beta-uniform.patch").write_text(text);(E/"phase-beta-uniform.patch").write_text(text)
work=own/("work-"+tag);exe=build_worker(repo,work);snapshot,identity=prepare_engine(repo,work);result={"exe":str(exe),"snapshot":str(snapshot),"identity":asdict(identity)};(E/("worker-"+tag+".json")).write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
