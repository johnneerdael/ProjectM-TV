import os,sys,json,subprocess,hashlib,math,struct,time
from pathlib import Path
import numpy as np
from PIL import Image
import argparse

sha=lambda data:hashlib.sha256(data).hexdigest()

def texture_inventory(root):
 if not root.is_dir():raise SystemExit('texture root unavailable: '+str(root))
 return {path.relative_to(root).as_posix():sha(path.read_bytes())
         for path in sorted(root.rglob('*')) if path.is_file()}

def texture_inventory_digest(inventory):
 return sha(json.dumps(inventory,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8'))

def verify_inputs(preset,pcm,textures,expected):
 current={'preset_sha256':sha(preset.read_bytes()),'pcm_sha256':sha(pcm.read_bytes()),
          'texture_inventory_sha256':texture_inventory_digest(texture_inventory(textures))}
 for key,value in current.items():
  if value!=expected[key]:raise SystemExit('capture input changed: '+key)

parser=argparse.ArgumentParser(description='Capture deterministic native master/main comparisons without changing production sources.')
parser.add_argument('--repo',type=Path,required=True)
parser.add_argument('--work',type=Path,required=True)
parser.add_argument('--name',required=True)
parser.add_argument('--preset',type=Path,required=True)
parser.add_argument('--frames',type=int,default=480)
parser.add_argument('--width',type=int,default=1280,choices=[1280,3840])
args=parser.parse_args()
repo=args.repo.resolve();root=args.work.resolve()
frames=args.frames
if frames<=0 or frames>480:parser.error('frames must be1..480')
w=args.width;h=w*9//16
name=args.name;preset=args.preset.resolve()
if not name or '/' in name or name in ('.','..'):parser.error('name must be a simple label')
jobdir=root/'captures'/name
jobdir.mkdir(parents=True,exist_ok=False)
t=np.arange(frames*1470)/44100
signal=((.4+.3*np.sin(2*np.pi*1.7*t)**2)*(.45*np.sin(2*np.pi*80*t)+.15*np.sin(2*np.pi*440*t)+.10*np.sin(2*np.pi*1600*t))).astype('<f4')
pcm=jobdir/'audio.f32';pcm.write_bytes(signal.tobytes())
selected={29,59,119,150,180,210,239,300,390,479}&set(range(frames))
textures=repo/'core/src/main/assets/textures'
inventory=texture_inventory(textures)
summary={'name':name,'preset_path':str(preset),'preset_sha256':sha(preset.read_bytes()),'pcm_sha256':sha(pcm.read_bytes()),'texture_root':str(textures),'texture_inventory':inventory,'texture_inventory_sha256':texture_inventory_digest(inventory),'width':w,'height':h,'frames':frames,'seed':12345,'roles':{}}
for role in ['upstream','patched']:
 identity=json.loads((root/role/'identity.json').read_text())
 if sha(Path(identity['worker']).read_bytes())!=identity['worker_sha256']:raise SystemExit('worker identity mismatch: '+role)
 hashes=[]
 for repeat in range(2):
  run=jobdir/f'{role}-{repeat}';run.mkdir(exist_ok=True)
  job={'schema_version':1,'config':{'width':w,'height':h,'fps':30,'warmup_seconds':0,'measurement_seconds':frames/30,'seed':12345,'line_reference_height':0,'line_antialiasing':False},'pcm_path':str(pcm),'preset_path':str(preset),'texture_root':str(textures),'bands_path':str(run/'bands.jsonl'),'manifest_path':str(run/'manifest.json'),'identity':identity}
  path=run/'job.json';path.write_text(json.dumps(job,indent=2))
  framehash=[]
  with (run/'diagnostics.txt').open('wb') as log:
   verify_inputs(preset,pcm,textures,summary)
   started=time.monotonic()
   process=subprocess.Popen([identity['worker'],'--job',str(path)],stdout=subprocess.PIPE,stderr=log,env=dict(os.environ,PRESET_LAB_SEED='12345'))
   for frame in range(frames):
    payload=bytearray()
    while len(payload)<w*h*3:
     piece=process.stdout.read(w*h*3-len(payload))
     if not piece:break
     payload.extend(piece)
    if len(payload)!=w*h*3:break
    framehash.append(sha(payload))
    if frame in selected and repeat==0:Image.frombytes('RGB',(w,h),bytes(payload)).save(run/f'frame-{frame:03d}.png')
   exitcode=process.wait()
   finished=time.monotonic()
   verify_inputs(preset,pcm,textures,summary)
  manifest=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else {}
  result={'exit':exitcode,'frames':len(framehash),'frame_sha256':framehash,'manifest':manifest,'wall_seconds':finished-started,'role':role,'repeat':repeat,'request':job,'inputs':{key:summary[key] for key in ('preset_sha256','pcm_sha256','texture_inventory_sha256')}}
  (run/'result.json').write_text(json.dumps(result,indent=2))
  if sha(Path(identity['worker']).read_bytes())!=identity['worker_sha256']:raise SystemExit('worker changed during capture')
  hashes.append(framehash)
  print(name,role,repeat,exitcode,len(framehash),manifest.get('gl_renderer'),flush=True)
  if exitcode or len(framehash)!=frames:raise SystemExit((run/'diagnostics.txt').read_text()[-4000:])
 summary['roles'][role]={'identity':identity,'repeat_equal':hashes[0]==hashes[1],'frame_sha256':hashes[0]}
 if hashes[0]!=hashes[1]:raise SystemExit('nonrepeatable role '+role)
summary['difference']={}
for frame in sorted(selected):
 a=np.asarray(Image.open(jobdir/'upstream-0'/f'frame-{frame:03d}.png'),dtype=np.int16)
 b=np.asarray(Image.open(jobdir/'patched-0'/f'frame-{frame:03d}.png'),dtype=np.int16)
 summary['difference'][str(frame)]={'mae':float(np.abs(a-b).mean()),'changed_pixels':int(np.any(a!=b,axis=2).sum())}
(jobdir/'comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
print('DONE',name,summary['difference'],flush=True)
