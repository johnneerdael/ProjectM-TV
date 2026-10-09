"""Conservative stored-RGB envelopes for supported typed shader expressions.

No equation/shader execution, time samples or pixel fields. These are conditional
expression bounds, not automatic preset-output qualification or GPU certificates.
EEL's existing integer-remainder domains do not implement this float32 shader
contract; reuse Field/layout/storage primitives with a separate bounded walker.
"""
import numpy as np
from field_math import typed,numeric_layout,UnresolvedMath,SWIZZLE
from feedback_field import unorm8
from descriptors import LUMA


POLICY='finite-float32-rgb-envelope-v1'


def _shape(dtype):
    base,shape=numeric_layout(dtype)
    if len(shape)>1 or '[' in dtype:raise UnresolvedMath('matrix/array bounds not established')
    return base,shape


def _coerce(lo,hi,dtype,*,outward=False):
    base,shape=_shape(dtype);lo=np.asarray(lo,np.float64);hi=np.asarray(hi,np.float64)
    if lo.shape!=hi.shape or not np.all(np.isfinite(lo)) or not np.all(np.isfinite(hi)) or np.any(lo>hi):
        raise UnresolvedMath('finite ordered matching interval endpoints required')
    count=int(np.prod(shape)) if shape else 1
    def resize(value):
        flat=value.reshape(-1)
        if len(flat)==1:flat=np.repeat(flat,count)
        elif len(flat)>=count:flat=flat[:count]
        else:raise UnresolvedMath('insufficient interval components')
        return flat.reshape(shape)
    lo,hi=resize(lo),resize(hi)
    if base=='float':
        with np.errstate(over='ignore',invalid='ignore'):
            a=lo.astype(np.float32);b=hi.astype(np.float32)
            # One outward float32 neighbour bounds endpoint evaluation/rounding
            # and retains real intermediate products for possible fused paths.
            if outward:
                a=np.nextafter(a,np.float32(-np.inf));b=np.nextafter(b,np.float32(np.inf))
            else:
                a=np.where(a.astype(np.float64)>lo,np.nextafter(a,np.float32(-np.inf)),a)
                b=np.where(b.astype(np.float64)<hi,np.nextafter(b,np.float32(np.inf)),b)
        if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
            raise UnresolvedMath('float32 interval overflow remains unresolved')
        return a.astype(np.float64),b.astype(np.float64)
    if base=='int':
        limits=np.iinfo(np.int32)
        if np.any(lo<limits.min) or np.any(hi>limits.max):raise UnresolvedMath('integer interval conversion outside int32')
        return np.trunc(lo),np.trunc(hi)
    if base=='bool':
        fixed_zero=(lo==0)&(hi==0);excludes_zero=(lo>0)|(hi<0)
        return excludes_zero.astype(float),(~fixed_zero).astype(float)
    raise UnresolvedMath('unsupported interval scalar type')


