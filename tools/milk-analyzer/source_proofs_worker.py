"""Bounded Z3 queries over validated JSON source graphs, never source text."""
from fractions import Fraction
import json
import math
import sys
import time

VERSION = '5.1.0.0'
MAX_NODES = 128
MAX_DEPTH = 48
ARITY = {'input':0, 'constant':0, 'add':2, 'subtract':2, 'multiply':2,
         'negate':1, 'sqr':1, 'unary':1, 'abs':1, 'min':2, 'max':2,
         'less':2, 'greater':2, 'less_equal':2, 'greater_equal':2,
         'equal':2, 'not_equal':2, 'select':3}
PREDICATES = {'less','greater','less_equal','greater_equal','equal','not_equal'}


def rational(value):
    if type(value) not in {int,float} or not math.isfinite(value):
        raise ValueError('finite scalar literal required')
    # Match the existing scalar analyser's float conversion, then preserve that
    # binary value exactly, rather than interpreting its decimal text as real.
    return Fraction(float(value))


def domains(value):
    if not isinstance(value,dict) or len(value)>128:
        raise ValueError('explicit bounded scalar input domains required')
    result={}
    for name,span in value.items():
        if not isinstance(name,str) or not name or len(name)>256 or not isinstance(span,(list,tuple)) or len(span)!=2:
            raise ValueError('invalid scalar domain')
        lo,hi=map(rational,span)
        if lo>hi:raise ValueError('reversed scalar domain')
        result[name]=(lo,hi)
    return result


def validate_node(node):
    op=node['op']; detail=node['detail']; args=node['args']
    if op not in ARITY or len(args)!=ARITY[op]:raise ValueError('unsupported original proof operation: '+op)
    if node['dtype']!=('bool' if op in PREDICATES else 'float'):
        raise ValueError('typed/native conversion excluded')
    if op=='input':
        if set(detail)!={'name'} or not isinstance(detail['name'],str) or not detail['name'] or len(detail['name'])>256 or ':' in detail['name']:
            raise ValueError('qualified phase/storage input requires binding adapter')
    elif op=='constant':
        if set(detail)!={'value'}:raise ValueError('qualified constant excluded')
        rational(detail['value'])
    elif op=='unary':
        if set(detail)!={'operator'} or detail['operator'] not in {0,1}:raise ValueError('unsupported unary')
    elif detail:raise ValueError('qualified operation requires numeric adapter')


def decide(solver,z3):
    result=solver.check()
    if result==z3.unsat:return {'status':'proven'}
    if result==z3.sat:return {'status':'refuted'}
    return {'status':'unknown','reason':solver.reason_unknown()}


class Query:
    def __init__(self,z3,budget_ms):
        if type(budget_ms) is not int or not 1<=budget_ms<=2000:raise ValueError('bounded solver budget required')
        self.z3=z3; self.deadline=time.monotonic()+budget_ms/1000; self.checks=0; self.unknowns=[]

    def check(self,constraints,violation):
        left=int((self.deadline-time.monotonic())*1000)
        if left<1:
            reason='request solver time budget exhausted';self.unknowns.append(reason)
            return {'status':'unknown','reason':reason}
        solver=self.z3.Solver();solver.set(timeout=left,rlimit=200000)
        solver.add(*constraints,violation);self.checks+=1
        result=decide(solver,self.z3)
        if result['status']=='unknown':self.unknowns.append(result['reason'])
        if result['status']=='refuted':
            result['counterexample']={str(d):str(solver.model()[d]) for d in solver.model().decls()}
        return result


def span_op(op,args):
    if op=='negate':return (-args[0][1],-args[0][0])
    if op in {'less','greater','less_equal','greater_equal','equal','not_equal'}:return (Fraction(0),Fraction(1))
    if op=='select':return (min(args[1][0],args[2][0]),max(args[1][1],args[2][1]))
    a=args[0]
    if op=='abs':return (max(0,a[0],-a[1]),max(abs(v) for v in a))
    if op=='sqr':return (0 if a[0]<=0<=a[1] else min(v*v for v in a),max(v*v for v in a))
    b=args[1]
    if op=='add':return (a[0]+b[0],a[1]+b[1])
    if op=='subtract':return (a[0]-b[1],a[1]-b[0])
    if op=='multiply':
        terms=[x*y for x in a for y in b];return (min(terms),max(terms))
    if op=='min':return (min(a[0],b[0]),min(a[1],b[1]))
    if op=='max':return (max(a[0],b[0]),max(a[1],b[1]))
    raise ValueError('unsupported interval operation')


def real(z3,value):return z3.RealVal(f'{value.numerator}/{value.denominator}')


