"""Nominal named control curves; these do not establish screen/image motion."""
import math
from source_temporal import affine_time_parameters


def motion_control(field,control,unit,*,application):
    from source_appearance import _phase_literal,_phase_terms,_expression
    result={'policy':'source-time-control-curves-v1','control':control,'control_unit':unit,
        'application':application,'curve_kind':'unknown','constant_value':None,
        'offset_value':None,'amplitude_value':None,'oscillator_function_code':None,
        'phase_expression':None,'phase_offset_rad':None,'angular_phase_rate_rad_per_second':None,
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
                        phase_expression=_expression(osc.args[0]),phase_offset_rad=phase[1],angular_phase_rate_rad_per_second=rate,
                        frequency_hz=frequency,period_seconds=period,nominal_value_range=[low,high],
                        maximum_absolute_control_rate_per_second=speed)
                    return result
    result['unknown_reasons']=['control is not a supported constant, affine-time or single affine-time sinusoid']
    return result


def planar_trajectory(fields):
    """Join two supported source control curves; no screen-space inference."""
    import numpy as np
    from fractions import Fraction
    curves=[motion_control(field,axis,'authored shape coordinate',application='shape centre')
            for axis,field in zip(('x','y'),fields)]
    result={'policy':'source-planar-control-trajectory-v1','path_kind':'unknown',
        'center_source_xy':None,'linear_velocity_source_xy':None,
        'harmonic_matrix_source_xy':None,'angular_rate_rad_per_second':None,
        'period_seconds':None,'semiaxis_lengths_source_units':None,
        'maximum_source_speed_units_per_second':None,'speed_estimate_kind':'unknown',
        'axis_curves':curves,'visible_motion_speed':None,'unknown_reasons':[],
        'conditions':['Path and speed use authored x/y coordinates before native projection, clipping and feedback',
                      'Circle/ellipse labels refer to source coordinates; viewport aspect can change physical screen shape',
                      'Nominal continuous formulas exclude floating-point trig/rounding, clock jumps and discrete frames',
                      'A stationary centre does not prove stationary geometry or feedback; radius/rotation/audio/material remain separate']}
    if any(c['curve_kind']=='unknown' for c in curves):
        result['unknown_reasons']=['one or both source axes lack a supported nominal control curve'];return result
    speeds=[c['maximum_absolute_control_rate_per_second'] for c in curves]
    joint_speed=math.hypot(*speeds)
    if not math.isfinite(joint_speed):
        result['unknown_reasons']=['nominal joint speed estimate is nonfinite'];return result
    result.update(maximum_source_speed_units_per_second=joint_speed,speed_estimate_kind='upper_bound')
    if all(c['curve_kind'] in {'constant','linear_time'} for c in curves):
        centre=[c['constant_value'] if c['curve_kind']=='constant' else c['offset_value'] for c in curves]
        velocity=[0. if c['curve_kind']=='constant' else c['signed_linear_rate_per_second'] for c in curves]
        result.update(path_kind='stationary' if not any(velocity) else 'linear_drift',
            center_source_xy=centre,linear_velocity_source_xy=velocity,speed_estimate_kind='exact_nominal')
        return result
    harmonic=[c for c in curves if c['curve_kind']=='sinusoidal_time']
    if any(c['curve_kind']=='linear_time' for c in curves) or len({abs(c['angular_phase_rate_rad_per_second']) for c in harmonic})!=1:
        result['path_kind']='independent_axis_curves';return result
    rate=abs(harmonic[0]['angular_phase_rate_rad_per_second']);matrix=[];centre=[]
    for c in curves:
        if c['curve_kind']=='constant':matrix.append([0.,0.]);centre.append(c['constant_value']);continue
        phase=c['phase_offset_rad'];amplitude=c['amplitude_value'];sign=1 if c['angular_phase_rate_rad_per_second']>0 else -1
        centre.append(c['offset_value'])
        matrix.append([amplitude*math.cos(phase),-sign*amplitude*math.sin(phase)] if c['oscillator_function_code']==1
                      else [amplitude*math.sin(phase),sign*amplitude*math.cos(phase)])
    m=np.array(matrix);axes=np.linalg.svd(m,compute_uv=False)
    fractions=[[Fraction(v) for v in row] for row in matrix]
    determinant=fractions[0][0]*fractions[1][1]-fractions[0][1]*fractions[1][0]
    canonical_phases=[c['phase_offset_rad']*(1 if c['angular_phase_rate_rad_per_second']>0 else -1)
                      for c in harmonic]
    # cos(-z)=cos(z), sin(-z)=-sin(z): a negative rate negates its
    # phase in the positive-rate representation; sine's sign moves to amplitude.
    same_phase=len(harmonic)==2 and canonical_phases[0]==canonical_phases[1]
    line=determinant==0 or same_phase and harmonic[0]['oscillator_function_code']==harmonic[1]['oscillator_function_code']
    circle=(same_phase and harmonic[0]['oscillator_function_code']!=harmonic[1]['oscillator_function_code'] and
            abs(harmonic[0]['amplitude_value'])==abs(harmonic[1]['amplitude_value']))
    if not circle:
        gram=[[sum(a*b for a,b in zip(fractions[i],fractions[j])) for j in range(2)] for i in range(2)]
        circle=gram[0][1]==0 and gram[0][0]==gram[1][1] and gram[0][0]!=0
    if line:axes[1]=0.
    speed=rate*float(axes[0])
    if not np.all(np.isfinite(axes)) or not math.isfinite(speed):
        result.update(maximum_source_speed_units_per_second=None,speed_estimate_kind='unknown',
                      unknown_reasons=['nominal paired-axis estimates are nonfinite']);return result
    result.update(path_kind='line_oscillation' if line else 'circle' if circle else 'ellipse',
        center_source_xy=centre,harmonic_matrix_source_xy=matrix,angular_rate_rad_per_second=rate,
        period_seconds=math.tau/rate,semiaxis_lengths_source_units=axes.tolist(),
        maximum_source_speed_units_per_second=speed,speed_estimate_kind='exact_nominal')
    return result
