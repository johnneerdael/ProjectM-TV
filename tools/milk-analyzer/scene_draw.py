"""Draw supported source scene components in pinned native order.

Shapes -> custom waves -> builtin waveform -> centre darkening -> borders.
Use an explicit canonical line/point model; hardware raster differences and
unsupported material/motion stages remain limitations, not claimed equivalence.
"""
import numpy as np
from primitives import draw_shape,shape_fan,draw_triangles,draw_borders,_finite,shape_centre_shift,LEGACY_SHAPE_CENTRES
from line_points import draw_lines,draw_points
from scene_equations import source_settings,_scalar
from quad_lines import PROFILE,draw_quad_lines,LEGACY_VIEWPORT


def _wave(target,wave,*,builtin=False,quantize=True,line_rendering_profile='canonical-gl-lines-v1',point_subpixel_bits=None,triangle_subpixel_bits=None,viewport_policy=LEGACY_VIEWPORT,reference_size=None):
    if builtin:
        groups=wave['positions'];colours=wave['rgba']
    else:groups=[wave['positions']];colours=wave['colours']
    height,width=target.shape[:2]
    from quad_lines import line_scale,dot_style
    scale=line_scale(width,height,reference_size)
    offsets=wave['copy_offsets']
    point_size=wave.get('point_size',1)
    if reference_size is not None:
        thick=bool(wave.get('thick',len(offsets)>1 or (not builtin and point_size==2)))
        if wave['draw_mode']=='points' and scale>0:
            style=dot_style('main' if builtin else 'custom',thick,scale)
            point_size=style['size']
            colours=np.asarray(colours,dtype=np.float32).copy()
            if builtin or style['alpha_scale']<1:
                colours[...,3]*=np.float32(style['alpha_scale'])
            offsets=[[0,0]]
        elif wave['draw_mode']=='points' and builtin:
            point_size=1
            offsets=[[0,0],[1/width,0],[1/width,-1/height],[0,-1/height]]
        elif wave['draw_mode']!='points':
            offset_scale=scale if scale>0 else np.float32(1)
            dx=float(offset_scale/np.float32(width))*(1 if builtin else .5)
            dy=float(offset_scale/np.float32(height))*(-1 if builtin else .5*height/width)
            offsets=[[0,0],[dx,0],[dx,dy],[0,dy]] if thick else [[0,0]]
    for group_index,positions in enumerate(groups):
        if not positions:continue
        points=np.asarray(positions,dtype=np.float32)
        for offset in offsets:
            shifted=points+np.asarray(offset,dtype=np.float32)
            if wave['draw_mode']=='points':
                target=draw_points(target,shifted,colours,point_size=point_size,additive=wave['additive'],quantize=quantize,
                                   subpixel_bits=point_subpixel_bits)
            else:
                if line_rendering_profile==PROFILE:
                    raw=wave.get('clip_positions')
                    clip=None if raw is None else np.asarray(raw[group_index] if builtin else raw,dtype=np.float32)
                    if clip is not None:
                        clip=clip+np.asarray(offset,dtype=np.float32)*np.array([2,-2],np.float32)
                    target=draw_quad_lines(target,shifted,colours,closed=wave['draw_mode']=='loop',additive=wave['additive'],
                                           quantize=quantize,clip_positions=clip,raster_subpixel_bits=triangle_subpixel_bits,viewport_policy=viewport_policy,reference_size=reference_size)
                else:
                    target=draw_lines(target,shifted,colours,closed=wave['draw_mode']=='loop',additive=wave['additive'],quantize=quantize)
    return target


def source_shape_thickness(source,index,attributes):
    """Resolve the evaluated binary64 flag without modifying authored values."""
    from engine_profiles import CORE_2331_ENGINE,matches
    from native_values import native_scalar
    saved=bool(_scalar(source_settings(source),f'shapecode_{index}_thickOutline',0,'bool'))
    if not matches(source.get('parser_inputs',{}).get('engine',{}),CORE_2331_ENGINE):return saved
    if 'thick' not in attributes:return saved
    value=native_scalar(attributes['thick'],allow_ieee=True)
    if not np.isfinite(value) or not -2147483649<value<2147483648:return saved
    return abs(value)>=1


