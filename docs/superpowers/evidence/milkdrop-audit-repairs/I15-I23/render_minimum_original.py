from pathlib import Path
import sys,json,hashlib,zipfile
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/audit').resolve();device='emulator-5640';text=runner.shell(device,'am','get-current-user').strip();assert text.isdecimal();user=int(text)
ids={role:json.loads((root/path/'identity.json').read_text()) for role,path in [('before','retained-policy-workers/candidate-native'),('after','minimum-oracle-native-workers/candidate-native')]}
for i in ids.values():runner.check_artifacts(i)
_,audio=runner.corpus.signal();pcm=root/'dot-diagnostics-audio.u8';pcm.write_bytes(audio)
with runner.corpus.session_lock(device,5037):

 for name in ('Rovastar - Parallelogram Bin 2.milk',):
  for role in ('before','after'):
   i=ids[role];preset_hash=hashlib.sha256((Path('core/src/main/assets/presets')/name).read_bytes()).hexdigest()
   for repeat in (0,1):
    request=runner.request(name,3840,2160,1280,720,0);request['expectedPresetCount']=9606
    directory=root/'captures'/('minimum-original-'+name.replace(' ','-').replace('.milk','')+'-'+role+'-'+str(repeat))
    runner.install_worker(device,i,user)
    installed=runner.shell(device,'pm','path','--user',user,i['package']).strip().splitlines()
    assert len(installed)==1 and installed[0].startswith('package:')
    assert hashlib.sha256(runner.adb(device,'exec-out','cat',installed[0][8:],binary=True)).hexdigest()==i['apk_sha256']
    m=runner.render(device,i,request,directory,pcm,preset_hash,user)
    print(json.dumps({'name':name,'role':role,'repeat':repeat,'status':m['status'],'canvas':m['nativeTrailsStatus'],'hashes':[c['rgbSha256'] for c in m['captures']]}),flush=True)
