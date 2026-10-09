"""Polar source maps retain radial/angle anchors and projection parameters."""
import math
import pytest
from test_source_sampling import maps


def test_native_reciprocal_projection_exports_scale_bias_and_audio_time_offsets():
    m=maps('ret=GetPixel(float2(ang/6.28+.1*bass,.2/(rad+.05)+time));')[0]
    p=m['polar_projection']
    assert p['kind']=='separable_angle_depth'
    assert p['coordinate_lanes']==['angle','depth']
    assert p['shared_anchor']['kind']=='native_rad_ang'
    assert p['angle']['input_scale']==pytest.approx(1/6.28)
    assert p['depth']['function']=='reciprocal'
    assert p['depth']['radius_scale']==1
    assert p['depth']['radius_bias']==pytest.approx(.05)
    assert p['depth']['output_scale']==pytest.approx(.2)
    assert p['depth']['offset_control']['signed_linear_rate_per_second']==1
    assert any(r['input_code']==1 for r in p['angle']['audio_routes'])
    assert p['appearance_guaranteed'] is False


def test_logarithmic_projection_preserves_base_and_swapped_lanes():
    p=maps('ret=GetPixel(float2(.3*log2(2*rad+.01),-ang*.2));')[0]['polar_projection']
    assert p['coordinate_lanes']==['depth','angle']
    assert p['depth']['function']=='log2'
    assert p['depth']['input_absolute'] is True
    assert p['depth']['domain_guard_retained'] is True
    assert p['depth']['radius_scale']==2
    assert p['depth']['radius_bias']==pytest.approx(.01)
    assert p['depth']['output_scale']==pytest.approx(.3)
    assert p['angle']['turn_span_uv']==pytest.approx(.2*math.tau)


def test_computed_polar_pair_exports_shared_elliptical_basis_and_centre():
    p=maps('float2 p=(uv-float2(.3,.7))*float2(2,1);'
        'ret=GetPixel(float2(atan2(p.y,p.x),1/length(p)));')[0]['polar_projection']
    assert p['shared_anchor']['kind']=='authored_affine_plane'
    assert p['shared_anchor']['matrix_uv4']==[[2,0,0,0],[0,1,0,0]]
    assert p['shared_anchor']['centre_in_basis_uv']==pytest.approx([.3,.7],abs=2e-7)


def test_different_polar_centres_do_not_form_a_shared_projection():
    p=maps('float2 p=uv-.5;float2 q=uv-.3;'
        'ret=GetPixel(float2(atan2(p.y,p.x),1/length(q)));')[0]['polar_projection']
    assert p['kind']=='unresolved'
    assert p['shared_anchor'] is None
    assert p['unknown_reasons']


@pytest.mark.parametrize('coordinate',['float2(ang,rad*rad)','float2(ang,bass/rad)',
    'float2(ang,log(rad+GetPixel(uv).r))','float2(ang,1/length(sin(uv)))'])
def test_unsupported_polar_expression_is_not_given_complete_parameters(coordinate):
    p=maps('ret=GetPixel('+coordinate+');')[0]['polar_projection']
    assert p['kind']=='unresolved'
    assert p['unknown_reasons']


def test_triangular_angle_fold_exports_nominal_period_not_rounded_symmetry():
    p=maps('ret=GetPixel(float2(abs(2*frac(ang/6.28*7+time*.05)-1),1/rad));')[0]['polar_projection']
    angle=p['angle']
    assert angle['function']=='triangular_frac'
    assert angle['input_scale']==pytest.approx(7/6.28,abs=2e-7)
    assert angle['angular_period_rad']==pytest.approx(6.28/7,abs=2e-7)
    assert angle['cycles_per_turn_nominal']==pytest.approx(math.tau*7/6.28,abs=2e-6)
    assert angle['exact_closed_turn_symmetry'] is None
    assert angle['offset_control']['signed_linear_rate_per_second']==pytest.approx(.05,abs=2e-7)


def test_cartesian_sample_has_no_invented_polar_profile():
    p=maps('ret=GetPixel(uv*.5);')[0]['polar_projection']
    assert p['kind']=='not_recognized'
    assert p['angle'] is None
    assert p['depth'] is None


def test_absolute_log_depth_keeps_negative_radius_scale():
    p=maps('ret=GetPixel(float2(ang,-.5*log(-2*rad+.3)));')[0]['polar_projection']
    assert p['kind']=='separable_angle_depth'
    assert p['depth']['radius_scale']==-2
    assert p['depth']['input_absolute'] is True
    assert p['depth']['output_scale']==-.5
    assert p['depth']['domain_condition']=='abs(radius_scale*r+radius_bias) > 0'


def test_same_centre_with_different_metrics_is_not_a_proved_shared_anchor():
    p=maps('float2 p=(uv-.5)*float2(2,1);float2 q=(uv-.5)*float2(3,1);'
        'ret=GetPixel(float2(atan2(p.y,p.x),1/length(q)));')[0]['polar_projection']
    assert p['kind']=='unresolved'
    assert p['shared_anchor'] is None


def test_distance_and_atan2_share_the_same_authored_plane():
    p=maps('float2 p=uv-.5;ret=GetPixel(float2(atan2(p.y,p.x),1/distance(uv,float2(.5,.5))));')[0]['polar_projection']
    assert p['kind']=='separable_angle_depth'
    assert p['shared_anchor']['centre_in_basis_uv']==[.5,.5]


def test_radial_gradients_describe_nominal_source_density_at_known_radii():
    cases=[('2/(3*rad+.1)',-6.,2,1.),('.5*log2(2*rad+.1)',1/math.log(2),1,math.log(2))]
    for code,coefficient,power,base in cases:
        depth=maps('ret=GetPixel(float2(ang,'+code+'));')[0]['polar_projection']['depth']
        derivative=depth['radial_derivative']
        assert derivative['coefficient']==pytest.approx(coefficient)
        assert derivative['denominator_power']==power
        r=.3;arg=derivative['radius_scale']*r+derivative['radius_bias']
        value=derivative['coefficient']/arg**power
        if power==2:expected=-6/(3*r+.1)**2
        else:expected=1/(math.log(2)*(2*r+.1))
        assert value==pytest.approx(expected,rel=2e-7)


def test_authored_uniform_cannot_collide_with_internal_atom_identity():
    from test_effect_families import shader
    from test_source_appearance import appearance
    source=shader('uniform float2 _polar_atom;shader_body {ret=GetPixel(float2(ang+_polar_atom.x,1/rad));}')
    p=appearance(source)['sampling_geometry']['stages']['composite'][0]['polar_projection']
    assert p['angle']['input_scale']==1
    assert p['angle']['offset_value'] is None


def test_dynamic_affine_plane_retains_shared_program_without_inventing_centre():
    p=maps('float2 p=(uv-.5)*aspect.xy;ret=GetPixel(float2(atan2(p.y,p.x),1/length(p)));')[0]['polar_projection']
    assert p['kind']=='separable_angle_depth'
    assert p['shared_anchor']['kind']=='authored_plane_program'
    assert p['shared_anchor']['matrix_uv4'] is None
    assert p['shared_anchor']['centre_in_basis_uv'] is None
    assert p['shared_anchor']['plane_expression']['complete'] is True


def test_polar_traversal_does_not_erase_existing_descriptor_on_complex_preset():
    from test_effect_families import read,PRESETS
    from test_source_appearance import appearance
    description=appearance(read((PRESETS/'flexi - grind my glitch up [191].milk').read_bytes()))
    assert 'sampling_geometry' in description
