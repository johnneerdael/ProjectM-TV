"""Analytic nominal native sampling displacement; no pixels or frame samples."""
import math

from source_native_warp import _f32,affine_center_displacement
from source_warp_transport import _product_span


def _positive(value):
    if not math.isfinite(value) or value<0:raise ValueError('displacement bound is nonfinite')
    return math.nextafter(value,math.inf) if value else 0.


def _product(a,b):
    if a==0 or b==0:return 0.
    result=a*b
    if result==0:raise ValueError('positive displacement product underflows')
    return _positive(result)


def native_warp_displacement(analysis,transport,*,radial_zoom=None):
    from scene_equations import _scalar
    result={'policy':'source-native-sampling-displacement-v1','status':'unknown',
        'sampling_model':None,
        'coordinate_basis':'aspect_corrected_source_uv','unit':'source_coordinate/feedback_step',
        'rms_upper_bound_terms':None,'affine_rms_squared_aspect_coefficients':None,
        'affine_mean_displacement_aspect_corrected':None,'native_float32_controls':None,
        'visible_motion_speed':None,'texel_alignment_included':False,
        'unknown_reasons':[],'uses_equation_execution':False,'uses_rendered_images':False,
        'formula':'rms <= translation_and_center + centered_geometry*sqrt(aspectX^2+aspectY^2) + procedural_warp',
        'rms_squared_basis':['1','aspectX^2','aspectY^2'],
        'conditions':['Uniform nominal mesh controls with finite source/converted/intermediate domains; radial fallback requires positive zoom/zoomexp',
                      'RMS integrates backward sampling displacement over uniform original UV in [0,1]^2; no image or audio/time samples',
                      'Aspect-corrected coordinates, finite positive renderer aspect supplied; texel displacement must be added separately',
                      'Procedural warp is bounded before rotation using a triangle inequality; no oscillator phase samples',
                      'Nominal real arithmetic excludes libm/GPU rounding, interpolation, transitions, wrapping, clipping and later shaders',
                      'Sampling displacement is not forward feature motion, displayed speed, flash rate or a mood score']}
    if transport['status']=='not_contributing':
        result['status']='not_contributing';return result
    try:
        radial=None
        if transport['status']!='bounded_uniform_affine_component':
            from source_radial_zoom import native_radial_zoom
            radial=radial_zoom if radial_zoom is not None else native_radial_zoom(transport)
            if radial['status']!='bounded_radial_zoom_component':raise ValueError('uniform affine/radial transport domain unresolved')
            if any(not row['uniform_across_vertices'] for row in transport['controls'].values()):
                raise ValueError('radial composition requires every native control to be uniform')
        domains={name:row['native_float32_endpoint_domain'] for name,row in transport['controls'].items()}
        if set(domains)!= {'zoom','zoomexp','rot','warp','cx','cy','dx','dy','sx','sy'}:
            raise ValueError('native displacement control inventory incomplete')
        if any(span is None for span in domains.values()):raise ValueError('one or more mesh controls lack finite endpoint domains')
        for name in ('sx','sy'):
            if domains[name][0]<=0<=domains[name][1]:raise ValueError(name+' domain reaches zero')
            for value in domains[name]:
                if _f32(1/value)==0:raise ValueError(name+' reciprocal underflows')
        scale=_scalar(analysis.values,'fWarpScale',1,'float')
        if scale==0:raise ValueError('native warp scale reciprocal is singular, even when warp is zero')
        if _f32(1/scale)==0:raise ValueError('native warp scale reciprocal underflows')
        _scalar(analysis.values,'fWarpAnimSpeed',1,'float')
        inv_z=radial['tangential_sampling_scale_range'] if radial is not None else sorted(1/v for v in domains['zoom'])
        terms=displacement_terms(domains,inv_z)
        coefficients=None;mean=None;controls=None
        if radial is None and all(span[0]==span[1] for span in domains.values()):
            controls={name:span[0] for name,span in domains.items()};p=controls
            c=math.cos(p['rot']);s=math.sin(p['rot'])
            a=1/p['zoom']/p['sx'];b=1/p['zoom']/p['sy']
            ex,ey=affine_center_displacement(p,c,s)
            coefficients=[ex*ex+ey*ey,((c*a-1)**2+(s*a)**2)/12,((s*b)**2+(c*b-1)**2)/12]
            if not all(math.isfinite(v) for v in coefficients):raise ValueError('affine nominal RMS coefficient overflows')
            mean=[ex,ey]
        result.update(status='bounded_uniform_sampling_displacement',rms_upper_bound_terms=terms,
            sampling_model='uniform_radial_zoom_envelope' if radial is not None else 'uniform_affine_envelope',
            affine_rms_squared_aspect_coefficients=coefficients,
            affine_mean_displacement_aspect_corrected=mean,native_float32_controls=controls)
        if radial is not None:
            result['radial_zoom_factor_range']=radial['zoom_factor_range']
            result['radial_sampling_scale_range']=inv_z
            result['radial_radius_domain']=radial['nominal_radius_domain']
    except (ValueError,OverflowError,ZeroDivisionError) as error:
        result['unknown_reasons'].append(str(error))
    return result


def displacement_terms(domains,inv_z):
    inv_stretch={}
    for name in ('sx','sy'):
        inv_stretch[name]=sorted(1/v for v in domains[name])
    diagonal={name:_product_span(inv_z,inv_stretch[name]) for name in ('sx','sy')}
    magnitude=lambda span:max(map(abs,span))
    rotation=2. if magnitude(domains['rot'])>=math.pi else _positive(2*math.sin(magnitude(domains['rot'])/2))
    diagonal_max=max(magnitude(span) for span in diagonal.values())
    diagonal_deviation=max(abs(v-1) for span in diagonal.values() for v in span)
    matrix_bound=_positive(_product(rotation,diagonal_max)+diagonal_deviation)
    stretch_max=max(magnitude(span) for span in inv_stretch.values())
    stretch_deviation=max(abs(v-1) for span in inv_stretch.values() for v in span)
    center_radius=math.hypot(*(max(abs(.5-v) for v in domains[name]) for name in ('cx','cy')))
    displacement_radius=math.hypot(magnitude(domains['dx']),magnitude(domains['dy']))
    center_bound=_positive(_product(_positive(_product(rotation,stretch_max)+stretch_deviation),center_radius)+displacement_radius)
    warp_bound=_product(_positive(math.sqrt(2)*2*_f32(.0035)),magnitude(domains['warp']))
    terms={'translation_and_center':center_bound,'centered_geometry':_positive(matrix_bound/math.sqrt(12)),
           'procedural_warp':warp_bound}
    if matrix_bound>0 and terms['centered_geometry']==0:raise ValueError('geometry displacement quotient underflows')
    return terms
