"""Main-frame Q snapshots into shader uniforms; no equations are executed."""
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def desc(main,code='ret=float3(q1,q5,q32);',pixel='',init=''):
    return appearance(read('fWaveAlpha=0\n'+init+'per_frame_1='+main+'\n'+pixel+'comp_1=`shader_body {'+code+'}\n'))


def test_constant_q_lanes_bind_all_eight_banks_to_shader_colour():
    d=desc('q1=.2;q5=.3;q32=.4;')
    e=next(e for e in d['elements'] if e['id']=='shader_composite')
    assert e['colour']['constant_rgb']==pytest.approx([.2,.3,.4],abs=2e-8)
    assert 'main_frame_q' in d['native_input_bindings']
    c=d['native_input_bindings']['main_frame_q']
    assert len(c['lanes'])==32
    assert c['lanes']['q32']['packed_uniform']=='_qh'
    assert c['lanes']['q32']['component']==3


def test_float32_q_upload_happens_after_double_equation_expression():
    d=desc('q1=16777217;',code='ret=q1;')
    e=next(e for e in d['elements'] if e['id']=='shader_composite')
    assert e['colour']['constant_rgb']==[1]*3 # descriptive RGB clips; the binding retains raw uploaded value
    assert d['native_input_bindings']['main_frame_q']['lanes']['q1']['native_float32_constant']==16777216


def test_shader_snapshot_does_not_use_pixel_mutated_q():
    d=desc('q1=.2;',code='ret=q1;',pixel='per_pixel_1=q1=q1+.1;\n')
    e=next(e for e in d['elements'] if e['id']=='shader_composite')
    assert e['colour']['constant_rgb']==pytest.approx([.2]*3,abs=1e-8)


def test_main_q_reloads_init_snapshot_before_each_frame():
    d=desc('q1=q1+.1;',code='ret=q1;',init='per_frame_init_1=q1=.2;\n')
    e=next(e for e in d['elements'] if e['id']=='shader_composite')
    assert e['colour']['constant_rgb']==pytest.approx([.3]*3,abs=2e-8)


def test_dynamic_q_retains_source_program_and_unknown_value():
    d=desc('q1=.5+.5*sin(bass);',code='ret=q1;')
    lane=d['native_input_bindings']['main_frame_q']['lanes']['q1']
    assert lane['native_float32_constant'] is None
    assert lane['source_expression']['nodes']
    assert lane['input_dependencies']==['bass']
    e=next(e for e in d['elements'] if e['id']=='shader_composite')
    assert e['colour']['constant_rgb'] is None
    assert any(r['input_code']==1 for r in e['audio_routes'])


def test_native_q_overflow_is_not_zero_or_a_finite_shader_constant():
    d=desc('q1=1e40;',code='ret=q1;')
    lane=d['native_input_bindings']['main_frame_q']['lanes']['q1']
    assert lane['native_float32_constant'] is None
    assert lane['binding_status']=='unknown'
    e=next(e for e in d['elements'] if e['id']=='shader_composite')
    assert e['colour']['constant_rgb'] is None


def test_local_q_macro_shadow_stays_local_and_does_not_rebind_uniform():
    d=desc('q1=.2;',code='float4 _qa=float4(.7,0,0,0);ret=q1;')
    e=next(e for e in d['elements'] if e['id']=='shader_composite')
    assert e['colour']['constant_rgb']==pytest.approx([.7]*3,abs=1e-7)


def test_grind_original_keeps_structured_description_without_budget_increase():
    from pathlib import Path
    source=Path(__file__).resolve().parents[2]/'core/src/main/assets/presets/flexi - grind my glitch up [191].milk'
    d=appearance(read(source.read_bytes()))
    assert 'native_input_bindings' in d
    assert len(d['native_input_bindings']['main_frame_q']['lanes'])==32
