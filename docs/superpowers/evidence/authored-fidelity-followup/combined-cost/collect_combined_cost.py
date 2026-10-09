"""Run after isolated timing ends; decode/reverify every capture before summarizing."""
from pathlib import Path
import collections,hashlib,json,math,statistics,sys
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import run_validation as runner
root=Path('build/authored-followup')
rows=[]
for line in (root/'combined-cost.txt').read_text().splitlines():
 try:
  row=json.loads(line)
  if 'mean_ms' in row:rows.append(row)
 except ValueError:pass
assert len(rows)==84 and all(r['status']=='ok' for r in rows),'Incomplete frozen ABBA run'
identities={role:json.loads((root/'diagnostics'/role/'identity.json').read_text()) for role in ['before','after']}
for identity in identities.values():
 for key in ['apk','aar']:
  assert hashlib.sha256(Path(identity[key]).read_bytes()).hexdigest()==identity[key+'_sha256']
focused=json.loads((root/'native-focused-results.json').read_text())
focused_hashes={}
for row in focused['rows']:
 for role in ['before','after']:
  m=json.loads(Path(row['manifests'][role][0]).read_text())
  focused_hashes[(row['preset'],role)]=[c['rgbSha256'] for c in m['captures']]
seen=set();driver=None;capture_count=0
for row in rows:
 key=(row['index'],row['cycle'],row['step']);assert key not in seen;seen.add(key)
 assert row['role']==['before','after','after','before'][row['step']]
 directory=Path(row['manifest']).parent
 request=json.loads((directory/'request.json').read_text());raw=json.loads((directory/'manifest.json').read_text())
 m=runner.verify(directory,request,raw['presetAssetSha256'])
 assert (request['width'],request['height'],request['referenceWidth'],request['referenceHeight'],request['seed'],request['nativeTrails'])==(3840,2160,1280,720,12345,0)
 assert request['preset']==row['name'] and request['expectedPresetCount']==9616
 assert m['pcmSha256']=='14a59e75249dee0dd15d74487688c248c6a4a4b24a843b6d6f612ccc5c408dbc'
 assert m['nativeTrailsStatus']=='Standard · 1280×720 canvas'
 assert [c['rgbSha256'] for c in m['captures']]==focused_hashes[(row['name'],row['role'])],'Cost output differs from the frozen correctness witness'
 observed={k:m[k] for k in ['glVendor','glRenderer','glVersion','glShadingLanguageVersion']}
 observed.update(sdk=m['device']['sdk'],fingerprint=m['device']['fingerprint'])
 if driver is None:driver=observed
 assert observed==driver
 assert row['apk_sha256']==identities[row['role']]['apk_sha256']
 for log_key,manifest_key in [('mean_ms','serializedFrameMeanMs'),('p90_ms','serializedFrameP90Ms')]:
  assert math.isfinite(row[log_key]) and row[log_key]==m[manifest_key] and row[log_key]>0
 row['manifest_sha256']=hashlib.sha256((directory/'manifest.json').read_bytes()).hexdigest()
 row['request_sha256']=hashlib.sha256((directory/'request.json').read_bytes()).hexdigest()
 capture_count+=len(m['captures'])
assert seen=={(i,c,s) for i in range(7) for c in range(3) for s in range(4)}
summary=[]
for index in range(7):
 group=[r for r in rows if r['index']==index]
 assert len({r['name'] for r in group})==1
 means={role:statistics.mean(r['mean_ms'] for r in group if r['role']==role) for role in ['before','after']}
 cycles=[]
 for c in range(3):
  values={role:statistics.mean(r['mean_ms'] for r in group if r['role']==role and r['cycle']==c) for role in ['before','after']}
  cycles.append({'cycle':c,'before_ms':values['before'],'after_ms':values['after'],'delta_ms':values['after']-values['before'],'delta_percent':100*(values['after']/values['before']-1)})
 summary.append({'preset':group[0]['name'],'runs_per_role':6,'before_mean_ms':means['before'],'after_mean_ms':means['after'],'delta_ms':means['after']-means['before'],'delta_percent':100*(means['after']/means['before']-1),'cycles':cycles,'mean_of_run_p90_ms':{role:statistics.mean(r['p90_ms'] for r in group if r['role']==role) for role in ['before','after']}})
result={'jobs':84,'selected_captures_verified':capture_count,'all_cost_outputs_match_focused_witness':True,'driver':driver,'source_baseline':'960eed2c6cf3badf0dccb97f02d64bdecc851ed5','source_candidate':'cd3f0e44aa09afa72b7b729a0d75574154973b0d','patch_counts':[28,33],'scope':'isolated instrumented emulator onDrawFrame plus glFinish;360 measured frames after120warmup per480-frame job; capture/PNG I/O excluded; not app FPS or physical-TV headroom; whole33 candidate versus28baseline, not summed independent costs','rows':summary,'runs':rows}
(root/'combined-cost-results.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['| Preset / workload | Before ms | Candidate ms | Delta ms | Delta % | Cycle deltas % |','|---|---:|---:|---:|---:|---|']
for r in summary:lines.append('| '+r['preset']+' | '+f"{r['before_mean_ms']:.3f} | {r['after_mean_ms']:.3f} | {r['delta_ms']:+.3f} | {r['delta_percent']:+.2f}"+' | '+', '.join(f"{c['delta_percent']:+.2f}" for c in r['cycles'])+' |')
(root/'combined-cost-table.md').write_text('\n'.join(lines)+'\n')
print('Verified84 jobs and',capture_count,'captures; all matched frozen focused witness')
print('\n'.join(lines))
