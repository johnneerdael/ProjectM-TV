"""Pinned VideoEcho/Filters math with explicit random inputs; no native images."""
import numpy as np
from field_math import UnresolvedMath
from feedback_field import unorm8
from spatial import sample2d,interpolate_mesh
from scene_equations import _scalar
from engine_profiles import CORE_2315_DISPLAY,CORE_2331_DISPLAY,LEGACY_DISPLAY
from native_values import native_scalar


def source_tint_amount(source):
    """PR57's static PresetState fShader; historical engines keep full tint."""
    from engine_profiles import CORE_2325_ENGINE,CORE_2327_ENGINE,CORE_2329_ENGINE,CORE_2331_ENGINE,matches
    from scene_equations import source_settings
    engine=source.get('parser_inputs',{}).get('engine',{})
    if not any(matches(engine,identity) for identity in (CORE_2325_ENGINE,CORE_2327_ENGINE,CORE_2329_ENGINE,CORE_2331_ENGINE)):
        return None
    return _scalar(source_settings(source),'fShader',0,'float')


def _live(main, name, *, finite=True):
    if main is None or name not in main:
        raise UnresolvedMath('live legacy control unresolved: '+name)
    try:return native_scalar(main[name],allow_ieee=not finite)
    except ValueError as error:raise UnresolvedMath('live legacy control unresolved: '+name) from error


def store(values,quantize):
    data=np.asarray(values,dtype=np.float32)
    if not np.all(np.isfinite(data)):raise UnresolvedMath('nonfinite legacy display surface')
    return unorm8(data) if quantize else np.clip(data,0,1)


def gamma_weights(gamma,*,echo,control_policy=LEGACY_DISPLAY):
    if control_policy not in {LEGACY_DISPLAY,CORE_2315_DISPLAY,CORE_2331_DISPLAY}:raise ValueError('unsupported legacy display policy')
    value=np.float32(gamma)
    if not np.isfinite(value):raise UnresolvedMath('legacy gamma is nonfinite')
    # Release0019 follows MilkDrop's distinct gamma-only count epsilon.
    epsilon=.001 if control_policy==CORE_2331_DISPLAY and not echo else .0001
    count_value=np.float32(value-np.float32(epsilon))
    if not -(2**31)<=float(count_value)<2**31:raise UnresolvedMath('legacy gamma integer domain')
    count=int(count_value)
    if not echo:count+=1
    if count>4096:raise UnresolvedMath('legacy redraw computation budget exceeded')
    if echo:
        return [1]+([1]*(count-1)+[float(np.float32(value-np.float32(count)))] if value>.001 and count>0 else [])
    if count<=0:raise UnresolvedMath('legacy gamma leaves invalidated target unwritten')
    return [1]*(count-1)+[float(np.float32(value-np.float32(count-1)))]


def corner_shades(time,hue_offsets,*,shader_amount=None):
    if time is None or not np.isfinite(time):raise UnresolvedMath('explicit legacy render time required')
    offsets=np.asarray(hue_offsets,dtype=np.float32)
    if offsets.shape!=(4,) or not np.all(np.isfinite(offsets)):
        raise UnresolvedMath('explicit four native hue offsets required')
    index=np.arange(4,dtype=np.float32)
    result=[]
    for rate,phase,mult,offset in [(.0143,3,21,3),(.0107,1,13,1),(.0129,6,9,2)]:
        # Pinned RenderContext.time is float; preserve each native float operation.
        angle=np.float32(time)*np.float32(30)*np.float32(rate)
        angle=angle+np.float32(phase)+index*np.float32(mult)+offsets[offset]
        result.append(np.float32(.6)+np.float32(.3)*np.sin(angle))
    shade=np.stack(result,axis=-1)
    result=np.float32(.5)+np.float32(.5)*(shade/np.max(shade,axis=1,keepdims=True))
    if shader_amount is not None:
        amount=np.float32(shader_amount)
        if not np.isfinite(amount):raise UnresolvedMath('legacy tint amount is nonfinite')
        result=(result*amount+np.float32(1)*(np.float32(1)-amount)
                if amount>np.float32(.001) else np.ones_like(result))
    return result


