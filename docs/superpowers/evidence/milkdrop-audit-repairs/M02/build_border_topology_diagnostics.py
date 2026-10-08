from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile
ROOT=Path.cwd(); OUT=ROOT/'build/audit/border-topology-diagnostics'; OUT.mkdir(exist_ok=True)
base='''MILKDROP_PRESET_VERSION=100
[preset00]
fDecay=0
fGammaAdj=1
fShader=0
fWaveAlpha=0
nWaveMode=0
ob_size=0
ib_size=0
mv_a=0
'''
fixtures={}
for label,size,alpha in [('inverted',1.5,.5),('ordinary',.1,.5),('half',.5,.5),('opaque',1.5,1),('invisible',1.5,0),('inner-inverted',.1,.5)]:
 name='audit border '+label+'.milk'
 text='MILKDROP_PRESET_VERSION=100\n[preset00]\nfDecay=0\nfGammaAdj=1\nfShader=0\nfWaveAlpha=0\nmv_a=0\nob_size='+str(size)+'\nob_a='+str(alpha)+'\nob_r=1\nob_g=1\nob_b=1\nib_size=0\nib_a=0\n'
 if label=='inner-inverted':text=text.replace('ib_size=0\nib_a=0\n','ib_size=1.5\nib_a=.5\nib_r=1\nib_g=1\nib_b=1\n')
 fixtures[name]=text
assert len(fixtures)==6

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for role,path,package in [('before','build/audit/retained-policy-workers/candidate-native','nl.neerdael.projectmtv.auditborderbefore'),('after','build/audit/border-topology-native-workers/candidate-native','nl.neerdael.projectmtv.auditborderafter')]:
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
