"""Owned emulator5582 native-frame validation of the bug/native-4k-phase-aware-diffusion reference-footprint
product (patch 0036 rewrite) against classic29 ref0 and the retained raw-point/P1 rows (read-only; raw-point equals
the merged PR28 product at 96/96 selected frames). Adapted from mrt-fix-validation/run.py; immutable resumable jobs."""
import collections
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
import zipfile

sys.dont_write_bytecode = True
import cv2
import numpy as np

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[2]
PROVIDER = ROOT / 'docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/run.py'
LAUNCH = ROOT / 'build/native-4k-current-main/emulator/launch.json'
SERIAL = 'emulator-5582'
DRIVER = 'Android Emulator OpenGL ES Translator (Apple M4 Pro)'
PICKS = [120, 150, 180, 210, 239, 300, 390, 479]
NAMES = ['$$$ Royal - Mashup (191).milk',
         'Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk',
         'Fed - quadratrail.milk',
         'Fumbling_Foo + En D & Martin - Mandelverse.milk',
         '$$$ Royal - Mashup (255).milk',
         'astral spinorgentics encrustcore nz+.milk']
PROFILES = {'classic': (1182, 665), '1330': (2364, 1330), '2160': (3840, 2160)}
LUMA = np.array([.2126, .7152, .0722], dtype=np.float32)
spec = importlib.util.spec_from_file_location('mrt_fix_core_provider', PROVIDER)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
assert runner.ROOT.resolve() == ROOT
lock = (WORK / 'host.lock').open('a')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
launch = json.loads(LAUNCH.read_text())
launch_sha = runner.file_hash(LAUNCH)


def validate_serial(value):
    if value != SERIAL:
        raise ValueError('Only explicitly delegated emulator-5582 is authorized')
    return value


def guard(value):
    validate_serial(value)
    assert runner.file_hash(LAUNCH) == launch_sha, 'Owned launch changed'
    assert launch['serial'] == SERIAL and type(launch['pid']) is int and launch['pid'] > 0
    owner = ROOT / 'build/native-4k-current-main/emulator'
    assert Path(launch['avd']).resolve().is_relative_to((owner / 'avds').resolve())
    command = launch['command']
    assert command[command.index('-port') + 1] == '5582'
    name = command[command.index('-avd') + 1]
    os.kill(launch['pid'], 0)
    process = subprocess.check_output(['ps', '-p', str(launch['pid']), '-o', 'command='], text=True)
    assert 'qemu-system-aarch64' in process and f'-avd {name}' in process and '-port 5582' in process
    qemu = subprocess.check_output(['adb', '-s', SERIAL, 'shell', 'getprop', 'ro.kernel.qemu'], text=True, timeout=30).strip()
    assert qemu == '1'
    return {'launch_sha256': launch_sha, 'pid': launch['pid'], 'avd': launch['avd'], 'command': command, 'ro.kernel.qemu': qemu}


runner.validate_device = validate_serial
runner.require_owned_emulator = guard
ownership = guard(SERIAL)
records = [{"path": name, "sha256": runner.file_hash(ROOT / 'core/src/main/assets/presets' / name),
            "bytes": (ROOT / 'core/src/main/assets/presets' / name).stat().st_size} for name in NAMES]
FIX_COMMIT = '45961f8c39d8820501c3a3dab37bb58761a988be'
COMPARATOR = ROOT / 'build/native-4k-current-main/raw-point-controls'
metadata_paths = {
    'reference': ROOT / 'build/native-4k-current-main/classic-reference-control/worker-baseline.json',
    'raw-point': ROOT / 'build/native-4k-current-main/raw-point-experiment/worker-candidate.json',
    'footprint': WORK / 'worker/worker-candidate.json'}