class _Bounds:
    def __init__(self,inputs,samplers,max_nodes):
        self.inputs=inputs;self.samplers=set(samplers);self.max_nodes=max_nodes
        self.cache={};self.active=set();self.nodes=0

    def visit(self,node):
        key=id(node)
        if key in self.cache:return self.cache[key]
        if key in self.active:raise UnresolvedMath('cyclic interval dependency')
        self.nodes+=1
        if self.nodes>self.max_nodes:raise UnresolvedMath('shader interval proof budget exceeded')
        self.active.add(key)
        try:result=self.calculate(node)
        finally:self.active.remove(key)
        self.cache[key]=result
        return result

    def calculate(self,node):
        op=node.op;dtype=node.dtype
        if op=='constant':
            value=typed(node.detail['value'],dtype)
            return _coerce(value,value,dtype)
        if op=='input':
            name=node.detail['name'];box=self.inputs.get(name)
            if box is None:
                if 'unbound_default' not in node.detail:raise UnresolvedMath('missing declared interval input: '+name)
                value=typed(node.detail['unbound_default'],dtype)
                return _coerce(value,value,dtype)
            if not isinstance(box,dict) or set(box)!={'lower','upper'}:
                raise UnresolvedMath('input interval needs lower and upper: '+name)
            _,shape=_shape(dtype)
            lo,hi=np.asarray(box['lower']),np.asarray(box['upper'])
            if lo.shape not in (shape,()) or hi.shape!=lo.shape:raise UnresolvedMath('declared interval input shape mismatch: '+name)
            return _coerce(lo,hi,dtype)
        if op=='select':
            lo,hi=self.visit(node.args[0])
            if lo.shape!=():raise UnresolvedMath('scalar interval condition required')
            if lo==0 and hi==0:return _coerce(*self.visit(node.args[2]),dtype)
            if lo>0 or hi<0:return _coerce(*self.visit(node.args[1]),dtype)
            a,b=self.visit(node.args[1]);c,d=self.visit(node.args[2])
            return _coerce(np.minimum(a,c),np.maximum(b,d),dtype)
        if op=='sample':
            if node.detail.get('sampler') not in self.samplers:
                raise UnresolvedMath('sample lacks declared normalized finite texture contract')
            if len(node.args)!=1:raise UnresolvedMath('texture overload bound not established')
            lo,hi=self.visit(node.args[0])
            if lo.shape!=(2,):raise UnresolvedMath('finite two-coordinate texture bound required')
            return _coerce(0,1,dtype)
        if op.startswith('loop_') or op in {'unknown','uninitialized','sequence'}:
            raise UnresolvedMath('control/state/domain effects not established for bounds: '+op)
        args=[self.visit(arg) for arg in node.args]
        if op in {'cast','domain_checked'}:return _coerce(*args[0],dtype)
        if op in {'construct','components','aggregate'}:
            return _coerce(np.concatenate([a.reshape(-1) for a,b in args]),
                           np.concatenate([b.reshape(-1) for a,b in args]),dtype)
        if op=='member' and node.detail.get('swizzle'):
            indices=[SWIZZLE[c] for c in node.detail['field']]
            a,b=args[0]
            if a.ndim!=1 or any(i>=len(a) for i in indices):raise UnresolvedMath('interval swizzle exceeds type')
            return _coerce(a[indices],b[indices],dtype)
        if op=='flat_component':
            index=node.detail['index'];a,b=args[0]
            if not 0<=index<a.size:raise UnresolvedMath('interval component exceeds type')
            return _coerce(a.flat[index],b.flat[index],dtype)
        if op=='unary':
            a,b=args[0];operator=node.detail['operator']
            if operator==0:return _coerce(-b,-a,dtype)
            if operator==1:return _coerce(a,b,dtype)
            if operator==2:
                lo,hi=_coerce(a,b,'bool');return _coerce(1-hi,1-lo,dtype)
            raise UnresolvedMath('stateful unary interval operation')
        if op=='abs':
            a,b=args[0]
            return _coerce(np.where((a<=0)&(b>=0),0,np.minimum(abs(a),abs(b))),np.maximum(abs(a),abs(b)),dtype)
        if op=='saturate':return _coerce(np.clip(args[0][0],0,1),np.clip(args[0][1],0,1),dtype)
        if op in {'add','subtract','multiply','divide'}:
            a,b=args[0];c,d=args[1]
            if op=='add':lo,hi=a+c,b+d
            elif op=='subtract':lo,hi=a-d,b-c
            else:
                if op=='divide' and np.any((c<=0)&(d>=0)):raise UnresolvedMath('interval division crosses zero')
                fn=np.multiply if op=='multiply' else np.divide
                values=np.stack([fn(x,y) for x in (a,b) for y in (c,d)])
                lo,hi=values.min(axis=0),values.max(axis=0)
            return _coerce(lo,hi,dtype,outward=dtype.startswith('float'))
        if op in {'min','max'}:
            fn=np.minimum if op=='min' else np.maximum
            return _coerce(fn(args[0][0],args[1][0]),fn(args[0][1],args[1][1]),dtype)
        if op=='clamp':
            a,b=args[0];c,d=args[1];e,f=args[2]
            if np.any(d>e):raise UnresolvedMath('clamp endpoint ordering unproved')
            return _coerce(np.minimum(np.maximum(a,c),e),np.minimum(np.maximum(b,d),f),dtype)
        if op in {'less','less_equal','greater','greater_equal','equal','not_equal'}:
            a,b=args[0];c,d=args[1]
            if op=='less':yes,no=b<c,a>=d
            elif op=='less_equal':yes,no=b<=c,a>d
            elif op=='greater':yes,no=a>d,b<=c
            elif op=='greater_equal':yes,no=a>=d,b<c
            else:
                same=(a==b)&(c==d)&(a==c);disjoint=(b<c)|(d<a)
                yes,no=(same,disjoint) if op=='equal' else (disjoint,same)
            return _coerce(np.asarray(yes,float),np.asarray(~no,float),dtype)
        raise UnresolvedMath('shader interval operation unsupported: '+op)


