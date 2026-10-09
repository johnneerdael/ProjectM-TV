from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile
ROOT=Path.cwd(); OUT=ROOT/'build/audit/motion-field-oracle-v2-diagnostics'; OUT.mkdir(exist_ok=True)
fixtures={'audit motion bilerp native48x32.milk':(ROOT/'build/audit/motion-field-diagnostic-v2.milk').read_text()}
assert len(fixtures)==1

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for role,path,package in [('before','build/audit/retained-policy-workers/candidate-native','nl.neerdael.projectmtv.auditbilerpv2before'),('after','build/audit/motion-field-oracle-native-workers/candidate-native','nl.neerdael.projectmtv.auditbilerpv2after')]:
 src=ROOT/path; original=json.loads((src/'identity.json').read_text()); dest=OUT/role; dest.mkdir(exist_ok=False)
 worker=dest/'worker'; shutil.copytree(src/'source/tools/core-corpus/android-worker',worker,ignore=shutil.ignore_patterns('build','.gradle'))
 java=worker/'app/src/main/java/nl/neerdael/projectmtv/corpus/CorpusInstrumentation.java';old=java.read_text();new=(ROOT/'tools/core-corpus/android-worker/app/src/main/java/nl/neerdael/projectmtv/corpus/CorpusInstrumentation.java').read_text();start=old.index('    private static JSONObject capture(');end=old.index('    private static void pausePrewarm(',start);ns=new.index('    private static JSONObject capture(');ne=new.index('    private static void pausePrewarm(',ns);java.write_text(old[:start]+new[ns:ne]+old[end:])
 gradle=worker/'app/build.gradle';s=gradle.read_text(); anchor="'nl.neerdael.projectmtv.corpuscandidate'";assert s.count(anchor)==1;s=s.replace(anchor,anchor+", '"+package+"'");gradle.write_text(s)
 assets=worker/'app/src/main/assets';(assets/'presets').mkdir(parents=True)
 with zipfile.ZipFile(original['aar']) as z:
  index=z.read('assets/presets.idx'); stock={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('assets/') and n!='assets/presets.idx' and not n.endswith('/')}
 (assets/'presets.idx').write_bytes(index.rstrip(b'\n')+b'\n'+''.join(n+'\t0\n' for n in fixtures).encode())
 for n,s in fixtures.items():(assets/'presets'/n).write_text(s)
 with (dest/'build.log').open('w') as log:
  subprocess.run([str(ROOT/'gradlew'),'-p',str(worker),'assembleDebug','--console=plain','-PcoreAar='+original['aar'],'-PcorpusApplicationId='+package],check=True,stdout=log,stderr=subprocess.STDOUT)
 apk=dest/(role+'.apk');shutil.copyfile(worker/'app/build/outputs/apk/debug/app-debug.apk',apk)
 with zipfile.ZipFile(apk) as z:
  for n,h in stock.items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
 identity=dict(original,role=role,package=package,apk=str(apk),apk_sha256=sha(apk),diagnostic_overlay={'stock_assets_preserved_except_index':len(stock),'stock_preset_count':9606,'expected_preset_count':9606+len(fixtures),'fixtures':{n:sha(assets/'presets'/n) for n in fixtures},'index_sha256':sha(assets/'presets.idx'),'instrumentation_sha256':sha(worker/'app/src/main/java/nl/neerdael/projectmtv/corpus/CorpusInstrumentation.java'),'builder_sha256':sha(Path(__file__))})
 (dest/'identity.json').write_text(json.dumps(identity,indent=2)+'\n');print(role,apk,flush=True)
