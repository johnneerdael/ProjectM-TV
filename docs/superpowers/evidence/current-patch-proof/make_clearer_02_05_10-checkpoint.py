from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageStat
ROOT=Path(__file__).resolve().parents[2];W=ROOT/'build/patch-proof';E=ROOT/'docs/superpowers/evidence/current-patch-proof';font=ImageFont.load_default(size=16);receipts=[]
rows=json.loads((E/'clearer-02-05-results.json').read_text())
for c in rows:
 number=c['patch'];name=Path(c['fixture']).stem;key=number+'-'+hashlib.sha256(name.encode()).hexdigest()[:10];folder=W/'clearer-02-05-captures'/key;frame=59;crop=(208,104,304,184)
 if number=='0002':title='Authored composite restored (0002)';file='0002-clear-original.png'
 else:title='Valid blur range restored (0005)';file='0005-clear-original.png'
 for v in c['roles'].values():assert v['repeat_equal'] and v['runs'][0]['frame_hashes']==v['runs'][1]['frame_hashes'] and all(x['manifest']['gl_error_frames']==0 for x in v['runs'])
 a=Image.open(folder/'without-0'/f'frame-{frame}.png').convert('RGB');b=Image.open(folder/'patched-0'/f'frame-{frame}.png').convert('RGB');im=Image.new('RGB',(1024,672),'#171717');d=ImageDraw.Draw(im)
 for col,src in enumerate([a,b]):
  d.text((col*512+8,8),title+(': WITHOUT' if col==0 else ': WITH'),fill='white',font=font);im.paste(src.resize((512,288),Image.Resampling.NEAREST),(col*512,32));tile=src.crop(crop);zoom=min(480//tile.width,256//tile.height);tile=tile.resize((tile.width*zoom,tile.height*zoom),Image.Resampling.NEAREST);im.paste(tile,(col*512+(512-tile.width)//2,368));d.text((col*512+8,336),'Same raw crop '+str(crop)+'; nearest '+str(zoom)+'x',fill='white',font=font);assert hashlib.sha256(src.tobytes()).hexdigest()==c['roles']['without' if col==0 else 'patched']['runs'][0]['frame_hashes'][frame]
 d.text((8,648),'Frame59; unchanged original preset. Unbrightened images; source-bound exact two-repeat GPU capture.',fill='white',font=font);im.save(E/file);delta=ImageChops.difference(a,b).tobytes();receipts.append({'patch':number,'preset':name+'.milk','asset_sha256':c['fixture_sha256'],'frame':frame,'dimensions':list(a.size),'crop':list(crop),'zoom':zoom,'full_nearest_scale':1,'raw_rgb_sha256':[hashlib.sha256(a.tobytes()).hexdigest(),hashlib.sha256(b.tobytes()).hexdigest()],'mae_rgb8':sum(delta)/len(delta),'max_delta':max(delta),'image':file,'image_sha256':hashlib.sha256((E/file).read_bytes()).hexdigest(),'repeat_proof':'clearer-02-05-results.json'})
# Host-level lifetime test: use real bundled photographs/textures under duplicate names.
root=W/'recognizable-texture-capture';c=json.loads((root/'results.json').read_text());im=Image.new('RGB',(1536,672),'#171717');d=ImageDraw.Draw(im)
for v in c['roles'].values():assert v['repeat_equal'] and v['runs'][0]['frame_hashes']==v['runs'][1]['frame_hashes']
for row,frame in enumerate([40,59]):
 for col,role in enumerate(['upstream','without-0010','patched']):
  src=Image.open(root/role/'0'/f'{frame}.png').convert('RGB');assert hashlib.sha256(src.tobytes()).hexdigest()==c['roles'][role]['runs'][0]['frame_hashes'][frame];d.text((col*512+8,row*320+8),role+'; frame '+str(frame),fill='white',font=font);im.paste(src,(col*512,row*320+32))
d.text((8,648),'Pack A: bundled spotted texture. Pack B: bundled rose. Root switch20; fade21; reset40. No brightness adjustment.',fill='white',font=font);im.save(E/'0010-recognizable-pack-switch.png');shutil.copyfile(root/'results.json',E/'recognizable-pack-switch-results.json');shutil.copyfile(root/'verification.json',E/'recognizable-pack-switch-verification.json')
assets=W/'recognizable-texture-journey';target=E/'recognizable-pack-fixture';shutil.copytree(assets,target,dirs_exist_ok=True);receipts.append({'patch':'0010','scenario':'host root-switch/soft-cut/reset; named custom-shape lookup fixture, not an unchanged artist preset','frames':[40,59],'image':'0010-recognizable-pack-switch.png','image_sha256':hashlib.sha256((E/'0010-recognizable-pack-switch.png').read_bytes()).hexdigest(),'inputs':{str(p.relative_to(target)):hashlib.sha256(p.read_bytes()).hexdigest() for p in target.rglob('*') if p.is_file()},'repeat_proof':'recognizable-pack-switch-results.json'})
(E/'clearer-02-05-10-figures.json').write_text(json.dumps(receipts,indent=2)+'\n');print([(r['patch'],r.get('mae_rgb8'),r['image']) for r in receipts])
