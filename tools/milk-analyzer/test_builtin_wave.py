import unittest
from pathlib import Path
import numpy as np
import pytest
from test_shader_components import lower
from test_scene_equations import native,frames
from scene_equations import execute_scene
from test_native_reader import READER
from test_native_wave import frame,BINARY
from engine_profiles import LEGACY_WAVE

# Pair the waveform binary with the reader rather than the old canonical build.
BINARY=READER.parent/'milk-wave-inputs'


def test_source51_builtin_dots_use_verified_unchanged_draw_contract(tmp_path):
    import os
    from forecast import read_source
    from builtin_wave import source_builtin_wave
    binaries=Path(os.environ.get('MILK_TEST_2317_BINARIES',READER.parent))
    path=tmp_path/'dots51.milk'
    path.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nnWaveMode=6\nbWaveDots=1\nfWaveAlpha=.5\n')
    source=read_source(path,reader=binaries/'milk-native-reader')
    if source['parser_inputs']['engine']['patches_sha256']!='bc80791e28e7559b81c33036c91b8163cfe611d9d9793e7d3e10f8cb4e5290c8':
        pytest.skip('Prepared51patchadapters required')
    inputs=frames()[:1]
    scene=execute_scene(source,inputs,reader=binaries/'milk-native-reader',width=256,height=144,mesh_x=8,mesh_y=8)
    result=source_builtin_wave(source,scene,audio(inputs),binary=binaries/'milk-wave-inputs',
        line_rendering_profile='projectmtv-gles-quad-lines-v1')
    assert len(result['frames'])==1


def test_wave_adapter_replacement_cannot_receive_geometry_producer_credit(tmp_path,monkeypatch):
    import shutil
    import subprocess
    from builtin_wave import source_builtin_wave
    source=native('nWaveMode=6\nfWaveAlpha=.5\n')
    inputs=frames()[:1]
    scene=execute_scene(source,inputs,reader=READER,width=32,height=32,mesh_x=8,mesh_y=8)
    binary=tmp_path/'wave-adapter';shutil.copy2(BINARY,binary)
    original=subprocess.run
    def replace(*args,**kwargs):
        result=original(*args,**kwargs)
        binary.write_bytes(b'replacement adapter did not produce this geometry')
        return result
    monkeypatch.setattr(subprocess,'run',replace)
    with pytest.raises(ValueError,match='wave.*changed'):
        source_builtin_wave(source,scene,audio(inputs),binary=binary)


def test_wave_adapter_invocation_uses_the_hashed_cwd_file_not_path(tmp_path,monkeypatch):
    import shutil
    import os
    from builtin_wave import source_builtin_wave
    source=native('nWaveMode=6\nfWaveAlpha=.5\n');inputs=frames()[:1]
    scene=execute_scene(source,inputs,reader=READER,width=32,height=32,mesh_x=8,mesh_y=8)
    local=tmp_path/'wave-adapter';shutil.copy2(BINARY,local)
    other=tmp_path/'path-bin';other.mkdir();shadow=other/'wave-adapter'
    shadow.write_text('#!/bin/sh\nexit 7\n');shadow.chmod(0o755)
    monkeypatch.chdir(tmp_path);monkeypatch.setenv('PATH',str(other)+os.pathsep+os.environ['PATH'])
    result=source_builtin_wave(source,scene,audio(inputs),binary=Path('wave-adapter'))
    assert len(result['frames'])==1


@pytest.fixture
def core235_dot_inputs(tmp_path):
    from forecast import read_source
    binaries = Path(__file__).resolve().parents[2] / 'build/visual-loop/source235/adapters'
    if not (binaries/'milk-native-reader').is_file():
        binaries = READER.parent
    # This fixture executes the separately prepared 42-patch CPU adapters.
    preset = tmp_path / 'dots.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nnWaveMode=6\nbWaveDots=1\nfWaveAlpha=.5\n')
    source = read_source(preset, reader=binaries/'milk-native-reader')
    if source['parser_inputs']['engine']['patches_sha256'] != 'd73c955a26380a502516e6ba3a18baf753851244de4de2e5a3083930766a539a':
        pytest.skip('separately prepared 42-patch CPU adapters required')
    inputs = frames()[:1]
    scene = execute_scene(source, inputs, reader=binaries/'milk-native-reader',
                          width=256, height=144, mesh_x=8, mesh_y=8)
    return source, scene, audio(inputs), binaries/'milk-wave-inputs'


def test_core235_gles_dots_use_one_two_pixel_point_without_changing_opacity(core235_dot_inputs):
    from builtin_wave import source_builtin_wave
    source, scene, data, binary = core235_dot_inputs
    legacy = source_builtin_wave(source, scene, data, binary=binary)['frames'][0]
    predicted = source_builtin_wave(source, scene, data, binary=binary,
        line_rendering_profile='projectmtv-gles-quad-lines-v1')['frames'][0]
    assert predicted['draw_mode'] == 'points'
    assert predicted['point_size'] == 2
    assert predicted['copy_offsets'] == [[0, 0]]
    assert predicted['rgba'] == legacy['rgba']  # DotStyleFor alphaScale is exactly 1 here.
    assert len(legacy['copy_offsets']) == 4
    assert legacy.get('point_size', 1) == 1


