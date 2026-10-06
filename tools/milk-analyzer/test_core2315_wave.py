"""Data-only waveform controls against the identified 49-patch CPU adapter."""
import json
import os
from pathlib import Path
import subprocess

import numpy as np
import pytest

from test_native_wave import frame


@pytest.fixture
def binary():
    folder = Path(os.environ.get('MILK_TEST_2315_BINARIES',
        Path(__file__).resolve().parents[2]/'build/visual-loop/source49/adapters'))
    executable = folder/'milk-wave-inputs'
    if not executable.is_file():
        pytest.skip('prepared published2.3.15 source waveform adapter required')
    return executable


def execute(binary, tmp_path, frames, **options):
    output = tmp_path/'geometry.json'; request = tmp_path/'request.json'
    request.write_text(json.dumps({'mode': 6, 'mode_policy': 'evaluated-live-v1',
        'width': 128, 'height': 72, 'output': str(output), 'frames': frames, **options}))
    process = subprocess.run([str(binary), str(request)], text=True, capture_output=True)
    assert process.returncode == 0, process.stderr
    result = json.loads(output.read_text())
    assert result['engine_identity']['patches_sha256'] == '7ef297fcab5d42d0531ec621ac6a464a5a0e7982da02bb40996bc62a886ae527'
    return result


def test_live_mode_uses_truncation_signed_remainder_and_omission(binary, tmp_path):
    result = execute(binary, tmp_path, [frame(time=1, wave_mode=mode) for mode in [-1.2, 2**31, 22.75, -16]])
    assert [row['omitted'] for row in result['frames']] == [True, True, False, False]
    assert [row['mode'] for row in result['frames']] == [None, None, 6, 0]
    assert len(result['frames'][2]['vertex_waves'][0]) == 159


def test_mode_change_recreates_wave_math_instead_of_reusing_old_smoothing(binary, tmp_path):
    first = frame(time=1, wave_mode=2, waveform_left=[128]*480, waveform_right=[128]*480)
    middle = frame(time=2, wave_mode=6)
    last = frame(time=3, wave_mode=2)
    changed = execute(binary, tmp_path, [first, middle, last])
    fresh = execute(binary, tmp_path, [last])
    assert [row['mode'] for row in changed['frames']] == [2, 6, 2]
    assert changed['frames'][2]['vertex_waves'] == fresh['frames'][0]['vertex_waves']


def test_source_wrapper_uses_live_mode_dots_thickness_and_additive(binary, tmp_path):
    from forecast import read_source
    from scene_equations import execute_scene
    from builtin_wave import source_builtin_wave
    from test_builtin_wave import audio
    from test_scene_equations import frames
    preset = tmp_path/'live-controls.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nnWaveMode=9\n'
        'per_frame_1=wave_mode=6+frame-1;wave_usedots=equal(frame,2);wave_thick=below(frame,2);wave_additive=-1;\n')
    source = read_source(preset, reader=binary.parent/'milk-native-reader')
    inputs = frames()
    inputs.append({**inputs[0], 'time': .1, 'frame': 3})
    scene = execute_scene(source, inputs, reader=binary.parent/'milk-native-reader', width=128, height=72)
    result = source_builtin_wave(source, scene, audio(inputs), binary=binary,
        line_rendering_profile='projectmtv-gles-quad-lines-v1')
    assert [row['mode'] for row in result['frames']] == [6, 7, 8]
    assert [row['draw_mode'] for row in result['frames']] == ['strip', 'points', 'strip']
    assert [len(row['copy_offsets']) for row in result['frames']] == [4, 1, 1]
    assert all(row['additive'] for row in result['frames'])


def test_source49_forecast_threads_signed_zoom_and_live_legacy_filters(binary, tmp_path):
    from forecast import read_source, forecast_source
    from test_forecast import domain
    from test_native_audio import NativeAudioTest
    import test_native_audio
    preset = tmp_path/'live-display.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=111\n[preset00]\nwarp=0\nfWaveAlpha=0\n'
        'fDecay=1\nfGammaAdj=2\nper_frame_1=zoom=-1;zoomexp=1;gamma=1;invert=1;\n')
    source = read_source(preset, reader=binary.parent/'milk-native-reader')
    old_binary = test_native_audio.BINARY
    try:
        test_native_audio.BINARY = binary.parent/'milk-audio-inputs'
        process, audio = NativeAudioTest().run_audio(np.zeros(2*1470), frames=2)
    finally:
        test_native_audio.BINARY = old_binary
    assert process.returncode == 0, process.stderr
    result = forecast_source(source, audio=audio, binaries=binary.parent, domain=domain(), compatibility={})
    assert result['status'] == 'computed'
    assert result['stage_resolution']['composite']['kind'] == 'legacy_composite'
    assert result['provenance']['warp_zoom_policy'] == 'projectmtv-core-2.3.15-signed-unit-zoom-v1'
    assert result['provenance']['legacy_control_policy'] == 'projectmtv-core-2.3.15-live-display-controls-v1'
    assert np.mean(result['frames'][0]['display'][..., :3]) > .5


