from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile
ROOT=Path.cwd();OUT=ROOT/'build/audit/i12-warm-workers';OUT.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for role,folder in [('before','main-sync-workers/candidate-native'),('after','i12-workers/candidate-native')]:
 src=ROOT/'build/audit'/folder;i=json.loads((src/'identity.json').read_text());dest=OUT/role;dest.mkdir();worker=dest/'worker';shutil.copytree(src/'source/tools/core-corpus/android-worker',worker,ignore=shutil.ignore_patterns('build','.gradle'))
 java=worker/'app/src/main/java/nl/neerdael/projectmtv/corpus/CorpusInstrumentation.java';s=java.read_text();anchor='LabBridge.setFrameClock(frame / (double) FPS)';assert s.count(anchor)==1;s=s.replace(anchor,'LabBridge.setFrameClock((frame + 1) / (double) FPS)').replace('result.put("simulatedSeconds", frame / (double) FPS);','result.put("simulatedSeconds", (frame + 1) / (double) FPS);');anchor='manifest.put("determinism",';idx=s.index(anchor);s=s[:idx]+'manifest.put("frameClockOffsetSeconds", 1.0 / FPS);\n        '+s[idx:];java.write_text(s)
 package='nl.neerdael.projectmtv.auditi12warm'+role;gradle=worker/'app/build.gradle';s=gradle.read_text();anchor="'nl.neerdael.projectmtv.corpuscandidate'";assert s.count(anchor)==1;gradle.write_text(s.replace(anchor,anchor+", '"+package+"'"))
 with (dest/'build.log').open('w') as log:subprocess.run([str(ROOT/'gradlew'),'-p',str(worker),'assembleDebug','--console=plain','-PcoreAar='+i['aar'],'-PcorpusApplicationId='+package],check=True,stdout=log,stderr=subprocess.STDOUT)
 apk=dest/'worker.apk';shutil.copyfile(worker/'app/build/outputs/apk/debug/app-debug.apk',apk)
 with zipfile.ZipFile(i['aar']) as aar,zipfile.ZipFile(apk) as z:
  for n in aar.namelist():
   if n.startswith('jni/') and n.endswith('.so'):assert aar.read(n)==z.read(n.replace('jni/','lib/',1))
   if n.startswith('assets/') and not n.endswith('/'):assert aar.read(n)==z.read(n)
 i.update(package=package,apk=str(apk),apk_sha256=sha(apk),worker_java_sha256=sha(java),worker_gradle_sha256=sha(gradle),clock_context={'surface_initialization_clock':0,'frame_clock':'(frame+1)/30','offset_seconds':1/30,'preset_bytes_unchanged':True,'native_aar_bytes_unchanged':True,'purpose':'Finite first timestep for original1/tic; source-derived Native context, not Windows recording','builder_sha256':sha(Path(__file__))});(dest/'identity.json').write_text(json.dumps(i,indent=2)+'\n');print(role,i['source_commit'],flush=True)
