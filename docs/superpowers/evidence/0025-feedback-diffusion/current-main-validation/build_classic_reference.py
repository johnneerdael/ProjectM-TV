import importlib.util,json,difflib
from pathlib import Path
ROOT=Path.cwd();provider=ROOT/'docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/build.py'
spec=importlib.util.spec_from_file_location('core_builder',provider);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.WORK=ROOT/'build/native-4k-current-main/classic-reference-control';b.WORK.mkdir(parents=True,exist_ok=True)
original=b.prepare
def prepare(variant,commit):
 destination,source,identity=original(variant,commit)
 file=source/'core/src/main/cpp/native-lib.cpp';before=file.read_text()
 old='projectm_opengl_set_line_reference_size(g_engine.pm, 1024, 768);'
 new='projectm_opengl_set_line_reference_size(g_engine.pm, 0, 0);'
 assert before.count(old)==1;file.write_text(before.replace(old,new))
 diff=''.join(difflib.unified_diff(before.splitlines(True),file.read_text().splitlines(True),fromfile='normal/core/native-lib.cpp',tofile='classic/core/native-lib.cpp'))
 (destination/'classic-reference.diff').write_text(diff)
 identity['instrumented_core_source_sha256']['native-lib.cpp']=b.sha(file)
 identity['private_reference_control']={'reference_width':0,'reference_height':0,'adapter_sha256':b.sha(Path(__file__)),'diff_sha256':b.sha(destination/'classic-reference.diff'),'source_sha256':b.sha(file),'shipping_byte_identity':False}
 (source/'corpus-app/src/main/assets/backend-identity.json').write_text(b.canonical(identity)+'\n');(destination/'identity.json').write_text(b.canonical(identity)+'\n')
 return destination,source,identity
b.prepare=prepare;b.build('baseline',b.subprocess.check_output(['git','rev-parse','0625587f'],cwd=ROOT,text=True).strip())
