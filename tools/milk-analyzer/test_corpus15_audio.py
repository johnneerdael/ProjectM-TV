"""Declared 15 Hz offline input; never a 30 Hz cold-JNI qualification label."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[2]
ENGINE29 = {
    'commit': '6f64807467e312034883a4389e6aa80a675458bc',
    'patches_sha256': '01d259c40d364f8d55b9ee43ab29dcf39fd85f107908969c23671b3cea064457',
}


@pytest.fixture
def adapters():
    folder = Path(os.environ.get('MILK_TEST_CORPUS15_BINARIES',
                               ROOT / 'build/preset-corpus/source29/adapters'))
    if not (folder / 'milk-audio-inputs').is_file():
        pytest.skip('prepared source29 adapters required')
    return folder


def run_audio(folder, tmp_path, samples, *, fps=15, frames=60, **options):
    pcm = tmp_path / 'samples.f32'
    np.asarray(samples, dtype='<f4').tofile(pcm)
    output = tmp_path / 'audio.json'
    output.unlink(missing_ok=True)
    request = dict(pcm_path=str(pcm), output=str(output), fps=fps, frames=frames,
                   channels=1, clock_policy='ideal-frame-fractions-v1',
                   preset_progress_policy='explicit-zero-placeholder-v1')
    request.update(options)
    path = tmp_path / 'request.json'
    path.write_text(json.dumps(request))
    result = subprocess.run([str(folder / 'milk-audio-inputs'), str(path)],
                            capture_output=True, text=True)
    return result, json.loads(output.read_text()) if output.exists() else None


def test_15hz_complete_60_frame_schedule_and_native_array_sizes(adapters, tmp_path):
    samples = np.zeros(60 * 2940)
    result, report = run_audio(adapters, tmp_path, samples)
    assert result.returncode == 0, result.stderr
    assert report['sample_rate'] == 44100
    assert report['pcm_sha256'] == hashlib.sha256(samples.astype('<f4').tobytes()).hexdigest()
    assert report['engine_identity'] == ENGINE29
    assert report['preset_progress_policy'] == 'explicit-zero-placeholder-v1'
    assert 'preset_timing' not in report
    assert len(report['frames']) == 60
    for index, frame in enumerate(report['frames']):
        assert frame['time'] == (index + 1) / 15
        assert frame['fps'] == 15
        assert frame['progress'] == 0
        assert len(frame['waveform_left']) == 480
        assert len(frame['spectrum_left']) == 512
    assert report['frames'][-1]['time'] == 4


def test_15hz_uses_last_native_576_samples_and_real_decay_dt(adapters, tmp_path):
    # The entire 2940-sample block is consumed, but native FrameBuffer clips its
    # analysis to the last AudioBufferSamples=576. A loud discarded prefix must
    # therefore have no effect on the exported waveform or spectrum.
    tail = .2 * np.sin(2 * np.pi * 80 * np.arange(576) / 44100)
    quiet = np.concatenate([np.zeros(2940 - 576), tail])
    loud = np.concatenate([np.full(2940 - 576, .9), tail])
    result, report = run_audio(adapters, tmp_path, quiet, frames=1)
    assert result.returncode == 0, result.stderr
    result, clipped = run_audio(adapters, tmp_path, loud, frames=1)
    assert result.returncode == 0, result.stderr
    assert report['frames'] == clipped['frames']
    first = report['frames'][0]
    assert max(np.abs(first['waveform_left'])) > 0
    assert max(first['spectrum_left']) > 0
    # First nonzero band: current/longAverage, and average/longAverage.
    # Native Loudness adjusts the 30 Hz rates by actual elapsed seconds.
    assert first['bass'] == pytest.approx(1 / (1 - .9**2), rel=2e-6)
    assert first['bass_att'] == pytest.approx((1 - .2**2) / (1 - .9**2), rel=2e-6)
    block30 = np.concatenate([np.zeros(1470 - 576), tail])
    result, at30 = run_audio(adapters, tmp_path, block30, fps=30, frames=1)
    assert result.returncode == 0, result.stderr
    assert first['spectrum_left'] == at30['frames'][0]['spectrum_left']
    assert first['bass_att'] != at30['frames'][0]['bass_att']
    result, falling = run_audio(adapters, tmp_path,
                               np.concatenate([quiet, np.zeros(2940)]), frames=2)
    assert result.returncode == 0, result.stderr
    assert falling['frames'][1]['bass'] == 0
    # Falling short and long averages use .5 and .9 at 30 Hz; at 15 Hz
    # each rate is squared, including the actual state update after silence.
    assert falling['frames'][1]['bass_att'] == pytest.approx(
        first['bass_att'] * .5**2 / .9**2, rel=2e-6)


@pytest.mark.parametrize('fps', [30, 60])
def test_existing_general_cadences_keep_their_schedule(adapters, tmp_path, fps):
    result, report = run_audio(adapters, tmp_path, np.zeros(2 * (44100 // fps)),
                               fps=fps, frames=2)
    assert result.returncode == 0, result.stderr
    assert [f['time'] for f in report['frames']] == [1 / fps, 2 / fps]
    assert [f['fps'] for f in report['frames']] == [fps, fps]


@pytest.mark.parametrize('size', [60 * 2940 - 1, 60 * 2940 + 1, 60 * 1470])
def test_15hz_rejects_truncated_or_wrong_cadence_pcm(adapters, tmp_path, size):
    result, report = run_audio(adapters, tmp_path, np.zeros(size))
    assert result.returncode != 0
    assert 'PCM length does not match complete frames' in result.stderr
    assert report is None


@pytest.mark.parametrize('label', ['2.3.16', '2.3.17', '2.3.21', '2.3.22',
                                   '2.3.25', '2.3.27', '2.3.29'])
@pytest.mark.parametrize('clock', ['ideal-frame-fractions-v1',
                                  'projectmtv-jni-rounded-nanoseconds30-v1'])
def test_15hz_never_relabels_as_cold_jni(adapters, tmp_path, label, clock):
    result, report = run_audio(adapters, tmp_path, np.zeros(60 * 2940),
        clock_policy=clock,
        preset_progress_policy=f'projectmtv-core-{label}-cold-jni-v1', entropy_seed=12345)
    assert result.returncode != 0
    assert report is None


@pytest.mark.parametrize('binary', ['milk-wave-inputs', 'milk-noise-inputs'])
def test_source29_wave_and_noise_admission_stays_exact(adapters, tmp_path, binary):
    from test_native_wave import frame
    requests = {
        'milk-wave-inputs': dict(mode=1, mode_policy='evaluated-live-v1', width=854,
            height=480, output=str(tmp_path / 'wave.json'), frames=[frame(time=1/15,
            wave_mode=1, wave_x=.5, wave_y=.5, wave_mystery=0, wave_a=.5, vol=1)]),
        'milk-noise-inputs': dict(names=['noise_lq_lite'], seed=3567620661,
            seed_policy='production-clock-seed-v1', output=str(tmp_path / 'noise')),
    }
    request = requests[binary]
    path = tmp_path / 'request.json'
    path.write_text(json.dumps(request))
    result = subprocess.run([str(adapters / binary), str(path)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report_path = Path(request['output'])
    if binary == 'milk-noise-inputs':
        report_path /= 'manifest.json'
    assert json.loads(report_path.read_text())['engine_identity'] == ENGINE29


def test_source29_cold_label_keeps_30hz_and_30_frame_limit(adapters, tmp_path):
    options = dict(clock_policy='projectmtv-jni-rounded-nanoseconds30-v1',
                   preset_progress_policy='projectmtv-core-2.3.29-cold-jni-v1',
                   entropy_seed=12345)
    result, report = run_audio(adapters, tmp_path, np.zeros(2 * 1470),
                               fps=30, frames=2, **options)
    if 'qualified libcxx-200100' in result.stderr:
        pytest.skip('cold duration sampling requires qualified libcxx')
    assert result.returncode == 0, result.stderr
    assert report['engine_identity'] == ENGINE29
    assert report['frames'][0]['fps'] == 35
    assert report['preset_timing']['physical_fps'] == 30
    result, rejected = run_audio(adapters, tmp_path, np.zeros(31 * 1470),
                                  fps=30, frames=31, **options)
    assert result.returncode != 0
    assert '<=30 frames' in result.stderr
    assert rejected is None
    options['preset_progress_policy'] = 'projectmtv-core-2.3.27-cold-jni-v1'
    result, rejected = run_audio(adapters, tmp_path, np.zeros(2 * 1470),
                                  fps=30, frames=2, **options)
    assert result.returncode != 0
    assert 'pinned 2.3.27' in result.stderr
    assert rejected is None
