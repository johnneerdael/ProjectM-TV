"""Uniform-controlled sinusoidal texture displacement from source algebra."""
import math
from fractions import Fraction
from shader_fields import Field

BASES=('_uv','_rad_ang')
COLUMNS=('_uv.x','_uv.y','_uv.z','_uv.w','_rad_ang.x','_rad_ang.y')


def uniform(field):
    from effect_families import _walk
    return not any(n.op in {'sample','unknown','uninitialized','sequence'} or n.op.startswith('loop_') or
        n.op=='input' and n.detail.get('name') in {*BASES,'_vDiffuse'} for n,p in _walk(field))


def number(v):return Field('constant',dtype='float',detail={'value':float(v)})


def combine(op,a,b):
    from source_appearance import _phase_literal
    x,y=_phase_literal(a),_phase_literal(b)
    if x is not None and y is not None:
        v=x+y if op=='add' else x*y
        if not math.isfinite(v):raise ValueError('periodic-map coefficient overflow')
        return number(v)
    if op=='add':
        if x==0:return b
        if y==0:return a
    else:
        if x==0 or y==0:return number(0)
        if x==1:return b
        if y==1:return a
    return Field(op,(a,b),'float')


def uniform_weighted_terms(field):
    """Distribute uniform weights only; never expand products of spatial fields."""
    result=[];active=set();visits=0
    def visit(node,weight,depth=0):
        nonlocal visits
        visits+=1
        if visits>512 or depth>64 or id(node) in active:raise ValueError('uniform-wave distribution node/depth budget exceeded')
        if len(result)>=64:raise ValueError('uniform-wave distribution exceeds64terms')
        active.add(id(node))
        try:
            if node.dtype=='float' and node.op in {'add','subtract'}:
                visit(node.args[0],weight,depth+1)
                visit(node.args[1],weight if node.op=='add' else combine('multiply',weight,number(-1)),depth+1)
            elif node.dtype=='float' and (node.op=='negate' or node.op=='unary' and node.detail.get('operator')==0):
                visit(node.args[0],combine('multiply',weight,number(-1)),depth+1)
            elif node.dtype=='float' and node.op=='multiply' and any(uniform(v) for v in node.args):
                i=0 if uniform(node.args[0]) else 1
                visit(node.args[1-i],combine('multiply',weight,node.args[i]),depth+1)
            elif node.dtype=='float' and node.op=='divide' and uniform(node.args[1]):
                visit(node.args[0],combine('multiply',weight,Field('divide',(number(1),node.args[1]),'float')),depth+1)
            else:result.append((weight,node))
        finally:active.remove(id(node))
    visit(field,number(1));return result


def uniform_affine_scalar(field):
    """Six declared spatial coefficients plus a uniform offset, all symbolic."""
    from source_appearance import _canonical_lane,_phase_literal
    from effect_families import _parts
    from field_math import SWIZZLE
    memo={};active=set()
    def zero():return [number(0) for _ in COLUMNS]
    def visit(original,depth=0):
        key=id(original)
        if key in memo:return memo[key][1]
        if depth>64 or len(memo)+len(active)>=512 or key in active:raise ValueError('uniform-affine phase budget/cycle exceeded')
        active.add(key)
        try:result=calculate(_canonical_lane(original),depth)
        finally:active.remove(key)
        memo[key]=(original,result);return result
    def scale(pair,factor):return [combine('multiply',v,factor) for v in pair[0]],combine('multiply',pair[1],factor)
    def calculate(node,depth):
        if node.dtype!='float':raise ValueError('spatial phase conversion is not scalar float')
        if node.op=='member' and node.detail.get('swizzle') and len(node.detail.get('field',''))==1:
            parent=node.args[0];lane=SWIZZLE[node.detail['field']]
            if parent.op=='input' and parent.detail.get('name') in BASES:
                name=parent.detail['name'];limit=2 if parent.dtype=='float2' else 4
                if parent.dtype not in {'float2','float4'} or name=='_rad_ang' and parent.dtype!='float2' or lane>=limit:raise ValueError('spatial phase lane/type unresolved')
                weights=zero();weights[(0 if name=='_uv' else 4)+lane]=number(1);return weights,number(0)
            if parent.op!='input':
                from source_sampling import _constant_matrix_vector_parts
                parts=_constant_matrix_vector_parts(parent) or _parts(parent)
                if lane<len(parts):
                    p=parts[lane]
                    if not (p.op=='member' and p.args and p.args[0] is parent):return visit(p,depth+1)
        if uniform(node):return zero(),node
        if node.op in {'cast','narrow','construct','components'} and len(node.args)==1 and node.args[0].dtype=='float':return visit(node.args[0],depth+1)
        if node.op=='negate' or node.op=='unary' and node.detail.get('operator')==0:return scale(visit(node.args[0],depth+1),number(-1))
        if node.op=='unary' and node.detail.get('operator')==1:return visit(node.args[0],depth+1)
        if node.op in {'add','subtract'}:
            a=visit(node.args[0],depth+1);b=visit(node.args[1],depth+1)
            if node.op=='subtract':b=scale(b,number(-1))
            return [combine('add',x,y) for x,y in zip(a[0],b[0])],combine('add',a[1],b[1])
        if node.op=='multiply':
            for i in (0,1):
                if uniform(node.args[i]):return scale(visit(node.args[1-i],depth+1),node.args[i])
        if node.op=='divide' and uniform(node.args[1]) and _phase_literal(node.args[1])!=0:
            return scale(visit(node.args[0],depth+1),Field('divide',(number(1),node.args[1]),'float'))
        if node.op=='dot' and len(node.args)==2:
            a,b=map(_parts,node.args)
            if len(a)!=len(b):raise ValueError('phase dot dimensions unresolved')
            result=(zero(),number(0))
            for x,y in zip(a,b):
                pair=visit(Field('multiply',(x,y),'float'),depth+1)
                result=([combine('add',v,w) for v,w in zip(result[0],pair[0])],combine('add',result[1],pair[1]))
            return result
        raise ValueError('phase is not uniform-affine in declared spatial inputs')
    return visit(field)


