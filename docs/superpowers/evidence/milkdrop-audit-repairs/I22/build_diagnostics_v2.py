from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile
ROOT=Path.cwd(); OUT=ROOT/'build/audit/diagnostics-v2'; OUT.mkdir(exist_ok=True)
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
fixtures={
 'audit single dot.milk':base+'''wavecode_0_enabled=1
wavecode_0_samples=1
wavecode_0_bUseDots=1
wavecode_0_smoothing=0
wave_0_per_point1=x=.25;y=.5;r=1;g=0;b=0;a=1;
''',
 'audit two dots.milk':base+'''wavecode_0_enabled=1
wavecode_0_samples=2
wavecode_0_bUseDots=1
wavecode_0_smoothing=0
wave_0_per_point1=x=.25+.5*sample;y=.5;r=1;g=0;b=0;a=1;
''',
 'audit dot ring.milk':base+'''wavecode_0_enabled=1
wavecode_0_samples=12
wavecode_0_bUseDots=1
wavecode_0_smoothing=0
wave_0_per_point1=x=.5+.35*cos(sample*6.283185307179586);y=.5+.35*sin(sample*6.283185307179586);r=1;g=0;b=0;a=1;
'''}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for role,path,package in [('before','build/audit/i08-workers/baseline-native','nl.neerdael.projectmtv.auditdiagbefore'),('after','build/audit/i22-workers/candidate-native','nl.neerdael.projectmtv.auditdiagafter')]:
 src=ROOT/path; original=json.loads((src/'identity.json').read_text()); dest=OUT/role; dest.mkdir(exist_ok=False)
 worker=dest/'worker'; shutil.copytree(src/'source/tools/core-corpus/android-worker',worker,ignore=shutil.ignore_patterns('build','.gradle'))
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
