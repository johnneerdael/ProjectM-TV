import json,os,subprocess,hashlib,sys,time
from pathlib import Path
import numpy as np
repo=Path(__file__).resolve().parents[2];root=Path(__file__).resolve().parent
pcm=repo/'docs/superpowers/evidence/patch-visual-catalog/audio/frozen-480-frames.f32'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
identities={r:json.loads((root/r/'identity.json').read_text()) for r in ['with-0019','without-0019']}
compact={r:{'role':r,'worker_sha256':identities[r]['worker_sha256'],'source_tree_sha256':hashlib.sha256(json.dumps(identities[r]['source'],sort_keys=True,separators=(',',':')).encode()).hexdigest()} for r in identities}
profiles={'classic':{'line_reference_height':0,'line_antialiasing':False,'feedback_detail':-1.0},'standard':{'line_reference_height':720,'line_antialiasing':True,'feedback_detail':0.0}}
def run(name,role,profile,preset):
 directory=root/'runs'/name;directory.mkdir(parents=True,exist_ok=False)
 job={'schema_version':1,'config':{'width':3840,'height':2160,'fps':30,'warmup_seconds':4,'measurement_seconds':12,'seed':12345,**profiles[profile]},'pcm_path':str(pcm),'preset_path':str(preset),'texture_root':str(repo/'core/src/main/assets/textures'),'manifest_path':str(directory/'result.json'),'identity':compact[role]}
 (directory/'job.json').write_text(json.dumps(job,indent=2)+'\n')
 identity=identities[role];assert sha(Path(identity['worker']))==identity['worker_sha256']
 with (directory/'stderr.txt').open('w') as log:
  subprocess.run([identity['worker'],'--job',str(directory/'job.json')],env=dict(os.environ,PRESET_LAB_SEED='12345'),check=True,stdout=log,stderr=subprocess.STDOUT,timeout=120)
 result=json.loads((directory/'result.json').read_text());assert result['status']=='success' and result['gl_error_frames']==0 and result['gl_renderer']=='Apple M4 Pro'
 measured=[s for s in result['samples'] if s['measured']]
 assert len(measured)==360 and len(result['samples'])==480
 stats={k:float(np.mean([s[k] for s in measured])) for k in ['submit_ms','complete_ms']}
 stats['gamma_draws']=sorted(set(s['gamma_draws'] for s in measured));stats['gamma_invocations']=sorted(set(s['gamma_invocations'] for s in measured));stats['gamma']=sorted(set(s['gamma'] for s in measured));stats['gpu_timer_valid']=result['gpu_timer_valid']
 print(name,stats,flush=True)
 return stats
if sys.argv[1]=='smoke':
 for profile in profiles:
  for role in identities:run('smoke-'+profile+'-'+role,role,profile,root/'original.milk')
else:
 schedule=[]
 for case,profile,blocks,preset in [('original-classic','classic',8,'original.milk'),('original-standard','standard',8,'original.milk'),('inactive-classic','classic',4,'inactive-gamma2.milk')]:
  for b in range(blocks):
   roles=['without-0019','with-0019','with-0019','without-0019'] if b%2==0 else ['with-0019','without-0019','without-0019','with-0019']
   for position,role in enumerate(roles):schedule.append({'case':case,'profile':profile,'block':b,'position':position,'role':role,'preset':preset,'name':f'{case}-b{b:02d}-p{position}-{role}'})
 (root/'schedule.json').write_text(json.dumps(schedule,indent=2)+'\n')
 results=[]
 for job in schedule:
  if (root/'runs'/job['name']/'result.json').exists():raise SystemExit('refuse reused benchmark runs')
  stats=run(job['name'],job['role'],job['profile'],root/job['preset']);results.append({**job,**stats})
  (root/'job-summary.json').write_text(json.dumps(results,indent=2)+'\n')
