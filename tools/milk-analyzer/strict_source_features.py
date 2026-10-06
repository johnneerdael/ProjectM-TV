"""Isolated source-program queries and frame-free equation/geometry extraction.

No framebuffer construction, optical flow or captured image inputs. Missing
feedback, material, diffuse, random and shader-domain inputs remain unknown.
"""
import copy
import hashlib
from pathlib import Path

import numpy as np

from field_math import evaluate,UnresolvedMath
from palette_features import palette_summary
from shader_fields import ShaderFields
from shader_uniforms import source_uniforms
from geometry_features import scene_geometry_features
from scene_equations import execute_scene
from stage_resolution import resolve_stages
from source_features import geometry_feature_record,_feature,_record,STRICT
from scene_warp import warp_fields
from engine_profiles import select_policy,CORE_2315_ZOOM,LEGACY_ZOOM
from forecast import digest,model_file_hashes,PRODUCTION_EQUATION_SEED,PRODUCTION_EQUATION_ENGINES,_MODEL_IMPORT_HASHES


def input_dependencies(expression):
    """Collect ordinary DAG inputs; conservatively flag hidden loop plan reads."""
    pending=[expression];seen=set();names=set();hidden=False;textures=False
    while pending:
        node=pending.pop()
        if id(node) in seen:continue
        seen.add(id(node))
        if node.op=='input':names.add(node.detail['name'])
        if node.op.startswith('loop_'):hidden=True
        if node.op=='sample':textures=True
        pending.extend(node.args)
    return names,hidden,textures


def colour_queries(expression,query_inputs,*,max_queries=128):
    if type(max_queries) is not int or max_queries<=0:raise ValueError('positive query budget required')
    if not isinstance(query_inputs,list) or not query_inputs or len(query_inputs)>max_queries:
        raise ValueError('nonempty query list within declared budget required')
    if any(not isinstance(inputs,dict) for inputs in query_inputs):raise ValueError('declared query input dictionaries required')
    names,hidden,textures=input_dependencies(expression)
    spatial=bool(names&{'_uv','_rad_ang','_vDiffuse','_uv_orig'}) or hidden or textures
    report={'status':'unknown','basis':STRICT,'uses_display_fields':False,
            'query_count':len(query_inputs),'max_queries':max_queries,
            'dependencies':sorted(names),'hidden_plan_dependencies':hidden,
            'spatially_uniform':not spatial,'coverage_kind':
                'source expression independent of spatial/texture inputs' if not spatial else
                'isolated shader queries; screen area unproved',
            'rgb_queries':None,'palette':None,'unknown_reasons':[]}
    try:
        rgb=[]
        for inputs in query_inputs:
            value=np.asarray(evaluate(expression,inputs=inputs),dtype=np.float32)
            if value.shape!=(3,) or not np.all(np.isfinite(value)):
                raise UnresolvedMath('finite shader RGB return required')
            rgb.append(np.clip(value,0,1))
        palette=palette_summary(np.asarray(rgb))
    except (UnresolvedMath,ValueError,TypeError) as error:
        report['unknown_reasons']=[str(error)]
        return report
    report.update(status='computed',rgb_queries=np.asarray(rgb).tolist(),palette=palette)
    return report


