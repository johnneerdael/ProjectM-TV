import pytest
import test_native_reader


def test_current_core_retries_only_rejected_per_frame_records():
    from equation_loading import select_equation
    source=test_native_reader.NativeReaderTest().read('per_frame_1=q1=is_\nper_frame_2=beat*.2;\n')
    section=source['sections']['per_frame_']
    strict=select_equation(section,'per_frame_',policy='strict-raw-v1')
    current=select_equation(section,'per_frame_',policy='projectmtv-core-2.2.6-v1')
    assert strict['compile_status']=='rejected'
    assert current['compile_status']=='accepted'
    assert current['assembly']=='legacy-retry'
    assert current['code']==section['assembled_source']


@pytest.mark.parametrize('prefix',['per_frame_init_','per_pixel_','wave_0_per_frame','shape_0_per_frame'])
def test_current_core_does_not_extend_retry_to_other_phases(prefix):
    from equation_loading import select_equation
    source=test_native_reader.NativeReaderTest().read(prefix+'1=q1=is_\n'+prefix+'2=beat*.2;\n')
    assert select_equation(source['sections'][prefix],prefix,policy='projectmtv-core-2.2.6-v1')['compile_status']=='rejected'


def test_current_core_preserves_raw_accepted_program():
    from equation_loading import select_equation
    source=test_native_reader.NativeReaderTest().read('per_frame_1=q1=2;\nper_frame_2=q2=3;\n')
    section=source['sections']['per_frame_']
    chosen=select_equation(section,'per_frame_',policy='projectmtv-core-2.2.6-v1')
    assert chosen['assembly']=='raw'
    assert chosen['code']==section['source']


def test_unknown_policy_is_not_silently_assumed():
    from equation_loading import select_equation
    with pytest.raises(ValueError,match='policy'):
        select_equation({},'per_frame_',policy='latest')


def test_pipeline_current_policy_does_not_reject_the_shipped_per_frame_retry():
    import numpy as np
    from pipeline_fields import SourcePipeline
    source=test_native_reader.NativeReaderTest().read('per_frame_1=q1=is_\nper_frame_2=beat*.2;\n')
    pipeline=SourcePipeline.from_source(source,profile='gles300',compatibility={},
        equation_loader_policy='projectmtv-core-2.2.6-v1',initial_feedback=np.zeros((4,4,4)),
        warp_reads_blur=False,blur_levels=0)
    assert pipeline.equation_loader_policy=='projectmtv-core-2.2.6-v1'


def test_current_policy_audit_accepts_only_the_shipped_phase():
    import hashlib
    from coverage_audit import audit_source
    for prefix,accepted in [('per_frame_',True),('per_pixel_',False)]:
        raw=(prefix+'1=q1=is_\n'+prefix+'2=beat*.2;\n').encode()
        cache=test_native_reader.NativeReaderTest().read(raw.decode())
        cache.update(preset_sha256=hashlib.sha256(raw).hexdigest(),reader_sha256='reader')
        report=audit_source(raw,cache=cache,reader_sha='reader',equation_loader_policy='projectmtv-core-2.2.6-v1')
        assert report['units'][0]['target_parsed']==accepted


def test_scene_executes_selected_retry_and_records_policy():
    from scene_equations import execute_scene
    from test_scene_equations import frames
    source=test_native_reader.NativeReaderTest().read('per_frame_1=is_beat=2;q1=is_\nper_frame_2=beat;\n')
    result=execute_scene(source,frames()[:1],reader=test_native_reader.READER,mesh_x=8,mesh_y=8,
                         equation_loader_policy='projectmtv-core-2.2.6-v1')
    assert result['frames'][0]['main']['q1']==2
    assert result['equation_loader_policy']=='projectmtv-core-2.2.6-v1'


def test_pipeline_cannot_treat_unknown_equation_compilation_as_success():
    import numpy as np
    from pipeline_fields import SourcePipeline
    from field_math import UnresolvedMath
    source=test_native_reader.NativeReaderTest().read('per_frame_1=q1=2;\n')
    source['sections']['per_frame_'].pop('projectm_native_compile_status')
    with pytest.raises(UnresolvedMath,match='compatibility unresolved'):
        SourcePipeline.from_source(source,profile='gles300',compatibility={},
            equation_loader_policy='projectmtv-core-2.2.6-v1',initial_feedback=np.zeros((4,4,4)),
            warp_reads_blur=False,blur_levels=0)


def test_raw_execution_request_does_not_silently_join_records():
    with pytest.raises(AssertionError,match='compile error'):
        test_native_reader.NativeReaderTest().execute(
            {'frame':{'code':'is_beat=2;q1=is_\nbeat;','assembly':'raw'}},[])

# Original pre0030 regression controls; current-profile behavior is tested separately.
pytestmark = pytest.mark.historical_profile("legacy_pre30")
