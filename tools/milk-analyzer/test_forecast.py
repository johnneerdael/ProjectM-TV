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


def test_explicit_composite_raster_setting_reaches_the_source_forecast():
    source=native(BASE+'warp_1=`shader_body {ret=0;}\ncomp_1=`shader_body {ret=uv.x;}\n')
    result=predict(source,domain=domain(composite_subpixel_bits=4),audio=audio(1))
    from composite_mesh import composite_fields,make_mesh
    expected=composite_fields(32,32,mesh=make_mesh(32,32,raster_subpixel_bits=4))['uv'][...,0]
    np.testing.assert_allclose(result['frames'][0]['display'][...,0],np.clip(expected,0,1))
    assert result['frames'][0]['history']['composite_subpixel_bits']==4


def test_warp_raster_setting_and_original_uv_reach_the_source_forecast():
    source=native(BASE+'warp_1=`shader_body {ret=float3(uv_orig,.25);}\ncomp_1=`shader_body {ret=0;}\n')
    settings=domain(warp_subpixel_bits=4);settings.update(mesh_x=10,mesh_y=10)
    result=predict(source,domain=settings,audio=audio(1))
    from spatial import mesh_inputs,interpolate_mesh
    mesh=mesh_inputs(10,10,aspect_x=1,aspect_y=1)
    x,y=np.meshgrid((np.arange(32,dtype=np.float32)+.5)/32,(np.arange(32,dtype=np.float32)+.5)/32)
    query=np.stack((x,y),-1)
    expected=interpolate_mesh(mesh['position']*.5+.5,query,raster_subpixel_bits=4,viewport=(32,32))
    np.testing.assert_allclose(result['frames'][0]['feedback'][...,:2],np.clip(expected,0,1),atol=1e-7)


def test_explicit_main_sampler_profile_reaches_source_forecast_and_history():
    source=native(BASE+'warp_1=`shader_body {ret=GetPixel(uv);}\ncomp_1=`shader_body {ret=GetPixel(uv);}\n')
    settings=domain(main_sampling_profile='swiftshader-unorm8-fixed16-v1');settings['quantize']=True
    result=predict(source,domain=settings,audio=audio(1))
    assert result['frames'][0]['history']['main_sampling_profile']=='swiftshader-unorm8-fixed16-v1'
    np.testing.assert_allclose(result['frames'][0]['display'][...,:3],np.broadcast_to([.2,.4,.6],(32,32,3)),atol=1/255)


def test_verified_engine_defaults_clamp_main_before_qualified_alias():
    source=native(BASE+'bTexWrap=0\nper_frame_1=q1=equal(frame,0);\n'
                  'warp_1=`shader_body {if(q1>.5){ret=float3(uv_orig,0);}'
                  'else{ret=float3(tex2D(sampler_main,float2(-.1,.5)).x,'
                  'tex2D(sampler_fc_main,float2(1.1,.5)).y,0);}}\n'
                  'comp_1=`shader_body {ret=GetPixel(uv);}\n')
    from shader_compat import check_shader
    stages={stage:check_shader(source['sections'][prefix]['source'],stage=stage,profile='glsl330',
                              translator=BINARIES/'milk-shader-translate',
                              validator=Path('/opt/homebrew/bin/glslangValidator'),
                              samplers={'sampler_main':'sampler2D','sampler_fc_main':'sampler2D'},
                              texture_sizes=['texsize_main'])
            for stage,prefix in [('warp','warp_'),('composite','comp_')]}
    assert all(item['offline_accepted'] for item in stages.values()),stages
    settings=domain()
    current=predict(source,domain=settings,audio=audio(2),compatibility=stages)
    historical=predict(source,domain=domain(main_binding_policy='legacy-sorted-v1'),audio=audio(2),compatibility=stages)
    assert current['domain']==settings
    assert current['input_hashes']['domain_sha256']==importlib.import_module('forecast').digest(settings)
    assert current['provenance']['main_binding_policy']=='projectmtv-core-2.2.6-v1'
    np.testing.assert_allclose(current['frames'][1]['feedback'][...,0],.5/32,atol=1e-6)
    np.testing.assert_allclose(historical['frames'][1]['feedback'][...,0],.9,atol=1e-6)


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