roles = {}
artifact_proofs = {}
for name, metadata_path in metadata_paths.items():
    metadata = json.loads(metadata_path.read_text())
    identity = metadata['backend_identity']
    apk = Path(metadata['apk'])
    assert runner.file_hash(apk) == metadata['apk_sha256']
    with zipfile.ZipFile(apk) as archive:
        assert json.loads(archive.read('assets/backend-identity.json')) == identity
        core_sha = hashlib.sha256(archive.read(identity['core_library_entry'])).hexdigest()
        assert core_sha == identity['core_sha256']
        for record in records:
            assert hashlib.sha256(archive.read('assets/presets/' + record['path'])).hexdigest() == record['sha256']
    export = apk.parent
    source = export / 'repo'
    aar = source / 'core/build/outputs/aar/core-release.aar'
    if not aar.exists():
        with (WORK / (name + '-aar-build.log')).open('w') as log:
            subprocess.run([str(source / 'gradlew'), '--no-daemon', ':core:bundleReleaseAar'], cwd=source,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
    with zipfile.ZipFile(aar) as archive:
        assert hashlib.sha256(archive.read('jni/arm64-v8a/libprojectmtv.so')).hexdigest() == core_sha
    units = list((source / 'core/.cxx/RelWithDebInfo').glob('*/*/compile_commands.json'))
    if units:
        compiled = {str(p.relative_to(source)): runner.file_hash(p) for p in units}
    else:
        # The recorded build-cache cleanup removed the comparator roles' .cxx intermediates; their compile
        # provenance was recorded by mrt-fix-validation for the same unchanged APK/AAR (verified here).
        assert name != 'footprint'
        prior = json.loads((WORK.parent / 'mrt-fix-validation/artifact-proof.json').read_text())[name]
        assert prior['apk_sha256'] == runner.file_hash(apk) and prior['aar_sha256'] == runner.file_hash(aar)
        assert prior['matching_elf_sha256'] == core_sha
        compiled = dict(prior['compiled_sources'], provenance='mrt-fix-validation/artifact-proof.json (cleanup-removed .cxx)')
    artifact_proofs[name] = {'apk': str(apk), 'apk_sha256': runner.file_hash(apk), 'aar': str(aar),
                            'aar_sha256': runner.file_hash(aar), 'matching_elf_sha256': core_sha,
                            'metadata_sha256': runner.file_hash(metadata_path),
                            'compiled_sources': compiled}
    roles[name] = {'apk_path': str(apk), 'apk_sha256': metadata['apk_sha256'], 'core_sha256': core_sha,
                   'backend_identity': identity, 'backend_identity_sha256': runner.digest(identity),
                   'metadata_path': str(metadata_path), 'metadata_sha256': runner.file_hash(metadata_path)}
assert roles['reference']['backend_identity']['private_reference_control']['reference_width'] == 0
assert roles['reference']['backend_identity']['private_reference_control']['reference_height'] == 0
for name in ['raw-point', 'footprint']:
    runner.validate_observer_pair(roles['reference'], roles[name])
    assert roles[name]['backend_identity']['source_commit'] == ('790aaa249d3cabe8e6ab01e5382e046d4b778252' if name == 'raw-point' else FIX_COMMIT)
    assert roles[name]['backend_identity']['ordered_patches'][:29] == roles['reference']['backend_identity']['ordered_patches']
    core_a = roles[name]['backend_identity']['original_core_source_sha256']
    core_b = roles['reference']['backend_identity']['original_core_source_sha256']
    differing = sorted(k for k in set(core_a) | set(core_b) if core_a.get(k) != core_b.get(k))
    # The footprint candidate is on the main35 line: native-lib.cpp only adds PR #27's initialization-warning
    # log callback (no rendering change; main35 vs main29 selected frames of these six presets are byte-identical,
    # precision-controls-v2/historical-mrt25-vs-current36.json). Nothing else may differ.
    assert differing == ([] if name == 'raw-point' else ['native-lib.cpp']), differing
artifact_proofs['core_source_exception'] = 'footprint native-lib.cpp differs from baseline29 only by the PR #27 initialization-warning log callback'
runner.atomic(WORK / 'artifact-proof.json', artifact_proofs)
signals = WORK / 'signals'
signals.mkdir(exist_ok=True)
pcm = {}
for frames in [240, 480]:
    origin = ROOT / f'build/native-4k-current-main/targeted-matrix/signals/pcm-{frames}.u8'
    target = signals / origin.name
    if not target.exists():
        shutil.copyfile(origin, target)
    assert runner.file_hash(target) == runner.file_hash(origin) and target.stat().st_size == frames * 1470
    pcm[str(frames)] = {'path': str(target), 'sha256': runner.file_hash(target), 'bytes': target.stat().st_size}
    assert pcm[str(frames)]['sha256'] == {240: '38a09d906e93452d4af5ebea36fcdc684a8383eacbd162d2d61b4ed3fbd2674c',
                                          480: '14a59e75249dee0dd15d74487688c248c6a4a4b24a843b6d6f612ccc5c408dbc'}[frames]
base = {'backend': 'actual ProjectM TV core production JNI/GLES3', 'device_serial': SERIAL,
        'roles': {k: roles[k] for k in ['reference', 'footprint']},
        'comparator_roles_read_only': {k: roles[k] for k in ['raw-point']}, 'pcm': pcm, 'provider_sha256': runner.file_hash(PROVIDER),
        'adapter_sha256': runner.file_hash(Path(__file__)), 'ownership': ownership,
        'presets': records, 'capture_frames': PICKS,
        'reference': 'baseline29 actual core with intentional lineReference0x0 at1182x665; retained raw-point-controls rows',
        'hypothesis': 'Per-read reference footprint brings Royal191, Fed quadratrail and astral nz+ closer to classic29 ref0 than the merged uniform product (raw-point rows) without regressing Mandelverse, Royal255 or Acid Mandala',
        'retention': '8 native RGB8 frames, all480 simulated frames, full1470 audio bytes/frame, fresh process each repeat',
        'limits': 'Six difficult presets, one signal/seed/AppleM4Pro emulator; not full corpus, TV or performance acceptance'}
protocols = {}
for label, size in [(k, v) for k, v in PROFILES.items() if k != 'classic']:
    protocol = dict(base, profile=label, config={'width': size[0], 'height': size[1], 'fps': 30,
                                               'warmup_frames': 120, 'measurement_frames': 360})
    protocol['sha256'] = runner.digest(protocol)
    path = WORK / label / 'protocol.json'
    if path.exists():
        assert json.loads(path.read_text()) == protocol, 'Immutable protocol changed; use a new WORK'
    else:
        runner.atomic(path, protocol)
    protocols[label] = protocol
original_job = runner.make_job


def make_job(protocol, *args):
    job = original_job(protocol, *args)
    job.update(width=protocol['config']['width'], height=protocol['config']['height'], capture_frames=PICKS)
    return job


runner.make_job = make_job
original_validate = runner.validate_result


def validate_result(job, result, frames, directory):
    status = original_validate(job, result, frames, directory)
    if status == 'success':
        role = next(r for r in roles.values() if r['core_sha256'] == job['expected_core_sha256'])
        assert result['backend_identity'] == role['backend_identity']
        assert result['pcm_samples_per_frame'] == 1470 and result['pcm_uint8_sha256'] == job['pcm_uint8_sha256']
        assert result['gl_renderer'] == DRIVER, result['gl_renderer']
    return status


runner.validate_result = validate_result
comparator_analysis = json.loads((COMPARATOR / 'analysis.json').read_text())
assert comparator_analysis['state'] == 'complete'
comparator_rows = {}
for case in comparator_analysis['cases']:
    preset = case['preset']['path']
    for role in ['p1', 'raw-point']:
        info = case['roles'][role]
        assert info['status'] == 'success'
        for path, digest in zip(info['row_paths'], info['row_sha256']):
            assert runner.file_hash(Path(path)) == digest, path
        comparator_rows[(role, case['profile'], preset)] = [Path(p) for p in info['row_paths']]
    for path, digest in zip(case['reference']['row_paths'], case['reference']['row_sha256']):
        assert runner.file_hash(Path(path)) == digest, path
    comparator_rows[('reference', 'classic', preset)] = [Path(p) for p in case['reference']['row_paths']]
raw_identity = roles['raw-point']['backend_identity']
for (role, label, preset), paths in comparator_rows.items():
    if role == 'raw-point':
        for path in paths:
            assert json.loads(path.read_text())['result']['backend_identity'] == raw_identity
runner.atomic(WORK / 'comparator-index.json', {'source': str(COMPARATOR / 'analysis.json'),
              'source_sha256': runner.file_hash(COMPARATOR / 'analysis.json'),
              'rows': [{'role': r, 'profile': l, 'preset': p, 'row_paths': [str(x) for x in v],
                        'row_sha256': [runner.file_hash(x) for x in v]} for (r, l, p), v in comparator_rows.items()]})


def slot_path(role, label, record, repeat):
    if role != 'footprint':
        return comparator_rows[(role, label, record['path'])][repeat - 1]
    key = runner.job_key(protocols[label]['sha256'], record, role, 'selected', repeat, 360)
    return WORK / label / 'jobs' / key / 'row.json'


def progress(state):
    rows = []
    for record in records:
        for label in ['1330', '2160']:
            for repeat in [1, 2]:
                path = slot_path('footprint', label, record, repeat)
                if path.exists():
                    row = json.loads(path.read_text())
                    rows.append({'role': 'footprint', 'profile': label, 'preset': record['path'], 'repeat': repeat,
                                 'status': row['status'], 'error': row.get('error'), 'path': str(path),
                                 'row_sha256': runner.file_hash(path)})
    counts = collections.Counter(r['status'] for r in rows)
    value = {'state': state, 'planned_new_jobs': 24, 'terminal_slots': len(rows), 'status_counts': dict(counts),
             'free_GiB': shutil.disk_usage(WORK).free / 2**30, 'updated_unix_seconds': time.time(), 'rows': rows}
    runner.atomic(WORK / 'progress.json', value)
    return value


def samples(path):
    row = json.loads(path.read_text())
    result = row['result']
    frames = {}
    metrics = {}
    for sample in result['selected_files']:
        raw = np.fromfile(path.parent / 'output' / sample['path'], dtype=np.uint8).reshape(result['height'], result['width'], 3)
        small = cv2.resize(raw, (1182, 665), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        frames[sample['frame']] = small
        mx, mn = small.max(axis=2), small.min(axis=2)
        h, w = raw.shape[:2]
        centre = raw[int(h*.45):int(h*.55), int(w*.45):int(w*.55)]
        luminance = small @ LUMA
        metrics[sample['frame']] = {'luma': sample['metrics']['native_luma_mean'],
                                   'centre_rgb': (centre.reshape(-1, 3).mean(axis=0)/255).tolist(),
                                   'saturation': float(((mx-mn)/np.maximum(mx, 1/255)).mean()),
                                   'contrast_luma_std_1182': float(luminance.std()),
                                   'laplacian_luma_var_1182': float(cv2.Laplacian(luminance, cv2.CV_32F).var())}
    return frames, metrics


def pair(role, label, record):
    paths = [slot_path(role, label, record, repeat) for repeat in [1, 2]]
    rows = [json.loads(p.read_text()) for p in paths]
    success = all(r['status'] == 'success' for r in rows)
    exact = success and rows[0]['selected_native_sha256'] == rows[1]['selected_native_sha256']
    fresh = success and rows[0]['result']['pid'] != rows[1]['result']['pid']
    return paths, rows, 'success' if exact and fresh else 'repeat_unstable' if success else 'failed'


def frame_files(path):
    result = json.loads(path.read_text())['result']
    return {s['frame']: path.parent / 'output' / s['path'] for s in result['selected_files']}


def analyze():
    cases = []
    for record in records:
        rpaths, rrows, rstatus = pair('reference', 'classic', record)
        assert rstatus == 'success'
        rf, rm = samples(rpaths[0])
        for label in ['1330', '2160']:
            case = {'preset': record, 'profile': label, 'roles': {}}
            arrays = {}
            for role in ['p1', 'raw-point', 'footprint']:
                paths, rows, status = pair(role, label, record)
                info = {'status': status, 'row_paths': [str(p) for p in paths], 'row_sha256': [runner.file_hash(p) for p in paths]}
                case['roles'][role] = info
                if status != 'success':
                    continue
                frames, mm = samples(paths[0])
                arrays[role] = frames
                info['fresh_process_pids'] = [r['result']['pid'] for r in rows]
                info['repeat_exact_selected'] = True
                info['windows'] = {}
                for window, picks in [('4', PICKS[:5]), ('12', PICKS)]:
                    summary = {k: np.mean([mm[f][k] for f in picks], axis=0).tolist() for k in mm[picks[0]]}
                    ref = {k: np.mean([rm[f][k] for f in picks], axis=0).tolist() for k in rm[picks[0]]}
                    info['windows'][window] = {'summary': summary, 'errors': {
                        'image_mae_1182_rgb01': float(np.mean([np.abs(frames[f]-rf[f]).mean() for f in picks])),
                        'luma_ratio': summary['luma']/ref['luma'] if ref['luma'] > 0 else None,
                        'luma_absolute_error': float(np.mean([abs(mm[f]['luma']-rm[f]['luma']) for f in picks]))}}
            fix, raw = case['roles']['footprint'], case['roles']['raw-point']
            if fix['status'] == 'success' and raw['status'] == 'success':
                ff, rawf = frame_files(Path(fix['row_paths'][0])), frame_files(Path(raw['row_paths'][0]))
                exact = {str(f): runner.file_hash(ff[f]) == runner.file_hash(rawf[f]) for f in PICKS}
                case['footprint_vs_raw_point'] = {
                    'selected_frames_byte_identical': exact, 'identical_count': sum(exact.values()), 'frames': len(PICKS),
                    'selected_native_sha256_equal': json.loads(Path(fix['row_paths'][0]).read_text())['selected_native_sha256'] ==
                                                    json.loads(Path(raw['row_paths'][0]).read_text())['selected_native_sha256'],
                    'image_mae_1182_footprint_vs_rawpoint': float(np.mean([np.abs(arrays['footprint'][f]-arrays['raw-point'][f]).mean() for f in PICKS])),
                    'max_abs_native_byte_difference': int(max(np.abs(np.fromfile(ff[f], np.uint8).astype(np.int16) -
                                                                     np.fromfile(rawf[f], np.uint8).astype(np.int16)).max() for f in PICKS))}
            case['status'] = 'success' if all(v['status'] == 'success' for v in case['roles'].values()) else 'incomplete_or_failed'
            cases.append(case)
    runner.atomic(WORK / 'analysis.json', {'state': 'complete', 'cases': cases, 'definitions': base,
                   'status_counts': dict(collections.Counter(c['status'] for c in cases))})


runner.atomic(WORK / 'lease.json', {'state': 'active', 'pid': os.getpid(), 'ownership': ownership,
                                  'adapter_sha256': base['adapter_sha256'], 'started_unix_seconds': time.time()})
try:
    progress('running')
    pending = [(record, label, repeat) for record in records for label in ['1330', '2160'] for repeat in [1, 2]
               if not slot_path('footprint', label, record, repeat).exists()]
    if pending:
        runner.install_role(SERIAL, roles['footprint'], WORK)
    for record, label, repeat in pending:
        free = shutil.disk_usage(WORK).free
        if free < 6*2**30:
            progress('disk_guard_stopped')
            raise RuntimeError(f'Disk guard needs6GiB; free={free/2**30:.3f}')
        guard(SERIAL)
        row = runner.run_one(type('Args', (), {'work': WORK / label, 'timeout': 300})(),
                             protocols[label], record, 'footprint', 'selected', repeat, 360, native=True)
        progress('running')
        if row['status'] != 'success':
            with (WORK / 'failure-log.jsonl').open('a') as stream:
                stream.write(runner.canonical({'role': 'footprint', 'profile': label, 'preset': record,
                              'repeat': repeat, 'status': row['status'], 'error': row.get('error')})+'\n')
    analyze()
    report = progress('complete')
    assert report['terminal_slots'] == 24
    manifest = {str(p.relative_to(WORK)): {'bytes': p.stat().st_size, 'sha256': runner.file_hash(p)}
                for p in sorted(WORK.rglob('*')) if p.is_file() and 'worker' not in p.relative_to(WORK).parts[:1]
                and p.name not in ['host.lock', 'screen.log', 'source-results-manifest.json', 'lease.json']}
    runner.atomic(WORK / 'source-results-manifest.json', {'files': manifest, 'sha256': runner.digest(manifest),
                   'provider_sha256': base['provider_sha256'], 'adapter_sha256': base['adapter_sha256']})
    print('FOOTPRINT_COMPLETE '+runner.canonical({k:v for k,v in report.items() if k != 'rows'}), flush=True)
except Exception:
    with (WORK / 'failure-log.txt').open('a') as stream:
        stream.write(traceback.format_exc())
    progress('failed')
    raise
finally:
    runner.atomic(WORK / 'lease.json', {'state': 'released', 'pid': os.getpid(), 'ownership': ownership,
                                      'finished_unix_seconds': time.time(), 'emulator_shutdown': False})
