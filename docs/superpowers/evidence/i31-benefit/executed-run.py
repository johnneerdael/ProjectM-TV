"""Original execution recipe with input/request checks added after review.

Existing timed-runs.json.gz is never rewritten or rerun by this script. Future private
runs retain complete request hashes and observed before/after input inventories.
"""
import json,os,subprocess,hashlib,sys,time
from pathlib import Path
import numpy as np
from benchmark import config as expected_config, digest, schedule_recipe
repo=Path(__file__).resolve().parents[2];root=Path(__file__).resolve().parent
pcm=repo/'docs/superpowers/evidence/patch-visual-catalog/audio/frozen-480-frames.f32'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
identities={r:json.loads((root/r/'identity.json').read_text()) for r in ['with-0019','without-0019']}
compact={r:{'role':r,'worker_sha256':identities[r]['worker_sha256'],'source_tree_sha256':hashlib.sha256(json.dumps(identities[r]['source'],sort_keys=True,separators=(',',':')).encode()).hexdigest()} for r in identities}
profiles = {name: expected_config(name) for name in ('classic', 'standard')}
def input_hashes(preset):
 textures=repo/'core/src/main/assets/textures'
 return {'preset_sha256':sha(preset),'pcm_sha256':sha(pcm),
         'textures_sha256':digest({p.relative_to(textures).as_posix():sha(p)
                                  for p in sorted(textures.rglob('*')) if p.is_file()})}
def run(name,role,profile,preset):
 directory=root/'runs'/name;directory.mkdir(parents=True,exist_ok=False)
 job={'schema_version':1,'config':profiles[profile],'pcm_path':str(pcm),'preset_path':str(preset),'texture_root':str(repo/'core/src/main/assets/textures'),'manifest_path':str(directory/'result.json'),'identity':compact[role]}
 before_inputs=input_hashes(preset)
 (directory/'job.json').write_text(json.dumps(job,indent=2)+'\n')
 identity=identities[role];assert sha(Path(identity['worker']))==identity['worker_sha256']
 with (directory/'stderr.txt').open('w') as log:
  subprocess.run([identity['worker'],'--job',str(directory/'job.json')],env=dict(os.environ,PRESET_LAB_SEED='12345'),check=True,stdout=log,stderr=subprocess.STDOUT,timeout=120)
 after_inputs=input_hashes(preset)
 assert before_inputs == after_inputs, 'runtime inputs changed during run'
 (directory/'request-receipt.json').write_text(json.dumps({'request':job,'request_sha256':digest(job),'inputs_before':before_inputs,'inputs_after':after_inputs},indent=2)+'\n')
 result=json.loads((directory/'result.json').read_text());assert result['config']==profiles[profile] and result['identity']==compact[role]
 assert result['status']=='success' and result['gl_error_frames']==0 and result['gl_renderer']=='Apple M4 Pro'
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
 schedule=schedule_recipe()
 (root/'schedule.json').write_text(json.dumps(schedule,indent=2)+'\n')
 results=[]
 for job in schedule:
  if (root/'runs'/job['name']/'result.json').exists():raise SystemExit('refuse reused benchmark runs')
  stats=run(job['name'],job['role'],job['profile'],root/job['preset']);results.append({**job,**stats})
  (root/'job-summary.json').write_text(json.dumps(results,indent=2)+'\n')
