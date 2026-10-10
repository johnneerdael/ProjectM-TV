"""Nominal two-state sampled-colour moduli, including powers singular at zero.

Delta is a maximum input-lane difference, not a time trajectory. Original
numeric/domain/coordinate guards remain separate from the real-valued modulus.
"""
from fractions import Fraction
import math

POLICY='source-sampled-colour-difference-modulus-v1'
HISTORY={'main','blur1','blur2','blur3'}


def _up(value):
    if not math.isfinite(value) or value<0:raise ValueError('nonfinite modulus coefficient/domain')
    return math.nextafter(value,math.inf) if value else 0.


def _product(a,b):
    from source_sampling_motion import _finite_round
    value=_finite_round(Fraction(a)*Fraction(b),upper=True)
    if value is None:raise ValueError('modulus coefficient product overflow/underflow')
    return value


def _sum(a,b):
    from source_sampling_motion import _finite_round
    value=_finite_round(Fraction(a)+Fraction(b),upper=True)
    if value is None:raise ValueError('modulus coefficient sum overflow/underflow')
    return value


def _terms(items):return [{'coefficient':c,'exponent':p} for p,c in sorted(items.items()) if c]


def _scale(items,factor):return {p:_product(c,factor) for p,c in items.items() if c and factor}


def _add(*items):
    result={}
    for terms in items:
        for p,c in terms.items():result[p]=_sum(result.get(p,0.),c)
    return result


