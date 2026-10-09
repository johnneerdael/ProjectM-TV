"""Machine-readable mental-map traits from source, never rendered images."""
import json
import pytest
from test_effect_families import shader,read,analyze


def appearance(source):
    result=analyze(source)
    assert 'visual_description' in result,'structured source appearance export missing'
    return result['visual_description']


def test_generated_phase_palette_exports_numeric_rgb_parameters():
    result=appearance(shader('shader_body {ret=.5+.5*cos(time+float3(0,2,4));}'))
    colour=result['elements'][0]['colour']
    assert colour['mode_code']==3
    assert colour['bias_rgb']==[.5]*3 and colour['amplitude_rgb']==[.5]*3
    assert colour['phase_offsets_rad']==[0,2,4]
    assert colour['common_phase_expression']['nodes']
    assert colour['distinct_channel_phases']==3
    assert colour['depends_on_time']==1
    assert result['uses_rendered_images'] is False
    json.dumps(result,allow_nan=False)


@pytest.mark.parametrize('code',[
    'shader_body {ret=sin(time);}',
    'shader_body {ret=float3(1,.5,.2)*sin(time);}',
    'shader_body {ret=GetPixel(uv);}',
    'shader_body {float3 unused=.5+.5*cos(time+float3(0,2,4));ret=0;}',
    'shader_body {ret=float4(1,0,0,sin(time));}',
])
def test_monochrome_inherited_and_dead_forms_are_not_generated_varied_palettes(code):
    result=appearance(shader(code))
    assert all(element['colour']['mode_code']!=3 for element in result['elements'])


def test_shape_audio_routes_target_named_controls_and_coefficients():
    source=read('PSVERSION_COMP=0\nfWaveAlpha=0\nshapecode_0_enabled=1\nshapecode_0_sides=5\n'
        'shapecode_0_rad=.2\nshape_0_per_frame1=rad=.2+bass*.05;ang=mid*.1;r=treb*.3;\n')
    result=appearance(source)
    element=next(row for row in result['elements'] if row['id']=='shape_0')
    assert element['family_codes']==[3]
    routes={row['control']:row for row in element['audio_routes']}
    assert routes['radius']['input_code']==1 and routes['radius']['linear_gain']==pytest.approx(.05)
    assert routes['rotation']['input_code']==2 and routes['rotation']['linear_gain']==pytest.approx(.1)
    assert routes['colour_r']['input_code']==3 and routes['colour_r']['linear_gain']==pytest.approx(.3)
    assert all(row['visible_response_strength'] is None for row in routes.values())


def test_rgb_shader_bass_mid_high_routes_do_not_claim_stems_or_image_strength():
    result=appearance(shader('shader_body {ret=float3(bass*.2,mid*.1,treb*.3);}'))
    routes=result['elements'][0]['audio_routes']
    assert {(r['control'],r['input_code']) for r in routes}=={('colour_r',1),('colour_g',2),('colour_b',3)}
    assert all(r['visible_response_strength'] is None for r in routes)


def test_alpha_only_audio_is_not_exported_as_colour_response():
    result=appearance(shader('shader_body {ret=float4(1,0,0,bass);}'))
    assert not result['elements'][0]['audio_routes']


def test_clipped_white_oscillators_are_not_multicolour_candidates():
    result=appearance(shader('shader_body {ret=10+.1*cos(time+float3(0,2,4));}'))
    assert result['elements'][0]['colour']['mode_code']!=3


def test_preference_description_keeps_flashing_and_motion_uncertainty():
    result=appearance(shader('shader_body {ret=.5+.5*cos(time+float3(0,2,4));}'))
    assert result['activity']['flashing']=={'value':None,'status':'unknown'}
    assert result['activity']['motion_intensity']=={'value':None,'status':'unknown'}
    assert result['mood_matches']['chill']['eligible'] is None


def test_final_constant_composite_removes_warp_element_and_audio_routes():
    result=appearance(read('PSVERSION_WARP=2\nPSVERSION_COMP=2\n'
        'warp_1=`shader_body {ret=GetPixel(uv)*bass;}\n'
        'comp_1=`shader_body {ret=0;}\n'))
    assert [row['id'] for row in result['elements']]==['shader_composite']
    assert not result['elements'][0]['audio_routes']


