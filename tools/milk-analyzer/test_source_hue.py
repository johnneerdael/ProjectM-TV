"""Native hue construction before authored shader colour processing."""
import math
import numpy as np
import pytest
from test_effect_families import shader,analyze,read,PRESETS
from test_source_appearance import appearance


def hue(body):
    d=appearance(shader('shader_body{'+body+'}'))
    return next(e for e in d['elements'] if e['id']=='shader_composite').get('native_colour_generators',[])


def test_consumed_native_hue_has_corner_formula_and_interpolation_contract():
    h=hue('ret=hue_shader;')[0]
    assert h['generator_code']==10
    assert h['consumed_rgb_components']==[0,1,2]
    assert h['raw_corner']['bias_rgb']==[float(np.float32(.6))]*3
    assert h['raw_corner']['angular_rate_rad_per_second_rgb']==pytest.approx([.429,.321,.387],abs=2e-8)
    assert h['normalization']['operation']=='0.5+0.5*(raw_channel/max(raw_rgb))'
    assert h['nominal_input_range_rgb']==[[pytest.approx(2/3,abs=2e-7),1]]*3
    assert h['spatial_interpolation']=='corner blend at composite mesh vertices, then triangle interpolation'
    assert h['actual_palette'] is None
    assert h['observed_runtime_binding'] is False


def test_red_only_consumption_does_not_claim_final_multicolour():
    h=hue('ret=hue_shader.r;')[0]
    assert h['consumed_rgb_components']==[0]
    assert h['final_multicolour_guaranteed'] is False


@pytest.mark.parametrize('body',['ret=float4(.1,.2,.3,hue_shader.r);','ret=hue_shader*0;',
    'ret=GetPixel(uv);'])
def test_dead_or_unused_hue_does_not_create_colour_generator(body):
    assert hue(body)==[]


def test_warp_vertex_decay_is_not_a_native_composite_hue_generator():
    d=appearance(shader('shader_body{ret=GetPixel(uv)*_vDiffuse.rgb;}',stage='warp'))
    assert all(not e.get('native_colour_generators') for e in d['elements'])


def test_independent_corner_values_and_convex_blend_match_exported_recipe():
    h=hue('ret=hue_shader;')[0];r=h['raw_corner']
    offsets=[1.25,2.5,3.75,5.]
    corners=[]
    for i in range(4):
        raw=[r['bias_rgb'][c]+r['amplitude_rgb'][c]*math.sin(2*r['angular_rate_rad_per_second_rgb'][c]+r['base_phase_offsets_rgb'][c]+i*r['corner_phase_steps_rgb'][c]+offsets[r['random_offset_indices_rgb'][c]]) for c in range(3)]
        corners.append([.5+.5*v/max(raw) for v in raw])
    weights=[.25,.25,.25,.25]
    output=np.array(weights)@np.array(corners)
    assert np.all(output>=2/3-2e-7) and np.all(output<=1+2e-7)
    assert h['random_phase_values'] is None
    assert h['nominal_unwrapped_clock_input']==':native-render-time-f32'


def test_original_hue_burst_retains_native_hue_recipe():
    d=appearance(read((PRESETS/'Flexi - hue burst.milk').read_bytes()))
    e=next(e for e in d['elements'] if e['id']=='shader_composite')
    assert e['native_colour_generators'][0]['consumed_rgb_components']==[0,1,2]
