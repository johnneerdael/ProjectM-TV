"""Saved source-bound offline compiler evidence, never runtime certification."""
import copy
import re

from corpus_store import digest


def _sha(value):return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None


def validate_manifest(manifest,profile):
    if not isinstance(manifest,dict):raise ValueError('offline compile manifest must be an object')
    m=copy.deepcopy(manifest)
    if type(m.get('schema_version')) is not int or m['schema_version']!=1 or m.get('kind')!='source-offline-compatibility-set':
        raise ValueError('unsupported offline compile manifest schema')
    if m.get('profile')!=profile:raise ValueError('offline compile manifest profile mismatch')
    claimed=m.get('record_sha256');payload={k:v for k,v in m.items() if k!='record_sha256'}
    if not _sha(claimed) or digest(payload)!=claimed:raise ValueError('offline compile manifest hash mismatch')
    if m.get('native_driver_verified') is not False or m.get('runtime_texture_bindings_verified') is not False:
        raise ValueError('offline compile manifest cannot certify runtime/texture bindings')
    if not isinstance(m.get('binding_assumptions'),str) or not m['binding_assumptions'].strip():
        raise ValueError('explicit offline descriptor assumptions required')
    compilers=m.get('compiler_inputs',{})
    if not isinstance(compilers,dict) or any(not _sha(compilers.get(k)) for k in ('translator_sha256','validator_sha256')):
        raise ValueError('offline compiler identities required')
    if not isinstance(m.get('engine'),dict) or not _sha(m.get('engine_archive_sha256')):
        raise ValueError('offline source engine identity required')
    records=m.get('presets')
    if not isinstance(records,dict) or any(not _sha(k) or not isinstance(v,dict) for k,v in records.items()):
        raise ValueError('offline compile preset hash inventory invalid')
    return m


def compatibility_from_manifest(m,source):
    inputs=source['parser_inputs']
    if m['engine']!=inputs['engine'] or m['engine_archive_sha256']!=inputs['engine_archive_sha256']:
        raise ValueError('offline compile source engine/archive mismatch')
    records=m['presets'].get(source['preset_sha256'],{})
    if set(records)-{'warp','composite'}:raise ValueError('offline compile stage inventory invalid')
    for stage,report in records.items():
        if not isinstance(report,dict):raise ValueError('offline compile report must be an object')
        prefix='warp_' if stage=='warp' else 'comp_'
        code=source.get('sections',{}).get(prefix,{}).get('source','')
        request=report.get('request',{});translation=report.get('translation',{})
        if not isinstance(request,dict) or not isinstance(translation,dict):raise ValueError('offline request/translation must be objects')
        if report.get('native_driver_verified') is not False:raise ValueError('offline report cannot certify native driver behavior')
        import hashlib
        if report.get('source_sha256')!=hashlib.sha256(code.encode()).hexdigest() or request.get('code')!=code:
            raise ValueError('offline compile shader source mismatch')
        if request.get('stage')!=stage or request.get('profile')!=m['profile']:
            raise ValueError('offline compile stage/profile mismatch')
        if any(report.get(k)!=m['compiler_inputs'][k] for k in ('translator_sha256','validator_sha256')):
            raise ValueError('offline compiler identity mismatch')
        accepted=report.get('offline_accepted')
        if accepted is not None and type(accepted) is not bool:raise ValueError('offline acceptance must be bool or null')
        status=translation.get('status')
        if status not in {'translated','rejected','unknown'}:raise ValueError('offline translation status invalid')
        if accepted is True and status!='translated' or accepted is False and status=='unknown' or accepted is None and status!='unknown':
            raise ValueError('offline acceptance/translation contradiction')
        if accepted is not None and (translation.get('engine')!=m['engine'] or
                translation.get('engine_archive_sha256')!=m['engine_archive_sha256'] or
                translation.get('profile')!=m['profile'] or translation.get('stage')!=stage):
            raise ValueError('offline translated engine/stage/profile mismatch')
        samplers=request.get('samplers');sizes=request.get('texture_sizes')
        if not isinstance(samplers,dict) or any(not isinstance(k,str) or not re.fullmatch('sampler_[A-Za-z_][A-Za-z_0-9]*',k) or
                v not in {'sampler2D','sampler3D'} for k,v in samplers.items()):
            raise ValueError('offline explicit sampler declarations invalid')
        if not isinstance(sizes,list) or any(not isinstance(v,str) or not re.fullmatch('texsize_[A-Za-z_][A-Za-z_0-9]*',v) for v in sizes):
            raise ValueError('offline explicit texsize declarations invalid')
    evidence={k:m[k] for k in ('record_sha256','profile','engine','engine_archive_sha256','compiler_inputs',
                               'binding_assumptions','native_driver_verified','runtime_texture_bindings_verified')}
    evidence['preset_record_present']=source['preset_sha256'] in m['presets']
    return records,evidence