def test_q_bridge_explains_shader_audio_dependency_with_main_source_formula():
    result=appearance(read('PSVERSION_COMP=2\nper_frame_1=q1=bass*.2;\n'
        'comp_1=`shader_body {ret=float3(q1,0,0);}\n'))
    route=next(row for row in result['elements'][0]['audio_routes'] if row['control']=='colour_r')
    assert route['input_code']==1
    assert route['q_bridge_expressions']['q1']['nodes']
    assert route['linear_gain'] is None #shader-side coefficient is not yet the composed gain


def test_fixed_tint_modulation_is_distinct_from_inherited_or_varied_palette():
    result=appearance(shader('shader_body {ret=float3(1,.5,.2)*sin(time);}'))
    assert result['elements'][0]['colour']['mode_code']==2
    assert result['elements'][0]['colour']['tint_rgb']==pytest.approx([1,.5,.2],abs=1e-7)


def test_fps_driven_phase_is_not_mislabelled_time_driven():
    result=appearance(shader('shader_body {ret=.5+.5*cos(fps+float3(0,2,4));}'))
    assert result['elements'][0]['colour']['mode_code']==3
    assert result['elements'][0]['colour']['depends_on_time']==0


def test_palette_under_common_spatial_mask_retains_colour_generator_parameters():
    result=appearance(shader('shader_body {float f=length(uv-.5);'
        'ret=(.5+.5*cos(time+float3(0,2,4)))*(1-smoothstep(.1,.3,f));}'))
    colour=result['elements'][0]['colour']
    assert colour['mode_code']==3
    assert colour['phase_offsets_rad']==[0,2,4]
    assert colour['shared_multiplier_expressions']
    assert colour['guaranteed_visible'] is False


def test_masked_palette_does_not_appear_through_zero_or_monochrome_composite():
    result=appearance(read('PSVERSION_WARP=2\nPSVERSION_COMP=2\n'
        'warp_1=`shader_body {ret=.5+.5*cos(time+float3(0,2,4));}\n'
        'comp_1=`shader_body {ret=GetPixel(uv).rrr;}\n'))
    assert result['elements'][-1]['colour']['mode_code']==1
    assert result['mood_matches']['psychedelic']['candidate'] is not True


def test_global_feedback_transform_routes_distinguish_audio_bands():
    result=appearance(read('fWaveAlpha=0\nper_frame_1=zoom=1+bass*.05;rot=mid*.2;warp=treb*.3;\n'))
    element=next(e for e in result['elements'] if e['id']=='mesh_warp')
    routes={r['control']:r for r in element['audio_routes']}
    assert routes['zoom']['input_code']==1 and routes['zoom']['linear_gain']==pytest.approx(.05)
    assert routes['rotation']['input_code']==2 and routes['rotation']['linear_gain']==pytest.approx(.2)
    assert routes['deformation']['input_code']==3 and routes['deformation']['linear_gain']==pytest.approx(.3)


def test_uv_orig_bypass_does_not_claim_native_zoom_audio_response():
    result=appearance(read('PSVERSION_WARP=2\nper_frame_1=zoom=1+bass*.05;\n'
        'warp_1=`shader_body {ret=GetPixel(uv_orig);}\n'))
    assert not any(e['id']=='mesh_warp' for e in result['elements'])


def test_loop_only_bass_does_not_invent_other_bands_or_channels():
    result=appearance(shader('shader_body {float v=0;for(int n=0;n<2;n++){v+=bass;}ret=float3(v,0,0);}'))
    routes=result['elements'][0]['audio_routes']
    assert {(r['control'],r['input_code']) for r in routes}=={('colour_r',1)}


def test_unrelated_loop_preserves_palette_data_but_keeps_execution_uncertainty():
    result=appearance(shader('shader_body {for(int n=0;n<2;n++){}ret=.5+.5*cos(time+float3(0,2,4));}'))
    assert result['elements'][0]['colour']['mode_code']==3
    assert result['execution_unknowns']


def test_zero_clipped_common_multiplier_removes_palette_candidate():
    result=appearance(shader('shader_body {ret=(.5+.5*cos(time+float3(0,2,4)))*saturate(-1)*GetPixel(uv).r;}'))
    element=next(e for e in result['elements'] if e['id']=='shader_composite')
    assert element['colour']['mode_code']!=3
    assert result['mood_matches']['psychedelic']['candidate'] is not True


