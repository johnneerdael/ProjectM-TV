from pathlib import Path
import hashlib,json,shutil,sys
import cv2
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
out=Path('docs/superpowers/evidence/milkdrop-audit-repairs/I01'); caps=Path('build/audit/captures')
identity=json.loads(Path('build/audit/i01-policy-diagnostics/current/identity.json').read_text())
rows=[]
for prefix,dimensions in [('i01policy-',(3840,2160)),('i01policy-small-',(256,144))]:
 dirs=[p for p in caps.glob(prefix+'*') if prefix=='i01policy-small-' or not p.name.startswith('i01policy-small-')]
 assert len(dirs)==20,(prefix,len(dirs))
 for p in sorted(dirs):
  m=json.loads((p/'manifest.json').read_text());m=runner.verify(p,m['job'],m['presetAssetSha256'])
  assert (m['job']['width'],m['job']['height'])==dimensions
  assert m['pcmSha256']=='14a59e75249dee0dd15d74487688c248c6a4a4b24a843b6d6f612ccc5c408dbc'
  assert m['bundledPresetCount']==9614 and m['job']['seed']==12345
  assert 'fallback' not in m['nativeTrailsStatus'].lower()
  q=out/'captures'/p.name;q.mkdir(parents=True,exist_ok=True);shutil.copyfile(p/'manifest.json',q/'manifest.json');shutil.copyfile(p/'frame-239.png',q/'frame-239.png')
  rows.append({'directory':p.name,'preset':m['job']['preset'],'width':dimensions[0],'height':dimensions[1],'repeat':int(p.name[-1]),'captures':[{k:c[k] for k in ('frame','rgbSha256','pngSha256','captureReadFramebufferBinding')} for c in m['captures']]})
 groups={}
 for r in rows:
  if r['width']!=dimensions[0]:continue
  groups.setdefault(r['preset'],[]).append(r)
 assert len(groups)==10
 for name,rr in groups.items():assert len(rr)==2 and rr[0]['captures']==rr[1]['captures'],name
 hi=['audit i01-actual-tolerant.milk','audit i01-canonical-positive.milk','audit i01-duplicate-upper-first.milk']
 lo=['audit i01-strict-source-oracle.milk','audit i01-missing-default.milk','audit i01-duplicate-lower-first.milk']
 hashes=lambda n:[c['rgbSha256'] for c in groups[n][0]['captures']]
 assert all(hashes(n)==hashes(hi[0]) for n in hi)
 assert all(hashes(n)==hashes(lo[0]) for n in lo)
 assert hashes(hi[0])!=hashes(lo[0])
 for stem in ['Computronium','Toxic Lithography']:
  actual='PyroCybin - '+stem+' [stahlregens gelatine finish].milk'; oracle='audit '+actual[:-5]+' - strict-source-defaults.milk'
  assert hashes(actual)==hashes(oracle)
result={'status':'retained policy qualified; no engine change','source_commit':identity['source_commit'],'runs':len(rows),'frames_per_run':480,'selected_frames_per_run':8,'exact_repeat_groups':20,'stock_pairs_selected_RGB_identical_both_resolutions':2,'shipping_byte_identity':False,'rows':rows}
(out/'native-results.json').write_text(json.dumps(result,indent=2)+'\n')
(out/'native-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
for name in ['build_i01_policy_diagnostics.py','render_i01_policy_diagnostics.py','render_i01_policy_small.py']:
 shutil.copyfile(Path('build/audit')/name,out/name)
print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
