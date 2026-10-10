"""Nominal named control curves; these do not establish screen/image motion."""
import math
from source_temporal import affine_time_parameters
from source_control_bounds import merge_continuity


def motion_control(field,control,unit,*,application,_include_switch_events=True):
    from source_appearance import _phase_literal,_phase_terms,_expression
    result={'policy':'source-time-control-curves-v1','control':control,'control_unit':unit,
        'application':application,'curve_kind':'unknown','constant_value':None,
        'rate_estimate_kind':'unknown','nominal_value_range_kind':'unknown','nominal_continuity':'unknown',
        'offset_value':None,'amplitude_value':None,'oscillator_function_code':None,
        'phase_expression':None,'phase_offset_rad':None,'angular_phase_rate_rad_per_second':None,
        'period_seconds':None,'frequency_hz':None,'nominal_value_range':None,
        'signed_linear_rate_per_second':None,'maximum_absolute_control_rate_per_second':None,
        'rate_unit':unit+'/source-time second','expression':_expression(field),
        'visible_motion_speed':None,'unknown_reasons':[],
        'conditions':['Continuous nominal source-time formula; clock jumps, finite precision and sampled frames excluded',
                      'Control variation does not establish visibility, geometry trajectories after projection, feedback motion or perceived intensity']}
    if _include_switch_events:
        from source_time_switches import time_switch_events
        result['time_switch_events']=time_switch_events(field)
        result['time_switch_events_are_exhaustive']=False
    literal=_phase_literal(field)
    if literal is not None:
        result.update(curve_kind='constant',rate_estimate_kind='exact_nominal',nominal_value_range_kind='exact_nominal',nominal_continuity='smooth_nominal',constant_value=literal,
                      nominal_value_range=[literal,literal],maximum_absolute_control_rate_per_second=0.)
        return result
    pair=affine_time_parameters(field)
    if pair is not None:
        rate,offset=pair
        if rate==0:
            result.update(curve_kind='constant',rate_estimate_kind='exact_nominal',nominal_value_range_kind='exact_nominal',nominal_continuity='smooth_nominal',constant_value=offset,
                          nominal_value_range=[offset,offset],maximum_absolute_control_rate_per_second=0.)
        else:
            result.update(curve_kind='linear_time',rate_estimate_kind='exact_nominal',nominal_continuity='smooth_nominal',offset_value=offset,
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
                    result.update(curve_kind='constant',rate_estimate_kind='exact_nominal',nominal_value_range_kind='exact_nominal',nominal_continuity='smooth_nominal',constant_value=value,
                        nominal_value_range=[value,value],maximum_absolute_control_rate_per_second=0.)
                    return result
            if phase is not None and phase[0]!=0:
                rate=phase[0];speed=abs(rate*amplitude);frequency=abs(rate)/math.tau;period=math.tau/abs(rate)
                low,high=bias-abs(amplitude),bias+abs(amplitude)
                if (not (rate!=0 and amplitude!=0 and speed==0) and
                        all(math.isfinite(v) for v in (bias,amplitude,speed,frequency,period,low,high))):
                    result.update(curve_kind='sinusoidal_time',rate_estimate_kind='exact_nominal',nominal_value_range_kind='exact_nominal',nominal_continuity='smooth_nominal',offset_value=bias,amplitude_value=amplitude,
                        oscillator_function_code=1 if osc.op=='cos' else 2,
                        phase_expression=_expression(osc.args[0]),phase_offset_rad=phase[1],angular_phase_rate_rad_per_second=rate,
                        frequency_hz=frequency,period_seconds=period,nominal_value_range=[low,high],
                        maximum_absolute_control_rate_per_second=speed)
                    return result
    from source_control_bounds import compound_time_bounds
    bounds=compound_time_bounds(field)
    result.update(nominal_value_range=bounds['nominal_value_range'],
                  nominal_value_range_kind='upper_bound' if bounds['nominal_value_range'] is not None else 'unknown',
                  nominal_continuity=bounds['nominal_continuity'],unknown_reasons=bounds['unknown_reasons'])
    if result['nominal_value_range'] is None:
        from source_control_bounds import scalar_value_envelope
        envelope=scalar_value_envelope(field)
        result['value_envelope']=envelope
        if envelope['nominal_value_range'] is not None:
            result.update(nominal_value_range=envelope['nominal_value_range'],nominal_value_range_kind='upper_bound')
    if bounds['maximum_absolute_control_rate_per_second'] is not None:
        result.update(curve_kind='compound_time',rate_estimate_kind='upper_bound',
                      maximum_absolute_control_rate_per_second=bounds['maximum_absolute_control_rate_per_second'])
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
        'nominal_continuity':merge_continuity([c['nominal_continuity'] for c in curves]),
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
    if any(c['curve_kind']=='compound_time' for c in curves):
        result['path_kind']='independent_axis_curves';return result
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


def shape_vertex_motion(controls,geometry,trajectory):
    """Bound continuous nominal perimeter-vertex speed before clipping/feedback."""
    import numpy as np
    from source_appearance import _phase_literal
    radius=motion_control(controls['rad'],'radius','NDC radius',application='shape perimeter')
    angle=motion_control(controls['ang'],'rotation','radian',application='shape perimeter')
    result={'policy':'source-custom-shape-vertex-motion-v1','estimate_kind':'unknown',
        'nominal_continuity':merge_continuity([trajectory['nominal_continuity'],radius['nominal_continuity'],angle['nominal_continuity']]),
        'centre_speed_ndc_per_second_upper_bound':None,
        'maximum_absolute_radius_ndc':None,'maximum_radius_rate_ndc_per_second':None,
        'maximum_angle_rate_rad_per_second':None,
        'local_vertex_speed_ndc_per_second_upper_bound':None,
        'maximum_vertex_speed_ndc_per_second_upper_bound':None,
        'visible_motion_speed':None,'radius_curve':radius,'angle_curve':angle,
        'unknown_reasons':[],
        'conditions':['Continuous nominal polygon-vertex paths with constant effective side count and fixed viewport/aspectY',
                      'Native projection is (2*x-1,1-2*y)+radius*(aspectY*cos(theta),sin(theta)); 0<aspectY<=1',
                      'Radius and angular derivatives are orthogonal before aspect scaling; centre and local speeds use triangle inequality',
                      'Bounds hold while source intermediates and native float32 conversions are finite; rounding, trig error and discrete frames excluded',
                      'Before clipping, rasterization, texture/material changes, composite and feedback; vertex movement is not measured visible motion or flashing']}
    centre=trajectory['maximum_source_speed_units_per_second']
    if centre is not None and math.isfinite(2*centre):
        result['centre_speed_ndc_per_second_upper_bound']=2*centre
    span=radius['nominal_value_range']
    maximum_radius=max(map(abs,span)) if span is not None else None
    dr=radius['maximum_absolute_control_rate_per_second']
    da=angle['maximum_absolute_control_rate_per_second']
    result.update(maximum_absolute_radius_ndc=maximum_radius,
        maximum_radius_rate_ndc_per_second=dr,maximum_angle_rate_rad_per_second=da)
    reasons=result['unknown_reasons']
    curves=dict(zip(('x','y'),trajectory['axis_curves']))
    curves.update(rad=radius,ang=angle)
    for name in ('x','y','rad','ang'):
        curve=curves[name]
        value=curve['constant_value'] if curve['curve_kind']=='constant' else _phase_literal(controls[name])
        if value is None:continue
        if name=='x':value=2*value-1
        elif name=='y':value=1-2*value
        with np.errstate(over='ignore',invalid='ignore'):converted=float(np.float32(value))
        if not math.isfinite(converted):
            reasons.append(name+' constant is outside its finite native float32 projection/conversion domain')
            result['nominal_continuity']='unknown'
    if geometry['effective_sides'] is None:
        reasons.append('effective side count is not a proved lifetime constant')
        result['nominal_continuity']='unknown'
    if result['centre_speed_ndc_per_second_upper_bound'] is None:reasons.append('centre speed has no finite nominal bound')
    if dr is None:reasons.append('radius derivative has no supported nominal bound')
    # A collapsed perimeter has no angular contribution, even with unknown angle.
    if maximum_radius==0 and dr==0:angular=0.
    elif da==0:angular=0.
    elif da is None:angular=None;reasons.append('angular derivative has no supported nominal bound')
    elif maximum_radius is None:angular=None;reasons.append('rotating radius has no finite lifetime magnitude bound')
    else:angular=maximum_radius*da
    if dr is not None and angular is not None:
        local=math.hypot(dr,angular)
        if math.isfinite(local):result['local_vertex_speed_ndc_per_second_upper_bound']=local
        else:reasons.append('derived local speed bound is nonfinite')
    if not reasons:
        total=result['centre_speed_ndc_per_second_upper_bound']+result['local_vertex_speed_ndc_per_second_upper_bound']
        if math.isfinite(total):
            result.update(estimate_kind='upper_bound',maximum_vertex_speed_ndc_per_second_upper_bound=total)
        else:reasons.append('derived combined speed bound is nonfinite')
    return result
