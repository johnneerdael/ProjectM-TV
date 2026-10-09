"""Nominal time rates through typed vector projection; no sampled frames."""
import pytest

from shader_fields import Field
from source_temporal import affine_time_parameters


def scalar(value):
    return Field('constant',dtype='float',detail={'value':value})


def time_input():
    return Field('input',dtype='float',detail={'name':'time'})


def lane(parent,name):
    return Field('member',(parent,),'float',{'field':name,'swizzle':True})


@pytest.mark.parametrize('op',['components','construct'])
def test_projected_time_vector_keeps_selected_rate_and_offset(op):
    t=Field('add',(Field('multiply',(time_input(),scalar(2.)),'float'),scalar(.25)),'float')
    v=Field(op,(scalar(7.),t),'float2')
    assert affine_time_parameters(lane(v,'y'))==(2.,.25)


def test_nested_swizzle_keeps_time_lane_order():
    v=Field('components',(time_input(),scalar(3.)),'float2')
    swap=Field('member',(v,),'float2',{'field':'yx','swizzle':True})
    assert affine_time_parameters(lane(swap,'y'))==(1.,0.)


def test_vector_arithmetic_projects_before_deriving_time_rate():
    v=Field('components',(time_input(),scalar(4.)),'float2')
    scales=Field('components',(scalar(-3.),scalar(8.)),'float2')
    assert affine_time_parameters(lane(Field('multiply',(v,scales),'float2'),'x'))==(-3.,0.)


def test_unselected_audio_lane_does_not_hide_independent_time_lane():
    v=Field('components',(time_input(),Field('input',dtype='float',detail={'name':'bass'})),'float2')
    assert affine_time_parameters(lane(v,'x'))==(1.,0.)
    assert affine_time_parameters(lane(v,'y')) is None


@pytest.mark.parametrize('parent',[
    Field('input',dtype='float2',detail={'name':'state'}),
    Field('sample',dtype='float4',detail={'canonical_texture':'main'}),
    Field('unknown',dtype='float2'),
])
def test_unresolved_vector_projection_retains_unknown_rate(parent):
    assert affine_time_parameters(lane(parent,'x')) is None


def test_projected_dynamic_integer_conversion_is_not_affine_time():
    quantized=Field('cast',(time_input(),),'int')
    v=Field('construct',(quantized,scalar(0.)),'float2')
    assert affine_time_parameters(lane(v,'x')) is None


def test_projected_literal_narrowing_preserves_float32_offset():
    v=Field('construct',(time_input(),Field('narrow',(scalar(.1),),'float')),'float2')
    assert affine_time_parameters(lane(v,'y'))==(0.,0.10000000149011612)


def test_actual_shader_projected_phase_exports_palette_timing():
    import math
    from test_effect_families import shader
    from test_source_appearance import appearance
    d=appearance(shader('shader_body{float2 phase=float2(time*2+.25,bass);'
                        'ret=.5+.5*cos(phase.x+float3(0,2,4));}'))
    timing=d['elements'][0]['colour']['temporal']
    assert timing['angular_rate_rad_per_second_rgb']==[2.,2.,2.]
    assert timing['period_seconds_rgb']==pytest.approx([math.pi]*3)
    assert timing['visible_flash_frequency_hz'] is None


@pytest.mark.parametrize('op',['cast','narrow','construct'])
def test_overflowing_float32_literal_is_not_a_finite_affine_coefficient(op):
    overflow=Field(op,(scalar(1e100),),'float')
    assert affine_time_parameters(overflow) is None
    formula=Field('multiply',(time_input(),overflow),'float')
    assert affine_time_parameters(formula) is None


def test_projected_overflowing_literal_remains_unknown():
    overflow=Field('narrow',(scalar(1e100),),'float')
    vector=Field('components',(overflow,time_input()),'float2')
    assert affine_time_parameters(lane(vector,'x')) is None
    assert affine_time_parameters(lane(vector,'y'))==(1.,0.)


