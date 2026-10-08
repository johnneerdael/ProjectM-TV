from pathlib import Path
import sys,json,shutil
import cv2,numpy as np
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
prefix,output,expected=sys.argv[1:];expected=int(expected);out=Path(output);out.mkdir(parents=True,exist_ok=True)
paths=sorted(Path('build/audit/captures').glob(prefix+'*'));assert len(paths)==expected,(len(paths),expected)
rows=[];groups={}
for p in paths:
 m=json.loads((p/'manifest.json').read_text());runner.verify(p,m['job'],m['presetAssetSha256']);assert (m['job']['width'],m['job']['height'])==(3840,2160)
 role='before' if '-before-' in p.name else 'after';repeat=int(p.name[-1]);q=out/'native-captures'/p.name;q.mkdir(parents=True,exist_ok=True)
 for name in ['manifest.json','frame-239.png']:shutil.copyfile(p/name,q/name)
 row={'directory':p.name,'preset':m['job']['preset'],'role':role,'repeat':repeat,'rgb_hashes':[c['rgbSha256'] for c in m['captures']]};rows.append(row);groups.setdefault((row['preset'],role),[]).append(row)
for key,rr in groups.items():assert len(rr)==2 and rr[0]['rgb_hashes']==rr[1]['rgb_hashes'],key
comparisons=[]
for name in sorted({r['preset'] for r in rows}):
 a=next(r for r in rows if r['preset']==name and r['role']=='before' and r['repeat']==0);b=next(r for r in rows if r['preset']==name and r['role']=='after' and r['repeat']==0);metrics=[]
 for frame in [120,150,180,210,239,300,390,479]:
  ai=cv2.imread(str(Path('build/audit/captures')/a['directory']/('frame-'+str(frame)+'.png')));bi=cv2.imread(str(Path('build/audit/captures')/b['directory']/('frame-'+str(frame)+'.png')));assert ai is not None and bi is not None
  delta=np.abs(ai.astype(np.int16)-bi.astype(np.int16));metrics.append({'frame':frame,'rgb_mae':float(delta.mean()),'changed_pixels':int(np.any(delta,axis=2).sum())})
 comparisons.append({'preset':name,'frames':metrics})
result={'scope':'Native4K finite/original fixtures as named; source-instrumented workers, not published shipping or Windows bytes','runs':expected,'exact_repeat_groups':len(groups),'selected_pngs_verified':8*expected,'rows':rows,'comparisons':comparisons};(out/'native-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
