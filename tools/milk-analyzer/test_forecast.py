import importlib
import hashlib
from pathlib import Path
import tempfile

import numpy as np
import pytest
import test_native_audio
import test_shader_compat


BINARIES = test_native_audio.ROOT / 'build/milk-analyzer/native'
BASE = 'warp=0\nfWaveAlpha=0\nnWaveMode=6\nfDecay=1\n'


def native(body):
    module=importlib.import_module('forecast')
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'fixture.milk'
        path.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\n'+body)
        return module.read_source(path,reader=BINARIES/'milk-native-reader')


def domain(**updates):
    return dict(width=32, height=32, mesh_x=8, mesh_y=8, profile='glsl330',
                initial_rgba=[.2,.4,.6,1], hue_offsets=[0,0,0,0],
                equation_seed=12345, blur_levels=0, quantize=False, **updates)


def audio(count=3):
    process, result = test_native_audio.NativeAudioTest().run_audio(np.zeros(count*1470), frames=count)
    assert process.returncode == 0, process.stderr
    return result


def compatibility(source):
    return {stage: test_shader_compat.ShaderCompatibilityTest().check(source['sections'][prefix]['source'], stage=stage)
            for stage, prefix in [('warp','warp_'),('composite','comp_')]
            if source.get('sections',{}).get(prefix,{}).get('source')}


def predict(source, **settings):
    return importlib.import_module('forecast').forecast_source(
        source, audio=settings.pop('audio', audio()), binaries=BINARIES,
        domain=settings.pop('domain', domain()),
        compatibility=settings.pop('compatibility', compatibility(source)), **settings)


def test_complete_equation_warp_draw_composite_forecast_keeps_feedback_separate():
    source = native(BASE + 'per_frame_1=q1=bass*.5;\n'
                    'warp_1=`shader_body {ret=GetPixel(uv)*q1;}\n'
                    'comp_1=`shader_body {ret=1-GetPixel(uv);}\n')
    result = predict(source)
    assert result['status'] == 'computed'
    assert result['uses_rendered_reference'] is False
    assert result['appearance_accuracy_verified'] is False
    for i, frame in enumerate(result['frames']):
        expected = np.array([.2,.4,.6]) * .5**(i+1)
        np.testing.assert_allclose(frame['feedback'][...,:3], np.broadcast_to(expected,(32,32,3)), atol=1e-6)
        np.testing.assert_allclose(frame['display'][...,:3], np.broadcast_to(1-expected,(32,32,3)), atol=1e-6)
    assert result['input_hashes']['pcm_sha256'] == audio()['pcm_sha256']
    assert result['input_hashes']['preset_sha256'] == source['preset_sha256']


def test_shapes_are_drawn_between_warp_and_composite_and_become_feedback():
    source = native(BASE + 'warp_1=`shader_body {ret=0;}\ncomp_1=`shader_body {ret=0;}\n'
                    'shapecode_0_enabled=1\nshapecode_0_x=.25\nshapecode_0_y=.75\n'
                    'shapecode_0_rad=.4\nshapecode_0_r=1\nshapecode_0_g=0\nshapecode_0_b=0\n'
                    'shapecode_0_r2=1\nshapecode_0_g2=0\nshapecode_0_b2=0\n'
                    'shapecode_0_a=1\nshapecode_0_a2=1\n')
    result = predict(source)
    assert result['frames'][0]['feedback'][8,8,0] > .99
    assert result['frames'][0]['feedback'][24,8,0] == 0
    assert np.count_nonzero(result['frames'][0]['display'][...,:3]) == 0


def test_textured_shape_samples_previous_main_instead_of_current_warp_output():
    source = native(BASE + 'warp_1=`shader_body {ret=0;}\ncomp_1=`shader_body {ret=GetPixel(uv);}\n'
                    'shapecode_0_enabled=1\nshapecode_0_textured=1\nshapecode_0_rad=1\n'
                    'shapecode_0_r=1\nshapecode_0_g=1\nshapecode_0_b=1\n'
                    'shapecode_0_r2=1\nshapecode_0_g2=1\nshapecode_0_b2=1\n'
                    'shapecode_0_a=1\nshapecode_0_a2=1\n')
    result = predict(source)
    np.testing.assert_allclose(result['frames'][0]['feedback'][16,16,:3], [.2,.4,.6], atol=2e-6)


def test_named_shape_image_is_not_silently_replaced_with_main():
    source = native(BASE + 'shapecode_0_enabled=1\nshapecode_0_textured=1\nshapecode_0_image=missing\n')
    with pytest.raises(ValueError, match='image'):
        predict(source)


def test_missing_random_dependency_or_target_stage_evidence_stays_unresolved():
    source = native(BASE + 'comp_1=`shader_body {ret=rand_frame.xyz;}\n')
    with pytest.raises(ValueError, match='rand_frame'):
        predict(source)
    with pytest.raises(ValueError, match='stage'):
        predict(source, compatibility={})


def test_audio_reference_data_or_wrong_engine_identity_is_rejected():
    source = native(BASE)
    values = audio()
    values['uses_rendered_reference'] = True
    with pytest.raises(ValueError, match='source'):
        predict(source, audio=values)
    values = audio()
    values['engine_archive_sha256'] = 'different'
    with pytest.raises(ValueError, match='engine'):
        predict(source, audio=values)


