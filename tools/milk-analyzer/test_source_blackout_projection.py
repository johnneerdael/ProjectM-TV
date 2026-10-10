"""Colour gate projection excludes lookup geometry without hiding its domains."""
import pytest
from shader_fields import Field


def projection(field):
    import source_activity
    assert hasattr(source_activity,'blackout_colour_channels'),'bounded colour-gate projection missing'
    return source_activity.blackout_colour_channels(field)


def test_large_sample_coordinate_is_preserved_as_leaf_without_colour_expansion():
    uv=Field('input',dtype='float2',detail={'name':'_uv'})
    coordinate=uv
    for _ in range(700):coordinate=Field('add',(coordinate,uv),'float2')
    sample=Field('sample',(coordinate,),'float4',{'canonical_texture':'main','site_index':1})
    gate=Field('greater',(Field('sin',(Field('input',detail={'name':'time'}),)),Field('constant',detail={'value':0.})),'bool')
    values=Field('multiply',(sample,Field('cast',(gate,),'float4',{'target_type':'float4'})),'float4')
    channels=projection(values)
    from source_appearance import _colour_product
    for channel in channels:
        _,factors=_colour_product(channel)
        assert any(f.op=='cast' and f.dtype=='float' and f.args[0].op=='greater' and
            f.args[0].dtype=='bool' for f in factors)
        lane=next(f for f in factors if f.op=='member')
        assert lane.args[0] is sample
        assert sample.args[0] is coordinate


def test_numeric_cast_of_rgb_does_not_become_an_unquantized_product():
    colour=Field('input',dtype='float3',detail={'name':'colour'})
    integer=Field('cast',(colour,),'int3',{'target_type':'int3'})
    channels=projection(Field('cast',(integer,),'float3',{'target_type':'float3'}))
    from effect_families import _walk
    for channel in channels:
        assert any(n.dtype=='int' for n,_ in _walk(channel))


def test_large_non_sample_colour_graph_keeps_projection_budget_guard():
    node=Field('input',detail={'name':'time'})
    for _ in range(700):node=Field('sin',(node,),'float')
    with pytest.raises(ValueError,match='activity scalar projection budget'):projection(node)


def test_known_invalid_texture_coordinate_still_prevents_blackout_certificate():
    from test_effect_families import shader
    from test_source_appearance import appearance
    d=appearance(shader('shader_body {ret=GetPixel(uv/0)*(sin(time*6)>0);}'))
    flashing=d['activity']['flashing']
    assert not any(h['kind']=='full_stage_blackout_gate' for h in flashing['hazards'])
    assert 'Known invalid' in flashing['unknown_reasons'][0]
