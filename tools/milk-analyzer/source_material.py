"""Source custom-shape vertex materials; no pixel/image/shader execution."""
import math
import numpy as np
from primitives import colour_modulo


def _flag(field):
    from effect_families import _number
    number=_number(field)
    if number is None or not -(2**31)-1<number<2**31:return None
    return math.trunc(number)!=0


def shape_material(controls,requested_image):
    from source_appearance import _phase_literal,_expression
    groups={'centre':['r','g','b','a'],'perimeter':['r2','g2','b2','a2'],
            'border':['border_r','border_g','border_b','border_a']}
    source={};converted={};programs={};unknowns=[]
    for group,names in groups.items():
        values=[_phase_literal(controls[name]) for name in names]
        source[group]=values;programs[group]={name:_expression(controls[name]) for name in names}
        rgba=[]
        for name,value in zip(names,values):
            if value is None:
                rgba.append(None);unknowns.append(name+' is dynamic or not a supported constant');continue
            try:
                with np.errstate(over='ignore',invalid='ignore'):rgba.append(float(colour_modulo(value)))
            except ValueError:
                rgba.append(None);unknowns.append(name+' lacks a finite native colour conversion')
        converted[group]=rgba
    additive=_flag(controls['additive']);textured=_flag(controls['textured'])
    border_alpha=_phase_literal(controls['border_a'])
    if additive is None:unknowns.append('blend mode is not a known native integer style')
    if textured is None:unknowns.append('textured style is not a known native integer style')
    role='unresolved_textured_style' if textured is None else 'untextured_vertex_gradient' if not textured else \
         'named_image_request' if requested_image else 'previous_main'
    return {'policy':'source-custom-shape-material-v1',
        'gradient_kind':'centre_to_perimeter_triangle_fan_vertex_rgba',
        'source_rgba':source,'centre_vertex_rgba':converted['centre'],
        'perimeter_vertex_rgba':converted['perimeter'],'border_vertex_rgba':converted['border'],
        'border_draw_enabled':None if border_alpha is None else border_alpha>float(np.float32(.0001)),
        'border_enable_threshold':float(np.float32(.0001)),
        'channel_expressions':programs,
        'colour_conversion':'qualified native float32 euclidean modulo256/255 before interpolation/storage',
        'blend_mode':None if additive is None else 'source_alpha_additive' if additive else 'source_alpha_over',
        'source_blend_factor':'source_alpha',
        'destination_blend_factor':None if additive is None else 'one' if additive else 'one_minus_source_alpha',
        'texture':{'role':role,'requested_name':requested_image if requested_image else None,
                   'fallback_role':'previous_main' if textured is not False else None,
                   'actual_asset_sha256':None,'actual_binding_verified':False,
                   'tex_zoom_source':_phase_literal(controls['tex_zoom']),
                   'tex_angle_source_rad':_phase_literal(controls['tex_ang']),
                   'tex_zoom_expression':_expression(controls['tex_zoom']),
                   'tex_angle_expression':_expression(controls['tex_ang'])},
        'final_palette_verified':False,'visible_colour_contribution':None,'unknown_reasons':unknowns,
        'conditions':['Vertex colours interpolate through the polygon fan; borders use their separate colour',
                      'Texture lookup/fallback and sampler/render-context transforms remain unresolved',
                      'Texture multiplication, alpha conversion/blending, clipping and later shaders determine displayed colours'],
        'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False}