def test_frozen_domain_and_cold_reset_make_forecasts_repeatable():
    source = native(BASE + 'per_frame_init_1=q1=rand(100);\nper_frame_1=q2=q1*.001;\n'
                    'comp_1=`shader_body {ret=q2;}\n')
    first, second = predict(source), predict(source)
    assert first['input_hashes'] == second['input_hashes']
    for a,b in zip(first['frames'],second['frames']):
        np.testing.assert_array_equal(a['display'],b['display'])
    altered = domain()
    altered['equation_seed'] = 98765
    assert predict(source, domain=altered)['input_hashes']['domain_sha256'] != first['input_hashes']['domain_sha256']


def test_streaming_forecast_does_not_retain_all_surface_arrays():
    source = native(BASE)
    visited = []
    result = predict(source, retain_surfaces=False,
                     on_frame=lambda frame: visited.append(float(np.mean(frame['display'][...,:3]))))
    assert len(visited) == len(result['frames']) == 3
    assert all('display' not in frame and 'feedback' not in frame for frame in result['frames'])


def test_native_source_loader_binds_original_bytes_and_actual_parser(tmp_path):
    module=importlib.import_module('forecast')
    preset=tmp_path/'sample.milk'
    preset.write_bytes(b'MILKDROP_PRESET_VERSION=201\r\nwarp=0\r\n')
    source=module.read_source(preset,reader=BINARIES/'milk-native-reader')
    assert source['preset_sha256']==hashlib.sha256(preset.read_bytes()).hexdigest()
    assert source['reader_sha256']==hashlib.sha256((BINARIES/'milk-native-reader').read_bytes()).hexdigest()


def test_renderer_hue_time_keeps_double_precision_before_native_sinf_narrowing():
    from composite_mesh import composite_fields
    source=native(BASE+'comp_1=`shader_body {ret=_vDiffuse.rgb;}\n')
    values=audio()
    for frame in values['frames']:
        frame['time']+=10001.123456789
    result=predict(source,audio=values)
    expected=composite_fields(32,32,time=values['frames'][0]['time'],hue_offsets=[0]*4)['diffuse'][...,:3]
    np.testing.assert_allclose(result['frames'][0]['display'][...,:3],expected,atol=3e-7,rtol=0)


def test_custom_wave_equations_and_projection_enter_the_full_draw_chain():
    source=native(BASE+'warp_1=`shader_body {ret=0;}\ncomp_1=`shader_body {ret=GetPixel(uv);}\n'
                  'wavecode_0_enabled=1\nwavecode_0_samples=3\nwavecode_0_bUseDots=1\n'
                  'wave_0_per_point1=x=.25+sample*.5;y=.75;r=1;g=0;b=0;a=1;\n')
    result=predict(source)
    red=result['frames'][0]['feedback'][...,0]
    assert np.count_nonzero(red)>0
    rows=np.nonzero(red)[0]
    assert np.max(rows)<12  # Source y=.75 appears toward the top, not bottom.
    assert np.count_nonzero(result['frames'][0]['feedback'][...,1:3])==0


def test_random_bindings_enter_full_forecast_and_wrong_frame_time_is_rejected():
    from shader_random import execute_ledger
    source=native(BASE+'comp_1=`shader_body {ret=rand_frame.xyz;}\n')
    values=audio()
    events=[{'kind':'construct','id':'comp'}]
    bindings=[]
    for frame in values['frames']:
        bindings.append({'composite':{'event_index':len(events),'shader_id':'comp'}})
        events.append({'kind':'load','id':'comp','time':frame['time']})
    ledger=execute_ledger(BINARIES/'milk-shader-random',seed=12345,events=events)
    inputs={'ledger':ledger,'profile':ledger['profile'],'bindings':bindings}
    result=predict(source,audio=values,random_inputs=inputs)
    for predicted,load in zip(result['frames'],ledger['loads']):
        expected=load['uniforms']['rand_frame'][:3]
        np.testing.assert_allclose(predicted['display'][...,:3],np.broadcast_to(expected,(32,32,3)),atol=1e-7)
    inputs['bindings'][0]['composite']['event_index']=2
    with pytest.raises(ValueError,match='time'):
        predict(source,audio=values,random_inputs=inputs)


def test_callback_cannot_mutate_the_declared_domain_during_forecast():
    import copy
    source=native(BASE)
    inputs=domain();original=copy.deepcopy(inputs)
    def callback(frame):
        inputs['quantize']=True
        inputs['initial_rgba'][0]=1
    result=predict(source,domain=inputs,on_frame=callback)
    assert result['domain']==original


def test_streamed_forecast_returns_source_colour_flash_and_motion_descriptors():
    source=native(BASE)
    result=predict(source,retain_surfaces=False)
    descriptors=result['descriptors']
    assert descriptors['frames_measured']==3
    assert descriptors['colour']['mean_effective_hue_bins']==pytest.approx(1)
    assert descriptors['flashing']['peak_mean_luma_jump']<1e-6
    assert descriptors['motion']['median_speed_viewports_per_second'] is None
    assert descriptors['appearance_accuracy_verified'] is False
