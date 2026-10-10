"""Direct sampled-colour coordinate responses; no screen-speed certification."""
import numpy as np
import pytest
from test_source_sampling import maps
from test_effect_families import shader,read,PRESETS
from test_source_appearance import appearance


def response(body):
    return maps(body)[0]['sampled_coordinate_response']


def test_direct_colour_displacement_exports_per_channel_uv_coefficients():
    r=response('ret=GetPixel(uv+.1*GetPixel(uv).rg);')
    assert r['source_model']=='affine_uv_and_sample_values'
    assert r['base_matrix_uv4']==[[1,0,0,0],[0,1,0,0]]
    assert r['sample_contributions'][0]['matrix_uv_rgba']==[[pytest.approx(.1),0,0,0],[0,pytest.approx(.1),0,0]]
    assert r['direct_sample_gain_norm']==pytest.approx(.1)
    assert r['visible_motion_speed'] is None


def test_gradient_pair_preserves_positive_negative_samples_and_conditional_range():
    r=response('float a=dot(GetPixel(uv+.01).rgb-GetPixel(uv-.01).rgb,float3(.3,.6,.1));'
        'ret=GetPixel(uv+float2(a,0)*.02);')
    assert len(r['sample_contributions'])==2
    assert r['direct_sample_gain_norm']==pytest.approx(.04,abs=2e-8)
    assert np.array(r['conditional_sample_offset_range_uv'])==pytest.approx(np.array([[-.02,.02],[0,0]]),abs=2e-8)
    assert r['range_premise']=='each directly sampled RGBA component independently lies in [0,1]; not certified by source'


def test_nested_image_coordinates_keep_indirect_feedback_uncertainty():
    r=response('ret=GetPixel(uv+.1*GetPixel(uv+.2*GetPixel(uv).rg).rg);')
    assert r['coordinate_sample_dependency'] is True
    assert r['direct_sample_gain_norm']==pytest.approx(.1)
    assert len(r['sample_contributions'])==1
    assert r['full_coordinate_sensitivity'] is None


@pytest.mark.parametrize('coordinate',['uv+pow(GetPixel(uv).rg,2)',
    'uv+bass*GetPixel(uv).rg','float2(int(GetPixel(uv).r),uv.y)',
    'uv+GetPixel(uv).rg*GetPixel(uv).ba'])
def test_nonlinear_dynamic_or_quantized_sample_response_stays_unknown(coordinate):
    r=response('ret=GetPixel('+coordinate+');')
    assert r['source_model']=='unknown'
    assert r['direct_sample_gain_norm'] is None
    assert r['unknown_reasons']


def test_shader_uniform_offsets_named_x_y_do_not_become_spatial_bases():
    source=shader('uniform float x;uniform float y;shader_body{ret=GetPixel(uv+float2(x,y));}')
    m=appearance(source)['sampling_geometry']['stages']['composite'][0]
    assert m['matrix_uv4']==[[1,0,0,0],[0,1,0,0]]
    assert m['offset_uv']==[None,None]


def test_pure_uv_map_has_zero_direct_sample_gain_without_visible_stillness_claim():
    r=response('ret=GetPixel(uv*2);')
    assert r['source_model']=='affine_uv_and_sample_values'
    assert r['sample_contributions']==[]
    assert r['direct_sample_gain_norm']==0
    assert r['visible_motion_speed'] is None


def test_xtramartin_original_gradient_is_disconnected_by_unassigned_q32():
    d=appearance(read((PRESETS/'xtramartin (454).milk').read_bytes()))
    assert d['native_input_bindings']['main_frame_q']['lanes']['q32']['native_float32_constant']==0
    assert d['sampling_geometry']['stages']['warp']==[]


def test_xtramartin_explicit_q32_control_preserves_gradient_math():
    original=(PRESETS/'xtramartin (454).milk').read_bytes()
    # Deliberate test-only control; never modify or credit the original preset.
    d=appearance(read(original+b'\nper_frame_init_2=q32=1;\n'))
    maps=d['sampling_geometry']['stages']['warp']
    known=[m['sampled_coordinate_response'] for m in maps
           if m['sampled_coordinate_response']['source_model']=='affine_uv_and_sample_values'
           and m['sampled_coordinate_response']['sample_contributions']]
    assert known
    assert any(r['direct_sample_gain_norm']==pytest.approx(.044,abs=2e-7) for r in known)


def test_source_response_coefficients_predict_independent_sample_perturbations():
    r=response('ret=GetPixel(uv+float2(GetPixel(uv).r*.1-GetPixel(uv+.02).g*.2,GetPixel(uv).b*.3));')
    matrices=[np.array(c['matrix_uv_rgba']) for c in r['sample_contributions']]
    assert sum(float(np.sum(abs(m))) for m in matrices)==pytest.approx(.6,abs=2e-8)
    # An independent .4 increase of one sample component produces its exported
    # column times .4; there is no assumed texture/content relationship.
    displacements=[m@np.array([.4,0,0,0]) for m in matrices]
    assert any(v==pytest.approx([.04,0],abs=2e-8) for v in displacements)


def test_many_independent_coordinate_samples_abstain_with_bounded_memory():
    from shader_fields import Field
    from source_advection import sampled_coordinate_response
    uv=Field('constant',dtype='float2',detail={'value':[.5,.5]})
    zero=Field('constant',dtype='float',detail={'value':0.})
    terms=[Field('member',(Field('sample',(uv,),'float4',{'site_index':i,'canonical_texture':'main'}),),
                 'float',{'field':'r','swizzle':True}) for i in range(65)]
    while len(terms)>1:
        terms=[Field('add',(terms[i],terms[i+1]),'float') if i+1<len(terms) else terms[i]
               for i in range(0,len(terms),2)]
    r=sampled_coordinate_response(Field('components',(terms[0],zero),'float2'))
    assert r['source_model']=='unknown'
    assert r['unknown_reasons']==['direct coordinate sample count exceeds 64-input budget']
