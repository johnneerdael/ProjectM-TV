"""Nominal named control curves; these do not establish screen/image motion."""
import math
from source_temporal import affine_time_parameters


def motion_control(field,control,unit,*,application):
    from source_appearance import _phase_literal,_phase_terms,_expression
    result={'policy':'source-time-control-curves-v1','control':control,'control_unit':unit,
        'application':application,'curve_kind':'unknown','constant_value':None,
        'offset_value':None,'amplitude_value':None,'oscillator_function_code':None,
        'phase_expression':None,'angular_phase_rate_rad_per_second':None,
        'period_seconds':None,'frequency_hz':None,'nominal_value_range':None,
        'signed_linear_rate_per_second':None,'maximum_absolute_control_rate_per_second':None,
        'rate_unit':unit+'/source-time second','expression':_expression(field),
        'visible_motion_speed':None,'unknown_reasons':[],
        'conditions':['Continuous nominal source-time formula; clock jumps, finite precision and sampled frames excluded',
                      'Control variation does not establish visibility, geometry trajectories after projection, feedback motion or perceived intensity']}
    literal=_phase_literal(field)
    if literal is not None:
        result.update(curve_kind='constant',constant_value=literal,
                      nominal_value_range=[literal,literal],maximum_absolute_control_rate_per_second=0.)
        return result
    pair=affine_time_parameters(field)
    if pair is not None:
        rate,offset=pair
        if rate==0:
            result.update(curve_kind='constant',constant_value=offset,
                          nominal_value_range=[offset,offset],maximum_absolute_control_rate_per_second=0.)
        else:
            result.update(curve_kind='linear_time',offset_value=offset,
                signed_linear_rate_per_second=rate,maximum_absolute_control_rate_per_second=abs(rate))
        return result
    try:terms=_phase_terms(field)
    except ValueError as error:
        result['unknown_reasons']=[str(error)];return result
    bias=0.;osc=None;amplitude=None
    for coefficient,term in terms:
        value=_phase_literal(term)
        if value is not None:bias+=coefficient*value;continue
        if term.op not in {'sin','cos'} or osc is not None:break
        osc=term;amplitude=coefficient
    else:
        if osc is not None:
            phase=affine_time_parameters(osc.args[0])
            if phase is not None and (amplitude==0 or phase[0]==0):
                value=bias if amplitude==0 else bias+amplitude*(math.cos(phase[1]) if osc.op=='cos' else math.sin(phase[1]))
                if math.isfinite(value):
                    result.update(curve_kind='constant',constant_value=value,
                        nominal_value_range=[value,value],maximum_absolute_control_rate_per_second=0.)
                    return result
            if phase is not None and phase[0]!=0:
                rate=phase[0];speed=abs(rate*amplitude);frequency=abs(rate)/math.tau;period=math.tau/abs(rate)
                low,high=bias-abs(amplitude),bias+abs(amplitude)
                if all(math.isfinite(v) for v in (bias,amplitude,speed,frequency,period,low,high)):
                    result.update(curve_kind='sinusoidal_time',offset_value=bias,amplitude_value=amplitude,
                        oscillator_function_code=1 if osc.op=='cos' else 2,
                        phase_expression=_expression(osc.args[0]),angular_phase_rate_rad_per_second=rate,
                        frequency_hz=frequency,period_seconds=period,nominal_value_range=[low,high],
                        maximum_absolute_control_rate_per_second=speed)
                    return result
    result['unknown_reasons']=['control is not a supported constant, affine-time or single affine-time sinusoid']
    return result
