from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile
ROOT=Path.cwd(); OUT=ROOT/'build/audit/input-diagnostics'; OUT.mkdir(exist_ok=True)
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
 'audit inverse aspect.milk':base.replace('fDecay=0','fDecay=.99')+'''per_pixel_1=dx=aspecty/10;
shapecode_0_enabled=1
shapecode_0_sides=4
shapecode_0_rad=.08
shapecode_0_x=.5
shapecode_0_y=.5
shapecode_0_r=1
shapecode_0_g=0
shapecode_0_b=0
shapecode_0_a=1
shapecode_0_r2=1
shapecode_0_g2=0
shapecode_0_b2=0
shapecode_0_a2=1
''',
 'audit fresh wave time.milk':base+'''per_frame_1=time=time*.1;
wavecode_0_enabled=1
wavecode_0_samples=2
wavecode_0_bUseDots=0
wavecode_0_bDrawThick=1
wave_0_per_point1=x=.2+.02*time;y=.3+.4*sample;r=1;g=0;b=0;a=1;
'''}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for role,path,package in [('before','build/audit/i09-workers/candidate-native','nl.neerdael.projectmtv.auditinputbefore'),('after','build/audit/input-workers/candidate-native','nl.neerdael.projectmtv.auditinputafter')]:
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
