"""Periodic coordinate preimages are not verified visible copy counts."""
import math
import numpy as np
import pytest
from test_source_sampling import maps


def lattice(body,stage='composite'):
    m=maps(body,stage)[0]
    assert 'copy_lattice' in m, 'periodic coordinate-copy descriptor is missing'
    return m['copy_lattice']


def test_scale_two_repeat_has_half_unit_generators_and_density_four():
    c=lattice('ret=GetPixel((uv-.5)*2+.5);')
    assert c['status']=='conditional_periodic_preimages'
    assert c['lattice_basis_uv']==[[.5,0],[0,.5]]
    assert c['origin_for_source_feature_zero_uv']==[.25,.25]
    assert c['fundamental_cell_area_uv2']==pytest.approx(.25)
    assert c['nominal_lattice_points_per_unit_uv_area']==pytest.approx(4)
    assert c['actual_visible_copy_count'] is None


def test_reflected_repeat_keeps_signed_generators():
    c=lattice('ret=GetPixel(float2(1-2*uv.x,2*uv.y));')
    assert c['lattice_basis_uv']==[[-.5,0],[0,.5]]
    assert c['orientation_reversed'] is True


def test_sheared_lattice_reconstructs_equal_wrapped_source_locations():
    c=lattice('ret=GetPixel(float2(2*uv.x+.5*uv.y+.1,-uv.x+3*uv.y-.2));')
    inv=np.array(c['lattice_basis_uv']);origin=np.array(c['origin_for_source_feature_zero_uv'])
    matrix=np.array([[2,.5],[-1,3]]);offset=np.array([.1,-.2]);feature=np.array([.2,.3])
    for shift in ([0,0],[1,0],[-1,2]):
        p=inv@(feature+shift)+origin
        assert matrix@p+offset==pytest.approx(feature+shift,abs=3e-7)
    assert c['nominal_lattice_points_per_unit_uv_area']==pytest.approx(6.5)


def test_clamped_sampler_has_no_periodic_preimage_lattice():
    c=lattice('ret=tex2D(sampler_fc_main,uv*2).xyz;')
    assert c['status']=='not_periodic'
    assert c['lattice_basis_uv'] is None


def test_singular_map_does_not_invent_point_lattice():
    c=lattice('ret=GetPixel(float2(uv.x,.5));')
    assert c['status']=='unknown'
    assert c['lattice_basis_uv'] is None


def test_mixed_warp_bases_keep_physical_lattice_unresolved():
    c=lattice('ret=GetPixel(uv+uv_orig*.5);','warp')
    assert c['status']=='unknown'
    assert c['lattice_basis_uv'] is None


def test_warp_mesh_precedes_shader_basis_and_prevents_screen_claim():
    c=lattice('ret=GetPixel(uv*2);','warp')
    assert c['native_mesh_transform_precedes_basis'] is True
    assert c['actual_visible_copy_count'] is None
    assert c['visible_screen_motion'] is None


def test_dynamic_offset_keeps_origin_formula_and_source_translation_speed():
    c=lattice('ret=GetPixel(uv*2+float2(.1*time,.2*time));')
    assert c['origin_for_source_feature_zero_uv'] is None
    assert c['origin_from_offset_matrix']==[[-.5,0],[0,-.5]]
    assert c['origin_velocity_uv_per_source_second']==pytest.approx([-.05,-.1])
    assert c['origin_speed_uv_per_source_second_upper_bound']==pytest.approx(math.hypot(.05,.1))
    assert c['origin_speed_estimate_kind']=='exact_nominal'


def test_oscillating_offset_has_upper_bound_not_exact_speed():
    c=lattice('ret=GetPixel(uv*2+float2(.1*sin(time),.2*cos(time)));')
    assert c['origin_velocity_uv_per_source_second'] is None
    assert c['origin_speed_uv_per_source_second_upper_bound']==pytest.approx(math.hypot(.05,.1))
    assert c['origin_speed_estimate_kind']=='upper_bound'


def test_unknown_audio_offset_keeps_lattice_but_not_origin_speed():
    c=lattice('ret=GetPixel(uv*2+float2(.1*bass,0));')
    assert c['lattice_basis_uv'] is not None
    assert c['origin_speed_uv_per_source_second_upper_bound'] is None
    assert c['origin_speed_estimate_kind']=='unknown'


def test_unknown_wrap_context_is_conditional_not_assumed_enabled():
    from source_copy_lattice import copy_lattice
    m=maps('ret=GetPixel(uv*2);')[0]
    m['sampling_policy']['wrap']=None;m['sampling_policy']['wrap_condition']='frame_wrap > .0001'
    c=copy_lattice(m)
    assert c['status']=='conditional_on_repeat_wrap'
    assert c['wrap_enabled'] is None
    assert c['wrap_condition']=='frame_wrap > .0001'


def test_dead_alpha_only_sample_does_not_add_copy_lattice():
    assert maps('ret=float4(.1,.2,.3,GetPixel(uv*2).r);')==[]


def test_origin_speed_underflow_does_not_claim_stationary_origin():
    from source_copy_lattice import copy_lattice
    m=maps('ret=GetPixel(uv);')[0]
    m['inverse_matrix']=[[1e-200,0],[0,1e-200]]
    m['determinant']=1e200
    m['offset_controls'][0].update(curve_kind='linear_time',signed_linear_rate_per_second=1e-200,maximum_absolute_control_rate_per_second=1e-200)
    c=copy_lattice(m)
    assert c['origin_speed_uv_per_source_second_upper_bound'] is None
    assert c['unknown_reasons']


def test_nonfinite_inverse_has_no_lattice_or_speed_certificate():
    from source_copy_lattice import copy_lattice
    m=maps('ret=GetPixel(uv);')[0]
    m['inverse_matrix']=[[float('inf'),0],[0,1]]
    c=copy_lattice(m)
    assert c['lattice_basis_uv'] is None
    assert c['unknown_reasons']
