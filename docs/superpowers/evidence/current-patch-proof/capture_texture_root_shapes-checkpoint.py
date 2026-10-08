from pathlib import Path
import subprocess,json,hashlib,shlex
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];W=Path(__file__).resolve().parent;E=ROOT/'docs/superpowers/evidence/current-patch-proof'
A='/Users/jneerdael/Library/Android/sdk/platform-tools/adb';D='emulator-5630';R='/data/local/tmp/current-patch-proof'
def adb(*args):return subprocess.run([A,'-s',D,*args],capture_output=True,text=True,check=True,timeout=180).stdout
def sha(b):return hashlib.sha256(b).hexdigest()
fixture=E/'fixtures/texture-roots-shapes';adb('push',str(fixture),R+'/texture-roots-shapes');directory=W/'texture-root-shape-captures';directory.mkdir(exist_ok=False)
report={'patch':'0010','scope':'controlled duplicate-name roots, soft cut and reset; synthetic fixture','events':[{'frame':20,'texture_root':R+'/texture-roots-shapes/b'},{'frame':21,'load_preset':R+'/texture-roots-shapes/preset.milk','smooth':True},{'frame':40,'reset_textures':True}],'fixtures':{str(p.relative_to(fixture)):sha(p.read_bytes()) for p in fixture.rglob('*') if p.is_file()},'roles':{}}
for role in ['upstream','without-0010','patched']:
 binary=W/'events-build'/role/'patch-proof-worker';adb('push',str(binary),R+'/event-worker');rows=[]
 for repeat in range(2):
  d=directory/(role+'-'+str(repeat));d.mkdir();job=json.loads((W/'patched/job.json').read_text());job['preset_path']=R+'/texture-roots-shapes/preset.milk';job['texture_root']=R+'/texture-roots-shapes/a';job['events']=report['events'];job['identity']={'role':role,'case':'texture-roots-shapes','repeat':repeat};job['manifest_path']=R+'/manifest.json';job['bands_path']=R+'/bands.jsonl'
  (d/'job.json').write_text(json.dumps(job,indent=2));adb('push',str(d/'job.json'),R+'/job.json')
  cmd=shlex.join(['env','PRESET_LAB_SEED=12345',R+'/event-worker','--job',R+'/job.json'])+' > '+R+'/frames.rgb 2> '+R+'/render.log'
  p=subprocess.run([A,'-s',D,'shell',cmd],capture_output=True,text=True,timeout=180);adb('pull',R+'/render.log',str(d/'render.log'))
  if p.returncode:rows.append({'status':'failed','exit':p.returncode,'log':(d/'render.log').read_text()});continue
  adb('pull',R+'/manifest.json',str(d/'manifest.json'));m=json.loads((d/'manifest.json').read_text());assert m['status']=='success' and m['gl_error_frames']==0
  adb('pull',R+'/frames.rgb',str(d/'frames.rgb'));b=(d/'frames.rgb').read_bytes();size=512*288*3;assert len(b)==120*size
  hashes=[sha(b[i*size:(i+1)*size]) for i in range(120)];colors=[list(b[i*size+((144*512+256)*3):i*size+((144*512+256)*3)+3]) for i in range(120)]
  rows.append({'status':'success','manifest':m,'stream_sha256':sha(b),'frame_hashes':hashes,'center_rgb':colors})
  for frame in [19,20,21,30,40,41,59,81,119]:Image.frombytes('RGB',(512,288),b[frame*size:(frame+1)*size]).save(d/('frame-'+str(frame)+'.png'))
  (d/'frames.rgb').unlink()
 report['roles'][role]={'binary_sha256':sha(binary.read_bytes()),'runs':rows,'repeat_equal':all(x['status']=='success' for x in rows) and rows[0].get('frame_hashes')==rows[1].get('frame_hashes')}
if all(v['repeat_equal'] for v in report['roles'].values()):
 report['different_frames_without_patch']=sum(a!=b for a,b in zip(report['roles']['without-0010']['runs'][0]['frame_hashes'],report['roles']['patched']['runs'][0]['frame_hashes']))
 img=Image.new('RGB',(1536,640),'#171717');draw=ImageDraw.Draw(img)
 for row,frame in enumerate([40,59]):
  for col,role in enumerate(['upstream','without-0010','patched']):
   draw.text((col*512+8,row*320+8),role+'; frame '+str(frame),fill='white');img.paste(Image.open(directory/(role+'-0')/('frame-'+str(frame)+'.png')),(col*512,row*320+32))
 img.save(E/'0010-texture-roots-shapes.png');report['image']='0010-texture-roots-shapes.png'
(E/'texture-roots-shapes-results.json').write_text(json.dumps(report,indent=2)+'\n');print({r:v['repeat_equal'] for r,v in report['roles'].items()},report.get('different_frames_without_patch'),flush=True)
