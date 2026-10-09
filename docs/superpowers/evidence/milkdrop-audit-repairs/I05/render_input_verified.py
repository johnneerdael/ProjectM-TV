from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/audit').resolve(); device='emulator-5640'
user_text=runner.shell(device,'am','get-current-user').strip()
if not user_text.isdecimal(): raise ValueError('Invalid Android user')
user=int(user_text)
identities={'before':json.loads((root/'i09-workers/candidate-native/identity.json').read_text()),'after':json.loads((root/'input-workers/candidate-native/identity.json').read_text())}
for identity in identities.values(): runner.check_artifacts(identity)
assert len({i['assets_sha256'] for i in identities.values()})==1
_,audio=runner.corpus.signal(); pcm=root/'i22-api34-audio.u8'; pcm.write_bytes(audio)
with runner.corpus.session_lock(device,5037):
 for identity in identities.values(): runner.adb(device,'install','-r','--user',user,identity['apk'])
 for name in ('163.milk','Shreyas - Carnival loavthephysyq.milk'):
  preset_hash=hashlib.sha256((Path('core/src/main/assets/presets')/name).read_bytes()).hexdigest()
  for role,repeat in [('before',0),('after',0),('after',1),('before',1)]:
   identity=identities[role]; label=role
   runner.install_worker(device,identity,user)
   installed=runner.shell(device,'pm','path','--user',user,identity['package']).strip().splitlines()
   assert len(installed)==1 and installed[0].startswith('package:')
   assert hashlib.sha256(runner.adb(device,'exec-out','cat',installed[0][8:],binary=True)).hexdigest()==identity['apk_sha256']
   directory=root/'captures'/('verified-input4k-'+('aspect' if name=='163.milk' else 'readonly')+'-'+label+'-'+str(repeat))
   manifest=runner.render(device,identity,runner.request(name,3840,2160,1280,720,0),directory,pcm,preset_hash,user)
   assert manifest['nativeTrailsStatus']=='Standard · 1280×720 canvas',manifest['nativeTrailsStatus']
   print(json.dumps({'role':role,'repeat':repeat,**{key:manifest.get(key) for key in ('status','framesRendered','glRenderer','nativeTrailsStatus','serializedFrameMeanMs','serializedFrameP90Ms','pssAfterFramesKB')}}),flush=True)