def operation(z3,op,args,model):
    fp=model=='ieee754-binary32-rne';r=z3.RNE()
    if op=='negate':return -args[0]
    if op in {'add','subtract','multiply','sqr'}:
        a=args[0];b=args[0] if op=='sqr' else args[1]
        if fp:return {'add':z3.fpAdd,'subtract':z3.fpSub,'multiply':z3.fpMul,'sqr':z3.fpMul}[op](r,a,b)
        return {'add':lambda:a+b,'subtract':lambda:a-b,'multiply':lambda:a*b,'sqr':lambda:a*b}[op]()
    if op=='abs':return z3.fpAbs(args[0]) if fp else z3.If(args[0]<0,-args[0],args[0])
    if op in {'min','max'}:
        if fp:raise ValueError('FP min/max native NaN policy requires adapter')
        return z3.If(args[0]<args[1],args[0],args[1]) if op=='min' else z3.If(args[0]>args[1],args[0],args[1])
    if op=='select':return z3.If(*args)
    a,b=args
    if fp:
        return {'less':z3.fpLT,'greater':z3.fpGT,'less_equal':z3.fpLEQ,'greater_equal':z3.fpGEQ,
                'equal':z3.fpEQ,'not_equal':lambda x,y:z3.Not(z3.fpEQ(x,y))}[op](a,b)
    return {'less':lambda:a<b,'greater':lambda:a>b,'less_equal':lambda:a<=b,'greater_equal':lambda:a>=b,
            'equal':lambda:a==b,'not_equal':lambda:a!=b}[op]()


def lower(program,declared,z3,model):
    if model not in {'nominal-real','ieee754-binary32-rne'}:raise ValueError('unknown numeric model')
    nodes=program['nodes'];memo={};active=set();variables={};constraints=[];finite=[]
    if not isinstance(nodes,list) or not 1<=len(nodes)<=MAX_NODES:raise ValueError('proof graph node budget exceeded')
    def visit(index,depth=0):
        if type(index) is not int or not 0<=index<len(nodes):raise ValueError('invalid graph reference')
        if index in memo:return memo[index]
        if depth>MAX_DEPTH or index in active:raise ValueError('proof depth/cycle budget exceeded')
        active.add(index);node=nodes[index];validate_node(node)
        children=[visit(i,depth+1) for i in node['args']]
        args=[c[0] for c in children];spans=[c[1] for c in children];op=node['op'];detail=node['detail']
        if op=='input':
            name=detail['name']
            if name not in declared:raise ValueError('missing declared domain for '+name)
            if name not in variables:
                if model=='nominal-real':
                    variable=z3.Real(name);lo,hi=(real(z3,v) for v in declared[name]);constraints.extend([variable>=lo,variable<=hi])
                else:
                    if declared[name][0]==declared[name][1]:
                        variable=z3.simplify(z3.fpRealToFP(z3.RNE(),real(z3,declared[name][0]),z3.Float32()))
                        if not z3.is_true(z3.simplify(z3.fpToReal(variable)==real(z3,declared[name][0]))):
                            raise ValueError('singleton FP domain is not representable as binary32')
                    else:
                        variable=z3.FP(name,z3.Float32());as_real=z3.fpToReal(variable)
                        constraints.extend([z3.Not(z3.fpIsNaN(variable)),z3.Not(z3.fpIsInf(variable)),
                                            as_real>=real(z3,declared[name][0]),as_real<=real(z3,declared[name][1])])
                variables[name]=variable
            result=variables[name];span=declared[name]
        elif op=='constant':
            value=rational(detail['value']);span=(value,value)
            result=real(z3,value) if model=='nominal-real' else z3.fpRealToFP(z3.RNE(),real(z3,value),z3.Float32())
        else:
            if op=='unary':op='negate' if detail['operator']==0 else 'identity'
            if op=='identity':result=args[0];span=spans[0]
            else:
                result=operation(z3,op,args,model);span=span_op(op,spans)
        if node['dtype']=='float' and model=='ieee754-binary32-rne':finite.append(z3.And(z3.Not(z3.fpIsNaN(result)),z3.Not(z3.fpIsInf(result))))
        active.remove(index);memo[index]=(result,span);return memo[index]
    expression,span=visit(program['root'])
    return expression,span,constraints,finite,sorted(variables)


def export_span(span):
    result=[]
    for index,value in enumerate(span):
        rounded=float(value)
        if not math.isfinite(rounded):raise ValueError('nominal bound cannot be represented as finite float')
        if index==0 and Fraction(rounded)>value:rounded=math.nextafter(rounded,-math.inf)
        if index==1 and Fraction(rounded)<value:rounded=math.nextafter(rounded,math.inf)
        if not math.isfinite(rounded):raise ValueError('nominal bound enclosure overflow')
        result.append(rounded)
    return result


