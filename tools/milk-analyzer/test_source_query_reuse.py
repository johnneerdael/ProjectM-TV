"""Reuse immutable source graph facts without changing their semantics or budgets."""
from pathlib import Path
import json
import pytest
from shader_fields import Field


@pytest.mark.parametrize('name',['_angle','_radius'])
def test_repeated_spatial_presence_probe_reuses_strong_identity(name):
    import effect_families as f
    field=Field('sin',(Field('input',detail={'name':'time'}),),'float')
    token=f._CACHE.set({})
    try:
        probe=getattr(f,name);assert probe(field) is False
        visits=f._CACHE.get()['field_visits']
        assert probe(field) is False
        assert f._CACHE.get()['field_visits']==visits
        special=Field('input',detail={'name':'ang' if name=='_angle' else 'rad'})
        assert probe(special) is True
    finally:f._CACHE.reset(token)


def test_coordinate_uniform_query_separates_basis_inputs():
    from source_sampling import _uniform_for_bases
    from effect_families import _CACHE
    field=Field('input',dtype='float4',detail={'name':'custom_basis'})
    token=_CACHE.set({})
    try:
        assert _uniform_for_bases(field,('_uv',)) is True
        assert _uniform_for_bases(field,('custom_basis',)) is False
        before=_CACHE.get()['field_visits']
        assert _uniform_for_bases(field,('_uv',)) is True
        assert _CACHE.get()['field_visits']==before
    finally:_CACHE.reset(token)


@pytest.mark.parametrize('op',['sample','unknown','uninitialized','loop_result'])
def test_coordinate_uniform_reuse_does_not_hide_unsafe_input_classes(op):
    from source_sampling import _uniform_for_bases
    from effect_families import _CACHE
    node=Field(op,dtype='float4')
    token=_CACHE.set({})
    try:
        assert _uniform_for_bases(node,('_uv',)) is False
        assert _uniform_for_bases(node,('_uv',)) is False
    finally:_CACHE.reset(token)


def test_failed_presence_query_cannot_cache_an_incomplete_negative(monkeypatch):
    import effect_families as f
    from source_sampling import _uniform_for_bases
    node=Field('sin',(Field('input',detail={'name':'time'}),),'float')
    for probe,key in ((f._angle,('angle_presence',id(node))),
                      (f._radius,('radius_presence',id(node))),
                      (lambda x:_uniform_for_bases(x,('_uv',)),('sampling_uniform',id(node),('_uv',)))):
        cache={};token=f._CACHE.set(cache)
        try:
            monkeypatch.setattr(f,'MAX_FIELD_VISITS',1)
            with pytest.raises(ValueError,match='traversal budget exceeded'):probe(node)
            assert key not in cache
        finally:f._CACHE.reset(token)


@pytest.mark.parametrize('name',[
    'flexi - grind my glitch up [230].milk',
    "Flexi + geiss - the deep diver's cognitive dissonance 1's and 0's where they don't belong.milk",
])
def test_remaining_exact_pool_profile_keeps_structured_description(name):
    from effect_family_export import export_preset
    root=Path(__file__).resolve().parents[2]
    proof=json.loads((root/'build/preset-corpus/source-random-2000-2026-10-10/results-run/compatibility'/Path(name).with_suffix('.json')).read_text())
    scenario=json.loads((root/'build/preset-corpus/source-sample-offset-scenario.json').read_text())
    r,hit=export_preset(root/'core/src/main/assets/presets'/name,
        reader=root/'build/preset-corpus/source34/adapters/milk-native-reader',compatibility=proof['reports'],input_scenario=scenario)
    assert 'sampling_geometry' in r['analysis']['visual_description'],r['analysis']['visual_description']
