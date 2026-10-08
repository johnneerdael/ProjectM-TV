from pathlib import Path
import subprocess, json, hashlib, shlex
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
WORK=Path(__file__).resolve().parent
EVIDENCE=ROOT/'docs/superpowers/evidence/current-patch-proof'
ADB='/Users/jneerdael/Library/Android/sdk/platform-tools/adb'
DEVICE='emulator-5630'
REMOTE='/data/local/tmp/current-patch-proof'
CASES=[
 ('0001-equations','161.milk'),
 ('0002-translator','Flexi - dimension window.milk'),
 ('0004-sampler','widest swing.milk'),
 ('0006-zoom','Hexcollie - This is where we begin stripped.milk'),
 ('0007-wave','319.milk'),
 ('0008-display','idiot - Forty Six and 2 (pushit!).milk'),
 ('0009-texture','suksma - chemosynthetic nosferatu - gdy patent pending free energy devices - rand tritex - inv play.milk'),
 ('0011-rotation','EoS_Phat_PeterP_Sentinel_Aware_6 EoS edit slice into your beautiful love.milk'),
]
def sha(data): return hashlib.sha256(data).hexdigest()
def adb(*args):
 return subprocess.run([ADB,'-s',DEVICE,*args],capture_output=True,check=True,text=True,timeout=180).stdout
reports=[]
for key,name in CASES:
 directory=WORK/'captures-v2'/key;directory.mkdir(parents=True,exist_ok=True)
 preset=ROOT/'core/src/main/assets/presets'/name
 adb('push',str(preset),REMOTE+'/witness.milk')
 report={'case':key,'preset':name,'preset_sha256':sha(preset.read_bytes()),'scope':'full current series, binary cache disabled, vs upstream with GLES3.0 admission; not single-patch causality','roles':{}}
 for role in ['upstream','patched']:
  rows=[]
  for repeat in range(2):
   d=directory/(role+'-'+str(repeat));d.mkdir(exist_ok=False)
   job=json.loads((WORK/role/'job.json').read_text());job['identity']={'role':role,'case':key,'repeat':repeat}
   job['manifest_path']=REMOTE+'/manifest.json';job['bands_path']=REMOTE+'/bands.jsonl'
   (d/'job.json').write_text(json.dumps(job,indent=2));adb('push',str(d/'job.json'),REMOTE+'/job.json')
   cmd=shlex.join(['env','PRESET_LAB_SEED=12345',REMOTE+'/'+role,'--job',REMOTE+'/job.json'])+' > '+REMOTE+'/frames.rgb 2> '+REMOTE+'/render.log'
   proc=subprocess.run([ADB,'-s',DEVICE,'shell',cmd],capture_output=True,text=True,timeout=180)
   adb('pull',REMOTE+'/render.log',str(d/'render.log'))
   if proc.returncode:
    rows.append({'status':'failed','shell_exit':proc.returncode,'log':(d/'render.log').read_text()});continue
   adb('pull',REMOTE+'/manifest.json',str(d/'manifest.json'));manifest=json.loads((d/'manifest.json').read_text())
   adb('pull',REMOTE+'/frames.rgb',str(d/'frames.rgb'));data=(d/'frames.rgb').read_bytes();size=512*288*3
   assert len(data)==size*120,(key,role,len(data))
   hashes=[sha(data[i*size:(i+1)*size]) for i in range(120)]
   (d/'hashes.json').write_text(json.dumps(hashes));rows.append({'manifest':manifest,'stream_sha256':sha(data),'frame_hashes':hashes,'status':manifest['status']})
   for frame in [29,59,119]:
    Image.frombytes('RGB',(512,288),data[frame*size:(frame+1)*size]).save(d/('frame-'+str(frame)+'.png'))
   (d/'frames.rgb').unlink()
  report['roles'][role]={'runs':rows,'repeat_equal':len(rows)==2 and rows[0].get('frame_hashes')==rows[1].get('frame_hashes') and rows[0]['status']=='success' and rows[1]['status']=='success'}
 if all(report['roles'][r]['repeat_equal'] for r in ['upstream','patched']):
  img=Image.new('RGB',(1024,320),'#171717');draw=ImageDraw.Draw(img)
  for col,role in enumerate(['upstream','patched']):
   src=directory/(role+'-0')/'frame-119.png';img.paste(Image.open(src),(col*512,32));draw.text((col*512+8,8),'Upstream + GLES3.0 admission' if col==0 else 'TV 13 patches; binary cache disabled',fill='white')
  img.save(EVIDENCE/(key+'.png'))
  report['image']=key+'.png';report['frame']=119
  report['different_frames']=sum(a!=b for a,b in zip(report['roles']['upstream']['runs'][0]['frame_hashes'],report['roles']['patched']['runs'][0]['frame_hashes']))
 (directory/'report.json').write_text(json.dumps(report,indent=2))
 reports.append(report);(EVIDENCE/'capture-results.json').write_text(json.dumps(reports,indent=2)+'\n')
 print(key,{r:report['roles'][r]['repeat_equal'] for r in ['upstream','patched']},report.get('different_frames'),flush=True)