def test_shape_instances_receive_distinct_inherited_and_texture_sampler_modes(monkeypatch):
    module=importlib.import_module('forecast')
    source=native(BASE+'bTexWrap=0\nwarp_1=`shader_body {ret=0;}\ncomp_1=`shader_body {ret=GetPixel(uv);}\n'
                  'shapecode_0_enabled=1\nshapecode_0_textured=1\nshapecode_0_num_inst=2\n'
                  'shapecode_0_rad=.4\nshapecode_0_a=1\nshapecode_0_a2=1\n'
                  'shape_0_per_frame1=x=.25+.5*instance;y=.5;\n')
    if source['parser_inputs']['engine']['patches_sha256']!=module.CORE_237_EQUATION_ENGINE['patches_sha256']:
        pytest.skip('Requires prepared 43-patch adapters for the observed shape-state contract')
    calls=[];original=module.sample2d
    def observe(field,uv,**settings):
        calls.append((settings['wrap'],settings['linear']))
        return original(field,uv,**settings)
    monkeypatch.setattr(module,'sample2d',observe)
    result=predict(source,audio=audio(1))
    assert calls and set(calls)=={(False,True),(True,False)}
    split=calls.index((True,False))
    assert all(value==(False,True) for value in calls[:split])
    assert all(value==(True,False) for value in calls[split:])
    assert result['provenance']['shape_sampler_policy']=='projectmtv-core-2.3.8-shape-state-v1'


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


def test_production_equation_rng_contract_rejects_a_lab_seed():
    source = native(BASE)
    settings = domain(equation_rng_policy='projectmtv-core-2.3.4-cold-thread-v1')
    with pytest.raises(ValueError, match='production equation RNG seed'):
        predict(source, domain=settings, audio=audio(1))


def test_production_equation_rng_sequence_and_provenance():
    source = native(BASE + 'per_frame_1=q1=rand(1);q2=rand(1);q3=rand(1);\n'
                    'comp_1=`shader_body {ret=float3(q1,q2,q3);}\n')
    from forecast import PRODUCTION_EQUATION_ENGINES
    engine=source['parser_inputs']['engine']
    policy=next(name for name,expected in PRODUCTION_EQUATION_ENGINES.items()
                if all(engine.get(key)==value for key,value in expected.items()))
    settings = domain(equation_rng_policy=policy)
    settings['equation_seed'] = 0x4141f00d
    result = predict(source, domain=settings, audio=audio(1))
    # Independent MT19937 implementation; evaluator scales an unsigned draw by UINT32_MAX.
    generator = np.random.RandomState(0x4141f00d)
    expected = generator.randint(0, 2**32, size=3, dtype=np.uint32).astype(np.float64) / (2**32-1)
    np.testing.assert_allclose(result['frames'][0]['display'][16,16,:3], expected, atol=1e-7)
    contract = result['provenance']['equation_rng']
    assert contract['seed'] == 0x4141f00d
    assert contract['policy'] == policy
    assert contract['lifecycle'] == 'fresh evaluator thread; no previous equation draws'
    assert contract['native_sequence_verified'] is False


def test_unknown_equation_rng_policy_is_rejected():
    with pytest.raises(ValueError, match='equation RNG policy'):
        predict(native(BASE), domain=domain(equation_rng_policy='future-engine'), audio=audio(1))


def test_production_equation_rng_policy_rejects_another_patch_series():
    source = native(BASE)
    source['parser_inputs']['engine']['patches_sha256'] = 'another-series'
    settings = domain(equation_rng_policy='projectmtv-core-2.3.4-cold-thread-v1')
    settings['equation_seed'] = 0x4141f00d
    with pytest.raises(ValueError, match='equation RNG engine identity'):
        predict(source, domain=settings, audio=audio(1))


