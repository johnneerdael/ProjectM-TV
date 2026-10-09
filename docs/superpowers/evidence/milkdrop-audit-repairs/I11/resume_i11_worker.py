from pathlib import Path
from dataclasses import asdict
import sys,json,hashlib,shutil,subprocess,zipfile
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import build_validation as builder
from preset_lab.identity import digest,file_digest,canonical_json
root=Path.cwd();dest=(root/'build/audit/i11-workers/candidate-native').resolve();source=dest/'source';engine=source/'third_party/projectm';cpp=source/'core/src/main/cpp';worker=source/'tools/core-corpus/android-worker';aar=dest/'candidate-native.aar';package='nl.neerdael.projectmtv.corpuscandidate'
assert not (dest/'identity.json').exists();commit=subprocess.check_output(['git','rev-parse','63ed4ef4'],text=True).strip()
patches=[{'name':p.name,'sha256':file_digest(p)} for p in sorted((source/'tools/projectm-patches').glob('*.patch'))];assert len(patches)==24
for p in patches:
 raw=subprocess.check_output(['git','show',commit+':tools/projectm-patches/'+p['name']]);assert hashlib.sha256(raw).hexdigest()==p['sha256']
engine_identity=json.loads((engine/'preset-lab-identity.json').read_text());assert engine_identity['patches_sha256']==digest([(p['name'],p['sha256']) for p in patches])
engine_pin=subprocess.check_output(['git','ls-tree',commit,'third_party/projectm'],text=True).split()[2]
evaluator_pin=subprocess.check_output(['git','-C',str(dest/'engine-checkout'),'ls-tree','HEAD','vendor/projectm-eval'],text=True).split()[2]
i={'source_commit':commit,'policy':'native','role':'candidate-native','abi':'arm64-v8a','ordered_patches':patches,'engine_identity':engine_identity,'engine_commit':engine_pin,'evaluator_commit':evaluator_pin,'native_frame_time_api':'projectm_set_frame_time(' in (engine/'src/api/include/projectM-4/parameters.h').read_text(),'builder_sha256':file_digest(root/'tools/native-trails/build_validation.py'),'instrumentation_diff_sha256':file_digest(dest/'instrumentation.diff'),'bridge_sha256':{p.name:file_digest(p) for p in (cpp/'lab_bridge.cpp',cpp/'lab_bridge.hpp')},'shipping_byte_identity':False,'worker_gradle_sha256':file_digest(worker/'app/build.gradle'),'source_files_sha256':{p.relative_to(source).as_posix():file_digest(p) for base in (cpp,engine/'src',engine/'vendor/projectm-eval') for p in sorted(base.rglob('*')) if p.is_file()},'aar_sha256':file_digest(aar),'worker_java_sha256':file_digest(worker/'app/src/main/java/nl/neerdael/projectmtv/corpus/CorpusInstrumentation.java'),'resume_builder_sha256':file_digest(Path(__file__)),'resume_reason':'Core build succeeded; worker assets compression failed on host disk exhaustion; resumed only worker with unchanged frozen AAR/source.','original_failed_worker_log_sha256':file_digest(dest/'worker-build.log')}
with zipfile.ZipFile(aar) as z:i['native_sha256']=builder.native_hashes(z);i['assets_sha256']=digest({n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('assets/')})
with (dest/'worker-build-resumed.log').open('w') as log:subprocess.run([str(source/'gradlew'),'-p',str(worker),':app:assembleDebug','--console=plain','-PcoreAar='+str(aar),'-PcorpusApplicationId='+package],check=True,stdout=log,stderr=subprocess.STDOUT)
assert file_digest(aar)==i['aar_sha256'];apk=dest/'candidate-native.apk';shutil.copyfile(worker/'app/build/outputs/apk/debug/app-debug.apk',apk)
with zipfile.ZipFile(apk) as z:
 for name,expected in i['native_sha256'].items():assert hashlib.sha256(z.read(name.replace('jni/','lib/',1))).hexdigest()==expected
 with zipfile.ZipFile(aar) as a:
  for n in a.namelist():
   if n.startswith('assets/') and not n.endswith('/'):assert a.read(n)==z.read(n)
i.update(aar=str(aar),apk=str(apk),apk_sha256=file_digest(apk),package=package);(dest/'identity.json').write_text(canonical_json(i)+'\n');print('worker resumed',i['source_commit'],i['aar_sha256'],i['apk_sha256'],flush=True)
