"""Optional proof evidence for actual typed scalar and main-frame source domains.

Nominal real proofs never amend native main-Q selector bounds. The explicit
binary32 expression model is a separate query, not a target/runtime certificate.
"""
from contextvars import ContextVar
import hashlib
import json
from pathlib import Path

from source_symbolic import SymbolicSession

ACTIVE = ContextVar('source_proof_component',default=None)
WORKER = Path(__file__).with_name('source_proofs_worker.py')


def active_identity():
    session=ACTIVE.get()
    return None if session is None else session.identity


class ProofSession(SymbolicSession):
    """Reuse the existing bounded transport without loading optional Z3 locally."""
    def __init__(self,python,*,timeout=1.,startup_timeout=10.,solver_timeout_ms=200):
        if type(solver_timeout_ms) is not int or not 1<=solver_timeout_ms<=2000:
            raise ValueError('bounded solver timeout required')
        super().__init__(python,timeout=timeout,startup_timeout=startup_timeout,
                         worker_path=WORKER,ready_message={'protocol':1,'z3_version':'5.1.0.0'})
        self.solver_timeout_ms=solver_timeout_ms
        self.identity={'policy':'source-z3-qualified-domain-evidence-v1','z3_version':'5.1.0.0',
                       'numeric_model':'nominal-real',
                       'worker_sha256':self.identity['worker_sha256'],'python':str(self.python),
                       'timeout_seconds':timeout,'solver_timeout_ms':solver_timeout_ms,
                       'nominal_literal_policy':'exact binary value after analyser float conversion',
                       'numeric_models':['nominal-real','ieee754-binary32-rne']}

    def __enter__(self):
        self.token=ACTIVE.set(self)
        return self

    def __exit__(self,*args):
        ACTIVE.reset(self.token)
        self.close()

    def prove(self,request):
        return super().query({**request,'solver_timeout_ms':self.solver_timeout_ms},[])


def _graph(field):
    from source_proofs_worker import validate_node
    nodes=[];memo={};active=set()
    def visit(node,depth=0):
        key=id(node)
        if key in active:raise ValueError('proof graph cycle')
        if key in memo:return memo[key]
        if depth>48 or len(nodes)>=128:raise ValueError('proof graph budget exceeded')
        validate_node({'op':node.op,'dtype':node.dtype,'args':node.args,'detail':node.detail})
        active.add(key);index=len(nodes);nodes.append(None);memo[key]=index
        args=[visit(a,depth+1) for a in node.args]
        nodes[index]={'op':node.op,'dtype':node.dtype,'args':args,'detail':node.detail}
        active.remove(key);return index
    root=visit(field)
    return {'root':root,'nodes':nodes}


def _evidence(request,session):
    model=request.get('numeric_model','nominal-real')
    result={'policy':session.identity['policy'],'backend':session.identity,
            'numeric_model':model,'native_numeric_certified':False,
            'uses_equation_execution':False,'uses_shader_execution':False,'uses_rendered_images':False,
            'conditions':['Explicit finite declaration domains and original pure supported scalar operations only',
                          'Nominal real bounds do not prove native rounding, overflow, state reachability or visible appearance',
                          'Binary32 RNE expression queries exclude target conversions, denorm policy and backend arithmetic qualification']}
    try:
        encoded=json.dumps(request,sort_keys=True,allow_nan=False).encode()
        result['request_sha256']=hashlib.sha256(encoded).hexdigest()
        response=session.prove(request)
        result.update(response)
        result['unknown_reasons']=(response.get('solver_unknown_reasons',[])
            if response['status'] in {'proven','bounded','mixed','refuted'} else [response.get('reason','unresolved solver query')])
    except (ValueError,TypeError,RecursionError,OverflowError) as error:
        result.update(status='unsupported',reason=str(error),unknown_reasons=[str(error)])
    return result


def _original_value_domain(field,input_domains,original_report):
    if original_report is None:
        from source_control_bounds import compound_time_bounds
        original_report=compound_time_bounds(field,_value_only=True,_input_domains=input_domains)
    permitted={'unsupported input, discontinuous operation or unproved denominator domain',
               'no finite source value envelope from supported formula'}
    errors=original_report.get('unknown_reasons',[])
    if any(error not in permitted for error in errors):
        raise ValueError('Original source value-domain failure retained: '+'; '.join(errors))
    return original_report


