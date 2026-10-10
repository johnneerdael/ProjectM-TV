"""Native mesh feedback displacement must reach mesh-UV texture lookups."""
import math
import pytest
from test_effect_families import read
from test_source_appearance import appearance


def record(body,lookup='uv',config=''):
    s=read('fWaveAlpha=0\n'+config+'per_frame_1=zoomexp=1;warp=0;'+body+'\n'
        'warp_1=`shader_body {ret=tex2D(sampler_pw_main,'+lookup+').rgb;}\n')
    d=appearance(s)
    return d,d['activity']['motion_intensity']['native_lookup_transport'][0]


def evaluate(r,ax=1,ay=1):
    t=r['rms_lookup_displacement_uv_upper_bound_terms']
    v=t['aspect_corrected_native_terms']
    native=v['translation_and_center']+v['centered_geometry']*math.hypot(ax,ay)+v['procedural_warp']
    return native*(t['matrix_gain_terms']['inverse_aspect_x']/ax+t['matrix_gain_terms']['inverse_aspect_y']/ay)


def test_constant_zoom_has_native_lookup_displacement_not_zero_time_drift():
    d,r=record('zoom=1.01;rot=0;')
    assert evaluate(r)>0
    assert r['feedback_step_unit']=='source_texture_uv/feedback_step'
    assert r['visible_screen_speed'] is None
    assert d['sampling_geometry']['stages']['warp'][0]['sampling_motion']['maximum_lookup_axis_speed_uv_per_second']==[0,0]


def test_identity_excluding_texel_alignment_has_zero_native_displacement():
    d,r=record('zoom=1;rot=0;dx=0;dy=0;sx=1;sy=1;')
    assert evaluate(r)==0
    assert r['texel_alignment_included'] is False


def test_shader_scaling_scales_native_lookup_displacement():
    _,base=record('zoom=1;rot=0;dx=.03;dy=-.04;')
    _,scaled=record('zoom=1;rot=0;dx=.03;dy=-.04;','2*uv')
    assert evaluate(scaled)==pytest.approx(2*evaluate(base),rel=1e-12)


def test_original_uv_bypasses_native_mesh_transport():
    d,r=record('zoom=1.01;rot=0;','uv_orig')
    assert r['native_mesh_contribution']=='bypassed'
    assert r['rms_lookup_displacement_uv_upper_bound_terms'] is None


def test_dynamic_uniform_zoom_domain_propagates_into_lookup():
    _,r=record('zoom=1.1+.02*sin(time);rot=.01*sin(time);')
    assert r['native_mesh_contribution']=='bounded'
    assert evaluate(r)>0


def test_singular_mesh_domain_does_not_publish_lookup_bound():
    _,r=record('zoom=0;rot=.02;')
    assert r['native_mesh_contribution']=='unknown'
    assert r['rms_lookup_displacement_uv_upper_bound_terms'] is None


def test_nearest_main_lookup_has_possible_native_feedback_jump_source():
    d,r=record('zoom=1.01;rot=0;')
    assert any(h['kind']=='nearest_native_feedback_displacement' for h in d['activity']['flashing']['hazards'])


def test_lookup_transport_bound_covers_independent_grid_displacement():
    import numpy as np
    d,r=record('zoom=1.2;sx=1.3;sy=.8;rot=.3;cx=.3;cy=.7;dx=.04;dy=-.02;',
               'float2(2*uv.x+.5*uv.y,-uv.x+3*uv.y)')
    p=d['native_warp_displacement']['native_float32_controls']
    R=np.array([[math.cos(p['rot']),-math.sin(p['rot'])],[math.sin(p['rot']),math.cos(p['rot'])]])
    shader_map=np.array([[2,.5],[-1,3]])
    grid=(np.arange(80)+.5)/80-.5;u,v=np.meshgrid(grid,grid)
    for ax,ay in ((1,1),(1,.5625),(.75,1)):
        point=np.stack([ax*u,ay*v],axis=-1)
        rel=(point/p['zoom']+np.array([.5-p['cx'],.5-p['cy']]))/np.array([p['sx'],p['sy']])
        native=rel@R.T+np.array([p['cx']-p['dx']-.5,p['cy']-p['dy']-.5])
        delta=((native-point)/np.array([ax,ay]))@shader_map.T
        actual=math.sqrt(np.mean(np.sum(delta**2,axis=-1)))
        assert actual<=evaluate(r,ax,ay)


def test_known_invalid_shader_offset_cannot_certify_native_transport():
    _,r=record('zoom=1.01;rot=0;','uv+float2(time/0,0)')
    assert r['native_mesh_contribution']=='unknown'


def test_external_nearest_texture_alone_does_not_claim_feedback_jump():
    s=read('per_frame_1=zoomexp=1;warp=0;zoom=1.01;\nwarp_1=`shader_body {ret=tex2D(sampler_pw_noise_lq,uv).rgb;}\n')
    d=appearance(s)
    assert not any(h['kind']=='nearest_native_feedback_displacement' for h in d['activity']['flashing']['hazards'])


def test_mixed_original_and_warped_map_only_propagates_mesh_columns():
    _,base=record('zoom=1.01;rot=0;')
    _,mixed=record('zoom=1.01;rot=0;','uv+uv_orig*7')
    assert evaluate(mixed)==pytest.approx(evaluate(base),rel=1e-12)


def test_column_norm_handles_extreme_values_without_finite_claim():
    from source_native_lookup_transport import _norm_upper
    assert _norm_upper([1e308,1e308]) is None
    assert _norm_upper([1e-300,1e-300]) is None
