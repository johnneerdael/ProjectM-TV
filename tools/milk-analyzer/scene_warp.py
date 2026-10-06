"""Derive warp coordinates from executed source equations, without image inputs.

This connects CPU EEL results to float32 mesh storage, the pinned vertex math
and triangle interpolation. Full drawing, shader uniforms and runtime precision
remain separate requirements for a complete appearance prediction.
"""
import numpy as np
from scene_equations import WARP,_scalar
from spatial import mesh_inputs,warp_vertex_uv,interpolate_mesh,PORTABLE_PROFILE


def warp_fields(source:dict,scene:dict,frame_index:int,*,numeric_profile=PORTABLE_PROFILE,raster_subpixel_bits=None,omit_transformed_uv=False)->dict:
    width,height=scene['viewport'];grid_x,grid_y=scene['mesh_size']
    frame=scene['frames'][frame_index]
    aspect_x=float(np.float32(min(1,width/height)))
    aspect_y=float(np.float32(min(1,height/width)))
    mesh=mesh_inputs(grid_x,grid_y,aspect_x=aspect_x,aspect_y=aspect_y)
    rows=frame['mesh']
    if len(rows)!=(grid_x+1)*(grid_y+1):raise ValueError('incomplete source mesh equation outputs')
    vertex_uv=None
    if not omit_transformed_uv:
        try:
            with np.errstate(over='ignore'):
                parameters={name:np.asarray([row[name] for row in rows],dtype=np.float32).reshape(grid_y+1,grid_x+1)
                            for name in WARP}
        except (TypeError,ValueError,KeyError) as error:
            raise ValueError('unresolved mesh equation value') from error
        values=source['values']
        vertex_uv=warp_vertex_uv(mesh['position'],aspect_x=aspect_x,aspect_y=aspect_y,
                                 **parameters,time=frame['render_inputs']['time'],
                                 warp_anim_speed=_scalar(values,'fWarpAnimSpeed',1,'float'),
                                 warp_scale=_scalar(values,'fWarpScale',1,'float'),numeric_profile=numeric_profile)
    x,y=np.meshgrid((np.arange(width,dtype=np.float32)+.5)/np.float32(width),
                    (np.arange(height,dtype=np.float32)+.5)/np.float32(height))
    original_uv=np.stack((x,y),axis=-1)
    raster=dict(raster_subpixel_bits=raster_subpixel_bits,viewport=(width,height))
    uv=None if omit_transformed_uv else interpolate_mesh(vertex_uv,original_uv,numeric_profile=numeric_profile,**raster)
    polar=interpolate_mesh(np.stack((mesh['radius'],mesh['angle']),axis=-1),original_uv,**raster)
    interpolated_original=(original_uv if raster_subpixel_bits is None else
        interpolate_mesh(mesh['position']*.5+.5,original_uv,**raster))
    return {'uv':uv,'original_uv':interpolated_original,'polar':polar,'vertex_uv':vertex_uv,'numeric_profile':numeric_profile,
            'raster_subpixel_bits':raster_subpixel_bits,
            'basis':'native source equations, float32 vertex storage and warp mesh interpolation',
            'appearance_prediction_complete':False}
