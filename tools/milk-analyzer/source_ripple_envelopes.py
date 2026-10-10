"""Conditional coefficient and deformation ranges for extracted ripple maps."""
import math
from fractions import Fraction
from shader_fields import Field


def coefficient_envelope(field,*,input_domains=None,response_inputs=None):
    from source_control_bounds import scalar_value_envelope,scalar_response_envelope
    from source_appearance import _canonical_lane
    from source_native_warp import _f32
    from field_math import SWIZZLE
    from effect_families import _parts,_deps
    memo={};active=set();domains=dict(input_domains or {});assumptions=set();derived=set();tainted=set()
    def project(original,depth=0):
        key=id(original)
        if key in memo:return memo[key][1]
        if depth>64 or len(memo)+len(active)>=512 or key in active:raise ValueError('ripple coefficient projection budget exceeded')
        active.add(key)
        try:
            node=_canonical_lane(original)
            if node.op=='cast' and node.dtype=='float' and node.detail.get('target_type')=='float' and len(node.args)==1 and node.args[0].dtype in {'float','float2','float3','float4'}:
                parts=_parts(node.args[0])
                if not parts or parts[0].dtype!='float':raise ValueError('float coefficient cast lane unresolved')
                result=project(parts[0],depth+1)
            elif node.op=='dot' and len(node.args)==2:
                a,b=map(_parts,node.args)
                if len(a)!=len(b) or not 1<=len(a)<=4:raise ValueError('coefficient dot dimensions unresolved')
                result=Field('constant',detail={'value':0.})
                for x,y in zip(a,b):result=Field('add',(result,Field('multiply',(project(x,depth+1),project(y,depth+1)),'float')),'float')
            elif node.op=='member' and node.detail.get('swizzle') and len(node.detail.get('field',''))==1:
                if node.dtype!='float':raise ValueError('coefficient member result is not scalar float')
                parent=node.args[0];lane=SWIZZLE[node.detail['field']];name=parent.detail.get('name')
                if parent.op=='input':
                    if parent.dtype not in {'float2','float3','float4'} or lane>=int(parent.dtype[-1]) or not isinstance(name,str) or not name:
                        raise ValueError('ripple coefficient scalar input identity/type unresolved')
                    result=Field('input',dtype='float',detail={'name':name+'.'+'xyzw'[lane]})
                elif parent.op=='domain_checked':
                    parts=_parts(parent.args[0])
                    if lane>=len(parts):raise ValueError('guarded coefficient lane unresolved')
                    result=Field('domain_checked',(project(parts[lane],depth+1),),'float',parent.detail)
                else:
                    parts=_parts(parent)
                    if lane>=len(parts) or parts[lane].op=='member' and parts[lane].args and parts[lane].args[0] is parent:
                        raise ValueError('cross-lane coefficient member unresolved')
                    result=project(parts[lane],depth+1)
            else:
                args=tuple(project(v,depth+1) for v in node.args)
                if node.op=='narrow' and node.detail.get('numeric_domain')=='shader-float32':
                    report=scalar_value_envelope(args[0],input_domains=domains);span=report['nominal_value_range']
                    assumptions.update(set(report['assumed_finite_input_names'])-derived)
                    if span is None:raise ValueError('ripple native upload range unresolved')
                    name=':ripple-coefficient-upload-'+str(len(memo));domains[name]=[_f32(v) for v in span]
                    derived.add(name)
                    dependencies=_deps(args[0])
                    if response_inputs is not None and (dependencies&set(response_inputs) or dependencies&tainted):tainted.add(name)
                    result=Field('input',dtype='float',detail={'name':name})
                else:result=Field(node.op,args,node.dtype,node.detail)
        finally:active.remove(key)
        memo[key]=(original,result);return result
    try:
        selected=project(field)
        if response_inputs is None:r=scalar_value_envelope(selected,input_domains=domains)
        else:
            if _deps(selected)&tainted:raise ValueError('sample-dependent quantized coefficient prevents continuous response')
            r=scalar_response_envelope(selected,input_names=response_inputs,input_domains=domains)
        r['assumed_finite_input_names']=sorted(assumptions|set(r['assumed_finite_input_names'])-derived)
        return r
    except (ValueError,RecursionError,OverflowError,IndexError) as error:
        unknown=Field('unknown',detail={'reason':str(error)})
        r=scalar_value_envelope(unknown) if response_inputs is None else scalar_response_envelope(unknown,input_names=response_inputs)
        r['unknown_reasons']=[str(error)];return r


def _upper(value):
    if value is None:return None
    try:result=float(value)
    except OverflowError:return None
    if Fraction(result)<value:result=math.nextafter(result,math.inf)
    if not math.isfinite(result):return None
    return result


def deformation_envelope(waves,*,basis,identity_baseline,input_domains=None):
    amp_reports=[];gradient_reports=[];displacement=[Fraction(0),Fraction(0)];jacobian=[Fraction(0),Fraction(0)]
    def magnitude(report):
        span=report['nominal_value_range']
        return None if span is None else max(abs(Fraction(v)) for v in span)
    def add(a,b):return None if a is None or b is None else a+b
    def multiply(a,b):
        if a==0 or b==0:return Fraction(0)
        return None if a is None or b is None else a*b
    for w in waves:
        amps=[coefficient_envelope(v,input_domains=input_domains) for v in w['amplitude']]
        gradients=[coefficient_envelope(v,input_domains=input_domains) for v in w['gradient']]
        amp_reports.append(amps);gradient_reports.append(gradients)
        k=sum((magnitude(r) for r in gradients if magnitude(r) is not None),Fraction(0))
        if any(magnitude(r) is None for r in gradients):k=None
        for i,a in enumerate(amps):
            value=magnitude(a);displacement[i]=add(displacement[i],value)
            jacobian[i]=add(jacobian[i],multiply(value,k))
    row_bounds=[_upper(v) for v in jacobian]
    bound=max(row_bounds) if all(v is not None for v in row_bounds) and basis in {'shader_uv','original_uv'} else None
    return {'policy':'source-uniform-ripple-deformation-envelope-v1',
        'amplitude_value_envelopes':amp_reports,'phase_gradient_value_envelopes':gradient_reports,
        'maximum_absolute_displacement_uv':[_upper(v) for v in displacement],
        'jacobian_perturbation_row_sum_upper_bounds':row_bounds if basis in {'shader_uv','original_uv'} else None,
        'jacobian_perturbation_infinity_norm_upper_bound':bound,
        'identity_no_fold_sufficient':bound<1 if bound is not None and identity_baseline else None,
        'visible_motion_intensity':None,'actual_fold_present':None,
        'native_numeric_certified':False,'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False,
        'conditions':['Each listed nominal uniform coefficient range holds under its finite-input/intermediate premises',
                      'Triangle bounds ignore phase correlations and may overestimate displacement/deformation',
                      'Uniform controls held fixed across the spatial domain; audio ranges are not invented',
                      'Native uploads require finite endpoint conversion; rounding, interpolation and shader arithmetic remain unqualified',
                      'UV Jacobian certificates require a single UV basis; identity no-fold condition is sufficient, not actual fold detection',
                      'No screen velocity, temporal continuity, source-area prominence, feedback persistence or mood score is established']}
