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
pcm=root/'dot-diagnostics-audio.u8';assert hashlib.sha256(pcm.read_bytes()).hexdigest()=='14a59e75249dee0dd15d74487688c248c6a4a4b24a843b6d6f612ccc5c408dbc'

import subprocess
# Run only after all build/test/correctness jobs are terminal; retain a workload snapshot.
snapshot=subprocess.run(['ps','-axo','pid,command'],check=True,capture_output=True,text=True).stdout
blocked=[line for line in snapshot.splitlines() if any(k in line for k in ('cmake --build','ctest --test-dir','GradleDaemon','clang++ -','run_mutant.sh','run_mesa')) and 'ps -axo' not in line and 'run_combined_cost.py' not in line]
# Idle Gradle daemons are stopped by the root before starting this measurement.
assert not blocked,blocked
containers=subprocess.run(['docker','ps','--format','{{.Names}}'],check=True,capture_output=True,text=True).stdout
assert not containers.strip(),containers
(root/'combined-cost-host-processes.txt').write_text(snapshot)
case_names=('$$$ Royal - Mashup (103).milk','shifter - mosaic mitosis.milk','$$$ Royal - Mashup (137).milk','martin - city lights v2 c.milk','martin - city lights v2(1).milk','audit followup uv custom-feedback.milk','audit followup uv all-disabled.milk')
with runner.corpus.session_lock(device,5037):
 for index,name in enumerate(case_names):
  for cycle in range(3):
   for step,role in enumerate(('before','after','after','before')):
    i=ids[role];preset_hash=i['diagnostic_overlay']['fixtures'].get(name) or hashlib.sha256((Path('core/src/main/assets/presets')/name).read_bytes()).hexdigest()
    runner.install_worker(device,i,user)
    installed=runner.shell(device,'pm','path','--user',user,i['package']).strip().splitlines()
    assert len(installed)==1 and installed[0].startswith('package:')
    assert hashlib.sha256(runner.adb(device,'exec-out','cat',installed[0][8:],binary=True)).hexdigest()==i['apk_sha256']
    request=runner.request(name,3840,2160,1280,720,0);request['expectedPresetCount']=9616
    directory=root/'cost'/('combined-'+str(index)+'-'+str(cycle)+'-'+str(step)+'-'+role)
    m=runner.render(device,i,request,directory,pcm,preset_hash,user)
    assert m['glRenderer']=='Android Emulator OpenGL ES Translator (Apple M4 Pro)'
    print(json.dumps({'name':name,'index':index,'cycle':cycle,'step':step,'role':role,'mean_ms':m['serializedFrameMeanMs'],'p90_ms':m['serializedFrameP90Ms'],'status':m['status'],'manifest':str(directory/'manifest.json'),'apk_sha256':i['apk_sha256']}),flush=True)
