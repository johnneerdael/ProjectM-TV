"""Nominal source-time threshold/floor schedules; no sampled event detection."""
import math

from source_triggers import REVERSE


def _clock(field):
    from effect_families import _deps
    names=_deps(field)
    if ':native-render-time-f32' in names:return 'native_render_time_float32'
    if 'time' in names:return 'equation_time'
    return 'shader_time_wrapped'


def _linear_transfer(root,target):
    from source_appearance import _phase_terms,_phase_literal
    from effect_families import _same,_walk
    if any(node.op in {'cast','narrow','construct'} and node.dtype in {'int','bool'} for node,path in _walk(root)):
        return None
    gain=0.;bias=0.
    try:terms=_phase_terms(root)
    except ValueError:return None
    for coefficient,node in terms:
        literal=_phase_literal(node)
        if literal is not None:bias+=coefficient*literal
        elif _same(node,target):gain+=coefficient
        else:return None
    return (gain,bias) if all(math.isfinite(v) for v in (gain,bias)) else None


def time_switch_events(field):
    from effect_families import _walk,_CACHE
    from source_appearance import _phase_literal,_data_return,_digest
    from source_temporal import affine_time_parameters
    from source_motion import motion_control
    cache=_CACHE.get();key=('time_switch_events',id(field))
    if cache is not None and key in cache and cache[key][0] is field:return cache[key][1]
    root=_data_return(field);events=[];seen=set()
    for index,(node,path) in enumerate(_walk(root)):
        if index>=2048 or len(events)>=32:break
        event=None
        if (node.op=='floor' or node.op=='int' and node.dtype=='float') and len(node.args)==1:
            pair=affine_time_parameters(node.args[0])
            if pair is None or pair[0]==0:continue
            rate,offset=pair;period=1/abs(rate)
            if not math.isfinite(period) or period==0:continue
            transfer=_linear_transfer(root,node)
            jump=None if transfer is None else abs(transfer[0])
            if jump==0:continue
            event={'event_kind':'affine_time_floor_steps','period_seconds':period,
                'floor_operator_kind':'EEL int/floor real floor' if node.op=='int' else 'real floor',
                'nominal_event_rate_hz':abs(rate),'events_per_period':1,
                'predicate_true_fraction':None,'event_offsets_seconds_mod_period':None,
                'absolute_control_jump':jump,'whole_control_levels_known':False,
                'clock_kind':_clock(node.args[0]),'signed_phase_rate_per_second':rate,'phase_offset':offset}
        elif node.op in REVERSE and len(node.args)==2:
            op=node.op;osc=node.args[0];threshold=_phase_literal(node.args[1])
            if threshold is None:
                threshold=_phase_literal(node.args[0]);osc=node.args[1];op=REVERSE[op]
            if threshold is None:continue
            curve=motion_control(osc,'predicate','source scalar',application='source comparison',_include_switch_events=False)
            if curve['curve_kind']!='sinusoidal_time':continue
            bias=curve['offset_value'];amplitude=curve['amplitude_value']
            if amplitude==0 or curve['nominal_value_range'][0]==curve['nominal_value_range'][1]:continue
            level=(threshold-bias)/amplitude
            if not math.isfinite(level) or not -1<level<1:continue
            if amplitude<0:op=REVERSE[op]
            omega=curve['angular_phase_rate_rad_per_second'];phase=curve['phase_offset_rad'];period=curve['period_seconds']
            greater=op in {'greater','greater_equal'}
            duty=math.acos(level)/math.pi
            if not greater:duty=1-duty
            if curve['oscillator_function_code']==1:roots=[math.acos(level),math.tau-math.acos(level)]
            else:
                a=math.asin(level);roots=[a%math.tau,(math.pi-a)%math.tau]
            offsets=None
            try:
                values=[((r-phase)/omega)%period for r in roots]
                if all(math.isfinite(v) for v in values) and values[0]!=values[1]:offsets=sorted(values)
            except (ValueError,OverflowError,ZeroDivisionError):pass
            jump=None;whole=False;yes=no=None
            if root is node:yes,no=1.,0.;whole=True
            elif root.op=='select' and root.args[0] is node:
                yes,no=map(_phase_literal,root.args[1:]);whole=yes is not None and no is not None
            if whole:
                jump=abs(yes-no)
                if jump==0:continue
                if not math.isfinite(jump):jump=None;whole=False
            frequency=2/period
            if not math.isfinite(frequency) or frequency==0:continue
            event={'event_kind':'periodic_threshold_crossing','period_seconds':period,
                'nominal_event_rate_hz':frequency,'events_per_period':2,
                'predicate_true_fraction':duty,'event_offsets_seconds_mod_period':offsets,
                'absolute_control_jump':jump,'whole_control_levels_known':whole,
                'control_true_value':yes if whole else None,'control_false_value':no if whole else None,
                'clock_kind':_clock(osc),'signed_phase_rate_per_second':omega,'phase_offset':phase,
                'normalized_oscillator_threshold':level,'normalized_comparison':op}
        if event is None:continue
        event.update(policy='source-nominal-time-switch-sites-v1',source_graph_path=path,
            scope='complete scalar control' if event['whole_control_levels_known'] else 'contributing source site; whole-control transfer unresolved',
            visible_flash_frequency_hz=None,
            conditions=['Nominal continuous source time and finite arithmetic; source clock resets/wrap and native comparison rounding excluded',
                        'Source site is reached and later control transfer/coverage/composition retain the change',
                        'Frame sampling can miss or alias events; a source schedule is not a measured visible pulse or flash'],
            events_are_exhaustive=False)
        identity=_digest({k:v for k,v in event.items() if k!='source_graph_path'})
        if identity not in seen:seen.add(identity);events.append(event)
    if cache is not None:cache[key]=(field,events)
    return events
