"""One isolated offline preset simulation. No AI service, device or native renderer."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import time

from corpus_store import atomic_json,file_hash,digest
from corpus_inputs import declared_random_assets,sampler_request,verify_inputs
from forecast import read_source,forecast_source,model_file_hashes,CORE_2329_EQUATION_RNG_POLICY,CORE_2331_EQUATION_RNG_POLICY,_MODEL_IMPORT_HASHES
from engine_profiles import CORE_2329_ENGINE,CORE_2331_ENGINE
from effect_families import analyze_families,POLICY as EFFECT_POLICY,_IMPORT_MODEL_HASHES as _FAMILY_IMPORT_HASHES
from materials import MaterialBank
from noise_inputs import NoiseBank
from shader_compat import check_shader
from shader_random import execute_ledger
from shape_sampling import native_blur_level
from stage_resolution import resolve_stages
from sampling_policy import texture_settings


def target_policies(config):
    engine=config.get('source_engine',CORE_2329_ENGINE)
    if engine==CORE_2331_ENGINE:return engine,CORE_2331_EQUATION_RNG_POLICY
    if engine==CORE_2329_ENGINE:return engine,CORE_2329_EQUATION_RNG_POLICY
    raise ValueError('unsupported corpus source engine')


def effect_metadata(source,compatibility,*,cache=None):
    """Cache static metadata by actual parsed inputs and selected compatibility."""
    models=model_file_hashes()
    if models!=_MODEL_IMPORT_HASHES or models!=_FAMILY_IMPORT_HASHES:
        raise ValueError('static family model changed since import; start a fresh process')
    # Parser timing is not part of source semantics. Keep every other parsed
    # field and the complete actual target binding, including compiler status.
    semantic_source={key:value for key,value in source.items() if key!='elapsed_ms'}
    identity={'policy':EFFECT_POLICY,'source':digest(semantic_source),'compatibility':compatibility,
              'profile':'gles300','model_modules':models}
    key=digest(identity);path=None if cache is None else Path(cache)/(key+'.json')
    if path is not None and path.is_file():
        saved=json.loads(path.read_text())
        if saved.get('cache_key')!=key or saved.get('analysis_sha256')!=digest(saved.get('analysis')):
            raise ValueError('static effect metadata cache identity changed')
        return saved['analysis'],True
    try:
        analysis=analyze_families(source,profile='gles300',compatibility=compatibility)
        if not isinstance(analysis,dict) or not isinstance(analysis.get('families'),list) or not isinstance(analysis.get('unknowns'),list):
            raise TypeError('static analysis returned an invalid metadata record')
        analysis_hash=digest(analysis)
    except Exception as error:
        # A numeric result can remain valid when its separately exported static
        # analysis fails. Keep the failure explicit and never cache it as proof.
        return {'status':'error','error_type':type(error).__name__,'error':str(error),
                'analysis_policy':EFFECT_POLICY,'appearance_prediction_complete':False},False
    if model_file_hashes()!=identity['model_modules']:
        raise ValueError('static effect model changed during analysis')
    if path is not None:atomic_json(path,{'cache_key':key,'analysis':analysis,'analysis_sha256':analysis_hash})
    return analysis,False


def compatibility_for(source,binaries,validator):
    result={};references={}
    for stage,prefix in [('warp','warp_'),('composite','comp_')]:
        code=source.get('sections',{}).get(prefix,{}).get('source','')
        if not code:continue
        probe=check_shader(code,stage=stage,profile='gles300',translator=binaries/'milk-shader-translate',
            validator=validator,samplers={'sampler_main':'sampler2D'},texture_sizes=['texsize_main'])
        refs=probe['translation'].get('referenced_samplers',[])
        references[stage]=refs
        explicit=sampler_request(refs)
        # Keep every authored alias as well as the normalized native references.
        names=set(re.findall(r'\bsampler_([A-Za-z_][A-Za-z_0-9]*)',code)) - {'state'}
        explicit.update(sampler_request(names))
        sizes=sorted({'texsize_main'}|{'texsize_'+texture_settings(n)['texture'] for n in refs}|
                     {'texsize_'+n for n in re.findall(r'\btexsize_([A-Za-z_][A-Za-z_0-9]*)',code)})
        result[stage]=check_shader(code,stage=stage,profile='gles300',translator=binaries/'milk-shader-translate',
            validator=validator,samplers=explicit,texture_sizes=sizes)
    return result,references


def material_inputs(source,references,manifest,binaries,inputs,seed):
    images=manifest['textures']
    slots,aliases=declared_random_assets(references,images,preset_sha=source['preset_sha256'],seed=seed)
    needed=set(aliases.values())
    for refs in references.values():
        for ref in refs:
            name=texture_settings(ref)['texture'].lower()
            if name in {'main','blur1','blur2','blur3'} or name.startswith(('noise_','noisevol_')) or re.fullmatch(r'rand\d\d(?:_\w+)?',name):continue
            if name not in images:raise ValueError('shader texture input missing: '+name)
            needed.add(name)
    for key,value in source.get('values',{}).items():
        if re.fullmatch(r'shapecode_\d+_image',key.lower()) and value:
            name=texture_settings(value)['texture'].lower()
            if name not in images:raise ValueError('shape texture input missing: '+name)
            needed.add(name)
    noise=NoiseBank(inputs/'noise',upload_format='RGBA')
    bank=MaterialBank([images[n]['path'] for n in sorted(needed)],decoder=binaries/'milk-image-inputs',noise_bank=noise)
    for alias,name in aliases.items():
        bank.textures[alias]=bank.textures[name]
        bank.manifest['images'][alias]={**bank.manifest['images'][name],'declared_alias_of':name}
    bank.manifest['random_slots']={k:{'asset':v['name'],'file_sha256':v['sha256']} for k,v in slots.items()}
    bank.manifest['random_slot_policy']=manifest['random_texture_policy']
    return bank


def random_uniforms(source,compatibility,audio,binaries,seed):
    stages=resolve_stages(source,profile='gles300',compatibility=compatibility)
    active=[s for s in ('warp','composite') if stages[s]['kind'].startswith('custom_')]
    if not active:return None
    events=[{'kind':'construct','id':stage} for stage in active];bindings=[]
    for frame in audio['frames']:
        row={}
        for stage in active:
            row[stage]={'event_index':len(events),'shader_id':stage}
            events.append({'kind':'load','id':stage,'time':frame['time'],'frame':frame['frame'],'feedback_detail_alpha':-1.0})
        bindings.append(row)
    ledger=execute_ledger(binaries/'milk-shader-random',seed=seed,events=events,rand_policy='declared-mt19937-u31-v1')
    ledger['rendered_frames_consumed']=False
    return {'ledger':ledger,'bindings':bindings,'profile':ledger['profile']}


def run(job):
    import cv2
    cv2.setNumThreads(1)
    started=time.monotonic();stage='identity'
    config=job['configuration'];binaries=Path(config['binaries']);inputs=Path(config['inputs'])
    base={'schema_version':1,'export_kind':'preset-corpus-result','feature_record':None,
          'effect_analysis':None,'effect_analysis_cache_hit':False,
          'simulation':config['simulation'],'uses_rendered_reference':False,'appearance_accuracy_verified':False}
    try:
        from preset_corpus import verify_frozen
        verify_frozen(config)
        engine,rng_policy=target_policies(config)
        if file_hash(job['case']['path'])!=job['case']['sha256']:raise ValueError('preset input changed')
        manifest=json.loads((inputs/'manifest.json').read_text())
        stage='source_parse';source=read_source(Path(job['case']['path']),reader=binaries/'milk-native-reader')
        stage='identity'
        if source['parser_inputs']['engine']!=engine:raise ValueError('actual source engine differs from configured corpus identity')
        if source['reader_sha256']!=config['binary_sha256']['milk-native-reader']:
            raise ValueError('actual source parser differs from frozen adapter identity')
        if ('source_engine_archive_sha256' in config and
                source['parser_inputs']['engine_archive_sha256']!=config['source_engine_archive_sha256']):
            raise ValueError('actual source adapter archive differs from configured identity')
        raw=Path(job['case']['path']).read_bytes()
        if source['preset_sha256']!=job['case']['sha256'] or hashlib.sha256(raw).hexdigest()!=job['case']['sha256']:
            raise ValueError('preset changed during source parse')
        base['corpus_identity']={key:copy.deepcopy(config[key]) for key in
            ('source_engine','source_engine_archive_sha256','published_aar_sha256','engine_profile_sha256') if key in config}
        stage='compatibility';compatibility,references=compatibility_for(source,binaries,Path(config['validator']))
        source['numbered_source']=raw.decode('utf-8',errors='replace')
        stage='effect_analysis'
        base['effect_analysis'],base['effect_analysis_cache_hit']=effect_metadata(source,compatibility,cache=config.get('effect_cache'))
        stage='resources';materials=material_inputs(source,references,manifest,binaries,inputs,config['seed'])
        audio=json.loads((inputs/'audio.json').read_text())
        stage='random_inputs';random=random_uniforms(source,compatibility,audio,binaries,config['seed'])
        stages=resolve_stages(source,profile='gles300',compatibility=compatibility)
        blur=native_blur_level(source,stages)
        sim=config['simulation']
        domain={'width':sim['width'],'height':sim['height'],'mesh_x':48,'mesh_y':32,'profile':'gles300',
            'simulation_fps':sim['fps'],'initial_rgba':[0]*4,'hue_offsets':[0]*4,'equation_seed':0x4141f00d,
            'equation_rng_policy':rng_policy,'equation_loader_policy':'projectmtv-core-2.2.8-v1',
            'equation_timeout_seconds':config['equation_timeout'],'blur_levels':blur,'quantize':True,
            'line_rendering_profile':'projectmtv-gles-quad-lines-v1','warp_subpixel_bits':8,
            'triangle_subpixel_bits':8,'point_subpixel_bits':8,'composite_subpixel_bits':8,
            'texture_sampling_profile':'apple-m4pro-gles-unorm8-fixed8-fraction4-volume-v1',
            'motion_uv_storage_profile':'apple-m4pro-gles-rg16f-rtz-finite-v1',
            'shader_numeric_policy':'gles300-highp-infinity-v1',
            'declared_random_profile':{'policy':'corpus-declared-inputs-v1','seed':config['seed'],
                'lifecycle':'fresh isolated preset; explicit assets and independent deterministic shader uniform stream'}}
        if engine==CORE_2331_ENGINE:
            domain.update(motion_uv_storage_profile='portable-half-nearest-v1',
                          motion_uv_sampling_profile='portable-half-bilinear-v1',motion_uv_backend='conditional')
        stage='simulation';report=forecast_source(source,audio=audio,binaries=binaries,domain=domain,
            compatibility=compatibility,materials=materials,random_inputs=random,retain_surfaces=False)
        record=report['source_features']
        if len(record['features'])!=47:raise ValueError('existing47-field exporter returned a different key count')
        base.update(status='computed',stage='completed',feature_record=record,
            known_features=sum(f['status']=='computed' for f in record['features'].values()),
            unknown_features=sum(f['status']=='unknown' for f in record['features'].values()),
            stage_resolution=report['stage_resolution'],prediction_basis=report['prediction_basis'],
            random_assets=materials.manifest.get('random_slots',{}),
            notes=['Sampled15fps simulation; no native30fps equivalence or no-flash proof',
                   'Unknown features retain null; no AI/model API involved'])
    except (ValueError,KeyError,TypeError,ArithmeticError) as error:
        base.update(status='unsupported',stage=stage,error_type=type(error).__name__,error=str(error))
    except Exception as error:
        base.update(status='error',stage=stage,error_type=type(error).__name__,error=str(error))
    base['elapsed_seconds']=time.monotonic()-started
    return base


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--job',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();job=json.loads(args.job.read_text());atomic_json(args.output,run(job))

if __name__=='__main__':main()
