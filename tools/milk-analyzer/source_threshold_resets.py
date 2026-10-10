"""Nominal boundary jumps of contributing top-level channel resets."""
import math


def channel_threshold_resets(projected,domains):
    from source_appearance import _phase_literal,_typed_control_identity
    from source_control_bounds import scalar_value_envelope,scalar_response_envelope
    from source_forms import known_invalid_phase_offset
    from source_time_switches import time_switch_events
    from source_polar import _nodes
    from shader_fields import Field
    memo={}
    def normalize(node,depth=0):
        if id(node) in memo:return memo[id(node)][1]
        if depth>64 or len(memo)>=1024:raise ValueError('threshold reset normalization budget exceeded')
        children=tuple(normalize(a,depth+1) for a in node.args)
        value=Field(node.op,children,node.dtype,node.detail)
        if value.op=='select' and len(children)==3:
            identity=_typed_control_identity(children[1])
            if identity is not None and identity==_typed_control_identity(children[2]):value=children[1]
        memo[id(node)]=(node,value);return value
    def schedule_clock(node):
        if node.op=='input' and node.detail.get('name')=='_c2.x':
            parent=Field('input',dtype='float4',detail={'name':'_c2'})
            return Field('member',(parent,),'float',{'field':'x','swizzle':True})
        return Field(node.op,tuple(schedule_clock(a) for a in node.args),node.dtype,node.detail)
    rows=[];reverse={'greater':'less','greater_equal':'less_equal','less':'greater','less_equal':'greater_equal'}
    for channel,field in zip('rgb',projected):
        if field.op!='select':continue
        original=field
        try:field=normalize(field)
        except (ValueError,RecursionError):continue
        if field.op!='select' or field.dtype!='float' or len(field.args)!=3:continue
        predicate,yes,no=field.args
        if predicate.op not in reverse or len(predicate.args)!=2:continue
        op=predicate.op;a,b=predicate.args;threshold=_phase_literal(b);signal=a
        if threshold is None:threshold=_phase_literal(a);signal=b;op=reverse[op]
        if threshold is None or not math.isfinite(threshold):continue
        signal_id=_typed_control_identity(signal)
        if signal_id is None:continue
        if _typed_control_identity(no)==signal_id:
            reset=_phase_literal(yes);reset_side='true'
        elif _typed_control_identity(yes)==signal_id:
            reset=_phase_literal(no);reset_side='false'
        else:continue
        if reset is None or not math.isfinite(reset):continue
        jump=abs(threshold-reset)
        if jump==0 or not math.isfinite(jump):continue
        try:
            if known_invalid_phase_offset(original,preserve_zero_products=True):continue
            names={n.detail.get('name') for n,p in _nodes(signal) if n.op=='input'}
            # A value interval alone does not establish approach to the boundary:
            # floor/casts can skip it completely. Reuse the continuous calculus
            # with every contributing input varied, rather than a blacklist.
            if not names or any(not isinstance(n,str) or not n for n in names):continue
            continuity=scalar_response_envelope(signal,input_names=names,input_domains=domains)
            if continuity['nominal_continuity'] not in {'smooth_nominal','piecewise_lipschitz'}:continue
            span=scalar_value_envelope(signal,input_domains=domains)['nominal_value_range']
            if span is not None and not span[0]<threshold<span[1]:continue
            image=any(isinstance(n,str) and n.startswith(':coordinate-sample-') for n in names)
            timed=bool(names&{'time',':native-render-time-f32','_c2.x'})
            events=time_switch_events(schedule_clock(predicate)) if timed else []
            rate=events[0]['nominal_event_rate_hz'] if len(events)==1 else None
            rows.append({'kind':'shader_channel_threshold_reset','channel':channel,'comparison':op,
                'threshold':threshold,'reset_value':reset,'reset_branch':reset_side,
                'absolute_nominal_boundary_jump':jump,'signal_value_range':span,
                'signal_nominal_continuity':continuity['nominal_continuity'],
                'threshold_inside_proved_range':span is not None,
                'trigger_source_kind':'sampled_image' if image else 'source_time' if timed else 'other_or_unresolved_input',
                'nominal_crossing_event_rate_hz':rate,'source_crossing_events':events,
                'visible_flashing_verified':False,'whole_frame_blackout_verified':False,
                'scope':'complete scalar raw-stage channel at a threshold boundary; temporal crossing/reachability unverified',
                'conditions':['Selected authored stage and finite supported signal/reset arithmetic under declared sample/input premises',
                    'A boundary jump requires the signal to cross the threshold; an enclosing interval does not prove reachability',
                    'Jump is a nominal limiting difference, not a discrete-frame sample difference or native-rounding guarantee',
                    'Sample-driven event timing depends on image/history/coordinate changes; no frequency is invented',
                    'One channel reset does not prove whole-frame blackout, visible flashing, screen prominence or a mood']})
        except (ValueError,RecursionError,OverflowError):continue
    return rows
