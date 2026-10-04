"""Explicit SwiftShader UNORM8 2D addressing/filter arithmetic.

Validated against float readbacks on the recorded emulator. This is a named
numerical profile, not portable GPU equivalence or support for float/sRGB images.
"""
import numpy as np

PROFILE='swiftshader-unorm8-fixed16-v1'


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
