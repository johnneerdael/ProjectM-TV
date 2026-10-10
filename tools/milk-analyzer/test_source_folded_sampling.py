"""Explicit coordinate folds describe source repeat cells, not visible copies."""
import pytest
from test_source_sampling import maps


def folded(code):return maps(code)[0]['folded_coordinate_map']


def test_explicit_frac_tiles_export_phase_and_repeat_lattice():
    r=folded('ret=GetPixel(frac(uv*float2(3,4)));')
    assert r['source_model']=='planar_periodic_folds'
    assert [a['function'] for a in r['axes']]==['frac','frac']
    assert r['phase_matrix_uv4']==[[3,0,0,0],[0,4,0,0]]
    assert r['repeat_lattice_basis_uv'][0]==pytest.approx([1/3,0])
    assert r['repeat_lattice_basis_uv'][1]==pytest.approx([0,1/4])
    assert r['fundamental_cell_area_uv2']==pytest.approx(1/12)
    assert r['actual_visible_copy_count'] is None


def test_triangular_fold_has_two_opposite_slope_branches():
    r=folded('ret=GetPixel(abs(2*frac(uv*2)-1));')
    assert [a['function'] for a in r['axes']]==['triangular_frac','triangular_frac']
    assert r['axes'][0]['fold_output_range']==[0,1]
    assert r['axes'][0]['derivative_wrt_phase_away_from_seams']==[-2,2]
    assert r['axes'][0]['continuous_nominal'] is True
    assert r['fundamental_cell_area_uv2']==pytest.approx(.25)


def test_frac_negative_phase_uses_floor_not_truncation_and_keeps_translation():
    r=folded('ret=GetPixel(frac(uv*float2(-2,3)+float2(.3,-.7)));')
    assert r['phase_matrix_uv4']==[[-2,0,0,0],[0,3,0,0]]
    assert r['axes'][0]['phase_offset_value']==pytest.approx(.3,abs=2e-8)
    assert r['axes'][0]['continuous_nominal'] is False


def test_one_fold_axis_retains_partial_structure_without_full_lattice():
    r=folded('ret=GetPixel(float2(frac(uv.x*3),uv.y));')
    assert r['source_model']=='partial_planar_periodic_folds'
    assert r['axes'][0]['function']=='frac' and r['axes'][1] is None
    assert r['repeat_lattice_basis_uv'] is None


@pytest.mark.parametrize('code',[
 'ret=GetPixel(frac(uv+GetPixel(uv).rg));',
 'ret=GetPixel(frac(uv*uv));',
 'ret=GetPixel(frac(uv+float2((bass/0.)*0.,0)));',
])
def test_image_nonlinear_and_invalid_phase_do_not_invent_lattice(code):
    r=folded(code)
    assert r['repeat_lattice_basis_uv'] is None
    if 'bass/0.' in code:assert r['source_model']=='unknown'


def test_dynamic_phase_scale_exports_formula_without_constant_lattice():
    r=folded('ret=GetPixel(frac(uv*bass));')
    assert r['source_model']=='planar_periodic_folds'
    assert r['phase_coefficient_programs']
    assert r['phase_matrix_uv4'] is None and r['repeat_lattice_basis_uv'] is None


def test_plain_repeat_sampler_does_not_invent_authored_frac_operation():
    assert folded('ret=GetPixel(uv*3);')['source_model']=='unknown'


def test_audio_scaled_repeat_frequency_has_named_band_route():
    r=folded('ret=GetPixel(frac(uv*bass));')
    assert any(a['input_code']==1 and a['control'].startswith('fold_phase_coefficient') for axis in r['axes'] for a in axis['audio_routes'])


def test_native_original_uv_fold_preserves_bypass_basis():
    r=maps('ret=GetPixel(frac(uv_orig*2));','warp')[0]['folded_coordinate_map']
    assert r['basis']=='original_uv'
    assert r['phase_matrix_uv4']==[[0,0,2,0],[0,0,0,2]]


def test_fold_kernel_and_phase_reproduce_negative_positive_coordinate_samples():
    import math
    r=folded('ret=GetPixel(abs(2*frac(uv*float2(-2,3)+float2(.3,-.7))-1));')
    for point in [(-.8,.2),(.25,.9),(1.3,-.5)]:
        for i,a in enumerate(r['axes']):
            phase=sum(k*v for k,v in zip(a['phase_coefficients_uv4'],[*point,*point]))+a['phase_offset_value']
            predicted=a['output_scale']*abs(2*(phase-math.floor(phase))-1)+a['output_offset_value']
            native_formula=abs(2*(([-2,3][i]*point[i]+[.3,-.7][i])%1)-1)
            assert predicted==pytest.approx(native_formula,abs=2e-7)
