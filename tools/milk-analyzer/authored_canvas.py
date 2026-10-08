"""Understood authored/native feedback operators for the pinned TV engine.

The authored state owns recurrence. Native detail is a centered residual whose
gain is shared per block/channel, preserving its zero mean before RGBA8 storage.
These operators do not execute equations, choose target policies or certify GPU
sampling. The full two-target forecaster must supply those separate contracts.
"""
import math
import numpy as np

from feedback_field import unorm8
from spatial import sample2d


def select_canvas(width, height, reference_width, reference_height):
    """Match FeedbackDetailCanvas; activation is a separate JNI setting."""
    dimensions=(width,height,reference_width,reference_height)
    if any(type(value) is not int for value in dimensions):
        raise ValueError('integer canvas dimensions required')
    if min(dimensions)<=0:return None
    # Positive std::lround uses half-away rounding, unlike Python round().
    scale=math.floor(math.sqrt((width*height)/(reference_width*reference_height))+.5)
    if scale<2 or width%scale or height%scale:return None
    return width//scale,height//scale,scale


def detail_configuration(*,native_size,physical_size,trails_level):
    """Released JNI selection math; allocation success is a separate input.

    Physical height gates native trails. A transition-scaled render extent does
    not change that gate. Initial uniforms use ShaderCanvasSize before integer
    detail selection replaces its reference dimensions for frame execution.
    """
    for size in (native_size,physical_size):
        if (not isinstance(size,(tuple,list)) or len(size)!=2 or
                any(type(n) is not int or not 0<n<2**31 for n in size)):
            raise ValueError('two positive int32 physical/native dimensions required')
    if type(trails_level) is not int or not 0<=trails_level<=2:
        raise ValueError('native trails level0..2 required')
    width,height=native_size
    active=physical_size[1]>1330
    reference=(1280,720) if active else (1024,768)
    alpha=trails_level*.5 if active else -1.0
    from quad_lines import line_scale
    scale=line_scale(width,height,reference)
    # BlurSourceFor first divides narrowed float32 dimensions by float32 scale;
    # then positive std::lround rounds the reported initialization canvas.
    initial=tuple(max(1,math.floor(float(np.float32(n)/scale)+.5))
                  for n in native_size) if scale>1 else tuple(native_size)
    canvas=select_canvas(width,height,*reference) if active else None
    return {'native_size':tuple(native_size),'physical_size':tuple(physical_size),
            'reference_size':reference,'alpha':alpha,'initial_shader_canvas':initial,
            'authored_size':None if canvas is None else canvas[:2],
            'scale':None if canvas is None else canvas[2],
            'selection_status':'disabled' if not active else
                               'integer-canvas-selected' if canvas is not None else 'no-integer-canvas',
            'resource_allocation_verified':False}


def _rgba(values):
    field=np.asarray(values,dtype=np.float32)
    if (field.ndim!=3 or field.shape[-1]!=4 or min(field.shape[:2])<=0 or
            not np.all(np.isfinite(field))):
        raise ValueError('finite nonempty RGBA field required')
    if np.any((field<0)|(field>1)):
        raise ValueError('normalized RGBA storage required')
    return field


def _scale(field, scale):
    if type(scale) is not int or scale<1 or any(n%scale for n in field.shape[:2]):
        raise ValueError('positive integer block ratio required')


def block_downsample(values, scale, *, quantize=True):
    """Box average in shader float32 order; arrays are top-row-first."""
    field=_rgba(values);_scale(field,scale)
    result=np.zeros((field.shape[0]//scale,field.shape[1]//scale,4),np.float32)
    # gl_FragCoord and texelFetch rows run bottom-up within each physical block.
    for j in reversed(range(scale)):
        for i in range(scale):result=np.add(result,field[j::scale,i::scale],dtype=np.float32)
    result=np.divide(result,np.float32(scale*scale),dtype=np.float32)
    return unorm8(result) if quantize else result


def _upsample(values,width,height,sampling_profile):
    x,y=np.meshgrid((np.arange(width,dtype=np.float32)+np.float32(.5))/np.float32(width),
                    (np.arange(height,dtype=np.float32)+np.float32(.5))/np.float32(height))
    uv=np.stack((x,y),axis=-1)
    if sampling_profile=='portable':sample=sample2d
    else:
        from unorm_sampler import sampler_2d
        sample=sampler_2d(sampling_profile)
    return sample(values,uv,wrap=False,linear=True,origin='top')


def combine_detail(authored_warp,native_warp,*,alpha,output_size,quantize=True,sampling_profile='portable'):
    """Upsample authored warp plus centered, blockwise headroom-limited detail.

    Standard alpha0 samples only authored state. For positive gain, downsampled
    native warp is RGBA8 stored, then upsampled to obtain its low-frequency part.
    Subtract the residual's actual block mean before selecting one gain per
    block/channel; per-pixel clamps would change that mean and corrupt fidelity.
    """
    low=_rgba(authored_warp)
    if (len(output_size)!=2 or any(type(n) is not int or n<=0 for n in output_size)):
        raise ValueError('positive integer output size required')
    width,height=output_size
    scale=width//low.shape[1]
    if scale<1 or width!=low.shape[1]*scale or height!=low.shape[0]*scale:
        raise ValueError('same integer authored/output ratio required')
    amount=np.float32(alpha)
    if not np.isfinite(amount) or not 0<=amount<=1:
        raise ValueError('finite detail gain within0..1 required')
    base=_upsample(low,width,height,sampling_profile)
    if amount==0:return unorm8(base) if quantize else base
    if native_warp is None:raise ValueError('positive gain requires native warp')
    high=_rgba(native_warp)
    if high.shape!=base.shape:raise ValueError('native warp dimensions differ from output')
    down=block_downsample(high,scale,quantize=True)
    band=np.subtract(high,_upsample(down,width,height,sampling_profile),dtype=np.float32)
    mean=np.zeros(low.shape,np.float32)
    for j in reversed(range(scale)):
        for i in range(scale):mean=np.add(mean,band[j::scale,i::scale],dtype=np.float32)
    mean=np.divide(mean,np.float32(scale*scale),dtype=np.float32)
    repeated_mean=np.repeat(np.repeat(mean,scale,axis=0),scale,axis=1)
    centered=np.subtract(band,repeated_mean,dtype=np.float32)
    gain=np.full(low.shape,amount,np.float32)
    epsilon=np.float32(1e-6)
    for j in reversed(range(scale)):
        for i in range(scale):
            b=base[j::scale,i::scale];d=centered[j::scale,i::scale]
            positive=(np.float32(1)-b)/np.maximum(d,epsilon)
            negative=b/np.maximum(-d,epsilon)
            limit=np.where(d>0,positive,amount)
            limit=np.where(d<0,negative,limit)
            gain=np.minimum(gain,limit)
    repeated_gain=np.repeat(np.repeat(gain,scale,axis=0),scale,axis=1)
    result=np.add(base,repeated_gain*centered,dtype=np.float32)
    return unorm8(result) if quantize else result
