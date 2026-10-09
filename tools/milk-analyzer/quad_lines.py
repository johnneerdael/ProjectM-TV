"""Patched GLES hard-edge quad-line vertex math in top-row screen coordinates.

Port of ProjectM-TV patch 0024 LineVertexShaderGlsl330.vert and LineTieBias.
An explicit reference size scales line width as native LineScale; the omitted
reference preserves the historical one-pixel profile and1024x768 area guard.
Authored targets with zero reference use canonical GL lines instead of quads.
Triangle raster precision remains the declared source model, not GPU identity.
"""
import math
import numpy as np
from primitives import _finite, draw_triangles

PROFILE='projectmtv-gles-quad-lines-v1'
LEGACY_VIEWPORT='normalized-float32-v1'
RETAINED_CLIP_VIEWPORT='retained-clip-window-v1'


def line_scale(width,height,reference_size=None):
    """Native double-area ratio, narrowed to float32 before the minimum of1."""
    if any(type(n) is not int or not 0<n<2**31 for n in (width,height)):
        raise ValueError('positive int32 line viewport required')
    if reference_size is None:return np.float32(1)
    if (not isinstance(reference_size,(tuple,list)) or len(reference_size)!=2 or
            any(type(n) is not int or not 0<=n<2**31 for n in reference_size)):
        raise ValueError('nonnegative int32 line reference size required')
    rw,rh=reference_size
    if rw==rh==0:return np.float32(0)
    if not rw or not rh:raise ValueError('line reference must have two positive dimensions or two zeros')
    return max(np.float32(1),np.float32(math.sqrt((float(width)*height)/(float(rw)*rh))))


def dot_style(kind,thick,scale):
    """Native integer dot raster size and area brightness, before GPU coverage."""
    if kind not in {'main','custom','shape','motion'} or type(thick) is not bool:
        raise ValueError('known dot kind and boolean thickness required')
    scale=np.float32(scale)
    if not np.isfinite(scale) or scale<=0:raise ValueError('finite positive dot scale required')
    size=np.float32(2 if kind=='main' or thick else 1)*scale
    raster=np.maximum(np.float32(1),np.ceil(size-np.float32(.0001)))
    return {'size':float(raster),'alpha_scale':float((size*size)/(raster*raster))}


def quad_line_vertices(positions,colours,*,width,height,closed=False,clip_positions=None,viewport_policy=LEGACY_VIEWPORT,reference_size=None):
    if viewport_policy not in (LEGACY_VIEWPORT,RETAINED_CLIP_VIEWPORT):
        raise ValueError('unknown quad-line viewport policy')
    if viewport_policy==RETAINED_CLIP_VIEWPORT and clip_positions is None:
        raise ValueError('retained viewport requires explicit clip positions')
    scale=line_scale(width,height,reference_size)
    if scale==0:raise ValueError('zero line reference requires canonical GL lines')
    if reference_size is None and width*height>1024*768:
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
        extent=(np.float32(.5)*scale)*major
        previous=pixels[(first-1)%len(points)] if closed or first else a
        following=pixels[(last+1)%len(points)] if closed or last<len(points)-1 else b
        corners=[];window_corners=[]
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
                    window_corners.append((projected.astype(np.float64)*.5+.5)*size.astype(np.float64))
        segment={'positions':np.array(corners,np.float32),
                 'colours':np.array([colour[first],colour[first],colour[last],colour[last]],np.float32)}
        if viewport_policy==RETAINED_CLIP_VIEWPORT:
            segment['window_positions']=np.array(window_corners,np.float64)
        result.append(segment)
    return result


def draw_quad_lines(destination,positions,colours,*,additive,closed=False,quantize=True,clip_positions=None,raster_subpixel_bits=None,viewport_policy=LEGACY_VIEWPORT,reference_size=None):
    if viewport_policy==RETAINED_CLIP_VIEWPORT and raster_subpixel_bits is None:
        raise ValueError('retained viewport requires explicit raster grid')
    if raster_subpixel_bits is not None and (type(raster_subpixel_bits) is not int or not 4<=raster_subpixel_bits<=16):
        raise ValueError('raster subpixel bits must be an integer within 4..16')
    target=_finite(destination,'framebuffer').copy()
    height,width=target.shape[:2]
    segments=quad_line_vertices(positions,colours,width=width,height=height,closed=closed,
        clip_positions=clip_positions,viewport_policy=viewport_policy,reference_size=reference_size)
    return _draw_quad_segments(target,segments,additive=additive,quantize=quantize,
                               raster_subpixel_bits=raster_subpixel_bits)


def _draw_quad_segments(destination,segments,*,additive,quantize,raster_subpixel_bits):
    """Batch generated quads without reordering triangle blends or rounding.

    Each segment remains four independent vertices. Concatenation changes only
    ownership/allocation: draw_triangles still visits the original triangle order
    and quantizes each blend. Callers supply an already owned framebuffer.
    """
    if not segments:return destination
    positions=np.concatenate([segment['positions'] for segment in segments])
    colours=np.concatenate([segment['colours'] for segment in segments])
    triangles=(np.arange(len(segments),dtype=np.int64)[:,None,None]*4+
               np.array([[0,1,2],[2,1,3]],np.int64)).reshape(-1,3)
    windows=[segment.get('window_positions') for segment in segments]
    window_positions=None if windows[0] is None else np.concatenate(windows)
    return draw_triangles(destination,positions,colours,triangles,additive=additive,
        quantize=quantize,raster_subpixel_bits=raster_subpixel_bits,window_positions=window_positions)
