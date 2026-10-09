"""Raw texture-colour mixtures, not certified final palette/feedback dynamics."""
import numpy as np
import pytest
from test_effect_families import shader,read,PRESETS
from test_source_appearance import appearance


def mix(body,stage='comp'):
    return appearance(shader('shader_body{'+body+'}',stage=stage))['texture_colour_transfer']['stages']['composite' if stage=='comp' else stage]


def test_positive_main_blur_mix_exports_signed_weights_and_raw_bias():
    r=mix('ret=GetPixel(uv)*.7+GetBlur1(uv)*.3+float3(.1,0,0);')
    assert r['source_model']=='affine_sample_colour'
    assert r['constant_offset_rgb']==pytest.approx([.1,0,0],abs=2e-8)
    assert {s['canonical_texture'] for s in r['sample_contributions']}=={'main','blur1'}
    assert r['source_mixture_kind']=='nonnegative_main_blur_mix'
    assert r['direct_colour_gain_norm']==pytest.approx(1,abs=2e-7)
    assert r['final_palette_verified'] is False


def test_main_minus_blur_keeps_contrast_candidate_conditional():
    r=mix('ret=GetPixel(uv)*1.2-GetBlur1(uv)*.2;')
    assert r['source_mixture_kind']=='signed_main_blur_mix'
    assert r['direct_colour_gain_norm']==pytest.approx(1.4,abs=2e-7)
    assert r['actual_sharpness'] is None
    assert r['actual_feedback_persistence'] is None


def test_swizzled_channel_mix_preserves_rgba_columns():
    r=mix('ret=tex2D(sampler_main,uv).bgr*float3(.5,.6,.7);')
    matrix=np.array(r['sample_contributions'][0]['matrix_rgb_rgba'])
    assert matrix==pytest.approx(np.array([[0,0,.5,0],[0,.6,0,0],[.7,0,0,0]]),abs=2e-7)


def test_uniform_offsets_remain_programs_without_inventing_rgb_constants():
    r=mix('ret=GetPixel(uv)+bass*.1;')
    assert r['source_model']=='affine_sample_colour'
    assert r['constant_offset_rgb']==[None,None,None]
    assert r['offset_expressions']


@pytest.mark.parametrize('body',['ret=GetPixel(uv)*bass;','ret=pow(GetPixel(uv),2);',
    'ret=GetPixel(uv)*GetBlur1(uv);','ret=float3(int(GetPixel(uv).r),0,0);'])
def test_dynamic_nonlinear_quantized_colour_cannot_claim_constant_transfer(body):
    r=mix(body)
    assert r['source_model']=='unknown'
    assert r['direct_colour_gain_norm'] is None


def test_nested_sample_coordinates_do_not_grant_closed_loop_gain():
    r=mix('ret=GetPixel(uv+GetBlur1(uv).rg*.1)*.8;')
    assert r['coordinate_sample_dependency'] is True
    assert r['direct_colour_gain_norm']==pytest.approx(.8,abs=2e-7)
    assert r['full_colour_sensitivity'] is None


def test_warp_vertex_colour_binding_resolves_only_consumed_lanes():
    r=mix('ret=GetPixel(uv)*_vDiffuse.rgb;',stage='warp')
    assert r['source_model']=='affine_sample_colour'
    assert r['direct_colour_gain_norm']==pytest.approx(.98,abs=2e-7)


def test_original_hue_burst_explains_affine_warp_mix_and_keeps_composite_unknown():
    d=appearance(read((PRESETS/'Flexi - hue burst.milk').read_bytes()))['texture_colour_transfer']['stages']
    assert d['warp']['source_model']=='affine_sample_colour'
    assert {'main','blur1','blur3','noise_lq'} <= {s['canonical_texture'] for s in d['warp']['sample_contributions']}
    assert d['composite']['source_model']=='unknown'


def test_composite_vertex_colour_is_not_replaced_with_warp_decay():
    r=mix('ret=GetPixel(uv)*hue_shader;')
    assert r['source_model']=='unknown'


def test_dynamic_warp_decay_keeps_rgb_unknown_but_alpha_one_known():
    source=read('per_frame_1=decay=bass;\nPSVERSION_WARP=2\nwarp_1=`shader_body{ret=GetPixel(uv)*_vDiffuse.rgb;}\n')
    d=appearance(source)
    assert d['texture_colour_transfer']['stages']['warp']['source_model']=='unknown'
    source=read('per_frame_1=decay=bass;\nPSVERSION_WARP=2\nwarp_1=`shader_body{ret=GetPixel(uv)*_vDiffuse.a;}\n')
    d=appearance(source)
    assert d['texture_colour_transfer']['stages']['warp']['direct_colour_gain_norm']==1
