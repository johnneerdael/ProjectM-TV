from pathlib import Path
import json,sys,shutil,statistics
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/audit');out=Path('docs/superpowers/evidence/milkdrop-audit-repairs/I03-I04/runtime-cost-proof');out.mkdir(exist_ok=True);rows=[]
for issue in ['runtime-div-mod','runtime-pow','runtime-ordinary']:
 paths=sorted((root/'captures').glob('warp-clean-'+issue+'-*'));assert len(paths)==12,(issue,len(paths))
 hashes={}
 for p in paths:
  m=json.loads((p/'manifest.json').read_text());runner.verify(p,m['job'],m['presetAssetSha256']);role=p.name.rsplit('-',1)[-1];q=out/issue/p.name;q.mkdir(parents=True,exist_ok=True);shutil.copyfile(p/'manifest.json',q/'manifest.json')
  h=[c['rgbSha256'] for c in m['captures']];hashes.setdefault(role,[]).append(h);rows.append({'issue':issue,'directory':p.name,'role':role,'mean_ms':m['serializedFrameMeanMs'],'rgb_hashes':h})
 for role,hh in hashes.items():assert len(hh)==6 and all(x==hh[0] for x in hh)
 assert hashes['before'][0]==hashes['after'][0],issue
 b=statistics.mean(r['mean_ms'] for r in rows if r['issue']==issue and r['role']=='before');a=statistics.mean(r['mean_ms'] for r in rows if r['issue']==issue and r['role']=='after');print(issue,b,a,(a/b-1)*100,flush=True)
(out/'verified-results.json').write_text(json.dumps({'status':'36runtime jobs verified; allrole/combined selectedRGB identical','rows':rows,'limits':'emulator/sourceinstrumentedcore/selectedframes only'},indent=2)+'\n')
for role in ['before','after']:shutil.copyfile(root/'arithmetic-runtime-q-diagnostics'/role/'identity.json',out/(role+'-identity.json'))