def scalar_difference_modulus(field, *, input_domains, varying_inputs, native_scalar_limit=None):
    """Bound a scalar difference by sum a*delta**p with 0<p<=1.

    Every named varying input changes independently by at most delta. Unlike a
    derivative along a common diagonal, subtraction cannot cancel independent
    input changes. Other inputs hold fixed, with finite domains when needed.
    """
    from source_control_bounds import scalar_value_envelope
    from source_appearance import _phase_literal, _canonical_lane
    from source_forms import known_invalid_phase_offset
    from source_native_warp import _f32
    from effect_families import _parts,_deps
    from field_math import SWIZZLE
    varying=set(varying_inputs);domains=dict(input_domains or {})
    report={'policy':POLICY,'status':'unknown','terms':[],'nominal_value_range':None,
        'lipschitz_gain_upper':None,'varying_input_names':sorted(varying),
        'held_fixed_input_names':[],'unknown_reasons':[],'power_sites':[],
        'native_numeric_certified':False,'uses_rendered_images':False,'uses_equation_execution':False,
        'conditions':['Nominal real-valued two-state response; all original inputs/intermediates remain finite',
            'Each varying scalar lane changes independently by at most delta; other inputs, phase/storage and coordinates remain fixed',
            'Positive powers below1 use Holder continuity, not a finite derivative at0; domain guards precede cancellation',
            'Native rounding/quantization, sampled-coordinate response and actual image/time trajectories are not certified']}
    memo={};active=set();inputs=set();value_reports=[]
    def span(node):
        result=scalar_value_envelope(node,input_domains=domains)
        value_reports.append(result)
        value=result['nominal_value_range']
        if any(any(word in reason for word in ('overflow','underflow','nonfinite','outside finite')) for reason in result['unknown_reasons']):
            raise ValueError('original numeric-domain failure retained: '+ '; '.join(result['unknown_reasons']))
        if value is None:return None
        if not all(math.isfinite(v) for v in value):raise ValueError('nonfinite original value domain')
        return value
    def magnitude(model):
        if model['span'] is None:raise ValueError('bounded held-mask/coefficient value domain unresolved')
        return max(map(abs,model['span']))
    def model(node,terms,nonnegative=False,range_override=None):
        interval=span(node) if range_override is None else range_override
        if nonnegative and interval is not None:interval=[max(0.,interval[0]),interval[1]]
        limit=native_scalar_limit
        if limit is not None and interval is not None and max(map(abs,interval))>limit:
            raise ValueError('finite native shader arithmetic domain is not established')
        return {'terms':terms,'span':interval,'nonnegative':nonnegative or interval is not None and interval[0]>=0}
    def visit(node,depth=0):
        original=node;key=id(original)
        if key in memo and memo[key][0] is original:return memo[key][1]
        if depth>64 or len(memo)+len(active)>=512 or key in active:raise ValueError('colour modulus graph budget/cycle exceeded')
        active.add(key)
        node=_canonical_lane(node)
        try:result=calculate(node,depth)
        finally:active.remove(key)
        memo[key]=(original,result);return result
    def calculate(node,depth):
        if node.op=='member' and node.dtype=='float' and node.detail.get('swizzle') and len(node.detail.get('field',''))==1:
            parent=node.args[0];index=SWIZZLE[node.detail['field']]
            if parent.op=='input' and parent.dtype in {'float2','float3','float4'} and index<int(parent.dtype[-1]):
                name=parent.detail.get('name')
                if set(parent.detail)!={'name'}:raise ValueError('qualified scalar uniform binding unresolved')
                from shader_fields import Field
                return visit(Field('input',dtype='float',detail={'name':name+'.'+'xyzw'[index]}),depth+1)
            if parent.op=='unary' and len(parent.args)==1:
                from shader_fields import Field
                parts=_parts(parent.args[0])
                if index>=len(parts):raise ValueError('unary vector lane unresolved')
                return visit(Field('unary',(parts[index],),'float',parent.detail),depth+1)
            if parent.op=='domain_checked':
                from shader_fields import Field
                parts=_parts(parent.args[0])
                if index>=len(parts):raise ValueError('domain-checked vector lane unresolved')
                return visit(Field('domain_checked',(parts[index],),'float',parent.detail),depth+1)
            if parent.op not in {'input','sample'}:
                parts=_parts(parent)
                if index<len(parts) and not (parts[index].op=='member' and parts[index].args and parts[index].args[0] is parent):
                    return visit(parts[index],depth+1)
        if node.dtype!='float':raise ValueError('non-scalar/discrete original colour operation: '+node.op)
        if node.op=='input':
            name=node.detail.get('name');inputs.add(name)
            if set(node.detail)!={'name'}:raise ValueError('qualified input phase/storage binding unresolved')
            if name in varying and name not in domains:raise ValueError('varying input lacks a declared finite domain')
            return model(node,{1.:1.} if name in varying else {})
        if node.op=='constant':
            value=_phase_literal(node)
            if value is None or not math.isfinite(value):raise ValueError('nonfinite original colour literal')
            native=node.detail.get('native_value',value)
            if native is None or not math.isfinite(native):raise ValueError('nonfinite native colour literal')
            return model(node,{},value>=0,[value,value])
        if node.op=='narrow':
            child=visit(node.args[0],depth+1)
            if child['terms']:raise ValueError('sample-dependent native upload/quantization needs a finite-difference adapter')
            if child['span'] is None:raise ValueError('held native upload value domain unresolved')
            return model(node,{},range_override=[_f32(v) for v in child['span']])
        if node.op=='cast':
            literal=_phase_literal(node)
            if node.args[0].op=='constant' and node.args[0].dtype=='int' and node.detail.get('target_type')=='float':
                if literal is None or not math.isfinite(literal):raise ValueError('invalid constant integer conversion')
                literal=_f32(literal)
                return model(node,{},literal>=0,[literal,literal])
            child=visit(node.args[0],depth+1)
            if literal is not None and math.isfinite(literal) and not child['terms']:
                return model(node,{},literal>=0,[literal,literal])
            if node.detail.get('target_type')!='float' or node.args[0].dtype!='float':
                raise ValueError('dynamic/discrete numeric cast requires an adapter')
            return child
        if node.op=='domain_checked':
            if node.detail.get('function') not in {'pow','sqrt'}:raise ValueError('unsupported original nonlinear domain: '+str(node.detail.get('function')))
            return visit(node.args[0],depth+1)
        if node.op in {'length','distance'}:
            groups=[_parts(arg) for arg in node.args]
            if not groups or any(not 1<=len(g)<=4 for g in groups) or len({len(g) for g in groups})!=1:
                raise ValueError('vector norm dimensions unresolved')
            values=[[visit(x,depth+1) for x in group] for group in groups]
            terms=_add(*(v['terms'] for group in values for v in group))
            return model(node,terms,True)
        if node.op in {'pow','sqrt','sqr'}:
            base=visit(node.args[0],depth+1)
            p=.5 if node.op=='sqrt' else 2. if node.op=='sqr' else _phase_literal(node.args[1])
            if node.op=='pow' and node.args[1].op=='constant' and node.args[1].dtype=='float':
                p=node.args[1].detail.get('native_value',p)
            if p is None or not math.isfinite(p) or p<=0:raise ValueError('positive literal authored power exponent required')
            if node.op!='sqr' and p!=1 and not base['nonnegative']:
                raise ValueError('original power base nonnegative domain unresolved')
            if p<1:
                terms={}
                for q,c in base['terms'].items():
                    exact=Fraction(q)*Fraction(p);exponent=float(exact)
                    if Fraction(exponent)>exact:exponent=math.nextafter(exponent,0.)
                    if exponent<=0:raise ValueError('Holder exponent underflow')
                    terms[exponent]=_sum(terms.get(exponent,0.),_up(math.pow(c,p)))
                kind='Holder continuity at zero'
            else:
                gain=1. if p==1 else _up(p*math.pow(magnitude(base),p-1))
                terms=_scale(base['terms'],gain);kind='bounded positive-power derivative'
            report['power_sites'].append({'exponent':p,'method':kind,'base_value_range':base['span'],
                'source_abs_lowering_required':node.op!='sqr' and p!=1})
            return model(node,terms,node.op=='sqr' or p!=1 and base['nonnegative'])
        if node.op in {'abs','negate','sin','cos'} or node.op=='unary':
            child=visit(node.args[0],depth+1)
            if node.op=='unary' and node.detail.get('operator') not in {0,1}:raise ValueError('unsupported unary operation')
            return model(node,child['terms'],node.op=='abs')
        if node.op in {'saturate','clamp'}:
            child=visit(node.args[0],depth+1)
            low,high=(0.,1.) if node.op=='saturate' else tuple(_phase_literal(v) for v in node.args[1:])
            if low is None or high is None or not all(math.isfinite(v) for v in (low,high)) or low>high:
                raise ValueError('constant clamp domain unresolved')
            return model(node,child['terms'],low>=0)
        if node.op=='select':
            dependencies=_deps(node.args[0])
            if any(name in varying or any(lane.startswith(name+'.') for lane in varying) for name in dependencies):
                raise ValueError('sample-dependent predicate seam lacks a continuous modulus')
            condition=scalar_value_envelope(node.args[0],input_domains=domains)
            if condition['nominal_value_range'] is None:raise ValueError('held predicate original value domain unresolved')
            a,b=[visit(x,depth+1) for x in node.args[1:]]
            return model(node,_add(a['terms'],b['terms']))
        if node.op=='lerp':
            a,b,t=[visit(x,depth+1) for x in node.args]
            mt=magnitude(t);mi=max(abs(1-t['span'][0]),abs(1-t['span'][1]))
            difference=None if a['span'] is None or b['span'] is None else max(abs(b['span'][1]-a['span'][0]),abs(a['span'][1]-b['span'][0]))
            if t['terms'] and difference is None:raise ValueError('varying colour-mix mask contrast domain unresolved')
            terms=_add(_scale(a['terms'],mi),_scale(b['terms'],mt),_scale(t['terms'],difference or 0.))
            return model(node,terms)
        if node.op in {'add','subtract','multiply','divide','eel_divide','min','max'}:
            a,b=[visit(x,depth+1) for x in node.args]
            if node.op in {'add','subtract','min','max'}:terms=_add(a['terms'],b['terms'])
            elif node.op=='multiply':
                terms=_add(_scale(a['terms'],magnitude(b)) if a['terms'] else {},
                           _scale(b['terms'],magnitude(a)) if b['terms'] else {})
            else:
                if b['span'] is None or b['span'][0]<=0<=b['span'][1]:raise ValueError('original divisor domain reaches zero or is unresolved')
                minimum=min(map(abs,b['span']))
                if node.op=='eel_divide' and minimum<.00001:raise ValueError('EEL epsilon-divide seam remains unresolved')
                terms=_add(_scale(a['terms'],_up(1/minimum)),
                           _scale(b['terms'],_up(magnitude(a)/(minimum*minimum))) if b['terms'] else {})
            return model(node,terms)
        raise ValueError('unsupported original colour operation: '+node.op)
    try:
        if known_invalid_phase_offset(field,preserve_zero_products=True):raise ValueError('known invalid original colour domain')
        answer=visit(field)
        report.update(status='bounded',terms=_terms(answer['terms']),nominal_value_range=answer['span'])
        if all(p==1 for p in answer['terms']):report['lipschitz_gain_upper']=sum(answer['terms'].values())
    except (ValueError,RecursionError,OverflowError,ZeroDivisionError,IndexError) as error:report['unknown_reasons']=[str(error)]
    report['held_fixed_input_names']=sorted(inputs-varying)
    report['declared_input_domains']={name:list(domains[name]) for name in sorted(inputs) if name in domains}
    # Keep domain reports for contributing operations, including supplemental
    # proof evidence; they are not discarded by a successful Holder calculation.
    report['original_value_domain_reports']=value_reports
    return report


