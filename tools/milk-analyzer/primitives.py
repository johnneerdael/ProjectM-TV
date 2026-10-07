"""Source-based custom primitive geometry, fill interpolation and blending.

Inputs are equation outputs and explicit texture functions, never native frames.
Coverage uses pixel centres and a shared-edge ownership rule. GPU subpixel
precision, line/point rasterization and anti-aliasing still require validation.
"""
import numpy as np
from feedback_field import unorm8


def _finite(value,name):
    array=np.asarray(value,dtype=np.float32)
    if not np.all(np.isfinite(array)):raise ValueError('nonfinite primitive '+name)
    return array


def colour_modulo(value):
    values=_finite(value,'colour');period=np.float32(256)/np.float32(255)
    return np.fmod(np.fmod(values,period)+period,period)


def blend_rgba(destination,source,*,additive:bool,quantize:bool=True):
    target=_finite(destination,'destination');colour=_finite(source,'source')
    if target.shape[-1:]!=(4,) or colour.shape[-1:]!=(4,):raise ValueError('RGBA blending required')
    colour=np.clip(colour,0,1);alpha=colour[...,3,None]
    output=colour*alpha+target*(1 if additive else 1-alpha)
    return unorm8(output) if quantize else np.clip(output,0,1)


def shape_fan(values:dict,*,aspect_y:float)->dict:
    sides=max(3,min(100,int(values.get('sides',4))))
    x=np.float32(values.get('x',.5));y=np.float32(values.get('y',.5))
    radius=np.float32(values.get('rad',.1));angle=np.float32(values.get('ang',0))
    if not np.all(np.isfinite([x,y,radius,angle,aspect_y])) or aspect_y<=0:
        raise ValueError('finite shape geometry and positive aspect required')
    theta=np.arange(sides,dtype=np.float32)/np.float32(sides)*np.float32(np.pi)*2+angle+np.float32(np.pi)*.25
    positions=np.empty((sides+2,2),dtype=np.float32);positions[0]=[x,1-y]
    positions[1:sides+1,0]=x+radius*np.cos(theta)*np.float32(aspect_y)*.5
    positions[1:sides+1,1]=1-y+radius*np.sin(theta)*.5
    positions[-1]=positions[1]
    centre=colour_modulo([values.get(c,default) for c,default in zip('rgba',[1,0,0,1])])
    perimeter=colour_modulo([values.get(c+'2',default) for c,default in zip('rgba',[0,1,0,0])])
    colours=np.tile(perimeter,(sides+2,1));colours[0]=centre
    indices=np.array([[0,i,i+1] for i in range(1,sides+1)],dtype=np.int64)
    return {'positions':positions,'colours':colours,'triangles':indices}


def draw_triangles(destination,positions,colours,triangles,*,additive:bool,
                   quantize:bool=True,texture_uv=None,texture_sample=None,raster_subpixel_bits=None):
    """Optionally snap window vertices to a declared grid, leaving attributes intact.

    Keep snapped coordinates in pixel space for coverage and interpolation;
    the numerical grid is an input, not a universal GPU precision assertion.
    """
    target=_finite(destination,'framebuffer').copy()
    points=_finite(positions,'positions');colour=_finite(colours,'colours')
    indices=np.asarray(triangles)
    if target.ndim!=3 or target.shape[2]!=4 or min(target.shape[:2])<=0:raise ValueError('RGBA framebuffer required')
    if points.ndim!=2 or points.shape[1]!=2 or colour.shape!=(len(points),4):raise ValueError('matching positions/RGBA attributes required')
    if indices.ndim!=2 or indices.shape[1]!=3 or not np.issubdtype(indices.dtype,np.integer):raise ValueError('integer triangle indices required')
    if np.any((indices<0)|(indices>=len(points))):raise ValueError('triangle index out of bounds')
    textured=texture_uv is not None or texture_sample is not None
    uv=_finite(texture_uv,'UV') if texture_uv is not None else None
    if textured and (texture_sample is None or uv is None or uv.shape!=(len(points),2)):
        raise ValueError('textured fills require UV attributes and an explicit sampler')
    height,width=target.shape[:2]
    if raster_subpixel_bits is not None and (type(raster_subpixel_bits) is not int or not 4<=raster_subpixel_bits<=16):
        raise ValueError('raster subpixel bits must be an integer within 4..16')
    pixel_space=raster_subpixel_bits is not None
    if pixel_space:
        scale=2**raster_subpixel_bits
        points=np.rint(points.astype(np.float64)*np.array([width,height])*scale)/scale
    coordinate_width,coordinate_height=(1,1) if pixel_space else (width,height)
    query_dtype=np.float64 if pixel_space else np.float32
    def edge(a,b,x,y):return (b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0])
    def inclusive(a,b):
        dx,dy=b-a
        return dy<0 or (dy==0 and dx>0)
    for triangle in indices:
        ids=triangle.copy();a,b,c=points[ids]
        area=edge(a,b,c[0],c[1])
        if area==0:continue
        if area<0:ids[[1,2]]=ids[[2,1]];a,b,c=points[ids];area=-area
        minimum=np.min([a,b,c],axis=0);maximum=np.max([a,b,c],axis=0)
        x0=max(0,int(np.ceil(float(minimum[0])*coordinate_width-.5)));x1=min(width-1,int(np.floor(float(maximum[0])*coordinate_width-.5)))
        y0=max(0,int(np.ceil(float(minimum[1])*coordinate_height-.5)));y1=min(height-1,int(np.floor(float(maximum[1])*coordinate_height-.5)))
        if x0>x1 or y0>y1:continue
        x,y=np.meshgrid((np.arange(x0,x1+1,dtype=query_dtype)+.5)/coordinate_width,
                        (np.arange(y0,y1+1,dtype=query_dtype)+.5)/coordinate_height)
        ea=edge(b,c,x,y);eb=edge(c,a,x,y);ec=edge(a,b,x,y)
        coverage=((ea>0)|((ea==0)&inclusive(b,c)))&((eb>0)|((eb==0)&inclusive(c,a)))&((ec>0)|((ec==0)&inclusive(a,b)))
        if not np.any(coverage):continue
        weights=np.stack((ea[coverage],eb[coverage],ec[coverage]),axis=-1)/area
        source=weights@colour[ids]
        if textured:
            sampled=_finite(texture_sample(weights@uv[ids]),'sampled texture')
            if sampled.shape!=source.shape:raise ValueError('texture sampler must return RGBA for each covered point')
            source*=sampled
        patch=target[y0:y1+1,x0:x1+1]
        patch[coverage]=blend_rgba(patch[coverage],source,additive=additive,quantize=quantize)
    return target


