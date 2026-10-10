"""Nominal two-state shape material differences at fixed barycentric positions."""
from fractions import Fraction


def _quadratic_maximum(matrix):
    """Max of sum w_i*w_j*M_ij for weights (w,1-w), 0<=w<=1."""
    from source_sampling_motion import _finite_round
    a,b=matrix[0];c,d=matrix[1]
    square=a-b-c+d;linear=b+c-2*d
    candidates=[a,d]
    if square<0:
        w=-linear/(2*square)
        if 0<w<1:candidates.append(square*w*w+linear*w+d)
    return _finite_round(max(candidates),upper=True)


def shape_material_jump_bounds(element):
    from source_fill_envelopes import native_channel_envelope
    from source_sampling_motion import _finite_round
    temporal=element['material_temporal'];channels=temporal['channels'];material=element['material']
    result=[]
    for part,groups in (('fill',(('r','g','b','a'),('r2','g2','b2','a2'))),
                        ('border',(('border_r','border_g','border_b','border_a'),))):
        if not any(channels[n]['may_be_consumed'] for group in groups for n in group):continue
        spans=[[native_channel_envelope(channels[n]) for n in group] for group in groups]
        reasons=[];incoming=[None]*3;blended=[None]*3
        untextured=part=='border' or material['texture']['role']=='untextured_vertex_gradient'
        if not untextured:reasons.append('texture RGB/alpha and coordinate changes are unresolved')
        alpha=[group[3] for group in spans]
        if part=='border' and temporal['border_gate']['nominal_always_enabled'] is not True and alpha[0] is not None:
            alpha=[[0.,alpha[0][1]]] # No draw is exactly zero effective blend alpha.
        if any(a is None for a in alpha):reasons.append('native alpha endpoint domain is unresolved')
        elif untextured:
            alpha_linear=all(a[1]<=1 for a in alpha)
            for axis in range(3):
                colours=[group[axis] for group in spans]
                if any(c is None for c in colours):
                    reasons.append('native RGB endpoint domain '+str(axis)+' is unresolved');continue
                amax=[Fraction(a[1]) for a in alpha];da=[Fraction(a[1])-Fraction(a[0]) for a in alpha]
                cmax=[Fraction(c[1]) for c in colours];dc=[Fraction(c[1])-Fraction(c[0]) for c in colours]
                contrast=[max(Fraction(c[1]),1-min(Fraction(c[0]),1)) for c in colours]
                def ceiling(magnitudes):
                    if alpha_linear and len(groups)==2:
                        matrix=[[amax[i]*dc[j]+magnitudes[j]*da[i] for j in range(2)] for i in range(2)]
                        return _quadratic_maximum(matrix)
                    # Clamp(interpolated alpha) is not interpolation of clipped
                    # endpoints. Use its global Lipschitz ceiling in this case.
                    return _finite_round(min(max(amax),1)*max(dc)+max(magnitudes)*min(max(da),1),upper=True)
                incoming[axis]=ceiling(cmax)
                if material['blend_mode']=='source_alpha_additive':blended[axis]=incoming[axis]
                elif material['blend_mode']=='source_alpha_over':blended[axis]=ceiling(contrast)
        if material['blend_mode'] is None:reasons.append('native blend mode is unresolved')
        area=element['fill_envelope']['nominal_area_fraction_per_aspect_y_bounds'] if part=='fill' else None
        maximum=None if area is None else area[1]
        instances=element['geometry']['configured_instances']
        weighted=[None if maximum is None or jump is None else _finite_round(
            Fraction(maximum)*Fraction(jump)*instances,upper=True) for jump in blended]
        result.append({'policy':'source-shape-two-state-material-difference-v1','element_id':element['id'],'part':part,
            'maximum_incoming_rgb_difference':incoming,'maximum_blended_rgb_difference':blended,
            'destination_rgb_domain':[0,1],'blend_mode':material['blend_mode'],
            'nominal_fill_area_fraction_per_aspect_y_upper_bound':maximum,
            'summed_nominal_rgb_difference_integral_per_aspect_y':weighted,
            'configured_instances':instances,'instance_aggregation':'sum; repeated overlap counted multiple times',
            'visible_flash_strength':None,'event_frequency_hz':None,'native_numeric_certified':False,
            'abrupt_change_verified':False,
            'unknown_reasons':reasons,
            'scope':'two possible material states, fixed geometry/barycentric position and fixed destination before later passes',
            'conditions':['Declared native endpoint domains hold; arbitrary two states can be more separated than adjacent frames',
                'Untextured source RGB and clamped blend alpha; optional RGB clipping is nonexpansive',
                'Fan alpha within [0,1] uses a barycentric quadratic ceiling; alpha clipping otherwise uses a scalar ceiling',
                'Over blend uses maximum endpoint contrast against the fixed destination in [0,1]',
                'Fill integrals use nominal unclipped area times target aspectY; they are not measured screen coverage',
                'Borders are one draw pass with unresolved raster footprint; repeat passes, instances/overlap, geometry movement, storage and later feedback/composition remain separate',
                'Border draw-gate uncertainty includes the zero-alpha off state; smooth colour swings can also have nonzero two-state bounds',
                'No minimum, attained jump, visible flash strength/frequency, safe absence or mood verdict']})
    return result
