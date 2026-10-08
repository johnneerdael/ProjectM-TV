from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/audit').resolve(); device='emulator-5640'
user_text=runner.shell(device,'am','get-current-user').strip()
if not user_text.isdecimal(): raise ValueError('Invalid Android user')
user=int(user_text)
identities={role:json.loads((root/'workers'/role/'identity.json').read_text()) for role in ('rebase-baseline','rebase-candidate')}
for identity in identities.values(): runner.check_artifacts(identity)
assert len({i['assets_sha256'] for i in identities.values()})==1
_,audio=runner.corpus.signal(); pcm=root/'i17-api34-audio.u8'; pcm.write_bytes(audio)
name='Happening.milk'; preset_hash=hashlib.sha256((Path('core/src/main/assets/presets')/name).read_bytes()).hexdigest()
with runner.corpus.session_lock(device,5037):
 for identity in identities.values(): runner.adb(device,'install','--user',user,identity['apk'])
 for role,repeat in [('rebase-baseline',0),('rebase-candidate',0),('rebase-candidate',1),('rebase-baseline',1)]:
  identity=identities[role]; label='before' if role=='rebase-baseline' else 'after'
  directory=root/'captures'/('i17-api34-'+label+'-'+str(repeat))
  manifest=runner.render(device,identity,runner.request(name,3840,2160,1280,720,0),directory,pcm,preset_hash,user)
  assert manifest['nativeTrailsStatus']=='Standard · 1280×720 canvas',manifest['nativeTrailsStatus']
  print(json.dumps({'role':role,'repeat':repeat,**{key:manifest.get(key) for key in ('status','framesRendered','glRenderer','nativeTrailsStatus','serializedFrameMeanMs','serializedFrameP90Ms','pssAfterFramesKB')}}),flush=True)