def test_main_q_bridge_reaches_shape_radius():
    source=read('fWaveAlpha=0\nper_frame_1=q1=bass*.2;\nshapecode_0_enabled=1\n'
        'shape_0_per_frame1=rad=.2+q1*.05;\n')
    result=appearance(source)
    route=next(r for e in result['elements'] if e['id']=='shape_0' for r in e['audio_routes'] if r['control']=='radius')
    assert route['input_code']==1
    assert route['linear_gain']==pytest.approx(.01)
    assert any(n['op']=='input' and n['detail'].get('name')=='bass' for n in route['expression']['nodes'])


def test_native_shape_frame_q_load_replaces_init_q_but_local_write_overrides():
    common='fWaveAlpha=0\nper_frame_1=q1=bass*.2;\nshapecode_0_enabled=1\nshape_0_init1=q1=.5;\n'
    loaded=appearance(read(common+'shape_0_per_frame1=rad=.2+q1*.05;\n'))
    element=next(e for e in loaded['elements'] if e['id']=='shape_0')
    assert any(r['control']=='radius' and r['input_code']==1 for r in element['audio_routes'])
    overridden=appearance(read(common+'shape_0_per_frame1=q1=.5;rad=.2+q1*.05;\n'))
    element=next(e for e in overridden['elements'] if e['id']=='shape_0')
    assert not any(r['control']=='radius' for r in element['audio_routes'])


def test_unwritten_main_q_zero_replaces_audio_dependent_shape_init_q():
    source=read('fWaveAlpha=0\nshapecode_0_enabled=1\nshape_0_init1=q1=bass*.2;\n'
        'shape_0_per_frame1=rad=.2+q1*.05;\n')
    element=next(e for e in appearance(source)['elements'] if e['id']=='shape_0')
    assert element['parameters']['rad']==pytest.approx(.2)
    assert not any(r['control']=='radius' for r in element['audio_routes'])


@pytest.mark.parametrize('mask',['clamp(-1,0,1)','saturate(abs(0))'])
def test_supported_constant_zero_masks_do_not_generate_palette(mask):
    source=shader('shader_body {ret=(.5+.5*cos(time+float3(0,2,4)))*'+mask+';}')
    element=next(e for e in appearance(source)['elements'] if e['id']=='shader_composite')
    assert element['colour']['mode_code']!=3


def test_hidden_loop_samples_do_not_claim_resources_resolved():
    source=shader('shader_body {float v=0;for(int n=0;n<2;n++){v+=GetPixel(uv).r*bass;}ret=float3(v,0,0);}')
    element=next(e for e in appearance(source)['elements'] if e['id']=='shader_composite')
    expression=element['audio_routes'][0]['expression']
    assert expression['resources_resolved'] is not True


def test_independent_rgb_phase_rates_export_each_control_program():
    result=appearance(shader('shader_body {ret=.5+.5*sin(time*float3(42,23,13.37));}'))
    colour=result['elements'][0]['colour']
    assert colour['mode_code']==5
    assert colour['distinct_channel_phases'] is None
    assert len(colour['channel_phase_expressions'])==3
    assert colour['oscillator_function_codes']==[2,2,2]
    assert colour['depends_on_time']==1


def test_fractal_with_generated_colour_marks_conditional_psychedelic_potential():
    source=read('PSVERSION_WARP=2\nPSVERSION_COMP=2\n'
        'warp_1=`shader_body {float2 z=uv-.5;for(int n=0;n<4;n++){'
        'z=float2(z.x*z.x-z.y*z.y,2*z.x*z.y)+float2(.1,.2);}ret=GetPixel(z);}\n'
        'comp_1=`shader_body {ret=(.5+.5*cos(time+float3(0,2,4)))*GetPixel(uv).r;}\n')
    result=appearance(source)
    assert any(7 in element['family_codes'] for element in result['elements'])
    assert result['mood_matches']['psychedelic']['candidate'] is True
    assert result['mood_matches']['psychedelic']['confidence'] is None
    assert result['mood_matches']['chill']['eligible'] is None


def test_exported_control_formulas_keep_texture_identity_and_obligations():
    expressions=[]
    for name in ['main','noise_lq','blur1']:
        result=appearance(shader('shader_body {ret=tex2D(sampler_'+name+',uv).rgb*bass;}'))
        element=next(e for e in result['elements'] if e['id']=='shader_composite')
        expression=element['audio_routes'][0]['expression']
        sample=next(n for n in expression['nodes'] if n['op']=='sample')
        assert sample['detail']['canonical_texture']==name
        assert sample['detail']['sampler']=='sampler_'+name
        assert expression['resources_resolved'] is False
        expressions.append(json.dumps(expression,sort_keys=True))
    assert len(set(expressions))==3
