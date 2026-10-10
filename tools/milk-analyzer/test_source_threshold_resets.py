"""Threshold reset mechanisms quantify source jumps, not observed flashes."""
import pytest
from test_effect_families import shader
from test_source_appearance import appearance


def resets(code):
    d=appearance(shader('shader_body {'+code+'}'))
    return [h for h in d['activity']['flashing']['hazards'] if h['kind']=='shader_channel_threshold_reset']


def test_sample_threshold_reset_has_exact_nominal_boundary_jump():
    rows=resets('float3 c=GetPixel(uv);ret=c;if(c.r>.7){ret.r=0;}')
    assert len(rows)==1
    r=rows[0]
    assert r['channel']=='r'
    assert r['absolute_nominal_boundary_jump']==pytest.approx(.7,rel=1e-6)
    assert r['trigger_source_kind']=='sampled_image'
    assert r['visible_flashing_verified'] is False


def test_three_channel_resets_are_local_channel_mechanisms():
    rows=resets('ret=GetPixel(uv);if(ret.r>.7){ret.r=0;}if(ret.g>.7){ret.g=0;}if(ret.b>.7){ret.b=0;}')
    assert {r['channel'] for r in rows}=={'r','g','b'}
    assert all(r['whole_frame_blackout_verified'] is False for r in rows)


def test_unreachable_unit_sample_threshold_does_not_claim_reset():
    assert resets('ret=GetPixel(uv);if(ret.r>2){ret.r=0;}')==[]


def test_continuous_clamp_at_threshold_has_no_boundary_jump():
    assert resets('ret=GetPixel(uv);if(ret.r>.7){ret.r=.7;}')==[]


def test_time_driven_reset_retains_nominal_event_schedule():
    r=resets('ret=.5+.5*sin(3*time);if(ret.r>.7){ret.r=0;}')[0]
    assert r['trigger_source_kind']=='source_time'
    assert r['nominal_crossing_event_rate_hz']==pytest.approx(3/3.141592653589793,rel=1e-6)


def test_nested_colour_transfer_does_not_claim_whole_output_jump():
    assert resets('float c=GetPixel(uv).r;if(c>.7){c=0;}ret=c*c;')==[]


def test_known_singular_channel_cannot_certify_threshold_jump():
    assert resets('ret=GetPixel(uv)*(1/0);if(ret.r>.7){ret.r=0;}')==[]


def test_reversed_comparison_and_false_branch_have_same_boundary_gap():
    r=resets('float c=GetPixel(uv).r;ret=c;if(.7>=c){ret.r=c;}else{ret.r=.1;}')[0]
    assert r['reset_branch']=='false'
    assert r['absolute_nominal_boundary_jump']==pytest.approx(.6,rel=1e-6)


def test_singular_redundant_predicate_is_not_removed_from_domain_check():
    assert resets('ret=GetPixel(uv);if(ret.r>.7){ret.r=0;}if(1/0>0){ret.r=ret.r;}')==[]


def test_integer_quantized_signal_does_not_invent_a_boundary_jump():
    assert resets('ret=(int)(GetPixel(uv).r*4);if(ret.r>.7){ret.r=0;}')==[]


@pytest.mark.parametrize('signal,comparison',[
    ('floor(GetPixel(uv).r*4)', '>.7'),
    ('floor(GetPixel(uv).r*4)', '>=2'),
    ('frac(GetPixel(uv).r*4)', '>.7'),
    ('GetPixel(uv).r>.5', '>.7'),
])
def test_discontinuous_signal_requires_a_separate_transition_proof(signal,comparison):
    assert resets('ret='+signal+';if(ret.r'+comparison+'){ret.r=0;}')==[]
