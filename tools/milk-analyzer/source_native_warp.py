"""Nominal native mesh sampling recipes from uniform source controls.

No pixels, equations or shaders are executed. Float32 control conversion is
retained; subsequent coefficients use real arithmetic, not GPU rounding.
"""
import math
from fractions import Fraction

import numpy as np


def _f32(value):
    with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
        result=float(np.float32(value))
    if not math.isfinite(result):raise ValueError('outside finite float32 domain')
    return result


def affine_center_displacement(p,c,s):
    """Nominal (R*S-I)*(.5-center)-distance without centre cancellation."""
    f={name:Fraction(p[name]) for name in ('sx','sy','cx','cy','dx','dy')}
    c=Fraction(c);s=Fraction(s);half=Fraction(1,2)
    x=(c/f['sx']-1)*(half-f['cx'])-s/f['sy']*(half-f['cy'])-f['dx']
    y=s/f['sx']*(half-f['cx'])+(c/f['sy']-1)*(half-f['cy'])-f['dy']
    result=[float(x),float(y)]
    if not all(math.isfinite(v) for v in result) or any(value!=0 and v==0 for value,v in zip((x,y),result)):
        raise ValueError('nominal centre displacement overflow or underflow')
    return result


def native_warp_recipe(analysis,*,consumed):
    from scene_equations import _scalar
    from source_appearance import _phase_literal
    stage=analysis.stages['warp']
    branch={'fixed_warp':'legacy','custom_warp':'custom'}.get(stage['kind'],'unknown')
    result={'policy':'uniform-native-warp-recipe-v1','shader_branch':branch,
        'conditional_on_native_profile':stage['conditional_on_native_profile'],
        'model_kind':'unknown','contribution':'consumed' if consumed else 'disconnected',
        'native_float32_controls':{},'rotation_matrix':None,
        'matrix_uv_aspect_coefficients':None,'offset_uv_aspect_coefficients':None,
        'affine_component_identity':None,'affine_area_ratio_source_to_output':None,
        'procedural_warp':None,'texel_offset_uv_is_runtime_input':True,
        'visible_screen_motion':None,'unknown_reasons':[],
        'matrix_basis':['1','aspectY/aspectX','aspectX/aspectY'],
        'offset_basis':['1','1/aspectX','1/aspectY','aspectY/aspectX','aspectX/aspectY'],
        'conditions':['Finite positive aspectX/aspectY and finite texel_offset_uv supplied by the renderer',
                      'Continuous source UV map at mesh vertices; triangle interpolation and pixel sampling remain separate',
                      'Nominal sin/cos and arithmetic after float32 control conversion; native libm/GPU precision not certified',
                      'Native time, oscillator phases, reciprocal and transformed-coordinate intermediates must remain finite',
                      'No preset transition blending; visible feedback contents, decay and later composition remain separate',
                      'Procedural signs follow the declared selected shader branch; unresolved nonzero-warp branch stays unknown']}
    if not consumed:
        result['model_kind']='not_contributing'
        return result
    controls=getattr(analysis,'mesh_controls',{})
    try:
        for name in ('zoom','zoomexp','rot','warp','cx','cy','dx','dy','sx','sy'):
            value=controls.get(name)
            literal=None if value is None else _phase_literal(value)
            if literal is None:raise ValueError(name+' is not a known uniform scalar')
            result['native_float32_controls'][name]=_f32(literal)
        p=result['native_float32_controls']
        if p['warp']!=0 and branch=='unknown':raise ValueError('selected native warp shader branch is unresolved')
        if p['zoomexp']!=1:raise ValueError('radial zoom exponent is not one')
        for name in ('zoom','sx','sy'):
            if p[name]==0:raise ValueError(name+' is singular')
            if _f32(1/p[name])==0:raise ValueError(name+' reciprocal underflows')
        speed=_scalar(analysis.values,'fWarpAnimSpeed',1,'float')
        scale=_scalar(analysis.values,'fWarpScale',1,'float')
        if scale==0:raise ValueError('warp scale inverse is singular, including when warp is zero')
        scale_inverse=_f32(1/scale)
        c=math.cos(p['rot']);s=math.sin(p['rot'])
        x=c/p['zoom']/p['sx'];y=c/p['zoom']/p['sy']
        xy=-s/p['zoom']/p['sy'];yx=s/p['zoom']/p['sx']
        ex,ey=affine_center_displacement(p,c,s)
        matrix=[[[x,0,0],[0,xy,0]],[[0,0,yx],[y,0,0]]]
        offset=[[.5-.5*x,ex,0,-.5*xy,0],[.5-.5*y,0,ey,0,-.5*yx]]
        area=abs(p['zoom']**2*p['sx']*p['sy'])
        if not all(math.isfinite(v) for row in matrix for cell in row for v in cell) or not all(
                math.isfinite(v) for row in offset for v in row) or not math.isfinite(area) or area==0:
            raise ValueError('nominal affine coefficient domain is nonfinite or degenerate')
    except (ValueError,OverflowError) as error:
        result['unknown_reasons'].append(str(error))
        return result
    amplitude=abs(p['warp'])*_f32(.0035)
    term_data=[('u','sin',.333,[[1,0,0,0],[0,0,0,1]]),
               ('v','cos',.375,[[0,0,-1,0],[0,1,0,0]]),
               ('u','cos',.753,[[0,-1,0,0],[0,0,-1,0]]),
               ('v','sin',.825,[[1,0,0,0],[0,0,0,-1]])]
    if branch=='custom':
        term_data=[(axis,function,rate,[rows[0],[-v for v in rows[1]]])
                   for axis,function,rate,rows in term_data]
    waves={'warp_time':'render_time_seconds * warp_animation_speed',
        'warp_animation_speed':speed,'warp_scale_inverse':scale_inverse,
        'signed_term_amplitude':p['warp']*_f32(.0035),
        'pre_rotation_displacement_bound_each_axis':2*amplitude,
        'uv_source_position_convention':('pos=2*original_uv-1; legacy warp reverses oscillator y signs'
            if branch=='legacy' else 'pos=2*original_uv-1; custom warp uses native oscillator y signs'),
        'phase_rule':'time_coefficient*warp_time + warp_scale_inverse*sum(pos[axis]*coefficients[axis][factor]*warp_factors[factor])',
        'factor_rule':'bias + amplitude*cos(time_coefficient*warp_time + phase_offset)',
        'warp_factors':[dict(zip(('bias','amplitude','time_coefficient','phase_offset'),map(_f32,row)))
                        for row in [(11.68,4,1.413,10),(8.77,3,1.113,7),(10.54,3,1.233,3),(11.49,4,.933,5)]],
        'terms':[{'axis':axis,'function':function,'time_coefficient':_f32(rate),
                  'phase_position_factor_coefficients':coefficients} for axis,function,rate,coefficients in term_data]}
    result.update(model_kind='uniform_affine' if p['warp']==0 else 'uniform_native_wave_warp',
        rotation_matrix=[[c,-s],[s,c]],matrix_uv_aspect_coefficients=matrix,
        offset_uv_aspect_coefficients=offset,
        affine_component_identity=(x==1 and y==1 and xy==0 and yx==0 and ex==0 and ey==0),
        affine_area_ratio_source_to_output=area,procedural_warp=waves)
    return result
