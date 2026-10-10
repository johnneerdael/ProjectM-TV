"""Non-affine lookup UV gains precede native displacement composition."""
import numpy as np
import pytest
from test_effect_families import shader,read,analyze
from test_source_appearance import appearance


def lookup(code):
    d=appearance(shader('shader_body {'+code+'}',stage='warp'))
    return d['sampling_geometry']['stages']['warp'][0]['mesh_uv_response']


def test_sinusoidal_coordinate_has_non_affine_uv_gain():
    r=lookup('ret=GetPixel(uv+float2(.02*sin(uv.y*8+time),0));')
    assert np.array(r['matrix_uv_output_input_gain_upper_bounds'])==pytest.approx(np.array([[1,.16],[0,1]]),rel=1e-6)
    assert r['global_lipschitz_domain_verified'] is True


def test_triangular_fold_is_continuous_but_frac_is_not():
    tri=lookup('ret=GetPixel(abs(2*frac(uv*3)-1));')
    assert tri['global_lipschitz_domain_verified'] is True
    assert np.array(tri['matrix_uv_output_input_gain_upper_bounds'])==pytest.approx(np.array([[6,0],[0,6]]),rel=1e-6)
    frac=lookup('ret=GetPixel(frac(uv*3));')
    assert frac['global_lipschitz_domain_verified'] is False


def test_unbounded_uv_square_does_not_receive_global_gain():
    r=lookup('ret=GetPixel(uv*uv);')
    assert r['global_lipschitz_domain_verified'] is False


def test_sample_coordinate_dependency_is_not_held_fixed_for_full_uv_gain():
    r=lookup('ret=GetPixel(uv+.1*GetBlur1(uv).rg);')
    assert r['global_lipschitz_domain_verified'] is False
    assert r['includes_sample_coordinate_chain'] is False


def test_original_uv_only_has_zero_mesh_response():
    r=lookup('ret=GetPixel(sin(uv_orig*8));')
    assert r['global_lipschitz_domain_verified'] is True
    assert r['matrix_uv_output_input_gain_upper_bounds']==[[0,0],[0,0]]


def test_declared_audio_domain_bounds_ripple_gain_without_altering_default():
    s=shader('shader_body {ret=GetPixel(uv+float2(.01*bass*sin(uv.y*(3+2*mid)),0));}',stage='warp')
    d=analyze(s,input_scenario={'schema_version':1,'name':'ripple','audio_band_ranges':{'bass':[0,2],'mid':[0,2]}})['visual_description']
    r=d['sampling_geometry']['stages']['warp'][0]['mesh_uv_response']
    assert r['global_lipschitz_domain_verified'] is False
    e=r['scenario_mesh_uv_response']
    assert e['global_lipschitz_domain_verified'] is True
    assert e['matrix_uv_output_input_gain_upper_bounds'][0]==pytest.approx([1,.14],rel=1e-6)


def test_nonaffine_uv_gain_composes_with_native_transport():
    d=appearance(read('per_frame_1=zoomexp=1;warp=0;zoom=1.01;\n'
        'warp_1=`shader_body {ret=GetPixel(uv+float2(.02*sin(uv.y*8),0));}\n'))
    r=d['activity']['motion_intensity']['native_lookup_transport'][0]
    assert r['native_mesh_contribution']=='bounded'
    assert r['lookup_response_model']=='nonlinear_mesh_uv_lipschitz'


def test_known_invalid_original_only_coordinate_is_not_certified():
    r=lookup('ret=GetPixel(uv_orig+float2(time/0,0));')
    assert r['global_lipschitz_domain_verified'] is False


def test_independent_coordinate_differences_respect_gain_matrix():
    d=appearance(read('per_frame_1=zoomexp=1;warp=0;zoom=1.01;\n'
        'warp_1=`shader_body {ret=GetPixel(uv+float2(.02*sin(uv.y*8+.4),.03*cos(uv.x*6)));}\n'))
    matrix=np.array(d['sampling_geometry']['stages']['warp'][0]['mesh_uv_response']['matrix_uv_output_input_gain_upper_bounds'])
    def f(p):return p+np.array([.02*np.sin(p[1]*8+.4),.03*np.cos(p[0]*6)])
    for a,b in ((np.array([-.4,.8]),np.array([.6,1.4])),(np.array([2.,-1.]),np.array([2.01,-1.03]))):
        assert np.all(np.abs(f(a)-f(b))<=matrix@np.abs(a-b)+1e-8)


