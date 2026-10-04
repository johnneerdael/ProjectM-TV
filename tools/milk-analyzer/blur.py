"""Pinned projectM six-pass blur math on explicit RGB fields, without images.

Input and returned arrays use physical top-row-first framebuffer storage. The
first pass flips its source vertically; subsequent passes preserve orientation.
Shader sampling of a returned blur bank therefore uses bottom-origin OpenGL UV.
Widths, offsets, kernels, progressive encoding and first-level edge darkening
come from BlurTexture.cpp and its two fragment shaders. Precision/dithering can
differ from a GPU, and this is not a complete appearance predictor.
"""
import numpy as np
from spatial import sample2d
from feedback_field import unorm8


def pass_dimensions(width:int,height:int)->list[tuple[int,int]]:
    if any(type(v) is not int or v<=0 for v in (width,height)):
        raise ValueError('positive integer source size required')
    result=[]
    for i in range(6):
        if i%2==0 or i<2:width=max(16,width//2);height=max(16,height//2)
        result.append(((width+3)//16*16,(height+3)//4*4))
    return result


def native_ranges(minimum,maximum):
    low=np.asarray(minimum,dtype=np.float32).copy();high=np.asarray(maximum,dtype=np.float32).copy()
    if low.shape!=(3,) or high.shape!=(3,) or not np.all(np.isfinite([low,high])):
        raise ValueError('three finite blur ranges required')
    for i in range(3):
        if i:
            high[i]=min(high[i-1],high[i]);low[i]=max(low[i-1],low[i])
        if high[i]-low[i]<np.float32(.1):
            average=(low[i]+high[i])*.5
            # Preserve the pinned implementation's collapsed interval. Do not
            # silently replace its second subtraction with an intended plus.
            low[i]=average-np.float32(.1)*.5;high[i]=low[i]
    return low,high


def blur_bank(source,*,levels:int,minimum=(0,0,0),maximum=(1,1,1),
              edge_darken:float=0,quantize:bool=True)->dict[int,np.ndarray]:
    field=np.asarray(source,dtype=np.float32)
    if field.ndim!=3 or field.shape[2]!=3 or min(field.shape[:2])<=0 or not np.all(np.isfinite(field)):
        raise ValueError('finite RGB feedback source required')
    if type(levels) is not int or levels not in (1,2,3):raise ValueError('blur level1..3 required')
    if not np.isfinite(edge_darken):raise ValueError('finite edge darkening required')
    low,high=native_ranges(minimum,maximum)
    if np.any(high[:levels]-low[:levels]==0):raise ValueError('collapsed native blur range; division domain unresolved')
    scales=[];biases=[]
    for i in range(levels):
        if i==0:temp_min=low[0];temp_max=high[0]
        else:
            temp_min=(low[i]-low[i-1])/(high[i-1]-low[i-1])
            temp_max=(high[i]-low[i-1])/(high[i-1]-low[i-1])
        scale=np.float32(1)/(temp_max-temp_min)
        scales.append(scale);biases.append(-temp_min*scale)
    weights=np.array([4,3.8,3.5,2.9,1.9,1.2,.7,.3],dtype=np.float32)
    horizontal=weights.reshape(4,2).sum(axis=1)
    horizontal_offset=np.arange(4,dtype=np.float32)*2+2*weights[1::2]/horizontal
    vertical=np.array([weights[:4].sum(),weights[4:].sum()],dtype=np.float32)
    vertical_offset=np.array([2*(weights[2]+weights[3])/vertical[0],
                              2+2*(weights[6]+weights[7])/vertical[1]],dtype=np.float32)
    dimensions=pass_dimensions(field.shape[1],field.shape[0]);bank={}
    for index,(width,height) in enumerate(dimensions[:levels*2]):
        source_height,source_width=field.shape[:2]
        u,v=np.meshgrid((np.arange(width,dtype=np.float32)+.5)/width,
                        1-(np.arange(height,dtype=np.float32)+.5)/height)
        uv=np.stack((u,v),axis=-1)
        if index==0:uv[...,1]=1-uv[...,1]
        output=np.zeros((height,width,3),dtype=np.float32)
        if index%2==0:
            uv=uv+np.array([1/source_width,1/source_height],dtype=np.float32)
            for weight,offset in zip(horizontal,horizontal_offset):
                delta=np.array([offset/source_width,0],dtype=np.float32)
                output+=(sample2d(field,uv+delta,wrap=False,linear=True,origin='bottom')+
                         sample2d(field,uv-delta,wrap=False,linear=True,origin='bottom'))*weight
            output*=np.float32(.5)/horizontal.sum()
            output=output*scales[index//2]+biases[index//2]
        else:
            for weight,offset in zip(vertical,vertical_offset):
                delta=np.array([0,offset/source_height],dtype=np.float32)
                output+=(sample2d(field,uv+delta,wrap=False,linear=True,origin='bottom')+
                         sample2d(field,uv-delta,wrap=False,linear=True,origin='bottom'))*weight
            output*=np.float32(1)/(vertical.sum()*2)
            if index==1:
                t=np.minimum(np.minimum(u,v),1-np.maximum(u,v))
                factor=(np.float32(1)-np.float32(edge_darken))+np.float32(edge_darken)*np.clip(np.sqrt(t)*5,0,1)
                output*=factor[...,None]
        if not np.all(np.isfinite(output)):raise ValueError('unresolved blur numeric domain')
        field=unorm8(output) if quantize else np.clip(output,0,1)
        if index%2:bank[index//2+1]=field
    return bank
