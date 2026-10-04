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
work=ROOT/'build/native-4k-current-main/placement-controls';work.mkdir(exist_ok=False)
corpus=runner.inventory();pcm=runner.prepare_pcm(work/'signals')
names=['$$$ Royal - Mashup (191).milk','Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk','Fed - quadratrail.milk']
records=[next(p for p in corpus['presets'] if p['path']==n) for n in names]
original_job=runner.make_job
picks=[120,150,180,210,239,300,390,479]
def make_job(protocol,*args):
 job=original_job(protocol,*args);job.update(width=protocol['config']['width'],height=protocol['config']['height'],capture_frames=picks);return job
runner.make_job=make_job
for variant,metadata in [('fixed-p2',ROOT/'build/follow-ups/core-corpus/worker-candidate.json'),('p1',ROOT/'build/native-4k-current-main/p1-experiment/worker-candidate.json')]:
 w=json.loads(metadata.read_text());identity=w['backend_identity'];apk=Path(w['apk']);assert runner.file_hash(apk)==w['apk_sha256']
 role={'apk_path':str(apk),'apk_sha256':w['apk_sha256'],'core_sha256':identity['core_sha256'],'backend_identity':identity,'backend_identity_sha256':runner.digest(identity)}
 runner.install_role(serial,role,work)
 for label,width,height in [('1330',2364,1330),('2160',3840,2160)]:
  directory=work/(variant+'-'+label);directory.mkdir()
  protocol={'backend':'actual ProjectM TV core production JNI/GLES3','device_serial':serial,'roles':{'candidate':role},'config':{'width':width,'height':height},'pcm':pcm,'variant':variant,'provider_sha256':runner.file_hash(provider),'adapter_sha256':runner.file_hash(Path(__file__)),'scope':'placement causal control; input clock and core wrapper preserved'}
  protocol['sha256']=runner.digest(protocol);runner.atomic(directory/'protocol.json',protocol)
  args=SimpleNamespace(work=directory,timeout=300)
  for record in records:
   for repeat in (1,2):
    row=runner.run_one(args,protocol,record,'candidate','selected',repeat,360,native=True)
    print(runner.canonical({'variant':variant,'profile':label,'preset':record['path'],**{k:row.get(k) for k in ('repeat','status','error','elapsed_seconds')}}),flush=True)
    if row['status']!='success':raise RuntimeError('Placement control failed')
print('Placement controls complete',flush=True)
