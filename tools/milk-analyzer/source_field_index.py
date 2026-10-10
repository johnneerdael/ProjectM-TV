"""Original bounded structural queries over the predictor's existing typed graph.

This implementation uses the project's Field/child/literal/domain facilities.
It contains no glsl-transformer source, grammar, AST classes or runtime binding.
Opaque captures describe local source constructions, never numeric or visible
behaviour. Object identities stay inside one analysis; exported ids are local.
"""
from collections import defaultdict

POLICY='source-typed-field-index-v1'
FOLD_POLICY='source-typed-outer-fold-structures-v1'
FLOAT_TYPES={'float','float2','float3','float4'}


class TypedFieldIndex:
    """Index semantic child edges once, retaining budgets and unresolved nodes."""
    def __init__(self, root, *, max_nodes=4096):
        from effect_families import _children,_CACHE
        if type(max_nodes) is not int or max_nodes <= 0:
            raise ValueError('positive distinct-node budget required')
        self.root=root
        self.max_nodes=max_nodes
        self.complete=True
        self.unknown_reasons=[]
        self._nodes={}
        self._objects={}
        self._operations=defaultdict(list)
        self._parents=defaultdict(list)
        self._paths={}
        self._barriers=[]
        self._rule_cache={}
        self._phase_domain_cache={}
        self._phase_domain_inspections=0
        self._work_cache={}
        token=_CACHE.set(self._work_cache)
        try:
            pending=[(root,'output',None,None)]
            while pending:
                node,path,parent,slot=pending.pop()
                identity=id(node)
                key=self._objects.get(identity)
                if key is None:
                    if len(self._nodes)>=max_nodes:
                        self.complete=False
                        self.unknown_reasons.append('typed index distinct-node budget exceeded')
                        break
                    key='n'+str(len(self._nodes))
                    self._objects[identity]=key
                    self._nodes[key]=node
                    self._paths[key]=path
                    self._operations[(node.op,node.dtype)].append(key)
                    if node.op in {'unknown','uninitialized','sequence'} or node.op.startswith('loop_'):
                        self._barriers.append(key)
                    try:
                        children=_children(node)
                    except (ValueError,RecursionError,IndexError) as error:
                        self.complete=False
                        self.unknown_reasons.append('semantic child selection unresolved: '+str(error))
                        children=()
                    pending.extend((child,path+'/'+node.op+'['+str(i)+']',key,i)
                                   for i,child in reversed(list(enumerate(children))))
                if parent is not None:
                    self._parents[key].append({'parent_node_id':parent,'semantic_child_slot':slot})
            if self._barriers:
                self.unknown_reasons.append('unresolved typed source or loop/control nodes retained')
        finally:
            _CACHE.reset(token)

    def query(self, op, *, dtype=None):
        if dtype is not None:return list(self._operations.get((op,dtype),()))
        return [key for (operation,_),keys in self._operations.items() if operation==op for key in keys]

    def node(self, node_id):return self._nodes[node_id]
    def node_id(self, node):return self._objects.get(id(node))
    def path(self, node_id):return self._paths[node_id]
    def parents(self, node_id):return list(self._parents.get(node_id,()))

    def summary(self):
        return {'policy':POLICY,'root_node_id':self.node_id(self.root),
                'complete':self.complete,'unique_nodes':len(self._nodes),
                'semantic_edges':sum(len(v) for v in self._parents.values()),
                'node_budget':self.max_nodes,'unknown_barriers':len(self._barriers),
                'unknown_reasons':list(dict.fromkeys(self.unknown_reasons)),
                'child_policy':'existing contributing typed children, selected branches and loop dependencies',
                'paths_and_slots':'semantic child traversal; slots are not original Field.args or authored AST offsets',
                'object_identities_persisted':False,
                'phase_domain_inspections':self._phase_domain_inspections,
                'work_scope':'isolated optional inspection',
                'optional_field_visits':self._work_cache.get('field_visits',0),
                'optional_normalized_term_nodes':self._work_cache.get('normalized_term_nodes',0),
                'optional_budget_exhausted':self._work_cache.get('traversal_budget_exhausted',False)}


