"""Measure separate nominal solver bounds on consumed main/shape source graphs.

No equation/shader execution or rendered input. Persistent state, qualified
coordinates and missing input domains remain explicit unsupported outcomes.
"""
import argparse
import atexit
from concurrent.futures import ProcessPoolExecutor
import gzip
import json
import math
import multiprocessing
from pathlib import Path
import time

from corpus_store import discover,file_hash,atomic_json

MODELS=('source_proofs.py','source_proofs_worker.py','source_symbolic.py',
        'source_control_bounds.py','effect_families.py','equation_loading.py',
        'equation_domains.py','scene_equations.py','shader_fields.py',
        'source_appearance.py','source_context.py','source_forms.py','field_math.py',
        'stage_resolution.py','native_values.py','forecast.py')
_SESSION=None


def model_hashes():
    return {name:file_hash(Path(__file__).parent/name) for name in MODELS}


def initialize(python,reader,models):
    global _SESSION,_READER,_MODELS
    from source_proofs import ProofSession
    _SESSION=ProofSession(python);_SESSION.__enter__();atexit.register(_SESSION.close)
    _READER=Path(reader);_MODELS=models


def evaluate(case):
    from effect_families import _Analysis,_CACHE,_deps
    from forecast import read_source
    from source_control_bounds import scalar_value_envelope
    from source_input_scenario import validate_scenario
    from source_appearance import EEL_AUDIO,SHAPE_CONTROLS,MESH_CONTROLS
    from source_proofs import ACTIVE
    if model_hashes()!=_MODELS:raise ValueError('frozen proof source model changed')
    started=time.perf_counter();row={'preset':{k:case[k] for k in ('relative_path','sha256')},
        'status':'computed','changes':[],'refinement_counts':{},'controls_tested':0,
        'unknown_checks':0,'solver_checks':0,'analysis_seconds':0.,'query_seconds':0.}
    source=read_source(case['path'],reader=_READER)
    if source['preset_sha256']!=case['sha256'] or file_hash(case['path'])!=case['sha256']:
        raise ValueError('frozen proof preset changed')
    row['engine']=source['parser_inputs']['engine']
    domains=validate_scenario({'schema_version':1,'name':'declared-band-control',
        'audio_band_ranges':{name:[0,2] for name in EEL_AUDIO}})['scalar_input_domains']
    token=_CACHE.set({});start_analysis=time.perf_counter()
    try:
        analysis=_Analysis(source,'gles300',None);analysis.main_equations();analysis.primitives()
        components=[('mesh_warp',analysis.mesh_controls,MESH_CONTROLS)]
        components += [(name,controls,SHAPE_CONTROLS) for name,controls in analysis.component_controls.items()]
        row['analysis_seconds']=time.perf_counter()-start_analysis
        for component,controls,consumed in components:
            for name in consumed:
                field=controls.get(name)
                if field is None:continue
                dependencies=_deps(field)
                # Count actual control expressions, excluding constant/default
                # fields whose intervals already contain no input uncertainty.
                if not dependencies:continue
                disabled=ACTIVE.set(None)
                try:baseline=scalar_value_envelope(field,input_domains=domains)
                finally:ACTIVE.reset(disabled)
                query_start=time.perf_counter();trial=scalar_value_envelope(field,input_domains=domains)
                row['query_seconds']+=time.perf_counter()-query_start
                proof=trial['solver_refinement'];status=proof['status']
                row['controls_tested']+=1
                row['refinement_counts'][status]=row['refinement_counts'].get(status,0)+1
                row['unknown_checks']+=proof.get('unknown_checks',0)
                row['solver_checks']+=proof.get('solver_checks',0)
                before=baseline['nominal_value_range'];after=proof['nominal_value_range']
                if after is None:continue
                if before is not None and (after[0]<before[0] or after[1]>before[1]):
                    # A separately computed real result can be wider. Preserve
                    # it in status counts without labelling it a tighter bound.
                    continue
                if before==after:continue
                old_width=None if before is None else before[1]-before[0]
                new_width=after[1]-after[0]
                material=old_width is None or not math.isfinite(old_width) or old_width>0 and new_width<.99*old_width
                row['changes'].append({'element':component,'control':name,'scenario':'declared_audio_0_2',
                    'before':before,'after':after,'materially_tighter':material,
                    'original_program_inputs':sorted(dependencies),'proof':proof,
                    'baseline_unknown_reasons':baseline['unknown_reasons']})
        row['equation_unknowns']=analysis.unknowns
    except (ValueError,RecursionError,OverflowError,IndexError) as error:
        row.update(status='unresolved',reason=str(error))
    finally:_CACHE.reset(token)
    row['elapsed_seconds']=time.perf_counter()-started
    row['worker_failure']=_SESSION.failure
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--presets',type=Path,default=Path('core/src/main/assets/presets'))
    parser.add_argument('--sample-manifest',type=Path)
    parser.add_argument('--reader',type=Path,required=True)
    parser.add_argument('--proof-python',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,choices=range(1,5),default=4)
    parser.add_argument('--limit',type=int)
    args=parser.parse_args();cases=discover(args.presets)
    sample_hash=None
    if args.sample_manifest:
        sample=json.loads(args.sample_manifest.read_text());sample_hash=file_hash(args.sample_manifest)
        selected=sample.get('presets',sample.get('source_inventory',[]))
        by_name={c['relative_path']:c for c in cases};cases=[]
        for requested in selected:
            case=by_name[requested['relative_path']]
            if case['sha256']!=requested['sha256']:raise ValueError('sample source hash changed')
            cases.append(case)
        if not cases:raise ValueError('sample manifest contains no presets')
    if args.limit is not None:
        if args.limit<1:raise ValueError('positive limit required')
        cases=cases[:args.limit]
    args.output.mkdir(parents=True,exist_ok=False)
    identity={'model_modules':model_hashes(),'reader_sha256':file_hash(args.reader),
        'source_inventory':[{k:c[k] for k in ('relative_path','sha256')} for c in cases],
        'sample_manifest_sha256':sample_hash,'runner_sha256':file_hash(__file__),
        'workers':args.workers,'backend':'z3-5.1.0.0','proof_python':str(args.proof_python.absolute()),
        'declared_audio_domains':{name:[0,2] for name in ('bass','mid','treb','bass_att','mid_att','treb_att')},
        'scope':'consumed main/perpixel/shape source scalar envelopes with explicit audio0_2 domains; no shader-field or native-state proof census',
        'uses_equation_execution':False,'uses_shader_execution':False,'uses_rendered_images':False,
        'baseline_predictions_changed':False,'native_numeric_certified':False}
    atomic_json(args.output/'manifest.json',identity);rows=[];started=time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn'),
        initializer=initialize,initargs=(str(args.proof_python),str(args.reader),identity['model_modules'])) as pool:
        with gzip.open(args.output/'rows.jsonl.gz','wt') as output:
            for row in pool.map(evaluate,cases,chunksize=1):
                if model_hashes()!=identity['model_modules'] or file_hash(args.reader)!=identity['reader_sha256']:
                    raise ValueError('frozen proof model/reader changed')
                rows.append(row);output.write(json.dumps(row,sort_keys=True,allow_nan=False)+'\n');output.flush()
                if len(rows)%100==0:
                    print(json.dumps({'completed':len(rows),'total':len(cases),
                        'changed_presets':sum(bool(r['changes']) for r in rows)}),flush=True)
    counts={}
    for row in rows:
        for status,count in row['refinement_counts'].items():counts[status]=counts.get(status,0)+count
    summary={'presets':len(rows),'computed_presets':sum(r['status']=='computed' for r in rows),
        'unresolved_presets':sum(r['status']!='computed' for r in rows),'controls_tested':sum(r['controls_tested'] for r in rows),
        'changed_presets':sum(bool(r['changes']) for r in rows),
        'new_nominal_bounds':sum(c['before'] is None for r in rows for c in r['changes']),
        'tighter_nominal_bounds':sum(c['before'] is not None for r in rows for c in r['changes']),
        'materially_tighter_bounds':sum(c['materially_tighter'] for r in rows for c in r['changes']),
        'materially_improved_presets':sum(any(c['materially_tighter'] for c in r['changes']) for r in rows),
        'refinement_counts':counts,'unknown_solver_checks':sum(r['unknown_checks'] for r in rows),
        'solver_checks':sum(r['solver_checks'] for r in rows),'query_seconds_sum':sum(r['query_seconds'] for r in rows),
        'source_analysis_seconds_sum':sum(r['analysis_seconds'] for r in rows),
        'wall_seconds':time.perf_counter()-started,'max_preset_seconds':max(r['elapsed_seconds'] for r in rows),
        'presets_with_unavailable_component':sum(bool(r['worker_failure']) for r in rows),
        'manifest_sha256':file_hash(args.output/'manifest.json'),'rows_sha256':file_hash(args.output/'rows.jsonl.gz'),
        'baseline_predictions_changed':False,'native_bounds_changed':False,
        'appearance_accuracy_verified':False,'mood_accuracy_verified':False}
    atomic_json(args.output/'summary.json',summary);print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