def strict_features(source,*,audio,binaries,domain,compatibility):
    """Execute source equations and selected custom-composite scalar queries.

    UVs are explicit shader-input query points, not raster pixel centers.
    Polar, interpolated diffuse, feedback and random/material values are not
    guessed. This initial path does not establish full-preset motion or no-flash.
    """
    model_hashes=model_file_hashes()
    if model_hashes!=_MODEL_IMPORT_HASHES:raise ValueError('source model changed since import; start a fresh process')
    source=copy.deepcopy(source);audio=copy.deepcopy(audio);domain=copy.deepcopy(domain)
    if audio.get('uses_rendered_reference') is not False or not audio.get('frames'):
        raise ValueError('source-generated audio/context required')
    profile=domain['profile'];width=domain['width'];height=domain['height']
    if any(type(value) is not int or value<=0 for value in (width,height)):raise ValueError('positive viewport required')
    engine=source.get('parser_inputs',{}).get('engine',{})
    archive=source['parser_inputs']['engine_archive_sha256']
    if audio.get('engine_archive_sha256')!=archive:raise ValueError('source/audio engine identity mismatch')
    policy=domain.get('equation_rng_policy','declared-seed-v1')
    if policy!='declared-seed-v1':
        expected=PRODUCTION_EQUATION_ENGINES.get(policy)
        if expected is None or any(engine.get(key)!=value for key,value in expected.items()):raise ValueError('equation engine policy mismatch')
        if domain['equation_seed']!=PRODUCTION_EQUATION_SEED:raise ValueError('production equation seed mismatch')
    reader=Path(binaries)/'milk-native-reader'
    reader_sha=hashlib.sha256(reader.read_bytes()).hexdigest()
    if source.get('reader_sha256')!=reader_sha:raise ValueError('source reader identity mismatch')
    loader=domain.get('equation_loader_policy','strict-raw-v1')
    scene=execute_scene(source,audio['frames'],reader=reader,width=width,height=height,
        mesh_x=domain['mesh_x'],mesh_y=domain['mesh_y'],seed=domain['equation_seed'],equation_loader_policy=loader)
    geometry=scene_geometry_features(scene)
    context={'input_hashes':{'preset_sha256':source['preset_sha256'],
        'parsed_source_sha256':digest({key:source[key] for key in ['values','sections','parser_inputs']}),
        'pcm_sha256':audio['pcm_sha256'],'audio_sha256':digest(audio),'domain_sha256':digest(domain),
        'compatibility_sha256':digest(compatibility),'random_sha256':None,'materials_sha256':None},
        'provenance':{'engine':engine,'engine_archive_sha256':archive,'reader_sha256':reader_sha,
                      'model_sha256':digest(model_hashes),'model_modules':model_hashes},'domain':domain}
    features=geometry_feature_record(geometry,context=context)['features']
    stages=resolve_stages(source,profile=profile,compatibility=compatibility)
    palette_rows=[];unknown=[];all_uniform=True
    queries=domain.get('shader_queries',[{'_uv':[.5,.5]}])
    if not isinstance(queries,list) or not queries or len(queries)>domain.get('max_shader_queries',128):
        raise ValueError('shader query budget exceeded or empty')
    if any(not isinstance(query,dict) or set(query)-{'_uv','_uv_orig','_rad_ang','_vDiffuse'} for query in queries):
        raise ValueError('shader queries may declare spatial inputs only; equation/audio uniforms cannot be overridden')
    warp_queries=domain.get('warp_queries',[[.25,.25],[.75,.25],[.5,.5],[.25,.75],[.75,.75]])
    displacements=[];warp_unknown=[]
    zoom_policy=select_policy(engine,domain.get('warp_zoom_policy'),current=CORE_2315_ZOOM,legacy=LEGACY_ZOOM)
    for index in range(len(scene['frames'])):
        try:
            warp=warp_fields(source,scene,index,query_uv=warp_queries,zoom_policy=zoom_policy)
            displacement=np.linalg.norm(warp['uv'].astype(np.float64)-np.asarray(warp_queries),axis=-1)
            displacements.extend(displacement.tolist())
        except (ValueError,TypeError) as error:warp_unknown.append(str(error))
    warp_support={'scope':'builtin warp mesh query map; custom shader changes/visibility not established',
                  'query_count_per_frame':len(warp_queries),'frames_required':len(scene['frames']),
                  'display_fields_constructed':False}
    for name,value in [('warp.query_displacement_mean',float(np.mean(displacements)) if displacements and not warp_unknown else None),
                       ('warp.query_displacement_maximum',max(displacements) if displacements and not warp_unknown else None)]:
        features[name]=_feature(value,'normalized viewport coordinates','source-point-query',support=warp_support,
            dependencies=['executed mesh equations','builtin warp vertex math','declared query positions'],
            unknown_reason='; '.join(dict.fromkeys(warp_unknown)) if warp_unknown else 'No supported warp queries')
    section=source.get('sections',{}).get('comp_',{})
    if stages['composite']['kind']=='custom_composite' and section.get('status')=='parsed':
        for index,frame in enumerate(scene['frames']):
            model=ShaderFields(stage='composite',frame=index,warp_reads_blur=False,
                frame_wrap=None,main_binding_policy='projectmtv-core-2.2.6-v1',
                global_input_policy=section.get('implicit_global_input_policy','strict-v1'),
                array_initializer_policy=section.get('array_initializer_policy','legacy-layout-v1'))
            expression=model.lower(section['tree'],language_extensions=section.get('language_extensions',[]),
                                   native_samplers=compatibility['composite']['request']['samplers'])
            if not model.complete:
                unknown.extend(model.unknown);continue
            names,hidden,_=input_dependencies(expression)
            try:
                common=source_uniforms(scene,index,names=None if hidden else names)
                result=colour_queries(expression,[{**common,**query} for query in queries],
                                      max_queries=domain.get('max_shader_queries',128))
            except (ValueError,TypeError) as error:
                unknown.append(str(error));continue
            if result['status']!='computed':unknown.extend(result['unknown_reasons']);continue
            all_uniform&=result['spatially_uniform']
            palette_rows.append(result['palette'])
    else:
        unknown.append('Final colour needs unsupported legacy/default/unknown composite or feedback state')
    supported=bool(palette_rows) and len(palette_rows)==len(scene['frames']) and all_uniform
    support={'scope':'preset-output' if supported else 'isolated shader queries',
             'domain_sha256':context['input_hashes']['domain_sha256'],
             'frames_sampled':len(palette_rows),'frames_required':len(scene['frames']),
             'query_count_per_frame':len(queries),'display_fields_constructed':False}
    values={}
    if supported:
        chromatic=sum(row['chromatic_weight'] for row in palette_rows)
        values['palette.warm_cool']=sum(row['warm_cool']*row['chromatic_weight'] for row in palette_rows
            if row['warm_cool'] is not None)/chromatic if chromatic else None
        values['palette.coloured_support']=float(np.mean([row['chromatic_support'] for row in palette_rows]))
        bins=[row['effective_hue_bins'] for row in palette_rows if row['effective_hue_bins'] is not None]
        values['palette.effective_hue_bins']=float(np.mean(bins)) if bins else None
    units={'palette.warm_cool':'warm/cool sector coordinate −1…1','palette.coloured_support':'screen fraction',
           'palette.effective_hue_bins':'effective hue bins'}
    for name,unit in units.items():
        features[name]=_feature(values.get(name),unit,'source-point-query',support=support,
            dependencies=['selected composite expression','declared equation/time/audio/query inputs'],
            unknown_reason='; '.join(dict.fromkeys(unknown)) if unknown else 'Spatial coverage or chromatic support not established')
    if model_file_hashes()!=model_hashes:raise ValueError('source model changed during extraction')
    record=_record(context,features,STRICT)
    record['limitations'].extend(['No complete motion/feedback transport or no-flash bound proof',
        'Spatial query colours are withheld from whole-preset palette scoring until independence is established'])
    record['record_sha256']=digest({key:value for key,value in record.items() if key!='record_sha256'})
    return record
