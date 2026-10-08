from pathlib import Path
import json,hashlib,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]; W=Path(__file__).resolve().parent; E=ROOT/'docs/superpowers/evidence/current-patch-proof'
sha=lambda b:hashlib.sha256(b).hexdigest()
verified=[];successful=0;failures=0

def rows_valid(rows):
 global successful,failures
 ok=[r for r in rows if r['status']=='success']
 if ok:
  assert len(ok)==2 and ok[0]['frame_hashes']==ok[1]['frame_hashes']
  for r in ok:
   m=r['manifest'];assert m['status']=='success' and m['gl_error_frames']==0 and m['frames']==120
   assert len(r['frame_hashes'])==120;successful+=1
 failures+=len(rows)-len(ok)

def verify_image(report,folder,roles,width,height,frame=119):
 im=Image.open(E/report['image']);assert im.size==(width*len(roles),height+32)
 for col,(role,rows,path) in enumerate(roles):
  rows_valid(rows)
  if rows[0]['status']!='success':continue
  source=Image.open(folder/path/('frame-'+str(frame)+'.png'));assert source.size==(width,height)
  assert sha(source.tobytes())==rows[0]['frame_hashes'][frame]
  assert im.crop((col*width,32,(col+1)*width,height+32)).tobytes()==source.tobytes()
 verified.append({'image':report['image'],'sha256':sha((E/report['image']).read_bytes())})

for c in json.loads((E/'capture-results.json').read_text()):
 preset=ROOT/'core/src/main/assets/presets'/c['preset'];assert sha(preset.read_bytes())==c['preset_sha256']
 verify_image(c,W/'captures-v2'/c['case'],[(r,c['roles'][r]['runs'],r+'-0') for r in ['upstream','patched']],512,288)
for c in json.loads((E/'ablation-results.json').read_text()):
 target=next(r for r in json.loads((E/'capture-results.json').read_text()) if r['preset']==c['preset'])
 im=Image.open(E/c['image']);rows_valid(c['runs']);source=Image.open(W/'ablation-captures'/target['case']/'0/frame-119.png');assert sha(source.tobytes())==c['runs'][0]['frame_hashes'][119];assert im.crop((0,32,512,320)).tobytes()==source.tobytes()
 source=Image.open(W/'captures-v2'/target['case']/'patched-0/frame-119.png');assert im.crop((512,32,1024,320)).tobytes()==source.tobytes()
 assert c['different_frames']==sum(a!=b for a,b in zip(c['runs'][0]['frame_hashes'],target['roles']['patched']['runs'][0]['frame_hashes']))
 verified.append({'image':c['image'],'sha256':sha((E/c['image']).read_bytes())})
for filename,folder in [('fixture-results.json','fixture-captures'),('fixture-results-v2.json','fixture-captures-v2'),('original-extra-results.json','original-extra-captures')]:
 for c in json.loads((E/filename).read_text()):
  path=ROOT/c['fixture'] if filename.startswith('original') else E/c['fixture'];assert sha(path.read_bytes())==c['fixture_sha256']
  key=c['patch']+'-original' if filename.startswith('original') else c['patch']+'-'+path.stem
  width,height=c['dimensions'];verify_image(c,W/folder/key,[(r,c['roles'][r]['runs'],r+'-0') for r in ['upstream','without','patched']],width,height)
  if 'different_frames' in c:assert c['different_frames']==sum(a!=b for a,b in zip(c['roles']['without']['runs'][0]['frame_hashes'],c['roles']['patched']['runs'][0]['frame_hashes']))
for filename,folder,fixture in [('texture-roots-results.json','texture-root-captures','texture-roots'),('texture-roots-shapes-results.json','texture-root-shape-captures','texture-roots-shapes')]:
 c=json.loads((E/filename).read_text());im=Image.open(E/c['image']);assert im.size==(1536,640)
 for name,identity in c['fixtures'].items():assert sha((E/'fixtures'/fixture/name).read_bytes())==identity
 for col,role in enumerate(['upstream','without-0010','patched']):
  rows=c['roles'][role]['runs'];rows_valid(rows)
  for row,frame in enumerate([40,59]):
   source=Image.open(W/folder/(role+'-0')/('frame-'+str(frame)+'.png'));assert sha(source.tobytes())==rows[0]['frame_hashes'][frame];assert im.crop((col*512,row*320+32,(col+1)*512,row*320+320)).tobytes()==source.tobytes()
 assert c['different_frames_without_patch']==sum(a!=b for a,b in zip(c['roles']['without-0010']['runs'][0]['frame_hashes'],c['roles']['patched']['runs'][0]['frame_hashes']))
 verified.append({'image':c['image'],'sha256':sha((E/c['image']).read_bytes())})
im=Image.open(E/'0013-composite-impulse-zoom.png')
for col,role in enumerate(['upstream','without','patched']):
 source=Image.open(W/'fixture-captures-v2/0013-composite-impulse'/(role+'-0/frame-119.png'))
 assert im.crop((col*256,32,(col+1)*256,176)).tobytes()==source.tobytes()
 assert im.crop((col*256+64,208,col*256+192,336)).tobytes()==source.crop((124,68,132,76)).resize((128,128),Image.Resampling.NEAREST).tobytes()
verified.append({'image':'0013-composite-impulse-zoom.png','sha256':sha((E/'0013-composite-impulse-zoom.png').read_bytes())})
series=json.loads((E/'series.json').read_text());assert len(series['patches'])==13
for p in series['patches']:assert sha((ROOT/'tools/projectm-patches'/p['filename']).read_bytes())==p['sha256']
protocol=json.loads((E/'protocol.json').read_text());assert sha((W/'audio.f32').read_bytes())==protocol['pcm']['sha256']
for t in protocol['textures']:assert sha((ROOT/'core/src/main/assets/textures'/t['filename']).read_bytes())==t['sha256']
for role,source in [('upstream','upstream'),('patched','patched-capture-engine')]:
 base=Path(protocol['roles'][role]['prepared_engine']['engine']) if role=='upstream' else W/source
 hashes=json.loads((E/(role+'-source-hashes.json')).read_text());assert {str(p.relative_to(base)):sha(p.read_bytes()) for p in base.rglob('*') if p.is_file()}==hashes
for p in [ROOT/'docs/UPSTREAM_PATCH_VALUE.md',E/'README.md']:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not link.startswith(('http','mailto','#')):assert (p.parent/link.split('#')[0]).exists(),link
report={'status':'passed','scope':'image pixel payloads against private PNGs and every-frame hashes; repeat/GL/frame counts; preset, fixture, PCM, texture and compiled-source inventories; current doc links','images':verified,'successful_runs_checked':successful,'explicit_failed_runs_preserved':failures,'patches':13,'helper_sha256':sha(Path(__file__).read_bytes())}
(E/'checkpoint-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','successful_runs_checked','explicit_failed_runs_preserved','patches']}));print('images',len(verified))
