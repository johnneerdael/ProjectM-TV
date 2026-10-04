from pathlib import Path
import json,sys,difflib
from dataclasses import asdict
from preset_lab.build_worker import build_worker,prepare_engine
REPO=Path(__file__).resolve().parents[5];own=REPO/"build/diffusion/acid-diagnosis";E=Path(__file__).resolve().parent;kind=sys.argv[1];tag=kind+"-sidecar3";repo=own/("repo-"+tag);patches=repo/"tools/projectm-patches";patches.mkdir(parents=True,exist_ok=True)
source=repo/"third_party";source.mkdir(exist_ok=True);link=source/"projectm"
if not link.exists():link.symlink_to(REPO/"third_party/projectm",target_is_directory=True)
for p in (REPO/("build/diffusion/repo-"+kind)/"tools/projectm-patches").glob("*.patch"):(patches/p.name).write_text(p.read_text())
root=REPO/"third_party/projectm";output=[]
def edit(name,fn):
 before=(root/name).read_text();after=fn(before);assert before!=after;output.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile="a/"+name,tofile="b/"+name))
def replace(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def header(s):
 s=replace(s,"    auto Shader() -> Renderer::Shader&;","    auto Shader() -> Renderer::Shader&;\n    void DrawAcidSidecar(int indices,int width,int height);")
 s=replace(s,"    Renderer::Shader m_shader;","    void CompileAcidSidecar(const std::string& vertex,const std::string& fragment);\n    Renderer::Shader m_acidSidecar;\n    bool m_acidSidecarReady{};\n    int m_acidSidecarFrame{};\n    Renderer::Shader m_shader;")
 return s
edit("src/libprojectM/MilkdropPreset/MilkdropShader.hpp",header)
def implementation(s):
 s="#include <stdexcept>\n"+s
 s=replace(s,"namespace libprojectM {",(E/"phase_sidecar.hpp").read_text()+"\nnamespace libprojectM {")
 s=replace(s,"        m_shader.CompileProgram(vertexShader, cachedGlsl);","        m_shader.CompileProgram(vertexShader, cachedGlsl);\n        CompileAcidSidecar(vertexShader,cachedGlsl);")
 s=replace(s,"    m_shader.CompileProgram(vertexShader, generator.GetResult());","    m_shader.CompileProgram(vertexShader, generator.GetResult());\n    CompileAcidSidecar(vertexShader,generator.GetResult());")
 return replace(s,"void MilkdropShader::UpdateMaxBlurLevel",(E/"sidecar_method.cpp").read_text()+"void MilkdropShader::UpdateMaxBlurLevel")
edit("src/libprojectM/MilkdropPreset/MilkdropShader.cpp",implementation)
edit("src/libprojectM/MilkdropPreset/PerPixelMesh.cpp",lambda s:replace(s,"    glDrawElements(GL_TRIANGLES, triangleCount * 3, GL_UNSIGNED_INT, nullptr);","    glDrawElements(GL_TRIANGLES, triangleCount * 3, GL_UNSIGNED_INT, nullptr);\n    if(m_warpShader) m_warpShader->DrawAcidSidecar(triangleCount*3,presetState.renderContext.viewportSizeX,presetState.renderContext.viewportSizeY);"))
edit("src/libprojectM/MilkdropPreset/FinalComposite.cpp",lambda s:replace(s,"        glDrawElements(GL_TRIANGLES, indexCount, GL_UNSIGNED_INT, nullptr);","        glDrawElements(GL_TRIANGLES, indexCount, GL_UNSIGNED_INT, nullptr);\n        m_compositeShader->DrawAcidSidecar(indexCount,presetState.renderContext.viewportSizeX,presetState.renderContext.viewportSizeY);"))
(patches/"0029-research-acid-sidecar.patch").write_text("".join(output));(E/(tag+".patch")).write_text("".join(output))
work=own/("work-"+tag);exe=build_worker(repo,work);snapshot,identity=prepare_engine(repo,work)
result={"exe":str(exe),"snapshot":str(snapshot),"identity":asdict(identity)}
(E/("worker-"+tag+".json")).write_text(json.dumps(result,indent=2)+"\n");print(result,flush=True)
