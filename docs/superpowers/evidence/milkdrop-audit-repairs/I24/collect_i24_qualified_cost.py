from pathlib import Path
import json,statistics,sys,shutil
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/audit/captures');rows=[]
for issue in ['I24-city-c','I24-city-alt']:
 for cycle in ([1,2,3] if issue=='I24-city-c' else [0,1,2]):
  prefix='warp-clean-i24-retry2-' if issue=='I24-city-c' and cycle in [1,2] else 'warp-clean-i24-retry3-'
  for step,role in enumerate(['before','after','after','before']):
   p=root/(prefix+issue+'-'+str(cycle)+'-'+str(step)+'-'+role);m=json.loads((p/'manifest.json').read_text());runner.verify(p,m['job'],m['presetAssetSha256'])
   rows.append({'issue':issue,'cycle':cycle,'step':step,'role':role,'directory':str(p),'mean_ms':m['serializedFrameMeanMs'],'rgb_hashes':[c['rgbSha256'] for c in m['captures']]})
assert len(rows)==24
results=[]
for issue in ['I24-city-c','I24-city-alt']:
 rr=[r for r in rows if r['issue']==issue];means={role:statistics.mean(r['mean_ms'] for r in rr if r['role']==role) for role in ['before','after']};cycles=[]
 for c in sorted({r['cycle'] for r in rr}):
  mm={role:statistics.mean(r['mean_ms'] for r in rr if r['cycle']==c and r['role']==role) for role in ['before','after']};cycles.append({'cycle':c,**mm,'delta_percent':100*(mm['after']/mm['before']-1)})
 for role in ['before','after']:assert len({tuple(r['rgb_hashes']) for r in rr if r['role']==role})==1,(issue,role)
 results.append({'issue':issue,'means':means,'delta_ms':means['after']-means['before'],'delta_percent':100*(means['after']/means['before']-1),'cycles':cycles})
result={'runs':24,'selected_pngs_verified':192,'exact_role_repeat_groups':4,'qualification':'city-c retry2 cycles1/2 and retry3 cycle3; alt retry3 cycles0/1/2. First-run ENOSPC and retry2city-c0 overlap/alt ENOSPC excluded, preserved separately','results':results,'rows':rows};Path('build/audit/i24-qualified-cost-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
