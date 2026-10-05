"""Custom-wave point outputs to native drawing attributes, without images.

Keep projection, float32 vertex storage, colour modulo, geometry smoothing and
static draw flags. Hardware line/point coverage remains unresolved.
"""
import numpy as np
from scene_equations import _scalar
from primitives import colour_modulo


def source_custom_waves(source,scene):
    width,height=scene['viewport'];values=source['values']
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
            c1,c2,c3,c4=[np.float32(n) for n in [-.15,1.15,1.15,-.15]];normal=np.float32(1)/(c1+c2+c3+c4)
            for i in range(count-1):
                below=max(0,i-1);above=i+1;above2=min(count-1,i+2)
                smoothed[i*2]=vertex[i];smoothed[i*2+1]=(c1*vertex[below]+c2*vertex[i]+c3*vertex[above]+c4*vertex[above2])*normal
                smooth_colours[i*2]=colours[i];smooth_colours[i*2+1]=colours[i]
            smoothed[-1]=vertex[-1];smooth_colours[-1]=colours[-1]
            screen=smoothed*np.float32(.5)+np.float32(.5) # Native orthogonalProjection reverses Y before top-origin conversion.
            dots=bool(_scalar(values,prefix+'bUseDots',0,'bool'));thick=bool(_scalar(values,prefix+'bDrawThick',0,'bool'))
            offsets=[[0,0],[.5/width,0],[.5/width,.5/width],[0,.5/width]] if thick and not dots else [[0,0]]
            projected=smoothed*np.array([1,-1],np.float32)
            waves.append({'index':index,'positions':screen.tolist(),'clip_positions':projected.tolist(),'colours':smooth_colours.tolist(),
                          'draw_mode':'points' if dots else 'strip','point_size':2 if thick else 1,
                          'additive':bool(_scalar(values,prefix+'bAdditive',0,'bool')),'copy_offsets':offsets})
        results.append(waves)
    return {'basis':'native source point equations, projection/colour/smoothing and static draw flags',
            'frames':results,'uses_rendered_reference':False,'appearance_prediction_complete':False,
            'remaining':['hardware line/point coverage and final draw integration']}
