import importlib.util,json,hashlib,difflib
from pathlib import Path
ROOT=Path.cwd();provider=ROOT/'docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/build.py'
spec=importlib.util.spec_from_file_location('shared_core_builder',provider);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.WORK=ROOT/'build/native-4k-current-main/p1-experiment';b.WORK.mkdir(parents=True,exist_ok=True)
original=b.prepare
adapter=Path(__file__)
def prepare(variant,commit):
 destination,source,identity=original(variant,commit)
 relative='src/libprojectM/MilkdropPreset/MilkdropPreset.cpp'
 file=source/'third_party/projectm'/relative;before=file.read_text()
 old='const bool diffuseAtOutput = m_feedbackDiffusion.Active() && !motionVectorsDrawn;'
 new='const bool diffuseAtOutput = false;'
 assert before.count(old)==1;file.write_text(before.replace(old,new))
 patch=source/'tools/projectm-patches/0030-feedback-diffusion-compensation.patch';text=patch.read_text();assert text.count('+'+old)==0
 assert text.count(old)==1;patch.write_text(text.replace(old,new))
 difference=''.join(difflib.unified_diff(before.splitlines(True),file.read_text().splitlines(True),fromfile='production/'+relative,tofile='diagnostic/'+relative))
 (destination/'placement-p1.diff').write_text(difference)
 identity['ordered_patches'][-1]['sha256']=b.sha(patch)
 identity['source_patch_sha256']=b.digest([(p['name'],p['sha256']) for p in identity['ordered_patches']])
 identity['private_placement_experiment']={'placement':'P1 always; extra input filtering pass, raw final composite','adapter_sha256':b.sha(adapter),'diff_sha256':b.sha(destination/'placement-p1.diff'),'modified_source_sha256':b.sha(file),'production_source_commit':commit,'shipping_byte_identity':False}
 (source/'corpus-app/src/main/assets/backend-identity.json').write_text(b.canonical(identity)+'\n')
 (destination/'identity.json').write_text(b.canonical(identity)+'\n')
 return destination,source,identity
b.prepare=prepare
b.build('candidate',b.subprocess.check_output(['git','rev-parse','790aaa24'],cwd=ROOT,text=True).strip())