def test_core235_gles_dots_reject_unimplemented_scaled_size(core235_dot_inputs):
    from builtin_wave import source_builtin_wave
    source, scene, data, binary = core235_dot_inputs
    scene['viewport'] = [1920, 1080]
    with pytest.raises(ValueError, match='dot.*reference area'):
        source_builtin_wave(source, scene, data, binary=binary,
            line_rendering_profile='projectmtv-gles-quad-lines-v1')


def test_core235_dot_spec_draws_a_centered_two_pixel_square(core235_dot_inputs):
    from builtin_wave import source_builtin_wave
    from scene_draw import _wave
    source, scene, data, binary = core235_dot_inputs
    wave = source_builtin_wave(source, scene, data, binary=binary,
        line_rendering_profile='projectmtv-gles-quad-lines-v1')['frames'][0]
    # Subpixel position distinguishes one centered 2px dot from four shifted 1px dots.
    wave['positions'] = [[[128.25/256, 72.25/144]]]
    rendered = _wave(np.zeros((144, 256, 4), np.float32), wave,
                     builtin=True, quantize=False)
    np.testing.assert_array_equal(np.argwhere(rendered[..., 0]>0),
                                  [[71, 127], [71, 128], [72, 127], [72, 128]])


def test_core235_gles_dot_policy_refuses_a_mislabeled_41_patch_source(core235_dot_inputs):
    from builtin_wave import source_builtin_wave
    source, scene, data, binary = core235_dot_inputs
    source['parser_inputs']['engine']['patches_sha256'] = 'd21d4e3d9725178c000fd6f7ea5cd331389fb1100b70fce51341ece65d3fd818'
    with pytest.raises(ValueError, match='dot.*engine identity'):
        source_builtin_wave(source, scene, data, binary=binary,
            line_rendering_profile='projectmtv-gles-quad-lines-v1')


@pytest.fixture
def core237_dot_inputs(tmp_path):
    from forecast import read_source
    binaries=Path(__file__).resolve().parents[2]/'build/visual-loop/source237/adapters'
    if not (binaries/'milk-native-reader').is_file():binaries=READER.parent
    preset=tmp_path/'dots237.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nnWaveMode=6\nbWaveDots=1\nfWaveAlpha=.5\n')
    source=read_source(preset,reader=binaries/'milk-native-reader')
    if source['parser_inputs']['engine']['patches_sha256']!='d70f5b5ec3f3c0b4da764cb824153f142b88e17e27c2e9e71d2b481c19998c7d':
        pytest.skip('separately prepared 43-patch CPU adapters required')
    inputs=frames()[:1]
    scene=execute_scene(source,inputs,reader=binaries/'milk-native-reader',width=256,height=144,mesh_x=8,mesh_y=8)
    return source,scene,audio(inputs),binaries/'milk-wave-inputs'


def test_core237_gles_dot_math_and_true_archive_match_historical_235(core237_dot_inputs,core235_dot_inputs):
    from builtin_wave import source_builtin_wave
    source,scene,data,binary=core237_dot_inputs
    result=source_builtin_wave(source,scene,data,binary=binary,line_rendering_profile='projectmtv-gles-quad-lines-v1')
    assert result['engine_archive_sha256']=='c17fc176d6a79556dbfd6a998bbf78350f7f6d76dcd81d0bf7f6c5febd4bc578'
    assert result['engine_archive_sha256']==source['parser_inputs']['engine_archive_sha256']
    old_source,old_scene,old_data,old_binary=core235_dot_inputs
    historical=source_builtin_wave(old_source,old_scene,old_data,binary=old_binary,line_rendering_profile='projectmtv-gles-quad-lines-v1')
    assert result['frames']==historical['frames']
    assert result['frames'][0]['point_size']==2
    assert result['frames'][0]['copy_offsets']==[[0,0]]
    assert historical['engine_archive_sha256']!=result['engine_archive_sha256']


@pytest.mark.parametrize('viewport', [[1920,1080],[3840,2160],[256,1331]])
def test_core237_gles_dots_reject_unimplemented_feedback_viewports(core237_dot_inputs,viewport):
    from builtin_wave import source_builtin_wave
    source,scene,data,binary=core237_dot_inputs
    scene['viewport']=viewport
    with pytest.raises(ValueError,match='dot.*reference area'):
        source_builtin_wave(source,scene,data,binary=binary,line_rendering_profile='projectmtv-gles-quad-lines-v1')


def audio(inputs):
    return {'frames':[{**frame(),**values,'vol':1} for values in inputs]}


