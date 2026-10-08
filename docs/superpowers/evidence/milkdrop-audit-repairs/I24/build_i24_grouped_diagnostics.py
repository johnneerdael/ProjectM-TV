from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile
ROOT=Path.cwd(); OUT=ROOT/'build/audit/i24-grouped-diagnostics'; OUT.mkdir(exist_ok=True)
fixtures={}
for label,thick,positions in [('alternating','instance%2','x=.25+.5*(instance%2);y=.25+.5*floor(instance/2);'),('disjoint-thick','1','x=.25+.5*(instance%2);y=.25+.5*floor(instance/2);'),('overlap-thick','1','x=.5;y=.5;')]:
 name='audit shape live '+label+'.milk'
 fixtures[name]='MILKDROP_PRESET_VERSION=100\n[preset00]\nfDecay=0\nfGammaAdj=1\nfShader=0\nfWaveAlpha=0\nmv_a=0\nob_size=0\nib_size=0\nshapecode_0_enabled=1\nshapecode_0_num_inst=3\nshapecode_0_sides=4\nshapecode_0_thickOutline=0\nshapecode_0_textured=0\nshapecode_0_additive=0\nshapecode_0_rad=.15\nshapecode_0_a=0\nshapecode_0_a2=0\nshapecode_0_border_a=.5\nshape_0_per_frame1='+positions+'thick='+thick+';border_r=equal(instance,0);border_g=equal(instance,1);border_b=equal(instance,2);\n'
assert len(fixtures)==3

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for role,path,package in [('before','build/audit/retained-policy-workers/candidate-native','nl.neerdael.projectmtv.auditshapebefore'),('after','build/audit/shape-thick-grouped-v2-native-workers/candidate-native','nl.neerdael.projectmtv.auditshapeafter')]:
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
