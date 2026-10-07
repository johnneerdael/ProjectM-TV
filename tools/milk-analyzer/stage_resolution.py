"""Native stage selection from file settings and source-bound offline evidence."""
import hashlib
import re
from scene_equations import source_settings,_scalar


def contains_sampler_state(value):
    if isinstance(value,list):return any(contains_sampler_state(v) for v in value)
    if not isinstance(value,dict):return False
    return value.get('kind')=='sampler_state' or any(contains_sampler_state(v) for v in value.values())


def resolve_stages(source:dict,*,profile:str,compatibility:dict)->dict:
    if profile not in {'glsl330','gles300'}:raise ValueError('explicit target profile required')
    values=source_settings(source);version=_scalar(values,'MILKDROP_PRESET_VERSION',100,'int')
    result={'profile':profile,'native_driver_verified':False,'appearance_prediction_complete':False}
    for name,prefix in [('warp','warp_'),('composite','comp_')]:
        key='PSVERSION' if version==200 else 'PSVERSION_'+('WARP' if name=='warp' else 'COMP')
        level=0 if version<200 else _scalar(values,key,2,'int')
        code=source.get('sections',{}).get(prefix,{}).get('source','')
        stage={'shader_version':level,'source_sha256':hashlib.sha256(code.encode()).hexdigest(),
               'conditional_on_native_profile':False,
               'source_contains_clip': 'clip' in code}
        if level<=0:
            stage.update(kind='fixed_warp' if name=='warp' else 'legacy_composite',reason='file-level shader version disabled')
        elif not code:
            stage.update(kind='fixed_warp' if name=='warp' else 'default_composite',reason='empty shader code')
        else:
            evidence=compatibility.get(name,{})
            request=evidence.get('request',{});translation=evidence.get('translation',{})
            identity=(evidence.get('source_sha256')==stage['source_sha256'] and
                      request.get('code')==code and request.get('stage')==name and request.get('profile')==profile)
            archive=source.get('parser_inputs',{}).get('engine_archive_sha256')
            if archive and translation.get('engine_archive_sha256')!=archive:identity=False
            accepted=evidence.get('offline_accepted')
            if not identity or accepted is None:
                stage.update(kind='unknown',reason='missing, stale or unresolved target compatibility evidence')
            elif accepted is True:
                section=source.get('sections',{}).get(prefix,{})
                scanner_hash=translation.get('sampler_reference_body_sha256','')
                references=translation.get('referenced_samplers')
                scanner_bound=(isinstance(scanner_hash,str) and re.fullmatch('[0-9a-f]{64}',scanner_hash) is not None
                               and translation.get('status')=='translated' and isinstance(references,list)
                               and 'main' in references and all(isinstance(value,str) and
                                   re.fullmatch('[A-Za-z0-9_]+',value) for value in references))
                if contains_sampler_state(section.get('tree',[])) and not scanner_bound:
                    stage.update(kind='unknown',reason='sampler-state acceptance lacks native reference-scan provenance')
                else:stage.update(kind='custom_'+name,reason='offline target accepted',conditional_on_native_profile=True)
            elif accepted is False:
                stage.update(kind='fixed_warp' if name=='warp' else 'default_composite',
                             reason='offline target rejected',conditional_on_native_profile=True)
            else:stage.update(kind='unknown',reason='invalid compatibility result')
        result[name]=stage
    return result
