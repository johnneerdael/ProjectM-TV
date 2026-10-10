"""Source native warp recipes do not render images or solve feedback state."""
import math
import hashlib
import numpy as np
import pytest
from test_effect_families import read,shader,analyze
from test_source_appearance import appearance


def recipe(body='',config=''):
    d=appearance(read('fWaveAlpha=0\n'+config+'per_frame_1='+body+'\n'))
    assert 'native_warp_recipe' in d, 'native source warp recipe is missing'
    return d['native_warp_recipe']


def apply(r,u,ax,ay,texel=(0,0)):
    p=r['native_float32_controls'];rotation=np.array(r['rotation_matrix'])
    q=np.array([ax*(u[0]-.5)/p['zoom']+( .5-p['cx']),ay*(u[1]-.5)/p['zoom']+(.5-p['cy'])])
    q/=np.array([p['sx'],p['sy']])
    q=rotation@q+np.array([p['cx']-p['dx']-.5,p['cy']-p['dy']-.5])
    return q/np.array([ax,ay])+.5+np.array(texel)


def test_identity_recipe_has_no_ideal_affine_displacement():
    r=recipe('zoom=1;zoomexp=1;warp=0;rot=0;dx=0;dy=0;sx=1;sy=1;')
    assert r['model_kind']=='uniform_affine'
    assert r['affine_component_identity'] is True
    assert apply(r,[.2,.7],1,.5625)==pytest.approx([.2,.7])
    assert r['visible_screen_motion'] is None


def test_constant_zoom_changes_feedback_each_step_without_parameter_variation():
    r=recipe('zoom=1.1;zoomexp=1;warp=0;rot=0;sx=1;sy=1;dx=0;dy=0;')
    assert r['affine_component_identity'] is False
    assert apply(r,[.2,.7],1,.5625)==pytest.approx([(.2-.5)/1.1+.5,(.7-.5)/1.1+.5],abs=2e-7)
    assert r['affine_area_ratio_source_to_output']==pytest.approx(1.1**2,abs=2e-7)


def test_source_recipe_matches_independent_ordered_aspect_transform():
    r=recipe('zoom=1.2;zoomexp=1;warp=0;rot=.3;sx=1.4;sy=.8;cx=.3;cy=.7;dx=.04;dy=-.02;')
    p=r['native_float32_controls']
    for ax,ay in [(1,1),(1,.5625),(.75,1)]:
        for u in ([.2,.7],[0,0],[1,1]):
            expected=apply(r,u,ax,ay)
            basis=np.array([1,ay/ax,ax/ay])
            matrix=np.array(r['matrix_uv_aspect_coefficients'])@basis
            ob=np.array([1,1/ax,1/ay,ay/ax,ax/ay])
            offset=np.array(r['offset_uv_aspect_coefficients'])@ob
            assert matrix@u+offset==pytest.approx(expected,abs=2e-12)


def test_native_wave_warp_exports_legacy_spatial_signs_and_amplitude_bounds():
    r=recipe('zoom=1;zoomexp=1;warp=.3;rot=0;sx=1;sy=1;')
    assert r['model_kind']=='uniform_native_wave_warp'
    waves=r['procedural_warp']
    assert waves['pre_rotation_displacement_bound_each_axis']==pytest.approx(2*.3*.0035,abs=2e-9)
    assert waves['uv_source_position_convention']=='pos=2*original_uv-1; legacy warp reverses oscillator y signs'
    assert waves['terms'][0]['phase_position_factor_coefficients']==[[1,0,0,0],[0,0,0,1]]
    assert waves['terms'][1]['phase_position_factor_coefficients']==[[0,0,-1,0],[0,1,0,0]]


def test_emitted_float32_controls_are_preserved_before_recipe_math():
    r=recipe('zoom=1.00000001;zoomexp=1;warp=0;rot=0;sx=1;sy=1;')
    assert r['native_float32_controls']['zoom']==1
    assert r['affine_component_identity'] is True


@pytest.mark.parametrize('body',[
    'zoom=1;zoomexp=1.2;warp=0;',
    'zoom=0;zoomexp=1;warp=0;',
    'zoom=1;zoomexp=1;warp=0;sx=0;',
    'zoom=bass;zoomexp=1;warp=0;',
    'zoom=1;zoomexp=1;warp=0;rot=1e40;',
])
def test_nonuniform_dynamic_singular_or_nonfinite_controls_remain_unknown(body):
    r=recipe(body)
    assert r['model_kind']=='unknown'
    assert r['unknown_reasons']


