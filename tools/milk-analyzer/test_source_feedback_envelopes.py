"""Dynamic affine-in-sample colour bounds; no image/history samples."""
import math
import numpy as np
import pytest
from test_effect_families import shader,read
from test_source_appearance import appearance


def test_feedback_memo_retains_synthetic_canonical_nodes_during_the_analysis(monkeypatch):
    """Nested swizzles manufacture nodes whose IDs must not be recycled."""
    import weakref
    from types import SimpleNamespace
    import source_appearance
    from source_feedback_envelopes import feedback_envelope
    from shader_fields import Field
    canonical=source_appearance._canonical_lane
    temporary=[]
    def observe(node):
        # Entries in the helper's identity memo remain live until it returns.
        assert all(ref() is not None for ref in temporary)
        result=canonical(node)
        if result is not node:temporary.append(weakref.ref(result))
        return result
    monkeypatch.setattr(source_appearance,'_canonical_lane',observe)
    uv=Field('input',dtype='float4',detail={'name':'_uv'})
    sample=Field('sample',(uv,),'float4',{'canonical_texture':'main','site_index':1})
    rgb=Field('member',(sample,),'float3',{'field':'rgb','swizzle':True})
    lanes=tuple(Field('member',(rgb,),'float',{'field':lane,'swizzle':True}) for lane in 'rgb')
    analysis=SimpleNamespace(outputs={'warp':Field('components',lanes,'float3')},
        stages={'warp':{'kind':'custom_warp'}})
    result=feedback_envelope(analysis)
    assert temporary
    assert result['source_model']=='bounded_affine_main_sample_colour'


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


def test_four_independent_blur_samples_keep_every_site_and_its_coefficient():
    r=envelope('ret=.25*(GetPixel(uv)+GetPixel(uv+.01)+GetPixel(uv+.02)+GetPixel(uv-.03))-.01;')
    assert len(r['sample_contributions'])==4
    assert r['maximum_colour_difference_gain']==pytest.approx(1.,abs=1e-7)
    for site in r['sample_contributions']:
        expected=[[[.25,.25] if i==j else [0.,0.] for j in range(3)] for i in range(3)]
        assert site['matrix_rgb_coefficient_ranges']==expected


def test_external_noise_offset_cannot_borrow_a_previous_main_sample_answer():
    r=envelope('ret=GetPixel(uv)+tex2D(sampler_noise_lq,uv).rgb*.01;')
    assert r['source_model']=='unknown'
    assert r['maximum_colour_difference_gain'] is None
    assert r['sample_contributions']==[]


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
