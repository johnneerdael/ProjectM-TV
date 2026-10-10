"""Source dependency projection must preserve typed coercion before swizzling."""
import pytest
from shader_fields import Field
from test_effect_families import shader,analyze,families


def test_scalar_broadcast_projection_keeps_a_valid_second_lane():
    from effect_families import _project,_deps
    t=Field('input',dtype='float',detail={'name':'time'})
    vector=Field('cast',(t,),'float3',{'target_type':'float3'})
    selected=_project(vector,(1,))
    assert selected.op!='unknown'
    assert selected.dtype=='float'
    assert _deps(selected)=={'time'}


@pytest.mark.parametrize('code',[
    'float3 c=sin(time);ret=c.g;',
    'float3 c=(float3)sin(time);ret=c.b;',
    'float3 c=GetPixel(uv).r;ret=c.b;',
    'float3 c=(float3)(int)time;ret=c.b;',
])
def test_authored_broadcast_lanes_do_not_report_false_projection_gaps(code):
    r=analyze(shader('shader_body {'+code+'}'))
    assert not any('component projection exceeds type' in x['reason'] for x in r['unknowns'])


def test_dynamic_integer_conversion_survives_dependency_projection():
    from effect_families import _project,_walk
    t=Field('input',dtype='float',detail={'name':'time'})
    integer=Field('cast',(t,),'int',{'target_type':'int','explicit_source_cast':True})
    vector=Field('cast',(integer,),'float3',{'target_type':'float3'})
    selected=_project(vector,(2,))
    assert any(n.op=='cast' and n.dtype=='int' for n,p in _walk(selected))


def test_literal_integer_conversion_is_not_erased_by_projection():
    from effect_families import _project,_number
    source=Field('constant',dtype='float',detail={'value':.8})
    integer=Field('cast',(source,),'int',{'target_type':'int','explicit_source_cast':True})
    vector=Field('cast',(integer,),'float3',{'target_type':'float3'})
    assert _number(_project(vector,(2,)))==0


def test_narrowed_scalar_broadcast_retains_upload_conversion():
    from effect_families import _project,_walk
    source=Field('input',dtype='float',detail={'name':'time'})
    narrowed=Field('narrow',(source,),'float',{'numeric_domain':'shader-float32'})
    vector=Field('cast',(narrowed,),'float3',{'target_type':'float3'})
    assert any(n.op=='narrow' for n,p in _walk(_project(vector,(1,))))


def test_truncated_fourth_lane_cannot_supply_an_effect_after_swizzling():
    code='shader_body {float3 c=(float3)float4(1,0,0,GetPixel(float2(ang,1/rad)).r);ret=c.gbr;}'
    assert 'polar_radial_sampling' not in families(analyze(shader(code)))


def test_consumed_sample_broadcast_keeps_its_source_effect():
    code='shader_body {float3 c=GetPixel(float2(ang,1/rad)).r;ret=c.b;}'
    assert 'polar_radial_sampling' in families(analyze(shader(code)))


def test_genuinely_out_of_range_component_is_still_unknown():
    from effect_families import _project
    assert _project(Field('input',dtype='float2',detail={'name':'p'}),(2,)).op=='unknown'


@pytest.mark.parametrize('coordinate',[
    'c.xy',
    'normalize(c)',
    'float2(c.x,c.y)',
])
def test_shortened_vector_never_reads_discarded_source_lane(coordinate):
    code='shader_body {float2 c=(float2)float3(uv,GetPixel(float2(ang,1/rad)).r);ret=GetPixel('+coordinate+');}'
    assert 'polar_radial_sampling' not in families(analyze(shader(code)))


def test_explicit_scalar_cast_uses_first_vector_lane_only():
    code='shader_body {float c=(float)float3(uv.x,0,GetPixel(float2(ang,1/rad)).r);ret=c;}'
    assert 'polar_radial_sampling' not in families(analyze(shader(code)))


