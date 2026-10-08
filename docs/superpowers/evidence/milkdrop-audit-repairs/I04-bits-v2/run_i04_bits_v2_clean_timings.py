from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/audit').resolve();device='emulator-5640';user=runner.current_user(device)
names=json.loads((root/'i04-bits-v2-diagnostics/before/identity.json').read_text())['diagnostic_overlay']['fixtures']
cases=[('I04-bits-v2-'+str(n),name,'i04-bits-v2-diagnostics/before','i04-bits-v2-diagnostics/after') for n,name in enumerate(names) if 'runtime-' in name]
_,audio=runner.corpus.signal();pcm=root/'warp-cost-audio.u8';pcm.write_bytes(audio)
with runner.corpus.session_lock(device,5037):
 for issue,name,before,after in cases:
  ids={role:json.loads((root/path/'identity.json').read_text()) for role,path in [('before',before),('after',after)]}
  for i in ids.values():
   for key in ('aar','apk'):assert hashlib.sha256(Path(i[key]).read_bytes()).hexdigest()==i[key+'_sha256']
  expected=ids['before']['diagnostic_overlay']['fixtures'][name]
  for cycle in range(3):
   for step,role in enumerate(('before','after','after','before')):
    i=ids[role];runner.install_worker(device,i,user);paths=runner.shell(device,'pm','path','--user',user,i['package']).strip().splitlines();assert len(paths)==1 and paths[0].startswith('package:');assert hashlib.sha256(runner.adb(device,'exec-out','cat',paths[0][8:],binary=True)).hexdigest()==i['apk_sha256']
    directory=root/'captures'/('warp-clean-'+issue+'-'+str(cycle)+'-'+str(step)+'-'+role);request=runner.request(name,3840,2160,1280,720,0);request['expectedPresetCount']=9611;m=runner.render(device,i,request,directory,pcm,expected,user)
    print(json.dumps({'issue':issue,'cycle':cycle,'step':step,'role':role,'mean_ms':m['serializedFrameMeanMs'],'p90_ms':m['serializedFrameP90Ms'],'status':m['status']}),flush=True)
