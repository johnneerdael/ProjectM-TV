"""Frozen source-only cohort qualification of activity and palette evidence."""
import argparse
import atexit
from contextlib import ExitStack
import subprocess
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import gzip
import json
import multiprocessing
from pathlib import Path
import time

from corpus_store import atomic_json, digest, discover, file_hash
from forecast import model_file_hashes


def compatibility_index(folder):
    records = {}
    for path in sorted(Path(folder).glob('*.json')):
        value = json.loads(path.read_text())
        payload = {key: item for key, item in value.items() if key != 'record_sha256'}
        if digest(payload) != value.get('record_sha256'):
            raise ValueError('saved compatibility seal mismatch: ' + path.name)
        source = value['preset']['sha256']
        if source in records:
            raise ValueError('duplicate saved compatibility source: ' + source)
        records[source] = value
    return records


def bind_compatibility(value, source):
    """Reuse the existing complete source/stage/compiler attribution validator."""
    from source_compile_manifest import compatibility_from_manifest, validate_manifest
    if value['preset']['sha256'] != source['preset_sha256']:
        raise ValueError('saved compatibility preset mismatch')
    reports = value['reports']
    compiler = next(iter(reports.values()), None)
    if compiler is None:
        if value['engine'] != source['parser_inputs']['engine'] or value['engine_archive_sha256'] != source['parser_inputs']['engine_archive_sha256']:
            raise ValueError('saved compatibility engine mismatch')
        return {}
    manifest = {'schema_version': 1, 'kind': 'source-offline-compatibility-set',
                'profile': 'gles300', 'engine': value['engine'],
                'engine_archive_sha256': value['engine_archive_sha256'],
                'native_driver_verified': False, 'runtime_texture_bindings_verified': False,
                'binding_assumptions': 'Saved explicit sampler declarations and texsize names; runtime assets and bindings unverified',
                'compiler_inputs': {key: compiler[key] for key in ('translator_sha256', 'validator_sha256')},
                'presets': {source['preset_sha256']: reports}}
    manifest['record_sha256'] = digest(manifest)
    return compatibility_from_manifest(validate_manifest(manifest, 'gles300'), source)[0]


def initialize(reader, models, compatibility, context, symbolic_python=None, proof_python=None):
    from source_stims_validate import initialize as prepare_reader
    global _MODELS, _COMPATIBILITY, _CONTEXT, _SESSIONS, _MATH
    prepare_reader(reader, models)
    _MODELS, _COMPATIBILITY, _CONTEXT = models, compatibility, context
    _SESSIONS = ExitStack()
    _MATH = {}
    from source_symbolic import SymbolicSession
    from source_proofs import ProofSession
    for name, python, factory in [('symbolic', symbolic_python, SymbolicSession), ('proof', proof_python, ProofSession)]:
        if python is not None:
            _MATH[name] = _SESSIONS.enter_context(factory(python))
    atexit.register(_SESSIONS.close)


def evaluate(case):
    from source_stims_validate import read_frozen_source
    from effect_families import analyze_families
    started = time.perf_counter()
    prior_stats = {name: dict(session.stats) for name, session in _MATH.items()}
    row = {'preset': {key: case[key] for key in ('relative_path', 'sha256')}, 'status': 'unresolved'}
    if model_file_hashes() != _MODELS:
        raise ValueError('frozen behaviour model changed')
    try:
        source = read_frozen_source(case)
        source['numbered_source'] = Path(case['path']).read_text(errors='replace')
        if file_hash(case['path']) != case['sha256']:
            raise ValueError('frozen behaviour source changed')
        compatibility = bind_compatibility(_COMPATIBILITY[case['sha256']], source)
        analysis = analyze_families(source, compatibility=compatibility, behaviour_context=_CONTEXT)
        row.update(status='computed', analysis=analysis)
    except (ValueError, KeyError, RecursionError, OverflowError, IndexError, subprocess.TimeoutExpired) as error:
        row.update(error_type=type(error).__name__, reason=str(error))
    row['source_components'] = {name: {'identity': session.identity, 'stats_delta': {key: count-prior_stats[name][key] for key,count in session.stats.items()}, 'failure': session.failure} for name,session in _MATH.items()}
    row['elapsed_seconds'] = time.perf_counter() - started
    if model_file_hashes() != _MODELS:
        raise ValueError('frozen behaviour model changed during analysis')
    return row


