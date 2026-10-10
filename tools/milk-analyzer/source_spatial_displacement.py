"""Per-vertex pure-control envelopes, distinct from uniform affine transforms."""
import math
import numpy as np


def spatial_displacement(analysis,uniform_displacement):
    from source_warp_transport import PURE
    from source_control_bounds import scalar_value_envelope
    from source_native_warp import _f32
    from source_radial_zoom import radial_scale_domains
    from source_warp_displacement import displacement_terms
    from scene_equations import WARP,_scalar
    from shader_fields import Field
    result={'policy':'source-spatial-control-displacement-v1','status':'unknown',
        'uniform_across_vertices':False,'control_domains':{},'rms_upper_bound_terms':None,
        'complete_sampling_map_area_ratio':None,'visible_motion_speed':None,'unknown_reasons':[],
        'coordinate_input_domains':{'x':[0,1],'y':[0,1],
            'rad':[0,float(np.nextafter(np.float32(math.sqrt(2)),np.float32(np.inf)))],
            'ang':[-float(np.nextafter(np.float32(math.pi),np.float32(np.inf))),float(np.nextafter(np.float32(math.pi),np.float32(np.inf)))]},
        'conditions':['Only pure per-vertex formulas with native reset coordinate inputs are bounded; frame/state/shared names do not inherit mesh ranges',
            'Positive finite renderer aspects at most one give EEL x/y in [0,1]; radius/angle endpoints use outward float32 padding of sqrt2/pi',
            'All controls may vary spatially inside independent native endpoint envelopes; source inputs/intermediates remain finite',
            'Pointwise operator/centre triangle bounds precede uniform original-area RMS integration, not exact spatial Jacobian/area',
            'Libm/intermediate accuracy beyond the declared endpoint padding, mesh interpolation, texel alignment, history and visible intensity remain separate']}
    if uniform_displacement['status']=='not_contributing':result['status']='not_contributing';return result
    if uniform_displacement['status']=='bounded_uniform_sampling_displacement':
        result['status']='not_required';return result
    memo={};has_spatial=False;domains={}
    def project(node,depth=0):
        nonlocal has_spatial
        if id(node) in memo:return memo[id(node)][1]
        if depth>64 or len(memo)>=4096:raise ValueError('spatial control projection budget exceeded')
        if node.op=='input':
            name=node.detail.get('name','')
            if name.startswith(('state:','shared:')) or node.detail.get('value_binding')=='shared_register':
                raise ValueError('persistent/shared input lacks a per-vertex domain proof')
            if node.detail.get('equation_phase')=='per_pixel_' and node.detail.get('value_binding')=='phase_scalar_snapshot' and node.detail.get('native_mesh_reset_input') is not True:
                raise ValueError('per-vertex persistent input lacks a reset or main-snapshot proof')
            if name in result['coordinate_input_domains']:
                if node.detail.get('native_mesh_reset_input') is not True:
                    raise ValueError('frame/state coordinate name is not a native mesh reset input')
                local=':spatial-mesh-'+name;domains[local]=result['coordinate_input_domains'][name]
                has_spatial=True;value=Field('input',dtype=node.dtype,detail={**node.detail,'name':local})
            else:value=node
        elif node.op not in PURE:raise ValueError('per-vertex control is not a supported pure formula')
        else:value=Field(node.op,tuple(project(a,depth+1) for a in node.args),node.dtype,node.detail)
        memo[id(node)]=(node,value);return value
    try:
        for name in WARP:
            field=analysis.mesh_controls.get(name)
            if field is None:raise ValueError('native control inventory incomplete')
            selected=project(field);r=scalar_value_envelope(selected,input_domains=domains);span=r['nominal_value_range']
            if span is None:raise ValueError(name+' lacks a bounded spatial control domain')
            native=[_f32(v) for v in span];result['control_domains'][name]=native
        if not has_spatial:raise ValueError('no bounded native coordinate dependence; remaining state/domain gap retained')
        for name in ('sx','sy'):
            span=result['control_domains'][name]
            if span[0]<=0<=span[1]:raise ValueError(name+' spatial domain reaches zero')
            for v in span:
                if _f32(1/v)==0:raise ValueError(name+' reciprocal underflows')
        z=result['control_domains']['zoom'];e=result['control_domains']['zoomexp']
        if z[0]<=0 or e[0]<=0:raise ValueError('spatial radial power domain unresolved')
        power,factors,tangent=radial_scale_domains(z,e,math.nextafter(math.sqrt(2),math.inf))
        scale=_scalar(analysis.values,'fWarpScale',1,'float')
        if scale==0 or _f32(1/scale)==0:raise ValueError('warp scale reciprocal is singular or underflows')
        _scalar(analysis.values,'fWarpAnimSpeed',1,'float')
        terms=displacement_terms(result['control_domains'],tangent)
        result.update(status='bounded_spatial_sampling_displacement',rms_upper_bound_terms=terms,
            radial_factor_range=factors)
    except (ValueError,RecursionError,OverflowError,ZeroDivisionError) as error:result['unknown_reasons']=[str(error)]
    return result
