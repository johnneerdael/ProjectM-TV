"""Conditional nonnegative fan colour/alpha and nominal area envelopes."""
import math
from fractions import Fraction
import numpy as np
from source_material_temporal import PERIOD,WRAP_MARGIN


def native_channel_envelope(channel):
    value=channel['native_value_if_singleton']
    if value is not None:return [value,value]
    endpoints=channel['native_float32_endpoint_domain']
    if endpoints is None:return None
    upper=float(np.nextafter(np.float32(PERIOD),np.float32(-np.inf)))
    period=Fraction(PERIOD);low,high=map(Fraction,endpoints)
    first=low//period;last=high//period
    if first!=last or channel['possible_native_wrap_jump'] is not False:return [0.,upper]
    # Ideal residual interval, padded for float32 remainder/add rounding.
    a=float(low-first*period);b=float(high-first*period)
    return [max(0.,a-WRAP_MARGIN),min(upper,b+WRAP_MARGIN)]


def shape_fill_envelope(controls,geometry,material,temporal):
    from source_motion import motion_control
    reasons=[];area=None;alpha=None;rgb=[None]*3
    channels=temporal['channels']
    radius=motion_control(controls['rad'],'radius','NDC radius',application='shape geometry parameter')
    span=radius['nominal_value_range'];sides=geometry['effective_sides']
    if span is not None and sides is not None:
        with np.errstate(over='ignore',invalid='ignore'):r=[float(np.float32(v)) for v in span]
        if all(math.isfinite(v) for v in r):
            low=0. if r[0]<=0<=r[1] else min(map(abs,r));high=max(map(abs,r))
            factor=sides*math.sin(math.tau/sides)/8
            area=[factor*low*low,factor*high*high]
    if area is None:reasons.append('nominal area needs a finite radius envelope and constant effective sides')
    if material['texture']['role']!='untextured_vertex_gradient':
        reasons.append('texture colour/alpha lacks a declared contract')
    else:
        a0=native_channel_envelope(channels['a']);a1=native_channel_envelope(channels['a2'])
        if a0 is None or a1 is None:reasons.append('fan endpoint alpha envelope is unresolved')
        else:
            # clip(interpolate(alpha)) is at least interpolate(clip(lower
            # endpoints)) and its mean is at most min(mean(upper endpoints),1).
            l0,l1=min(a0[0],1.),min(a1[0],1.)
            alpha=[(l0+2*l1)/3,min((a0[1]+2*a1[1])/3,1.)]
            for i,(center,edge) in enumerate(zip(('r','g','b'),('r2','g2','b2'))):
                c=native_channel_envelope(channels[center]);p=native_channel_envelope(channels[edge])
                if c is None or p is None:
                    reasons.append('RGB channel '+str(i)+' envelope is unresolved');continue
                # The lower term remains valid with or without source-RGB
                # clamping; upper uses unclipped positive vertex envelopes.
                cl,pl=min(c[0],1.),min(p[0],1.)
                low=((l0+l1)*cl+(l0+3*l1)*pl)/6
                high=((a0[1]+a1[1])*c[1]+(a0[1]+3*a1[1])*p[1])/6
                high=min(high,max(c[1],p[1])*alpha[1])
                rgb[i]=[low,high]
    def weighted(pair):return None if pair is None or area is None else [pair[0]*area[0],pair[1]*area[1]]
    def summed(pair):
        if pair is None:return None
        values=[v*geometry['configured_instances'] for v in pair]
        return values if all(math.isfinite(v) for v in values) else None
    alpha_area=weighted(alpha);rgb_area=[weighted(pair) for pair in rgb]
    return {'policy':'source-custom-shape-fill-envelope-v1',
        'mean_alpha_bounds':alpha,'mean_rgb_times_alpha_bounds':rgb,
        'nominal_area_fraction_per_aspect_y_bounds':area,
        'nominal_alpha_area_fraction_per_aspect_y_bounds':alpha_area,
        'nominal_source_rgb_integral_per_aspect_y_bounds':rgb_area,
        'summed_nominal_alpha_area_fraction_per_aspect_y_bounds':summed(alpha_area),
        'summed_nominal_source_rgb_integral_per_aspect_y_bounds':[summed(pair) for pair in rgb_area],
        'native_channel_envelopes':{name:native_channel_envelope(channels[name]) for name in ('r','g','b','a','r2','g2','b2','a2')},
        'overlap_aggregation':'sum; repeated coverage counted multiple times',
        'visible_screen_contribution':None,'unknown_reasons':reasons,
        'uses_rendered_images':False,'uses_equation_execution':False,
        'conditions':['Conditional source envelopes and finite native conversions; scalar input/intermediate premises from material temporal data apply',
                      'Continuous nominal polygon area with constant effective sides; multiply by target aspectY, no aspect is assumed',
                      'Fan barycentric moments bound nonnegative source RGB times clamped blend alpha; extrema need not coincide in time or across inputs',
                      'Bounds allow source-RGB clipping but do not assume its exact stage; pointwise alpha clipping is bounded rather than treated as linear',
                      'Modulo-stable intervals include float32 residual/add margin; possible crossings use the full finite colour range',
                      'Before clipping/rasterization, borders, overlap union, destination, storage, later shaders and feedback; incoming term bounds are not visible brightness']}
