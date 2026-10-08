"""PR57 source-math controls; published-AAR comparisons remain separate."""
import os
import json
import subprocess
from pathlib import Path

import numpy as np
import pytest


ENGINE = {
    'commit': '6f64807467e312034883a4389e6aa80a675458bc',
    'patches_sha256': '6e27be9d314e464c6ed67925c65092164e35e8a1b5273f81b1bf0b6786beefae',
}


@pytest.fixture
def core2325_adapters():
    variable=os.environ.get('MILK_TEST_2325_BINARIES')
    if variable is None:pytest.skip('explicit prepared PR57 source adapters required')
    folder=Path(variable)
    for name in ['milk-native-reader','milk-wave-inputs','milk-audio-inputs','milk-noise-inputs']:
        if not (folder/name).is_file():pytest.skip('missing PR57 adapter: '+name)
    return folder


def test_2325_exact_identity_inherits_centres_and_has_distinct_rng():
    import engine_profiles as profiles
    import forecast
    from composite_mesh import CORE_2322_CENTRES
    from primitives import CORE_2322_SHAPE_CENTRES
    assert profiles.CORE_2325_ENGINE == ENGINE
    assert profiles.matches(ENGINE)
    assert forecast.PRODUCTION_EQUATION_ENGINES['projectmtv-core-2.3.25-cold-thread-v1'] == ENGINE
    assert forecast.source_centre_policies(ENGINE, {}) == (CORE_2322_CENTRES, CORE_2322_SHAPE_CENTRES)
    assert not profiles.matches({**ENGINE, 'patches_sha256': '0'*64})


def test_2325_retained_builtin_viewport_requires_qualified_context_and_grid():
    from forecast import source_builtin_viewport_policy
    from quad_lines import LEGACY_VIEWPORT,RETAINED_CLIP_VIEWPORT,PROFILE
    from engine_profiles import CORE_2322_ENGINE
    context={'profile':'gles300','line_rendering_profile':PROFILE,'triangle_subpixel_bits':8}
    assert source_builtin_viewport_policy(ENGINE,context)==RETAINED_CLIP_VIEWPORT
    assert source_builtin_viewport_policy(CORE_2322_ENGINE,context)==LEGACY_VIEWPORT
    assert source_builtin_viewport_policy(ENGINE,{})==LEGACY_VIEWPORT
    for engine,domain in [(CORE_2322_ENGINE,context),(ENGINE,{**context,'profile':'glsl330'}),
                          (ENGINE,{**context,'triangle_subpixel_bits':None})]:
        with pytest.raises(ValueError,match='viewport'):
            source_builtin_viewport_policy(engine,{**domain,'builtin_wave_viewport_policy':RETAINED_CLIP_VIEWPORT})


@pytest.mark.parametrize('amount', [0, .001, .25, 1, 1.5])
def test_2325_source_tint_uses_authored_amount_without_changing_old_profiles(amount):
    from legacy_composite import source_tint_amount, legacy_display, corner_shades
    from engine_profiles import CORE_2322_ENGINE
    source = {'values': {'fshader': str(amount)}, 'parser_inputs': {
        'engine': ENGINE, 'setting_lookup_policy': 'native-case-insensitive-v1'}}
    assert source_tint_amount(source) == np.float32(amount)
    field = np.ones((8,8,4), dtype=np.float32)*.2
    actual = legacy_display(field, values={'fGammaAdj': '1'}, time=0,
        hue_offsets=[0]*4, quantize=False, shader_amount=source_tint_amount(source))
    if amount <= .001:
        np.testing.assert_allclose(actual[...,:3], .2, atol=1e-7)
    else:
        assert np.ptp(actual[...,:3]) > 0
    old = {**source, 'parser_inputs': {**source['parser_inputs'], 'engine': CORE_2322_ENGINE}}
    assert source_tint_amount(old) is None
    assert source_tint_amount({'values':{}, 'parser_inputs': {'engine': ENGINE}}) == 0
    np.testing.assert_array_equal(corner_shades(0,[0]*4,shader_amount=None),corner_shades(0,[0]*4))


