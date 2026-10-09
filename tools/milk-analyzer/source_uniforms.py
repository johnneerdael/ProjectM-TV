"""Source-proven native uniform inputs, never observed GPU/context bindings."""
import numpy as np


def blur_decode_bindings(main):
    from source_appearance import _phase_literal
    from blur import native_ranges,CORE_2315_BLUR
    result={'policy':'source31-constant-blur-decode-v1','status':'unresolved',
            'packed_components':None,'raw_ranges':None,'safe_ranges':None,
            'observed_runtime_binding':False,'unknown_reasons':[],
            'conditions':['Exact target safe-range normalization and float32 packing; not original MilkDrop2 close-range bug',
                          'All six main-frame blur values must be supported constants before triplet binding',
                          'Bound decode constants do not certify kernel history, texture contents, appearance or mood']}
    fields=[main.get('blur'+str(i)+'_'+side) for side in ('min','max') for i in range(1,4)]
    values=[None if field is None else _phase_literal(field) for field in fields]
    if any(v is None for v in values):
        result['unknown_reasons']=['main-frame blur triplet contains unsupported or dynamic values'];return result
    low,high=native_ranges(values[:3],values[3:],policy=CORE_2315_BLUR)
    with np.errstate(all='ignore'):gaps=np.asarray(high-low,dtype=np.float32)
    packed={'_c5':[float(gaps[0]),float(low[0]),float(gaps[1]),float(low[1])],
            '_c6':[float(gaps[2]),float(low[2]),float(low[0]),float(high[0])]}
    result.update(status='source_constant',packed_components=packed,
                  raw_ranges={'minimum':values[:3],'maximum':values[3:]},
                  safe_ranges={'minimum':low.tolist(),'maximum':high.tolist()})
    return result
