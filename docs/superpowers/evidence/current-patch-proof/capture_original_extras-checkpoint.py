from pathlib import Path
import subprocess,json,hashlib,shlex
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];W=Path(__file__).resolve().parent;E=ROOT/'docs/superpowers/evidence/current-patch-proof'
A='/Users/jneerdael/Library/Android/sdk/platform-tools/adb';D='emulator-5630';R='/data/local/tmp/current-patch-proof'
def adb(*args):return subprocess.run([A,'-s',D,*args],capture_output=True,text=True,check=True,timeout=180).stdout
def sha(b):return hashlib.sha256(b).hexdigest()
reports=[]
for number,name in [(2,'Flexi - dimension window'),(3,'Stahlregen - funky Blur (lotus mix) the genius in me lies right at the heart of the flacc'),(5,'Cope - The Cloud'),(9,'suksma - chemosynthetic nosferatu - gdy patent pending free energy devices - rand tritex - inv play'),(12,'amandio c - the green machine 2 skin lard bone beacon nz+ consume, in fear, in excessiveness'),(13,'amandio c - the green machine 2 skin lard bone beacon nz+ consume, in fear, in excessiveness')]:
 number=str(number).zfill(4);fixture=ROOT/'core/src/main/assets/presets'/(name+'.milk');key=number+'-original';directory=W/'original-extra-captures'/key;directory.mkdir(parents=True,exist_ok=False)
 adb('push',str(fixture),R+'/witness.milk');width,height=(256,144) if number in ['0012','0013'] else (512,288);size=width*height*3
 report={'patch':number,'fixture':str(fixture.relative_to(ROOT)),'fixture_sha256':sha(fixture.read_bytes()),'dimensions':[width,height],'frames':120,'scope':'unchanged bundled original preset; instrumented Android TV GPU capture, not MilkDrop2 render','roles':{}}
 for role in ['upstream','without','patched']:
  binary=W/'ablations'/('without-'+number)/'ndk-build/patch-proof-worker' if role=='without' else W/('upstream/ndk-build/patch-proof-worker' if role=='upstream' else 'patched-capture-build/patch-proof-worker')
  adb('push',str(binary),R+'/fixture-worker');rows=[]
  for repeat in range(2):
   d=directory/(role+'-'+str(repeat));d.mkdir();job=json.loads((W/'patched/job.json').read_text());job['config']['width']=width;job['config']['height']=height;job['identity']={'role':role,'fixture':name,'repeat':repeat};job['manifest_path']=R+'/manifest.json';job['bands_path']=R+'/bands.jsonl'
   (d/'job.json').write_text(json.dumps(job,indent=2));adb('push',str(d/'job.json'),R+'/job.json')
   cmd=shlex.join(['env','PRESET_LAB_SEED=12345',R+'/fixture-worker','--job',R+'/job.json'])+' > '+R+'/frames.rgb 2> '+R+'/render.log'
   p=subprocess.run([A,'-s',D,'shell',cmd],capture_output=True,text=True,timeout=180);adb('pull',R+'/render.log',str(d/'render.log'))
   if p.returncode:rows.append({'status':'failed','exit':p.returncode,'log':(d/'render.log').read_text()});continue
   adb('pull',R+'/manifest.json',str(d/'manifest.json'));m=json.loads((d/'manifest.json').read_text());assert m['status']=='success' and m['gl_error_frames']==0
   adb('pull',R+'/frames.rgb',str(d/'frames.rgb'));b=(d/'frames.rgb').read_bytes();assert len(b)==120*size
   hashes=[sha(b[i*size:(i+1)*size]) for i in range(120)];rows.append({'status':'success','manifest':m,'stream_sha256':sha(b),'frame_hashes':hashes,'last_frame_max':max(b[-size:]),'last_frame_nonzero_pixels':sum(any(b[i+c] for c in range(3)) for i in range(len(b)-size,len(b),3))})
   for frame in [29,59,119]:Image.frombytes('RGB',(width,height),b[frame*size:(frame+1)*size]).save(d/('frame-'+str(frame)+'.png'))
   (d/'frames.rgb').unlink()
  report['roles'][role]={'binary_sha256':sha(binary.read_bytes()),'runs':rows,'repeat_equal':all(x['status']=='success' for x in rows) and rows[0].get('frame_hashes')==rows[1].get('frame_hashes')}
 if report['roles']['patched']['repeat_equal']:
  img=Image.new('RGB',(width*3,height+32),'#171717');draw=ImageDraw.Draw(img)
  for col,role in enumerate(['upstream','without','patched']):
   label=['Upstream + GLES3.0 admission','Current without '+number+'; cache off','Current with '+number+'; cache off'][col];draw.text((col*width+4,8),label,fill='white');value=report['roles'][role]
   if value['repeat_equal']:img.paste(Image.open(directory/(role+'-0')/'frame-119.png'),(col*width,32))
   else:draw.text((col*width+8,80),'Load rejected\nNo rendered framebuffer',fill='#ffb4ab')
  img.save(E/(key+'.png'));report['image']=key+'.png';report['frame']=119
 if report['roles']['patched']['repeat_equal'] and report['roles']['without']['repeat_equal']:
  report['different_frames']=sum(a!=b for a,b in zip(report['roles']['patched']['runs'][0]['frame_hashes'],report['roles']['without']['runs'][0]['frame_hashes']))
 reports.append(report);(E/'original-extra-results.json').write_text(json.dumps(reports,indent=2)+'\n');print(key,{r:v['repeat_equal'] for r,v in report['roles'].items()},report.get('different_frames'),flush=True)
