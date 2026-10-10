"""Frozen mathematical prominence controls; no raster frames or audio samples."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile

import pytest


def evidence(body='', *, composite='ret=GetPixel(uv);', viewport=(1920,1080), config='', compiled=True, shader_version=2):
    import effect_families as ef
    from source_appearance import appearance_from_analysis
    import source_prominence
    raw=('MILKDROP_PRESET_VERSION=201\n[preset00]\nfWaveAlpha=0\n'
         'PSVERSION_COMP='+str(shader_version)+'\ncomp_1=`shader_body {'+composite+'}\n'
         'shapecode_0_enabled=1\nshapecode_0_sides=4\nshapecode_0_rad=.5\n'
         'shapecode_0_a=1\nshapecode_0_a2=1\nshapecode_0_border_a=0\n'+config+
         'shape_0_per_frame1='+body+'\n').encode()
    reader=Path(__file__).resolve().parents[2]/'build/preset-corpus/source34/adapters/milk-native-reader'
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'control.milk';path.write_bytes(raw)
        source=json.loads(subprocess.check_output([str(reader),str(path)]))
    source['preset_sha256']=hashlib.sha256(raw).hexdigest()
    source['parser_inputs']['setting_lookup_policy']='native-case-insensitive-v1'
    code=source['sections']['comp_']['source']
    compatibility={'composite':{'source_sha256':hashlib.sha256(code.encode()).hexdigest(),
        'request':{'code':code,'stage':'composite','profile':'gles300'},
        'translation':{'engine_archive_sha256':source['parser_inputs']['engine_archive_sha256']},
        'offline_accepted':True}}
    token=ef._CACHE.set({})
    try:
        analysis=ef._Analysis(source,'gles300',compatibility if compiled else None);analysis.input_scenario=None
        analysis.main_equations();analysis.primitives()
        analysis.shader('warp','warp_');analysis.shader('composite','comp_');analysis.contribution_gates()
        description=appearance_from_analysis(analysis)
        result=source_prominence.prominence_evidence(analysis,description,{'viewport':list(viewport),'feedback_fps':30})
    finally:ef._CACHE.reset(token)
    json.dumps(result,allow_nan=False)
    return result['by_component']['shape_0'],result


def test_shape_radius_is_ndc_and_horizontal_aspect_uses_actual_viewport():
    square,_=evidence(viewport=(1080,1080))
    wide,_=evidence()
    portrait,_=evidence(viewport=(1080,1920))
    assert square['support']['area_fraction_interval']==pytest.approx([.125,.125])
    assert wide['support']['area_fraction_interval']==pytest.approx([.125*9/16]*2)
    assert portrait['support']['area_fraction_interval']==pytest.approx([.125,.125])
    assert wide['visible_contrast_interval'][0]==0


def test_half_clipped_polygon_has_half_area_and_offscreen_has_zero():
    centered,_=evidence()
    clipped,_=evidence('x=0;')
    offscreen,_=evidence('x=-2;')
    expected=centered['support']['area_fraction_interval'][1]/2+(.5/math.sqrt(2))/1920/2
    assert clipped['support']['area_fraction_interval']==pytest.approx([expected]*2)
    assert offscreen['support']['area_fraction_interval']==[0,0]
    assert offscreen['displayed_contribution_interval']==[0,0]


def test_viewport_covering_polygon_and_tiny_polygon_keep_quantified_extent():
    large,_=evidence('rad=10;')
    tiny,_=evidence('rad=.001;')
    assert large['support']['area_fraction_interval']==[1,1]
    assert tiny['source_contribution_interval'][1]==pytest.approx(.001**2/2*9/16)
    assert tiny['displayed_contribution_interval'][1]<.00001


def test_transparent_fill_is_zero_but_visible_border_remains_possible():
    transparent,_=evidence('a=0;a2=0;')
    border,_=evidence('a=0;a2=0;border_a=1;')
    assert transparent['displayed_contribution_interval']==[0,0]
    assert border['displayed_contribution_interval'][1]>0
    assert border['unknown_reasons']


def test_coincident_instances_do_not_sum_union_coverage_above_one():
    single,_=evidence()
    repeated,_=evidence(config='shapecode_0_num_inst=20\n')
    assert repeated['support']['area_fraction_interval']==single['support']['area_fraction_interval']
    assert repeated['source_contribution_interval'][1]<=1
    assert repeated['support']['summed_nominal_area_fraction']>1


def test_separated_instance_overlap_union_has_safe_bounds():
    row,_=evidence('x=.1+.04*instance;',config='shapecode_0_num_inst=20\n')
    assert 0<row['support']['area_fraction_interval'][0]<=row['support']['area_fraction_interval'][1]<=1


def test_translucent_separated_instances_do_not_multiply_summed_area_twice():
    row,_=evidence('x=.1+.04*instance;a=.1;a2=.1;',config='shapecode_0_num_inst=20\n')
    assert row['source_contribution_interval'][1]<=row['support']['summed_clipped_area_fraction_upper']*.100001


@pytest.mark.parametrize('gain',[.01,.5,2])
def test_later_pointwise_composite_transfer_attenuates_or_amplifies(gain):
    row,_=evidence(composite='ret=GetPixel(uv)*'+str(gain)+';')
    assert row['final_transfer']['difference_gain_interval'][1]==pytest.approx(gain)
    assert row['displayed_contribution_interval'][1]==pytest.approx(row['displayed_support_fraction_interval'][1]*min(1,gain))


def test_amplification_of_translucent_fill_is_not_clamped_to_input_alpha():
    row,_=evidence('a=.1;a2=.1;',composite='ret=GetPixel(uv)*2;')
    baseline,_=evidence('a=.1;a2=.1;')
    assert row['displayed_contribution_interval'][1]==pytest.approx(baseline['displayed_contribution_interval'][1]*2)


def test_constant_composite_disconnects_configured_drawing():
    row,_=evidence(composite='ret=float3(.3,.4,.5);')
    assert row['final_transfer']['difference_gain_interval']==[0,0]
    assert row['displayed_contribution_interval']==[0,0]


def test_resampling_tiny_source_can_cover_display_and_history_stays_unknown():
    row,result=evidence('rad=.001;',composite='ret=GetPixel(float2(.5,.5));')
    assert row['displayed_support_fraction_interval']==[0,1]
    assert row['displayed_contribution_interval'][1]==pytest.approx(1)
    assert row['feedback_contribution_interval']==[0,1]
    assert result['uses_rendered_images'] is False


def test_saturated_affine_composite_independent_output_is_zero():
    row,_=evidence(composite='ret=saturate(GetPixel(uv)+2);')
    assert row['displayed_contribution_interval']==[0,0]
    assert 'saturation' in row['final_transfer']['method']


@pytest.mark.parametrize('composite',['ret=pow(GetPixel(uv),.5);','ret=GetPixel(uv)*bass;'])
def test_gamma_and_unknown_mask_do_not_invent_transparency(composite):
    row,_=evidence(composite=composite)
    assert row['displayed_contribution_interval'][1] is None or row['displayed_contribution_interval'][1]>0
    assert row['visible_contrast_interval'][0]==0


def test_dynamic_center_still_has_radius_area_upper_bound():
    row,_=evidence('x=.5+sin(time);rad=.01;')
    assert row['support']['area_fraction_interval'][0]==0
    assert row['support']['area_fraction_interval'][1]==pytest.approx(.01**2/2*9/16)


def test_source_context_and_model_hashes_are_stable_and_context_sensitive():
    _,first=evidence();_,repeat=evidence();_,other=evidence(viewport=(1280,720))
    assert first['provenance']==repeat['provenance']
    assert first['provenance']['preset_sha256']==other['provenance']['preset_sha256']
    assert first['provenance']['context_sha256']!=other['provenance']['context_sha256']


def test_missing_viewport_retains_unknown_area_without_assuming_square():
    row,_=evidence(viewport=(0,0))
    assert row['support']['area_fraction_interval']==[0,1]
    assert any('viewport' in reason for reason in row['unknown_reasons'])


def test_clipping_area_tracks_source_angle_plus_quarter_pi():
    # With ang=pi/4 the native four-sided polygon is a diamond in NDC.
    # At x=0 the half-diamond is 1/2 of its uncut support, even at wide aspect.
    row,_=evidence('ang=.7853981633974483;x=0;')
    shift=1/1920;radius=.5;aspect=9/16
    expected=.125*aspect/2+radius*shift/2-shift*shift/(4*aspect)
    assert row['support']['area_fraction_interval']==pytest.approx([expected]*2,abs=1e-8)


def test_unqualified_custom_compilation_cannot_resolve_a_disconnected_zero():
    row,_=evidence(composite='ret=0;',compiled=False)
    assert row['final_transfer']['difference_gain_interval']==[0,None]
    assert row['displayed_contribution_interval'][1]>0


def test_invalid_composite_domain_does_not_resolve_zero_by_saturation():
    row,_=evidence(composite='ret=saturate(GetPixel(uv/0)+2);')
    assert row['final_transfer']['difference_gain_interval'][1] is None
    assert row['displayed_contribution_interval'][1]>0


def test_dynamic_offscreen_domain_proves_no_support_without_sampling_time():
    row,_=evidence('x=-3+.1*sin(time);')
    assert row['support']['area_fraction_interval']==[0,0]
    assert row['displayed_contribution_interval']==[0,0]


def test_unknown_texture_alpha_keeps_possible_contribution():
    row,_=evidence(config='shapecode_0_textured=1\nshapecode_0_image=missing.png\n')
    assert row['opacity']['interval'][0]==0
    assert row['opacity']['interval'][1]>0
    assert row['unknown_reasons']


def test_z3_relational_range_rejects_impossible_on_screen_center():
    python=os.environ.get('MILK_PROOF_PYTHON')
    if python is None:pytest.skip('set MILK_PROOF_PYTHON to the pinned optional Z3 environment')
    from shader_fields import Field
    from effect_families import _constant
    from source_prominence import _shape_support
    from source_proofs import ProofSession
    bass=Field('input',detail={'name':'bass'})
    center=Field('subtract',(Field('add',(_constant(-3),bass)),bass))
    controls={'x':center,'y':_constant(.5),'rad':_constant(.5),'ang':_constant(0),'sides':_constant(4)}
    baseline,_=_shape_support(controls,1,[1920,1080],{'bass':[-2,2]})
    with ProofSession(python):refined,_=_shape_support(controls,1,[1920,1080],{'bass':[-2,2]})
    assert baseline['area_fraction_interval'][1]>0
    assert refined['area_fraction_interval']==[0,0]
    proof=refined['parameter_ranges'][0]['range_evidence']['x']['solver_refinement']
    assert proof['nominal_value_range'][0]<=-3<=proof['nominal_value_range'][1]<-2
    assert proof['native_numeric_certified'] is False


def test_gradient_alpha_integral_can_bound_a_clipped_subset_tighter_than_endpoint_max():
    row,_=evidence('a=1;a2=0;')
    assert row['source_contribution_interval'][1]==pytest.approx(.125*9/16/3)
    assert row['incoming_source_rgb_integral_intervals'] is not None


@pytest.mark.parametrize('flags,factor',[('',1),('bDarken=1\n',2),('bBrighten=1\nbSolarize=1\n',4)])
def test_native_legacy_gamma_and_filter_gain_uses_bounded_pointwise_transfer(flags,factor):
    row,_=evidence('a=.1;a2=.1;',shader_version=0,config='fGammaAdj=.5\n'+flags)
    assert row['final_transfer']['difference_gain_interval'][1]==pytest.approx(.5*factor)
    assert row['final_transfer']['pointwise_support_preserved'] is True


def test_history_dependent_coordinates_do_not_reuse_fixed_sample_alpha_gain():
    row,_=evidence('a=.001;a2=.001;',composite='ret=GetPixel(uv+GetPixel(uv).xy*.1)*.01;')
    assert row['final_transfer']['difference_gain_interval'][1] is None
    assert row['displayed_contribution_interval'][1]>=.00999


def test_pointwise_lookup_includes_bilinear_support_allowance():
    row,_=evidence('rad=.001;')
    assert row['displayed_support_fraction_interval'][1]>row['support']['area_fraction_interval'][1]
    assert row['sampling_support_allowance_fraction']>0


@pytest.mark.parametrize('body',['r=1e100;r2=1e100;a=0;a2=0;','rad=1e100;a=0;a2=0;',
    'tex_zoom=0;a=0;a2=0;','additive=1e100;a=0;a2=0;'])
def test_known_invalid_native_inputs_do_not_become_zero_by_transparency(body):
    row,_=evidence(body,config='shapecode_0_textured=1\n' if 'tex_zoom' in body else '')
    assert row['displayed_contribution_interval'][1]>0
    assert row['feedback_contribution_interval'][1]>0
    assert row['unknown_reasons']
