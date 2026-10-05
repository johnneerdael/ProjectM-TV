"""Draw supported source scene components in pinned native order.

Shapes -> custom waves -> builtin waveform -> centre darkening -> borders.
Use an explicit canonical line/point model; hardware raster differences and
unsupported material/motion stages remain limitations, not claimed equivalence.
"""
import numpy as np
from primitives import draw_shape,shape_fan,draw_triangles,draw_borders,_finite
from line_points import draw_lines,draw_points
from scene_equations import _scalar
from quad_lines import PROFILE,draw_quad_lines


def _wave(target,wave,*,builtin=False,quantize=True,line_rendering_profile='canonical-gl-lines-v1'):
    if builtin:
        groups=wave['positions'];colours=wave['rgba']
    else:groups=[wave['positions']];colours=wave['colours']
    for group_index,positions in enumerate(groups):
        if not positions:continue
        points=np.asarray(positions,dtype=np.float32)
        for offset in wave['copy_offsets']:
            shifted=points+np.asarray(offset,dtype=np.float32)
            if wave['draw_mode']=='points':
                target=draw_points(target,shifted,colours,point_size=wave.get('point_size',1),additive=wave['additive'],quantize=quantize)
            else:
                if line_rendering_profile==PROFILE:
                    raw=wave.get('clip_positions')
                    clip=None if raw is None else np.asarray(raw[group_index] if builtin else raw,dtype=np.float32)
                    if clip is not None:
                        clip=clip+np.asarray(offset,dtype=np.float32)*np.array([2,-2],np.float32)
                    target=draw_quad_lines(target,shifted,colours,closed=wave['draw_mode']=='loop',additive=wave['additive'],
                                           quantize=quantize,clip_positions=clip)
                else:
                    target=draw_lines(target,shifted,colours,closed=wave['draw_mode']=='loop',additive=wave['additive'],quantize=quantize)
    return target


def draw_source_scene(destination,source,frame,builtin_wave,custom_waves,*,quantize=True,shape_textures=None,shape_texture_aspects=None,motion_vectors_prewarped=False,line_rendering_profile='canonical-gl-lines-v1'):
    target=_finite(destination,'framebuffer').copy();height,width=target.shape[:2];main=frame['main'];values=source['values']
    if line_rendering_profile not in {'canonical-gl-lines-v1',PROFILE}:
        raise ValueError('unknown line rendering profile')
    from motion_vectors import motion_active
    if motion_active(main) and not motion_vectors_prewarped:
        raise ValueError('motion vector drawing before warp requires separate source integration')
    aspect_y=np.float32(min(1,height/width));shape_textures=shape_textures or {};shape_texture_aspects=shape_texture_aspects or {}
    for shape in frame['shapes']:
        attributes=shape['values'];index=shape['index'];fill=dict(attributes);fill['border_a']=0
        texture=shape_textures.get(index)
        target=draw_shape(target,fill,aspect_y=aspect_y,quantize=quantize,texture_sample=texture,
                          texture_aspect_y=shape_texture_aspects.get(index))
        if attributes.get('border_a',0)>.0001:
            fan=shape_fan(attributes,aspect_y=aspect_y);positions=fan['positions'][1:-1]
            colour=np.array([attributes.get('border_'+c,1 if c!='a' else 0) for c in 'rgba'],dtype=np.float32)
            thick=_scalar(values,f'shapecode_{index}_thickOutline',0,'bool')
            offsets=[[0,0],[.5/width,0],[.5/width,.5/height],[0,.5/height]] if thick else [[0,0]]
            for offset in offsets:
                draw=draw_quad_lines if line_rendering_profile==PROFILE else draw_lines
                target=draw(target,positions+np.asarray(offset,dtype=np.float32),colour,closed=True,
                                  additive=int(attributes.get('additive',0))!=0,quantize=quantize)
    for wave in custom_waves:target=_wave(target,wave,quantize=quantize,line_rendering_profile=line_rendering_profile)
    if builtin_wave is not None:target=_wave(target,builtin_wave,builtin=True,quantize=quantize,line_rendering_profile=line_rendering_profile)
    if main.get('darken_center',0)>0:
        half=np.float32(.025)
        points=np.array([[.5,.5],[.5-half*aspect_y,.5],[.5,.5-half],[.5+half*aspect_y,.5],
                         [.5,.5+half],[.5-half*aspect_y,.5]],dtype=np.float32)
        colours=np.zeros((6,4),dtype=np.float32);colours[0,3]=np.float32(3)/32
        target=draw_triangles(target,points,colours,[[0,i,i+1] for i in range(1,5)],additive=False,quantize=quantize)
    return draw_borders(target,main,quantize=quantize)
