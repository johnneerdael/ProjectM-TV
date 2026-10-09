"""Procedural radial grids are source generators, not certified particles."""
import math
import pytest
from test_effect_families import shader,analyze,read,PRESETS
from test_source_appearance import appearance


def forms(body,stage='comp'):
    result=appearance(shader('shader_body {'+body+'}',stage=stage))
    element=next(e for e in result['elements'] if e['id']=='shader_'+('composite' if stage=='comp' else 'warp'))
    return element.get('procedural_forms',[])


def test_repeating_radial_glow_exports_cell_geometry_and_raw_falloff():
    f=forms('ret=saturate(.04/length(frac(uv*8)-.5));')[0]
    assert f['form_code']==9
    assert f['cell_centre']==[.5,.5]
    assert f['radial_gain']==pytest.approx(.04,abs=2e-8)
    assert f['core_radius_cell_units']==pytest.approx(.04,abs=2e-8)
    assert f['core_disk_area_per_cell']==pytest.approx(math.pi*.04**2,rel=2e-7)
    assert f['mapping_matrix_uv4']==[[8,0,0,0],[0,8,0,0]]
    assert f['actual_screen_coverage'] is None
    assert f['appearance_guaranteed'] is False


def test_abs_fold_does_not_change_euclidean_radial_grid():
    f=forms('float2 p=abs(frac(uv*3)-float2(.3,.6));ret=saturate(.02/length(p));')[0]
    assert f['cell_centre']==pytest.approx([.3,.6],abs=2e-7)
    assert f['mapping_matrix_uv4']==[[3,0,0,0],[0,3,0,0]]


def test_multiple_grid_layers_keep_distinct_records():
    fs=forms('float2 p=frac(uv*4)-.5;ret=saturate(.04/length(p))+saturate(.02/length(p));')
    assert len(fs)==2
    assert len({f['id'] for f in fs})==2
    assert sorted(f['radial_gain'] for f in fs)==pytest.approx([.02,.04],abs=2e-8)


@pytest.mark.parametrize('body',[
    'ret=float4(.1,.2,.3,saturate(.04/length(frac(uv*8)-.5)));',
    'ret=saturate(.04/length(frac(uv*8)-.5))*0;',
    'ret=saturate(.04/length(uv-.5));',
    'ret=saturate(.04/length(frac(time.xx)-.5));',
    'ret=saturate(.04/length(float2(frac(uv.x),frac(uv.x))-.5));',
    'ret=saturate(1/length(frac(uv*8)-.5));',
])
def test_dead_single_point_uniform_rank_one_or_constant_forms_do_not_claim_grid(body):
    record=analyze(shader('shader_body {'+body+'}'))
    assert not any(f['mechanism']=='periodic_radial_glow' for f in record['families'])


def test_cell_clipping_prevents_full_core_disk_area_claim():
    f=forms('ret=saturate(.4/length(frac(uv*8)-float2(.1,.5)));')[0]
    assert f['core_disk_area_per_cell'] is None
    assert f['core_clipped_by_cell'] is True


def test_grid_phase_audio_route_targets_mapping_not_colour_gain():
    f=forms('ret=saturate(.04/length(frac(uv*8+float2(.1*bass,time))-.5));')[0]
    assert any(r['input_code']==1 and r['control']=='grid_phase_x' for r in f['audio_routes'])
    assert f['phase_motion_controls'][1]['signed_linear_rate_per_second']==1
    assert f['visible_motion_speed'] is None


def test_original_xtramartin_contains_two_radial_grid_generators():
    result=appearance(read((PRESETS/'xtramartin (454).milk').read_bytes()))
    fs=next(e for e in result['elements'] if e['id']=='shader_composite')['procedural_forms']
    assert len(fs)==2
    assert sorted(f['radial_gain'] for f in fs)==pytest.approx([.02,.04],abs=2e-8)
    assert all(f['mapping_matrix_uv4'] is None for f in fs)


def test_highly_anisotropic_mapping_is_not_a_rank_one_proof():
    fs=forms('ret=saturate(.04/length(frac(uv*float2(1e20,1))-.5));')
    assert len(fs)==1
    assert fs[0]['mapping_rank_uv4']==2


def test_shader_uniforms_named_like_eel_coordinates_do_not_claim_spatial_grid():
    source=shader('uniform float x;uniform float y;shader_body{ret=saturate(.04/length(frac(float2(x,y))-.5));}')
    record=analyze(source)
    assert not any(f['mechanism']=='periodic_radial_glow' for f in record['families'])


def test_identical_repeated_formula_is_one_canonical_generator_not_a_layer_count():
    fs=forms('ret=saturate(.04/length(frac(uv*8)-.5))+saturate(.04/length(frac(uv*8)-.5));')
    assert len(fs)==1