def draw_source_scene(destination,source,frame,builtin_wave,custom_waves,*,quantize=True,shape_textures=None,shape_texture_aspects=None,motion_vectors_prewarped=False,line_rendering_profile='canonical-gl-lines-v1',point_subpixel_bits=None,triangle_subpixel_bits=None,shape_centre_policy=LEGACY_SHAPE_CENTRES,builtin_wave_viewport_policy=LEGACY_VIEWPORT,line_reference_size=None):
    target=_finite(destination,'framebuffer').copy();height,width=target.shape[:2];main=frame['main'];values=source_settings(source)
    if line_rendering_profile not in {'canonical-gl-lines-v1',PROFILE}:
        raise ValueError('unknown line rendering profile')
    from quad_lines import line_scale
    scale=line_scale(width,height,line_reference_size)
    if scale==0:line_rendering_profile='canonical-gl-lines-v1'
    from motion_vectors import motion_active
    if motion_active(main) and not motion_vectors_prewarped:
        raise ValueError('motion vector drawing before warp requires separate source integration')
    shift=shape_centre_shift(width,height,shape_centre_policy)
    aspect_y=np.float32(min(1,height/width));shape_textures=shape_textures or {};shape_texture_aspects=shape_texture_aspects or {}
    for ordinal,shape in enumerate(frame['shapes']):
        attributes=shape['values'];index=shape['index'];fill=dict(attributes);fill['border_a']=0
        texture=shape_textures.get((index,ordinal),shape_textures.get(index))
        target=draw_shape(target,fill,aspect_y=aspect_y,quantize=quantize,texture_sample=texture,
                          texture_aspect_y=shape_texture_aspects.get(index),raster_subpixel_bits=triangle_subpixel_bits,centre_policy=shape_centre_policy)
        if attributes.get('border_a',0)>.0001:
            fan=shape_fan(attributes,aspect_y=aspect_y);positions=fan['positions'][1:-1]+shift
            colour=np.array([attributes.get('border_'+c,1 if c!='a' else 0) for c in 'rgba'],dtype=np.float32)
            thick=source_shape_thickness(source,index,attributes)
            offset_scale=scale if line_reference_size is not None and scale>0 else 1
            offsets=[[0,0],[.5*offset_scale/width,0],[.5*offset_scale/width,.5*offset_scale/height],[0,.5*offset_scale/height]] if thick else [[0,0]]
            for offset in offsets:
                draw=draw_quad_lines if line_rendering_profile==PROFILE else draw_lines
                raster={'raster_subpixel_bits':triangle_subpixel_bits,'reference_size':line_reference_size} if line_rendering_profile==PROFILE else {}
                target=draw(target,positions+np.asarray(offset,dtype=np.float32),colour,closed=True,
                                  additive=int(attributes.get('additive',0))!=0,quantize=quantize,**raster)
    for wave in custom_waves:target=_wave(target,wave,quantize=quantize,line_rendering_profile=line_rendering_profile,point_subpixel_bits=point_subpixel_bits,triangle_subpixel_bits=triangle_subpixel_bits,reference_size=line_reference_size)
    if builtin_wave is not None:target=_wave(target,builtin_wave,builtin=True,quantize=quantize,line_rendering_profile=line_rendering_profile,point_subpixel_bits=point_subpixel_bits,triangle_subpixel_bits=triangle_subpixel_bits,viewport_policy=builtin_wave_viewport_policy,reference_size=line_reference_size)
    if main.get('darken_center',0)>0:
        half=np.float32(.025)
        points=np.array([[.5,.5],[.5-half*aspect_y,.5],[.5,.5-half],[.5+half*aspect_y,.5],
                         [.5,.5+half],[.5-half*aspect_y,.5]],dtype=np.float32)
        colours=np.zeros((6,4),dtype=np.float32);colours[0,3]=np.float32(3)/32
        target=draw_triangles(target,points,colours,[[0,i,i+1] for i in range(1,5)],additive=False,quantize=quantize,raster_subpixel_bits=triangle_subpixel_bits)
    return draw_borders(target,main,quantize=quantize,raster_subpixel_bits=triangle_subpixel_bits)
