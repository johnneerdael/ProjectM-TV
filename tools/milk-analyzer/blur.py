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
from engine_profiles import CORE_2315_BLUR, LEGACY_BLUR
from native_values import native_scalar
from custom_wave import _fmaf

SEPARATE_ARITHMETIC='separate-float32-v1'
APPLE_VERTICAL_FMA='apple-m4pro-gles-vertical-blur-fma-v1'


def vertical_weighted_sum(first,second,first_weight,second_weight,*,arithmetic_profile=SEPARATE_ARITHMETIC):
    if arithmetic_profile not in (SEPARATE_ARITHMETIC,APPLE_VERTICAL_FMA):
        raise ValueError('unsupported blur arithmetic profile')
    a=np.asarray(first,np.float32);b=np.asarray(second,np.float32)
    if a.shape!=b.shape or not np.all(np.isfinite([a,b])):
        raise ValueError('finite matching blur sample pairs required')
    weights=np.asarray([first_weight,second_weight],np.float32)
    if not np.all(np.isfinite(weights)):raise ValueError('finite blur weights required')
    base=a*weights[0]
    if arithmetic_profile==SEPARATE_ARITHMETIC:return base+b*weights[1]
    fused=_fmaf()
    return np.asarray([fused(weights[1],x,y) for x,y in zip(b.flat,base.flat)],np.float32).reshape(a.shape)


def pass_dimensions(width:int,height:int)->list[tuple[int,int]]:
    if any(type(v) is not int or v<=0 for v in (width,height)):
        raise ValueError('positive integer source size required')
    result=[]
    for i in range(6):
        if i%2==0 or i<2:width=max(16,width//2);height=max(16,height//2)
        result.append(((width+3)//16*16,(height+3)//4*4))
    return result


def _coefficients(low, high):
    """Mirror patch0046's progressive float32 normalization producer."""
    scales=[];biases=[]
    with np.errstate(all='ignore'):
        gaps=high-low
        if not np.all(np.isfinite([low,high,gaps])) or np.any(gaps<=0):return None
        for i in range(3):
            a=low[i] if i==0 else np.float32((low[i]-low[i-1])/gaps[i-1])
            b=high[i] if i==0 else np.float32((high[i]-low[i-1])/gaps[i-1])
            denominator=np.float32(b-a)
            if not np.all(np.isfinite([a,b,denominator])) or denominator<=0:return None
            scale=np.float32(1)/denominator;bias=np.float32(-a*scale)
            if not np.all(np.isfinite([scale,bias])) or scale<=0:return None
            scales.append(scale);biases.append(bias)
    return scales,biases


def native_ranges(minimum,maximum,*,policy=LEGACY_BLUR):
    if policy not in {LEGACY_BLUR,CORE_2315_BLUR}:raise ValueError('unsupported blur range policy')
    current=policy==CORE_2315_BLUR
    if current:
        raw_low=np.asarray([native_scalar(v,allow_ieee=True) for v in minimum],dtype=np.float64)
        raw_high=np.asarray([native_scalar(v,allow_ieee=True) for v in maximum],dtype=np.float64)
        if raw_low.shape!=(3,) or raw_high.shape!=(3,):raise ValueError('three blur ranges required')
        if not np.all(np.isfinite([raw_low,raw_high])) or np.any(np.abs([raw_low,raw_high])>np.finfo(np.float32).max):
            return np.zeros(3,dtype=np.float32),np.ones(3,dtype=np.float32)
        minimum,maximum=raw_low,raw_high
    low=np.asarray(minimum,dtype=np.float32).copy();high=np.asarray(maximum,dtype=np.float32).copy()
    if low.shape!=(3,) or high.shape!=(3,) or not np.all(np.isfinite([low,high])):
        raise ValueError('three finite blur ranges required')
    with np.errstate(all='ignore'):
        for i in range(3):
            if i:
                high[i]=min(high[i-1],high[i]);low[i]=max(low[i-1],low[i])
            if high[i]-low[i]<np.float32(.1):
                average=np.float32((low[i]+high[i])*np.float32(.5))
                low[i]=np.float32(average-np.float32(.1)*np.float32(.5))
                high[i]=np.float32(average+np.float32(.1)*np.float32(.5)) if current else low[i]
    if current and _coefficients(low,high) is None:
        return np.zeros(3,dtype=np.float32),np.ones(3,dtype=np.float32)
    return low,high


def blur_bank(source,*,levels:int,minimum=(0,0,0),maximum=(1,1,1),
              edge_darken:float=0,quantize:bool=True,policy=LEGACY_BLUR,sampling_profile='portable',arithmetic_profile=SEPARATE_ARITHMETIC)->dict[int,np.ndarray]:
    from unorm_sampler import sampler_2d
    sample=sampler_2d(sampling_profile)
    if arithmetic_profile not in (SEPARATE_ARITHMETIC,APPLE_VERTICAL_FMA):raise ValueError('unsupported blur arithmetic profile')
    if sampling_profile!='portable' and not quantize:
        raise ValueError('texture profile requires actual unorm blur storage')
    field=np.asarray(source,dtype=np.float32)
    if field.ndim!=3 or field.shape[2]!=3 or min(field.shape[:2])<=0 or not np.all(np.isfinite(field)):
        raise ValueError('finite RGB feedback source required')
    if type(levels) is not int or levels not in (1,2,3):raise ValueError('blur level1..3 required')
    if not np.isfinite(edge_darken):raise ValueError('finite edge darkening required')
    low,high=native_ranges(minimum,maximum,policy=policy)
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
                output+=(sample(field,uv+delta,wrap=False,linear=True,origin='bottom')+
                         sample(field,uv-delta,wrap=False,linear=True,origin='bottom'))*weight
            output*=np.float32(.5)/horizontal.sum()
            output=output*scales[index//2]+biases[index//2]
        else:
            pairs=[]
            for weight,offset in zip(vertical,vertical_offset):
                delta=np.array([0,offset/source_height],dtype=np.float32)
                pairs.append(sample(field,uv+delta,wrap=False,linear=True,origin='bottom')+
                             sample(field,uv-delta,wrap=False,linear=True,origin='bottom'))
            output=vertical_weighted_sum(*pairs,*vertical,arithmetic_profile=arithmetic_profile)
            output*=np.float32(1)/(vertical.sum()*2)
            if index==1:
                t=np.minimum(np.minimum(u,v),1-np.maximum(u,v))
                factor=(np.float32(1)-np.float32(edge_darken))+np.float32(edge_darken)*np.clip(np.sqrt(t)*5,0,1)
                output*=factor[...,None]
        if not np.all(np.isfinite(output)):raise ValueError('unresolved blur numeric domain')
        field=unorm8(output) if quantize else np.clip(output,0,1)
        if index%2:bank[index//2+1]=field
    return bank
