from pathlib import Path
import subprocess,json,hashlib,shlex,sys
from PIL import Image,ImageChops,ImageDraw
ROOT=Path(__file__).resolve().parents[2];W=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools/core-corpus'))
from run_corpus import session_lock
A='/Users/jneerdael/Library/Android/sdk/platform-tools/adb';D='emulator-5630';R='/data/local/tmp/visible-preset-threshold-screen-20261007'
inv=json.loads((W/'visible-candidate-inventory.json').read_text())
selection=[{'patch':'0013','asset_sha256':hashlib.sha256((ROOT/'core/src/main/assets/presets'/x['filename']).read_bytes()).hexdigest(),**x} for x in json.loads((W/'additional-visible-source-candidates.json').read_text())['threshold_composite'][:24]]
work=W/'visible-screen-threshold-v1';work.mkdir(exist_ok=False);(work/'selection.json').write_text(json.dumps(selection,indent=2))
sha=lambda b:hashlib.sha256(b).hexdigest()
def adb(*args,check=True):return subprocess.run([A,'-s',D,*args],capture_output=True,text=True,check=check,timeout=180)
reports=[]
with session_lock(D,5037):
 assert adb('shell','am','get-current-user').stdout.strip()=='0'
 features=adb('shell','pm','list','features').stdout
 assert 'feature:android.software.leanback\n' in features and 'feature:android.hardware.type.television\n' in features
 adb('shell','mkdir','-p',R);adb('push',str(ROOT/'core/src/main/assets/textures'),R+'/textures')
 (work/'audio.f32').write_bytes((W/'audio.f32').read_bytes()[:60*1470*4]);adb('push',str(work/'audio.f32'),R+'/audio.f32')
 adb('push',str(W/'patched-capture-build/patch-proof-worker'),R+'/patched')
 for key in ['0009','0012','0013']:adb('push',str(W/'ablations'/('without-'+key)/'ndk-build/patch-proof-worker'),R+'/without-'+key)
 for index,c in enumerate(selection):
  name=c['filename'];key=c['patch'];directory=work/f'{index:03d}-{key}';directory.mkdir();preset=ROOT/'core/src/main/assets/presets'/name;assert sha(preset.read_bytes())==c['asset_sha256'];adb('push',str(preset),R+'/witness.milk')
  record={'patch':key,'preset':name,'asset_sha256':c['asset_sha256'],'source_rank':c['score'],'scope':'exploratory source-matched original-preset selection; one run per role, repeat confirmation required','roles':{},'directory':str(directory)}
  for role in ['without','patched']:
   d=directory/role;d.mkdir();job=json.loads((W/'patched/job.json').read_text());job['config'].update({'width':256,'height':144,'measurement_seconds':2});job.update({'pcm_path':R+'/audio.f32','preset_path':R+'/witness.milk','texture_root':R+'/textures','manifest_path':R+'/manifest.json','bands_path':R+'/bands.jsonl','identity':{'role':role,'patch':key,'preset':name}})
   (d/'job.json').write_text(json.dumps(job,indent=2));adb('push',str(d/'job.json'),R+'/job.json')
   binary=R+'/patched' if role=='patched' else R+'/without-'+key
   command=shlex.join(['env','PRESET_LAB_SEED=12345',binary,'--job',R+'/job.json'])+' > '+R+'/frames.rgb 2> '+R+'/render.log'
   try:p=adb('shell',command,check=False)
   except subprocess.TimeoutExpired:
    record['roles'][role]={'status':'timeout'};break
   adb('pull',R+'/render.log',str(d/'render.log'))
   if p.returncode:
    record['roles'][role]={'status':'failed','exit':p.returncode,'log':(d/'render.log').read_text()};continue
   adb('pull',R+'/manifest.json',str(d/'manifest.json'));m=json.loads((d/'manifest.json').read_text());assert m['frames']==60 and m['gl_error_frames']==0 and m['status']=='success';assert 'Apple M4 Pro' in m['gl_renderer']
   adb('pull',R+'/frames.rgb',str(d/'frames.rgb'));b=(d/'frames.rgb').read_bytes();size=256*144*3;assert len(b)==60*size
   hashes=[sha(b[i*size:(i+1)*size]) for i in range(60)]
   for frame in [14,29,59]:Image.frombytes('RGB',(256,144),b[frame*size:(frame+1)*size]).save(d/f'{frame}.png')
   record['roles'][role]={'status':'success','manifest':m,'frame_hashes':hashes,'stream_sha256':sha(b)};(d/'frames.rgb').unlink()
  if all(record['roles'].get(r,{}).get('status')=='success' for r in ['without','patched']):
   measurements=[]
   for frame in [14,29,59]:
    a=Image.open(directory/'without'/f'{frame}.png').convert('RGB');b=Image.open(directory/'patched'/f'{frame}.png').convert('RGB');delta=ImageChops.difference(a,b);raw=delta.tobytes();pixels=[max(raw[i:i+3]) for i in range(0,len(raw),3)];lit=sum(max(b.tobytes()[i:i+3])>16 for i in range(0,len(raw),3));measurements.append({'frame':frame,'mae_rgb8':sum(raw)/len(raw),'changed_pixels':sum(x>0 for x in pixels),'pixels_delta_gt16':sum(x>16 for x in pixels),'max_delta':max(raw),'patched_lit_pixels_gt16':lit})
   record['metrics']=measurements;record['different_frames']=sum(a!=b for a,b in zip(record['roles']['without']['frame_hashes'],record['roles']['patched']['frame_hashes']))
   record['visibility_score']=max(m['pixels_delta_gt16']/36864 for m in measurements)
   img=Image.new('RGB',(512,176),'#171717');draw=ImageDraw.Draw(img);draw.text((4,8),'Without '+key,fill='white');draw.text((260,8),'With '+key,fill='white');img.paste(Image.open(directory/'without/59.png'),(0,32));img.paste(Image.open(directory/'patched/59.png'),(256,32));img.save(directory/'comparison.png')
  reports.append(record);(work/'results.json').write_text(json.dumps(reports,indent=2));print(index,key,name,'visibility',round(record.get('visibility_score',0),3),'diffFrames',record.get('different_frames'),flush=True)
