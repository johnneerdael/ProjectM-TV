from pathlib import Path
import subprocess,json,hashlib,shlex,shutil,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];W=Path(__file__).resolve().parent
SOURCE=Path('/Users/jneerdael/Downloads/projectm-patch-0010-aurora-witness-2026-10-08')
sys.path.insert(0,str(ROOT/'tools/core-corpus'));from run_corpus import session_lock
A='/Users/jneerdael/Library/Android/sdk/platform-tools/adb';D='emulator-5630'
work=W/'aurora-owner-experiment-v1';work.mkdir(exist_ok=False)
shutil.copytree(SOURCE,work/'inputs');source=work/'inputs';sha=lambda b:hashlib.sha256(b).hexdigest()
R='/data/local/tmp/aurora-owner-proof-'+sha(str(work.resolve()).encode())[:12]
workers=json.loads((W/'texture-audit-workers.json').read_text())
def adb(*args,check=True):return subprocess.run([A,'-s',D,*args],capture_output=True,text=True,check=check,timeout=180)
report={'scope':'user/predictor supplied SOL/LUNA unchanged source bytes; fixed GPU TV host ownership experiment','prediction':json.loads((source/'predicted-host-sequence.json').read_text()),'inputs':{str(p.relative_to(source)):sha(p.read_bytes()) for p in source.rglob('*') if p.is_file()},'pcm_sha256':sha((W/'audio.f32').read_bytes()),'roles':{}}
with session_lock(D,5037):
 assert adb('shell','am','get-current-user').stdout.strip()=='0'
 features=adb('shell','pm','list','features').stdout;assert 'feature:android.hardware.type.television\n' in features
 adb('shell','mkdir','-p',R);adb('push',str(source/'pack-a'),R+'/pack-a');adb('push',str(source/'pack-b'),R+'/pack-b');adb('push',str(W/'audio.f32'),R+'/audio.f32')
 for role,identity in workers.items():
  assert sha(Path(identity['binary']).read_bytes())==identity['binary_sha256'];adb('push',identity['binary'],R+'/worker');adb('shell','chmod','755',R+'/worker');rows=[]
  for repeat in range(2):
   d=work/role/str(repeat);d.mkdir(parents=True)
   job=json.loads((W/'patched/job.json').read_text());job['config'].update({'width':512,'height':288,'soft_cut_seconds':2});job.update({'preset_path':R+'/pack-a/presets/Aurora Ownership - SOL.milk','texture_root':R+'/pack-a/textures','pcm_path':R+'/audio.f32','manifest_path':R+'/manifest.json','bands_path':R+'/bands.jsonl','identity':{'role':role,'repeat':repeat,'experiment':'AuroraSOL-LUNA'}})
   job['events']=[{'frame':20,'texture_root':R+'/pack-b/textures'},{'frame':21,'load_preset':R+'/pack-b/presets/Aurora Ownership - LUNA.milk','smooth':True},{'frame':40,'reset_textures':True}]
   (d/'job.json').write_text(json.dumps(job,indent=2));adb('push',str(d/'job.json'),R+'/job.json');adb('shell','rm','-f',R+'/manifest.json')
   cmd=shlex.join(['env','PRESET_LAB_SEED=12345',R+'/worker','--job',R+'/job.json'])+' > '+R+'/frames.rgb 2> '+R+'/render.log';p=adb('shell',cmd,check=False);adb('pull',R+'/render.log',str(d/'render.log'))
   if p.returncode:
    rows.append({'status':'failed','exit':p.returncode,'log':(d/'render.log').read_text()});continue
   adb('pull',R+'/manifest.json',str(d/'manifest.json'));m=json.loads((d/'manifest.json').read_text());assert m['gl_error_frames']==0 and m['frames']==120
   adb('pull',R+'/frames.rgb',str(d/'frames.rgb'));b=(d/'frames.rgb').read_bytes();size=512*288*3;assert len(b)==120*size;hashes=[sha(b[i*size:(i+1)*size]) for i in range(120)]
   for frame in [0,19,20,21,29,40,59,81,119]:Image.frombytes('RGB',(512,288),b[frame*size:(frame+1)*size]).save(d/f'{frame}.png')
   rows.append({'status':'success','manifest':m,'stream_sha256':sha(b),'frame_hashes':hashes});(d/'frames.rgb').unlink()
  report['roles'][role]={'worker':identity,'runs':rows,'repeat_equal':all(x['status']=='success' for x in rows) and rows[0]['frame_hashes']==rows[1]['frame_hashes']};(work/'results.json').write_text(json.dumps(report,indent=2));print(role,report['roles'][role]['repeat_equal'],flush=True)
 adb('shell','rm','-rf',R)
if all(v['repeat_equal'] for v in report['roles'].values()):
 a=report['roles']['without-0010']['runs'][0]['frame_hashes'];b=report['roles']['patched']['runs'][0]['frame_hashes'];report['first_difference_without10_vs_current']=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),None);report['different_frames_without10_vs_current']=sum(x!=y for x,y in zip(a,b))
 image=Image.new('RGB',(1536,4*320),'#171717');draw=ImageDraw.Draw(image);font=ImageFont.load_default(size=16)
 for row,frame in enumerate([19,20,40,59]):
  for col,role in enumerate(['upstream','without-0010','patched']):
   draw.text((col*512+8,row*320+8),role+': frame '+str(frame),fill='white',font=font);image.paste(Image.open(work/role/'0'/f'{frame}.png'),(col*512,row*320+32))
 image.save(work/'ownership-comparison.png')
(work/'results.json').write_text(json.dumps(report,indent=2)+'\n');print('first divergence',report.get('first_difference_without10_vs_current'),'differentframes',report.get('different_frames_without10_vs_current'),flush=True)
