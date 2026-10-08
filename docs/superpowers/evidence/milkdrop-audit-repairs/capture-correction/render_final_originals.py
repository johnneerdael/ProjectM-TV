from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/audit').resolve();device='emulator-5640';user=runner.current_user(device)
cases=[('I17','Happening.milk','p15','p16'),('I08','Mig_304 - geiss remix 2.milk','p16','p17'),('I22-mosaic','shifter - mosaic mitosis.milk','p17','p18'),('I22-stars','phat + EoS - Bass_responce_Red_Movements_Disorienting nebula3.milk','p17','p18'),('I31','suksma - type o negative - world coming down.milk','p18','p19'),('I05','163.milk','p20','p21'),('I06','Shreyas - Carnival loavthephysyq.milk','p20','p21'),('I19','$$$ Royal - Mashup (103).milk','p16','i19proposal')]
_,audio=runner.corpus.signal();pcm=root/'final-output-audio.u8';pcm.write_bytes(audio)
ids={label:json.loads((root/'final-capture-workers'/label/'identity.json').read_text()) for label in {v for row in cases for v in row[2:]}}
for i in ids.values():runner.check_artifacts(i)
for row in cases:assert (Path('core/src/main/assets/presets')/row[1]).is_file(),row[1]
with runner.corpus.session_lock(device,5037):
 for issue,name,before,after in cases:
  expected_hash=hashlib.sha256((Path('core/src/main/assets/presets')/name).read_bytes()).hexdigest()
  for role,label in [('before',before),('after',after)]:
   i=ids[label]
   for repeat in (0,1):
    request=runner.request(name,3840,2160,1280,720,0);directory=root/'captures'/('final-'+issue+'-'+role+'-'+str(repeat))
    if (directory/'manifest.json').exists():m=runner.verify(directory,request,expected_hash)
    else:
     runner.install_worker(device,i,user)
     installed=runner.shell(device,'pm','path','--user',user,i['package']).strip().splitlines();assert len(installed)==1 and installed[0].startswith('package:')
     assert hashlib.sha256(runner.adb(device,'exec-out','cat',installed[0][8:],binary=True)).hexdigest()==i['apk_sha256']
     m=runner.render(device,i,request,directory,pcm,expected_hash,user)
    assert all(c['captureReadFramebufferBinding']==0 for c in m['captures'])
    print(json.dumps({'issue':issue,'role':role,'repeat':repeat,'status':m['status'],'canvas':m['nativeTrailsStatus'],'prior_read_bindings':[c['previousReadFramebufferBinding'] for c in m['captures']],'hashes':[c['rgbSha256'] for c in m['captures']]}),flush=True)
