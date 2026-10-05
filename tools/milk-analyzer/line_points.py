"""Canonical unsmoothed OpenGL line/point coverage on source-derived geometry.

Use diamond-exit, half-open line endpoints and w=1 varying interpolation. Native
GL permits bounded alternative raster rules, so this is an explicit canonical
model, not a guarantee of pixel-identical driver output. Coordinates are top
origin; the infinitesimal GL perturbation is reflected into that convention.
"""
import numpy as np
from primitives import _finite,blend_rgba


def _inputs(destination,positions,colours):
    target=_finite(destination,'framebuffer').copy();points=_finite(positions,'positions');colour=_finite(colours,'colours')
    if target.ndim!=3 or target.shape[-1]!=4 or min(target.shape[:2])<1:raise ValueError('RGBA framebuffer required')
    if points.ndim!=2 or points.shape[1]!=2:raise ValueError('two-component positions required')
    if colour.shape==(4,):colour=np.tile(colour,(len(points),1))
    if colour.shape!=(len(points),4):raise ValueError('matching per-vertex RGBA required')
    return target,points.astype(np.float64),colour


def _clip(a,b,width,height):
    low,high=0.,1.;delta=b-a
    for axis,limit in [(0,width),(1,height)]:
        if delta[axis]==0:
            if a[axis]<0 or a[axis]>limit:return None
        else:
            t0=-a[axis]/delta[axis];t1=(limit-a[axis])/delta[axis]
            low=max(low,min(t0,t1));high=min(high,max(t0,t1))
    if low>=high:return None
    return low,high


def draw_lines(destination,positions,colours,*,additive:bool,closed=False,quantize=True):
    target,points,colour=_inputs(destination,positions,colours);height,width=target.shape[:2]
    points=points*np.array([width,height]);segments=list(zip(range(len(points)-1),range(1,len(points))))
    if closed and len(points)>1:segments.append((len(points)-1,0))
    normals=np.array([[1,1],[1,-1],[-1,1],[-1,-1]],dtype=np.float64)
    perturb=np.array([-1e-5,1e-10])
    for first,last in segments:
        original_a,original_b=points[first],points[last];interval=_clip(original_a,original_b,width,height)
        if interval is None:continue
        low,high=interval;delta=original_b-original_a
        a=original_a+delta*low;b=original_a+delta*high
        ca=colour[first]+(colour[last]-colour[first])*low;cb=colour[first]+(colour[last]-colour[first])*high
        minimum=np.minimum(a,b)-.5;maximum=np.maximum(a,b)+.5
        x0=max(0,int(np.floor(minimum[0])));x1=min(width-1,int(np.floor(maximum[0])))
        y0=max(0,int(np.floor(minimum[1])));y1=min(height-1,int(np.floor(maximum[1])))
        if x0>x1 or y0>y1:continue
        x,y=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5);centres=np.stack((x,y),axis=-1)
        pa=a+perturb;pb=b+perturb;direction=pb-pa
        relative=(pa-centres)@normals.T;slope=direction@normals.T
        enter=np.zeros(x.shape);leave=np.ones(x.shape);possible=np.ones(x.shape,dtype=bool)
        for index,d in enumerate(slope):
            if d==0:possible&=relative[...,index]<.5
            elif d>0:leave=np.minimum(leave,(.5-relative[...,index])/d)
            else:enter=np.maximum(enter,(.5-relative[...,index])/d)
        endpoint_inside=np.all((pb-centres)@normals.T<.5,axis=-1)
        coverage=possible&(enter<leave)&~endpoint_inside
        if not np.any(coverage):continue
        parameter=np.sum((centres[coverage]-a)*(b-a),axis=-1)/np.dot(b-a,b-a)
        source=ca+(cb-ca)*parameter[:,None]
        patch=target[y0:y1+1,x0:x1+1]
        patch[coverage]=blend_rgba(patch[coverage],source,additive=additive,quantize=quantize)
    return target


def draw_points(destination,positions,colours,*,point_size=1,additive:bool,quantize=True,subpixel_bits=None):
    """Optionally round window centres to an explicit grid with np.rint (ties to even).

    This is a declared mathematical input, not a universal GPU precision rule.
    Native halfway ties remain unverified; None retains canonical coverage.
    """
    target,points,colour=_inputs(destination,positions,colours);height,width=target.shape[:2]
    if not np.isfinite(point_size) or point_size<=0:raise ValueError('positive finite point size required')
    if subpixel_bits is not None and (type(subpixel_bits) is not int or not 0<=subpixel_bits<=16):
        raise ValueError('point subpixel bits must be an integer within 0..16')
    subpixel_scale=None if subpixel_bits is None else 2**subpixel_bits
    half=point_size*.5
    for point,rgba in zip(points,colour):
        if np.any((point<0)|(point>1)):continue # Point clip tests its centre, not its square.
        px,py=point*np.array([width,height])
        if subpixel_scale is not None:
            px,py=np.rint(np.array([px,py])*subpixel_scale)/subpixel_scale
        x0=max(0,int(np.ceil(px-half-.5)));x1=min(width-1,int(np.ceil(px+half-.5))-1)
        y0=max(0,int(np.floor(py-half-.5))+1);y1=min(height-1,int(np.floor(py+half-.5)))
        if x0>x1 or y0>y1:continue
        patch=target[y0:y1+1,x0:x1+1];patch[:]=blend_rgba(patch,rgba,additive=additive,quantize=quantize)
    return target
