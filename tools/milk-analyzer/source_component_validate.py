"""Compare optional source components on all main/shape audio-control graphs.

Native source parsing and symbolic algebra only. No shader/frame/audio execution.
Shader-field graphs and final visual/mood accuracy are outside this census.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import gzip
import json
import multiprocessing
from pathlib import Path
import time

from corpus_store import discover, file_hash, atomic_json
from effect_family_export import loaded_model_hashes

_SESSION = None


def initialize(python, reader, models):
    global _SESSION, _READER, _MODELS
    from source_symbolic import SymbolicSession
    _SESSION = SymbolicSession(python)
    _SESSION.__enter__()
    _READER = Path(reader)
    _MODELS = models
    import atexit
    atexit.register(_SESSION.close)


def evaluate(case):
    from effect_families import _Analysis, _CACHE, _deps
    from forecast import read_source
    from source_control_bounds import scalar_response_envelope
    from source_input_scenario import validate_scenario
    from source_appearance import EEL_AUDIO, SHAPE_CONTROLS, MESH_CONTROLS
    from source_symbolic import ACTIVE
    started = time.perf_counter()
    row = {'preset': {k: case[k] for k in ('relative_path', 'sha256')},
           'status': 'computed', 'changes': [], 'refinement_counts': {}, 'controls_tested': 0}
    if loaded_model_hashes() != _MODELS:
        raise ValueError('frozen source model changed')
    source = read_source(case['path'], reader=_READER)
    if source['preset_sha256'] != case['sha256'] or file_hash(case['path']) != case['sha256']:
        raise ValueError('frozen preset changed')
    row['engine'] = source['parser_inputs']['engine']
    domains = validate_scenario({'schema_version': 1, 'name': 'declared-band-control',
        'audio_band_ranges': {name: [0, 2] for name in EEL_AUDIO}})['scalar_input_domains']
    token = _CACHE.set({})
    try:
        analysis = _Analysis(source, 'gles300', None)
        analysis.main_equations()
        analysis.primitives()
        components = [('mesh_warp', analysis.mesh_controls, MESH_CONTROLS)]
        components += [(name, controls, SHAPE_CONTROLS)
                       for name, controls in analysis.component_controls.items()]
        for component, controls, consumed in components:
            for name in consumed:
                field = controls.get(name)
                if field is None:
                    continue
                dependencies = _deps(field)
                for band in EEL_AUDIO:
                    if band not in dependencies:
                        continue
                    for scenario, inputs in (('unconstrained', None), ('declared_0_2', domains)):
                        disabled = ACTIVE.set(None)
                        try:
                            baseline = scalar_response_envelope(field, input_names={band}, input_domains=inputs)
                        finally:
                            ACTIVE.reset(disabled)
                        trial = scalar_response_envelope(field, input_names={band}, input_domains=inputs)
                        row['controls_tested'] += 1
                        refinement = trial.get('symbolic_refinement')
                        status = 'baseline_zero' if refinement is None else refinement['status']
                        row['refinement_counts'][status] = row['refinement_counts'].get(status, 0) + 1
                        before = baseline['maximum_absolute_control_change_per_audio_unit']
                        after = trial['maximum_absolute_control_change_per_audio_unit']
                        if before != after:
                            row['changes'].append({'element': component, 'control': name, 'band': band,
                                'scenario': scenario, 'before': before, 'after': after,
                                'original_program_inputs': sorted(dependencies), 'refinement': refinement})
        row['equation_unknowns'] = analysis.unknowns
    except (ValueError, RecursionError, OverflowError, IndexError) as error:
        row.update(status='unresolved', reason=str(error))
    finally:
        _CACHE.reset(token)
    row['elapsed_seconds'] = time.perf_counter() - started
    row['worker_failure'] = _SESSION.failure
    row['worker_stats'] = dict(_SESSION.stats)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--presets', type=Path, default=Path('core/src/main/assets/presets'))
    parser.add_argument('--reader', type=Path, required=True)
    parser.add_argument('--symbolic-python', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, choices=range(1, 5), default=4)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    cases = discover(args.presets)
    if args.limit is not None:
        if args.limit < 1:
            raise ValueError('positive source limit required')
        cases = cases[:args.limit]
    args.output.mkdir(parents=True, exist_ok=False)
    models = loaded_model_hashes()
    identity = {'model_modules': models, 'reader_sha256': file_hash(args.reader),
        'source_inventory': [{k: c[k] for k in ('relative_path', 'sha256')} for c in cases],
        'native_operations': 'source parsing only', 'uses_equation_execution': False,
        'uses_shader_execution': False, 'uses_rendered_images': False,
        'scope': 'main/shape control response comparisons; excludes custom shader fields and final visibility',
        'runner_sha256': file_hash(__file__), 'workers': args.workers,
        'declared_audio_domains': {name: [0, 2] for name in ('bass','mid','treb','bass_att','mid_att','treb_att')},
        'symbolic_python': str(args.symbolic_python.absolute()), 'backend_version': 'sympy1.14.0'}
    atomic_json(args.output/'manifest.json', identity)
    rows = []; start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn'),
        initializer=initialize, initargs=(str(args.symbolic_python), str(args.reader), models)) as pool:
        with gzip.open(args.output/'rows.jsonl.gz', 'wt') as output:
            for row in pool.map(evaluate, cases, chunksize=1):
                if loaded_model_hashes() != models or file_hash(args.reader) != identity['reader_sha256']:
                    raise ValueError('frozen source model/reader changed')
                rows.append(row)
                output.write(json.dumps(row, sort_keys=True, allow_nan=False)+'\n')
                output.flush()
                if len(rows) % 100 == 0:
                    print(json.dumps({'completed': len(rows), 'total': len(cases),
                        'changed_presets': sum(bool(r['changes']) for r in rows)}), flush=True)
    counts = {}
    for row in rows:
        for status, count in row['refinement_counts'].items():
            counts[status] = counts.get(status, 0) + count
    summary = {'presets': len(rows), 'changed_presets': sum(bool(r['changes']) for r in rows),
        'unresolved_presets': sum(r['status'] != 'computed' for r in rows),
        'new_bounds': sum(c['before'] is None for r in rows for c in r['changes']),
        'tighter_bounds': sum(c['before'] is not None for r in rows for c in r['changes']),
        'more_than_1_percent_tighter_bounds': sum(c['before'] is not None and c['before'] > 0 and c['after'] < .99*c['before'] for r in rows for c in r['changes']),
        'materially_improved_presets': sum(any(c['before'] is None or c['before'] > 0 and c['after'] < .99*c['before'] for c in r['changes']) for r in rows),
        'presets_with_unavailable_component': sum(bool(r['worker_failure']) for r in rows),
        'refinement_counts': counts, 'wall_seconds': time.perf_counter()-start,
        'manifest_sha256': file_hash(args.output/'manifest.json'),
        'rows_sha256': file_hash(args.output/'rows.jsonl.gz'),
        'appearance_accuracy_verified': False, 'mood_accuracy_verified': False}
    atomic_json(args.output/'summary.json', summary)
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
