"""Compact replay of the frozen source pool; retain all semantic differences."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import hashlib
import json
import multiprocessing
import sys
import time

ROOT=Path.cwd().resolve()
BASE=ROOT/'build/preset-corpus/source-shape-flash-size-2000-2026-10-10'
OUT=ROOT/'build/preset-corpus/source-blackout-projection-replay'
sys.path.insert(0,str(ROOT/'tools/milk-analyzer'))

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def budget_reasons(obj,path=''):
    rows=[]
    if isinstance(obj,dict):
        for k,v in obj.items():rows+=budget_reasons(v,path+'/'+k)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):rows+=budget_reasons(v,path+'/'+str(i))
    elif isinstance(obj,str) and 'budget exceeded' in obj:rows.append({'path':path,'reason':obj})
    return rows

def work(case,model,scenario,reader_sha):
    from effect_family_export import export_preset,loaded_model_hashes
    from corpus_store import file_hash
    reader=ROOT/'build/preset-corpus/source34/adapters/milk-native-reader'
    if loaded_model_hashes()!=model or file_hash(reader)!=reader_sha:raise ValueError('frozen model/reader changed')
    rel=Path(case['relative_path']);path=ROOT/'core/src/main/assets/presets'/rel
    if file_hash(path)!=case['sha256']:raise ValueError('frozen source changed')
    proof=json.loads((BASE/'compatibility'/rel.with_suffix('.json')).read_text())
    old=json.loads((BASE/'results'/rel.with_suffix('.json')).read_text())
    if proof['preset']['sha256']!=case['sha256'] or old['preset']['sha256']!=case['sha256']:raise ValueError('join mismatch')
    new,_=export_preset(path,reader=reader,compatibility=proof['reports'],input_scenario=scenario,cache=None)
    old_a=old['analysis'];new_a=new['analysis']
    def semantic(a):return {k:v for k,v in a.items() if k not in {'record_sha256','analysis_work'}}
    before=digest(semantic(old_a));after=digest(semantic(new_a))
    changed=before!=after
    if changed:
        target=OUT/'changed'/rel.with_suffix('.json');target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(new,sort_keys=True,allow_nan=False))
    return {'preset':case,'semantic_equal':not changed,'before_sha256':before,'after_sha256':after,
        'before_structured':'sampling_geometry' in old_a['visual_description'],
        'after_structured':'sampling_geometry' in new_a['visual_description'],
        'before_work':old_a['analysis_work'],'after_work':new_a['analysis_work'],
        'before_budget_reasons':budget_reasons(old_a),'after_budget_reasons':budget_reasons(new_a),
        'before_unknowns':old_a['unknowns'],'after_unknowns':new_a['unknowns']}

def main():
    from effect_family_export import loaded_model_hashes
    from corpus_store import file_hash
    OUT.mkdir(parents=True,exist_ok=False)
    selection=json.loads((BASE/'sample-selection.json').read_text())
    model=loaded_model_hashes();scenario_path=ROOT/'build/preset-corpus/source-sample-offset-scenario.json'
    scenario=json.loads(scenario_path.read_text());scenario_sha=file_hash(scenario_path)
    reader=ROOT/'build/preset-corpus/source34/adapters/milk-native-reader';reader_sha=file_hash(reader)
    started=time.perf_counter();rows=[]
    with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn')) as pool:
        futures=[pool.submit(work,c,model,scenario,reader_sha) for c in selection['presets']]
        with (OUT/'comparison.jsonl').open('w') as stream:
            for future in as_completed(futures):
                row=future.result();rows.append(row);stream.write(json.dumps(row,sort_keys=True)+'\n');stream.flush()
                if len(rows)%100==0:print(json.dumps({'completed':len(rows),'total':len(futures)}),flush=True)
    if loaded_model_hashes()!=model or file_hash(reader)!=reader_sha or file_hash(scenario_path)!=scenario_sha:raise ValueError('frozen identity changed')
    summary={'count':len(rows),'structured':sum(r['after_structured'] for r in rows),
        'previously_structured_semantic_changes':[r['preset'] for r in rows if r['before_structured'] and not r['semantic_equal']],
        'newly_structured':[r['preset'] for r in rows if not r['before_structured'] and r['after_structured']],
        'lost_structured':[r['preset'] for r in rows if r['before_structured'] and not r['after_structured']],
        'budget_cases':[r['preset'] for r in rows if r['after_budget_reasons']],
        'wall_seconds':time.perf_counter()-started,'model_modules':model,'reader_sha256':reader_sha,
        'selection_sha256':file_hash(BASE/'sample-selection.json'),'scenario_sha256':scenario_sha,
        'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