def scalar_value_evidence(field,*,input_domains=None,candidate_bounds=None,original_report=None):
    session=ACTIVE.get()
    if session is None:return None
    try:
        if original_report is None:
            from source_control_bounds import compound_time_bounds
            original_report=compound_time_bounds(field,_value_only=True,_input_domains=input_domains)
        _original_value_domain(field,input_domains,original_report)
        request={'task':'predicate' if field.dtype=='bool' else 'value','graph':_graph(field),'input_domains':input_domains or {},
                 'candidate_bounds':candidate_bounds,'numeric_model':'nominal-real'}
        result=_evidence(request,session)
        if field.dtype=='bool' and result['status'] in {'proven','mixed'}:
            result['predicate_status']=result['status']
            truth=result['truth_value']
            result.update(status='bounded',nominal_value_range=([0.,1.] if truth is None else [float(truth),float(truth)]))
    except (ValueError,TypeError,RecursionError,OverflowError) as error:
        result={'status':'unsupported','reason':str(error),'unknown_reasons':[str(error)],
                'native_numeric_certified':False,'backend':session.identity,'numeric_model':'nominal-real'}
    result.setdefault('nominal_value_range',None)
    result['original_value_domain']=original_report
    return result


def predicate_evidence(field,*,input_domains=None,numeric_model='nominal-real'):
    session=ACTIVE.get()
    if session is None:return None
    original_report=None
    try:
        from source_control_bounds import compound_time_bounds
        original_report=compound_time_bounds(field,_value_only=True,_input_domains=input_domains)
        _original_value_domain(field,input_domains,original_report)
        result=_evidence({'task':'predicate','graph':_graph(field),'input_domains':input_domains or {},
                          'numeric_model':numeric_model},session)
    except (ValueError,TypeError,RecursionError,OverflowError) as error:
        result={'status':'unsupported','reason':str(error),'unknown_reasons':[str(error)],
                'native_numeric_certified':False,'backend':session.identity,'numeric_model':numeric_model}
    result.setdefault('truth_value',None)
    result['original_value_domain']=original_report
    return result


def main_q_invariant_evidence(source,*,policy,candidates,input_domains=None):
    """Check candidate private-state induction with actual native reader trees."""
    session=ACTIVE.get()
    if session is None:return None
    from equation_loading import select_equation
    from equation_domains import _program
    import re
    def register(node):
        if isinstance(node,list):return any(register(n) for n in node)
        if not isinstance(node,dict):return False
        if node.get('kind')=='variable' and re.fullmatch(r'reg[0-9]{2}',node['name'],re.I):return True
        return any(register(n) for n in node.values())
    try:
        sections=source.get('sections',{})
        for prefix,section in sections.items():
            if prefix not in {'warp_','comp_'}:
                selected=select_equation(section,prefix,policy=policy)
                if selected['compile_status'] not in {'accepted','omitted'}:
                    raise ValueError('equation compile failure retained')
                if register(selected['tree']):raise ValueError('shared registers need cross-phase initialization adapter')
        programs={}
        for prefix in ('per_frame_init_','per_frame_','per_pixel_'):
            selected=select_equation(sections.get(prefix),prefix,policy=policy)
            if selected['compile_status']=='omitted':program=[]
            elif selected['compile_status']!='accepted' or selected['tree_status']!='parsed':
                raise ValueError('accepted parsed equation program required')
            else:program=_program(selected['tree'])
            if program is None:raise ValueError('equation effects/format excluded')
            programs[prefix]=program
        if programs['per_pixel_']:raise ValueError('per-pixel storage mutation excluded')
        from scene_equations import MAIN,READONLY
        reset_names=sorted(set(MAIN)|set(READONLY)|{'meshx','meshy','pixelsx','pixelsy','aspectx','aspecty'})
        result=_evidence({'task':'invariant','initialization':programs['per_frame_init_'],
                          'transition':programs['per_frame_'],'reset_names':reset_names,
                          'candidates':candidates,'input_domains':input_domains or {},
                          'equation_loader_policy':policy,'numeric_model':'nominal-real'},session)
        result['source_identity']={'preset_sha256':source.get('preset_sha256'),
                                   'parser_inputs':source.get('parser_inputs')}
        return result
    except (ValueError,KeyError,TypeError,RecursionError) as error:
        return {'status':'unsupported','reason':str(error),'unknown_reasons':[str(error)],
                'native_numeric_certified':False,'backend':session.identity,'numeric_model':'nominal-real'}
