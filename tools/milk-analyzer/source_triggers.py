"""Contributing direct-band comparison sites, without audio or frame execution."""
REVERSE={'greater':'less','less':'greater','greater_equal':'less_equal','less_equal':'greater_equal'}


def direct_band(node):
    from source_appearance import AUDIO,PACKED,_canonical_lane
    node=_canonical_lane(node)
    if node.op=='input' and node.dtype=='float':return AUDIO.get(node.detail.get('name'))
    if node.op=='member' and node.dtype=='float' and node.detail.get('swizzle'):
        parent=node.args[0];name=parent.detail.get('name');lane=node.detail.get('field','')
        if parent.op=='input' and parent.dtype=='float4' and name in PACKED and len(lane)==1:
            index='xyzw'.find(lane)
            if index<0:index='rgba'.find(lane)
            if index>=0:return PACKED[name][index]
    return None


def switch_triggers(field,input_code):
    """Site evidence; only a complete direct scalar switch gets control levels."""
    from effect_families import _walk
    from source_appearance import _data_return,_phase_literal,_expression,_digest
    from field_math import typed
    root=_data_return(field)
    float_coercion=False
    while root.op=='cast' and root.dtype=='float' and (root.args[0].dtype in {'float','bool'} or
            root.args[0].dtype=='int' and root.args[0].op=='select'):
        float_coercion=True
        root=root.args[0]
    events=[];seen=set()
    for node,path in _walk(root):
        if node.op not in REVERSE or len(node.args)!=2:continue
        # Strict self comparisons are false even for NaN; no finite-input
        # assumption is borrowed to simplify non-strict self comparisons.
        if node.op in {'greater','less'} and direct_band(node.args[0]) is not None and \
                direct_band(node.args[0])==direct_band(node.args[1]):continue
        op=node.op;threshold=None
        if direct_band(node.args[0])==input_code:threshold=node.args[1]
        elif direct_band(node.args[1])==input_code:
            threshold=node.args[0];op=REVERSE[op]
        if threshold is None:continue
        yes=no=None;scope='contributing comparison site; whole control levels unresolved'
        if root is node:
            yes,no=1.,0.;scope='complete scalar comparison control'
        elif root.op in {'select','_if'} and root.args[0] is node:
            yes,no=(_phase_literal(root.args[1]),_phase_literal(root.args[2]))
            if float_coercion:
                yes=None if yes is None else float(typed(yes,'float'))
                no=None if no is None else float(typed(no,'float'))
            scope='complete scalar conditional control'
            if yes is not None and no is not None and yes==no:continue
        event={'policy':'direct-band-switch-sites-v1','input_code':input_code,'comparison':op,
            'threshold_value':_phase_literal(threshold),'threshold_expression':_expression(threshold),
            'control_true_value':yes,'control_false_value':no,
            'absolute_control_jump':None if yes is None or no is None else abs(yes-no),
            'scope':scope,'trigger_frequency_hz':None,'source_graph_path':path,
            'conditions':['Band inputs and threshold permit a predicate change',
                          'Source execution terminates and the branch is reached',
                          'Later masks, composition and visibility retain any resulting change'],
            'limitations':['A comparison site is not a proven visible flash or threshold-crossing frequency']}
        key=_digest({k:v for k,v in event.items() if k!='source_graph_path'})
        if key not in seen:events.append(event);seen.add(key)
    return events
