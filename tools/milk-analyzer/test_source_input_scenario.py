"""Declared input scenarios are assumptions, never captured or genre evidence."""
import pytest
from test_effect_families import shader,analyze


def scenario(**kwargs):return {'schema_version':1,'name':'bounded-test','audio_band_ranges':{},**kwargs}


def test_scenario_binds_audio_aliases_without_changing_default_envelope():
    s=shader('shader_body {ret=GetPixel(uv+float2(.02*bass*sin(uv.y*8),0));}')
    plain=analyze(s)
    declared=analyze(s,input_scenario=scenario(audio_band_ranges={'bass':[0,2]}))
    m=declared['visual_description']['sampling_geometry']['stages']['composite'][0]['oscillatory_displacement']
    assert m['deformation_envelope']['maximum_absolute_displacement_uv']==[None,0]
    assert m['scenario_deformation_envelope']['maximum_absolute_displacement_uv']==pytest.approx([.04,0],abs=2e-8)
    assert plain['visual_description']['sampling_geometry']['stages']['composite'][0]['oscillatory_displacement']['deformation_envelope']==m['deformation_envelope']
    assert declared['input_scenario']['observed_runtime_inputs'] is False


def test_explicit_shader_canvas_size_binds_dimensions_and_native_reciprocals():
    from source_input_scenario import validate_scenario
    r=validate_scenario(scenario(shader_canvas_size=[854,480]))
    d=r['scalar_input_domains']
    assert d['_c7.x']==[854,854] and d['_c7.y']==[480,480]
    assert d['_c7.z'][0]==pytest.approx(1/854,rel=1e-7)
    assert d['_c7.w'][0]==pytest.approx(1/480,rel=1e-7)
    assert r['runtime_binding_verified'] is False


@pytest.mark.parametrize('bad',[
    scenario(audio_band_ranges={'bass':[2,0]}),scenario(audio_band_ranges={'bass':[0,float('inf')]}),
    scenario(audio_band_ranges={'q1':[0,2]}),scenario(audio_band_ranges={'bass':[False,2]}),
    scenario(shader_canvas_size=[0,480]),scenario(shader_canvas_size=[854.5,480]),
    scenario(unknown_setting=1),scenario(audio_band_ranges={'bass':[0,10**400]}),
])
def test_malformed_unbounded_or_unknown_scenario_inputs_are_rejected(bad):
    from source_input_scenario import validate_scenario
    with pytest.raises(ValueError):validate_scenario(bad)


def test_scenario_identity_is_semantic_and_different_ranges_have_different_hashes():
    from source_input_scenario import validate_scenario
    a=validate_scenario(scenario(audio_band_ranges={'bass':[0,2]}))
    b=validate_scenario(scenario(audio_band_ranges={'bass':[0,3]}))
    assert a['record_sha256']!=b['record_sha256']
    assert a['scalar_input_domains']['bass']==a['scalar_input_domains']['_c3.x']==[0,2]


def test_volume_scenario_does_not_bind_an_eel_custom_register_named_vol():
    from source_input_scenario import validate_scenario
    r=validate_scenario(scenario(audio_band_ranges={'vol':[0,2]}))
    assert r['scalar_input_domains']=={'_c3.w':[0,2]}


def test_cache_identity_separates_declared_scenarios_and_unconstrained_export(tmp_path):
    from effect_family_export import export_preset
    from test_core2331_warp import BINARIES
    p=tmp_path/'ripple.milk';p.write_text('[preset00]\ncomp_1=`shader_body {ret=GetPixel(uv+float2(.02*bass*sin(uv.y*8),0));}\n')
    cache=tmp_path/'cache';reader=BINARIES/'milk-native-reader'
    plain,_=export_preset(p,reader=reader,cache=cache)
    a,hit=export_preset(p,reader=reader,cache=cache,input_scenario=scenario(audio_band_ranges={'bass':[0,2]}))
    b,_=export_preset(p,reader=reader,cache=cache,input_scenario=scenario(audio_band_ranges={'bass':[0,3]}))
    assert hit is False
    assert len({plain['cache_key'],a['cache_key'],b['cache_key']})==3
    again,hit=export_preset(p,reader=reader,cache=cache,input_scenario=scenario(audio_band_ranges={'bass':[0,2]}))
    assert hit is True and again==a


