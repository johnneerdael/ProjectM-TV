"""Source band generators preserve their basis and conditional appearance."""
import math
import pytest
from test_effect_families import shader,analyze
from test_source_appearance import appearance


def bands(body,stage='comp'):
    d=appearance(shader('shader_body {'+body+'}',stage=stage))
    return [f for e in d['elements'] for f in e.get('procedural_forms',[])
            if f['form_code']==10]


def test_planar_bands_export_normal_period_and_phase_motion():
    f=bands('ret=.5+.5*sin(uv.x*8+time);')[0]
    assert f['construction']=='planar_oscillatory_bands'
    assert f['phase_coefficients']==[8,0,0,0]
    assert f['phase_normal_uv']==[1,0]
    assert f['nominal_period_in_basis_units']==pytest.approx(math.tau/8)
    assert f['phase_motion_control']['signed_linear_rate_per_second']==1
    assert f['actual_screen_coverage'] is None
    assert f['appearance_guaranteed'] is False


def test_diagonal_dot_phase_preserves_orientation_and_bass_phase_route():
    f=bands('ret=cos(dot(uv,float2(3,4))+.2*bass);')[0]
    assert f['phase_normal_uv']==pytest.approx([.6,.8])
    assert f['nominal_period_in_basis_units']==pytest.approx(math.tau/5)
    assert any(r['control']=='band_phase' and r['input_code']==1 for r in f['audio_routes'])


def test_native_radius_bands_keep_radial_varying_basis_not_exact_circle_claim():
    f=bands('ret=.5+.5*cos(rad*20+time);')[0]
    assert f['construction']=='native_radius_oscillatory_bands'
    assert f['basis']=='native_radial_varying'
    assert f['nominal_period_in_basis_units']==pytest.approx(math.tau/20)
    assert f['phase_normal_uv'] is None


def test_original_uv_bands_keep_warp_mesh_bypass_distinct():
    f=bands('ret=sin(uv_orig.y*12);',stage='warp')[0]
    assert f['basis']=='original_uv'
    assert f['phase_coefficients']==[0,0,0,12]


@pytest.mark.parametrize('body',[
    'ret=sin(time);',
    'ret=sin(bass);',
    'ret=sin(uv.x*0+time);',
    'ret=sin(uv.x*bass);',
    'ret=sin(uv.x*uv.x);',
    'ret=sin(ang*5);',
    'ret=sin(GetPixel(uv).x);',
    'ret=float4(1,0,0,sin(uv.x*8));',
    'ret=sin(uv.x*8)*0;',
    'float dead=sin(uv.x*8);ret=GetPixel(uv);',
])
def test_uniform_dynamic_nonaffine_angular_image_driven_and_dead_terms_abstain(body):
    record=analyze(shader('shader_body {'+body+'}'))
    assert not any(f['mechanism']=='spatial_oscillatory_bands' for f in record['families'])


def test_repeated_identical_generator_is_not_a_layer_count():
    fs=bands('float a=sin(uv.x*8);ret=a+a;')
    assert len(fs)==1
    assert fs[0]['record_semantics'].startswith('canonical contributing generator')


def test_opposite_phase_keeps_signed_normal():
    f=bands('ret=cos(-uv.x*8);')[0]
    assert f['phase_normal_uv']==[-1,0]


def test_mixed_uv_and_radius_angle_phase_do_not_invent_single_spacing():
    assert bands('ret=sin(uv.x+uv_orig.y);',stage='warp')==[]
    assert bands('ret=sin(rad+ang);')==[]


def test_coordinate_only_sine_displacement_is_not_a_colour_band_generator():
    assert bands('ret=GetPixel(uv+.02*sin(uv.y*8));')==[]


def test_shared_generator_reaching_colour_and_coordinates_retains_colour_form():
    assert len(bands('float b=sin(uv.y*8);ret=GetPixel(uv+.02*b)+b;'))==1


@pytest.mark.parametrize('body',[
    'ret=clamp(sin(uv.x*8),1,1);',
    'ret=saturate(2+sin(uv.x*8));',
    'ret=min(2+sin(uv.x*8),0);',
    'ret=max(sin(uv.x*8),2);',
])
def test_proved_complete_clipping_suppresses_contributing_band_claim(body):
    assert bands(body)==[]


def test_partial_clipping_keeps_raw_generator_not_final_period_claim():
    assert len(bands('ret=saturate(.5+.8*sin(uv.x*8));'))==1


@pytest.mark.parametrize('offset',['1./0.','pow(0,-1)','log(0)'])
def test_known_singular_phase_offsets_do_not_claim_usable_bands(offset):
    assert bands('ret=sin(uv.x*8+'+offset+');')==[]


def test_native_abs_root_lowering_remains_usable_in_phase():
    assert len(bands('ret=sin(uv.x*8+sqrt(-1.));'))==1