LEGACY_SHAPE_CENTRES='legacy-unshifted-shape-v1'
CORE_2322_SHAPE_CENTRES='projectmtv-core-2.3.22-shape-pixel-centres-v1'

def shape_centre_shift(width,height,policy):
    if policy not in (LEGACY_SHAPE_CENTRES,CORE_2322_SHAPE_CENTRES):
        raise ValueError('unknown shape centre policy')
    if width<=0 or height<=0:raise ValueError('positive shape target dimensions required')
    return np.asarray([.5/width,.5/height] if policy==CORE_2322_SHAPE_CENTRES else [0,0],np.float32)

def draw_shape(destination,values:dict,*,aspect_y:float,quantize:bool=True,
               texture_sample=None,texture_aspect_y:float|None=None,raster_subpixel_bits=None,centre_policy=LEGACY_SHAPE_CENTRES):
    """Render a source-equation shape fill; unresolved outlines remain explicit.

    The caller supplies the correct previous-main or named-image sampler. It
    must not accidentally substitute the current, already drawn framebuffer.
    """
    fan=shape_fan(values,aspect_y=aspect_y)
    textured=int(values.get('textured',0))!=0
    if textured and texture_sample is None:raise ValueError('shape texture input required')
    if values.get('border_a',0)>.0001:raise ValueError('shape outline rasterization is not yet implemented')
    uv=None
    if textured:
        zoom=np.float32(values.get('tex_zoom',1))
        angle=np.float32(values.get('tex_ang',0))
        if not np.isfinite(zoom) or zoom==0 or not np.isfinite(angle):raise ValueError('unresolved shape texture domain')
        sides=len(fan['positions'])-2
        texture_aspect=np.float32(aspect_y if texture_aspect_y is None else texture_aspect_y)
        theta=np.arange(sides,dtype=np.float32)/np.float32(sides)*np.float32(np.pi)*2+angle+np.float32(np.pi)*.25
        uv=np.empty_like(fan['positions']);uv[0]=[.5,.5]
        uv[1:sides+1,0]=.5+.5*np.cos(theta)/zoom*texture_aspect
        uv[1:sides+1,1]=.5+.5*np.sin(theta)/zoom
        uv[-1]=uv[1]
    height,width=np.asarray(destination).shape[:2]
    positions=fan['positions']+shape_centre_shift(width,height,centre_policy)
    return draw_triangles(destination,positions,fan['colours'],fan['triangles'],
                          additive=int(values.get('additive',0))!=0,quantize=quantize,
                          texture_uv=uv,texture_sample=texture_sample,raster_subpixel_bits=raster_subpixel_bits)


def draw_borders(destination,values:dict,*,quantize:bool=True,raster_subpixel_bits=None):
    """Pinned Border::Draw fans, outer then inner, with ordinary alpha blending."""
    target=_finite(destination,'framebuffer').copy()
    if raster_subpixel_bits is not None and (type(raster_subpixel_bits) is not int or not 4<=raster_subpixel_bits<=16):
        raise ValueError('raster subpixel bits must be an integer within 4..16')
    outer=np.float32(values.get('ob_size',.01));inner=np.float32(values.get('ib_size',.01))
    if not np.all(np.isfinite([outer,inner])):raise ValueError('nonfinite border size')
    for index,prefix in enumerate(['ob_','ib_']):
        defaults=[0,0,0,0] if index==0 else [.25,.25,.25,0]
        colour=_finite([values.get(prefix+c,d) for c,d in zip('rgba',defaults)],'border colour')
        if colour[3]<=np.float32(.001):continue
        inside=np.float32(1)-outer-(inner if index else np.float32(0))
        outside=np.float32(1)-outer if index else np.float32(1)
        vertices=np.array([[inside,inside],[outside,outside],[outside,-outside],[inside,-inside]],dtype=np.float32)
        colours=np.tile(colour,(4,1))
        for rotation in range(4):
            # Native inverted projection followed by top-origin coordinates.
            positions=vertices*np.float32(.5)+np.float32(.5)
            target=draw_triangles(target,positions,colours,[[0,1,2],[0,2,3]],additive=False,quantize=quantize,
                                  raster_subpixel_bits=raster_subpixel_bits)
            x=vertices[:,0].copy();vertices[:,0]=-vertices[:,1];vertices[:,1]=x
    return target
