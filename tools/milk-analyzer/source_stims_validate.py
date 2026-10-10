"""Frozen source-only census of supplemental Stims local may-dependencies."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import gzip
import json
import multiprocessing
from pathlib import Path
import subprocess
import tempfile
import time

from corpus_store import discover, file_hash, atomic_json

MODELS = ('source_stims.py', 'effect_families.py', 'equation_loading.py',
          'scene_equations.py', 'shader_fields.py', 'source_appearance.py')
AUDIO = {'bass', 'mid', 'treb', 'bass_att', 'mid_att', 'treb_att'}


def model_hashes():
    return {name: file_hash(Path(__file__).parent/name) for name in MODELS}


def dependency_signature(record):
    """Compare source identities/sets, independent of output enumeration order."""
    keys = ('control', 'new_current_audio_ancestry', 'baseline_input_dependencies',
            'may_input_dependencies', 'newly_exposed_input_dependencies', 'predecessor_inputs')
    return {change['control']: {key: change[key] for key in keys} for change in record['changes']}


def initialize(reader, models):
    global _READER, _MODELS, _WORKSPACE
    import atexit
    _WORKSPACE = tempfile.TemporaryDirectory(prefix='milk-stims-source-')
    _READER = Path(_WORKSPACE.name)/'reader'
    _READER.write_bytes(Path(reader).read_bytes()); _READER.chmod(0o700)
    _MODELS = models
    atexit.register(_WORKSPACE.cleanup)


def read_frozen_source(case):
    """Reuse one immutable native reader per worker, freeze source per request."""
    from engine_profiles import CORE_2321_ENGINE, CORE_2322_ENGINE, CORE_2325_ENGINE, CORE_2327_ENGINE, CORE_2329_ENGINE, CORE_2331_ENGINE, math_matches
    from scene_equations import source_settings
    frozen = Path(_WORKSPACE.name)/'source.milk'
    frozen.write_bytes(Path(case['path']).read_bytes())
    if file_hash(frozen) != case['sha256']:
        raise ValueError('frozen Stims preset input changed')
    process = subprocess.run([str(_READER), str(frozen)], capture_output=True, text=True, timeout=30)
    if process.returncode:
        raise ValueError('native source parser failed: ' + process.stderr.strip())
    source = json.loads(process.stdout)
    engine = source.get('parser_inputs', {}).get('engine', {})
    if any(math_matches(engine, target) for target in
           (CORE_2321_ENGINE, CORE_2322_ENGINE, CORE_2325_ENGINE, CORE_2327_ENGINE, CORE_2329_ENGINE, CORE_2331_ENGINE)):
        source['parser_inputs']['setting_lookup_policy'] = 'native-case-insensitive-v1'
        source['values'] = source_settings(source)
    source['preset_sha256'] = case['sha256']
    return source


def evaluate(case):
    from effect_families import _CACHE
    from source_stims import source_phase_dependency_evidence
    started = time.perf_counter()
    row = {'preset': {key: case[key] for key in ('relative_path', 'sha256')},
           'status': 'unresolved', 'changes': []}
    if model_hashes() != _MODELS:
        raise ValueError('frozen Stims source model changed')
    try:
        source = read_frozen_source(case)
    except (ValueError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        return {**row, 'reason': str(error), 'converged': False,
                'analysis_seconds': 0, 'elapsed_seconds': time.perf_counter()-started}
    if source['preset_sha256'] != case['sha256'] or file_hash(case['path']) != case['sha256']:
        raise ValueError('frozen Stims preset changed')
    row['engine'] = source['parser_inputs']['engine']
    started_analysis = time.perf_counter()
    token = _CACHE.set({})
    try:
        result = source_phase_dependency_evidence(source)
        row.update(status=result['status'], state_count=result['state_count'],
                   converged=result['converged'], unknowns=result['unresolved_reasons'])
        for name, details in sorted(result['outputs'].items()):
            new_audio = sorted(AUDIO.intersection(details['newly_exposed_input_dependencies']))
            if new_audio:
                row['changes'].append({'control': name, 'new_current_audio_ancestry': new_audio, **details})
    except (ValueError, RecursionError, OverflowError, IndexError) as error:
        row.update(reason=str(error), converged=False)
    finally:
        _CACHE.reset(token)
    row['analysis_seconds'] = time.perf_counter() - started_analysis
    row['elapsed_seconds'] = time.perf_counter() - started
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--presets', type=Path, default=Path('core/src/main/assets/presets'))
    parser.add_argument('--reader', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, choices=range(1, 5), default=4)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--sample-manifest', type=Path)
    parser.add_argument('--prior-rows', type=Path)
    args = parser.parse_args()
    cases = discover(args.presets)
    if args.sample_manifest is not None:
        inventory = json.loads(args.sample_manifest.read_text())['source_inventory']
        indexed = {case['relative_path']: case for case in cases}
        cases = [indexed[item['relative_path']] for item in inventory]
        if any(case['sha256'] != item['sha256'] for case, item in zip(cases, inventory)):
            raise ValueError('fixed source sample identity changed')
    if args.limit is not None:
        if args.limit < 1:
            raise ValueError('positive source limit required')
        cases = cases[:args.limit]
    args.output.mkdir(parents=True, exist_ok=False)
    identity = {'model_modules': model_hashes(), 'reader_sha256': file_hash(args.reader),
                'source_inventory': [{key: case[key] for key in ('relative_path', 'sha256')} for case in cases],
                'runner_sha256': file_hash(__file__), 'workers': args.workers,
                'reader_lifecycle': 'immutable executable copy once per worker; frozen source copy per request',
                'sample_manifest_sha256': None if args.sample_manifest is None else file_hash(args.sample_manifest),
                'prior_rows_sha256': None if args.prior_rows is None else file_hash(args.prior_rows),
                'uses_equation_execution': False, 'uses_shader_execution': False,
                'uses_rendered_images': False,
                'scope': 'main scalar local may-ancestry only; excludes numeric/visible response and custom/pixel scopes'}
    atomic_json(args.output/'manifest.json', identity)
    rows = []; started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn'),
                             initializer=initialize, initargs=(str(args.reader), identity['model_modules'])) as pool:
        with gzip.open(args.output/'rows.jsonl.gz', 'wt') as output:
            for row in pool.map(evaluate, cases, chunksize=1):
                if model_hashes() != identity['model_modules'] or file_hash(args.reader) != identity['reader_sha256']:
                    raise ValueError('frozen Stims model/reader changed')
                rows.append(row); output.write(json.dumps(row, sort_keys=True, allow_nan=False)+'\n')
                if len(rows) % 1000 == 0:
                    print(json.dumps({'completed': len(rows), 'total': len(cases)}), flush=True)
    status_counts = {}
    for row in rows:
        status_counts[row['status']] = status_counts.get(row['status'], 0) + 1
    summary = {'presets': len(rows), 'terminal_status_counts': status_counts,
               'presets_with_new_current_audio_ancestry': sum(bool(row['changes']) for row in rows),
               'main_controls_with_new_current_audio_ancestry': sum(len(row['changes']) for row in rows),
               'main_control_band_paths_added': sum(len(change['new_current_audio_ancestry']) for row in rows for change in row['changes']),
               'numeric_bounds_changed': 0, 'appearance_predictions_changed': 0,
               'wall_seconds': time.perf_counter()-started,
               'analysis_worker_seconds': sum(row['analysis_seconds'] for row in rows),
               'mean_analysis_ms': sum(row['analysis_seconds'] for row in rows)/len(rows)*1000,
               'max_analysis_seconds': max(row['analysis_seconds'] for row in rows),
               'manifest_sha256': file_hash(args.output/'manifest.json'),
               'rows_sha256': file_hash(args.output/'rows.jsonl.gz')}
    if args.prior_rows is not None:
        prior = {row['preset']['relative_path']: row for row in
                 (json.loads(line) for line in gzip.open(args.prior_rows, 'rt'))}
        changed_dependencies = []; changed_unknowns = 0
        for row in rows:
            before = prior[row['preset']['relative_path']]
            if before['preset']['sha256'] != row['preset']['sha256']:
                raise ValueError('prior source row identity changed')
            if dependency_signature(before) != dependency_signature(row):
                changed_dependencies.append(row['preset']['relative_path'])
            if before.get('unknowns') != row.get('unknowns'):
                changed_unknowns += 1
        summary.update(prior_dependency_sets_changed=changed_dependencies,
                       presets_with_changed_explicit_unknowns=changed_unknowns,
                       compared_with_prior_full_pack_rows=len(rows))
    atomic_json(args.output/'summary.json', summary)
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
