"""Conservative main-Q interval proofs for simple native equation programs.

Unknown intervals stay unknown. This is not a replacement evaluator: supported
operators follow the pinned native bodies, and unsupported control/memory effects
prevent inference. No rendered input or preset-specific name rule is used.
"""
import math
import re
from equation_loading import select_equation

# These calls do not write variable storage. Unknown numerical results can still
# feed a native comparison, whose return is always finite zero or one.
CALLS={'_add','_sub','_mul','_div','_neg','_mod','rand',
       'above','below','equal','bnot','band','bor','abs','sin','cos','tan','pow','max','min'}
BOOLEAN={'above','below','equal','bnot','band','bor'}


def _program(tree):
    if tree is None:return []
    nodes=tree.get('instructions',[]) if tree.get('function')=='sequence' else [tree]
    def pure(node):
        if node.get('kind') in {'constant','variable'}:return True
        return (node.get('kind')=='call' and node.get('function') in CALLS and
                not node.get('instructions') and all(pure(a) for a in node.get('args',[])))
    if any(n.get('function')!='assign' or len(n.get('args',[]))!=2 or
           n['args'][0].get('kind')!='variable' or not pure(n['args'][1]) for n in nodes):return None
    return nodes


def _value(node,state):
    if node['kind']=='constant':
        if not isinstance(node['value'],(int,float)):return None
        x=float(node['value']);return (x,x) if math.isfinite(x) else None
    if node['kind']=='variable':return state.get(node['name'].lower())
    name=node['function'];args=[_value(a,state) for a in node.get('args',[])]
    if name in BOOLEAN:return (0,1)
    if name=='rand':
        a=args[0]
        if a is not None and a[0]==a[1] and 1<=a[0]<=2147483647:
            # Native genrand_int32 / UINT32_MAX can reach the upper endpoint.
            return (0,math.floor(a[0]))
        return None
    if any(a is None for a in args):return None
    if name=='_neg':result=(-args[0][1],-args[0][0])
    elif name=='_add':result=(args[0][0]+args[1][0],args[0][1]+args[1][1])
    elif name=='_sub':result=(args[0][0]-args[1][1],args[0][1]-args[1][0])
    elif name=='_mul':
        values=[x*y for x in args[0] for y in args[1]];result=(min(values),max(values))
    elif name=='_mod':
        a,b=args
        if not (0<=a[0]<=a[1]<=2147483647 and b[0]==b[1] and
                b[0]==int(b[0]) and 1<=b[0]<=2147483647):return None
        # Native signed integer remainder after truncation. This rule requires
        # nonnegative, bounded input, not GLSL floating-point mod semantics.
        result=(0,min(int(a[1]),int(b[0])-1))
    else:return None
    return result if all(math.isfinite(x) for x in result) else None


def _execute(program,state):
    state=dict(state)
    for node in program:
        state[node['args'][0]['name'].lower()]=_value(node['args'][1],state)
    return state


def main_q_domains(source,*,policy):
    """Prove bounded frame outputs using an init-containing inductive state.

    Growing bounds widen to unknown. Returning a domain requires a stable
    inductive state; a few observed frames never establish an invariant.
    Per-pixel mutation and non-straight-line effects remain unsupported.
    """
    sections=source.get('sections',{})
    for prefix,section in sections.items():
        if prefix not in {'warp_','comp_'} and select_equation(section,prefix,policy=policy)['compile_status'] not in {'accepted','omitted'}:return {}
    programs={}
    def uses_register(node):
        if isinstance(node,list):return any(uses_register(n) for n in node)
        if not isinstance(node,dict):return False
        if node.get('kind')=='variable' and re.fullmatch(r'reg[0-9]{2}',node['name'],re.I):return True
        return any(uses_register(n) for n in node.values())
    for prefix in ['per_frame_init_','per_frame_','per_pixel_']:
        selected=select_equation(sections.get(prefix),prefix,policy=policy)
        if selected['compile_status']=='omitted':program=[]
        elif selected['compile_status']!='accepted' or selected['tree_status']!='parsed':return {}
        else:program=_program(selected['tree'])
        if program is None or uses_register(selected['tree']):return {}
        programs[prefix]=program
    if programs['per_pixel_']:return {}
    state=_execute(programs['per_frame_init_'],{f'q{i}':(0,0) for i in range(1,33)})
    # Mirror the reset names already used by scene equation orchestration.
    # Configuration and frame inputs remain unknown without explicit bounds;
    # main Q values reload their init snapshot, custom variables persist.
    from source_context import FRAME_INPUTS
    reset_names=set(FRAME_INPUTS)
    q_defaults={f'q{i}':state.get(f'q{i}') for i in range(1,33)}
    growth={}
    for _ in range(16):
        inputs={**state,**{name:None for name in reset_names},**q_defaults}
        output=_execute(programs['per_frame_'],inputs);joined={}

        for name in state.keys()|output.keys():
            prior=state.get(name);new=output.get(name)
            bound=None if prior is None or new is None else (min(prior[0],new[0]),max(prior[1],new[1]))
            if bound!=prior:
                growth[name]=growth.get(name,0)+1
                if growth[name]>1:bound=None
            joined[name]=bound
        if joined==state:
            return {f'q{i}':output[f'q{i}'] for i in range(1,33) if output.get(f'q{i}') is not None}
        state=joined
    return {}


def q_uniform_domains(source,*,policy):
    """Pack proven post-frame main Q domains without guessing other lanes."""
    result={}
    for name,bounds in main_q_domains(source,policy=policy).items():
        index=int(name[1:])-1
        result.setdefault('_q'+chr(ord('a')+index//4),{})[index%4]=bounds
    return result
