"""Uniform native affine-component scaling envelopes, without frame samples."""
import math
from fractions import Fraction

from source_native_warp import _f32

# Pure scalar constructions only. A dependency-free random/memory operation
# can still vary between vertices; phase provenance is not reconstructed here.
PURE={'constant','input','add','subtract','multiply','divide','eel_divide',
      'negate','sin','cos','tan','asin','acos','atan','atan2','abs','min','max',
      'pow','sqrt','sqr','exp','log','log10','floor','ceil','int','sign',
      'select','less','greater','less_equal','greater_equal','equal','eel_equal',
      'not_equal','cast','narrow','construct','components','bnot','band','bor'}


def uniform_scalar_input(node,readonly):
    if node.detail.get('name') in readonly:return True
    return (node.detail.get('equation_phase') in {'per_frame_','per_frame_init_'} and
            node.detail.get('value_binding')=='phase_scalar_snapshot')


def _product_span(*spans):
    """Exact products of binary endpoint values, rounded outwards once."""
    values=[Fraction(1)]
    for lo,hi in spans:values=[v*Fraction(e) for v in values for e in (lo,hi)]
    low,high=min(values),max(values)
    result=[]
    for value,direction in ((low,-math.inf),(high,math.inf)):
        endpoint=float(value)
        if not math.isfinite(endpoint) or value!=0 and endpoint==0:
            raise ValueError('transport coefficient overflow or underflow')
        if direction<0 and Fraction(endpoint)>value or direction>0 and Fraction(endpoint)<value:
            endpoint=math.nextafter(endpoint,direction)
        result.append(endpoint)
    return result


def native_warp_transport(analysis,*,consumed):
    from effect_families import _deps,_walk
    from scene_equations import READONLY,WARP
    from source_motion import motion_control
    result={'policy':'source-uniform-affine-transport-envelope-v1','status':'unknown',
        'controls':{},'source_to_output_axis_scales':None,'axis_scale_behavior':None,
        'area_ratio_source_to_output':None,'orientation':None,
        'procedural_warp_present':None,'complete_sampling_map_area_ratio':None,
        'visible_screen_motion':None,'unknown_reasons':[],
        'uses_equation_execution':False,'uses_rendered_images':False,
        'conditions':['Controls are uniform across mesh vertices at a frame; readonly frame inputs and frozen main/init scalar snapshots may vary between frames',
                      'Nominal source envelopes exclude intermediate/libm rounding; float32 endpoint conversion is monotone',
                      'Aspect-corrected source-to-output singular scales are abs(zoom*sx),abs(zoom*sy), not physical-screen singular scales',
                      'Affine area/orientation exclude procedural warp, texel shifts, mesh interpolation, transition blending and later shaders',
                      'Relevant source intermediates and native control conversions remain finite; no time/audio history or visible speed inferred']}
    if not consumed:
        result['status']='not_contributing';return result
    uniform=set(READONLY)|{'meshx','meshy','pixelsx','pixelsy','aspectx','aspecty'}
    try:
        blockers=[]
        for name in WARP:
            field=analysis.mesh_controls.get(name)
            if field is None:raise ValueError(name+' control missing')
            deps=_deps(field)
            curve=motion_control(field,name,'native mesh control',application='affine feedback component each step')
            span=curve['nominal_value_range'];native=None
            if span is not None:
                try:native=[_f32(v) for v in span]
                except ValueError:pass
            pure=all(n.op in PURE for n,p in _walk(field))
            uniform_inputs=all(uniform_scalar_input(n,uniform) for n,p in _walk(field) if n.op=='input')
            row={'raw_time_curve':{k:v for k,v in curve.items() if k not in {'expression','phase_expression','value_envelope'}},
                 'native_float32_endpoint_domain':native,
                 'assumed_finite_input_names':sorted(deps),
                 'uniform_across_vertices':uniform_inputs and pure,
                 'uniformity_basis':'frozen main/init phase scalar snapshots and readonly frame inputs'}
            result['controls'][name]=row
            if not uniform_inputs:blockers.append(name+' has spatial/state input without uniformity proof')
            if not pure:
                blockers.append(name+' lacks a pure uniform expression proof')
        if blockers:
            result['unknown_reasons']=blockers;return result
        controls=result['controls']
        if controls['zoomexp']['native_float32_endpoint_domain']!=[1,1]:
            raise ValueError('zoomexp is not uniformly one')
        magnitudes={}
        for name in ('zoom','sx','sy'):
            span=controls[name]['native_float32_endpoint_domain']
            if span is None:raise ValueError(name+' has no finite native endpoint domain')
            if span[0]<=0<=span[1]:raise ValueError(name+' native endpoint domain reaches zero')
            for v in span:
                if _f32(1/v)==0:raise ValueError(name+' reciprocal underflows')
            magnitudes[name]=sorted(map(abs,span))
        axes={axis:_product_span(magnitudes['zoom'],magnitudes[stretch]) for axis,stretch in [('x','sx'),('y','sy')]}
        z=magnitudes['zoom']
        area=_product_span(z,z,magnitudes['sx'],magnitudes['sy'])
        def behavior(span):
            if span==[1,1]:return 'neutral'
            if span[0]>1:return 'expansion'
            if span[1]<1:return 'contraction'
            return 'crosses_neutral'
        sx=controls['sx']['native_float32_endpoint_domain'];sy=controls['sy']['native_float32_endpoint_domain']
        w=controls['warp']['native_float32_endpoint_domain']
        warp=None if w is None else w!=[0,0]
        result.update(status='bounded_uniform_affine_component',source_to_output_axis_scales=axes,
            axis_scale_behavior={axis:behavior(span) for axis,span in axes.items()},area_ratio_source_to_output=area,
            orientation='preserving' if (sx[0]>0)==(sy[0]>0) else 'reversing',procedural_warp_present=warp)
    except (ValueError,OverflowError,ZeroDivisionError) as error:
        result['unknown_reasons'].append(str(error))
    return result
