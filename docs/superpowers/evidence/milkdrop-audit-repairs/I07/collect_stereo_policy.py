from pathlib import Path
import json,shutil,sys
import cv2,numpy as np
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
out=Path('docs/superpowers/evidence/milkdrop-audit-repairs/I07'); rows=[];groups={}
paths=sorted(Path('build/audit/captures').glob('stereopolicy-*'));assert len(paths)==6,len(paths)
for p in paths:
 m=json.loads((p/'manifest.json').read_text());runner.verify(p,m['job'],m['presetAssetSha256']);assert m['job']['width']==3840 and m['job']['height']==2160 and m['bundledPresetCount']==9608
 q=out/'native-captures'/p.name;q.mkdir(parents=True,exist_ok=True)
 for name in ['manifest.json','frame-239.png']:shutil.copyfile(p/name,q/name)
 row={'directory':p.name,'preset':m['job']['preset'],'repeat':int(p.name[-1]),'rgb_hashes':[c['rgbSha256'] for c in m['captures']]};rows.append(row);groups.setdefault(row['preset'],[]).append(row)
assert len(groups)==3
for name,rr in groups.items():assert len(rr)==2 and rr[0]['rgb_hashes']==rr[1]['rgb_hashes'],name
comparisons=[]
a='audit stereo i07-averaged-stage.milk';b='audit stereo i07-left-only-stage.milk'
assert groups[a][0]['rgb_hashes']!=groups[b][0]['rgb_hashes']
comparisons.append({'case':'executed finite stereo-analysis coefficients rendered as explicit border inputs; not stereo JNI execution','different_selected_RGB':True})

identity=json.loads(Path('build/audit/stereo-policy-diagnostics/current/identity.json').read_text());(out/'native-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
result={'status':'capture stage passed; mono preservation and explicit stereo stage-oracle surrogates; policy review finalizing','runs':6,'frames_per_run':480,'selected_captures_per_run':8,'exact_repeat_groups':3,'shipping_byte_identity':False,'rows':rows,'finite_fixture_comparisons':comparisons}
(out/'native-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('rows','finite_fixture_comparisons')},indent=2))