def test_cli_records_scenario_identity_and_refuses_changed_scenario(tmp_path,monkeypatch):
    import json
    import effect_family_export as export
    from test_core2331_warp import BINARIES
    from test_effect_family_export import preset
    source=tmp_path/'sources';source.mkdir();preset(source,'one.milk')
    context=tmp_path/'scenario.json';context.write_text(json.dumps(scenario(audio_band_ranges={'bass':[0,2]})))
    real=export.read_source
    def mutate(path,*args,**kwargs):
        r=real(path,*args,**kwargs)
        if path.name=='one.milk':context.write_text(json.dumps(scenario(audio_band_ranges={'bass':[0,3]})))
        return r
    monkeypatch.setattr(export,'read_source',mutate)
    output=tmp_path/'output'
    assert export.main([str(source),'--reader',str(BINARIES/'milk-native-reader'),'--output',str(output),'--input-scenario',str(context)])==2
    manifest=json.loads((output/'run-manifest.json').read_text())
    assert manifest['configuration']['input_scenario_file_sha256']


def test_api_freezes_caller_scenario_before_native_read(tmp_path,monkeypatch):
    import effect_family_export as export
    from test_core2331_warp import BINARIES
    from test_effect_family_export import preset
    request=scenario(audio_band_ranges={'bass':[0,2]});real=export.read_source
    def mutate(path,*args,**kwargs):
        request['audio_band_ranges']['bass'][1]=3
        return real(path,*args,**kwargs)
    monkeypatch.setattr(export,'read_source',mutate)
    r,_=export.export_preset(preset(tmp_path),reader=BINARIES/'milk-native-reader',input_scenario=request)
    assert r['analysis']['input_scenario']['audio_band_ranges']['bass']==[0,2]


def test_cli_writes_conditional_scenario_record_and_resume_identity(tmp_path):
    import json
    import effect_family_export as export
    from test_core2331_warp import BINARIES
    from test_effect_family_export import preset
    source=tmp_path/'sources';source.mkdir();preset(source,'one.milk')
    context=tmp_path/'scenario.json';context.write_text(json.dumps(scenario(shader_canvas_size=[854,480])))
    output=tmp_path/'output'
    args=[str(source),'--reader',str(BINARIES/'milk-native-reader'),'--output',str(output),'--input-scenario',str(context)]
    assert export.main(args)==0
    r=json.loads((output/'results/one.json').read_text())
    assert r['analysis']['input_scenario']['shader_canvas_size']==[854,480]
    assert r['provenance']['input_scenario_sha256']==r['analysis']['input_scenario']['record_sha256']
    assert export.main(args)==0


def test_cli_rejects_oversized_json_audio_integer_cleanly(tmp_path):
    import json
    import effect_family_export as export
    from test_core2331_warp import BINARIES
    context=tmp_path/'huge.json';context.write_text(json.dumps(scenario(audio_band_ranges={'bass':[0,10**400]})))
    assert export.main([str(tmp_path),'--reader',str(BINARIES/'milk-native-reader'),'--output',str(tmp_path/'output'),'--input-scenario',str(context)])==2


def test_scenario_bounds_audio_driven_image_offset_without_changing_default():
    s=shader('shader_body {ret=GetPixel(uv+float2(.05*bass*pow(GetBlur1(uv).r,2),0));}')
    plain=analyze(s)['visual_description']['sampling_geometry']['stages']['composite'][0]['sample_value_offset_envelope']
    declared=analyze(s,input_scenario=scenario(audio_band_ranges={'bass':[0,2]}))
    r=declared['visual_description']['sampling_geometry']['stages']['composite'][0]['sample_value_offset_envelope']
    assert r['offset_range_uv']==plain['offset_range_uv']==[None,[0,0]]
    extra=r['scenario_offset_envelope']
    assert extra['offset_range_uv'][0]==pytest.approx([0,.1],abs=2e-8)
    assert extra['source_model']=='sample_value_offset_bounds'
    assert extra['input_scenario_sha256']==declared['input_scenario']['record_sha256']
    assert r['visible_motion_intensity'] is None


def test_scenario_bounds_texel_sized_image_offsets_with_authored_canvas():
    s=shader('shader_body {ret=GetPixel(uv+12*texsize.zw*(GetPixel(uv).rg-.5));}')
    r=analyze(s,input_scenario=scenario(shader_canvas_size=[854,480]))['visual_description']['sampling_geometry']['stages']['composite'][0]['sample_value_offset_envelope']
    assert r['offset_range_uv']==[None,None]
    spans=r['scenario_offset_envelope']['offset_range_uv']
    assert spans[0]==pytest.approx([-6/854,6/854],rel=2e-7)
    assert spans[1]==pytest.approx([-6/480,6/480],rel=2e-7)
    assert r['full_coordinate_sensitivity'] is None