def value_bounds(expression,span,constraints,query):
    z3=query.z3
    # Every returned endpoint is checked against the original, unsimplified
    # source expression. SAT does not prove a bound; UNKNOWN keeps it unresolved.
    result=query.check(constraints,z3.Or(expression<real(z3,span[0]),expression>real(z3,span[1])))
    if result['status']!='proven':return result
    lo,hi=span
    for candidate in (Fraction(0),Fraction(1),Fraction(-1)):
        if lo<candidate<=hi and query.check(constraints,expression<real(z3,candidate))['status']=='proven':lo=candidate
        if lo<=candidate<hi and query.check(constraints,expression>real(z3,candidate))['status']=='proven':hi=candidate
    # A fixed number of binary decisions limits cost. Retain the proven outer
    # endpoints; this is a conservative range, not an optimisation optimum.
    for lower in (True,False):
        left,right=lo,hi
        for _ in range(6):
            if left==right:break
            middle=(left+right)/2
            violation=expression<real(z3,middle) if lower else expression>real(z3,middle)
            check=query.check(constraints,violation)
            if check['status']=='unknown':break
            if lower:
                if check['status']=='proven':lo=middle;left=middle
                else:right=middle
            else:
                if check['status']=='proven':hi=middle;right=middle
                else:left=middle
    return {'status':'bounded','nominal_value_range':export_span((lo,hi)),
            'exact_rational_bounds':[[str(v.numerator),str(v.denominator)] for v in (lo,hi)]}


def graph_query(request,z3,query):
    model=request.get('numeric_model','nominal-real')
    expression,span,constraints,finite,names=lower(request['graph'],domains(request.get('input_domains')),z3,model)
    feasible=query.check(constraints,z3.BoolVal(True))
    if feasible['status']!='refuted':
        return {'status':'unknown','reason':'input domain feasibility not established','feasibility_obligation':feasible}
    if finite:
        check=query.check(constraints,z3.Not(z3.And(*finite)))
        if check['status']!='proven':return {'status':'unknown','reason':'FP model may have nonfinite intermediates','finite_obligation':check}
    if request['task']=='predicate':
        if not z3.is_bool(expression):raise ValueError('predicate must have bool result')
        false=query.check(constraints,z3.Not(expression))
        if false['status']=='proven':result={'status':'proven','truth_value':True}
        else:
            true=query.check(constraints,expression)
            if true['status']=='proven':result={'status':'proven','truth_value':False}
            elif false['status']=='refuted' and true['status']=='refuted':result={'status':'mixed','truth_value':None,'false_counterexample':false['counterexample'],'true_counterexample':true['counterexample']}
            else:result={'status':'unknown','truth_value':None,'reason':false.get('reason',true.get('reason','solver unknown'))}
    else:
        if model!='nominal-real' or z3.is_bool(expression):raise ValueError('scalar range requires nominal real scalar')
        candidate=request.get('candidate_bounds')
        if candidate is not None:
            proposed=domains({'candidate':candidate})['candidate']
            check=query.check(constraints,z3.Or(expression<real(z3,proposed[0]),expression>real(z3,proposed[1])))
            if check['status']=='proven':span=(max(span[0],proposed[0]),min(span[1],proposed[1]))
        result=value_bounds(expression,span,constraints,query)
    result['assumed_finite_input_names']=names
    return result


