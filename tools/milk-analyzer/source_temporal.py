"""Nominal source oscillator timing; no time samples, shader execution or pixels."""
import math


def affine_time_parameters(field):
    """Return (slope, offset) for finite constant-affine scalar time, else None.

    Arithmetic describes the authored real-valued formula, not float32 rounding
    or shader-clock wrap events. Reject dynamic casts, state and other inputs.
    """
    from source_appearance import _canonical_lane,_phase_literal
    memo={};active=set()

    def visit(node,depth=0):
        key=id(node)
        if key in memo:return memo[key]
        if depth>64 or len(memo)+len(active)>=256 or key in active:return None
        active.add(key)
        try:result=calculate(node,depth)
        finally:active.remove(key)
        if result is not None and not all(math.isfinite(v) for v in result):result=None
        memo[key]=result
        return result

    def calculate(node,depth):
        node=_canonical_lane(node)
        op=node.op
        literal=_phase_literal(node)
        if literal is not None:return (0.,literal)
        if op=='constant':
            value=node.detail.get('value')
            if isinstance(value,(int,float)) and not isinstance(value,bool):
                return (0.,float(value)) if math.isfinite(value) else None
            return None
        if op=='unary' and node.dtype=='int' and node.detail.get('operator')==0:
            child=node.args[0]
            if child.op=='constant' and child.dtype=='int':
                value=child.detail.get('value')
                if type(value) is int and -(2**31)<value<2**31:return (0.,float(-value))
            return None
        if op=='input' and node.dtype=='float' and node.detail.get('name') in {'time',':native-render-time-f32'}:return (1.,0.)
        if op=='member' and node.dtype=='float' and node.detail.get('swizzle'):
            parent=node.args[0]
            if (node.detail.get('field') in {'x','r'} and parent.op=='input' and
                    parent.dtype=='float4' and parent.detail.get('name')=='_c2'):
                return (1.,0.)
            if parent.op not in {'input','sample'} and len(node.detail.get('field',''))==1:
                from effect_families import _parts
                from field_math import SWIZZLE
                parts=_parts(parent);index=SWIZZLE[node.detail['field']]
                if index<len(parts):
                    projected=parts[index]
                    if not (projected.op=='member' and projected.args and projected.args[0] is parent):
                        return visit(projected,depth+1)
            return None
        if node.dtype!='float':return None
        if op in {'cast','narrow','construct','components'} and len(node.args)==1:
            # Dynamic int/bool casts remain rejected by their own typed node.
            pair=visit(node.args[0],depth+1)
            if pair is not None and pair[0]==0 and op in {'cast','narrow','construct'}:
                import numpy as np
                with np.errstate(over='ignore',invalid='ignore'):offset=float(np.float32(pair[1]))
                return (0.,offset) if math.isfinite(offset) else None
            return pair
        if op in {'negate','unary'} and len(node.args)==1:
            pair=visit(node.args[0],depth+1)
            if pair is None:return None
            if op=='negate' or node.detail.get('operator')==0:return (-pair[0],-pair[1])
            if node.detail.get('operator')==1:return pair
            return None
        if op not in {'add','subtract','multiply','divide'} or len(node.args)!=2:return None
        a=visit(node.args[0],depth+1);b=visit(node.args[1],depth+1)
        if a is None or b is None:return None
        if op=='add':return (a[0]+b[0],a[1]+b[1])
        if op=='subtract':return (a[0]-b[0],a[1]-b[1])
        if op=='multiply':
            if a[0]!=0 and b[0]!=0:return None
            left=a[0]*b[1];right=b[0]*a[1]
            if (a[0]!=0 and b[1]!=0 and left==0 or b[0]!=0 and a[1]!=0 and right==0):return None
            return (left+right,a[1]*b[1])
        if b[0]!=0 or b[1]==0:return None
        rate=a[0]/b[1]
        if a[0]!=0 and rate==0:return None
        return (rate,a[1]/b[1])

    return visit(field)


def affine_shader_time_rate(field):
    pair=affine_time_parameters(field)
    return None if pair is None else pair[0]


def clock_kinds(field):
    from source_appearance import _packed_reads
    from effect_families import _deps
    names=_deps(field);result=[]
    if 'time' in names or 0 in _packed_reads(field).get('_c2',set()):result.append('shader_time_wrapped')
    if ':native-render-time-f32' in names:result.append('native_render_time_float32')
    return result


def oscillator_timing(oscillators):
    """Three RGB oscillator estimates; masks/storage/visibility remain separate."""
    rates=[affine_shader_time_rate(o['phase_expression']) for o in oscillators]
    clocks=[clock_kinds(o['phase_expression']) for o in oscillators]
    frequencies=[None if r is None else abs(r)/math.tau for r in rates]
    periods=[None if r in {None,0} else math.tau/abs(r) for r in rates]
    slopes=[None if r is None else abs(r*o['amplitude']) for r,o in zip(rates,oscillators)]
    # Very small/large finite source coefficients can overflow derived estimates.
    def finite(values):return [v if v is None or math.isfinite(v) else None for v in values]
    return {'policy':'nominal-affine-shader-time-v1',
        'scope':'unmasked source RGB oscillators within declared clock continuity domains' if any('native_render_time_float32' in c for c in clocks) else 'unmasked source RGB oscillators between shader-clock wraps',
        'angular_rate_rad_per_second_rgb':finite(rates),
        'cycle_frequency_hz_rgb':finite(frequencies),'period_seconds_rgb':finite(periods),
        'unmasked_component_slope_rgb_per_second':finite(slopes),
        'channel_status':['unknown' if r is None else 'constant' if r==0 else 'computed' for r in rates],
        'clock_kinds_rgb':clocks,'shader_time_wrap_seconds':10000 if any('shader_time_wrapped' in c for c in clocks) else None,'visible_flash_frequency_hz':None,
        'conditions':['Shader time resets at10000seconds; native roaming inputs use float32 render time before that wrapping',
                      'Nominal formula rates omit float32 quantization, discrete frame sampling and wrap discontinuities',
                      'Masks, textures, blend/storage and visibility can change final brightness behaviour'],
        'unknown_reasons_rgb':[None if r is not None else
            'phase is not a supported finite constant-affine shader-time expression' for r in rates]}