def oscillatory_displacement(field,analysis):
    from effect_families import _parts,_deps
    from source_appearance import _phase_literal,_expression,_digest,_routes
    from source_forms import known_invalid_phase_offset
    from source_motion import motion_control
    result={'policy':'source-uniform-periodic-sampling-v1','source_model':'unknown','basis':None,
        'base_matrix_uv4':None,'base_coefficient_programs':None,'base_offset_programs':None,'waves':[],
        'jacobian_perturbation_infinity_norm_upper_bound':None,
        'sufficient_no_fold_of_unwrapped_nominal_map':None,'actual_fold_present':None,
        'deformation_envelope':None,
        'visible_motion_speed':None,'unknown_reasons':[],
        'uses_equation_execution':False,'uses_shader_execution':False,'uses_rendered_images':False,
        'conditions':['Nominal unwrapped lookup map with uniform inputs fixed; all source domains/inputs/intermediates usable and finite',
                      'Frequency/amplitude programs can vary with audio/time/state; no guessed audio ranges or temporal rates',
                      'Spatial basis distinguishes mesh UV, original UV and supplied radial/angular varyings',
                      'No-fold sufficient condition is restricted to identity base and one UV basis with constant wave coefficients',
                      'Native precision/interpolation, wrapping/filtering, textures/history, later composition and perceived motion remain separate']}
    try:
        parts=_parts(field)
        if len(parts)!=2:raise ValueError('sampling displacement is not two-dimensional')
        base=[number(0),number(0)];waves={}
        for axis,lane in enumerate(parts):
            for coefficient,term in uniform_weighted_terms(lane):
                pending=[term];factors=[];osc=[]
                while pending:
                    n=pending.pop()
                    if n.op=='multiply':pending.extend(n.args)
                    elif n.op in {'sin','cos'} and not uniform(n):osc.append(n)
                    else:factors.append(n)
                    if len(pending)+len(factors)+len(osc)>64:raise ValueError('oscillatory product budget exceeded')
                if len(osc)==1 and all(uniform(n) for n in factors):
                    node=osc[0];gradient,offset=uniform_affine_scalar(node.args[0])
                    if all(_phase_literal(v)==0 for v in gradient):raise ValueError('oscillator has no proved spatial phase')
                    if known_invalid_phase_offset(node.args[0]):raise ValueError('oscillator phase has a known invalid domain')
                    amplitude=coefficient
                    for n in factors:amplitude=combine('multiply',amplitude,n)
                    if known_invalid_phase_offset(amplitude):raise ValueError('wave amplitude has a known invalid domain')
                    program=_expression(node)
                    if program is None:raise ValueError('wave expression export budget exceeded')
                    key=_digest(program)
                    if key not in waves:
                        if len(waves)>=32:raise ValueError('oscillatory wave count exceeds32')
                        waves[key]={'node':node,'gradient':gradient,'offset':offset,'amplitude':[number(0),number(0)]}
                    waves[key]['amplitude'][axis]=combine('add',waves[key]['amplitude'][axis],amplitude)
                else:base[axis]=combine('add',base[axis],combine('multiply',coefficient,term))
        if not waves:raise ValueError('no supported spatial oscillators')
        baselines=[uniform_affine_scalar(v) for v in base]
        # Check the untouched original graph only for a candidate map. Maps
        # already rejected by structural extraction need no repeated preflight.
        if known_invalid_phase_offset(field,preserve_zero_products=True):
            raise ValueError('sampling arithmetic has a known invalid source domain')
        if any(known_invalid_phase_offset(v) for pair in baselines for v in pair[0]+[pair[1]]):
            raise ValueError('sampling baseline has a known invalid domain')
        matrix=[[_phase_literal(v) for v in pair[0]] for pair in baselines]
        base_constant=all(v is not None for row in matrix for v in row)
        bases=set();rows=[];bound_rows=[Fraction(0),Fraction(0)];constant_waves=True
        for key,w in sorted(waves.items()):
            gradient=[_phase_literal(v) for v in w['gradient']];amp=[_phase_literal(v) for v in w['amplitude']]
            if all(v==0 for v in amp):continue
            for i,v in enumerate(w['gradient']):
                if _phase_literal(v)!=0:bases.add('shader_uv' if i<2 else 'original_uv' if i<4 else 'radial_angular_varyings')
            routes=[]
            for name,v in list(zip(('wave_amplitude_x','wave_amplitude_y'),w['amplitude']))+[(f'wave_frequency_{i}',v) for i,v in enumerate(w['gradient'])]+[('wave_phase',w['offset'])]:
                routes+=_routes(name,'source UV' if 'amplitude' in name else 'radian/declared basis unit' if 'frequency' in name else 'radian',v,analysis)
            programs=[_expression(v) for v in w['gradient']];amp_programs=[_expression(v) for v in w['amplitude']]
            if any(v is None for v in programs+amp_programs):raise ValueError('wave coefficient export budget exceeded')
            rows.append({'id':key,'oscillator':w['node'].op,'constant_amplitude_uv':amp if all(v is not None for v in amp) else None,
                'amplitude_uv_programs':amp_programs,'constant_phase_gradient':gradient if all(v is not None for v in gradient) else None,
                'phase_gradient_programs':programs,'phase_offset_program':_expression(w['offset']),
                'phase_motion_control':motion_control(w['offset'],'wave_phase','radian',application='texture-displacement phase'),
                'audio_routes':routes})
            if any(v is None for v in amp+gradient):constant_waves=False
            else:
                for i,a in enumerate(amp):bound_rows[i]+=abs(Fraction(a))*sum(abs(Fraction(k)) for k in gradient)
        if not rows:raise ValueError('all wave amplitudes are zero')
        basis=next(iter(bases)) if len(bases)==1 else 'mixed_spatial_bases'
        bound=None
        if constant_waves and basis in {'shader_uv','original_uv'}:
            exact=max(bound_rows);bound=float(exact)
            if Fraction(bound)<exact:bound=math.nextafter(bound,math.inf)
            if not math.isfinite(bound):raise ValueError('wave Jacobian bound overflow')
        identity=[[1,0,0,0,0,0],[0,1,0,0,0,0]] if basis=='shader_uv' else [[0,0,1,0,0,0],[0,0,0,1,0,0]]
        base_programs=[[_expression(v) for v in pair[0]] for pair in baselines]
        offset_programs=[_expression(pair[1]) for pair in baselines]
        if any(p is None for row in base_programs for p in row) or any(p is None for p in offset_programs) or any(w['phase_offset_program'] is None for w in rows):
            raise ValueError('periodic map program export budget exceeded')
        from source_ripple_envelopes import deformation_envelope
        envelopes=deformation_envelope([waves[w['id']] for w in rows],basis=basis,identity_baseline=matrix==identity)
        result.update(source_model='uniform_affine_plus_oscillators',basis=basis,
            base_matrix_uv4=[r[:4] for r in matrix] if base_constant and all(v==0 for r in matrix for v in r[4:]) else None,
            base_coefficient_programs=base_programs,base_offset_programs=offset_programs,waves=rows,
            jacobian_perturbation_infinity_norm_upper_bound=bound,
            sufficient_no_fold_of_unwrapped_nominal_map=bound<1 if bound is not None and matrix==identity else None,
            deformation_envelope=envelopes)
    except (ValueError,RecursionError,OverflowError,IndexError) as error:result['unknown_reasons']=[str(error)]
    result['phase_gradient_column_order']=list(COLUMNS)
    return result