def evaluate_colour_modulus(report, delta, *, concave_envelope=False):
    """Evaluate a source difference ceiling; never infer a time rate."""
    if type(delta) not in {int,float} or not math.isfinite(delta) or not 0<=delta<=1:
        raise ValueError('declared sampled-lane difference in[0,1] required')
    if report.get('status')!='bounded':return None
    groups=(report['channels'] if 'channels' in report and not concave_envelope else
            [{'terms':report.get('concave_envelope_terms',report.get('terms',[]))}])
    try:
        values=[]
        for group in groups:
            total=0.
            for term in group['terms']:
                value=0. if delta==0 else _up(term['coefficient']*math.pow(delta,term['exponent']))
                total=_sum(total,value)
            values.append(total)
        return max(values,default=0.)
    except (ValueError,OverflowError):return None


def _f32_max():
    return float.fromhex('0x1.fffffep127')


def sampled_colour_difference_modulus(analysis, *, stage='composite', input_domains=None):
    """Stage RGB modulus on independent unit sampled values at fixed locations."""
    from source_advection import substitute_sample_values
    from source_activity import blackout_colour_channels
    from source_appearance import _data_return,_digest
    from source_forms import known_invalid_phase_offset
    from effect_families import _walk
    result={'policy':POLICY,'status':'unknown','stage':stage,'channels':[],'unknown_reasons':[],
        'input_change_metric':'maximum_declared_sample_RGBA_lane_change','input_delta_domain':[0.,1.],
        'sampling_coordinate_response_included':False,'sample_history_trajectory_known':False,
        'native_numeric_certified':False,'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False,
        'source_sha256':getattr(analysis,'source',{}).get('preset_sha256'),
        'conditions':['All declared sampled RGBA lanes lie independently in[0,1]; this is a finite input contract, not texture inspection',
            'History/sample locations, source uniforms, masks, phase/state and other inputs remain fixed across the compared states',
            'Input delta bounds sampled-site lanes; blur/sampling image-operator amplification and actual history evolution require separate bounds',
            'Only authored shader power nodes are interpreted; native legacy gamma remains its existing summed gain',
            'Modulus is nominal real source response before native quantization, storage/clipping and perceived visibility']}
    try:
        selected=analysis.stages[stage]
        field=analysis.outputs.get(stage)
        if selected['kind'] not in {'custom_composite','custom_warp'} or field is None:
            raise ValueError('selected authored shader field required; native/default/unknown stage remains separate')
        if selected.get('source_contains_clip'):raise ValueError('shader discard/incomplete writes prevent full colour modulus')
        if known_invalid_phase_offset(field,preserve_zero_products=True):raise ValueError('known invalid original shader/coordinate domain')
        original=list(_walk(_data_return(field)))
        if any(n.op in {'unknown','uninitialized','unresolved','sequence'} or n.op.startswith('loop_') for n,p in original):
            raise ValueError('opaque original shader colour or coordinate path')
        for sample,path in original:
            if sample.op!='sample':continue
            for node,where in _walk(sample.args[0]):
                if node.op=='sample' and node.detail.get('canonical_texture') in HISTORY:
                    raise ValueError('history-driven sampling coordinate prevents fixed-site colour modulus')
        replaced,samples=substitute_sample_values(_data_return(field))
        domains=dict(input_domains or {});varying=set();sites=[]
        for name,sample in samples:
            for lane in 'xyzw':domains[name+'.'+lane]=[0.,1.]
            if sample.detail.get('canonical_texture') in HISTORY:varying.update(name+'.'+lane for lane in 'xyzw')
            sites.append({'sample_site_index':sample.detail.get('site_index'),'canonical_texture':sample.detail.get('canonical_texture'),
                          'varying':sample.detail.get('canonical_texture') in HISTORY})
        if not varying:raise ValueError('no declared varying main/blur sample sites')
        channels=blackout_colour_channels(replaced)
        if len(channels)!=3:raise ValueError('typed RGB channel projection unresolved')
        result['channels']=[scalar_difference_modulus(c,input_domains=domains,varying_inputs=varying,native_scalar_limit=_f32_max()) for c in channels]
        result['sample_sites']=sites
        result['status']='bounded' if all(c['status']=='bounded' for c in result['channels']) else 'partial'
        if result['status']!='bounded':result['unknown_reasons']=sorted({s for c in result['channels'] for s in c['unknown_reasons']})
        coefficients={}
        for channel in result['channels']:
            for term in channel['terms']:coefficients[term['exponent']]=max(coefficients.get(term['exponent'],0.),term['coefficient'])
        result['concave_envelope_terms']=_terms(coefficients)
        result['concave_envelope_scope']='sum of per-exponent maximum channel coefficients; monotone concave upper for Jensen/area integration, not exact RGB infinity response'
    except (ValueError,RecursionError,OverflowError,IndexError) as error:result['unknown_reasons']=[str(error)]
    result['record_sha256']=_digest(result)
    return result
