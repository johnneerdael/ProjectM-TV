import os
from pathlib import Path
import numpy as np
import pytest
from engine_profiles import CORE_2327_ENGINE


def settings(**updates):
    return {**dict(width=1920,height=1080,physical_size=[3840,2160],native_trails_level=0,
        authored_canvas_policy='projectmtv-authored-native-detail-v1',
        feedback_detail_resource_status='allocated',profile='gles300',quantize=True,
        line_rendering_profile='projectmtv-gles-quad-lines-v1',triangle_subpixel_bits=8,
        mesh_x=8,mesh_y=8,initial_rgba=[.2,.4,.6,1],hue_offsets=[0]*4,
        equation_seed=0x4141f00d,blur_levels=0),**updates}


def test_detail_context_requires_exact_engine_and_declared_allocated_resources():
    from forecast import forecast_detail_context
    result=forecast_detail_context(CORE_2327_ENGINE,settings())
    assert result['authored_size']==(960,540)
    assert result['initial_shader_canvas']==(1280,720)
    with pytest.raises(ValueError,match='engine'):
        forecast_detail_context({},settings())
    with pytest.raises(ValueError,match='allocation'):
        forecast_detail_context(CORE_2327_ENGINE,settings(feedback_detail_resource_status='unknown'))
    with pytest.raises(ValueError,match='gain'):
        forecast_detail_context(CORE_2327_ENGINE,settings(feedback_detail_alpha=1))
    with pytest.raises(ValueError,match='integer canvas'):
        forecast_detail_context(CORE_2327_ENGINE,settings(width=1921))


def test_full_forecaster_connects_init_canvas_and_native_display(tmp_path,monkeypatch):
    variable=os.environ.get('MILK_TEST_2327_BINARIES')
    if variable is None:pytest.skip('explicit prepared PR59 adapters required')
    folder=Path(variable)
    from forecast import read_source,forecast_source
    import test_native_audio
    preset=tmp_path/'declared.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nwarp=0\nfDecay=1\n'
        'fWaveAlpha=0\nfGammaAdj=1\nfVideoEchoAlpha=0\n'
        'per_frame_init_1=q1=pixelsx;\nper_frame_1=q2=pixelsx;\n')
    source=read_source(preset,reader=folder/'milk-native-reader')
    monkeypatch.setattr(test_native_audio,'BINARY',folder/'milk-audio-inputs')
    process,audio=test_native_audio.NativeAudioTest().run_audio(np.zeros(1470),frames=1)
    assert process.returncode==0,process.stderr
    report=forecast_source(source,audio=audio,binaries=folder,domain=settings(),compatibility={})
    frame=report['frames'][0]
    assert frame['display'].shape==(2160,3840,4)
    assert frame['feedback'].shape==(1080,1920,4)
    assert frame['history']['authored_canvas']==[960,540]
    assert frame['history']['warp_evaluated'] is False
    states=report['source_equation_states']['states'][0]
    assert states['q']['q1']==1280 and states['q']['q2']==960
    np.testing.assert_array_equal(frame['feedback'][100,100,:3],np.array([.2,.4,.6],np.float32))
    assert report['appearance_accuracy_verified'] is False
