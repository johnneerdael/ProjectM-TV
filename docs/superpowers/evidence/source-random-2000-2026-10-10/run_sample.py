"""Frozen random source-only audit using existing native parser/compile/export APIs."""
import argparse
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
import hashlib
import json
import multiprocessing
from pathlib import Path
import sys
import time
import subprocess

SEED='ProjectM-TV-source-random-2000-2026-10-10-v1'


def initialize(root):
    sys.path.insert(0,str(Path(root)/'tools/milk-analyzer'))


def work(case,root,scenario,expected):
    initialize(root)
    from corpus_store import digest,file_hash
    from forecast import read_source
    from corpus_worker import compatibility_for
    from effect_family_export import export_preset,loaded_model_hashes
    from analyzer_test_profiles import validator_path
    root=Path(root);bins=root/'build/preset-corpus/source34/adapters';reader=bins/'milk-native-reader'
    validator=validator_path().resolve();started=time.perf_counter()
    try:
        if loaded_model_hashes()!=expected['model_modules']:raise ValueError('worker model identity changed')
        for p,sha in expected['native_tools'].items():
            if file_hash(p)!=sha:raise ValueError('worker native tool identity changed')
        source=read_source(Path(case['path']),reader=reader)
        if source['preset_sha256']!=case['sha256']:raise ValueError('source hash changed')
        reports,refs=compatibility_for(source,bins,validator)
        proof={'preset':{k:case[k] for k in ('relative_path','name','sha256')},
            'engine':source['parser_inputs']['engine'],
            'engine_archive_sha256':source['parser_inputs']['engine_archive_sha256'],
            'reports':reports,'referenced_samplers':refs,
            'native_driver_verified':False,'runtime_texture_bindings_verified':False}
        proof['record_sha256']=digest(proof)
        result,hit=export_preset(case['path'],reader=reader,compatibility=reports,input_scenario=scenario,cache=None)
        result['provenance']['offline_compile_evidence']={
            'record_sha256':proof['record_sha256'],'native_driver_verified':False,
            'runtime_texture_bindings_verified':False,
            'binding_assumptions':'Conditional explicit sampler/texture-size declarations from corpus_worker.compatibility_for; no selected images, driver or upload claims'}
        return result,proof,time.perf_counter()-started
    except Exception as error:
        return {'export_kind':'preset-effect-families','status':'timeout' if isinstance(error,subprocess.TimeoutExpired) else 'error','analysis':None,
            'error_type':type(error).__name__,'error':str(error),
            'uses_rendered_reference':False,'appearance_accuracy_verified':False},None,time.perf_counter()-started


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path.cwd())
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--count',type=int,default=2000)
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args();root=args.root.resolve();initialize(root)
    from corpus_store import discover,file_hash,digest,atomic_json,RunStore
    from effect_family_export import loaded_model_hashes
    from analyzer_test_profiles import validator_path
    if not 1<=args.workers<=4:raise ValueError('workers must be 1..4 for this bounded audit')
    inventory=discover(root/'core/src/main/assets/presets')
    if not 1<=args.count<=len(inventory):raise ValueError('sample count outside corpus')
    def rank(c):return hashlib.sha256((SEED+'\0'+c['relative_path']+'\0'+c['sha256']).encode()).hexdigest()
    cases=sorted(inventory,key=rank)[:args.count]
    bins=root/'build/preset-corpus/source34/adapters';scenario_path=root/'build/preset-corpus/source-sample-offset-scenario.json'
    scenario=json.loads(scenario_path.read_text())
    tools=[bins/'milk-native-reader',bins/'milk-shader-translate',validator_path().resolve()]
    identity={'export_kind':'source-random-sample-audit','model_modules':loaded_model_hashes(),
        'native_tools':{str(p):file_hash(p) for p in tools},'runner_sha256':file_hash(__file__),
        'sampling_seed':SEED,'sampling_policy':'ascending SHA256(seed NUL relative-path NUL full-source-SHA256)',
        'source_inventory_sha256':digest([{k:c[k] for k in ('relative_path','sha256')} for c in inventory]),
        'corpus_count':len(inventory),'sample_count':args.count,'scenario_sha256':file_hash(scenario_path),
        'simulation':False,'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False,
        'native_operations':'file parsing and source-bound offline translation/validation only','AI_involved':False}
    args.output.mkdir(parents=True,exist_ok=True)
    selection={'identity':identity,'presets':[{**{k:c[k] for k in ('relative_path','sha256')},'rank':rank(c)} for c in cases]}
    with RunStore(args.output,identity,cases,batch_size=100) as store:
        selection_path=args.output/'sample-selection.json'
        if selection_path.exists() and json.loads(selection_path.read_text())!=selection:
            raise ValueError('saved sample selection changed')
        if not selection_path.exists():atomic_json(selection_path,selection)
        remaining=iter(store.pending());started=time.perf_counter()
        print(json.dumps({'event':'ready','presets':len(cases),'pending':len(store.pending()),'workers':args.workers,'simulation':False,'output':str(args.output)}),flush=True)
        with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
            active={}
            def submit():
                case=next(remaining,None)
                if case is not None:active[pool.submit(work,case,str(root),scenario,identity)]=case
            for _ in range(args.workers):submit()
            while active:
                ready,_=wait(active,return_when=FIRST_COMPLETED)
                for future in ready:
                    case=active.pop(future);result,proof,seconds=future.result()
                    if loaded_model_hashes()!=identity['model_modules'] or file_hash(scenario_path)!=identity['scenario_sha256']:
                        raise ValueError('frozen model/scenario changed')
                    for p,sha in identity['native_tools'].items():
                        if file_hash(p)!=sha:raise ValueError('frozen native compiler/parser changed')
                    if file_hash(__file__)!=identity['runner_sha256']:raise ValueError('frozen runner changed')
                    if proof is not None:atomic_json(args.output/'compatibility'/Path(case['relative_path']).with_suffix('.json'),proof)
                    store.complete(case,result)
                    print(json.dumps({'event':'preset_completed','completed':sum(store.counts().values()),'preset':case['name'],
                        'status':result['status'],'elapsed_seconds':round(seconds,3),'wall_seconds':round(time.perf_counter()-started,3),'counts':store.counts()}),flush=True)
                    submit()
        store.flush(partial=True)
        print(json.dumps({'event':'finished','counts':store.counts(),'wall_seconds':time.perf_counter()-started}),flush=True)


if __name__=='__main__':main()
