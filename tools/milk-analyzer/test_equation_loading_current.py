from analyzer_test_profiles import historical_source
import pytest
from equation_loading import select_equation

from test_native_reader import READER


def source(body):
    return historical_source('merged35', ('MILKDROP_PRESET_VERSION=201\n'+body).encode())


@pytest.mark.parametrize('prefix',['per_frame_init_','per_pixel_','wave_0_per_frame','shape_0_per_frame'])
def test_current_core_retries_all_equation_phases(prefix):
    s=source(prefix+'1=q1=is_\n'+prefix+'2=beat;\n')
    selected=select_equation(s['sections'][prefix],prefix,policy='projectmtv-core-2.2.8-v1')
    assert selected['compile_status']=='accepted'
    assert selected['assembly']=='legacy-retry'


def test_lone_dot_is_compiled_as_zero_by_current_native_evaluator():
    s=source('per_pixel_1=zoom=1+.;\n')
    selected=select_equation(s['sections']['per_pixel_'],'per_pixel_',policy='projectmtv-core-2.2.8-v1')
    assert selected['compile_status']=='accepted'
    assert selected['assembly']=='raw'


def test_genuinely_bad_block_is_omitted_with_warning_and_no_fake_parse():
    s=source('per_frame_init_1=q1=;\n')
    selected=select_equation(s['sections']['per_frame_init_'],'per_frame_init_',policy='projectmtv-core-2.2.8-v1')
    assert selected['compile_status']=='omitted'
    assert selected['assembly']=='omitted'
    assert selected['code']=='0;'
    assert selected['tree_status']=='unknown'
    assert selected['warning']


def test_current_policy_cannot_borrow_old_assembly_evidence():
    section={'projectm_native_compile_status':'rejected','compile_status':'accepted','status':'parsed',
             'source':'q1=is_\nbeat;','assembled_source':'q1=is_beat;','tree':{},
             'target_assembly_policy':'milkdrop-records-v1'}
    assert select_equation(section,'per_frame_',policy='projectmtv-core-2.2.8-v1')['compile_status']=='unknown'


def test_omitted_init_executes_zero_defaults_and_retains_warning():
    from scene_equations import execute_scene
    from test_scene_equations import frames
    s=source('per_frame_init_1=q1=;\nper_frame_1=q2=q1+1;\n')
    result=execute_scene(s,frames()[:1],reader=READER,mesh_x=8,mesh_y=8,
                         equation_loader_policy='projectmtv-core-2.2.8-v1')
    assert result['frames'][0]['main']['q1']==0
    assert result['frames'][0]['main']['q2']==1
    assert result['equation_warnings'][0]['section']=='per_frame_init_'


def test_omission_keeps_original_tokens_without_parsing_credit():
    import hashlib
    from coverage_audit import audit_source
    from gap_priority import rank_gaps
    raw=b'per_frame_init_1=q1=;\n';s=source(raw.decode())
    s.update(preset_sha256=hashlib.sha256(raw).hexdigest(),reader_sha256='reader')
    report=audit_source(raw,cache=s,reader_sha='reader',equation_loader_policy='projectmtv-core-2.2.8-v1')
    assert report['code_tokens']>0
    assert report['parsed_code_tokens']==0
    report.update(preset='test.milk',preset_sha256=s['preset_sha256'])
    assert rank_gaps([report])['presets_with_known_gaps']==0
    assert report['units'][0]['equation_loading']['warning']


def test_old_retry_cannot_borrow_new_parenthesis_semicolon_rule():
    s=source('per_frame_1=q1=sin(1;*2);\n')
    section=s['sections']['per_frame_']
    assert select_equation(section,'per_frame_',policy='projectmtv-core-2.2.8-v1')['compile_status']=='accepted'
    assert select_equation(section,'per_frame_',policy='projectmtv-core-2.2.6-v1')['compile_status']=='unknown'

pytestmark = pytest.mark.historical_profile("merged35")
