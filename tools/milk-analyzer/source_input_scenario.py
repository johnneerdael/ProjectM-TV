"""Opt-in declared input domains; no runtime observations or mood calibration."""
import math
import numpy as np


def validate_scenario(request):
    from source_appearance import AUDIO,EEL_AUDIO,PACKED,_digest
    if not isinstance(request,dict) or set(request)-{'schema_version','name','audio_band_ranges','shader_canvas_size'}:
        raise ValueError('unsupported input scenario fields')
    if type(request.get('schema_version')) is not int or request['schema_version']!=1:
        raise ValueError('input scenario schema_version1 required')
    name=request.get('name')
    if not isinstance(name,str) or not name.strip() or len(name)>128:raise ValueError('nonempty scenario name up to128characters required')
    ranges=request.get('audio_band_ranges',{})
    if not isinstance(ranges,dict) or set(ranges)-set(AUDIO):raise ValueError('named engine audio-band intervals required')
    domains={};audio={}
    def finite_number(value):
        if type(value) not in {int,float}:return False
        try:return math.isfinite(value)
        except OverflowError:return False
    for band,span in sorted(ranges.items()):
        if not isinstance(span,(list,tuple)) or len(span)!=2 or any(not finite_number(v) for v in span) or span[0]<0 or span[0]>span[1]:
            raise ValueError('finite ordered nonnegative audio interval required')
        audio[band]=[float(v) for v in span]
        if band in EEL_AUDIO:domains[band]=audio[band]
        for bank,codes in PACKED.items():
            for lane,code in enumerate(codes):
                if code==AUDIO[band]:domains[bank+'.'+'xyzw'[lane]]=audio[band]
    size=request.get('shader_canvas_size')
    if size is not None:
        if not isinstance(size,(list,tuple)) or len(size)!=2 or any(type(v) is not int or not 0<v<2**31 for v in size):
            raise ValueError('two positive int32 declared shader-canvas dimensions required')
        width,height=map(np.float32,size)
        values=(width,height,np.float32(1)/width,np.float32(1)/height)
        for lane,value in zip('xyzw',values):domains['_c7.'+lane]=[float(value),float(value)]
        size=list(size)
    result={'schema_version':1,'policy':'declared-source-input-scenario-v1','name':name,
        'audio_band_ranges':audio,'shader_canvas_size':size,'scalar_input_domains':domains,
        'observed_runtime_inputs':False,'runtime_binding_verified':False,
        'bound_scope':'additional ripple deformation, sampled-value offset and nonlinear colour envelopes only; unconstrained descriptions preserved',
        'conditions':['Caller-declared input assumptions, not measured or guaranteed music/genre/audience ranges',
                      'Band intervals constrain actual engine inputs; waveform reachability and cross-band correlation are unverified',
                      'Shader canvas dimensions are explicit authored-canvas uniforms, not inferred from display/output pixels',
                      'Native canvas/selection/allocation/profile must match the declaration before native appearance credit']}
    result['record_sha256']=_digest(result);return result
