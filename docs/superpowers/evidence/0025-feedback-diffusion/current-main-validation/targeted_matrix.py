import json,os,subprocess,importlib.util,zipfile,hashlib
from pathlib import Path
from types import SimpleNamespace
ROOT=Path.cwd()
provider=ROOT/'docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/run.py'
spec=importlib.util.spec_from_file_location('core_provider',provider); runner=importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
serial='emulator-5582'; launch=ROOT/'build/native-4k-current-main/emulator/launch.json'
def validate_serial(value):
 if value!=serial: raise ValueError('Only this task emulator-5582 is allowed')
 return value
def guard(value):
 validate_serial(value); owned=json.loads(launch.read_text()); os.kill(owned['pid'],0)
 command=subprocess.check_output(['ps','-p',str(owned['pid']),'-o','command='],text=True)
 if '-port 5582' not in command or 'ProjectM_Native4K_API34_20261004' not in command: raise ValueError('Owned emulator PID mismatch')
 if subprocess.check_output(['adb','-s',serial,'shell','getprop','ro.kernel.qemu'],text=True).strip()!='1': raise ValueError('Target is not the owned emulator')
 return owned
runner.validate_device=validate_serial; runner.require_owned_emulator=guard
guard(serial)
work=ROOT/'build/native-4k-current-main/targeted-matrix'; work.mkdir(exist_ok=False)
corpus=runner.inventory(); roles={}
for role,count in [('baseline',29),('candidate',30)]:
 record=json.loads((ROOT/'build/follow-ups/core-corpus'/('worker-'+role+'.json')).read_text()); apk=Path(record['apk'])
 if runner.file_hash(apk)!=record['apk_sha256']: raise ValueError('APK changed')
 identity=record['backend_identity']
 with zipfile.ZipFile(apk) as z:
  assert json.loads(z.read('assets/backend-identity.json'))==identity
  core=hashlib.sha256(z.read(identity['core_library_entry'])).hexdigest();assert core==identity['core_sha256']
 assert len(identity['ordered_patches'])==count
 roles[role]={'apk_path':str(apk),'apk_sha256':record['apk_sha256'],'core_sha256':core,'backend_identity':identity,'backend_identity_sha256':runner.digest(identity)}
runner.validate_observer_pair(roles['baseline'],roles['candidate'])
assert roles['baseline']['backend_identity']['ordered_patches']==roles['candidate']['backend_identity']['ordered_patches'][:29]
assert roles['baseline']['backend_identity']['original_core_source_sha256']==roles['candidate']['backend_identity']['original_core_source_sha256']
pcm=runner.prepare_pcm(work/'signals')
names=['$$$ Royal - Mashup (191).milk','Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk','Fed - quadratrail.milk']
# Match the bundled Cartoon name exactly, without changing its bytes.
names += [p['path'] for p in corpus['presets'] if 'I Like Cartoon' in p['path'] and 'Isosceles' in p['path']][:1]
records=[next(p for p in corpus['presets'] if p['path']==name) for name in names]
base={'backend':'actual ProjectM TV core production JNI/GLES3','device_serial':serial,'roles':roles,'pcm':pcm,'provider_sha256':runner.file_hash(provider),'adapter_sha256':runner.file_hash(Path(__file__)),'ownership':json.loads(launch.read_text()),'scope':'targeted current-main29 versus diffusion30; near-reference uses normal core reference1024x768, not no-reference classic'}
profiles=[('near-reference',1182,665),('1330',2364,1330),('2160',3840,2160)]
protocols={}
for label,w,h in profiles:
 protocol=dict(base,config={'width':w,'height':h,'fps':30,'warmup_frames':120,'measurement_frames':360},profile=label)
 protocol['sha256']=runner.digest(protocol);protocols[label]=protocol
 directory=work/label;directory.mkdir();runner.atomic(directory/'protocol.json',protocol)
original_job=runner.make_job
picks=[120,150,180,210,239,300,390,479]
def make_job(protocol,*args):
 job=original_job(protocol,*args);job.update(width=protocol['config']['width'],height=protocol['config']['height'],capture_frames=picks)
 return job
runner.make_job=make_job
# Use role blocks to avoid repeated package installs; all jobs still have fresh processes.
for role in ('baseline','candidate'):
 runner.install_role(serial,roles[role],work)
 for label,_,_ in profiles:
  args=SimpleNamespace(work=work/label,timeout=300)
  for record in records:
   for repeat in (1,2):
    row=runner.run_one(args,protocols[label],record,role,'selected',repeat,360,native=True)
    print(runner.canonical({'profile':label,'preset':record['path'],**{k:row.get(k) for k in ('role','repeat','status','error','elapsed_seconds')}}),flush=True)
    if row['status']!='success': raise RuntimeError('Actual-core targeted validation failed; retain artifacts')
print('Targeted matrix finished',flush=True)