def field_index(field, *, stage=None, max_nodes=4096):
    """Reuse a root-bound index only inside the current analysis cache."""
    from effect_families import _CACHE
    cache=_CACHE.get()
    key=('typed_field_index',POLICY,id(field),stage,max_nodes)
    saved=None if cache is None else cache.get(key)
    if saved is not None and saved.root is field:return saved
    index=TypedFieldIndex(field,max_nodes=max_nodes)
    if cache is not None:cache[key]=index
    return index


def _uniform_literal(node):
    from source_appearance import _phase_literal
    from effect_families import _parts
    if node.dtype not in FLOAT_TYPES:return None
    if node.dtype=='float':return _phase_literal(node)
    parts=_parts(node)
    values=[_phase_literal(part) for part in parts]
    return values[0] if values and values[0] is not None and all(v==values[0] for v in values) else None


def _scaled_frac(node):
    """Capture a leaf phase, without projecting/traversing that phase program."""
    if node.dtype not in FLOAT_TYPES:return None
    if node.op=='frac' and len(node.args)==1:return 1.,node
    if node.op=='multiply' and len(node.args)==2:
        for wrapped,coefficient in (node.args,tuple(reversed(node.args))):
            if wrapped.op!='frac' or wrapped.dtype not in FLOAT_TYPES or len(wrapped.args)!=1:continue
            value=_uniform_literal(coefficient)
            if value is not None and value != 0:return value,wrapped
    return None


def _outer_match(node):
    if node.op!='abs' or node.dtype not in FLOAT_TYPES or len(node.args)!=1:return None
    inner=node.args[0]
    if inner.dtype not in FLOAT_TYPES or inner.op not in {'add','subtract'} or len(inner.args)!=2:return None
    left,right=inner.args
    for moving,fixed,reversed_order in ((left,right,False),(right,left,True)):
        part=_scaled_frac(moving)
        if part is None:continue
        constant=_uniform_literal(fixed)
        if constant is None:continue
        scale,wrapped=part
        if inner.op=='subtract':
            if reversed_order:scale=-scale;bias=constant
            else:bias=-constant
        else:bias=constant
        # Retain the mathematical construction, not a native range certificate.
        triangular=abs(scale)==2 and scale*bias==-2
        centred=scale!=0 and 0 < -bias/scale < 1
        if not triangular and not centred:continue
        return {'function':'triangular_frac_structure' if triangular else 'biased_abs_frac_structure',
                'fraction_scale':scale,'bias':bias,'wrapped':wrapped,'phase':wrapped.args[0]}
    return None


def unknown_fold_evidence(analysis, *, stage, reason):
    """Represent an optional inspection failure without changing legacy math."""
    return {'policy':FOLD_POLICY,'stage':stage,'source_sha256':analysis.source.get('preset_sha256'),
            'status':'unknown','index':{'policy':POLICY,'root_node_id':None,'complete':False,
                'unique_nodes':0,'semantic_edges':0,'node_budget':None,'unknown_barriers':0,
                'unknown_reasons':[reason],'object_identities_persisted':False},
            'candidates':[],'absence_proved':False,'inspection_complete':False,
            'quantitative_bounds_eligible':False,'phase_value_range':None,
            'visible_motion_speed':None,'fundamental_cell_area_uv2':None,
            'unknown_reasons':[reason],'uses_rendered_images':False,
            'uses_shader_execution':False,'uses_equation_execution':False,
            'conditions':['Optional structural inspection failed; existing fold fields and unknowns are retained']}


def outer_fold_evidence(field, analysis, *, stage, index=None):
    """Run auxiliary work privately; only immutable/root-bound results are shared."""
    from effect_families import _CACHE
    if stage is not None and stage not in {'warp','composite'}:raise ValueError('shader stage required')
    if index is None:
        try:index=field_index(field,stage=stage)
        except (ValueError,RecursionError,OverflowError) as error:
            return unknown_fold_evidence(analysis,stage=stage,reason='typed index inspection unresolved: '+str(error))
    if index.root is not field:raise ValueError('index must be bound to this field root')
    token=_CACHE.set(index._work_cache)
    try:return _inspect_outer_folds(field,analysis,stage=stage,index=index)
    finally:_CACHE.reset(token)