def stored_rgb_bounds(expression,*,inputs=None,normalized_samplers=(),brightness_jump=.1,rgb_jump=.1,max_nodes=65536):
    """Bound a complete expression under supplied domains; admit no preset labels."""
    if type(max_nodes) is not int or max_nodes<1:raise ValueError('positive interval proof budget required')
    for value in (brightness_jump,rgb_jump):
        if isinstance(value,bool) or not np.isfinite(value) or value<=0:raise ValueError('positive finite jump thresholds required')
    if inputs is not None and not isinstance(inputs,dict):raise ValueError('declared interval input dictionary required')
    if not isinstance(normalized_samplers,(list,tuple,set)) or any(not isinstance(s,str) for s in normalized_samplers):
        raise ValueError('explicit normalized sampler names required')
    report={'policy':POLICY,'status':'unknown','scope':'stored RGB expression under declared input/sampler domain',
        'display_fields_constructed':False,'shader_or_equation_execution':False,
        'stored_rgb':None,'maximum_rgb_jump_bound':None,'maximum_luma_jump_bound':None,
        'stored_rgb_invariant':None,'no_sampled_brightness_or_rgb_jump':None,
        'motion_bound':None,'automatic_preset_classification':False,'unknown_reasons':[],
        'premises':['Declared intervals include every admitted effective shader input',
                    'Named sampler calls are defined and return finite normalized components',
                    'Complete final expression and nearest-even UNORM8 store; later display changes excluded'],
        'thresholds':{'brightness_jump':brightness_jump,'rgb_jump':rgb_jump}}
    walker=_Bounds(inputs or {},normalized_samplers,max_nodes)
    try:
        lo,hi=walker.visit(expression)
        if expression.dtype!='float3' or lo.shape!=(3,):raise UnresolvedMath('complete float3 RGB expression required')
        lo,hi=unorm8(lo),unorm8(hi)
        delta=hi.astype(np.float64)-lo.astype(np.float64)
        # Bounds contain all pixel locations and updates; no pairing assumption.
        # Positive luma weights plus outward float32 neighbours account for
        # the maintained encoded-RGB dot/reduction's finite rounding envelope.
        lower,upper=np.float64(0),np.float64(0)
        for index,weight in enumerate(LUMA):
            a,b=_coerce(lo[index]*np.float64(weight),hi[index]*np.float64(weight),'float',outward=True)
            lower,upper=_coerce(lower+a,upper+b,'float',outward=True)
        # Descriptor differences subtract in float32, not in the float64
        # arithmetic used to describe the envelope endpoints.
        _,rgb_difference=_coerce(-delta,delta,'float3',outward=True)
        _,luma_difference=_coerce(0,float(upper-lower),'float',outward=True)
        rgb_delta=min(1.,float(rgb_difference.max()));luma_delta=float(luma_difference)
        report.update(status='computed',stored_rgb={'lower':lo.tolist(),'upper':hi.tolist()},
            maximum_rgb_jump_bound=rgb_delta,maximum_luma_jump_bound=luma_delta,
            stored_rgb_invariant=bool(np.array_equal(lo,hi)),
            no_sampled_brightness_or_rgb_jump=bool(rgb_delta<rgb_jump and luma_delta<brightness_jump))
    except (UnresolvedMath,ValueError,TypeError,IndexError,RecursionError) as error:
        report['unknown_reasons']=[str(error)]
    finally:
        report['proof_nodes']=walker.nodes
        walker.inputs=None;walker.cache.clear();walker.active.clear()
    return report
