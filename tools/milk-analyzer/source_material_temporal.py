"""Source material variation and conditional native vertex-wrap risk."""
import math
from fractions import Fraction
import numpy as np
from primitives import colour_modulo
from source_motion import motion_control

PERIOD=float(np.float32(256)/np.float32(255))
# The float32 remainder-plus-period operation can reset just below a boundary.
WRAP_MARGIN=2*float(np.spacing(np.float32(PERIOD)))
GROUPS={'centre':('r','g','b','a'),'perimeter':('r2','g2','b2','a2'),
        'border':('border_r','border_g','border_b','border_a')}


def _channel(field,name,group):
    curve=motion_control(field,name,'source colour/opacity component',application='shape colour channel')
    curve={k:v for k,v in curve.items() if k not in {'expression','phase_expression'}}
    result={'group':group,'raw_time_curve':curve,'native_float32_endpoint_domain':None,
        'native_endpoint_domain_singleton':None,'native_value_if_singleton':None,
        'possible_native_wrap_jump':None,'may_be_consumed':True,'unknown_reasons':[]}
    from source_shape_modulo_schedule import modulo_schedule
    result['nominal_modulo_schedule']=modulo_schedule(curve,PERIOD)
    span=curve['nominal_value_range']
    if span is None:
        result['unknown_reasons']=['raw channel has no supported lifetime source envelope'];return result
    with np.errstate(over='ignore',invalid='ignore'):endpoints=[float(np.float32(v)) for v in span]
    if not all(math.isfinite(v) for v in endpoints):
        result['unknown_reasons']=['channel envelope lacks finite native float32 conversion'];return result
    result['native_float32_endpoint_domain']=endpoints
    singleton=endpoints[0]==endpoints[1]
    result['native_endpoint_domain_singleton']=singleton
    if singleton:
        result['native_value_if_singleton']=float(colour_modulo(endpoints[0]))
        result['possible_native_wrap_jump']=False
        result['nominal_modulo_schedule']=modulo_schedule(curve,PERIOD,native_singleton=True)
    elif curve['maximum_absolute_control_rate_per_second']==0 and curve['nominal_continuity']!='unknown':
        result['possible_native_wrap_jump']=False
    else:
        # Is a wrap boundary k*m in (lo, hi+margin]? Exact rational comparison
        # avoids losing modulo-cell identity for large finite float32 inputs.
        low,high=map(Fraction,endpoints);period=Fraction(PERIOD);margin=Fraction(WRAP_MARGIN)
        first=low//period+1;last=(high+margin)//period
        result['possible_native_wrap_jump']=first<=last
    return result


def shape_material_temporal(controls):
    channels={name:_channel(controls[name],name,group) for group,names in GROUPS.items() for name in names}
    threshold=float(np.float32(.0001));curve=channels['border_a']['raw_time_curve']
    span=curve['nominal_value_range'];always=None;change=None
    if span is not None:
        if span[1]<=threshold:always=False;change=False
        elif span[0]>threshold:always=True;change=False
        else:change=True
    if always is False:
        for name in GROUPS['border']:channels[name]['may_be_consumed']=False
    if all(channels[name]['native_value_if_singleton']==0 for name in ('a','a2')):
        for group in ('centre','perimeter'):
            for name in GROUPS[group]:channels[name]['may_be_consumed']=False
    active=[c['possible_native_wrap_jump'] for c in channels.values() if c['may_be_consumed']]
    risk=True if True in active else None if None in active else False
    return {'policy':'source-native-shape-material-temporal-v1','channels':channels,
        'native_modulo_period':PERIOD,'native_wrap_margin':WRAP_MARGIN,
        'possible_consumed_wrap_jump':risk,
        'border_gate':{'comparison':'raw border_a > threshold','threshold':threshold,
                       'nominal_always_enabled':always,'possible_state_change':change},
        'visible_flashing':None,'visible_flash_frequency_hz':None,
        'uses_equation_execution':False,'uses_rendered_images':False,
        'conditions':['Channel source envelopes and float32 endpoint domains are conditional on supported nominal source formulas',
                      'Possible wrap risk includes a two-period-ULP margin below each modulo boundary; it is not an observed event or certified absence of all numeric steps',
                      'A singleton endpoint domain means all values in the supplied envelope cast to one float32 value; native constant conversion uses the established colour function',
                      'Border draw gating uses raw double alpha and the native float32 threshold, separately from modulo alpha',
                      'Fill channels are excluded only when both native fan endpoint alphas are proved zero under finite ordinary source-alpha blending; one transparent endpoint still participates through interpolation',
                      'Textures, opacity, primitive coverage, clipping, sampling, storage, feedback and later shaders determine visibility; no whole-preset Chill eligibility follows']}
