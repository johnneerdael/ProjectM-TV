from pathlib import Path
import sys,json,statistics
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
rows=[]
for p in sorted(Path('build/audit/captures').glob('warp-clean-I04-bits-v3-*')):
 m=json.loads((p/'manifest.json').read_text());runner.verify(p,m['job'],m['presetAssetSha256']);parts=p.name.rsplit('-',3);rows.append({'case':parts[0].removeprefix('warp-clean-'),'preset':m['job']['preset'],'cycle':int(parts[1]),'step':int(parts[2]),'role':parts[3],'directory':str(p),'mean_ms':m['serializedFrameMeanMs'],'rgb_hashes':[c['rgbSha256'] for c in m['captures']]})
assert len(rows)==48
results=[]
for case in sorted({r['case'] for r in rows}):
 rr=[r for r in rows if r['case']==case];assert len(rr)==12;means={role:statistics.mean(x['mean_ms'] for x in rr if x['role']==role) for role in ['before','after']};cycles=[]
 for c in range(3):
  cc=[r for r in rr if r['cycle']==c];assert len(cc)==4;mm={role:statistics.mean(x['mean_ms'] for x in cc if x['role']==role) for role in ['before','after']};cycles.append({'cycle':c,**mm,'delta_percent':100*(mm['after']/mm['before']-1)})
 assert len({tuple(r['rgb_hashes']) for r in rr})==1,(case,'constant-geometry RGB must match all repeats and both roles')
 results.append({'case':case,'preset':rr[0]['preset'],'means':means,'delta_ms':means['after']-means['before'],'delta_percent':100*(means['after']/means['before']-1),'cycles':cycles})
res={'runs':48,'selected_pngs_verified':384,'exact_constant_geometry_groups':4,'scope':'v3 common-domain unchanged-flags evaluator candidate; all four runtime-Q workloads; no I03 recovery','results':results,'rows':rows};Path('build/audit/i04-v3-qualified-cost-results.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({k:v for k,v in res.items() if k!='rows'},indent=2))