@pytest.mark.parametrize('variable', ['wave_mode', 'echo_orient', 'blur1_min'])
def test_reader_ieee_tags_follow_only_native_defined_control_fallbacks(binary, tmp_path, variable):
    from forecast import read_source
    from scene_equations import execute_scene
    from test_scene_equations import frames
    from test_builtin_wave import audio
    from builtin_wave import source_builtin_wave
    from legacy_composite import legacy_display
    from blur import native_ranges
    preset = tmp_path/'ieee-controls.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=111\n[preset00]\n'
                     f'per_frame_1={variable}=exp(1000);echo_alpha=1;gamma=1;\n')
    source = read_source(preset, reader=binary.parent/'milk-native-reader')
    inputs = frames()[:1]
    scene = execute_scene(source, inputs, reader=binary.parent/'milk-native-reader', width=32, height=32)
    main = scene['frames'][0]['main']
    assert main[variable] == {'ieee': 'positive_infinity'}
    if variable == 'wave_mode':
        result = source_builtin_wave(source, scene, audio(inputs), binary=binary)
        assert result['frames'][0]['omitted'] is True
    elif variable == 'echo_orient':
        field = np.full((8,8,4), .1, dtype=np.float32)
        result = legacy_display(field, values={}, main=main, control_policy='projectmtv-core-2.3.15-live-display-controls-v1',
            time=0, hue_offsets=[0]*4, quantize=False)
        expected = legacy_display(field, values={'fGammaAdj': '1'}, time=0, hue_offsets=[0]*4, quantize=False)
        np.testing.assert_array_equal(result, expected)
    else:
        low, high = native_ranges([main['blur1_min'], 0, 0], [1]*3, policy='projectmtv-core-2.3.15-blur-ranges-v1')
        np.testing.assert_array_equal(low, [0]*3); np.testing.assert_array_equal(high, [1]*3)


@pytest.mark.parametrize('variable', ['wave_x', 'wave_additive', 'wave_usedots'])
def test_omitted_wave_does_not_consume_unused_geometry_or_flags(binary, tmp_path, variable):
    from forecast import read_source
    from scene_equations import execute_scene
    from test_scene_equations import frames
    from test_builtin_wave import audio
    from builtin_wave import source_builtin_wave
    preset = tmp_path/'omitted-wave.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\n'
                     f'per_frame_1=wave_mode=2147483648;{variable}=exp(1000);\n')
    source = read_source(preset, reader=binary.parent/'milk-native-reader')
    inputs = frames()[:1]
    scene = execute_scene(source, inputs, reader=binary.parent/'milk-native-reader', width=32, height=32)
    result = source_builtin_wave(source, scene, audio(inputs), binary=binary)
    assert result['frames'][0]['omitted'] is True
    assert result['frames'][0]['positions'] == []


@pytest.mark.parametrize('expression,expected', [('exp(1000)', [8,1000]),
                                                ('-exp(1000)', [0,.001]),
                                                ('exp(1000)-exp(1000)', [8,1000])])
def test_native_per_frame_clamps_apply_to_explicit_ieee_exports(binary, tmp_path, expression, expected):
    from forecast import read_source
    from scene_equations import execute_scene
    from test_scene_equations import frames
    preset = tmp_path/'clamps.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=111\n[preset00]\n'
                     f'per_frame_1=gamma={expression};echo_zoom={expression};\n')
    source = read_source(preset, reader=binary.parent/'milk-native-reader')
    result = execute_scene(source, frames()[:1], reader=binary.parent/'milk-native-reader')['frames'][0]['main']
    assert [result['gamma'],result['echo_zoom']] == expected


def test_live_nonzero_wave_flags_accept_reader_ieee_tags(binary, tmp_path):
    from forecast import read_source
    from scene_equations import execute_scene
    from test_scene_equations import frames
    from test_builtin_wave import audio
    from builtin_wave import source_builtin_wave
    preset = tmp_path/'nonzero-wave.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nnWaveMode=6\n'
        'per_frame_1=wave_usedots=exp(1000);wave_additive=exp(1000)-exp(1000);\n')
    source = read_source(preset, reader=binary.parent/'milk-native-reader')
    inputs = frames()[:1]
    scene = execute_scene(source, inputs, reader=binary.parent/'milk-native-reader', width=32, height=32)
    result = source_builtin_wave(source,scene,audio(inputs),binary=binary)
    assert result['frames'][0]['draw_mode'] == 'points'
    assert result['frames'][0]['additive'] is True
