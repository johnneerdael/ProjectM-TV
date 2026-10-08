"""Custom-wave point outputs to native drawing attributes, without images.

Keep projection, float32 vertex storage, colour modulo, geometry smoothing and
static draw flags. Hardware line/point coverage remains unresolved.
"""
import numpy as np
import ctypes
from functools import lru_cache
from scene_equations import source_settings,_scalar
from primitives import colour_modulo

DEFAULT_SMOOTHING='separate-float32-v1'
FMA_SMOOTHING='float32-fma-first-v1'


@lru_cache(maxsize=1)
def _fmaf():
    try:
        function=ctypes.CDLL(None).fmaf
    except AttributeError as error:
        raise ValueError('float32 fused smoothing is unavailable on this producer') from error
    function.argtypes=[ctypes.c_float]*3
    function.restype=ctypes.c_float
    return function


def smooth_position(points,*,profile=DEFAULT_SMOOTHING):
    """Interpolate four native float32 positions under declared contraction rules."""
    if profile not in (DEFAULT_SMOOTHING,FMA_SMOOTHING):
        raise ValueError('unknown custom-wave smoothing profile')
    vertex=np.asarray(points,dtype=np.float32)
    if vertex.shape!=(4,2) or not np.all(np.isfinite(vertex)):
        raise ValueError('four finite custom-wave positions required')
    c1,c2,c3,c4=[np.float32(n) for n in [-.15,1.15,1.15,-.15]]
    normal=np.float32(1)/(c1+c2+c3+c4)
    if profile==DEFAULT_SMOOTHING:
        result=(c1*vertex[0]+c2*vertex[1]+c3*vertex[2]+c4*vertex[3])*normal
    else:
        fused=_fmaf()
        result=np.asarray([fused(c4,vertex[3,k],fused(c3,vertex[2,k],
                          fused(c1,vertex[0,k],np.float32(c2*vertex[1,k]))))*normal
                          for k in range(2)],dtype=np.float32)
    if not np.all(np.isfinite(result)):
        raise ValueError('nonfinite custom-wave smoothing output')
    return result


def source_custom_waves(source,scene,*,smoothing_profile=DEFAULT_SMOOTHING):
    if smoothing_profile not in (DEFAULT_SMOOTHING,FMA_SMOOTHING):
        raise ValueError('unknown custom-wave smoothing profile')
    width,height=scene['viewport'];values=source_settings(source)
    ax=np.float32(min(1,width/height));ay=np.float32(min(1,height/width))
    inverse=np.array([np.float32(1)/ax,np.float32(1)/ay],dtype=np.float64)
    results=[]
    for frame in scene['frames']:
        waves=[]
        for wave in frame['waves']:
            points=wave['points'];index=wave['index'];prefix=f'wavecode_{index}_'
            if not points:continue
            try:
                xy=np.asarray([[p['x'],p['y']] for p in points],dtype=np.float64)
                colours=colour_modulo([[p[c] for c in 'rgba'] for p in points])
            except (ValueError,TypeError) as error:raise ValueError('unresolved custom wave point output') from error
            vertex=((xy*np.array([2,-2])+np.array([-1,1]))*inverse).astype(np.float32)
            if not np.all(np.isfinite(vertex)):raise ValueError('nonfinite custom wave geometry')
            count=len(points);smoothed=np.empty((count*2-1,2),dtype=np.float32);smooth_colours=np.empty((count*2-1,4),dtype=np.float32)
            for i in range(count-1):
                below=max(0,i-1);above=i+1;above2=min(count-1,i+2)
                smoothed[i*2]=vertex[i];smoothed[i*2+1]=smooth_position(
                    [vertex[below],vertex[i],vertex[above],vertex[above2]],profile=smoothing_profile)
                smooth_colours[i*2]=colours[i];smooth_colours[i*2+1]=colours[i]
            smoothed[-1]=vertex[-1];smooth_colours[-1]=colours[-1]
            screen=smoothed*np.float32(.5)+np.float32(.5) # Native orthogonalProjection reverses Y before top-origin conversion.
            dots=bool(_scalar(values,prefix+'bUseDots',0,'bool'));thick=bool(_scalar(values,prefix+'bDrawThick',0,'bool'))
            offsets=[[0,0],[.5/width,0],[.5/width,.5/width],[0,.5/width]] if thick and not dots else [[0,0]]
            projected=smoothed*np.array([1,-1],np.float32)
            waves.append({'index':index,'positions':screen.tolist(),'clip_positions':projected.tolist(),'colours':smooth_colours.tolist(),
                          'draw_mode':'points' if dots else 'strip','point_size':2 if thick else 1,'thick':bool(thick),
                          'additive':bool(_scalar(values,prefix+'bAdditive',0,'bool')),'copy_offsets':offsets})
        results.append(waves)
    return {'basis':'native source point equations, projection/colour/smoothing and static draw flags',
            'smoothing_profile':smoothing_profile,
            'frames':results,'uses_rendered_reference':False,'appearance_prediction_complete':False,
            'remaining':['hardware line/point coverage and final draw integration']}
