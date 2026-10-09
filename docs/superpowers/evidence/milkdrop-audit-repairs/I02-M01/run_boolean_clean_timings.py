from pathlib import Path
import sys,json,hashlib,zipfile
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/audit').resolve();device='emulator-5640';text=runner.shell(device,'am','get-current-user').strip();assert text.isdecimal();user=int(text)
ids={role:json.loads((root/'boolean-diagnostics'/role/'identity.json').read_text()) for role in ('before','after')}
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
 name='audit m01-wave--1.milk'
 for cycle in range(3):
  for step,role in enumerate(('before','after','after','before')):
   i=ids[role];runner.install_worker(device,i,user)
   installed=runner.shell(device,'pm','path','--user',user,i['package']).strip().splitlines();assert len(installed)==1 and installed[0].startswith('package:')
   assert hashlib.sha256(runner.adb(device,'exec-out','cat',installed[0][8:],binary=True)).hexdigest()==i['apk_sha256']
   request=runner.request(name,3840,2160,1280,720,0);request['expectedPresetCount']=9612
   directory=root/'captures'/('bool-clean-'+str(cycle)+'-'+str(step)+'-'+role)
   m=runner.render(device,i,request,directory,pcm,i['diagnostic_overlay']['fixtures'][name],user)
   print(json.dumps({'cycle':cycle,'step':step,'role':role,'mean_ms':m['serializedFrameMeanMs'],'p90_ms':m['serializedFrameP90Ms'],'status':m['status']}),flush=True)