def test_2325_mode1_source_wrapper_has_boost_and_open_topology(tmp_path,core2325_adapters):
    from forecast import read_source
    from scene_equations import execute_scene
    from builtin_wave import source_builtin_wave, _colour
    from test_builtin_wave import audio
    from test_scene_equations import frames
    folder = core2325_adapters
    preset = tmp_path/'spiral.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=111\n[preset00]\nnWaveMode=1\nfWaveAlpha=.5\nbMaximizeWaveColor=0\n')
    source = read_source(preset, reader=folder/'milk-native-reader')
    assert source['parser_inputs']['engine'] == ENGINE
    inputs = frames()[:1]
    scene = execute_scene(source,inputs,reader=folder/'milk-native-reader',width=256,height=144)
    data = audio(inputs)
    data['frames'][0]['waveform_left'] = np.linspace(-.5,.5,480).tolist()
    data['frames'][0]['waveform_right'] = np.linspace(.3,-.3,480).tolist()
    wave = source_builtin_wave(source,scene,data,binary=folder/'milk-wave-inputs')['frames'][0]
    assert wave['draw_mode'] == 'strip'
    assert wave['rgba'][3] == .625
    assert _colour(source,scene['frames'][0]['main'],data['frames'][0],1,.5,256,144)[3] == .5
    assert wave['positions'][0][0] != wave['positions'][0][-1]


def test_2325_rejects_historical_wave_adapter_instead_of_mixing_semantics(tmp_path,core2325_adapters):
    from forecast import read_source
    from scene_equations import execute_scene
    from builtin_wave import source_builtin_wave
    from test_builtin_wave import audio
    from test_scene_equations import frames
    folder=core2325_adapters
    old=Path(os.environ.get('MILK_TEST_2322_BINARIES','build/visual-loop/source2322/adapters'))
    if not (folder/'milk-native-reader').is_file() or not (old/'milk-wave-inputs').is_file():
        pytest.skip('paired current/historical adapters required')
    preset=tmp_path/'spiral.milk';preset.write_text('MILKDROP_PRESET_VERSION=111\n[preset00]\nnWaveMode=1\n')
    source=read_source(preset,reader=folder/'milk-native-reader');inputs=frames()[:1]
    scene=execute_scene(source,inputs,reader=folder/'milk-native-reader',width=256,height=144)
    with pytest.raises(ValueError,match='waveform.*identity'):
        source_builtin_wave(source,scene,audio(inputs),binary=old/'milk-wave-inputs')


def test_2325_pipeline_threads_static_tint_from_source(tmp_path,core2325_adapters):
    from forecast import read_source
    from pipeline_fields import SourcePipeline
    folder=core2325_adapters
    preset=tmp_path/'tint.milk';preset.write_text('MILKDROP_PRESET_VERSION=111\n[preset00]\nfShader=.25\n')
    source=read_source(preset,reader=folder/'milk-native-reader')
    pipeline=SourcePipeline.from_source(source,profile='gles300',compatibility={},
        initial_feedback=np.zeros((8,8,4),np.float32),warp_reads_blur=False,blur_levels=0)
    assert pipeline.legacy_tint_amount==.25


@pytest.mark.parametrize('kind', ['audio', 'noise'])
def test_2325_input_adapters_preserve_exact_production_inputs(tmp_path,kind,core2325_adapters):
    folder = core2325_adapters
    binary = folder/('milk-audio-inputs' if kind=='audio' else 'milk-noise-inputs')
    if not binary.is_file():pytest.skip('prepared PR57 input adapters required')
    output = tmp_path/'output'
    if kind=='audio':
        pcm=tmp_path/'pcm.f32';np.zeros(2*1470,dtype='<f4').tofile(pcm)
        request=dict(pcm_path=str(pcm),output=str(output),fps=30,frames=2,channels=1,
            clock_policy='projectmtv-jni-rounded-nanoseconds30-v1',
            preset_progress_policy='projectmtv-core-2.3.25-cold-jni-v1',entropy_seed=12345)
    else:
        request=dict(output=str(output),names=['noise_lq_lite'],seed=3567620661,
            seed_policy='production-clock-seed-v1')
    path=tmp_path/'request.json'
    if kind=='audio':
        probe={**request,'preset_progress_policy':'explicit-zero-placeholder-v1'}
        del probe['entropy_seed']
        path.write_text(json.dumps(probe))
        result=subprocess.run([str(binary),str(path)],capture_output=True,text=True)
        assert result.returncode==0,result.stderr
        if json.loads(output.read_text()).get('duration_distribution_model')!='libcxx-200100-fresh-normal-v1':
            pytest.skip('qualified libcxx-200100 cold runtime required')
    path.write_text(json.dumps(request))
    result=subprocess.run([str(binary),str(path)],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    data=json.loads(output.read_text() if kind=='audio' else result.stdout)
    if kind=='audio':
        assert data['frames'][0]['fps']==35
        assert data['preset_timing']['duration_draws']==3
        request['preset_progress_policy']='projectmtv-core-2.3.22-cold-jni-v1'
        path.write_text(json.dumps(request))
        assert subprocess.run([str(binary),str(path)],capture_output=True).returncode!=0
    else:
        assert data['seed_model']=='raw-declared-native-noise-v1'
        assert data['textures']['noise_lq_lite']['generator_seed']==3567620661
