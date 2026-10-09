"""Static built-in waveform forms and controls; no waveform math execution."""
import math
import numpy as np

FORMS={
 0:('audio_deformed_circle',['waveform_right'],1),
 1:('stereo_polar_rotating_trace',['waveform_left','waveform_right'],1),
 2:('stereo_xy_trace',['waveform_left','waveform_right'],1),
 3:('stereo_xy_trace_volume_alpha',['waveform_left','waveform_right'],1),
 4:('horizontal_momentum_trace',['waveform_left','waveform_right'],1),
 5:('rotating_quadratic_stereo_trace',['waveform_left','waveform_right'],1),
 6:('angled_waveform_trace',['waveform_left'],1),
 7:('two_channel_parallel_traces',['waveform_left','waveform_right'],2),
 8:('angled_log_spectrum_trace',['spectrum_left'],1),
 9:('extended_angled_waveform_trace',['waveform_left'],1),
 10:('extended_crossed_stereo_traces',['waveform_left','waveform_right'],2),
 11:('extended_parallel_vertical_stereo_traces',['waveform_left','waveform_right'],2),
 12:('extended_skewed_polar_trace',['waveform_left','waveform_right'],1),
 13:('extended_star_named_radial_trace',['waveform_right'],1),
 14:('extended_flower_named_polar_trace',['waveform_right'],1),
 15:('extended_lasso_named_nonlinear_trace',['waveform_left'],1)}


def builtin_wave_possible(main):
    from effect_families import _number
    from native_values import live_wave_mode
    raw=_number(main['wave_mode']);mode=None if raw is None else live_wave_mode(raw)
    if raw is not None and mode is None:return False
    # Mode3 replaces authored alpha before volume modulation. Dynamic mode can
    # reach3, so zero source alpha alone cannot prove no waveform contribution.
    return _number(main['wave_a'])!=0 or raw is None or mode==3


def consumed_wave_controls(mode):
    names={'wave_mode','wave_a','wave_r','wave_g','wave_b','wave_x','wave_y','wave_mystery'}
    if mode is None:return names
    if mode==3:names.remove('wave_a')
    if mode in {2,3,5,11,15}:names.remove('wave_mystery')
    if mode in {6,8,9,10,11}:names.remove('wave_y')
    if mode==15:names.remove('wave_x')
    return names


def waveform_recipe(analysis):
    from source_appearance import _phase_literal,_expression
    from native_values import live_wave_mode
    from scene_equations import _scalar
    main=analysis.main
    def value(name):return None if name not in main else _phase_literal(main[name])
    def flag(name):
        v=value(name);return None if v is None else v!=0
    from effect_families import _number
    mode_value=_number(main['wave_mode']);mode=None if mode_value is None else live_wave_mode(mode_value)
    dots=flag('wave_usedots');mystery=value('wave_mystery')
    def f32(value):
        if value is None:return None
        with np.errstate(all='ignore'):v=float(np.float32(value))
        return v if math.isfinite(v) else None
    normalized=f32(mystery)
    if normalized is not None:
        if mode in {0,1,4} and (normalized<-1 or normalized>1):
            v=np.float32(np.float32(normalized)*np.float32(.5)+np.float32(.5))
            v=np.float32(v-np.floor(v));normalized=float(np.float32(abs(v)*np.float32(2)-np.float32(1)))
    result={'policy':'source31-static-builtin-waveform-v1','mode_expression':_expression(main['wave_mode']),
        'effective_mode':mode,'form_name':None if mode is None else FORMS[mode][0],
        'audio_inputs':[] if mode is None else FORMS[mode][1],'audio_instrument_identity':None,
        'path_count':None if mode is None or mode==9 else FORMS[mode][2],
        'primary_generated_path_count':None if mode is None else FORMS[mode][2],
        'secondary_storage_status':'allocated by source without explicit vertex assignment; actual draw outcome not modeled' if mode==9 else None,
        'source_alpha_policy':'depends on evaluated mode; mode3may replace authored wave_a' if mode is None else 'reference coefficient*1.3*treb^2 before volume ramp; authored wave_a is replaced' if mode==3 else 'authored wave_a with mode-specific attenuation/boost and optional volume ramp',
        'dots':dots,
        'thick':flag('wave_thick'),'additive':flag('wave_additive'),
        'path_topology':None if mode is None or dots is None else 'points' if dots else 'loop' if mode in {13,14} else 'strip',
        'hardware_draw_primitive':'points' if mode is not None and dots is True else None,
        'hardware_draw_candidates':[] if mode is None or dots is None else ['points'] if dots else
            ['line_loop','triangle_strip'] if mode in {13,14} else ['line_strip','triangle_strip'],
        'consumed_authored_controls':sorted(consumed_wave_controls(mode)),
        'geometry_closed_endpoint':True if mode==0 else False if mode is not None and mode<13 else None,
        'control_expressions':{name:_expression(main[name]) for name in ('wave_x','wave_y','wave_mystery','wave_a','wave_r','wave_g','wave_b')},
        'wave_x':value('wave_x'),'wave_y':value('wave_y'),'normalized_mystery':normalized,
        'line_angle_rad':None,'separation_normal_offset':None,
        'base_radius_model_units':None,'sample_radial_gain':None,'nominal_rotation_rad_per_second':None,
        'preprocess':{'wave_scale':_scalar(analysis.values,'fWaveScale',1,'float'),
            'wave_smoothing':_scalar(analysis.values,'fWaveSmoothing',.75,'float'),
            'raw_scale_divisor':128,'recurrence':'s[0]=raw[0]*scale/128; s[i]=raw[i]*(scale/128)*(1-smoothing)+s[i-1]*smoothing',
            'geometry_smoothing':'four-tap interleaving weights[-.15,1.15,1.15,-.15] divided by2'},
        'actual_screen_coverage':None,'visible_motion_speed':None,'appearance_guaranteed':False,
        'native_control_domains_verified':False,
        'conditions':['Audio sample windows, volume/treble-dependent alpha, aspect, render context and projection affect drawing',
                      'Wave x/y are native controls, not a uniform centre for every mode; line modes use edge clipping',
                      'Native reference width can cap sample counts; no exact onscreen vertices, thickness or visible footprint is claimed',
                      'Extended star/flower/lasso names identify source constructions, not guaranteed recognizable silhouettes',
                      'Later shader/composition/feedback can hide or reshape the wave; no flash, party/chill or instrument identity is certified']}
    if mode in {0,1,12,13,14}:
        base,gain,rotation={0:(.5,.4,.2),1:(.53,.43,2.3),12:(.63,.23,3.3),13:(.7,.4,.2),14:(.7,.7,None)}[mode]
        result.update(base_radius_model_units=base,sample_radial_gain=gain,nominal_rotation_rad_per_second=rotation)
    if mode==5:result['nominal_rotation_rad_per_second']=.3
    if mode in {6,7,8,9} and f32(mystery) is not None:
        with np.errstate(all='ignore'):angle=float(np.float32(np.float32(1.57)*np.float32(mystery)))
        result['line_angle_rad']=angle if math.isfinite(angle) else None
    if mode==7 and f32(value('wave_y')) is not None:
        with np.errstate(all='ignore'):separation=float(np.float32(np.float32(value('wave_y'))**np.float32(2)))
        result['separation_normal_offset']=separation if math.isfinite(separation) else None
    return result