def test_spatial_native_upload_does_not_hide_uv_dependency():
    from shader_fields import Field
    from source_ripple_envelopes import coefficient_envelope
    uv=Field('input',dtype='float4',detail={'name':'_uv'})
    x=Field('member',(uv,),'float',{'field':'x','swizzle':True})
    q=Field('narrow',(Field('sin',(x,),'float'),),'float',{'numeric_domain':'shader-float32'})
    assert coefficient_envelope(q,response_inputs={'_uv.x'})['maximum_absolute_control_change_per_audio_unit'] is None


def test_scenario_uv_gain_retains_separate_native_transport():
    source=read('per_frame_1=zoomexp=1;warp=0;zoom=1.01;\n'
        'warp_1=`shader_body {ret=GetPixel(uv+float2(.01*bass*sin(uv.y*3),0));}\n')
    d=analyze(source,input_scenario={'schema_version':1,'name':'transport','audio_band_ranges':{'bass':[0,2]}})['visual_description']
    r=d['activity']['motion_intensity']['native_lookup_transport'][0]
    assert r['native_mesh_contribution']=='unknown'
    e=r['scenario_native_lookup_transport']
    assert e['native_mesh_contribution']=='bounded'
    assert e['input_scenario_sha256'] is not None


def test_original_grind_full_export_profile_retains_structured_description():
    import json
    from pathlib import Path
    from effect_family_export import export_preset
    root=Path(__file__).resolve().parents[2]
    raw=json.loads((root/'build/preset-corpus/source-compile-manifest-2026-10-10/manifest.json').read_text())
    scenario=json.loads((root/'build/preset-corpus/source-sample-offset-scenario.json').read_text())
    r,hit=export_preset(root/'core/src/main/assets/presets/flexi - grind my glitch up [191].milk',
        reader=root/'build/preset-corpus/source34/adapters/milk-native-reader',compile_manifest=raw,input_scenario=scenario)
    d=r['analysis']['visual_description']
    assert 'sampling_geometry' in d,d


def test_projection_preserves_selected_input_taint_and_domains():
    from shader_fields import Field
    from source_ripple_envelopes import coefficient_envelope
    x=Field('input',detail={'name':'x'});y=Field('input',detail={'name':'y'})
    q=Field('narrow',(x,),'float',{'numeric_domain':'shader-float32'})
    expr=Field('multiply',(q,y),'float')
    domains={'x':[0,1],'y':[0,2]}
    a=coefficient_envelope(expr,input_domains=domains,response_inputs={'y'})
    assert a['maximum_absolute_control_change_per_audio_unit']==pytest.approx(1,rel=1e-6)
    b=coefficient_envelope(expr,input_domains=domains,response_inputs={'x'})
    assert b['maximum_absolute_control_change_per_audio_unit'] is None
    c=coefficient_envelope(expr,input_domains={'x':[0,.5],'y':[0,2]},response_inputs={'y'})
    assert c['maximum_absolute_control_change_per_audio_unit']==pytest.approx(.5,rel=1e-6)


def test_uniform_cache_reuses_identity_without_cross_field_leak():
    from effect_families import _CACHE
    from source_periodic_sampling import uniform
    from shader_fields import Field
    cache={};token=_CACHE.set(cache)
    try:
        t=Field('sin',(Field('input',detail={'name':'time'}),),'float')
        assert uniform(t)
        before=cache['field_visits'];assert uniform(t);assert cache['field_visits']==before
        assert not uniform(Field('input',dtype='float4',detail={'name':'_uv'}))
    finally:_CACHE.reset(token)


def test_failed_original_domain_preflight_clears_candidate_certificates(monkeypatch):
    import source_forms
    from source_lookup_uv_response import mesh_uv_response
    from shader_fields import Field
    from source_input_scenario import validate_scenario
    uv=Field('input',dtype='float2',detail={'name':'_uv'})
    field=Field('sin',(uv,),'float2')
    lookup={'sampled_coordinate_response':{'direct_sample_count':0},'matrix_uv4':None,
        'folded_coordinate_map':{'source_model':'unknown'},'sampling_motion':{'unknown_reasons':[]}}
    monkeypatch.setattr(source_forms,'known_invalid_phase_offset',lambda *a,**k:True)
    r=mesh_uv_response(field,lookup,input_scenario=validate_scenario({'schema_version':1,'name':'domain','audio_band_ranges':{}}))
    assert r['global_lipschitz_domain_verified'] is False
    assert r['scenario_mesh_uv_response']['global_lipschitz_domain_verified'] is False
