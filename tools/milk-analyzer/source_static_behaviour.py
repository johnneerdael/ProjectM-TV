"""Join source activity producers for conditional, frame-free preferences."""
import hashlib
import json
import math
from pathlib import Path

POLICY='source-static-behaviour-v1'
DEFAULT_CONTEXT={'viewport':[1920,1080], 'feedback_fps':30., 'reference_profile':'declared-home-tv-reference'}


def _digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,allow_nan=False).encode()).hexdigest()


def validate_context(request=None):
    request=dict(DEFAULT_CONTEXT if request is None else request)
    if set(request)-{'viewport','feedback_fps','reference_profile','scalar_input_domains'}:
        raise ValueError('unsupported static behaviour context field')
    viewport=request.get('viewport');fps=request.get('feedback_fps')
    if not isinstance(viewport,(list,tuple)) or len(viewport)!=2 or any(type(v) is not int or not 0<v<2**31 for v in viewport):
        raise ValueError('two positive int32 viewport dimensions required')
    if type(fps) not in {int,float} or not math.isfinite(fps) or not 0<fps<=1000:
        raise ValueError('finite positive feedback FPS up to1000 required')
    domains=request.get('scalar_input_domains',{})
    if not isinstance(domains,dict):raise ValueError('declared scalar input domains must be an object')
    for name,span in domains.items():
        if not isinstance(name,str) or not name or not isinstance(span,(list,tuple)) or len(span)!=2 or any(
                type(v) not in {int,float} or not math.isfinite(v) for v in span) or span[0]>span[1]:
            raise ValueError('finite ordered static input domain required')
    result={'viewport':list(viewport),'feedback_fps':float(fps),
            'reference_profile':request.get('reference_profile','caller-declared-reference'),
            'scalar_input_domains':{name:list(span) for name,span in sorted(domains.items())}}
    if not isinstance(result['reference_profile'],str) or not result['reference_profile']:
        raise ValueError('named declared reference profile required')
    return result


def _complete(analysis,flashing,motion):
    """Initial complete scope: selected custom RGB independent of stored images.

    Other paths remain productive partial evidence. Absence of a listed hazard
    never closes the feedback/audio/storage model for them.
    """
    if analysis.stages['composite']['kind']!='custom_composite':return False
    if getattr(analysis,'unknowns',[]):return False
    if analysis.stages['composite'].get('source_contains_clip'):return False
    final=[r for r in flashing['records'] if r['component_id']=='shader_composite']
    if not final or any(not r['total_brightness_rate_known'] for r in final):return False
    if flashing['source_hazards']:return False
    return not motion['unresolved_contributors']


def static_behaviour(analysis,description,context=None):
    from effect_families import _CACHE,_SemanticBudget
    from source_flash_behaviour import flash_evidence
    from source_motion_behaviour import motion_evidence
    from source_prominence import prominence_evidence
    from static_behaviour_scoring import score_static_behaviour
    from source_colour_character import colour_character
    normalized=validate_context(context)
    token=_CACHE.set({}) if _CACHE.get() is None else None
    try:
        result={'policy':POLICY,'context':normalized,'context_sha256':_digest(normalized),
                'preset_sha256':analysis.source.get('preset_sha256'),
                'engine':analysis.source.get('parser_inputs',{}).get('engine'),
                'model_sources':{name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                for name in ['source_static_behaviour.py','source_flash_behaviour.py',
                                             'source_motion_behaviour.py','source_prominence.py','source_colour_character.py','static_behaviour_scoring.py']},
                'uses_rendered_images':False,'uses_shader_execution':False,'uses_equation_execution':False,
                'native_numeric_certified':False,'appearance_accuracy_verified':False}
        result['flashing']=flash_evidence(analysis,description,normalized)
        result['motion']=motion_evidence(analysis,description,normalized)
        result['prominence']=prominence_evidence(analysis,description,normalized)
        result['colour']=colour_character(analysis,description,result['prominence'],normalized)
        result['output_model_complete']=_complete(analysis,result['flashing'],result['motion'])
        result['classification']=score_static_behaviour(result)
        result['limitations']=['Reference viewport/FPS/input domains are declared assumptions, not device observations',
            'Physical component bounds and source potential estimates are not rendered appearance or native certification',
            'Remaining feedback/audio/state/composition gaps remain explicit and can prevent automatic mood eligibility']
        result['record_sha256']=_digest(result)
        return result
    except (_SemanticBudget,RecursionError,OverflowError,ValueError,IndexError) as error:
        return {'policy':POLICY,'context':normalized,'context_sha256':_digest(normalized),
                'status':'unresolved','unknown_reasons':[str(error)],
                'uses_rendered_images':False,'uses_shader_execution':False,'uses_equation_execution':False,
                'output_model_complete':False,'appearance_accuracy_verified':False}
    finally:
        if token is not None:_CACHE.reset(token)
