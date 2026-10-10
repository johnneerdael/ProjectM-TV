"""Bounded calculus on continuous nominal scalar source-time formulas."""
import math


def merge_continuity(kinds):
    if not kinds or any(k=='unknown' for k in kinds):return 'unknown'
    return 'piecewise_lipschitz' if 'piecewise_lipschitz' in kinds else 'smooth_nominal'


def compound_time_bounds(field):
    from source_appearance import _phase_literal
    memo={};active=set()
    def magnitude(span):return None if span is None else max(map(abs,span))
    def add_rates(a,b):return None if a is None or b is None else a+b
    def positive_divide(a,b):
        value=a/b
        if a>0 and b>0 and value==0:raise ValueError('nominal rate quotient underflow')
        return math.nextafter(value,math.inf) if value>0 else value
    def positive_multiply(a,b):
        if a==0 or b==0:return 0.
        value=a*b
        if a>0 and b>0 and value==0:raise ValueError('nominal rate product underflow')
        return math.nextafter(value,math.inf) if value>0 else value
    def product_term(rate,span):
        if rate==0:return 0.
        maximum=magnitude(span)
        if rate is None or maximum is None:return None
        return positive_multiply(rate,maximum)
    def continuity(*items):
        return 'piecewise_lipschitz' if any(i[2]=='piecewise_lipschitz' for i in items) else 'smooth_nominal'
    def checked(span,rate,kind):
        if span is not None:
            if not all(math.isfinite(v) for v in span) or span[0]>span[1]:span=None
            else:
                # One outward step covers rounding in each endpoint operation.
                span=[math.nextafter(span[0],-math.inf),math.nextafter(span[1],math.inf)]
                if not all(math.isfinite(v) for v in span):span=None
        if rate is not None and (not math.isfinite(rate) or rate<0):rate=None
        elif rate is not None and rate>0:
            rate=math.nextafter(rate,math.inf)
            if not math.isfinite(rate):rate=None
        return span,rate,kind
    def visit(node,depth=0):
        key=id(node)
        if key in memo:return memo[key]
        if depth>64 or len(memo)+len(active)>=512 or key in active:raise ValueError('compound source-time node/depth budget exceeded')
        active.add(key)
        try:result=calculate(node,depth)
        finally:active.remove(key)
        memo[key]=result;return result
    def calculate(node,depth):
        literal=_phase_literal(node)
        if literal is not None:return ([literal,literal],0.,'smooth_nominal')
        if node.dtype!='float':return None
        if node.op=='input' and node.detail.get('name') in {'time',':native-render-time-f32'}:
            return (None,1.,'smooth_nominal')
        if node.op in {'cast','narrow','construct','components','negate','sin','cos','abs'} and len(node.args)==1:
            child=visit(node.args[0],depth+1)
            if child is None:return None
            span,rate,kind=child
            if node.op in {'cast','narrow','construct','components'}:return child
            if node.op=='negate':return checked(None if span is None else [-span[1],-span[0]],rate,kind)
            if node.op in {'sin','cos'}:
                if span is not None and span[0]==span[1] and rate==0:
                    value=(math.sin if node.op=='sin' else math.cos)(span[0]);return ([value,value],0.,kind)
                return ([-1.,1.],rate,kind)
            if span is not None:
                low=0. if span[0]<=0<=span[1] else min(map(abs,span));high=max(map(abs,span))
                if span[0]>=0 or span[1]<=0:return ([low,high],rate,kind)
                span=[low,high]
            return (span,rate,'piecewise_lipschitz')
        if node.op not in {'add','subtract','multiply','divide','eel_divide','min','max'} or len(node.args)!=2:return None
        a=visit(node.args[0],depth+1);b=visit(node.args[1],depth+1)
        if a is None or b is None:return None
        x,dx,_=a;y,dy,_=b;kind=continuity(a,b)
        if node.op in {'add','subtract'}:
            span=None if x is None or y is None else ([x[0]+y[0],x[1]+y[1]] if node.op=='add' else [x[0]-y[1],x[1]-y[0]])
            return checked(span,add_rates(dx,dy),kind)
        if node.op=='multiply':
            span=None if x is None or y is None else [min(u*v for u in x for v in y),max(u*v for u in x for v in y)]
            return checked(span,add_rates(product_term(dx,y),product_term(dy,x)),kind)
        if node.op in {'min','max'}:
            if x is not None and y is not None:
                if x[1]<=y[0]:return a if node.op=='min' else b
                if y[1]<=x[0]:return b if node.op=='min' else a
                op=min if node.op=='min' else max;span=[op(x[0],y[0]),op(x[1],y[1])]
            else:span=None
            rate=None if dx is None or dy is None else max(dx,dy)
            return checked(span,rate,'piecewise_lipschitz')
        if y is None:return None
        if node.op=='eel_divide' and -.00001<y[0]<=y[1]<.00001:
            return ([0.,0.],0.,'smooth_nominal')
        minimum=min(map(abs,y))
        if y[0]<=0<=y[1] or node.op=='eel_divide' and minimum<.00001:return None
        span=None if x is None else [min(u/v for u in x for v in y),max(u/v for u in x for v in y)]
        # Quotient rule: Df/|g|min + Dg*|f|max/|g|min^2.
        left=None if dx is None else positive_divide(dx,minimum)
        if dy==0:right=0.
        elif dy is None or x is None:right=None
        else:
            first=positive_divide(dy,minimum);second=positive_divide(magnitude(x),minimum)
            right=positive_multiply(first,second)
        return checked(span,add_rates(left,right),kind)
    result={'policy':'source-compound-time-calculus-v1','nominal_value_range':None,
            'maximum_absolute_control_rate_per_second':None,'nominal_continuity':'unknown',
            'supported_nominal_formula':False,'unknown_reasons':[]}
    try:value=visit(field)
    except (ValueError,RecursionError,OverflowError,ZeroDivisionError) as error:
        result['unknown_reasons']=[str(error)];return result
    if value is None:
        result['unknown_reasons']=['unsupported input, discontinuous operation or unproved denominator domain'];return result
    span,rate,kind=value
    result.update(nominal_value_range=span,maximum_absolute_control_rate_per_second=rate,
                  nominal_continuity=kind,supported_nominal_formula=True)
    if rate is None:result['unknown_reasons']=['no finite lifetime nominal rate bound from supported formula']
    return result
