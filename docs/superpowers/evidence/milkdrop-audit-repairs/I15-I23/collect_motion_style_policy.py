from pathlib import Path
import json,shutil,sys
import cv2,numpy as np
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
out=Path('docs/superpowers/evidence/milkdrop-audit-repairs/I15-I23'); rows=[];groups={}
paths=sorted(Path('build/audit/captures').glob('motionstyle-*'));assert len(paths)==44,len(paths)
for p in paths:
 m=json.loads((p/'manifest.json').read_text());runner.verify(p,m['job'],m['presetAssetSha256']);assert m['job']['width']==3840 and m['job']['height']==2160 and m['bundledPresetCount']==9626
 q=out/'native-captures'/p.name;q.mkdir(parents=True,exist_ok=True)
 for name in ['manifest.json','frame-239.png']:shutil.copyfile(p/name,q/name)
 row={'directory':p.name,'preset':m['job']['preset'],'repeat':int(p.name[-1]),'rgb_hashes':[c['rgbSha256'] for c in m['captures']]};rows.append(row);groups.setdefault(row['preset'],[]).append(row)
assert len(groups)==22
for name,rr in groups.items():assert len(rr)==2 and rr[0]['rgb_hashes']==rr[1]['rgb_hashes'],name
comparisons=[]
comparisons.append({'status':'explicit endpoint/style surrogates need target/source-scope review; no pixel-equivalence assumption'})

identity=json.loads(Path('build/audit/motion-style-diagnostics/current/identity.json').read_text());(out/'native-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
result={'status':'capture stage passed; production source controls passed; policy/image comparison review pending','runs':44,'frames_per_run':480,'selected_captures_per_run':8,'exact_repeat_groups':22,'shipping_byte_identity':False,'rows':rows,'finite_fixture_comparisons':comparisons}
(out/'native-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('rows','finite_fixture_comparisons')},indent=2))
