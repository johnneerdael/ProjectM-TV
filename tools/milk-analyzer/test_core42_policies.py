import json,os,subprocess
from pathlib import Path
import numpy as np
import pytest

BINARIES=Path(os.environ.get('MILK_TEST_2321_BINARIES','build/visual-loop/source2321/adapters'))

@pytest.fixture
def qualified_core42_adapters():
    if 'MILK_TEST_2321_BINARIES' not in os.environ:
        pytest.skip('explicit prepared 4.2 adapters required')
    for name in ['milk-wave-inputs','milk-audio-inputs','milk-native-reader','milk-noise-inputs']:
        if not (BINARIES/name).is_file():
            pytest.skip('prepared 4.2 adapter missing: '+name)

@pytest.fixture
def qualified_core42_cold_runtime(qualified_core42_adapters,tmp_path):
    pcm=tmp_path/'qualification.f32';np.zeros(2*1470,dtype='<f4').tofile(pcm)
    output=tmp_path/'qualification.json';request=tmp_path/'qualification-request.json'
    request.write_text(json.dumps(dict(pcm_path=str(pcm),output=str(output),fps=30,frames=2,channels=1)))
    process=subprocess.run([str(BINARIES/'milk-audio-inputs'),str(request)],capture_output=True,text=True)
    assert process.returncode==0,process.stderr
    result=json.loads(output.read_text())
    if result.get('duration_distribution_model')!='libcxx-200100-fresh-normal-v1':
        pytest.skip('qualified libcxx-200100 cold runtime required')


def test_core42_live_wave_accepts_exact_new_identity(tmp_path,qualified_core42_adapters):
    from test_native_wave import frame
    output=tmp_path/'output.json';request=tmp_path/'request.json'
    request.write_text(json.dumps(dict(mode=6,mode_policy='evaluated-live-v1',width=256,height=144,
        frames=[frame(time=1,wave_mode=6)],output=str(output))))
    process=subprocess.run([str(BINARIES/'milk-wave-inputs'),str(request)],capture_output=True,text=True)
    assert process.returncode==0,process.stderr
    result=json.loads(output.read_text());assert result['mode_policy']=='evaluated-live-v1'
    assert result['engine_identity']['commit']=='6f64807467e312034883a4389e6aa80a675458bc'

def test_core42_cold_audio_progress_is_separate_and_pinned(tmp_path,qualified_core42_cold_runtime):
    pcm=tmp_path/'pcm.f32';np.zeros(30*1470,dtype='<f4').tofile(pcm)
    output=tmp_path/'output.json';request=tmp_path/'request.json'
    request.write_text(json.dumps(dict(pcm_path=str(pcm),output=str(output),fps=30,frames=30,channels=1,
       clock_policy='projectmtv-jni-rounded-nanoseconds30-v1',
       preset_progress_policy='projectmtv-core-2.3.21-cold-jni-v1',entropy_seed=12345)))
    process=subprocess.run([str(BINARIES/'milk-audio-inputs'),str(request)],capture_output=True,text=True)
    assert process.returncode==0,process.stderr
    result=json.loads(output.read_text());assert result['preset_timing']['duration_draws']==3
    assert result['frames'][0]['fps']==35
    assert result['preset_progress_policy']=='projectmtv-core-2.3.21-cold-jni-v1'


@pytest.mark.parametrize('policy',['projectmtv-core-2.3.16-cold-jni-v1','projectmtv-core-2.3.17-cold-jni-v1'])
def test_core42_audio_rejects_historical_progress_labels(tmp_path,policy,qualified_core42_adapters):
    pcm=tmp_path/'pcm.f32';np.zeros(30*1470,dtype='<f4').tofile(pcm)
    output=tmp_path/'output.json';request=tmp_path/'request.json'
    request.write_text(json.dumps(dict(pcm_path=str(pcm),output=str(output),fps=30,frames=30,channels=1,
       clock_policy='projectmtv-jni-rounded-nanoseconds30-v1',
       preset_progress_policy=policy,entropy_seed=12345)))
    process=subprocess.run([str(BINARIES/'milk-audio-inputs'),str(request)],capture_output=True,text=True)
    assert process.returncode!=0
    assert not output.exists()


def test_core42_source_identity_is_exact_and_has_separate_rng_label():
    import engine_profiles,forecast
    expected={'commit':'6f64807467e312034883a4389e6aa80a675458bc',
              'patches_sha256':'fd02c15d040ca073f7c09a0b798040c2696fa6bf2252d6ddc6c7b6ff7bcd92eb'}
    assert engine_profiles.CORE_2321_ENGINE==expected
    assert engine_profiles.matches(expected)
    assert not engine_profiles.matches({**expected,'patches_sha256':'0'*64})
    assert forecast.PRODUCTION_EQUATION_ENGINES['projectmtv-core-2.3.21-cold-thread-v1']==expected


