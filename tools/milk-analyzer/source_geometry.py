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
