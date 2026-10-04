from pathlib import Path
import json,difflib
from dataclasses import asdict
from preset_lab.build_worker import build_worker,prepare_engine
REPO=Path(__file__).resolve().parents[5];E=Path(__file__).resolve().parent;own=REPO/"build/diffusion/acid-diagnosis";tag="author-footprint-v2";repo=own/("repo-"+tag);patches=repo/"tools/projectm-patches";patches.mkdir(parents=True,exist_ok=True)
source=repo/"third_party";source.mkdir(exist_ok=True);link=source/"projectm"
if not link.exists():link.symlink_to(REPO/"third_party/projectm",target_is_directory=True)
for p in (own/"repo-baseline-sidecar3/tools/projectm-patches").glob("*.patch"):
 text=p.read_text()
 if p.name=="0029-research-acid-sidecar.patch":
  text=text.replace("vec3 acid_A=texture(sampler_main,uv_dy).xyz;","vec3 acid_A=AcidLocalPixel(uv_dy,_uv.zw);")
  text=text.replace("vec3 acid_M=texture(sampler_main,_uv.xy).xyz;","vec3 acid_M=AcidLocalPixel(_uv.xy,_uv.zw);")
 (patches/p.name).write_text(text)
name="src/libprojectM/MilkdropPreset/MilkdropShader.cpp";before=(REPO/"third_party/projectm"/name).read_text();anchor='    m_shader.SetUniformFloat4("_c8",'
assert before.count(anchor)==1
after=before.replace(anchor,'    m_shader.SetUniformFloat4("projectm_lab_source_dims", {float(presetState.renderContext.viewportSizeX), float(presetState.renderContext.viewportSizeY),\n        LineScale(presetState.renderContext.viewportSizeX,presetState.renderContext.viewportSizeY,presetState.renderContext.lineReferenceWidth,presetState.renderContext.lineReferenceHeight)>1.0f ? 1.0f : 0.0f, 0.0f});\n'+anchor)
text="".join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile="a/"+name,tofile="b/"+name));(patches/"0030-research-author-footprint-uniform.patch").write_text(text);(E/"author-footprint-uniform.patch").write_text(text)
name="src/libprojectM/MilkdropPreset/PerPixelMesh.cpp";before=(REPO/"third_party/projectm"/name).read_text();after="#define MILKDROP_PRESET_DEBUG\n"+before
text="".join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile="a/"+name,tofile="b/"+name));(patches/"0031-research-warp-compile-log.patch").write_text(text)
work=own/("work-"+tag);exe=build_worker(repo,work);snapshot,identity=prepare_engine(repo,work)
result={"exe":str(exe),"snapshot":str(snapshot),"identity":asdict(identity)}
(E/("worker-"+tag+".json")).write_text(json.dumps(result,indent=2)+"\n");print(result,flush=True)
