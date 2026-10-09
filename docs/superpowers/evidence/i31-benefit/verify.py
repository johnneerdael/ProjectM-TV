"""Verify the frozen I31 timing and selected-frame records without rendering."""
import gzip
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
load = lambda name: json.loads((root / name).read_text())
workers, schedule = load('workers.json'), load('schedule.json')
with gzip.open(root / 'timed-runs.json.gz', 'rt') as stream:
    runs = json.load(stream)
assert len(schedule) == len(runs) == 80
assert set(runs) == {job['name'] for job in schedule}
before, after = workers['without-0019'], workers['with-0019']
assert before['harness'] == after['harness']
assert {path for path in set(before['source']) | set(after['source'])
        if before['source'].get(path) != after['source'].get(path)} == {
            'src/libprojectM/MilkdropPreset/VideoEcho.cpp'}
measured_frames = 0
for job in schedule:
    run = runs[job['name']]
    assert run['status'] == 'success' and run['gl_error_frames'] == 0
    assert run['gl_renderer'] == 'Apple M4 Pro'
    assert run['width'] == 3840 and run['height'] == 2160
    assert run['frames'] == 480 and run['warmup_frames'] == 120
    assert run['identity']['role'] == job['role']
    assert run['identity']['worker_sha256'] == workers[job['role']]['worker_sha256']
    source_digest = hashlib.sha256(json.dumps(workers[job['role']]['source'],
        sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert run['identity']['source_tree_sha256'] == source_digest
    assert run['gpu_timer_valid'] and run['gpu_probe_nonzero'] == 10
    assert len(run['samples']) == 480
    expected = 2 if job['case'] == 'inactive-classic' or job['role'] == 'with-0019' else 3
    measured = [sample for sample in run['samples'] if sample['measured']]
    assert len(measured) == 360
    assert all(sample['gamma_draws'] == expected and sample['gamma_invocations'] == 1
               and sample['gpu_ns'] > 0 for sample in measured)
    measured_frames += len(measured)
visual = load('visual-results.json')
for profile in ('classic', 'standard'):
    for role in ('with-0019', 'without-0019'):
        assert visual[profile][role]['repeat_equal']
        assert visual[profile][role]['hashes'][0] == visual[profile][role]['hashes'][1]
    assert visual[profile]['with-0019']['hashes'] == visual[profile]['without-0019']['hashes']
    assert all(value['total_rgb_difference'] == 0
               for value in visual[profile]['frame_differences'].values())
print(f'PASS: 80 timed runs, {measured_frames} measured frames, exact one-patch ablation; '
      '3→2 active draws, 2→2 control, selected RGB/repeats match')
