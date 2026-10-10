"""Oscillatory lookup maps describe texture deformation, not visible trajectories."""
import pytest
from test_source_sampling import maps


def warp(body):
    m=maps(body)[0]
    assert 'oscillatory_displacement' in m
    return m['oscillatory_displacement']


def test_two_cross_axis_waves_export_amplitude_frequency_and_base():
    r=warp('ret=GetPixel(uv+float2(.02*sin(uv.y*8+time),.03*cos(uv.x*6+time)));')
    assert r['source_model']=='uniform_affine_plus_oscillators'
    assert r['base_matrix_uv4']==[[1,0,0,0],[0,1,0,0]]
    assert len(r['waves'])==2
    for actual,expected in zip(sorted(w['constant_amplitude_uv'] for w in r['waves']),[[0,.03],[.02,0]]):
        assert actual==pytest.approx(expected,abs=2e-8)
    assert r['jacobian_perturbation_infinity_norm_upper_bound']==pytest.approx(.18,abs=2e-8)
    assert r['sufficient_no_fold_of_unwrapped_nominal_map'] is True
    assert r['visible_motion_speed'] is None


def test_shared_phase_has_one_vector_displacement_wave():
    r=warp('float s=sin(uv.y*8);ret=GetPixel(uv+float2(.02*s,.03*s));')
    assert len(r['waves'])==1
    assert r['waves'][0]['constant_amplitude_uv']==pytest.approx([.02,.03],abs=2e-8)


def test_audio_controls_frequency_and_amplitude_without_invented_range():
    r=warp('ret=GetPixel(uv+float2(.01*bass*sin(uv.y*(3+2*mid)+time),0));')
    assert r['source_model']=='uniform_affine_plus_oscillators'
    w=r['waves'][0]
    assert w['constant_amplitude_uv'] is None
    assert w['constant_phase_gradient'] is None
    assert {(a['input_code'],a['control']) for a in w['audio_routes']} >= {(1,'wave_amplitude_x'),(2,'wave_frequency_1')}
    assert r['jacobian_perturbation_infinity_norm_upper_bound'] is None
    assert r['sufficient_no_fold_of_unwrapped_nominal_map'] is None


def test_original_uv_basis_keeps_native_mesh_bypass_distinct():
    from test_source_sampling import maps
    r=maps('ret=GetPixel(uv_orig+float2(.01*sin(uv_orig.y*8),0));','warp')[0]['oscillatory_displacement']
    assert r['basis']=='original_uv'


def test_large_ripple_fails_sufficient_bound_without_claiming_actual_fold():
    r=warp('ret=GetPixel(uv+float2(.3*sin(uv.x*8),0));')
    assert r['sufficient_no_fold_of_unwrapped_nominal_map'] is False
    assert r['actual_fold_present'] is None


@pytest.mark.parametrize('code',[
    'ret=GetPixel(uv);',
    'ret=GetPixel(uv+float2(.02*sin(time),0));',
    'ret=GetPixel(uv+float2(.02*sin(uv.x*uv.y),0));',
    'ret=GetPixel(uv+float2(.02*sin(GetPixel(uv).x),0));',
    'ret=GetPixel(uv+float2(.02*sin(uv.x+1./0.),0));',
])
def test_plain_uniform_nonaffine_image_driven_and_singular_offsets_are_not_supported_maps(code):
    assert warp(code)['source_model']=='unknown'


def test_nonidentity_base_has_no_identity_perturbation_certificate():
    r=warp('ret=GetPixel(uv*2+float2(.01*sin(uv.x*8),0));')
    assert r['base_matrix_uv4']==[[2,0,0,0],[0,2,0,0]]
    assert r['sufficient_no_fold_of_unwrapped_nominal_map'] is None


@pytest.mark.parametrize('code',[
    'ret=GetPixel(uv+float2(.01*sin(uv.x*8)+1./0.,0));',
    'ret=GetPixel(uv+float2((1./0.)*sin(uv.x*8),0));',
    'ret=GetPixel(uv+float2(.01*sin(int(uv.x*8)),0));',
])
def test_invalid_baseline_amplitude_and_quantized_spatial_phase_abstain(code):
    r=warp(code)
    assert r['source_model']=='unknown'
    assert r['sufficient_no_fold_of_unwrapped_nominal_map'] is None


def test_dynamic_baseline_program_is_preserved_without_inventing_constant_matrix():
    r=warp('ret=GetPixel(uv*(1+.1*bass)+float2(.01*sin(uv.x*8),0));')
    assert r['source_model']=='uniform_affine_plus_oscillators'
    assert r['base_matrix_uv4'] is None
    assert r['base_coefficient_programs']
    assert r['sufficient_no_fold_of_unwrapped_nominal_map'] is None


def test_missing_baseline_export_is_not_a_complete_supported_map():
    from types import SimpleNamespace
    from shader_fields import Field
    from source_periodic_sampling import oscillatory_displacement,number
    uv=Field('input',dtype='float2',detail={'name':'_uv'})
    x=Field('member',(uv,),'float',{'field':'x','swizzle':True})
    y=Field('member',(uv,),'float',{'field':'y','swizzle':True})
    deep=Field('input',detail={'name':'time'})
    for _ in range(300):deep=Field('sin',(deep,),'float')
    wave=Field('multiply',(number(.01),Field('sin',(Field('multiply',(x,number(8)),'float'),),'float')),'float')
    field=Field('components',(Field('add',(x,Field('add',(deep,wave),'float')),'float'),y),'float2')
    assert oscillatory_displacement(field,SimpleNamespace(main={}))['source_model']=='unknown'


def test_invalid_native_spatial_input_width_is_rejected():
    from shader_fields import Field
    from source_periodic_sampling import uniform_affine_scalar
    parent=Field('input',dtype='float4',detail={'name':'_rad_ang'})
    node=Field('member',(parent,),'float',{'field':'x','swizzle':True})
    with pytest.raises(ValueError):uniform_affine_scalar(node)


def test_literal_matrix_phase_uses_existing_typed_matrix_policy():
    r=warp('float2 p=mul(float2x2(2,0,0,3),uv);ret=GetPixel(uv+float2(.01*sin(p.x),0));')
    assert r['source_model']=='uniform_affine_plus_oscillators'
    assert r['waves'][0]['constant_phase_gradient']==[2,0,0,0,0,0]


@pytest.mark.parametrize('code',[
    'ret=GetPixel(uv+float2((bass/0.)*0.+.01*sin(uv.x*8),0));',
    'ret=GetPixel(uv+float2((bass/0.)*0.*sin(uv.x*8)+.01*cos(uv.x*8),0));',
])
def test_zero_products_do_not_erase_known_singular_source_intermediates(code):
    r=warp(code)
    assert r['source_model']=='unknown'
    assert r['sufficient_no_fold_of_unwrapped_nominal_map'] is None
    assert r['unknown_reasons']


@pytest.mark.parametrize('code',[
    'ret=GetPixel(uv+0.*(uv/float2(0.,0.))+float2(.01*sin(uv.x*8),0));',
    'ret=GetPixel(uv+float2(0.,0.)*pow(float2(0.,0.),-1.)+float2(.01*sin(uv.x*8),0));',
])
def test_vector_domain_failures_are_checked_before_zero_simplification(code):
    r=warp(code)
    assert r['source_model']=='unknown'
    assert r['sufficient_no_fold_of_unwrapped_nominal_map'] is None
