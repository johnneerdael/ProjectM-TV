"""Conditional shader colour ranges through supported nonlinear scalar math."""
from shader_fields import Field


def nonlinear_texture_colour_bounds(analysis,warp_vertex):
    from source_advection import substitute_sample_values
    from source_control_bounds import scalar_value_envelope
    from source_appearance import _data_return,_canonical_lane
    from effect_families import _parts
    from field_math import SWIZZLE
    from source_native_warp import _f32
    stages={}
    for stage in ('warp','composite'):
        r={'source_model':'unknown','channel_value_envelopes':None,
            'raw_rgb_bounds_if_samples_unit_interval':None,'sample_textures':[],
            'colour_difference_gain':None,'whole_feedback_contraction':None,
            'actual_feedback_persistence':None,'visible_flashing':None,'unknown_reasons':[]}
        field=analysis.outputs.get(stage)
        if field is None:
            r['unknown_reasons']=['no authored stage field'];stages[stage]=r;continue
        try:
            replaced,samples=substitute_sample_values(_data_return(field),known_vertex=warp_vertex if stage=='warp' else None)
            domains={};memo={};active=set();assumptions=set()
            for name,sample in samples:
                for lane in 'xyzw':domains[name+'.'+lane]=[0.,1.]
            def project(node,depth=0):
                original=node;key=id(original)
                if key in memo:return memo[key][1]
                node=_canonical_lane(original)
                if depth>64 or len(memo)+len(active)>=4096 or key in active:
                    raise ValueError('nonlinear colour projection budget/cycle exceeded')
                active.add(key)
                try:value=calculate(node,depth)
                finally:active.remove(key)
                memo[key]=(original,value);return value
            def calculate(node,depth):
                if node.op=='dot' and len(node.args)==2:
                    a,b=map(_parts,node.args)
                    if len(a)!=len(b) or not 1<=len(a)<=4:raise ValueError('colour dot dimensions unresolved')
                    value=Field('constant',detail={'value':0.})
                    for x,y in zip(a,b):
                        value=Field('add',(value,Field('multiply',(project(x,depth+1),project(y,depth+1)),'float')),'float')
                    return value
                if node.op=='narrow' and node.detail.get('numeric_domain')=='shader-float32':
                    child=project(node.args[0],depth+1);report=scalar_value_envelope(child,input_domains=domains)
                    span=report['nominal_value_range']
                    assumptions.update(set(report['assumed_finite_input_names'])-domains.keys())
                    if span is None:raise ValueError('native colour-input upload domain unresolved')
                    name=':nonlinear-colour-narrow-'+str(len(memo));domains[name]=[_f32(v) for v in span]
                    return Field('input',dtype='float',detail={'name':name})
                if node.op=='member' and node.detail.get('swizzle') and len(node.detail.get('field',''))==1:
                    parent=node.args[0];lane=SWIZZLE[node.detail['field']]
                    if parent.op=='input' and parent.dtype.startswith('float'):
                        return Field('input',dtype='float',detail={'name':parent.detail['name']+'.'+'xyzw'[lane]})
                    if parent.op=='domain_checked':
                        child=_parts(parent.args[0])[lane]
                        return Field('domain_checked',(project(child,depth+1),),'float',parent.detail)
                    if parent.op not in {'input','sample'}:
                        parts=_parts(parent)
                        if lane<len(parts):
                            p=parts[lane]
                            if not (p.op=='member' and p.args and p.args[0] is parent):return project(p,depth+1)
                return Field(node.op,tuple(project(arg,depth+1) for arg in node.args),node.dtype,node.detail)
            channels=[]
            for lane in _parts(replaced)[:3]:
                try:
                    channel=scalar_value_envelope(project(lane),input_domains=domains)
                except (ValueError,RecursionError,OverflowError,IndexError) as error:
                    channel=scalar_value_envelope(Field('unresolved',dtype='float'))
                    channel['unknown_reasons']=[str(error)]
                channels.append(channel)
            if len(channels)!=3:raise ValueError('nonlinear RGB scalar lanes unresolved')
            spans=[c['nominal_value_range'] for c in channels]
            r['channel_value_envelopes']=channels
            r['sample_textures']=sorted({s.detail.get('canonical_texture') for name,s in samples},key=str)
            if all(span is not None for span in spans):
                r['source_model']='bounded_declared_texture_inputs';r['raw_rgb_bounds_if_samples_unit_interval']=spans
            elif any(span is not None for span in spans):r['source_model']='partial_declared_texture_inputs'
            r['unknown_reasons']=[reason for c in channels for reason in c['unknown_reasons']]
            r['assumed_finite_nontexture_input_names']=sorted(assumptions|set().union(*(
                set(c['assumed_finite_input_names'])-domains.keys() for c in channels)))
        except (ValueError,RecursionError,OverflowError,IndexError) as error:r['unknown_reasons']=[str(error)]
        stages[stage]=r
    return {'policy':'source-nonlinear-declared-texture-colour-ranges-v1','stages':stages,
        'uses_shader_execution':False,'uses_equation_execution':False,'uses_rendered_images':False,
        'conditions':['Direct sampled RGBA components independently lie in [0,1]; this input premise is not certified by source',
                      'Nominal scalar arithmetic ranges, explicit packed-input and native-upload domains; no time/pixel samples',
                      'Known nonfinite uploads, singular or unsupported operation domains remain unknown',
                      'Patched shader abs/domain lowering is retained; no blanket negative-power-base reinterpretation',
                      'Correlation, native precision/storage, sampling positions/history, drawing/detail and final display remain separate',
                      'Range bounds do not establish sensitivity, continuity, visible flashing, palette or mood']}
