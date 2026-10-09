from pathlib import Path
import json,shutil,sys
import cv2,numpy as np
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
out=Path('docs/superpowers/evidence/milkdrop-audit-repairs/I26-I27/stock-volume'); rows=[];groups={}
paths=sorted(Path('build/audit/captures').glob('shaderstock-*'));assert len(paths)==4,len(paths)
for p in paths:
 m=json.loads((p/'manifest.json').read_text());runner.verify(p,m['job'],m['presetAssetSha256']);assert m['job']['width']==3840 and m['job']['height']==2160 and m['bundledPresetCount']==9607
 q=out/'native-captures'/p.name;q.mkdir(parents=True,exist_ok=True)
 for name in ['manifest.json','frame-239.png']:shutil.copyfile(p/name,q/name)
 row={'directory':p.name,'preset':m['job']['preset'],'repeat':int(p.name[-1]),'rgb_hashes':[c['rgbSha256'] for c in m['captures']]};rows.append(row);groups.setdefault(row['preset'],[]).append(row)
assert len(groups)==2
for name,rr in groups.items():assert len(rr)==2 and rr[0]['rgb_hashes']==rr[1]['rgb_hashes'],name
comparisons=[]
a='Cope - The Neverending Explosion of Red Liquid Fire.milk';b='audit shader stock cope-original-comma-volume.milk'
aa=Path('build/audit/captures')/groups[a][0]['directory'];bb=Path('build/audit/captures')/groups[b][0]['directory'];values=[]
for frame in runner.CAPTURES:
 x=cv2.imread(str(aa/('frame-%03d.png'%frame)),cv2.IMREAD_COLOR);y=cv2.imread(str(bb/('frame-%03d.png'%frame)),cv2.IMREAD_COLOR);values.append({'frame':frame,'RGB_MAE':float(np.abs(x.astype(np.int16)-y.astype(np.int16)).mean())})
comparisons.append({'original':a,'original_shader_comma_scalar_surrogate':b,'selected_images':values})

identity=json.loads(Path('build/audit/shader-stock-diagnostics/current/identity.json').read_text());(out/'native-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
result={'status':'capture stage passed; scope: original versus full preset shader-comma-scalar surrogate; no Windows claim','runs':4,'frames_per_run':480,'selected_captures_per_run':8,'exact_repeat_groups':2,'shipping_byte_identity':False,'rows':rows,'finite_fixture_comparisons':comparisons}
(out/'native-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('rows','finite_fixture_comparisons')},indent=2))