def summarize(rows):
    statuses = Counter(row['status'] for row in rows)
    eligible, provisional, unknowns = Counter(), Counter(), Counter()
    reports = []
    for row in rows:
        report = row.get('analysis', {}).get('visual_description', {}).get('static_behaviour', {})
        if not report or report.get('status') == 'unresolved':
            unknowns.update(report.get('unknown_reasons', [row.get('reason', 'behaviour report unavailable')]))
            continue
        reports.append(report)
        classification = report['classification']
        eligible.update(classification['eligible_bands'])
        provisional.update(classification['predicted_bands'])
        unknowns.update(set(item['reason'] for item in classification['unknown_contributors']))
    return {'presets': len(rows), 'terminal_status_counts': dict(statuses),
            'behaviour_reports': len(reports),
            'presets_with_useful_hue_description': sum(r['colour']['useful_hue_description'] for r in reports),
            'presets_with_conditional_activity_index': sum(r['classification']['intensity']['value'] is not None for r in reports),
            'eligible_bands': dict(eligible), 'provisional_source_potential_bands': dict(provisional),
            'unknown_reasons_by_presets': unknowns.most_common(),
            'uses_rendered_images': False, 'appearance_accuracy_verified': False,
            'scope': 'Source evidence and uncalibrated preference mapping; counts are not visual accuracy'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--presets', type=Path, required=True)
    parser.add_argument('--sample-manifest', type=Path, required=True)
    parser.add_argument('--compatibility', type=Path, required=True)
    parser.add_argument('--reader', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--context', type=Path)
    parser.add_argument('--symbolic-python', type=Path)
    parser.add_argument('--proof-python', type=Path)
    parser.add_argument('--workers', type=int, choices=range(1, 5), default=4)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    from source_static_behaviour import validate_context
    context = validate_context(None if args.context is None else json.loads(args.context.read_text()))
    inventory = json.loads(args.sample_manifest.read_text())['presets']
    indexed = {case['relative_path']: case for case in discover(args.presets)}
    cases = []
    for item in inventory:
        case = indexed[item['relative_path']]
        if case['sha256'] != item['sha256']:
            raise ValueError('fixed behaviour sample source mismatch')
        cases.append(case)
    if args.limit is not None:
        if args.limit < 1:
            raise ValueError('positive sample limit required')
        cases = cases[:args.limit]
    compatibility = compatibility_index(args.compatibility)
    if any(case['sha256'] not in compatibility for case in cases):
        raise ValueError('fixed sample missing source-bound compiler record')
    models = model_file_hashes()
    manifest = {'model_modules': models, 'reader_sha256': file_hash(args.reader),
                'sample_manifest_sha256': file_hash(args.sample_manifest),
                'compatibility_record_hashes': {case['sha256']: compatibility[case['sha256']]['record_sha256'] for case in cases},
                'source_inventory': [{key: case[key] for key in ('relative_path', 'sha256')} for case in cases],
                'context': context, 'workers': args.workers,
                'uses_equation_execution': False, 'uses_shader_execution': False, 'uses_rendered_images': False}
    from source_symbolic import SymbolicSession
    from source_proofs import ProofSession
    manifest['source_components'] = {name: factory(python).identity for name,python,factory in [('symbolic',args.symbolic_python,SymbolicSession),('proof',args.proof_python,ProofSession)] if python is not None}
    args.output.mkdir(parents=True, exist_ok=False)
    atomic_json(args.output/'manifest.json', manifest)
    started = time.perf_counter()
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn'),
                             initializer=initialize, initargs=(str(args.reader), models, compatibility, context, args.symbolic_python, args.proof_python)) as pool:
        with gzip.open(args.output/'rows.jsonl.gz', 'wt') as output:
            for row in pool.map(evaluate, cases, chunksize=1):
                if model_file_hashes() != models or file_hash(args.reader) != manifest['reader_sha256']:
                    raise ValueError('frozen behaviour model/reader changed')
                rows.append(row)
                output.write(json.dumps(row, sort_keys=True, allow_nan=False)+'\n')
                if len(rows) % 100 == 0:
                    print(json.dumps({'completed': len(rows), 'total': len(cases)}), flush=True)
    summary = summarize(rows)
    summary.update(wall_seconds=time.perf_counter()-started,
                   worker_seconds=sum(row['elapsed_seconds'] for row in rows),
                   manifest_sha256=file_hash(args.output/'manifest.json'), rows_sha256=file_hash(args.output/'rows.jsonl.gz'))
    atomic_json(args.output/'summary.json', summary)
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
