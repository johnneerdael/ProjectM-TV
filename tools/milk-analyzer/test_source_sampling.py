"""Source sampling maps describe texture lookup, not certified visible motion."""
import pytest
from test_effect_families import shader
from test_source_appearance import appearance


def maps(body,stage='composite'):
    return appearance(shader('shader_body {'+body+'}',stage='comp' if stage=='composite' else stage))['sampling_geometry']['stages'][stage]


def test_scaled_copy_exports_sampling_and_inverse_feature_transform():
    m=maps('ret=GetPixel((uv-.5)*2+.5);')[0]
    assert m['matrix_uv4']==[[2,0,0,0],[0,2,0,0]]
    assert m['offset_uv']==[-.5,-.5]
    assert m['basis']=='shader_uv'
    assert m['inverse_matrix']==[[.5,0],[0,.5]]
    assert m['inverse_offset_uv']==[.25,.25]
    assert m['nominal_feature_area_ratio']==.25
    assert m['visible_screen_motion'] is None


def test_reflection_and_permutation_keep_negative_orientation():
    m=maps('ret=GetPixel(float2(1-uv.y,uv.x));')[0]
    assert m['matrix_uv4']==[[0,-1,0,0],[1,0,0,0]]
    assert m['orientation_reversed'] is False
    reflected=maps('ret=GetPixel(float2(1-uv.x,uv.y));')[0]
    assert reflected['orientation_reversed'] is True
    assert reflected['inverse_offset_uv']==[1,0]


def test_warp_original_coordinates_remain_separate_from_mesh_uv():
    m=maps('ret=GetPixel(uv_orig*.5);','warp')[0]
    assert m['basis']=='original_uv'
    assert m['matrix_uv4']==[[0,0,.5,0],[0,0,0,.5]]
    assert m['native_mesh_transform_precedes_basis'] is False
    m=maps('ret=GetPixel(uv*.5);','warp')[0]
    assert m['native_mesh_transform_precedes_basis'] is True


def test_mixed_original_and_mesh_uv_cannot_invent_a_single_basis_inverse():
    m=maps('ret=GetPixel(uv+uv_orig*.5);','warp')[0]
    assert m['basis']=='mixed_uv'
    assert m['matrix_uv4']==[[1,0,.5,0],[0,1,0,.5]]
    assert m['inverse_matrix'] is None


def test_source_translation_retains_band_route_and_time_rate():
    m=maps('ret=GetPixel(uv+float2(.1*bass,.2*time));')[0]
    assert m['matrix_uv4']==[[1,0,0,0],[0,1,0,0]]
    assert m['offset_uv']==[None,None]
    assert m['offset_controls'][1]['signed_linear_rate_per_second']==pytest.approx(.2)
    route=m['audio_routes'][0]
    assert route['input_code']==1
    assert route['control']=='sample_offset_x'
    assert route['linear_gain']==pytest.approx(.1)
    assert m['inverse_offset_uv'] is None


@pytest.mark.parametrize('coordinate',['uv*uv','sin(uv)','float2(int(uv.x),uv.y)',
    'uv*bass','uv+GetPixel(uv).rg','float2(rad,ang)'])
def test_nonaffine_or_dynamic_scale_cannot_export_a_constant_map(coordinate):
    records=maps('ret=GetPixel('+coordinate+');')
    m=records[0]
    assert m['matrix_uv4'] is None
    assert m['unknown_reasons']
    assert m['inverse_matrix'] is None


def test_singular_copy_has_known_map_without_inverse_or_area_claim():
    m=maps('ret=GetPixel(float2(uv.x,.5));')[0]
    assert m['matrix_uv4']==[[1,0,0,0],[0,0,0,0]]
    assert m['determinant']==0
    assert m['inverse_matrix'] is None
    assert m['nominal_feature_area_ratio'] is None


def test_multiple_samples_keep_distinct_copy_sites_and_policies():
    records=maps('ret=GetPixel(uv)*.5+GetPixel(uv*2)*.5;')
    assert len(records)==2
    assert records[0]['sample_site_index']!=records[1]['sample_site_index']
    assert records[0]['matrix_uv4']!=records[1]['matrix_uv4']
    assert all(r['sampling_policy'] for r in records)


def test_dead_rgb_sample_is_not_described_as_visible_copy():
    assert maps('ret=float4(.1,.2,.3,GetPixel(uv*2).r);')==[]


def test_composite_vertex_colour_is_not_a_spatially_uniform_translation():
    m=maps('ret=GetPixel(uv+.1*hue_shader.rg);')[0]
    assert m['matrix_uv4'] is None
    assert m['unknown_reasons']


def test_affine_map_matches_inverse_at_independent_coordinate_points():
    import numpy as np
    m=maps('ret=GetPixel(float2(2*uv.x+.5*uv.y+.1,-uv.x+3*uv.y-.2));')[0]
    matrix=np.array(m['matrix_uv4'])[:,:2];offset=np.array(m['offset_uv'])
    inverse=np.array(m['inverse_matrix']);inv_offset=np.array(m['inverse_offset_uv'])
    for p in ([-.3,.7],[0,0],[.25,.8],[1.3,-.2]):
        source=matrix@p+offset
        assert inverse@source+inv_offset==pytest.approx(p,abs=2e-7)
    assert m['nominal_feature_area_ratio']==pytest.approx(1/6.5)


def test_scalar_swizzles_of_vector_arithmetic_keep_affine_map():
    m=maps('float2 p=(uv-float2(.3,.7))*float2(2,1);ret=GetPixel(float2(p.y,p.x));')[0]
    assert m['matrix_uv4']==[[0,1,0,0],[2,0,0,0]]
    assert m['offset_uv']==pytest.approx([-.7,-.6],abs=2e-7)


def test_constant_matrix_lookup_respects_vector_matrix_argument_order():
    left=maps('ret=GetPixel(mul(uv,float2x2(1,2,3,4)));')[0]
    right=maps('ret=GetPixel(mul(float2x2(1,2,3,4),uv));')[0]
    assert left['matrix_uv4']==[[1,3,0,0],[2,4,0,0]]
    assert right['matrix_uv4']==[[1,2,0,0],[3,4,0,0]]


def test_dynamic_matrix_lookup_cannot_be_folded_from_unbound_input_defaults():
    m=maps('ret=GetPixel(mul(uv,float2x2(_qa)));')[0]
    assert m['matrix_uv4'] is None
    assert m['unknown_reasons']
