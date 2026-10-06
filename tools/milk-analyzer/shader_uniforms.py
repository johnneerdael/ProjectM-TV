"""Deterministic shader inputs from native render state and saved frame Q.

The pinned PCM implementation derives vol/vol_att with .333f, not division by
three. This function returns common inputs. Random vectors/matrices come from
shader_random's explicit per-stage lifecycle; diffuse colours are supplied by
the draw/composite model rather than invented here.
"""
import numpy as np


def source_uniforms(scene:dict,frame_index:int,*,names=None)->dict:
    frame=scene['frames'][frame_index];render=frame['render_inputs'];main=frame['main']
    time=np.float32(render['time'])
    quotient=int(float(time)/10000.0)
    if not -(2**31)<=quotient*10000<2**31:raise ValueError('native wrapped-time integer domain unresolved')
    wrapped=np.float32(time-np.float32(quotient*10000))
    volume=(np.float32(render['bass'])+np.float32(render['mid'])+np.float32(render['treb']))*np.float32(.333)
    volume_att=(np.float32(render['bass_att'])+np.float32(render['mid_att'])+np.float32(render['treb_att']))*np.float32(.333)
    result={'_c2':[float(wrapped),render['fps'],render['frame'],render['progress']],
            '_c3':[render['bass'],render['mid'],render['treb'],float(volume)],
            '_c4':[render['bass_att'],render['mid_att'],render['treb_att'],float(volume_att)]}
    for index,letter in enumerate('abcdefgh'):
        if names is not None and '_q'+letter not in names:continue
        try:bank=np.asarray([main[f'q{index*4+i+1}'] for i in range(4)],dtype=np.float32)
        except (ValueError,TypeError) as error:raise ValueError('unresolved shader Q input') from error
        if not np.all(np.isfinite(bank)):raise ValueError('nonfinite shader Q input')
        result['_q'+letter]=bank.tolist()
    for first,frequencies,phases in [(8,[.329,1.293,5.070,20.051],[1.2,3.9,2.5,5.4]),
                                    (10,[.0050,.0085,.0133,.0217],[2.7,5.3,4.5,3.8])]:
        angle=time*np.asarray(frequencies,dtype=np.float32)+np.asarray(phases,dtype=np.float32)
        result[f'_c{first}']=(np.float32(.5)+np.float32(.5)*np.cos(angle)).tolist()
        result[f'_c{first+1}']=(np.float32(.5)+np.float32(.5)*np.sin(angle)).tolist()
    width,height=scene['viewport']
    mip=np.log(np.asarray([width,height],dtype=np.float32))/np.log(np.float32(2))
    result['_c12']=[float(mip[0]),float(mip[1]),float(np.float32(.5)*(mip[0]+mip[1])),0]
    return result if names is None else {name:value for name,value in result.items() if name in names}