def apply_filters(field,values,*,quantize,main=None,control_policy=LEGACY_DISPLAY):
    if control_policy not in {LEGACY_DISPLAY,CORE_2315_DISPLAY,CORE_2331_DISPLAY}:raise ValueError('unsupported legacy display policy')
    def enabled(name,key):
        return _live(main,name,finite=False)!=0 if control_policy!=LEGACY_DISPLAY else bool(_scalar(values,key,0,'bool'))
    result=np.asarray(field,dtype=np.float32)
    if enabled('brighten','bBrighten'):
        result=store(1-result,quantize);result=store(result*result,quantize);result=store(1-result,quantize)
    if enabled('darken','bDarken'):result=store(result*result,quantize)
    if enabled('solarize','bSolarize'):
        result=store(result*(1-result),quantize);result=store(result+result,quantize)
    if enabled('invert','bInvert'):result=store(1-result,quantize)
    return result


def legacy_display(feedback,*,values,time,hue_offsets,quantize=True,main=None,control_policy=LEGACY_DISPLAY,sampling_profile='portable',shader_amount=None):
    from unorm_sampler import sampler_2d
    sample=sampler_2d(sampling_profile)
    if sampling_profile!='portable' and not quantize:
        raise ValueError('texture profile requires actual unorm feedback storage')
    if control_policy not in {LEGACY_DISPLAY,CORE_2315_DISPLAY,CORE_2331_DISPLAY}:raise ValueError('unsupported legacy display policy')
    live=control_policy!=LEGACY_DISPLAY
    source=np.asarray(feedback,dtype=np.float32)
    if source.ndim!=3 or source.shape[-1]!=4 or min(source.shape[:2])<=0 or not np.all(np.isfinite(source)):
        raise UnresolvedMath('finite RGBA legacy feedback required')
    height,width=source.shape[:2]
    shade=corner_shades(time,hue_offsets,shader_amount=shader_amount)
    gamma=np.float32(_live(main,'gamma')) if live else _scalar(values,'fGammaAdj',2,'float')
    alpha=np.float32(_live(main,'echo_alpha',finite=False)) if live else _scalar(values,'fVideoEchoAlpha',0,'float')
    echo=alpha>np.float32(.001)
    orientation=0
    if live and echo:
        raw=_live(main,'echo_orient',finite=False)
        truncated=np.trunc(raw)
        if not np.isfinite(truncated) or not -(2**31)<=truncated<=2**31-1:
            echo=False
        else:orientation=int(truncated)
    weights=gamma_weights(gamma,echo=echo,control_policy=control_policy)
    inverse_aspect_y=np.float32(1)/np.float32(min(1,height/width))
    aspect=np.float32(width)/np.float32(np.float32(height)*inverse_aspect_y)
    ax=np.float32(1) if aspect>1 else np.float32(1)/aspect
    ay=aspect if aspect>1 else np.float32(1)
    extent=np.array([(np.float32(1)+np.float32(1)/np.float32(width))*ax,
                     (np.float32(1)+np.float32(1)/np.float32(height))*ay],dtype=np.float32)
    x,y=np.meshgrid((np.arange(width,dtype=np.float32)+.5)/width,
                    (np.arange(height,dtype=np.float32)+.5)/height)
    local_uv=(np.stack((x,y),axis=-1)-.5)/extent+.5
    colours=interpolate_mesh(shade.reshape(2,2,3),local_uv)
    zoom=(np.float32(_live(main,'echo_zoom')) if live else _scalar(values,'fVideoEchoZoom',2,'float')) if echo else 1
    if zoom==0:raise UnresolvedMath('legacy echo zoom division by zero')
    if not live:orientation=_scalar(values,'nVideoEchoOrientation',0,'int')
    orientation-=int(orientation/4)*4  # C++ remainder retains the dividend's sign.
    passes=[(1,1)] if not echo else [(1,np.float32(1)-np.float32(alpha)),(zoom,np.float32(alpha))]
    output=None
    for pass_index,(zoom,mix) in enumerate(passes):
        low=np.float32(.5)-np.float32(.5)/np.float32(zoom)
        high=np.float32(.5)+np.float32(.5)/np.float32(zoom)
        uv=low+local_uv*(high-low)
        if pass_index==1:
            flip_u=orientation%2!=0 if control_policy==CORE_2331_DISPLAY else orientation%2==1 and orientation>0
            if flip_u:uv[...,0]=1-uv[...,0]
            if orientation>=2:uv[...,1]=1-uv[...,1]
        sampled=sample(source,uv,wrap=False,linear=True,origin='top')
        for weight in weights:
            colour=np.concatenate((colours*np.float32(mix)*np.float32(weight),
                                   np.ones((height,width,1),dtype=np.float32)),axis=-1)
            fragment=store(sampled*colour,False)
            output=store(fragment if output is None else output+fragment,quantize)
    return apply_filters(output,values,quantize=quantize,main=main,control_policy=control_policy)
