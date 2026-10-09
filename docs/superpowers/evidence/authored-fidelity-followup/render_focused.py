from pathlib import Path
import sys,json,hashlib,zipfile
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/authored-followup').resolve();device='emulator-5640';text=runner.shell(device,'am','get-current-user').strip();assert text.isdecimal();user=int(text)
ids={role:json.loads((root/'diagnostics'/role/'identity.json').read_text()) for role in ('before','after')}
for i in ids.values():
 for key in ('aar','apk'):
  assert hashlib.sha256(Path(i[key]).read_bytes()).hexdigest()==i[key+'_sha256']
 with zipfile.ZipFile(i['aar']) as aar,zipfile.ZipFile(i['apk']) as apk:
  for n in apk.namelist():
   if n.startswith('lib/') and n.endswith('.so'):
    assert apk.read(n)==aar.read(n.replace('lib/','jni/',1)),n
  for n in aar.namelist():
   if n.startswith('assets/') and not n.endswith('/') and n!='assets/presets.idx':
    assert apk.read(n)==aar.read(n),n
  fixtures=i['diagnostic_overlay']['fixtures']
  expected=aar.read('assets/presets.idx').rstrip(b'\n')+b'\n'+''.join(n+'\t0\n' for n in fixtures).encode()
  assert apk.read('assets/presets.idx')==expected
  for n,h in fixtures.items():assert hashlib.sha256(apk.read('assets/presets/'+n)).hexdigest()==h,n
  stock={n for n in aar.namelist() if n.startswith('assets/') and not n.endswith('/')}
  assert {n for n in apk.namelist() if n.startswith('assets/') and not n.endswith('/')}==stock|{'assets/presets/'+n for n in fixtures}
_,audio=runner.corpus.signal();pcm=root/'dot-diagnostics-audio.u8';pcm.write_bytes(audio)
with runner.corpus.session_lock(device,5037):

 for name in tuple(ids['before']['diagnostic_overlay']['fixtures'])+('$$$ Royal - Mashup (103).milk','phat + EoS - Bass_responce_Red_Movements_Disorienting nebula3.milk','shifter - mosaic mitosis.milk','$$$ Royal - Mashup (137).milk','$$$ Royal - Mashup (11).milk','martin - city lights v2 c.milk','martin - city lights v2(1).milk','101.milk','Mig_304 - geiss remix 2.milk'):
  for role in ('before','after'):
   i=ids[role];preset_hash=i['diagnostic_overlay']['fixtures'].get(name) or hashlib.sha256((Path('core/src/main/assets/presets')/name).read_bytes()).hexdigest()
   for repeat in (0,1):
    request=runner.request(name,3840,2160,1280,720,0);request['expectedPresetCount']=9616
    directory=root/'captures'/('authored-followup-'+name.replace(' ','-').replace('.milk','')+'-'+role+'-'+str(repeat))
    runner.install_worker(device,i,user)
    installed=runner.shell(device,'pm','path','--user',user,i['package']).strip().splitlines()
    assert len(installed)==1 and installed[0].startswith('package:')
    assert hashlib.sha256(runner.adb(device,'exec-out','cat',installed[0][8:],binary=True)).hexdigest()==i['apk_sha256']
    m=runner.render(device,i,request,directory,pcm,preset_hash,user)
    print(json.dumps({'name':name,'role':role,'repeat':repeat,'status':m['status'],'canvas':m['nativeTrailsStatus'],'hashes':[c['rgbSha256'] for c in m['captures']]}),flush=True)