def test_core42_forecast_keeps_new_identity_and_native_live_controls(tmp_path,qualified_core42_cold_runtime):
    from forecast import read_source,forecast_source,CORE_2321_EQUATION_RNG_POLICY,PRODUCTION_EQUATION_SEED
    source_path=tmp_path/'fixture.milk';source_path.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nwarp=0\nfWaveAlpha=0\nfDecay=1\n')
    source=read_source(source_path,reader=BINARIES/'milk-native-reader')
    pcm=tmp_path/'pcm.f32';np.zeros(3*1470,dtype='<f4').tofile(pcm)
    audio_path=tmp_path/'audio.json';request=tmp_path/'request.json';request.write_text(json.dumps(dict(
        pcm_path=str(pcm),output=str(audio_path),fps=30,frames=3,channels=1,
        clock_policy='projectmtv-jni-rounded-nanoseconds30-v1',
        preset_progress_policy='projectmtv-core-2.3.21-cold-jni-v1',entropy_seed=12345)))
    subprocess.run([str(BINARIES/'milk-audio-inputs'),str(request)],check=True,capture_output=True)
    domain=dict(width=32,height=32,mesh_x=8,mesh_y=8,profile='gles300',
        initial_rgba=[0,0,0,0],hue_offsets=[0]*4,equation_seed=PRODUCTION_EQUATION_SEED,
        equation_rng_policy=CORE_2321_EQUATION_RNG_POLICY,blur_levels=0,quantize=True)
    result=forecast_source(source,audio=json.loads(audio_path.read_text()),binaries=BINARIES,
                           domain=domain,compatibility={})
    assert result['status']=='computed' and len(result['frames'])==3
    assert result['provenance']['engine']['commit']=='6f64807467e312034883a4389e6aa80a675458bc'
    assert result['provenance']['wave_control_policy']=='projectmtv-core-2.3.15-live-wave-controls-v1'
    assert result['provenance']['equation_rng']['policy']==CORE_2321_EQUATION_RNG_POLICY


def test_core42_noise_uses_raw_declared_seed_repeatably(tmp_path,qualified_core42_adapters):
    rows=[]
    for i,seed in enumerate([3567620661,3567620661,3567620662]):
        out=tmp_path/str(i);request=tmp_path/f'request{i}.json';request.write_text(json.dumps(dict(
            names=['noise_lq_lite'],seed=seed,seed_policy='production-clock-seed-v1',output=str(out))))
        process=subprocess.run([str(BINARIES/'milk-noise-inputs'),str(request)],capture_output=True,text=True)
        assert process.returncode==0,process.stderr
        manifest=json.loads(process.stdout)
        assert manifest['textures']['noise_lq_lite']['generator_seed']==seed
        assert manifest['seed_model']=='raw-declared-native-noise-v1'
        rows.append((out/'noise_lq_lite.u32le').read_bytes())
    assert rows[0]==rows[1] and rows[0]!=rows[2]


def test_corrected_centre_policies_require_the_exact_2322_identity():
    import engine_profiles,forecast
    from composite_mesh import CORE_2322_CENTRES,LEGACY_CENTRES
    from primitives import CORE_2322_SHAPE_CENTRES,LEGACY_SHAPE_CENTRES
    expected={'commit':'6f64807467e312034883a4389e6aa80a675458bc',
        'patches_sha256':'3ade58a837591acde97d07a45f703d53047bbe0fc3993149bdfe0dd54298a381'}
    assert engine_profiles.CORE_2322_ENGINE==expected
    assert forecast.source_centre_policies(expected,{})==(CORE_2322_CENTRES,CORE_2322_SHAPE_CENTRES)
    assert forecast.source_centre_policies(engine_profiles.CORE_2321_ENGINE,{})==(LEGACY_CENTRES,LEGACY_SHAPE_CENTRES)
    with pytest.raises(ValueError,match='centre.*identity'):
        forecast.source_centre_policies(engine_profiles.CORE_2321_ENGINE,
            {'composite_centre_policy':CORE_2322_CENTRES})


def test_corrected_engine_keeps_unmodeled_high_resolution_guard(tmp_path,qualified_core42_adapters):
    import forecast
    path=tmp_path/'fixture.milk';path.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nfWaveAlpha=0\n')
    source=forecast.read_source(path,reader=BINARIES/'milk-native-reader')
    source['parser_inputs']['engine']=dict(forecast.CORE_2322_ENGINE)
    domain=dict(width=1920,height=1080,mesh_x=48,mesh_y=32,profile='gles300',
        initial_rgba=[0]*4,hue_offsets=[0]*4,equation_seed=0x4141f00d,blur_levels=0,quantize=True)
    with pytest.raises(ValueError,match='2.3.22 higher-resolution'):
        forecast.forecast_source(source,audio={},binaries=BINARIES,domain=domain,compatibility={})