@pytest.fixture
def profile_gate(tmp_path, monkeypatch):
    """Test metadata validation without executing adapters under a false identity."""
    module = importlib.import_module('forecast')
    reader = tmp_path / 'milk-native-reader'
    reader.write_bytes(b'profile-gate-fixture')

    def stop_before_execution(*args, **kwargs):
        raise RuntimeError('profile accepted before source execution')

    monkeypatch.setattr(module.SourcePipeline, 'from_source', stop_before_execution)

    def check(patches_sha256, settings, *, source_archive='fixture', audio_archive='fixture'):
        source = dict(parser_inputs=dict(engine=dict(
            commit='e0b0a967f0ffd7d332106c366668ed271718472b',
            patches_sha256=patches_sha256), engine_archive_sha256=source_archive),
            reader_sha256=hashlib.sha256(reader.read_bytes()).hexdigest())
        values = dict(uses_rendered_reference=False, frames=[dict(time=0)],
                      engine_archive_sha256=audio_archive)
        return module.forecast_source(source, audio=values, binaries=tmp_path,
                                      domain=settings, compatibility={})

    return check


PATCHES_234 = 'd21d4e3d9725178c000fd6f7ea5cd331389fb1100b70fce51341ece65d3fd818'
PATCHES_235 = 'd73c955a26380a502516e6ba3a18baf753851244de4de2e5a3083930766a539a'
PATCHES_237 = 'd70f5b5ec3f3c0b4da764cb824153f142b88e17e27c2e9e71d2b481c19998c7d'


@pytest.mark.parametrize('version,patches', [('2.3.4', PATCHES_234), ('2.3.5', PATCHES_235), ('2.3.7', PATCHES_237)])
def test_release_equation_profile_accepts_only_its_source_identity(profile_gate, version, patches):
    settings = domain(equation_rng_policy=f'projectmtv-core-{version}-cold-thread-v1')
    settings['equation_seed'] = 0x4141f00d
    with pytest.raises(RuntimeError, match='profile accepted before source execution'):
        profile_gate(patches, settings)
    other = PATCHES_234 if version != '2.3.4' else PATCHES_235
    with pytest.raises(ValueError, match='equation RNG engine identity'):
        profile_gate(other, settings)


@pytest.mark.parametrize('version,patches', [('2.3.5', PATCHES_235), ('2.3.7', PATCHES_237)])
def test_release_equation_profile_rejects_a_lab_seed(profile_gate, version, patches):
    settings = domain(equation_rng_policy=f'projectmtv-core-{version}-cold-thread-v1')
    with pytest.raises(ValueError, match='production equation RNG seed'):
        profile_gate(patches, settings)


@pytest.mark.parametrize('patches', [PATCHES_234, PATCHES_235, PATCHES_237])
@pytest.mark.parametrize('width,height', [(256, 144), (1024, 768), (256, 1330)])
def test_quad_line_profile_accepts_known_low_resolution_engines(profile_gate, patches, width, height):
    settings = domain(line_rendering_profile='projectmtv-gles-quad-lines-v1')
    settings.update(profile='gles300', width=width, height=height)
    with pytest.raises(RuntimeError, match='profile accepted before source execution'):
        profile_gate(patches, settings)


def test_quad_line_profile_still_rejects_unknown_patch_series(profile_gate):
    settings = domain(line_rendering_profile='projectmtv-gles-quad-lines-v1')
    settings['profile'] = 'gles300'
    with pytest.raises(ValueError, match='quad-line engine identity'):
        profile_gate('unknown-series', settings)


@pytest.mark.parametrize('line_profile', ['canonical-gl-lines-v1', 'projectmtv-gles-quad-lines-v1'])
@pytest.mark.parametrize('width,height', [(1920, 1080), (3840, 2160), (256, 1331)])
@pytest.mark.parametrize('version,patches', [('2.3.5', PATCHES_235), ('2.3.7', PATCHES_237)])
def test_release_engine_refuses_unimplemented_scaled_lines_and_native_detail(profile_gate, line_profile, width, height, version, patches):
    # Applies even with a declared lab equation seed; rendering gaps are independent of RNG.
    settings = domain(line_rendering_profile=line_profile)
    settings.update(profile='gles300', width=width, height=height)
    with pytest.raises(ValueError, match=version+'.*higher-resolution'):
        profile_gate(patches, settings)


def test_237_equation_profile_rejects_wrong_audio_archive(profile_gate):
    settings=domain(equation_rng_policy='projectmtv-core-2.3.7-cold-thread-v1')
    settings['equation_seed']=0x4141f00d
    with pytest.raises(ValueError,match='source/audio engine identity'):
        profile_gate(PATCHES_237,settings,source_archive='c17fc176d6a79556dbfd6a998bbf78350f7f6d76dcd81d0bf7f6c5febd4bc578',audio_archive='wrong-archive')