def _inspect_outer_folds(field, analysis, *, stage, index):
    """Report local source fold structure while leaving phase math unqualified."""
    from source_forms import known_invalid_phase_offset
    if stage is not None and stage not in {'warp','composite'}:raise ValueError('shader stage required')
    if index is None:
        try:index=field_index(field,stage=stage)
        except (ValueError,RecursionError,OverflowError) as error:
            return unknown_fold_evidence(analysis,stage=stage,reason='typed index inspection unresolved: '+str(error))
    if index.root is not field:raise ValueError('index must be bound to this field root')
    selected=analysis.stages[stage] if stage is not None else {
        'kind':'unknown','conditional_on_native_profile':True,'reason':'caller shader stage unspecified'}
    result={'policy':FOLD_POLICY,'stage':stage,'source_sha256':analysis.source.get('preset_sha256'),
            'status':'unknown','index':index.summary(),'candidates':[],
            'absence_proved':False,'inspection_complete':True,'quantitative_bounds_eligible':False,
            'phase_value_range':None,'visible_motion_speed':None,
            'fundamental_cell_area_uv2':None,'unknown_reasons':[],
            'uses_rendered_images':False,'uses_shader_execution':False,'uses_equation_execution':False,
            'conditions':['Local typed source structure before phase projection, finite-domain/rate and live material proofs',
                          'Native stage selection, casts, zero-product domain and persistent/loop semantics remain authoritative',
                          'No range, repeat lattice, visible copy, speed, flashing or activity claim follows from a capture']}
    if selected['kind'] not in {'custom_'+str(stage),'unknown'}:

        result['status']='not_contributing';return result
    rule_failures=[]
    for key in index.query('abs'):
        node=index.node(key)
        cache_key=(key,'outer_abs_frac')
        try:
            if cache_key not in index._rule_cache:index._rule_cache[cache_key]=_outer_match(node)
        except (ValueError,RecursionError,OverflowError) as error:
            rule_failures.append('outer fold rule inspection unresolved: '+str(error))
            continue
        match=index._rule_cache[cache_key]
        if match is None:continue
        phase=match['phase']
        saved=index._phase_domain_cache.get(id(phase))
        if saved is None or saved[0] is not phase:
            domain='unqualified';domain_reasons=[]
            index._phase_domain_inspections+=1
            try:
                if known_invalid_phase_offset(phase,preserve_zero_products=True):
                    domain='known_invalid';domain_reasons.append('original phase has a known invalid numeric domain')
                else:domain_reasons.append('opaque phase finite domain, scalar projection and response bounds remain unqualified')
            except (ValueError,RecursionError,IndexError,OverflowError) as error:
                domain_reasons.append('opaque phase validity remains unresolved: '+str(error))
            index._phase_domain_cache[id(phase)]=(phase,domain,domain_reasons)
        else:_,domain,domain_reasons=saved
        reasons=list(domain_reasons)
        if selected['kind']=='unknown':reasons.append('native custom/fallback stage selection unresolved')
        phase_id=index.node_id(phase)
        candidate={k:v for k,v in match.items() if k not in {'wrapped','phase'}}
        candidate.update(kernel_node_id=key,wrapped_node_id=index.node_id(match['wrapped']),
                         phase_node_id=phase_id,phase_dtype=phase.dtype,source_graph_path=index.path(key),
                         phase_is_opaque=True,phase_scalar_projection_performed=False,
                         phase_domain_status=domain,quantitative_bounds_eligible=False,
                         native_selection_verified=(selected['kind']=='custom_'+str(stage) and
                                                    analysis.stages.get('native_driver_verified') is True),
                         native_source_branch=selected['kind'],
                         conditional_on_native_profile=selected.get('conditional_on_native_profile',False),
                         unknown_reasons=reasons)
        result['candidates'].append(candidate)
    result['index']=index.summary()
    result['unknown_reasons']=result['index']['unknown_reasons']+rule_failures
    result['inspection_complete']=index.complete and not rule_failures
    if result['candidates'] and index.complete:
        result['status']='structural_candidates' if result['inspection_complete'] else 'partial_structural_candidates'
    elif result['inspection_complete'] and not index.summary()['unknown_barriers']:result['status']='no_supported_structure_detected'
    return result
