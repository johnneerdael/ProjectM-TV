"""Conditional varying affine-in-main-sample colour envelopes, never frames."""
import math

from shader_fields import Field


def feedback_envelope(analysis):
    from effect_families import _parts,_walk,_constant
    from source_appearance import _canonical_lane,_phase_literal,_data_return,_expression
    from source_control_bounds import scalar_value_envelope
    from field_math import SWIZZLE
    result={'policy':'source-varying-affine-feedback-colour-envelope-v1','source_model':'unknown',
        'maximum_colour_difference_gain':None,'raw_rgb_bounds_if_samples_unit_interval':None,
        'coordinate_feedback_dependency':None,'sufficient_contraction_bound':None,
        'ideal_perturbation_half_life_upper_bound_evaluations':None,
        'sample_contributions':[],'assumed_finite_input_names':[],
        'actual_feedback_persistence':None,'unknown_reasons':[],
        'uses_equation_execution':False,'uses_shader_execution':False,'uses_rendered_images':False,
        'conditions':['Nominal real affine-in-sampled-RGB operator before native rounding, storage and drawing',
                      'Each sampled previous-main RGB component is independently in [0,1]; premise not certified by source',
                      'Identical non-image inputs and fixed sampling coordinates across compared colour states',
                      'Contraction requires image-independent nonexpansive sampling; blur/history, image-driven coordinates and incomplete writes remain separate',
                      'Finite inputs/intermediates/uploads; native precision, clipping, blending, source injection and authored/detail paths excluded',
                      'A failed sufficient bound is not instability; no actual persistence, flashing or mood is inferred']}
    samples={};memo={};active=set();image_memo={};envelope_memo={};assumptions=set();scalar_memo={};derived_domains={}
    def op(name,*args):return Field(name,tuple(args),'float')
    def image(node,depth=0):
        if id(node) in image_memo:return image_memo[id(node)]
        if depth>64 or len(image_memo)>=4096:raise ValueError('feedback sample-dependency budget exceeded')
        if node.op=='sample':answer=True
        elif node.op in {'unknown','uninitialized'} or node.op.startswith('loop_'):
            raise ValueError('feedback expression/dependency unresolved')
        else:answer=any(image(arg,depth+1) for arg in node.args)
        image_memo[id(node)]=answer;return answer
    def visit(node,depth=0):
        node=_canonical_lane(node);key=id(node)
        if key in memo:return memo[key]
        if depth>64 or len(memo)+len(active)>=4096 or key in active:raise ValueError('feedback affine graph budget/cycle exceeded')
        active.add(key)
        try:value=calculate(node,depth)
        finally:active.remove(key)
        memo[key]=value;return value
    def calculate(node,depth):
        if not image(node):return node,{}
        if node.op=='member' and node.dtype=='float' and node.detail.get('swizzle') and len(node.detail['field'])==1:
            parent=node.args[0];lane=SWIZZLE[node.detail['field']]
            if parent.op=='sample' and parent.detail.get('canonical_texture')=='main' and lane<3:
                site=parent.detail.get('site_index')
                if site is None:raise ValueError('main sample site identity missing')
                if site in samples and samples[site] is not parent:raise ValueError('main sample site identity collision')
                samples[site]=parent;return _constant(0),{(site,lane):_constant(1)}
        if node.op in {'cast','narrow'} and node.dtype=='float' and node.args[0].dtype=='float':return visit(node.args[0],depth+1)
        if node.op not in {'add','subtract','multiply','divide'} or node.dtype!='float':
            raise ValueError('colour is not supported affine previous-main RGB')
        a,at=visit(node.args[0],depth+1);b,bt=visit(node.args[1],depth+1)
        if node.op in {'add','subtract'}:
            terms=dict(at)
            for key,c in bt.items():terms[key]=op(node.op,terms.get(key,_constant(0)),c)
            return op(node.op,a,b),terms
        if node.op=='divide':
            if bt:raise ValueError('feedback-dependent divisor')
            span=bound(b)
            if span[0]<=0<=span[1]:raise ValueError('feedback coefficient divisor reaches zero')
            return op('divide',a,b),{key:op('divide',c,b) for key,c in at.items()}
        if at and bt:raise ValueError('nonlinear product of previous-main colour')
        return op('multiply',a,b),{**{key:op('multiply',c,b) for key,c in at.items()},
                                  **{key:op('multiply',c,a) for key,c in bt.items()}}
    def scalar_inputs(node,depth=0):
        if id(node) in scalar_memo:return scalar_memo[id(node)]
        if depth>64 or len(scalar_memo)>=4096:raise ValueError('feedback scalar projection budget exceeded')
        value=node
        if node.op=='narrow' and node.detail.get('numeric_domain')=='shader-float32':
            from source_native_warp import _f32
            child=scalar_inputs(node.args[0],depth+1)
            report=scalar_value_envelope(child,input_domains=derived_domains);span=report['nominal_value_range']
            assumptions.update(set(report['assumed_finite_input_names'])-derived_domains.keys())
            if span is None:raise ValueError('native feedback coefficient upload domain unresolved')
            converted=[_f32(v) for v in span]
            value=Field('input',dtype='float',detail={'name':':feedback-native-narrow-'+str(len(scalar_memo)),
                'source_domain':converted})
            derived_domains[value.detail['name']]=converted
            # Carry the converted range directly; do not treat it as arbitrary input.
            scalar_memo[id(node)]=value;envelope_memo[id(node)]=(node,converted)
            return value
        if node.op=='member' and node.dtype=='float' and node.detail.get('swizzle') and len(node.detail['field'])==1:
            parent=node.args[0];lane=SWIZZLE[node.detail['field']]
            if parent.op=='input' and parent.dtype.startswith('float'):
                value=Field('input',dtype='float',detail={'name':parent.detail['name']+'.'+'xyzw'[lane]})
            elif parent.op not in {'input','sample'}:
                parts=_parts(parent)
                if lane<len(parts):
                    part=parts[lane]
                    if not (part.op=='member' and part.args and part.args[0] is parent):value=scalar_inputs(part,depth+1)
        if value is node:value=Field(node.op,tuple(scalar_inputs(arg,depth+1) for arg in node.args),node.dtype,node.detail)
        scalar_memo[id(node)]=value;return value
    def bound(node):
        key=id(node)
        if key in envelope_memo:return envelope_memo[key][1]
        literal=_phase_literal(node)
        if literal is not None:span=[literal,literal]
        else:
            projected=scalar_inputs(node)
            if key in envelope_memo:return envelope_memo[key][1]
            report=scalar_value_envelope(projected,input_domains=derived_domains);span=report['nominal_value_range']
            assumptions.update(set(report['assumed_finite_input_names'])-derived_domains.keys())
            if span is None:raise ValueError('feedback coefficient/offset lacks a finite source envelope')
        if not all(math.isfinite(v) for v in span):raise ValueError('feedback coefficient/offset envelope is nonfinite')
        envelope_memo[key]=(node,span);return span
    def outward_add(a,b,direction):
        value=a+b
        if not math.isfinite(value):raise ValueError('feedback aggregate envelope is nonfinite')
        return math.nextafter(value,direction) if value else 0.
    try:
        if analysis.stages['warp']['kind']=='fixed_warp':
            decay=analysis.main.get('decay')
            if decay is None:raise ValueError('fixed warp decay missing')
            narrow=Field('narrow',(decay,),'float',{'numeric_domain':'shader-float32'})
            gain=Field('min',(narrow,_constant(1)),'float')
            # A synthetic site identifies the native passthrough, never a texture observation.
            samples[0]=None;lanes=[(_constant(0),{(0,i):gain}) for i in range(3)]
        else:
            field=analysis.outputs.get('warp')
            if field is None:raise ValueError('warp source/selection unresolved')
            lanes=[visit(n) for n in _parts(_data_return(field))[:3]]
            if len(lanes)!=3:raise ValueError('warp RGB lanes unresolved')
        matrices={site:[[[0.,0.] for _ in range(3)] for _ in range(3)] for site in samples}
        lows=[];highs=[];norms=[]
        for row,(offset,terms) in enumerate(lanes):
            lo,hi=bound(offset);norm=0.
            for (site,column),coefficient in terms.items():
                span=bound(coefficient);matrices[site][row][column]=span
                lo=outward_add(lo,min(0.,span[0]),-math.inf);hi=outward_add(hi,max(0.,span[1]),math.inf)
                norm=outward_add(norm,max(map(abs,span)),math.inf)
            lows.append(lo);highs.append(hi);norms.append(norm)
        dependency=False;contributions=[]
        for site,matrix in matrices.items():
            if not any(v!=0 for row in matrix for span in row for v in span):continue
            sample=samples[site]
            if sample is not None:
                nodes=list(_walk(sample.args[0]))
                if any(n.op=='sample' and n.detail.get('canonical_texture') in {'main','blur1','blur2','blur3'} for n,p in nodes):dependency=True
                elif dependency is not True and any(n.op in {'unknown','uninitialized'} or n.op.startswith('loop_') for n,p in nodes):dependency=None
            contributions.append({'sample_site_index':site,'matrix_rgb_coefficient_ranges':matrix,
                'coordinate_expression':None if sample is None else _expression(sample.args[0])})
        gain=max(norms,default=0.)
        result.update(source_model='bounded_affine_main_sample_colour',maximum_colour_difference_gain=gain,
            raw_rgb_bounds_if_samples_unit_interval=list(map(list,zip(lows,highs))),
            coordinate_feedback_dependency=dependency,sample_contributions=contributions,
            assumed_finite_input_names=sorted(assumptions))
        if dependency is False:
            result['sufficient_contraction_bound']=gain<1
            if 0<gain<1:result['ideal_perturbation_half_life_upper_bound_evaluations']=math.log(.5)/math.log(gain)
    except (ValueError,RecursionError,OverflowError,ZeroDivisionError) as error:
        result['unknown_reasons']=[str(error)]
    return result