def test_scenario_cannot_hide_image_domain_singularity_or_dynamic_scale():
    for code in ('ret=GetPixel(uv+float2(bass/GetPixel(uv).r,0));', 'ret=GetPixel(uv*(1+bass*GetPixel(uv).r));'):
        r=analyze(shader('shader_body {'+code+'}'),input_scenario=scenario(audio_band_ranges={'bass':[0,2]}))['visual_description']['sampling_geometry']['stages']['composite'][0]['sample_value_offset_envelope']
        extra=r['scenario_offset_envelope']
        assert extra['source_model']!='sample_value_offset_bounds'
        assert extra['offset_range_uv'] is None or extra['offset_range_uv'][0] is None


def test_sample_offset_scenario_without_required_canvas_stays_unresolved():
    s=shader('shader_body {ret=GetPixel(uv+12*texsize.zw*(GetPixel(uv).rg-.5));}')
    r=analyze(s,input_scenario=scenario(audio_band_ranges={'bass':[0,2]}))['visual_description']['sampling_geometry']['stages']['composite'][0]['sample_value_offset_envelope']
    assert r['scenario_offset_envelope']['source_model']=='unknown'
    assert r['scenario_offset_envelope']['offset_range_uv']==[None,None]


def test_declared_audio_bounds_time_component_of_texture_translation():
    s=shader('shader_body {ret=GetPixel(uv+float2(.01*sin(time*bass),0));}')
    plain=analyze(s)['visual_description']['sampling_geometry']['stages']['composite'][0]['offset_controls'][0]
    a=analyze(s,input_scenario=scenario(audio_band_ranges={'bass':[0,2]}))
    r=a['visual_description']['sampling_geometry']['stages']['composite'][0]['offset_controls'][0]
    assert r['maximum_absolute_control_rate_per_second']==plain['maximum_absolute_control_rate_per_second'] is None
    extra=r['scenario_time_component']
    assert extra['maximum_absolute_control_rate_per_source_second']==pytest.approx(.02,abs=2e-8)
    assert extra['input_scenario_sha256']==a['input_scenario']['record_sha256']
    assert extra['visible_motion_speed'] is None


def test_time_component_without_required_audio_range_stays_unbounded():
    s=shader('shader_body {ret=GetPixel(uv+float2(.01*sin(time*bass),0));}')
    r=analyze(s,input_scenario=scenario(audio_band_ranges={'mid':[0,2]}))['visual_description']['sampling_geometry']['stages']['composite'][0]['offset_controls'][0]
    assert r['scenario_time_component']['maximum_absolute_control_rate_per_source_second'] is None


def test_time_switched_texture_translation_has_no_continuous_time_bound():
    s=shader('shader_body {ret=GetPixel(uv+float2(time>1 ? .01 : .05,0));}')
    r=analyze(s,input_scenario=scenario())['visual_description']['sampling_geometry']['stages']['composite'][0]['offset_controls'][0]
    assert r['scenario_time_component']['maximum_absolute_control_rate_per_source_second'] is None


def test_nominal_time_component_does_not_claim_total_native_clock_or_motion():
    from shader_fields import Field
    from source_motion import motion_control
    from source_input_scenario import validate_scenario
    f=Field('add',(Field('input',detail={'name':'time'}),Field('input',detail={'name':'frame'})),'float')
    r=motion_control(f,'x','UV',application='test',input_scenario=validate_scenario(scenario()))
    extra=r['scenario_time_component']
    assert extra['maximum_absolute_control_rate_per_source_second']==pytest.approx(1)
    assert 'frame' in extra['held_fixed_input_names']
    assert extra['total_control_rate_per_second'] is None


def test_shape_geometry_control_receives_declared_time_component():
    from test_effect_families import read
    s=read('shapecode_0_enabled=1\nshape_0_per_frame1=x=.5+.1*sin(time*bass);\n')
    a=analyze(s,input_scenario=scenario(audio_band_ranges={'bass':[0,2]}))
    controls=[c for e in a['visual_description']['elements'] for c in e.get('motion_controls',[]) if c['control']=='position_x']
    assert controls
    assert controls[0]['scenario_time_component']['maximum_absolute_control_rate_per_source_second']==pytest.approx(.2,abs=2e-8)


def test_quantized_q_time_upload_retains_unknown_time_component():
    from test_effect_families import read
    s=read('per_frame_1=q1=.1*time;\ncomp_1=`shader_body {ret=GetPixel(uv+float2(sin(q1),0));}\n')
    r=analyze(s,input_scenario=scenario())['visual_description']['sampling_geometry']['stages']['composite'][0]['offset_controls'][0]
    assert r['scenario_time_component']['maximum_absolute_control_rate_per_source_second'] is None
