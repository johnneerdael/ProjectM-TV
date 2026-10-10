"""Recheck the frozen first100 without rendering or source program execution."""
from collections import Counter
from pathlib import Path
import hashlib
import gzip
import json
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'tools/milk-analyzer'))
from effect_families import analyze_families
from source_motion_behaviour import motion_evidence
from source_symbolic import SymbolicSession
from test_effect_families import read
import source_appearance

BASE = Path(__file__).resolve().parent

def modules():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT / 'tools/milk-analyzer').glob('source_*.py')}


def main():
    selection = json.loads((BASE / 'source-selection.json').read_text())
    original = source_appearance.appearance_from_analysis
    collected = []
    durations = []
    context = {'viewport': [1920, 1080], 'feedback_fps': 30}
    def capture(analysis):
        description = original(analysis)
        start = time.perf_counter()
        motion = motion_evidence(analysis, description, context)
        durations.append(time.perf_counter()-start)
        collected.append({'source_sha256': analysis.source['preset_sha256'], 'motion': motion})
        return description
    source_appearance.appearance_from_analysis = capture
    before = modules()
    started = time.perf_counter()
    records = []
    python = os.environ['MILK_SYMBOLIC_PYTHON']
    with SymbolicSession(Path(python)) as session:
        for i, row in enumerate(selection['presets']):
            raw = (ROOT / 'core/src/main/assets/presets' / row['relative_path']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == row['sha256']
            count = len(collected)
            try:
                result = analyze_families(read(raw))
                fact = collected[-1] if len(collected) > count else {'motion': None, 'unknowns': result['unknowns']}
                records.append({'relative_path': row['relative_path'], **fact})
            except Exception as error:
                records.append({'relative_path': row['relative_path'], 'source_sha256': row['sha256'],
                                'motion': None, 'exception': type(error).__name__+': '+str(error)})
            if (i+1) % 20 == 0: print(f'completed {i+1}/100', flush=True)
        stats = dict(session.stats)
    after = modules()
    used = sorted({Path(module.__file__).name for module in list(sys.modules.values())
                   if getattr(module, '__file__', None) and Path(module.__file__).parent == ROOT / 'tools/milk-analyzer'
                   and Path(module.__file__).name.startswith('source_')})
    quantities = Counter(row['kind'] for r in records if r['motion'] for row in r['motion']['contributions']
                         if row['speed_interval_vp_per_second'][1] is not None)
    unresolved = Counter(row['kind'] for r in records if r['motion'] for row in r['motion']['unresolved_contributors'])
    summary = {'policy': 'source-motion-producer-first100-v1',
               'selection_sha256': hashlib.sha256((BASE / 'source-selection.json').read_bytes()).hexdigest(),
               'context': context, 'source_count': len(records),
               'resolved_records': sum(r['motion'] is not None for r in records),
               'quantified_kind_counts': dict(quantities), 'unresolved_kind_counts': dict(unresolved),
               'elapsed_seconds': time.perf_counter()-started, 'motion_producer_seconds': sum(durations),
               'motion_producer_mean_seconds': sum(durations)/len(durations),
               'backend_stats': stats, 'source_modules_before': before,
               'source_modules_changed_during_run': sorted(name for name in set(before)|set(after) if before.get(name) != after.get(name)),
               'source_modules_used': used,
               'used_source_modules_changed_during_run': sorted(name for name in used if before.get(name) != after.get(name)),
               'uses_rendered_images': False, 'uses_shader_execution': False,
               'scope': 'movement producer qualification; integrated score and prominence are separate gates',
               'records': records}
    full = (json.dumps(summary, indent=2, allow_nan=False)+'\n').encode()
    (BASE / 'first100-census.json.gz').write_bytes(gzip.compress(full, mtime=0))
    compact = {k: v for k, v in summary.items() if k != 'records'}
    compact['full_evidence_sha256'] = hashlib.sha256(full).hexdigest()
    compact['full_evidence_file'] = 'first100-census.json.gz'
    compact['records'] = []
    omit = {'derivative_reports', 'sampling_record', 'source_evidence', 'conditions'}
    for record in records:
        motion = record.get('motion')
        if motion is None:
            compact['records'].append(record)
            continue
        compact['records'].append({'relative_path': record['relative_path'], 'source_sha256': record['source_sha256'],
            'motion_record_sha256': motion['record_sha256'], 'model_sha256': motion['model_sha256'],
            'maximum_potential_speed_interval_vp_per_second': motion['maximum_potential_speed_interval_vp_per_second'],
            'contributions': [{k: v for k, v in row.items() if k not in omit} for row in motion['contributions']],
            'unresolved_contributors': motion['unresolved_contributors']})
    (BASE / 'first100-census.json').write_text(json.dumps(compact, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: v for k, v in summary.items() if k not in {'records', 'source_modules_before'}}, indent=2))


if __name__ == '__main__': main()
