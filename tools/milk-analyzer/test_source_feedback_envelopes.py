"""Dynamic affine-in-sample colour bounds; no image/history samples."""
import math
import numpy as np
import pytest
from test_effect_families import shader,read
from test_source_appearance import appearance


def envelope(code):
    d=appearance(shader('shader_body {'+code+'}',stage='warp'))
    assert 'feedback_envelope' in d,'dynamic feedback colour envelope missing'
    return d['feedback_envelope']


def test_time_varying_weight_has_gain_bound_not_point_gain():
    r=envelope('ret=GetPixel(uv)*(.5+.1*sin(time));')
    assert r['source_model']=='bounded_affine_main_sample_colour'
    assert r['maximum_colour_difference_gain']==pytest.approx(.6,abs=2e-7)
    assert r['sufficient_contraction_bound'] is True
    assert r['ideal_perturbation_half_life_upper_bound_evaluations']==pytest.approx(math.log(.5)/math.log(.6),rel=1e-5)
    assert r['actual_feedback_persistence'] is None


def test_signed_independent_sites_use_absolute_gain_not_net_cancellation():
    r=envelope('ret=GetPixel(uv)*(.5+.1*sin(time))-GetPixel(uv*.5)*.2;')
    assert r['maximum_colour_difference_gain']==pytest.approx(.8,abs=2e-7)
    assert len(r['sample_contributions'])==2


def test_audio_weight_bound_does_not_gain_audio_timing():
    r=envelope('ret=GetPixel(uv)*(.5+.1*sin(bass));')
    assert r['source_model']=='bounded_affine_main_sample_colour'
    assert r['maximum_colour_difference_gain']==pytest.approx(.6,abs=2e-7)
    assert r['assumed_finite_input_names']


def test_dynamic_offset_has_unit_sample_envelope_without_changed_gain():
    r=envelope('ret=GetPixel(uv)*.4+.1*sin(time);')
    assert np.array(r['raw_rgb_bounds_if_samples_unit_interval'])==pytest.approx(np.array([[-.1,.5]]*3),abs=1e-7)
    assert r['maximum_colour_difference_gain']==pytest.approx(.4,abs=1e-7)


def test_image_driven_coordinates_keep_contraction_unknown():
    r=envelope('ret=GetPixel(uv+GetPixel(uv).rg*.1)*(.5+.1*sin(time));')
    assert r['maximum_colour_difference_gain'] is not None
    assert r['coordinate_feedback_dependency'] is True
    assert r['sufficient_contraction_bound'] is None


@pytest.mark.parametrize('code',[
 'ret=GetPixel(uv)*GetPixel(uv);',
 'ret=GetPixel(uv)*bass;',
 'ret=pow(GetPixel(uv),2);',
 'ret=GetPixel(uv)/sin(time);',
 'ret=GetBlur1(uv)*.5;',
])
def test_nonlinear_unbounded_singular_or_blur_history_stays_unknown(code):
    r=envelope(code)
    assert r['source_model']=='unknown'
    assert r['maximum_colour_difference_gain'] is None
    assert r['unknown_reasons']


def test_dynamic_q_coefficient_uses_narrowed_main_source_envelope():
    d=appearance(read('fWaveAlpha=0\nper_frame_1=q1=.5+.1*sin(time);\nwarp_1=`shader_body {ret=GetPixel(uv)*q1;}\n'))
    r=d['feedback_envelope']
    assert r['maximum_colour_difference_gain']==pytest.approx(.6,abs=2e-7)


def test_dynamic_fixed_warp_decay_uses_native_upper_clamp_without_zero_fill():
    d=appearance(read('fWaveAlpha=0\nper_frame_1=decay=.9+.2*sin(time);\n'))
    assert d['feedback_envelope']['maximum_colour_difference_gain']==pytest.approx(1,abs=1e-7)
    assert d['feedback_envelope']['sufficient_contraction_bound'] is False


def test_duplicate_same_sample_path_combines_coefficients_before_bounding():
    r=envelope('float3 c=GetPixel(uv);ret=c*.5-c*.2;')
    assert r['maximum_colour_difference_gain']==pytest.approx(.3,abs=1e-7)


def test_dynamic_q_upload_overflow_cannot_gain_finite_feedback_envelope():
    d=appearance(read('fWaveAlpha=0\nper_frame_1=q1=1e40*sin(time);\nwarp_1=`shader_body {ret=GetPixel(uv)*q1;}\n'))
    r=d['feedback_envelope']
    assert r['source_model']=='unknown'
    assert r['maximum_colour_difference_gain'] is None


def test_fixed_decay_native_overflow_stays_unknown_before_upper_clamp():
    d=appearance(read('fWaveAlpha=0\nper_frame_1=decay=1e40*sin(time);\n'))
    assert d['feedback_envelope']['source_model']=='unknown'


def test_explicit_derived_scalar_domain_is_preserved_as_a_premise():
    from source_control_bounds import scalar_value_envelope
    from shader_fields import Field
    r=scalar_value_envelope(Field('input',detail={'name':'x'}),input_domains={'x':[.2,.4]})
    assert r['nominal_value_range']==[.2,.4]
    assert r['declared_input_domains']=={'x':[.2,.4]}


def test_invalid_declared_scalar_domain_is_unknown_not_a_finite_bound():
    from source_control_bounds import scalar_value_envelope
    from shader_fields import Field
    r=scalar_value_envelope(Field('input',detail={'name':'x'}),input_domains={'x':[1,0]})
    assert r['nominal_value_range'] is None
    assert r['unknown_reasons']
