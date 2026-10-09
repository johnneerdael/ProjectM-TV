from pathlib import Path
import json,hashlib
import numpy as np
root=Path(__file__).resolve().parent
schedule=json.loads((root/'schedule.json').read_text());summary={}
rng=np.random.default_rng(12345)
for case in sorted(set(j['case'] for j in schedule)):
 jobs=[j for j in schedule if j['case']==case];rows=[]
 for job in jobs:
  result=json.loads((root/'runs'/job['name']/'result.json').read_text())
  assert result['status']=='success' and result['gl_error_frames']==0 and result['gpu_timer_valid']
  assert result['width']==3840 and result['height']==2160
  frames=[s for s in result['samples'] if s['measured']];assert len(frames)==360
  expected=2 if case=='inactive-classic' or job['role']=='with-0019' else 3
  assert all(s['gamma_draws']==expected and s['gamma_invocations']==1 and s['gpu_ns']>0 for s in frames)
  rows.append({**job,**{m:float(np.mean([s[m] for s in frames])) for m in ['submit_ms','complete_ms']},'gpu_ms':float(np.mean([s['gpu_ns']/1e6 for s in frames]))})
 metrics={}
 for metric in ['submit_ms','complete_ms','gpu_ms']:
  blocks=[]
  for block in sorted(set(j['block'] for j in rows)):
   pair={role:float(np.mean([j[metric] for j in rows if j['block']==block and j['role']==role])) for role in ['without-0019','with-0019']}
   blocks.append({'block':block,'before':pair['without-0019'],'after':pair['with-0019'],'delta_ms':pair['with-0019']-pair['without-0019']})
  deltas=np.array([b['delta_ms'] for b in blocks]);resamples=rng.choice(deltas,size=(100000,len(deltas)),replace=True).mean(axis=1)
  before=float(np.mean([b['before'] for b in blocks]));after=float(np.mean([b['after'] for b in blocks]))
  metrics[metric]={'before_ms':before,'after_ms':after,'delta_ms':after-before,'change_percent':100*(after-before)/before,'paired_block_bootstrap95_ms':np.percentile(resamples,[2.5,97.5]).tolist(),'all_blocks_faster':bool(np.all(deltas<0)),'blocks':blocks}
 summary[case]={'jobs':len(jobs),'measured_frames':len(jobs)*360,'gamma_draws_before':2 if case=='inactive-classic' else 3,'gamma_draws_after':2,'metrics':metrics}
(root/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
for case,data in summary.items():
 print(case)
 for metric,value in data['metrics'].items():print(metric,{k:v for k,v in value.items() if k!='blocks'})
