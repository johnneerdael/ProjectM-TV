"""Typed literal vector projections remain source arithmetic, not image labels."""
import pytest
from test_effect_families import shader,read
from test_source_appearance import appearance


def rgb(body):
    d=appearance(shader('shader_body{'+body+'}'))
    return d['elements'][0]['colour']['constant_rgb']


def test_constructor_swizzle_exports_constant_rgb_without_opaque_members():
    assert rgb('float4 c=float4(.2,.3,.4,.5);ret=c.bgr;')==pytest.approx([.4,.3,.2],abs=2e-7)


def test_nested_vector_members_retain_declared_channel_order():
    assert rgb('float4 c=float4(.2,.3,.4,.5);float3 d=c.wxy;ret=d.yzx;')==pytest.approx([.2,.3,.5],abs=2e-7)


def test_integer_vector_conversion_keeps_truncation_before_float_output():
    assert rgb('int3 c=int3(.2,1.9,-.9);ret=c.zyx;')==[0,1,0]


def test_literal_vector_arithmetic_can_resolve_source_colour():
    assert rgb('float3 c=float3(.1,.2,.3)+float3(.2,.3,.4);ret=c.rgb;')==pytest.approx([.3,.5,.7],abs=2e-7)


def test_nonliteral_vector_members_do_not_invent_constant_colour():
    assert rgb('float4 c=tex2D(sampler_main,uv);ret=c.bgr;') is None


def test_discarded_unknown_fourth_lane_does_not_block_literal_rgb():
    assert rgb('float4 c=float4(.2,.3,.4,bass);ret=c.rgb;')==pytest.approx([.2,.3,.4],abs=2e-7)


def test_local_native_uniform_shadow_can_now_expose_its_literal_colour():
    assert rgb('float4 _c5=float4(.2,.3,.4,.5);ret=_c5.rgb;')==pytest.approx([.2,.3,.4],abs=2e-7)