def invariant_query(request,z3,query):
    declared=domains(request.get('input_domains'));candidates=domains(request['candidates'])
    if not candidates:raise ValueError('candidate persistent-state bounds required')
    resets=set(request['reset_names']);qnames={f'q{i}' for i in range(1,33)}
    state={name:real(z3,Fraction(0)) for name in qnames}
    spans={f'q{i}':(Fraction(0),Fraction(0)) for i in range(1,33)};constraints=[];count=0
    for name,span in declared.items():
        state[name]=z3.Real('init:'+name);spans[name]=span
        constraints.extend([state[name]>=real(z3,span[0]),state[name]<=real(z3,span[1])])
    def execute(program,current,ranges):
        nonlocal count
        def expression(node,depth=0):
            nonlocal count
            count+=1
            if count>512 or depth>MAX_DEPTH:raise ValueError('equation proof budget exceeded')
            kind=node.get('kind')
            if kind=='constant':
                value=rational(node['value']);return real(z3,value),(value,value)
            if kind=='variable':
                name=node['name'].lower()
                if name not in current:raise ValueError('unknown initialized/reset storage '+name)
                return current[name],ranges[name]
            functions={'_add':'add','_sub':'subtract','_mul':'multiply','_neg':'negate','min':'min','max':'max','abs':'abs','above':'greater','below':'less'}
            op=functions.get(node.get('function'))
            if kind!='call' or op is None or node.get('instructions') or len(node.get('args',[]))!=ARITY[op]:
                raise ValueError('unsupported equation effect/numeric operation')
            children=[expression(a,depth+1) for a in node['args']]
            args=[a[0] for a in children];bounds=[a[1] for a in children]
            value=operation(z3,op,args,'nominal-real')
            if op in PREDICATES:value=z3.If(value,real(z3,Fraction(1)),real(z3,Fraction(0)))
            span=span_op(op,bounds)
            # Preserve original arithmetic representability obligations before
            # Z3 can correlate/cancel a later use of this intermediate.
            export_span(span)
            return value,span
        for node in program:
            if node.get('function')!='assign' or len(node.get('args',[]))!=2 or node['args'][0].get('kind')!='variable':
                raise ValueError('straight-line assignments required')
            name=node['args'][0]['name'].lower();current[name],ranges[name]=expression(node['args'][1])
    execute(request['initialization'],state,spans)
    for name in candidates:
        if name in resets or name in qnames:raise ValueError('candidate is reset storage, not persistent state')
        if name not in state:raise ValueError('candidate state lacks initialization')
    def violations(current):
        return z3.Or(*[z3.Or(current[n]<real(z3,s[0]),current[n]>real(z3,s[1])) for n,s in candidates.items()])
    initial=query.check(constraints,violations(state))
    if initial['status']!='proven':return {**initial,'failed_obligation':'initialization'}
    qdefaults={n:state[n] for n in qnames}
    qspans={n:spans[n] for n in qdefaults};inputs={};ranges={};constraints=[]
    # Every persistent dependency must have an explicit candidate. Merely
    # retaining a post-init constant would miss later mutation by this phase.
    for name,span in candidates.items():
        inputs[name]=z3.Real('state:'+name);ranges[name]=span
        constraints.extend([inputs[name]>=real(z3,span[0]),inputs[name]<=real(z3,span[1])])
    for name,span in declared.items():
        if name not in resets:raise ValueError('declared frame input is not host reset storage')
        inputs[name]=z3.Real('frame:'+name);ranges[name]=span
        constraints.extend([inputs[name]>=real(z3,span[0]),inputs[name]<=real(z3,span[1])])
    # Init Q snapshots may depend on declared init inputs. Preserve their
    # original constraints rather than sharing them with fresh frame inputs.
    for name,span in declared.items():
        variable=state.get(name)
        # The init symbol appears inside Q expressions even after init writes.
        original=z3.Real('init:'+name)
        constraints.extend([original>=real(z3,span[0]),original<=real(z3,span[1])])
    inputs.update(qdefaults);ranges.update(qspans)
    execute(request['transition'],inputs,ranges)
    transition=query.check(constraints,violations(inputs))
    if transition['status']!='proven':return {**transition,'failed_obligation':'transition'}
    outputs={}
    assigned={n['args'][0]['name'].lower() for n in request['transition']}
    for name in sorted(assigned):
        if name in qdefaults:
            bounded=value_bounds(inputs[name],ranges[name],constraints,query)
            if bounded['status']=='bounded':outputs[name]=bounded['nominal_value_range']
    return {'status':'proven','obligations':{'initialization':'proven','transition':'proven'},
            'candidate_state_domains':request['candidates'],'frame_output_domains':outputs,
            'reset_policy':'main-Q reloads post-init snapshot; host inputs reset; only candidate private state persists'}


def solve(request,z3):
    query=Query(z3,request.get('solver_timeout_ms',200))
    result=invariant_query(request,z3,query) if request['task']=='invariant' else graph_query(request,z3,query)
    result['solver_checks']=query.checks
    result['unknown_checks']=len(query.unknowns)
    result['solver_unknown_reasons']=sorted(set(query.unknowns))
    return result


def main():
    import z3
    if z3.get_version()!=(5,1,0,0):raise ValueError('pinned Z3 '+VERSION+' required')
    print(json.dumps({'protocol':1,'z3_version':VERSION}),flush=True)
    for line in sys.stdin:
        try:
            if len(line)>131072:raise ValueError('proof request byte budget exceeded')
            request=json.loads(line)['program']
            result=solve(request,z3)
        except (ValueError,KeyError,TypeError,RecursionError,OverflowError,z3.Z3Exception) as error:
            result={'status':'unsupported','reason':str(error)}
        print(json.dumps(result,allow_nan=False),flush=True)


if __name__=='__main__':main()
