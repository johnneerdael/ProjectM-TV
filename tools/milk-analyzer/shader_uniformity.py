"""Bounded proof of lane independence for pure, explicitly bound shader inputs."""
import numpy as np
from field_math import numeric_layout,UnresolvedMath

PURE_OPERATIONS={
    'constant','input','components','member','flat_component','construct','aggregate',
    'cast','matrix_cast','matrix_constructor','matrix_product','unary','index',
    'add','subtract','multiply','divide','remainder','and','or','select',
    'less','greater','less_equal','greater_equal','equal','not_equal',
    'saturate','clamp','min','max','frac','sin','cos','tan','exp','exp2','log','log2',
    'log10','sqrt','rsqrt','pow','abs','floor','ceil','sign','step','smoothstep',
    'lerp','all','any','dot','length','distance','normalize','reflect','cross','mul',
    'domain_checked','source_domain_guard','index_guard',
}


class UniformityProof:
    """Keep per-call memo only; equal pixel values never substitute for a proof."""
    def __init__(self,inputs,batch_shape,*,max_nodes=65536,blocked=None):
        if type(max_nodes) is not int or max_nodes<1:raise ValueError('positive uniform proof budget required')
        self.inputs=inputs;self.batch_shape=tuple(batch_shape);self.max_nodes=max_nodes
        self.cache={};self.nodes=0;self.budget_exceeded=False
        self.blocked=set(blocked or ())

    def is_uniform(self,field):
        if self.inputs is None or self.budget_exceeded:return False
        pending=[(field,False)];active=set()
        while pending:
            node,expanded=pending.pop();key=id(node)
            if key in self.cache:continue
            if key in self.blocked:self.cache[key]=False;continue
            if expanded:
                self.cache[key]=all(self.cache.get(id(arg),False) for arg in node.args)
                active.discard(key);continue
            self.nodes+=1
            if self.nodes>self.max_nodes:
                self.budget_exceeded=True;return False
            if key in active:
                # Ordinary data DAGs are acyclic; loop state needs its executor.
                self.cache[key]=False;continue
            if node.op not in PURE_OPERATIONS:
                self.cache[key]=False;continue
            if node.op=='input':
                name=node.detail['name']
                if name not in self.inputs and 'unbound_default' not in node.detail:
                    self.cache[key]=False;continue
                try:
                    data=np.asarray(self.inputs.get(name,node.detail.get('unbound_default')))
                    _,shape=numeric_layout(node.dtype)
                    self.cache[key]=data.shape in (shape,())
                except (UnresolvedMath,ValueError,TypeError):self.cache[key]=False
                continue
            active.add(key);pending.append((node,True))
            pending.extend((arg,False) for arg in node.args if id(arg) not in self.cache)
        return self.cache.get(id(field),False)

    def release(self):
        self.inputs=None;self.cache.clear();self.blocked.clear()


def sampler_coordinate_roots(field,*,max_nodes=65536):
    """Find mutable callback values, including sample calls hidden in loops."""
    pending=[field];seen=set();blocked=set();plans=set()
    while pending:
        node=pending.pop()
        if id(node) in seen:continue
        seen.add(id(node))
        if len(seen)>max_nodes:return None
        if node.op=='sample' and node.args:blocked.add(id(node.args[0]))
        pending.extend(node.args)
        if node.op.startswith('loop_'):
            plan=node.detail.get('plan')
            if plan is not None and id(plan) not in plans:
                plans.add(id(plan));pending.extend(plan.updates.values());pending.extend(plan.effects)
                if plan.condition is not None:pending.append(plan.condition)
    return blocked
