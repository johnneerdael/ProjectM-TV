"""Patched GLES hard-edge quad-line vertex math in top-row screen coordinates.

Port of ProjectM-TV patch 0024 LineVertexShaderGlsl330.vert and LineTieBias.
The published JNI host sets a 1024x768 reference and leaves antialiasing disabled.
This profile covers viewports at or below that reference area (one-pixel lines).
Triangle raster precision remains the declared source model, not GPU identity.
"""
import numpy as np
from primitives import _finite, draw_triangles

PROFILE='projectmtv-gles-quad-lines-v1'


def quad_line_vertices(positions,colours,*,width,height,closed=False,clip_positions=None):
    if width<=0 or height<=0 or width*height>1024*768:
        raise ValueError('quad-line profile requires viewport within 1024x768 reference area')
    points=_finite(positions,'line positions')
    colour=_finite(colours,'line colours')
    if points.ndim!=2 or points.shape[1]!=2:
        raise ValueError('two-component line positions required')
    if colour.shape==(4,):colour=np.tile(colour,(len(points),1))
    if colour.shape!=(len(points),4):raise ValueError('per-vertex RGBA required')
    if len(points)<2:return []
    size=np.array([width,height],np.float32)
    if clip_positions is None:
        pixels=points*size
    else:
        clip=_finite(clip_positions,'projected clip positions')
        if clip.shape!=points.shape:raise ValueError('matching projected clip positions required')
        # Native ToPixels runs before adding the viewport's centre. Avoid losing
        # small segments by rounding their positions near normalized screen 0.5.
        pixels=clip*np.array([.5,-.5],np.float32)*size
    # LineBatch repeats neighbours at strip ends, or pads a loop with last/first.
    count=len(points) if closed else len(points)-1
    result=[]
    for first in range(count):
        last=(first+1)%len(points)
        a,b=pixels[first],pixels[last]
        delta=b-a
        length=np.float32(np.sqrt(np.dot(delta,delta)))
        if not length>np.float32(.0001) or not np.isfinite(length):continue
        direction=delta/length
        # Reflect the GL normal into top-row coordinates, keeping vertex side
        # order (and thus the native triangle-strip diagonal) intact.
        normal=np.array([direction[1],-direction[0]],np.float32)
        major=np.max(np.abs(direction))
        extent=np.float32(.5)*major
        previous=pixels[(first-1)%len(points)] if closed or first else a
        following=pixels[(last+1)%len(points)] if closed or last<len(points)-1 else b
        corners=[]
        for endpoint,neighbour in [(a,a-previous),(b,following-b)]:
            offset=normal
            neighbour_length=np.float32(np.sqrt(np.dot(neighbour,neighbour)))
            if neighbour_length>np.float32(.0001) and np.isfinite(neighbour_length):
                tangent_sum=neighbour/neighbour_length+direction
                tangent_length=np.float32(np.sqrt(np.dot(tangent_sum,tangent_sum)))
                if tangent_length>np.float32(.0001):
                    tangent=tangent_sum/tangent_length
                    miter=np.array([tangent[1],-tangent[0]],np.float32)
                    cosine=np.dot(miter,normal)
                    if cosine>np.float32(.49):offset=miter/cosine
            for side in [-1,1]:
                corner=endpoint+offset*np.float32(side)*extent
                corner=corner+np.array([0,-1/64],np.float32)
                if clip_positions is None:
                    corners.append(corner/size)
                else:
                    # Mirror the shader's gl_Position division, then viewport
                    # conversion, retaining its float32 operation boundaries.
                    projected=corner/(np.float32(.5)*size)
                    corners.append(projected*np.float32(.5)+np.float32(.5))
        result.append({'positions':np.array(corners,np.float32),
                       'colours':np.array([colour[first],colour[first],colour[last],colour[last]],np.float32)})
    return result


def draw_quad_lines(destination,positions,colours,*,additive,closed=False,quantize=True,clip_positions=None,raster_subpixel_bits=None):
    if raster_subpixel_bits is not None and (type(raster_subpixel_bits) is not int or not 4<=raster_subpixel_bits<=16):
        raise ValueError('raster subpixel bits must be an integer within 4..16')
    target=_finite(destination,'framebuffer').copy()
    height,width=target.shape[:2]
    triangles=np.array([[0,1,2],[2,1,3]],np.int64)
    for segment in quad_line_vertices(positions,colours,width=width,height=height,closed=closed,clip_positions=clip_positions):
        target=draw_triangles(target,segment['positions'],segment['colours'],triangles,
                              additive=additive,quantize=quantize,raster_subpixel_bits=raster_subpixel_bits)
    return target
