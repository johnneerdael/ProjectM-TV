"""Source-bound native blur decoding; dynamic triplets are never default-filled."""
import numpy as np
import pytest
from test_effect_families import read,shader
from test_source_appearance import appearance


def control(source):
    d=appearance(source)
    return d,d['native_input_bindings']['blur_decode']


def test_default_blur_ranges_resolve_packed_inputs_and_gradient_response():
    d,b=control(shader('shader_body{float2 p=(GetBlur1(uv+.01).rg-GetBlur1(uv-.01).rg)*.02;ret=GetPixel(uv+p);}',stage='warp'))
    assert b['status']=='source_constant'
    assert b['packed_components']=={'_c5':[1,0,1,0],'_c6':[1,0,0,1]}
    rs=[m['sampled_coordinate_response'] for m in d['sampling_geometry']['stages']['warp']]
    assert any(r['direct_sample_gain_norm']==pytest.approx(.04,abs=2e-8) for r in rs if r['direct_sample_gain_norm'] is not None)
    assert b['observed_runtime_binding'] is False


def test_per_frame_constants_override_authored_config_before_binding():
    source=read('''b1n=.2
b1x=.8
per_frame_1=blur1_min=.3;blur1_max=.7;
PSVERSION_COMP=2
comp_1=`shader_body{ret=GetBlur1(uv);}
''')
    d,b=control(source)
    assert b['packed_components']['_c5']==pytest.approx([.4,.3,.4,.3],abs=2e-7)


def test_dynamic_any_level_keeps_triplet_unresolved_without_zero_filling():
    source=read('''per_frame_1=blur3_max=bass;
PSVERSION_COMP=2
comp_1=`shader_body{ret=GetBlur1(uv);}
''')
    d,b=control(source)
    assert b['status']=='unresolved'
    assert b['packed_components'] is None
    assert b['unknown_reasons']


def test_native_minimum_gap_hierarchy_and_fallback_are_preserved():
    source=read('''b1n=.5
b1x=.5
b2n=.8
b2x=.2
PSVERSION_COMP=2
comp_1=`shader_body{ret=GetBlur2(uv);}
''')
    d,b=control(source)
    from blur import native_ranges,CORE_2315_BLUR
    lo,hi=native_ranges([.5,.8,0],[.5,.2,1],policy=CORE_2315_BLUR)
    expected=[float(np.float32(hi[0]-lo[0])),float(lo[0]),float(np.float32(hi[1]-lo[1])),float(lo[1])]
    assert b['packed_components']['_c5']==expected


def test_extreme_finite_known_config_uses_target_coherent_default_policy():
    source=read('''per_frame_1=blur1_min=1e100;
PSVERSION_COMP=2
comp_1=`shader_body{ret=GetBlur1(uv);}
''')
    d,b=control(source)
    assert b['status']=='source_constant'
    assert b['packed_components']['_c5']==[1,0,1,0]


def test_initial_audio_cannot_be_mistaken_for_a_known_frame_blur_input():
    source=read('''per_frame_init_1=blur1_max=bass;
PSVERSION_COMP=2
comp_1=`shader_body{ret=GetBlur1(uv);}
''')
    d,b=control(source)
    assert b['packed_components']['_c5']==[1,0,1,0]


def test_local_uniform_name_shadowing_preserves_authored_source_value():
    source=shader('shader_body{float4 _c5=float4(.2,.3,.4,.5);ret=_c5.rgb;}')
    d,b=control(source)
    channels=d['colour_processing']['stages']['composite']['channels']
    # The descriptor currently keeps member-of-constructor colour opaque, but
    # its source DAG must preserve the authored local, not the packed binding.
    values=[n['detail']['value'] for n in channels[0]['base']['expression']['nodes'] if n['op']=='constant']
    assert values==pytest.approx([.2,.3,.4,.5],abs=2e-7)
    assert b['packed_components']['_c5']==[1,0,1,0]
