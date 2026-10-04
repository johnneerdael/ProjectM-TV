"""Source FinalComposite mesh fields in the pipeline's physical texture rows."""
import numpy as np
from field_math import UnresolvedMath
from legacy_composite import corner_shades


def axis(count):
    indices=np.arange(count,dtype=np.int32)
    x=(indices-indices//(count//2)).astype(np.float32)*(np.float32(1)/np.float32(count-2))
    return np.where(x>.5,np.power(x*2-1,np.float32(3))*.5+.5,
                    (1-np.power(1-x*2,np.float32(3)))*.5).astype(np.float32)


def make_mesh(width,height):
    if any(type(n) is not int or n<=0 for n in (width,height)):raise ValueError('positive integer viewport required')
    u=axis(32);v=axis(24);uu,vv=np.meshgrid(u,v)
    positions=np.stack((uu*2-1,-(vv*2-1)),axis=-1)
    ax=np.float32(min(1,width/height));ay=np.float32(min(1,height/width))
    px=(uu*2-1)*ax;py=(vv*2-1)*ay
    rad=np.sqrt(px*px+py*py)/np.sqrt(ax*ax+ay*ay)
    pi=np.float32(np.pi);ang=np.arctan2(py,px);ang=np.where(ang<0,ang+np.float32(2*np.pi),ang)
    for row in range(24):
        for col in range(32):
            if col==15:
                mult=1.5 if row<11 else 1.25 if row==11 else .75 if row==12 else .5
            elif col==16:
                mult=1.5 if row<11 else 1.75 if row==11 else .25 if row==12 else .5
            elif row==11:mult=1 if col<15 else 2
            elif row==12:mult=1 if col<15 else 0
            else:continue
            ang[row,col]=pi*np.float32(mult)
    triangles=[]
    for row in range(23):
        if row==11:continue
        for col in range(31):
            if col==15:continue
            a=row*32+col;b=a+1;c=a+32;d=c+1
            if (int(col<16)+int(row<12)+int((col,row)==(16,12)))%2:
                triangles.extend([[a,b,d],[d,c,a]])
            else:triangles.extend([[c,a,b],[b,d,c]])
    return {'u':u,'v':v,'positions':positions,
            'uv':np.stack((uu+np.float32(.5)/width,vv+np.float32(.5)/height),axis=-1),
            'polar':np.stack((rad,ang),axis=-1),
            'triangles':np.asarray(triangles,dtype=np.int32)}


def vertex_colours(mesh,shade):
    shade=np.asarray(shade,dtype=np.float32)
    if shade.shape!=(4,3) or not np.all(np.isfinite(shade)):raise UnresolvedMath('finite four-corner shades required')
    x=mesh['positions'][...,0,None]*.5+.5;y=mesh['positions'][...,1,None]*.5+.5
    colors=shade[0]*x*y+shade[1]*(1-x)*y+shade[2]*x*(1-y)+shade[3]*(1-x)*(1-y)
    return np.concatenate((colors,np.ones(colors.shape[:2]+(1,),dtype=np.float32)),axis=-1)


def interpolate(mesh,values,query):
    data=np.asarray(values,dtype=np.float32);q=np.asarray(query,dtype=np.float32)
    if data.shape[:2]!=(24,32) or q.shape[-1:]!=(2,) or not np.all(np.isfinite(q)) or np.any((q<0)|(q>1)):
        raise UnresolvedMath('invalid composite field interpolation')
    col=np.clip(np.searchsorted(mesh['u'],q[...,0],side='right')-1,0,30)
    row=np.clip(np.searchsorted(mesh['v'],q[...,1],side='right')-1,0,22)
    fx=(q[...,0]-mesh['u'][col])/(mesh['u'][col+1]-mesh['u'][col])
    fy=(q[...,1]-mesh['v'][row])/(mesh['v'][row+1]-mesh['v'][row])
    extra=(None,)*(data.ndim-2);x=fx[(...,)+extra];y=fy[(...,)+extra]
    a,b,c,d=data[row,col],data[row,col+1],data[row+1,col],data[row+1,col+1]
    diagonal=((col<16).astype(int)+(row<12).astype(int)+((col==16)&(row==12)).astype(int))%2
    tlbr=np.where((fx>=fy)[(...,)+extra],a+(b-a)*x+(d-b)*y,a+(d-c)*x+(c-a)*y)
    trbl=np.where((fx+fy<=1)[(...,)+extra],a+(b-a)*x+(c-a)*y,d+(c-d)*(1-x)+(b-d)*(1-y))
    return np.where(diagonal[(...,)+extra],tlbr,trbl)


def composite_fields(width,height,*,time=None,hue_offsets=None,mesh=None):
    mesh=make_mesh(width,height) if mesh is None else mesh
    x,y=np.meshgrid((np.arange(width,dtype=np.float32)+.5)/width,
                    (np.arange(height,dtype=np.float32)+.5)/height)
    query=np.stack((x,y),axis=-1)
    result={'uv':interpolate(mesh,mesh['uv'],query),'polar':interpolate(mesh,mesh['polar'],query),
            'native_driver_verified':False,'seam_ownership':'numerical right/bottom; GPU raster ties unverified'}
    if time is not None and hue_offsets is not None:
        result['diffuse']=interpolate(mesh,vertex_colours(mesh,corner_shades(time,hue_offsets)),query)
    return result
