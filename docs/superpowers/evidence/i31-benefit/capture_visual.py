from pathlib import Path
import json,subprocess,os,hashlib
import numpy as np
from PIL import Image
import argparse
parser=argparse.ArgumentParser(description='Run isolated selected-frame checks with restored caller readback state.')
parser.add_argument('--repo',type=Path,required=True)
parser.add_argument('--work',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
repo=args.repo.resolve();root=args.work.resolve();output=args.output.resolve()
output.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(preset,pcm,textures):
 inventory={p.relative_to(textures).as_posix():sha(p) for p in sorted(textures.rglob('*')) if p.is_file()}
 return {'preset_sha256':sha(preset),'pcm_sha256':sha(pcm),'texture_inventory':inventory}
records={}
harness={p.relative_to(root/'image-harness').as_posix():sha(p) for p in sorted((root/'image-harness').rglob('*')) if p.is_file()}
harness.setdefault('CMakeLists.txt',sha(root/'harness/CMakeLists.txt'))
visual_workers={role:{'observer_worker_sha256':sha(root/role/'image-worker'),'engine_library_sha256':sha(root/role/'native-build/projectm/src/libprojectM/libprojectM-4.a'),'harness':harness} for role in ['with-0019','without-0019']}
(output/'visual-workers.json').write_text(json.dumps(visual_workers,indent=2)+'\n')
pcm=repo/'docs/superpowers/evidence/patch-visual-catalog/audio/frozen-480-frames.f32'
profiles={'classic':{'line_reference_height':0,'line_antialiasing':False,'feedback_detail':-1.0},'standard':{'line_reference_height':720,'line_antialiasing':True,'feedback_detail':0.0}}
results={}
for profile,settings in profiles.items():
 results[profile]={}
 for role in ['with-0019','without-0019']:
  hashes=[]
  for repeat in range(2):
   folder=output/'visual'/f'{profile}-{role}-{repeat}';folder.mkdir(parents=True,exist_ok=False)
   job={'schema_version':1,'config':{'width':3840,'height':2160,'fps':30,'warmup_seconds':4,'measurement_seconds':12,'seed':12345,**settings},'pcm_path':str(pcm),'preset_path':str(root/'original.milk'),'texture_root':str(repo/'core/src/main/assets/textures'),'manifest_path':str(folder/'manifest.json'),'identity':{'role':role,'kind':'selected-frame verification, outside timedjobs'}}
   before=snapshot(root/'original.milk',pcm,repo/'core/src/main/assets/textures')
   worker=root/role/'image-worker';library=root/role/'native-build/projectm/src/libprojectM/libprojectM-4.a'
   worker_hash=sha(worker);library_hash=sha(library)
   job['identity'].update(observer_worker_sha256=worker_hash,engine_library_sha256=library_hash)
   (folder/'job.json').write_text(json.dumps(job,indent=2)+'\n')
   with (folder/'stderr.txt').open('wb') as log:
    proc=subprocess.Popen([str(root/role/'image-worker'),'--job',str(folder/'job.json')],stdout=subprocess.PIPE,stderr=log,env=dict(os.environ,PRESET_LAB_SEED='12345'))
    frames=[]
    for f in [119,239,479]:
     data=bytearray()
     while len(data)<3840*2160*3:
      part=proc.stdout.read(3840*2160*3-len(data))
      if not part:break
      data.extend(part)
     assert len(data)==3840*2160*3
     frames.append(hashlib.sha256(data).hexdigest())
     if repeat==0:Image.frombytes('RGB',(3840,2160),bytes(data)).save(folder/f'frame-{f:03d}.png')
    assert proc.wait()==0
   manifest=json.loads((folder/'manifest.json').read_text());assert manifest['status']=='success' and manifest['gl_error_frames']==0
   after=snapshot(root/'original.milk',pcm,repo/'core/src/main/assets/textures')
   if before!=after or sha(worker)!=worker_hash or sha(library)!=library_hash:raise RuntimeError('visual input/worker/library changed')
   states=manifest['readback_states']
   if len(states)!=3 or [x['frame'] for x in states]!=[119,239,479]:raise RuntimeError('missing readback state')
   for state in states:
    for field in ['read_framebuffer','read_buffer','pack_alignment']:
     if state['before_'+field]!=state['after_'+field]:raise RuntimeError('observer changed caller state')
   records[f'{profile}-{role}-{repeat}']={'job':job,'manifest':manifest,'inputs_before':before,'inputs_after':after,'observer_worker_sha256':worker_hash,'linked_engine_library_sha256':library_hash,'frame_sha256':frames,'observer_harness':harness,'selected_pngs':{p.name:sha(p) for p in folder.glob('*.png')}}
   hashes.append(frames)
  assert hashes[0]==hashes[1]
  results[profile][role]={'repeat_equal':True,'hashes':hashes}
 results[profile]['frame_differences']={}
 for f in [119,239,479]:
  before=np.asarray(Image.open(output/'visual'/f'{profile}-without-0019-0'/f'frame-{f:03d}.png'),dtype=np.int16)
  after=np.asarray(Image.open(output/'visual'/f'{profile}-with-0019-0'/f'frame-{f:03d}.png'),dtype=np.int16)
  delta=np.abs(after-before)
  results[profile]['frame_differences'][str(f)]={'total_rgb_difference':int(delta.sum()),'changed_pixels':int(np.any(delta>0,axis=2).sum()),'max_channel_difference':int(delta.max()),'mae':float(delta.mean())}
 print(profile,results[profile]['frame_differences'],flush=True)
(output/'visual-jobs.json').write_text(json.dumps(records,indent=2)+'\n')
(output/'visual-results.json').write_text(json.dumps(results,indent=2)+'\n')
