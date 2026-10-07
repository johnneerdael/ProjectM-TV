"""Explicit driver profiles for UNORM8 2D addressing/filter arithmetic.

Validated against float readbacks on the recorded emulator. This is a named
numerical profile, not portable GPU equivalence or support for float/sRGB images.
"""
import numpy as np

PROFILE='swiftshader-unorm8-fixed16-v1'
APPLE_PROFILE='apple-m4pro-gles-unorm8-fixed8-fraction4-v1'
APPLE_VOLUME_PROFILE='apple-m4pro-gles-unorm8-fixed8-fraction4-volume-v1'


def sampler_2d(profile):
    if profile in (APPLE_PROFILE,APPLE_VOLUME_PROFILE):return sample_apple_unorm8
    if profile=='portable':
        from spatial import sample2d
        return sample2d
    raise ValueError('unsupported texture sampling profile')


def sample_apple_volume_unorm8(volume,uvw,*,wrap:bool,linear:bool):
    """Observed Apple UNORM8 volume filtering, in raw upload [z,y,x] order.

    Apply fixed8 fractions, conserving fixed16 X/Z coefficient pairs across Y,
    then final fixed4 raw-byte rounding. Integer accumulation avoids premature
    float32 rounding near the final threshold.
    """
    field=np.asarray(volume,dtype=np.float32);coords=np.asarray(uvw,dtype=np.float32)
    if (field.ndim!=4 or field.shape[-1] not in (3,4) or min(field.shape[:3])<1 or
            max(field.shape[:3])>32768 or coords.shape[-1:]!=(3,) or
            not np.all(np.isfinite(field)) or not np.all(np.isfinite(coords))):
        raise ValueError('finite RGB/RGBA unorm volume and three-component coordinates required')
    if type(wrap) is not bool or type(linear) is not bool:
        raise ValueError('explicit volume wrap/filter required')
    packed=np.rint(field*255)
    if np.any((packed<0)|(packed>255)) or not np.allclose(field,packed/255,rtol=0,atol=1e-7):
        raise ValueError('actual unorm8 texels required for Apple volume profile')
    packed=packed.astype(np.int64)
    depth,height,width=field.shape[:3];size=np.array([width,height,depth],np.float32)
    coords=np.mod(coords,1) if wrap else np.clip(coords,0,1)
    query=coords*size
    def fetch(x,y,z):
        x=np.mod(x,width) if wrap else np.clip(x,0,width-1)
        y=np.mod(y,height) if wrap else np.clip(y,0,height-1)
        z=np.mod(z,depth) if wrap else np.clip(z,0,depth-1)
        return packed[z,y,x]
    if not linear:
        index=np.floor(query).astype(np.int64)
        return (fetch(index[...,0],index[...,1],index[...,2])/255).astype(np.float32)
    query-=np.float32(.5);index=np.floor(query).astype(np.int64)
    fraction=np.floor((query-index)*256+.5).astype(np.int64)
    x,y,z=index[...,0],index[...,1],index[...,2]
    fx,fy,fz=fraction[...,0],fraction[...,1],fraction[...,2]
    numerator=np.zeros(coords.shape[:-1]+(field.shape[-1],),dtype=np.int64)
    for iz in (0,1):
        for ix in (0,1):
            base=(fx if ix else 256-fx)*(fz if iz else 256-fz)
            lower=(base*(256-fy)+128)//256
            upper=base-lower
            numerator+=fetch(x+ix,y,z+iz)*lower[...,None]
            numerator+=fetch(x+ix,y+1,z+iz)*upper[...,None]
    raw16=(numerator+2048)//4096
    return (raw16.astype(np.float32)/16/255).astype(np.float32)


