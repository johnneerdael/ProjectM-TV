"""Validate source-bound random aliases without extrapolating host data to Android.

Selected images are inputs of one observed compiled pair, not predictions of a
future random selection. Binding validity and framebuffer/appearance status stay
separate. The default caller receives no credit without this context.
"""
import re
from sampling_policy import texture_settings


def verified_context(source,*,stage,profile,evidence,asset_metadata,policy_patch_sha256):
    digest=source.get('preset_sha256')
    valid_hash=lambda value:isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None
    if not valid_hash(digest) or not valid_hash(policy_patch_sha256):return None
    if (profile!='glsl330' or evidence.get('profile')!='host-real-GL-production-random-device-v1' or
            evidence.get('engine_patch_count')!=37 or evidence.get('patch_sha256')!=policy_patch_sha256):return None
    outcomes=[v for v in evidence.get('preset_results',[]) if v.get('preset_sha256')==digest]
    if len(outcomes)!=1:return None
    outcome=outcomes[0]
    if outcome.get('raw_source_parse')!='accepted' or outcome.get('custom_'+stage+'_compile')!='accepted':return None
    rows=[v for v in evidence.get('bindings',[]) if v.get('preset_sha256')==digest]
    if not rows:return None
    samplers={};selected={};slots={};units={};alias_keys=set()
    for row in rows:
        alias=row.get('requested_alias','')
        match=re.fullmatch(r'(?:[A-Za-z]{2}_)?rand([0-9]{2})(?:_([A-Za-z0-9_]+))?',alias)
        if match is None or int(match[1])>15:return None
        uniform='sampler_'+alias
        row_stage=row.get('stage')
        if row_stage not in {'warp','composite'} or (row_stage,uniform) in alias_keys:return None
        alias_keys.add((row_stage,uniform))
        if (row.get('uniform')!=uniform or row.get('slot')!=int(match[1]) or
                row.get('target')!=3553 or row.get('texsize_uniform')!='texsize_'+alias):return None
        if any(type(row.get(k)) is not int or not 1<=row[k]<=16384 for k in ['width','height']):return None
        if type(row.get('unit')) is not int or not 0<=row['unit']<32:return None
        asset_hash=row.get('asset_sha256','')
        if not isinstance(asset_hash,str) or re.fullmatch('[0-9a-f]{64}',asset_hash) is None:return None
        asset=asset_metadata.get(row.get('asset_path'),{})
        if not isinstance(asset,dict) or asset.get('sha256')!=asset_hash:return None
        if any(type(asset.get(k)) is not int or not 1<=asset[k]<=16384 for k in ['width','height']):return None
        if asset.get('loading_policy')=='soil2-multiply-alpha-no-resize':
            size=(asset['width'],asset['height'])
        elif asset.get('loading_policy')=='soil2-multiply-alpha-pot-ceil':
            # Observed host profile follows SOIL's NPOT-unavailable branch.
            # Preserve decoded dimensions; derive the declared upload dimensions.
            size=tuple(1<<(asset[k]-1).bit_length() for k in ['width','height'])
        else:return None
        if size!=(row['width'],row['height']):return None
        settings=texture_settings(uniform)
        if row.get('filter')!=(9729 if settings['linear'] else 9728):return None
        if row.get('wrap')!=(10497 if settings['wrap'] else 33071):return None
        identity=(row['asset_path'],row['asset_sha256'],row['width'],row['height'])
        if row['slot'] in slots and slots[row['slot']]!=identity:return None
        slots[row['slot']]=identity
        unit_key=(row_stage,row['unit'])
        binding=(identity,row['filter'],row['wrap'])
        if unit_key in units and units[unit_key]!=binding:return None
        units[unit_key]=binding
        if row_stage==stage:samplers[uniform]='sampler2D';selected[uniform]=dict(row)
    if not samplers:return None
    return {'samplers':samplers,'selected_assets':selected,'profile':profile,
            'context_scope':evidence.get('scope'),'full_render_gl_error':outcome.get('full_render_gl_error'),
            'appearance_verified':False,'random_selection_scope':'observed compiled pair only',
            'policy_patch_sha256':policy_patch_sha256}
