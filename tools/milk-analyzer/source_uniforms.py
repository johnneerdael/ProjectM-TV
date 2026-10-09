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


NATIVE_TIME_INPUT=':native-render-time-f32'
NATIVE_OSCILLATORS={
    '_c8':('cos',(.329,1.293,5.070,20.051),(1.2,3.9,2.5,5.4)),
    '_c9':('sin',(.329,1.293,5.070,20.051),(1.2,3.9,2.5,5.4)),
    '_c10':('cos',(.0050,.0085,.0133,.0217),(2.7,5.3,4.5,3.8)),
    '_c11':('sin',(.0050,.0085,.0133,.0217),(2.7,5.3,4.5,3.8))}


def native_time_component_fields():
    from shader_fields import Field
    time=Field('input',dtype='float',detail={'name':NATIVE_TIME_INPUT})
    def constant(value):return Field('constant',dtype='float',detail={'value':float(np.float32(value))})
    result={}
    for name,(function,rates,offsets) in NATIVE_OSCILLATORS.items():
        lanes={}
        for i,(rate,offset) in enumerate(zip(rates,offsets)):
            phase=Field('add',(Field('multiply',(time,constant(rate)),'float'),constant(offset)),'float')
            lanes[i]=Field('add',(constant(.5),Field('multiply',(constant(.5),Field(function,(phase,),'float')),'float')),'float')
        result[name]=lanes
    return result


def native_time_contract():
    return {'policy':'source31-native-time-oscillators-v1','native_clock_input':NATIVE_TIME_INPUT,
        'clock_basis':'float32(renderContext.time), before shader-time10000second wrapping',
        'observed_runtime_binding':False,'uniforms':{
            name:{'function':function,'bias':.5,'amplitude':.5,
                  'rates_rad_per_second':[float(np.float32(v)) for v in rates],
                  'phase_offsets_rad':[float(np.float32(v)) for v in offsets]}
            for name,(function,rates,offsets) in NATIVE_OSCILLATORS.items()},
        'conditions':['Nominal source curves omit CPU float32 rounding, transcendental approximation and frame sampling',
                      'Clock origin/resets/jumps must follow declared render context; no visible flash rate is certified']}
