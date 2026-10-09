"""Native roaming uniforms retain their unwrapped float32 clock identity."""
import math
import numpy as np
import pytest
from test_effect_families import shader
from test_source_appearance import appearance


def colour(body):
    d=appearance(shader('shader_body{'+body+'}'))
    return d,d['elements'][0]['colour']


def test_native_roam_rgb_has_independent_source_rates_and_clock():
    d,c=colour('ret=roam_cos.rgb;')
    assert c['mode_code']==5
    assert c['depends_on_time']==1
    assert c['bias_rgb']==[.5,.5,.5]
    assert c['amplitude_rgb']==[.5,.5,.5]
    t=c['temporal']
    assert t['angular_rate_rad_per_second_rgb']==pytest.approx([.329,1.293,5.07],abs=3e-7)
    assert t['clock_kinds_rgb']==[['native_render_time_float32']]*3
    assert t['shader_time_wrap_seconds'] is None
    assert t['visible_flash_frequency_hz'] is None


def test_slow_native_sine_preserves_function_and_long_periods():
    d,c=colour('ret=slow_roam_sin.rgb;')
    assert c['mode_code']==5
    assert c['oscillator_function_codes']==[2,2,2]
    assert c['temporal']['period_seconds_rgb']==pytest.approx([math.tau/.005,math.tau/.0085,math.tau/.0133],rel=2e-7)


def test_mixed_shader_and_native_clock_retains_shader_reset_condition():
    d,c=colour('ret=.5+.5*cos(time+float3(0,2,4))+roam_cos.rgb*.2;')
    # Two oscillators per channel remain outside the current palette rule.
    assert c['mode_code'] is None
    record=d['native_input_bindings']['time_oscillators']
    assert record['native_clock_input']==':native-render-time-f32'
    assert record['observed_runtime_binding'] is False


def test_authored_shader_clock_still_wraps_and_uses_its_own_basis():
    d,c=colour('ret=.5+.5*cos(time+float3(0,2,4));')
    assert c['temporal']['clock_kinds_rgb']==[['shader_time_wrapped']]*3
    assert c['temporal']['shader_time_wrap_seconds']==10000


def test_native_uniform_formulas_match_independent_trigonometric_values():
    from source_uniforms import native_time_component_fields
    from field_math import evaluate
    fields=native_time_component_fields()
    for time in (0.,1.,10001.):
        value=evaluate(fields['_c8'][0],inputs={':native-render-time-f32':time})
        native_time=np.float32(time);rate=np.float32(.329);offset=np.float32(1.2)
        expected=np.float32(.5)+np.float32(.5)*np.cos(np.float32(native_time*rate+offset))
        assert value==pytest.approx(expected,abs=2e-7)


def test_local_roam_uniform_name_shadowing_is_not_overwritten():
    d,c=colour('float4 _c8=float4(.2,.3,.4,.5);ret=float3(_c8.r,_c8.g,_c8.b);')
    assert not any(n['op']=='input' and n['detail'].get('name')==':native-render-time-f32'
                   for channel in d['colour_processing']['stages']['composite']['channels']
                   for n in (channel['base'].get('expression') or {}).get('nodes',[]))