def test_237_profile_prefix_does_not_accept_an_unregistered_policy(profile_gate):
    settings=domain(equation_rng_policy='projectmtv-core-2.3.7-cold-thread-v2')
    with pytest.raises(ValueError,match='unknown equation RNG policy'):
        profile_gate(PATCHES_237,settings)


def test_real_237_forecast_reports_true_archive_and_rejects_forged_archives(tmp_path,monkeypatch):
    module=importlib.import_module('forecast')
    binaries=test_native_audio.ROOT/'build/visual-loop/source237/adapters'
    if not (binaries/'milk-native-reader').is_file():binaries=BINARIES
    preset=tmp_path/'forecast237.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\n'+BASE)
    source=module.read_source(preset,reader=binaries/'milk-native-reader')
    if source['parser_inputs']['engine']['patches_sha256']!=PATCHES_237:
        pytest.skip('separately prepared 43-patch CPU adapters required')
    monkeypatch.setattr(test_native_audio,'BINARY',binaries/'milk-audio-inputs')
    values=audio(1)
    settings=domain(equation_rng_policy='projectmtv-core-2.3.7-cold-thread-v1',
                    line_rendering_profile='projectmtv-gles-quad-lines-v1')
    settings.update(equation_seed=0x4141f00d,profile='gles300')

    def compute():
        return module.forecast_source(source,audio=values,binaries=binaries,domain=settings,compatibility={})

    result=compute()
    actual='c17fc176d6a79556dbfd6a998bbf78350f7f6d76dcd81d0bf7f6c5febd4bc578'
    assert source['parser_inputs']['engine_archive_sha256']==values['engine_archive_sha256']==actual
    assert result['provenance']['engine_archive_sha256']==actual
    assert result['provenance']['equation_rng']['policy']=='projectmtv-core-2.3.7-cold-thread-v1'
    assert result['appearance_accuracy_verified'] is False
    values['engine_archive_sha256']='wrong-archive'
    with pytest.raises(ValueError,match='source/audio engine identity'):compute()
    # Even matching forged parser/audio metadata must fail the actual wave adapter identity.
    source['parser_inputs']['engine_archive_sha256']='wrong-archive'
    with pytest.raises(ValueError,match='builtin-wave source engine identity'):compute()


def test_patched_quad_line_profile_reaches_custom_wave_forecast():
    source=native(BASE+'wavecode_0_enabled=1\nwavecode_0_samples=2\n'
                  'wavecode_0_r=1\nwavecode_0_g=0\nwavecode_0_b=0\nwavecode_0_a=1\n'
                  'wave_0_per_point1=x=.25+.5*sample;y=.625;\n')
    settings=domain(line_rendering_profile='projectmtv-gles-quad-lines-v1')
    settings.update(profile='gles300',initial_rgba=[0,0,0,0])
    result=predict(source,domain=settings,audio=audio(1))
    np.testing.assert_array_equal(np.nonzero(result['frames'][0]['feedback'][...,0]),
                                  (np.full(16,11),np.arange(8,24)))


def test_quad_profile_refuses_other_contexts_and_scaled_viewports():
    settings=domain(line_rendering_profile='projectmtv-gles-quad-lines-v1')
    with pytest.raises(ValueError,match='quad-line profile'):
        predict(native(BASE),domain=settings,audio=audio(1))
    settings.update(profile='gles300',width=1920,height=1080)
    with pytest.raises(ValueError,match='quad-line profile|higher-resolution lines/native feedback detail'):
        predict(native(BASE),domain=settings,audio=audio(1))


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


def test_renderer_hue_time_uses_native_float_context():
    from composite_mesh import composite_fields
    source=native(BASE+'comp_1=`shader_body {ret=_vDiffuse.rgb;}\n')
    values=audio()
    for frame in values['frames']:
        frame['time']+=10001.123456789
    result=predict(source,audio=values)
    expected=composite_fields(32,32,time=float(np.float32(values['frames'][0]['time'])),hue_offsets=[0]*4)['diffuse'][...,:3]
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