def test_constructor_width_conversion_does_not_read_extra_source_lanes():
    code='shader_body {float2 c=float2(float3(uv,GetPixel(float2(ang,1/rad)).r));ret=GetPixel(c.xy);}'
    assert 'polar_radial_sampling' not in families(analyze(shader(code)))


def test_scalar_numeric_conversion_traversal_does_not_reconstruct_itself():
    from effect_families import _children
    source=Field('input',dtype='float',detail={'name':'time'})
    integer=Field('cast',(source,),'int',{'target_type':'int','explicit_source_cast':True})
    converted=Field('cast',(integer,),'float',{'target_type':'float'})
    assert _children(converted)==(integer,)


def test_repeated_subtree_membership_reuses_complete_strong_node_inventory():
    from effect_families import _CACHE,_masked_by_output
    leaf=Field('input',detail={'name':'value'})
    root=Field('multiply',(leaf,Field('constant',detail={'value':2.})),'float')
    cache={};token=_CACHE.set(cache)
    try:
        assert _masked_by_output(root,leaf)
        visits=cache['field_visits']
        assert _masked_by_output(root,leaf)
        assert not _masked_by_output(root,Field('input',detail={'name':'value'}))
        assert cache['field_visits']==visits
        assert not _masked_by_output(Field('multiply',(leaf,Field('constant',detail={'value':0.})),'float'),leaf)
    finally:_CACHE.reset(token)


def test_shared_leaf_masked_and_unmasked_routes_are_both_considered():
    from effect_families import _CACHE,_masked_by_output
    leaf=Field('input',detail={'name':'shared'})
    other=Field('input',detail={'name':'gain'})
    root=Field('add',(leaf,Field('multiply',(leaf,other),'float')),'float')
    token=_CACHE.set({})
    try:
        assert _masked_by_output(root,leaf)
        assert not _masked_by_output(Field('add',(leaf,other),'float'),leaf)
    finally:_CACHE.reset(token)


def test_failed_budget_walk_cannot_publish_partial_multiplier_inventory(monkeypatch):
    import effect_families as f
    leaf=Field('input',detail={'name':'value'})
    root=Field('multiply',(leaf,Field('constant',detail={'value':2.})),'float')
    cache={};token=f._CACHE.set(cache)
    try:
        monkeypatch.setattr(f,'MAX_FIELD_VISITS',1)
        with pytest.raises(ValueError,match='traversal budget exceeded'):f._masked_by_output(root,leaf)
        assert ('output_multiplier_nodes',id(root)) not in cache
    finally:f._CACHE.reset(token)


def test_mask_condition_remains_equivalent_without_an_analysis_cache():
    from effect_families import _CACHE,_masked_by_output
    leaf=Field('input',detail={'name':'time'})
    integer=Field('cast',(leaf,),'int',{'target_type':'int','explicit_source_cast':True})
    vector=Field('cast',(integer,),'float3',{'target_type':'float3'})
    root=Field('multiply',(vector,Field('input',detail={'name':'gain'})),'float3')
    token=_CACHE.set(None)
    try:assert _masked_by_output(root,leaf)
    finally:_CACHE.reset(token)


@pytest.mark.parametrize('name',['flexi - grind my glitch up [237].milk','flexi - grind my glitch up [342].milk'])
def test_exact_random_pool_grind_profile_keeps_structured_description(name):
    import json
    from pathlib import Path
    from effect_family_export import export_preset
    root=Path(__file__).resolve().parents[2]
    proof=json.loads((root/'build/preset-corpus/source-random-2000-2026-10-10/results-run/compatibility'/Path(name).with_suffix('.json')).read_text())
    scenario=json.loads((root/'build/preset-corpus/source-sample-offset-scenario.json').read_text())
    r,hit=export_preset(root/'core/src/main/assets/presets'/name,
        reader=root/'build/preset-corpus/source34/adapters/milk-native-reader',compatibility=proof['reports'],input_scenario=scenario)
    assert 'sampling_geometry' in r['analysis']['visual_description']
    assert not any('static field traversal budget exceeded' in x['reason'] for x in r['analysis']['unknowns'])
