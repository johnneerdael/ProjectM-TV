from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile
ROOT=Path.cwd();OUT=ROOT/'build/audit/final-capture-workers';OUT.mkdir(exist_ok=False)
sources={'p15':'workers/rebase-baseline','p16':'workers/rebase-candidate','p17':'i08-workers/baseline-native','p18':'i22-workers/candidate-native','p19':'i31-workers/candidate-native','p20':'i09-workers/candidate-native','p21':'input-workers/candidate-native','p22':'i29-workers/candidate-native','i19proposal':'i19-workers/candidate-native'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
current=(ROOT/'tools/core-corpus/android-worker/app/src/main/java/nl/neerdael/projectmtv/corpus/CorpusInstrumentation.java').read_text();ns=current.index('    private static JSONObject capture(');ne=current.index('    private static void pausePrewarm(',ns)
for label,rel in sources.items():
 src=ROOT/'build/audit'/rel;i=json.loads((src/'identity.json').read_text());dest=OUT/label;dest.mkdir();worker=dest/'worker';shutil.copytree(src/'source/tools/core-corpus/android-worker',worker,ignore=shutil.ignore_patterns('build','.gradle'))
 java=worker/'app/src/main/java/nl/neerdael/projectmtv/corpus/CorpusInstrumentation.java';s=java.read_text();start=s.index('    private static JSONObject capture(');end=s.index('    private static void pausePrewarm(',start);s=s[:start]+current[ns:ne]+s[end:];s=s.replace('eight selected frames, top-down RGB8 SHA256','eight selected final-output frames from read framebuffer zero, top-down RGB8 SHA256');java.write_text(s)
 package='nl.neerdael.projectmtv.auditfinal'+label;gradle=worker/'app/build.gradle';s=gradle.read_text();anchor="'nl.neerdael.projectmtv.corpuscandidate'";assert s.count(anchor)==1;gradle.write_text(s.replace(anchor,anchor+", '"+package+"'"))
 with (dest/'build.log').open('w') as log:subprocess.run([str(ROOT/'gradlew'),'-p',str(worker),'assembleDebug','--console=plain','-PcoreAar='+i['aar'],'-PcorpusApplicationId='+package],check=True,stdout=log,stderr=subprocess.STDOUT)
 apk=dest/'worker.apk';shutil.copyfile(worker/'app/build/outputs/apk/debug/app-debug.apk',apk)
 with zipfile.ZipFile(i['aar']) as aar,zipfile.ZipFile(apk) as z:
  for n in aar.namelist():
   if n.startswith('jni/') and n.endswith('.so'):assert aar.read(n)==z.read(n.replace('jni/','lib/',1))
   if n.startswith('assets/') and not n.endswith('/'):assert aar.read(n)==z.read(n)
 i.update(package=package,apk=str(apk),apk_sha256=sha(apk),worker_java_sha256=sha(java),worker_gradle_sha256=sha(gradle),capture_correction={'previous_identity':str(src/'identity.json'),'previous_identity_sha256':sha(src/'identity.json'),'native_and_assets_unchanged':True,'builder_sha256':sha(Path(__file__)),'read_framebuffer':0,'restores_previous_read_binding':True})
 (dest/'identity.json').write_text(json.dumps(i,indent=2)+'\n');print(label,i['source_commit'],flush=True)
