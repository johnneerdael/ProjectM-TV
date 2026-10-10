"""Nominal native radial-zoom component, not a visible tunnel classifier."""
import math

from source_native_warp import _f32
from source_warp_transport import _product_span
from source_control_bounds import merge_continuity


def _outward(values):
    low,high=min(values),max(values)
    if not math.isfinite(low) or not math.isfinite(high) or low<=0:
        raise ValueError('positive power envelope overflow/underflow')
    return [math.nextafter(low,-math.inf),math.nextafter(high,math.inf)]


def native_radial_zoom(transport):
    result={'policy':'source-uniform-native-radial-zoom-v1','status':'unknown',
        'native_zoom_domain':None,'native_zoomexp_domain':None,
        'nominal_radius_domain':[0,math.sqrt(2)],'zoom_factor_range':None,
        'tangential_sampling_scale_range':None,'log_zoom_radial_derivative_range':None,
        'radial_derivative_positive_sufficient':None,'actual_fold_present':None,
        'nominal_continuity':'unknown','assumed_finite_input_names':[],
        'complete_sampling_map_area_ratio':None,'visible_effect_family':None,
        'unknown_reasons':[],'uses_equation_execution':False,'uses_rendered_images':False,
        'formulas':{'zoom_factor':'z^(e^(2*r-1))','radial_sampling':'r/zoom_factor',
            'tangential_sampling_scale':'1/zoom_factor',
            'log_zoom_radial_derivative':'2*ln(e)*ln(z)*e^(2*r-1)',
            'radial_sampling_derivative':'(1-r*log_zoom_radial_derivative)/zoom_factor'},
        'conditions':['Positive finite uniform zoom and zoomexp; readonly/pure source controls with supported envelopes',
                      'Radius is aspect-corrected source-mesh hypot, with nominal |pos.x|/|pos.y|<=1 and 0<aspectX/aspectY<=1',
                      'Bounds are nominal continuous real math; finite float32 power/reciprocal endpoint controls are not GPU/libm error certification',
                      'Radius construction/intermediate power rounding and triangle interpolation remain separate from these nominal derivatives',
                      'Only the initial radial zoom component; stretch, procedural warp, rotation, translation, feedback contents and later shaders remain separate',
                      'A failed sufficient positive-derivative bound does not prove a fold or visible effect family']}
    if transport['status']=='not_contributing':
        result['status']='not_contributing';return result
    try:
        rows=transport['controls']
        selected=[rows.get(name) for name in ('zoom','zoomexp')]
        if any(row is None for row in selected):raise ValueError('zoom/zoomexp control rows missing')
        if any(not row['uniform_across_vertices'] for row in selected):raise ValueError('zoom/zoomexp uniformity unresolved')
        z,e=[row['native_float32_endpoint_domain'] for row in selected]
        if z is None or e is None or z[0]<=0 or e[0]<=0:raise ValueError('zoom/zoomexp lack positive finite native domains')
        rmax=result['nominal_radius_domain'][1]
        power=_outward([math.pow(base,exponent) for base in e for exponent in (-1,2*rmax-1)])
        for value in power:
            if _f32(value)==0:raise ValueError('native inner power endpoint underflows')
        factors=_outward([math.pow(base,exponent) for base in z for exponent in power])
        for value in factors:
            if _f32(value)==0 or _f32(1/value)==0:raise ValueError('native power/reciprocal endpoint underflows')
        tangent=_outward([1/v for v in factors])
        logs_e=[math.log(v) for v in e];logs_z=[math.log(v) for v in z]
        derivative=_product_span([2,2],logs_e,logs_z,power)
        fold_term=_product_span([0,rmax],derivative)
        result.update(status='bounded_radial_zoom_component',native_zoom_domain=z,native_zoomexp_domain=e,
            zoom_factor_range=factors,tangential_sampling_scale_range=tangent,
            log_zoom_radial_derivative_range=derivative,
            radial_derivative_positive_sufficient=fold_term[1]<1,
            nominal_continuity=merge_continuity([row['raw_time_curve']['nominal_continuity'] for row in selected]),
            assumed_finite_input_names=sorted(set().union(*(row['assumed_finite_input_names'] for row in selected))))
    except (ValueError,OverflowError,ZeroDivisionError) as error:
        result['unknown_reasons'].append(str(error))
    return result
