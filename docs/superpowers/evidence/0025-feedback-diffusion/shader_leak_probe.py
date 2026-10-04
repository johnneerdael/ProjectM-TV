"""Real GL shader-object lifetime check in a private preset-lab build."""
import json
import shutil
import sys
import difflib
from dataclasses import asdict
from pathlib import Path
import preset_lab.build_worker as builder
from measure import REPO, EVIDENCE, SCRATCH, measure

label=sys.argv[1]
native=SCRATCH/("native-leak-"+label)
shutil.copytree(builder.NATIVE,native,dirs_exist_ok=True)
h=native/"analysis_hooks.hpp";t=h.read_text().replace("#include <string>","#include <string>\n#include <vector>")
t=t.replace("namespace lab {","namespace lab {\ninline std::vector<unsigned int> shader_ids;");h.write_text(t)
w=native/"worker.cpp";t=w.read_text();needle="        bands.close();"
t=t.replace(needle,"""        int liveShaders = 0;
        for (auto shader : lab::shader_ids) if (glIsShader(shader)) ++liveShaders;
        std::cerr << "LEAK_PROBE live_shaders=" << liveShaders << "\\n";
        if (liveShaders != 0) throw std::runtime_error("optional shader compilation leaked GL objects");
"""+needle);w.write_text(t)
builder.NATIVE=native
repo=SCRATCH/("repo-leak-"+label);patches=repo/"tools/projectm-patches";patches.mkdir(parents=True,exist_ok=True)
third=repo/"third_party";third.mkdir(exist_ok=True)
if not (third/"projectm").exists():(third/"projectm").symlink_to(REPO/"third_party/projectm",target_is_directory=True)
for source in sorted((REPO/"tools/projectm-patches").glob("*.patch")):
 text=source.read_text()
 if source.name.startswith("0025-"):
  needle="m_shader.CompileProgram(vertexShader, fragmentShader);";assert text.count(needle)==1
  text=text.replace(needle,'m_shader.CompileProgram(vertexShader, fragmentShader + "invalid_shader_token");')
 (patches/source.name).write_text(text)
f="src/libprojectM/Renderer/Shader.cpp";old=(REPO/"third_party/projectm"/f).read_text()
new='#include "../analysis_hooks.hpp"\n'+old.replace('    auto shader = glCreateShader(type);','    auto shader = glCreateShader(type);\n    lab::shader_ids.push_back(shader);')
track=f"diff --git a/{f} b/{f}\n"+"".join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile="a/"+f,tofile="b/"+f))
(patches/"0026-research-shader-lifetimes.patch").write_text(track)
work=SCRATCH/("work-leak-"+label);exe=builder.build_worker(repo,work);snapshot,identity=builder.prepare_engine(repo,work)
name="leak-"+label
(EVIDENCE/f"worker-{name}.json").write_text(json.dumps({"exe":str(exe),"snapshot":str(snapshot),"identity":asdict(identity)},indent=2)+"\n")
result=measure("Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk",name,2364,1330)
log=Path(result["diagnostics"]).read_text()
(EVIDENCE/f"shader-leak-{label}.json").write_text(json.dumps({"status":result["status"],"frames":result["frames"],"diagnostic":log},indent=2)+"\n")
print(result["status"],result["frames"],log,flush=True)
assert result["status"]=="success" and "live_shaders=0" in log
