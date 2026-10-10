"""Conditional ripple envelopes bound coordinates, not perceived intensity."""
import pytest
from test_source_periodic_sampling import warp


def envelope(code):
    r=warp(code)
    assert 'deformation_envelope' in r
    return r['deformation_envelope']


def test_bounded_uniform_time_amplitude_supplies_displacement_and_gradient_bounds():
    e=envelope('ret=GetPixel(uv+float2(.02*sin(time)*sin(uv.y*8),0));')
    assert e['maximum_absolute_displacement_uv']==pytest.approx([.02,0],abs=2e-8)
    assert e['jacobian_perturbation_infinity_norm_upper_bound']==pytest.approx(.16,abs=2e-8)
    assert e['identity_no_fold_sufficient'] is True
    assert e['visible_motion_intensity'] is None


def test_bounded_dynamic_frequency_is_not_assumed_constant():
    e=envelope('ret=GetPixel(uv+float2(.02*sin(uv.y*(3+sin(time))),0));')
    assert e['jacobian_perturbation_infinity_norm_upper_bound']==pytest.approx(.08,abs=2e-8)
    assert e['identity_no_fold_sufficient'] is True


def test_unbounded_audio_amplitude_keeps_displacement_unknown():
    e=envelope('ret=GetPixel(uv+float2(.02*bass*sin(uv.y*8),0));')
    assert e['maximum_absolute_displacement_uv']==[None,0]
    assert e['jacobian_perturbation_infinity_norm_upper_bound'] is None
    assert e['identity_no_fold_sufficient'] is None


def test_unknown_frequency_does_not_erase_bounded_displacement():
    e=envelope('ret=GetPixel(uv+float2(.02*sin(uv.y*bass),0));')
    assert e['maximum_absolute_displacement_uv']==pytest.approx([.02,0],abs=2e-8)
    assert e['jacobian_perturbation_infinity_norm_upper_bound'] is None


def test_mixed_basis_withholds_uv_jacobian_but_retains_output_coordinate_amplitude():
    e=envelope('ret=GetPixel(uv+float2(.02*sin(rad+uv.x),0));')
    assert e['maximum_absolute_displacement_uv']==pytest.approx([.02,0],abs=2e-8)
    assert e['jacobian_perturbation_infinity_norm_upper_bound'] is None


def test_nonidentity_baseline_withholds_identity_certificate():
    e=envelope('ret=GetPixel(uv*2+float2(.02*sin(time)*sin(uv.y*8),0));')
    assert e['jacobian_perturbation_infinity_norm_upper_bound'] is not None
    assert e['identity_no_fold_sufficient'] is None


def test_coefficient_bounds_retain_native_upload_domain_guards():
    from shader_fields import Field
    from source_ripple_envelopes import coefficient_envelope
    large=Field('multiply',(Field('constant',detail={'value':1e40}),Field('sin',(Field('input',detail={'name':'time'}),))))
    f=Field('narrow',(large,),'float',{'numeric_domain':'shader-float32'})
    r=coefficient_envelope(f)
    assert r['nominal_value_range'] is None
    assert r['unknown_reasons']


def test_coefficient_narrowing_range_covers_rounded_upload_endpoints():
    import numpy as np
    from shader_fields import Field
    from source_ripple_envelopes import coefficient_envelope
    field=Field('multiply',(Field('constant',detail={'value':.1}),Field('sin',(Field('input',detail={'name':'time'}),))))
    r=coefficient_envelope(Field('narrow',(field,),'float',{'numeric_domain':'shader-float32'}))
    lo,hi=r['nominal_value_range']
    assert lo<=float(np.float32(-.1)) and hi>=float(np.float32(.1))
    assert 'time' in r['assumed_finite_input_names']


def test_unrepresentable_gradient_bound_does_not_erase_displacement():
    from source_periodic_sampling import number
    from source_ripple_envelopes import deformation_envelope
    e=deformation_envelope([{'amplitude':[number(1e308),number(0)],
                            'gradient':[number(1e308)]+[number(0)]*5}],basis='shader_uv',identity_baseline=True)
    assert e['maximum_absolute_displacement_uv']==[1e308,0]
    assert e['jacobian_perturbation_infinity_norm_upper_bound'] is None
    assert e['identity_no_fold_sufficient'] is None


def test_positive_gradient_underflow_rounds_outward_not_to_stationary():
    from source_periodic_sampling import number
    from source_ripple_envelopes import deformation_envelope
    e=deformation_envelope([{'amplitude':[number(1e-300),number(0)],
                            'gradient':[number(1e-300)]+[number(0)]*5}],basis='shader_uv',identity_baseline=True)
    assert e['jacobian_perturbation_infinity_norm_upper_bound']>0