def sample_apple_unorm8(texture,uv,*,wrap:bool,linear:bool,origin:str):
    """Apply the observed Apple emulator's 2D UNORM8 sampler arithmetic.

    Fractions round to eight bits; filtered byte values round to four fractional
    bits. Both exact half-way rules round upward. This is an explicit driver
    profile, not a portable texture-language rule or support for float/sRGB.
    """
    field=np.asarray(texture,dtype=np.float32);coords=np.asarray(uv,dtype=np.float32)
    if (field.ndim!=3 or field.shape[-1] not in (3,4) or min(field.shape[:2])<1 or
            max(field.shape[:2])>32768 or coords.shape[-1:]!=(2,) or
            not np.all(np.isfinite(field)) or not np.all(np.isfinite(coords))):
        raise ValueError('finite RGB/RGBA unorm texture and two-component coordinates required')
    if origin not in ('top','bottom') or type(wrap) is not bool or type(linear) is not bool:
        raise ValueError('explicit sampling origin/wrap/filter required')
    packed=np.rint(field*255)
    if np.any((packed<0)|(packed>255)) or not np.allclose(field,packed/255,rtol=0,atol=1e-7):
        raise ValueError('actual unorm8 texels required for Apple sampler profile')
    height,width=field.shape[:2]
    coords=np.mod(coords,1) if wrap else np.clip(coords,0,1)
    query=coords*np.array([width,height],dtype=np.float32)
    def fetch(x,y):
        x=np.mod(x,width) if wrap else np.clip(x,0,width-1)
        y=np.mod(y,height) if wrap else np.clip(y,0,height-1)
        if origin=='bottom':y=height-1-y
        return packed[y,x]
    if not linear:
        index=np.floor(query).astype(np.int64)
        return (fetch(index[...,0],index[...,1])/255).astype(np.float32)
    query-=np.float32(.5);index=np.floor(query).astype(np.int64)
    fraction=np.floor((query-index)*256+.5).astype(np.float32)/256
    x,y=index[...,0],index[...,1];fx,fy=fraction[...,0,None],fraction[...,1,None]
    raw=(fetch(x,y)*(1-fx)+fetch(x+1,y)*fx)*(1-fy)+(fetch(x,y+1)*(1-fx)+fetch(x+1,y+1)*fx)*fy
    return (np.floor(raw*16+.5)/16/255).astype(np.float32)


def sample_unorm8(texture,uv,*,wrap:bool,linear:bool,origin:str):
    field=np.asarray(texture,dtype=np.float32);coords=np.asarray(uv,dtype=np.float32)
    if (field.ndim!=3 or field.shape[-1] not in (3,4) or not 1<=min(field.shape[:2]) or
            max(field.shape[:2])>32768 or coords.shape[-1:]!=(2,) or
            not np.all(np.isfinite(field)) or not np.all(np.isfinite(coords))):
        raise ValueError('finite RGB/RGBA unorm texture and two-component coordinates required')
    if origin not in ('top','bottom') or type(wrap) is not bool or type(linear) is not bool:
        raise ValueError('explicit sampling origin/wrap/filter required')
    packed=np.rint(field*255)
    if np.any((packed<0)|(packed>255)) or not np.allclose(field,packed/255,rtol=0,atol=1e-7):
        raise ValueError('actual unorm8 texels required for fixed sampler profile')
    packed=packed.astype(np.int64)*256
    height,width=field.shape[:2];size=np.array([width,height],dtype=np.int64)
    addressed=np.mod(coords,1) if wrap else np.clip(coords,0,np.float32(65535/65536))
    fixed=np.floor(addressed*np.float32(65536)).astype(np.int64)
    if wrap:fixed&=65535
    def fetch(position):
        index=position*size//65536;x,y=index[...,0],index[...,1]
        if origin=='bottom':y=height-1-y
        return packed[y,x]
    if not linear:return fetch(fixed).astype(np.float32)*np.float32(1/65280)
    half=32768//size
    lower=fixed-half;upper=fixed+half
    lower=lower&65535 if wrap else np.clip(lower,0,65535)
    upper=upper&65535 if wrap else np.clip(upper,0,65535)
    fraction=(lower*size)&65535;inverse=65535-fraction
    fx,fy=fraction[...,0],fraction[...,1];ix,iy=inverse[...,0],inverse[...,1]
    positions=[lower,np.stack((upper[...,0],lower[...,1]),-1),
               np.stack((lower[...,0],upper[...,1]),-1),upper]
    weights=[(ix*iy)>>16,(fx*iy)>>16,(ix*fy)>>16,(fx*fy)>>16]
    total=sum((fetch(position)*weight[...,None])>>16 for position,weight in zip(positions,weights))
    return total.astype(np.float32)*np.float32(1/65280)