class BuiltinWaveTest(unittest.TestCase):
    def test_native_wave_receives_original_double_renderer_time(self):
        from builtin_wave import source_builtin_wave
        from test_native_wave import NativeWaveTest
        source=native('nWaveMode=0\nfWaveSmoothing=0\n')
        inputs=frames()[:1];inputs[0]['time']=10001.123456789
        scene=execute_scene(source,inputs,reader=READER,width=512,height=288,mesh_x=8,mesh_y=8)
        data=audio(inputs)
        predicted=source_builtin_wave(source,scene,data,binary=BINARY)['frames'][0]
        process,expected=NativeWaveTest().run_wave(0,[{**data['frames'][0],
            'wave_x':scene['frames'][0]['main']['wave_x'],'wave_y':scene['frames'][0]['main']['wave_y'],
            'wave_mystery':scene['frames'][0]['main']['wave_mystery'],'wave_a':scene['frames'][0]['main']['wave_a']}],
            wave_smoothing=0)
        self.assertEqual(process.returncode,0,process.stderr)
        points=np.asarray(expected['frames'][0]['vertex_waves'][0],dtype=np.float32)
        screen=points*np.array([.5,-.5],dtype=np.float32)+np.float32(.5)
        np.testing.assert_array_equal(predicted['positions'][0],screen)
    def test_volume_modulation_overrides_mode_opacity_factor_in_native_order(self):
        from builtin_wave import source_builtin_wave
        source=native('nWaveMode=2\nfWaveAlpha=.8\nbModWaveAlphaByVolume=1\n')
        inputs=frames()[:1];scene=execute_scene(source,inputs,reader=READER,width=512,height=288,mesh_x=8,mesh_y=8)
        wave=source_builtin_wave(source,scene,audio(inputs),binary=BINARY)['frames'][0]
        self.assertAlmostEqual(wave['rgba'][3],.8,places=6)

    def test_historical_static_flags_and_native_projection_drive_drawing_spec(self):
        from builtin_wave import source_builtin_wave
        source=native('nWaveMode=6\nbWaveThick=1\nfWaveSmoothing=0\nwave_x=.25\nwave_y=.9\n'
                      'wave_r=.5\nwave_g=.5\nwave_b=.5\nfWaveAlpha=1.17\nbMaximizeWaveColor=0\n'
                      'per_frame_1=wave_mode=0;wave_thick=0;wave_additive=1;\n')
        scene=execute_scene(source,frames()[:1],reader=READER,width=512,height=288,mesh_x=8,mesh_y=8)
        result=source_builtin_wave(source,scene,audio(frames()[:1]),binary=BINARY,control_policy=LEGACY_WAVE)
        wave=result['frames'][0]
        self.assertEqual(result['mode'],6)
        self.assertEqual(wave['draw_mode'],'strip')
        self.assertEqual(len(wave['positions'][0]),159)
        self.assertAlmostEqual(float(np.mean(np.asarray(wave['positions'][0])[:,1])),.75,places=6)
        np.testing.assert_allclose(wave['rgba'],[.5,.5,.5,1])
        self.assertFalse(wave['additive'])
        np.testing.assert_allclose(wave['copy_offsets'],[[0,0],[1/512,0],[1/512,-1/288],[0,-1/288]])

    def test_source_colour_maximization_and_mode_specific_opacity(self):
        from builtin_wave import source_builtin_wave
        source=native('nWaveMode=2\nwave_r=.2\nwave_g=.4\nwave_b=.1\nfWaveAlpha=.8\n')
        scene=execute_scene(source,frames()[:1],reader=READER,width=512,height=288,mesh_x=8,mesh_y=8)
        wave=source_builtin_wave(source,scene,audio(frames()[:1]),binary=BINARY)['frames'][0]
        np.testing.assert_allclose(wave['rgba'],[.5,1,.25,.8*.09],atol=1e-7)

    def test_frame_audio_mismatch_is_rejected(self):
        from builtin_wave import source_builtin_wave
        source=native('nWaveMode=6\n');scene=execute_scene(source,frames(),reader=READER,mesh_x=8,mesh_y=8)
        with self.assertRaisesRegex(ValueError,'schedule'):
            source_builtin_wave(source,scene,audio(frames()[:1]),binary=BINARY)


if __name__=='__main__':unittest.main()


def test_pr57_mode1_opacity_boost_after_volume_modulation():
    from builtin_wave import _colour
    main={'wave_r':1,'wave_g':.5,'wave_b':.25,'wave_brighten':0}
    frame={'vol':.85,'treb':1}
    source={'values':{'bModWaveAlphaByVolume':'1','fModWaveAlphaStart':'.75','fModWaveAlphaEnd':'.95'}}
    old=_colour(source,main,frame,1,.8,256,144)
    patched=_colour(source,main,frame,1,.8,256,144,mode1_alpha_boost=True)
    assert abs(patched[3]-old[3]*1.25)<=1e-7
    saturated=_colour({'values':{}},main,frame,1,.9,256,144,mode1_alpha_boost=True)
    assert saturated[3]==1
