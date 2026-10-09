from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/audit').resolve();device='emulator-5640';user=runner.current_user(device)
ids={role:json.loads((root/({'before':'i12-workers/candidate-native','after':'i13-workers/candidate-native'}[role])/'identity.json').read_text()) for role in ('before','after')}
for i in ids.values():runner.check_artifacts(i)
_,audio=runner.corpus.signal();pcm=root/'i12-audio.u8';pcm.write_bytes(audio)
names=('Liquido.milk','Bmelgren - Liquirdo 2.milk')
with runner.corpus.session_lock(device,5037):
 for name in names:
  expected_hash=hashlib.sha256((Path('core/src/main/assets/presets')/name).read_bytes()).hexdigest()
  for role,repeat in [('before',0),('after',0),('after',1),('before',1)]:
   i=ids[role];runner.install_worker(device,i,user)
   paths=runner.shell(device,'pm','path','--user',user,i['package']).strip().splitlines();assert len(paths)==1 and paths[0].startswith('package:')
   assert hashlib.sha256(runner.adb(device,'exec-out','cat',paths[0][8:],binary=True)).hexdigest()==i['apk_sha256']
   request=runner.request(name,3840,2160,1280,720,0);directory=root/'captures'/('i13-original-'+name.replace(' ','-').replace('.milk','')+'-'+role+'-'+str(repeat))
   m=runner.render(device,i,request,directory,pcm,expected_hash,user)
   print(json.dumps({'name':name,'role':role,'repeat':repeat,'status':m['status'],'canvas':m['nativeTrailsStatus'],'hashes':[c['rgbSha256'] for c in m['captures']]}),flush=True)
