from pathlib import Path
import subprocess,json,hashlib,shlex
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];W=Path(__file__).resolve().parent;E=ROOT/'docs/superpowers/evidence/current-patch-proof'
A='/Users/jneerdael/Library/Android/sdk/platform-tools/adb';D='emulator-5630';R='/data/local/tmp/current-patch-proof'
def adb(*args):return subprocess.run([A,'-s',D,*args],capture_output=True,text=True,check=True,timeout=180).stdout
def sha(b):return hashlib.sha256(b).hexdigest()
current={c['case']:c for c in json.loads((E/'capture-results.json').read_text())}
reports=[]
for number,key in [(4,'0004-sampler'),(6,'0006-zoom'),(7,'0007-wave'),(8,'0008-display'),(11,'0011-rotation')]:
 role='without-'+str(number).zfill(4);binary=W/'ablations'/role/'ndk-build/patch-proof-worker';assert binary.is_file()
 adb('push',str(binary),R+'/without');c=current[key];preset=ROOT/'core/src/main/assets/presets'/c['preset'];adb('push',str(preset),R+'/witness.milk')
 directory=W/'ablation-captures'/key;directory.mkdir(parents=True,exist_ok=False);rows=[]
 for repeat in range(2):
  d=directory/str(repeat);d.mkdir();job=json.loads((W/'patched/job.json').read_text());job['identity']={'role':role,'case':key,'repeat':repeat};job['manifest_path']=R+'/manifest.json';job['bands_path']=R+'/bands.jsonl'
  (d/'job.json').write_text(json.dumps(job,indent=2));adb('push',str(d/'job.json'),R+'/job.json')
  cmd=shlex.join(['env','PRESET_LAB_SEED=12345',R+'/without','--job',R+'/job.json'])+' > '+R+'/frames.rgb 2> '+R+'/render.log'
  p=subprocess.run([A,'-s',D,'shell',cmd],capture_output=True,text=True,timeout=180);adb('pull',R+'/render.log',str(d/'render.log'))
  if p.returncode:rows.append({'status':'failed','exit':p.returncode,'log':(d/'render.log').read_text()});continue
  adb('pull',R+'/manifest.json',str(d/'manifest.json'));m=json.loads((d/'manifest.json').read_text());assert m['status']=='success' and m['gl_error_frames']==0
  adb('pull',R+'/frames.rgb',str(d/'frames.rgb'));b=(d/'frames.rgb').read_bytes();size=512*288*3;assert len(b)==120*size
  hashes=[sha(b[i*size:(i+1)*size]) for i in range(120)];rows.append({'status':'success','manifest':m,'stream_sha256':sha(b),'frame_hashes':hashes})
  for frame in [29,59,119]:Image.frombytes('RGB',(512,288),b[frame*size:(frame+1)*size]).save(d/('frame-'+str(frame)+'.png'))
  (d/'frames.rgb').unlink()
 report={'patch':str(number).zfill(4),'preset':c['preset'],'preset_sha256':c['preset_sha256'],'binary_sha256':sha(binary.read_bytes()),'method':'current capture engine minus exactly one patch; binary-cache export disabled in both','runs':rows,'repeat_equal':all(x['status']=='success' for x in rows) and rows[0].get('frame_hashes')==rows[1].get('frame_hashes')}
 if report['repeat_equal']:
  target=c['roles']['patched']['runs'][0]['frame_hashes'];report['different_frames']=sum(x!=y for x,y in zip(rows[0]['frame_hashes'],target));img=Image.new('RGB',(1024,320),'#171717');draw=ImageDraw.Draw(img)
  img.paste(Image.open(directory/'0/frame-119.png'),(0,32));img.paste(Image.open(W/'captures-v2'/key/'patched-0/frame-119.png'),(512,32));draw.text((8,8),'Current series without '+str(number).zfill(4)+'; cache off',fill='white');draw.text((520,8),'Current series with '+str(number).zfill(4)+'; cache off',fill='white');img.save(E/(key+'-isolated.png'));report['image']=key+'-isolated.png';report['frame']=119
 reports.append(report);(E/'ablation-results.json').write_text(json.dumps(reports,indent=2)+'\n');print(key,report['repeat_equal'],report.get('different_frames'),flush=True)