def test_negative_uniform_zoom_uses_current_signed_power_policy():
    r=recipe('zoom=-1;zoomexp=1;warp=0;rot=0;sx=1;sy=1;')
    assert r['model_kind']=='uniform_affine'
    assert apply(r,[.2,.7],1,.5625)==pytest.approx([.8,.3])


def test_zero_warp_does_not_hide_invalid_warp_scale_inverse():
    r=recipe('zoom=1;zoomexp=1;warp=0;',config='fWarpScale=0\n')
    assert r['model_kind']=='unknown'
    assert r['unknown_reasons']


def test_texel_offset_is_declared_not_silently_zeroed():
    r=recipe('zoom=1;zoomexp=1;warp=0;rot=0;sx=1;sy=1;')
    assert r['texel_offset_uv_is_runtime_input'] is True
    assert apply(r,[.2,.7],1,.5625,texel=(.001,.002))==pytest.approx([.201,.702])


def test_disconnected_mesh_does_not_claim_contributing_warp():
    r=appearance(shader('shader_body {ret=float3(1,0,0);}'))['native_warp_recipe']
    assert r['model_kind']=='not_contributing'
    assert r['matrix_uv_aspect_coefficients'] is None


def test_neutral_scale_with_offcenter_rotation_is_not_identity():
    r=recipe('zoom=-1;zoomexp=1;warp=0;sx=-1;sy=-1;cx=.2;cy=.3;')
    assert r['affine_component_identity'] is False


def test_procedural_recipe_matches_legacy_four_term_nominal_math():
    r=recipe('zoom=1;zoomexp=1;warp=.3;rot=0;sx=1;sy=1;')
    w=r['procedural_warp']
    for t in (0,.7,3):
        f=np.array([row['bias']+row['amplitude']*math.cos(t*row['time_coefficient']+row['phase_offset'])
                    for row in w['warp_factors']])
        for pos in ([.2,-.4],[-1,1]):
            actual=np.zeros(2)
            for term in w['terms']:
                phase=t*term['time_coefficient']+w['warp_scale_inverse']*(np.array(pos)@np.array(term['phase_position_factor_coefficients'])@f)
                actual['uv'.index(term['axis'])]+=w['signed_term_amplitude']*getattr(math,term['function'])(phase)
            rates=[term['time_coefficient'] for term in w['terms']]
            x,y=pos;ws=w['warp_scale_inverse'];a=w['signed_term_amplitude']
            expected=[a*(math.sin(t*rates[0]+ws*(x*f[0]+y*f[3]))+math.cos(t*rates[2]-ws*(x*f[1]+y*f[2]))),
                      a*(math.cos(t*rates[1]-ws*(x*f[2]-y*f[1]))+math.sin(t*rates[3]+ws*(x*f[0]-y*f[3])))]
            assert actual==pytest.approx(expected,abs=1e-15)
            assert max(abs(actual))<=w['pre_rotation_displacement_bound_each_axis']


@pytest.mark.parametrize('accepted,branch,first_y',[(True,'custom',-1),(False,'legacy',1),(None,'unknown',None)])
def test_selected_native_shader_branch_controls_warp_signs(accepted,branch,first_y):
    source=read('fWaveAlpha=0\nPSVERSION_WARP=2\nper_frame_1=zoom=1;zoomexp=1;warp=.3;\nwarp_1=`shader_body {ret=GetPixel(uv);}\n')
    code=source['sections']['warp_']['source']
    evidence={'source_sha256':hashlib.sha256(code.encode()).hexdigest(),
              'request':{'code':code,'stage':'warp','profile':'gles300'},
              'translation':{'engine_archive_sha256':source['parser_inputs']['engine_archive_sha256']},
              'offline_accepted':accepted}
    r=analyze(source,compatibility={'warp':evidence})['visual_description']['native_warp_recipe']
    assert r['shader_branch']==branch
    if accepted is None:
        assert r['model_kind']=='unknown'
        assert r['unknown_reasons']
    else:
        assert r['procedural_warp']['terms'][0]['phase_position_factor_coefficients'][1][3]==first_y


@pytest.mark.parametrize('center,dx',[(1e20,.03),(.5,1e-20)])
def test_neutral_recipe_center_offset_does_not_cancel_translation(center,dx):
    r=recipe(f'zoom=1;zoomexp=1;warp=0;sx=1;sy=1;rot=0;cx={center};cy=.5;dx={dx};dy=0;')
    assert r['offset_uv_aspect_coefficients'][0][1]==pytest.approx(-r['native_float32_controls']['dx'],rel=1e-12,abs=0)
