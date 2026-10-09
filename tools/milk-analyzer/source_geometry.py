"""Nominal source custom-shape geometry, without rendering or pixel sampling."""
import math
import numpy as np


def shape_geometry(controls,configured_instances):
    from source_appearance import _phase_literal
    radius=_phase_literal(controls['rad']);sides=_phase_literal(controls['sides'])
    reasons=[]
    if radius is None:reasons.append('radius is not a lifetime-constant supported scalar')
    else:
        with np.errstate(over='ignore',invalid='ignore'):radius=float(np.float32(radius))
        if not math.isfinite(radius):
            radius=None;reasons.append('radius conversion is outside finite float32')
    if sides is None or not -(2**31)-1<sides<2**31:
        sides=None;reasons.append('side count is not a known value in the native int32 conversion domain')
    else:sides=min(100,max(3,math.trunc(sides)))
    coefficient=None if radius is None or sides is None else sides*radius*radius*math.sin(math.tau/sides)/8
    return {'policy':'source-custom-shape-footprint-v1',
        'status':'conditional nominal geometry' if coefficient is not None else 'unknown geometry',
        'radius_ndc':radius,'effective_sides':sides,'configured_instances':configured_instances,
        'nominal_area_fraction_per_aspect_y':coefficient,
        'summed_nominal_area_fraction_per_aspect_y':None if coefficient is None else coefficient*configured_instances,
        'circumcircle_width_fraction_per_aspect_y':None if radius is None else abs(radius),
        'circumcircle_height_fraction':None if radius is None else abs(radius),
        'center_source_xy':[_phase_literal(controls[name]) for name in ('x','y')],
        'aspect_y_formula':'min(1, viewport_height / viewport_width)',
        'visible_coverage_fraction':None,'unknown_reasons':reasons,
        'conditions':['Qualified source31 shape projection: center=(2*x-1,1-2*y), radius in NDC, horizontal radius scaled by aspectY',
                      'Area and circumcircle extents are nominal unclipped primitive geometry; float32 trigonometry and raster edge coverage are excluded',
                      'Multiply area/width coefficients by the target aspectY; summed area counts overlap repeatedly',
                      'Opacity conversion, textures, borders, clipping, blend order and later feedback/composite determine prominence'],
        'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False}


def shape_audio_area_response(controls,geometry,fill):
    """Square a proved constant-affine audio radius as nominal source algebra."""
    from shader_fields import Field
    from source_appearance import EEL_AUDIO,_expression,_phase_literal
    from source_sampling import _affine_basis_map
    result={'policy':'source-custom-shape-audio-area-v1','source_model':'unknown',
        'input_codes':None,'radius_bias':None,'radius_gains':None,
        'nominal_area_polynomial_per_aspect_y':None,
        'area_derivative_constant_per_aspect_y':None,
        'area_derivative_linear_matrix_per_aspect_y':None,
        'area_to_alpha_integral_factor':fill['mean_fill_alpha'],
        'area_to_rgb_integral_factors':fill['mean_source_rgb_times_alpha'],
        'configured_instances':geometry['configured_instances'],
        'radius_expression':_expression(controls['rad']),
        'maximum_finite_float32_radius_magnitude':float(np.finfo(np.float32).max),
        'visible_bass_response_strength':None,'unknown_reasons':[],
        'conditions':['Nominal continuous source radius before float32 projection, trig rounding and clipping',
                      'Inputs and all source intermediates must be finite, with radius in the finite float32 conversion domain',
                      'Area is per target aspectY; negative radius still has squared nominal area',
                      'Derivative is with respect to declared engine band units, not beats, frequency or perceived response',
                      'Material factors apply only when their independent source fill model is known; overlap and later composition remain unresolved'],
        'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False}
    memo={};names=tuple(':shape-area-audio-'+str(code) for code in EEL_AUDIO.values())
    def substitute(node,depth=0):
        if depth>64 or len(memo)>=4096:raise ValueError('audio radius substitution budget exceeded')
        if id(node) in memo:return memo[id(node)]
        name=node.detail.get('name')
        if node.op=='input' and node.dtype=='float' and name in EEL_AUDIO:
            basis=Field('input',dtype='float4',detail={'name':names[EEL_AUDIO[name]-1]})
            value=Field('member',(basis,),'float',{'field':'x','swizzle':True})
        else:value=Field(node.op,tuple(substitute(a,depth+1) for a in node.args),node.dtype,node.detail)
        memo[id(node)]=value;return value
    try:
        radius=substitute(controls['rad'])
        matrix,offsets=_affine_basis_map(radius,names,output_width=1)
        bias=_phase_literal(offsets[0])
        if bias is None:raise ValueError('radius offset depends on unresolved time/state or source math')
        indices=[i for i in range(6) if matrix[0,4*i]!=0]
        gains=matrix[0,[4*i for i in indices]]
        if not indices and abs(bias)>float(np.finfo(np.float32).max):
            raise ValueError('constant radius is outside finite float32 conversion')
        sides=geometry['effective_sides']
        if sides is None:raise ValueError('effective polygon side count is unresolved')
        factor=sides*math.sin(math.tau/sides)/8
        with np.errstate(over='ignore',invalid='ignore'):
            constant=factor*bias*bias;linear=2*factor*bias*gains
            quadratic=factor*np.outer(gains,gains)
            derivative=2*quadratic
        if (not math.isfinite(constant) or not np.all(np.isfinite(linear)) or
                not np.all(np.isfinite(quadratic)) or not np.all(np.isfinite(derivative))):
            raise ValueError('nominal area polynomial coefficients are nonfinite')
        result.update(source_model='affine_audio_radius' if indices else 'constant_radius',
            input_codes=[i+1 for i in indices],radius_bias=bias,radius_gains=gains.tolist(),
            nominal_area_polynomial_per_aspect_y={'constant':constant,'linear':linear.tolist(),
                                                'quadratic_matrix':quadratic.tolist()},
            area_derivative_constant_per_aspect_y=linear.tolist(),
            area_derivative_linear_matrix_per_aspect_y=derivative.tolist())
    except (ValueError,RecursionError) as error:result['unknown_reasons']=[str(error)]
    return result
