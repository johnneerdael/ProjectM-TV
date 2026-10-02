import numpy as np
import pytest
from pathlib import Path
import os
import json

from preset_lab.bass_screen import measure_preset_bass, pixel_response, summarize_response
from preset_lab.identity import file_digest
from preset_lab.models import EngineIdentity, PresetRecord, RunConfig, WorkerResult


def test_same_animation_has_zero_bass_response():
    rng = np.random.default_rng(8)
    for _ in range(4):
        frame = rng.integers(0, 256, (10, 10, 3), dtype=np.uint8)
        assert pixel_response(frame, frame)['magnitude'] == 0
        assert pixel_response(frame, frame)['affected_area'] == 0


def test_large_scene_response_beats_small_element_with_same_intensity():
    control = np.zeros((10, 10, 3), dtype=np.uint8)
    tiny = control.copy()
    tiny[0, 0] = 128
    whole = np.full_like(control, 128)
    a, b = pixel_response(tiny, control), pixel_response(whole, control)
    assert a['affected_area'] == pytest.approx(.01)
    assert b['affected_area'] == 1
    assert b['magnitude'] == pytest.approx(a['magnitude'] * 100)
    assert a['local_intensity'] == pytest.approx(b['local_intensity'])


def test_intensity_and_geometry_changes_are_measured_without_code_heuristics():
    control = np.zeros((10, 10, 3), dtype=np.uint8)
    small = np.full_like(control, 20)
    large = np.full_like(control, 160)
    assert pixel_response(large, control)['magnitude'] == pytest.approx(8 * pixel_response(small, control)['magnitude'])
    moved = control.copy()
    control[0, 0] = 255
    moved[0, 1] = 255
    assert pixel_response(moved, control)['affected_area'] == pytest.approx(.02)


def test_shape_or_type_mismatch_is_not_silently_scored():
    a = np.zeros((10, 10, 3), dtype=np.uint8)
    with pytest.raises(ValueError):
        pixel_response(a, a[:2])
    with pytest.raises(ValueError):
        pixel_response(a.astype(float), a)


def test_summary_reports_delay_and_screen_amount_with_known_signal():
    trajectory = [dict(magnitude=0., affected_area=0., local_intensity=0.) for _ in range(60)]
    for i in range(6, 15):
        trajectory[i] = dict(magnitude=.2, affected_area=.5, local_intensity=.4)
    result = summarize_response(trajectory, fps=30)
    assert result['first_response_seconds'] == pytest.approx(.2)
    assert result['peak_magnitude'] == pytest.approx(.2)
    assert result['area_at_peak'] == pytest.approx(.5)
    assert result['mean_magnitude'] == pytest.approx(.03)


def test_no_response_has_zero_amount_and_no_latency():
    result = summarize_response([dict(magnitude=0., affected_area=0., local_intensity=0.)] * 60, 30)
    assert result['first_response_seconds'] is None
    assert result['peak_magnitude'] == 0


def fake_scene(tmp_path, monkeypatch, non_repeatable=False, prefix_drift=False):
    root = tmp_path / 'core/src/main/assets'
    (root / 'presets').mkdir(parents=True)
    (root / 'textures').mkdir()
    preset = root / 'presets/scene.milk'
    preset.write_text('[preset00]\nper_frame_1=zoom=bass;\n')
    worker = tmp_path / 'worker'
    worker.write_text('worker-v1')
    launches = []
    def render(worker, job, observe, timeout):
        launches.append(job.stimulus_id)
        cfg = job.config
        count = round((cfg.warmup_seconds + cfg.measurement_seconds) * cfg.fps)
        warmup = round(cfg.warmup_seconds * cfg.fps)
        for i in range(count):
            level = round(float(job.stimulus_id.split('-')[1]) * 255) if job.stimulus_id.startswith('bass-') else 0
            if job.stimulus_id == 'repeat' and non_repeatable:
                level = 50
            elif i < warmup and not prefix_drift:
                level = 0
            observe(np.full((cfg.height, cfg.width, 3), level, dtype=np.uint8))
        log = tmp_path / 'stderr.log'
        log.write_text('')
        return WorkerResult('success', {}, log)
    monkeypatch.setattr('preset_lab.bass_screen.render_job', render)
    cfg = RunConfig(width=10, height=10, warmup_seconds=.1, measurement_seconds=1)
    record = PresetRecord(preset.name, file_digest(preset), 0)
    identity = EngineIdentity('a'*40, 'b'*64, 'c'*64)
    def run():
        return measure_preset_bass(record, tmp_path, tmp_path/'work', worker, identity, cfg)
    return run, launches, root, worker


def test_automatic_measurement_cache_reuses_without_rendering_and_invalidates_assets(tmp_path, monkeypatch):
    run, launches, assets, worker = fake_scene(tmp_path, monkeypatch)
    measured = run()
    assert measured['status'] == 'success'
    assert len(launches) == 5
    assert measured['score'] == pytest.approx(np.mean([13, 38, 76])/255)
    assert run()['reused'] and run()['render_jobs'] == 0
    assert len(launches) == 5
    (assets / 'textures/new.png').write_bytes(b'new')
    assert not run()['reused']
    assert len(launches) == 10
    worker.write_text('worker-v2')
    assert not run()['reused']
    assert len(launches) == 15


@pytest.mark.parametrize('failure', ['non_repeatable', 'prefix_drift'])
def test_uncontrolled_divergence_is_unknown_not_high_response(tmp_path, monkeypatch, failure):
    run, launches, _, _ = fake_scene(tmp_path, monkeypatch, **{failure: True})
    result = run()
    assert result['status'] == 'unknown'
    assert result['score'] is None
    assert result['reasons']


@pytest.mark.native
def test_real_engine_distinguishes_time_animation_from_full_screen_bass_shader(tmp_path):
    binary = os.environ.get('PRESET_LAB_WORKER')
    if not binary:
        pytest.skip('set PRESET_LAB_WORKER for actual shader execution')
    worker = Path(binary)
    identity = EngineIdentity(**json.loads((worker.parent / 'build-identity.json').read_text()))
    assets = tmp_path / 'core/src/main/assets'
    (assets/'presets').mkdir(parents=True)
    (assets/'textures').mkdir()
    config = RunConfig(width=64, height=36, measurement_seconds=2)
    results = {}
    for name, expression in [('time', '.2+.1*sin(time)'), ('bass', '.05*bass')]:
        preset = assets/'presets'/f'{name}.milk'
        preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nfWaveAlpha=0\nPSVERSION_COMP=2\n'
                          'comp_1=`shader_body\ncomp_2=`{\n'
                          f'comp_3=`ret=float3({expression},0,0);\ncomp_4=`}}\n')
        record = PresetRecord(preset.name, file_digest(preset), 0)
        result = measure_preset_bass(record, tmp_path, tmp_path/'work', worker, identity, config)
        assert result['status'] == 'success', result
        results[name] = result
    assert results['time']['score'] == 0
    assert results['bass']['score'] > .001
