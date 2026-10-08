from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/audit').resolve();device='emulator-5640';user=runner.current_user(device)
cases=[('I20-circle','$$$ Royal - Mashup (137).milk','i12-workers/candidate-native','circle-workers/candidate-native')]
_,audio=runner.corpus.signal();pcm=root/'warp-cost-audio.u8';pcm.write_bytes(audio)
with runner.corpus.session_lock(device,5037):
 for issue,name,before,after in cases:
  ids={role:json.loads((root/path/'identity.json').read_text()) for role,path in [('before',before),('after',after)]}
  for i in ids.values():runner.check_artifacts(i)
  expected=hashlib.sha256((Path('core/src/main/assets/presets')/name).read_bytes()).hexdigest()
  for cycle in range(3):
   for step,role in enumerate(('before','after','after','before')):
    i=ids[role];runner.install_worker(device,i,user);paths=runner.shell(device,'pm','path','--user',user,i['package']).strip().splitlines();assert len(paths)==1 and paths[0].startswith('package:');assert hashlib.sha256(runner.adb(device,'exec-out','cat',paths[0][8:],binary=True)).hexdigest()==i['apk_sha256']
    directory=root/'captures'/('warp-clean-'+issue+'-'+str(cycle)+'-'+str(step)+'-'+role);m=runner.render(device,i,runner.request(name,3840,2160,1280,720,0),directory,pcm,expected,user)
    print(json.dumps({'issue':issue,'cycle':cycle,'step':step,'role':role,'mean_ms':m['serializedFrameMeanMs'],'p90_ms':m['serializedFrameP90Ms'],'status':m['status']}),flush=True)
