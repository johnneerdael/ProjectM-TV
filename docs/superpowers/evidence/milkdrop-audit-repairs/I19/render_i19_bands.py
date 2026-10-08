from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/audit').resolve(); device='emulator-5640'
text=runner.shell(device,'am','get-current-user').strip()
if not text.isdecimal():raise ValueError('invalid user')
user=int(text)
identities={'before':json.loads((root/'workers/rebase-candidate/identity.json').read_text()),'after':json.loads((root/'i19-workers/candidate-native/identity.json').read_text())}
for identity in identities.values():runner.check_artifacts(identity)
assert len({i['assets_sha256'] for i in identities.values()})==1
pcm=root/'i19-api34-audio.u8';assert hashlib.sha256(pcm.read_bytes()).hexdigest()=='14a59e75249dee0dd15d74487688c248c6a4a4b24a843b6d6f612ccc5c408dbc'
name='$$$ Royal - Mashup (103).milk';h=hashlib.sha256((Path('core/src/main/assets/presets')/name).read_bytes()).hexdigest()
profiles=[('authored256',256,144,0,0,-1),('authored1024',1024,768,0,0,-1),('authored1280',1280,720,0,0,-1),('fallback720',1280,720,1024,768,0),('fallback1080',1920,1080,1024,768,0),('native1440',2560,1440,1280,720,0)]
with runner.corpus.session_lock(device,5037):
 for profile,w,ht,rw,rh,level in profiles:
  for role,repeat in [('before',0),('after',0),('after',1),('before',1)]:
   directory=root/'captures'/('i19-band-'+profile+'-'+role+'-'+str(repeat))
   m=runner.render(device,identities[role],runner.request(name,w,ht,rw,rh,level),directory,pcm,h,user)
   if profile=='native1440':assert m['nativeTrailsStatus']=='Standard · 1280×720 canvas',m['nativeTrailsStatus']
   print(json.dumps({'profile':profile,'role':role,'repeat':repeat,'status':m['status'],'trails':m['nativeTrailsStatus'],'mean_ms':m['serializedFrameMeanMs']}),flush=True)
