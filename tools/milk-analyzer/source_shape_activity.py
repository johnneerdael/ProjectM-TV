"""Conditional material-change bounds before geometry, feedback and storage."""
import math


def _channel_bound(channel):
    from source_fill_envelopes import native_channel_envelope
    span=native_channel_envelope(channel)
    if span is None or channel['possible_native_wrap_jump'] is not False:return None
    if channel['native_endpoint_domain_singleton']:
        return max(span),0.
    curve=channel['raw_time_curve'];rate=curve['maximum_absolute_control_rate_per_second']
    if rate is None or curve['nominal_continuity']=='unknown':return None
    if not math.isfinite(rate) or rate<0:return None
    return max(span),rate


def _sum_products(a,b,c,d):
    """Round a positive nominal rate ceiling outwards; retain exact zero."""
    from fractions import Fraction
    exact=Fraction(a)*Fraction(b)+Fraction(c)*Fraction(d)
    try:value=float(exact)
    except OverflowError:return None
    if not math.isfinite(value):return None
    if Fraction(value)<exact:value=math.nextafter(value,math.inf)
    return value if math.isfinite(value) else None


def shape_activity(element):
    temporal=element['material_temporal'];channels=temporal['channels']
    material=element['material'];identity=element['id'];hazards=[];records=[]
    crossings=[name for name,c in channels.items() if c['may_be_consumed'] and c['possible_native_wrap_jump'] is True]
    if crossings:hazards.append({'kind':'shape_channel_modulo_crossing','element_id':identity,
        'channels':crossings,'event_rate_hz':None,'visible_flashing_verified':False,
        'nominal_channel_schedules':{name:channels[name]['nominal_modulo_schedule'] for name in crossings},
        'scope':'possible consumed vertex colour/opacity jump; source envelope crossing is not a reached or visible event'})
    gate=temporal['border_gate']
    if gate['possible_state_change'] is True:hazards.append({'kind':'shape_border_draw_gate',
        'element_id':identity,'event_rate_hz':None,'visible_flashing_verified':False,
        'scope':'possible raw-alpha draw gate crossing; colour modulo and screen coverage are separate'})
    parts=[('fill',(('r','g','b','a'),('r2','g2','b2','a2'))),
           ('border',(('border_r','border_g','border_b','border_a'),))]
    for part,groups in parts:
        if not any(channels[name]['may_be_consumed'] for group in groups for name in group):continue
        reasons=[];incoming=[None]*3;blended=[None]*3
        bounds=[[_channel_bound(channels[name]) for name in group] for group in groups]
        untextured=part=='border' or material['texture']['role']=='untextured_vertex_gradient'
        if not untextured:reasons.append('texture colour, alpha and coordinate variation remain unresolved')
        if any(group[3] is None for group in bounds):reasons.append('alpha rate/domain is unresolved or may wrap')
        elif untextured:
            # Fixed barycentric coordinates: convex interpolation cannot exceed
            # the largest endpoint magnitude or time-rate bound. This retains
            # transparent centre colours when edge alpha is nonzero.
            alpha_max=min(max(group[3][0] for group in bounds),1.)
            alpha_rate=max(group[3][1] for group in bounds)
            for i in range(3):
                if any(group[i] is None for group in bounds):
                    reasons.append('RGB channel '+str(i)+' rate/domain is unresolved or may wrap');continue
                colour_max=max(group[i][0] for group in bounds)
                colour_rate=max(group[i][1] for group in bounds)
                incoming[i]=_sum_products(alpha_max,colour_rate,alpha_rate,colour_max)
                blend=material['blend_mode']
                if blend=='source_alpha_additive':blended[i]=incoming[i]
                elif blend=='source_alpha_over' and incoming[i] is not None:
                    blended[i]=_sum_products(1.,incoming[i],1.,alpha_rate)
        if material['blend_mode'] is None:reasons.append('native blend mode is unresolved')
        if part=='border' and gate['nominal_always_enabled'] is None:
            reasons.append('border draw gating may add a discontinuity; bounds apply only while drawn')
        records.append({'element_id':identity,'part':part,'policy':'source-shape-material-rate-v1',
            'maximum_incoming_rgb_rate_per_second':incoming,
            'maximum_blended_rgb_rate_per_second':blended,'destination_rgb_domain':[0,1],
            'blend_mode':material['blend_mode'],'visible_flashing_verified':False,
            'scope':'nominal material partial time rate at fixed barycentric coordinates and fixed destination',
            'unknown_reasons':reasons,
            'conditions':['Finite supported channel arithmetic and stable modulo cell; source-clock jumps excluded',
                'Native float32 and legacy packed-byte quantization/storage steps are not continuous rate guarantees',
                'Fixed geometry/coverage, barycentric coordinates, destination RGB in [0,1] and no later shaders/feedback',
                'Fill requires untextured vertex colour; borders are untextured and rate applies only while drawn',
                'Rates bound incoming alpha*RGB and, for source-alpha-over, add alpha-rate times destination ceiling',
                'Rate ceilings need not be reached; no displayed flash frequency, whole-screen intensity or mood verdict']})
    return records,hazards
