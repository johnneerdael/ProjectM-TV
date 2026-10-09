from pathlib import Path
import json,subprocess,os,hashlib
import numpy as np
from PIL import Image
repo=Path(__file__).resolve().parents[2];root=Path(__file__).resolve().parent
pcm=repo/'docs/superpowers/evidence/patch-visual-catalog/audio/frozen-480-frames.f32'
profiles={'classic':{'line_reference_height':0,'line_antialiasing':False,'feedback_detail':-1.0},'standard':{'line_reference_height':720,'line_antialiasing':True,'feedback_detail':0.0}}
results={}
for profile,settings in profiles.items():
 results[profile]={}
 for role in ['with-0019','without-0019']:
  hashes=[]
  for repeat in range(2):
   folder=root/'visual'/f'{profile}-{role}-{repeat}';folder.mkdir(parents=True,exist_ok=False)
   job={'schema_version':1,'config':{'width':3840,'height':2160,'fps':30,'warmup_seconds':4,'measurement_seconds':12,'seed':12345,**settings},'pcm_path':str(pcm),'preset_path':str(root/'original.milk'),'texture_root':str(repo/'core/src/main/assets/textures'),'manifest_path':str(folder/'manifest.json'),'identity':{'role':role,'kind':'selected-frame verification, outside timedjobs'}}
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
   hashes.append(frames)
  assert hashes[0]==hashes[1]
  results[profile][role]={'repeat_equal':True,'hashes':hashes}
 results[profile]['frame_differences']={}
 for f in [119,239,479]:
  before=np.asarray(Image.open(root/'visual'/f'{profile}-without-0019-0'/f'frame-{f:03d}.png'),dtype=np.int16)
  after=np.asarray(Image.open(root/'visual'/f'{profile}-with-0019-0'/f'frame-{f:03d}.png'),dtype=np.int16)
  delta=np.abs(after-before)
  results[profile]['frame_differences'][str(f)]={'total_rgb_difference':int(delta.sum()),'changed_pixels':int(np.any(delta>0,axis=2).sum()),'max_channel_difference':int(delta.max()),'mae':float(delta.mean())}
 print(profile,results[profile]['frame_differences'],flush=True)
(root/'visual-results.json').write_text(json.dumps(results,indent=2)+'\n')