def test_overflowing_authored_vector_formula_retains_unknown_timing():
    from test_effect_families import shader
    from test_source_appearance import appearance
    d=appearance(shader('shader_body{ret=.5+.5*cos(time*float(1e30*1e30)+float3(0,2,4));}'))
    for element in d['elements']:
        timing=element['colour'].get('temporal')
        if timing is not None:
            assert timing['angular_rate_rad_per_second_rgb']==[None,None,None]


def test_uniform_literal_conversion_abstains_on_float_overflow():
    from effect_families import _uniform_scalar_conversion
    assert _uniform_scalar_conversion(1e100,'float3') is None
    assert _uniform_scalar_conversion(.5,'float3')==.5


@pytest.mark.parametrize('op',['cast','narrow'])
def test_source_literal_folder_does_not_erase_failed_same_base_conversion(op):
    from effect_families import _number
    assert _number(Field(op,(scalar(1e100),),'float')) is None
    assert _number(Field(op,(scalar(.1),),'float'))==0.10000000149011612


@pytest.mark.parametrize('body',[
    'ret=GetPixel(uv)*((float)(1e30*1e30)-(1e30*1e30));',
    'float a=(float)(1e30*1e30);ret=GetPixel(uv)*(a-a);',
    'ret=GetPixel(uv)*((1e30*1e30)-(1e30*1e30));',
])
def test_overflow_cancellation_cannot_remove_feedback_dependencies(body):
    from test_effect_families import shader
    from test_source_appearance import appearance
    d=appearance(shader('shader_body{'+body+'}'))
    assert d['composition']['shader_sample_reads']['composite']


def test_authored_shader_literal_arithmetic_keeps_float32_rounding():
    from test_effect_families import shader
    from test_source_appearance import appearance
    d=appearance(shader('shader_body{ret=(1.0+.1)-1.0;}'))
    assert d['elements'][0]['colour']['constant_rgb']==[0.10000002384185791]*3


def test_plain_eel_literal_arithmetic_remains_double():
    from source_appearance import _phase_literal
    expr=Field('subtract',(Field('add',(scalar(1.),scalar(.1)),'float'),scalar(1.)),'float')
    assert _phase_literal(expr)==(1.+.1)-1.


@pytest.mark.parametrize('body',[
    'float a=1.;a+=.1;a-=1.;ret=a;',
    'float3 a=float3(1,1,1);a+=.1;a-=1.;ret=a;',
])
def test_shader_compound_arithmetic_keeps_float32_rounding(body):
    from test_effect_families import shader
    from test_source_appearance import appearance
    d=appearance(shader('shader_body{'+body+'}'))
    assert d['elements'][0]['colour']['constant_rgb']==[0.10000002384185791]*3


def test_compound_shader_overflow_cannot_remove_feedback_dependencies():
    from test_effect_families import shader
    from test_source_appearance import appearance
    d=appearance(shader('shader_body{float a=1e30;a*=1e30;ret=GetPixel(uv)*(a-a);}'))
    assert d['composition']['shader_sample_reads']['composite']


def test_shader_post_increment_keeps_float32_precision():
    from test_effect_families import shader
    from test_source_appearance import appearance
    d=appearance(shader('shader_body{float a=16777216.;a++;ret=a-16777216.;}'))
    assert d['elements'][0]['colour']['constant_rgb']==[0.]*3


def test_exported_time_formula_retains_its_arithmetic_domain():
    from source_appearance import _expression
    expr=Field('multiply',(time_input(),scalar(2.)),'float',{'numeric_domain':'shader-float32'})
    nodes=_expression(expr)['nodes']
    assert nodes[0]['detail']['numeric_domain']=='shader-float32'
    assert 'numeric_domain' not in _expression(Field('multiply',expr.args,'float'))['nodes'][0]['detail']


def test_exported_explicit_cast_preserves_source_conversion_identity():
    from source_appearance import _expression
    expr=Field('cast',(time_input(),),'float',{'target_type':'float','explicit_source_cast':True})
    assert _expression(expr)['nodes'][0]['detail']['explicit_source_cast'] is True
