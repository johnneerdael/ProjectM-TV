import sys,json,time,tempfile,zipfile,hashlib,copy,platform
from pathlib import Path
from collections import Counter
import numpy as np
sys.path.insert(0,str(Path('tools/milk-analyzer').resolve()))
from forecast import read_source,model_file_hashes,forecast_source,CORE_2331_EQUATION_RNG_POLICY
from pipeline_fields import SourcePipeline
from corpus_worker import compatibility_for,material_inputs,random_uniforms
from shape_sampling import native_blur_level
from stage_resolution import resolve_stages
from analyzer_test_profiles import validator_path
from field_math import UnresolvedMath

root=Path.cwd();binaries=root/'build/preset-corpus/source31/adapters';reader=binaries/'milk-native-reader'
archive=Path('/Users/jneerdael/Downloads/ProjectM-TV-static-effects-review-100-2026-10-09/batch-000001.zip')
model_hashes=model_file_hashes();rows=[];started=time.perf_counter()
def snapshot(model,expression,current_frame):
    # Number the full DAG plus hidden loop plans; normalize only the explicit
    # source-frame offset. No expression/math/texture execution occurs here.
    nodes=[];plans=[];node_ids={};plan_ids={}
    def field(node):
        if id(node) in node_ids:return node_ids[id(node)]
        index=len(nodes);node_ids[id(node)]=index;nodes.append(None)
        detail=copy.deepcopy({k:v for k,v in node.detail.items() if k!='plan'})
        if node.op=='sample' and detail.get('frame') is not None:detail['frame']+=current_frame-model.frame
        if 'plan' in node.detail:detail['plan_index']=plan(node.detail['plan'])
        nodes[index]={'op':node.op,'dtype':node.dtype,'args':[field(a) for a in node.args],'detail':detail}
        return index
    def plan(p):
        if id(p) in plan_ids:return plan_ids[id(p)]
        index=len(plans);plan_ids[id(p)]=index;plans.append(None)
        plans[index]={'names':p.names,'condition':None if p.condition is None else field(p.condition),
            'updates':{name:field(value) for name,value in p.updates.items()},
            'effects':[field(e) for e in p.effects],'iteration_limit':p.iteration_limit}
        return index
    roots=[field(expression)]
    if model.stage=='warp' and '_mv_tex_coords' in model.environment:
        roots.append(field(SourcePipeline._motion_expression(model)))
    return hashlib.sha256(json.dumps({'roots':roots,'nodes':nodes,'plans':plans},sort_keys=True,separators=(',',':')).encode()).hexdigest()

with zipfile.ZipFile(archive) as z,tempfile.TemporaryDirectory() as folder:
    for item in z.namelist():
        if not item.startswith('presets/') or not item.endswith('.milk'):continue
        raw=z.read(item);path=Path(folder)/Path(item).name;path.write_bytes(raw)
        source=read_source(path,reader=reader)
        for name,prefix in [('warp','warp_'),('composite','comp_')]:
            section=source.get('sections',{}).get(prefix,{})
            row={'preset':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'stage':name,'status':section.get('status')}
            if section.get('status')=='parsed':
                args=dict(initial_feedback=np.zeros((18,32,4),np.float32),warp_reads_blur=False,blur_levels=0,
                          main_binding_policy='projectmtv-core-2.2.6-v1',
                          language_extensions={name:section.get('language_extensions',[])})
                policies={p:SourcePipeline(None,None,**args,shader_lowering_policy=p)
                          for p in ['per-frame-v1','cached-program-v1']}
                for p in policies.values():
                    p.global_input_policies[name]=section.get('implicit_global_input_policy','strict-v1')
                    p.array_initializer_policies[name]=section.get('array_initializer_policy','legacy-layout-v1')
                durations={};digests={}
                try:
                    for policy,p in policies.items():
                        times=[];hashes=[]
                        for frame in range(5):
                            p.frame=frame;t=time.perf_counter()
                            model,expr=p._lower_stage(section['tree'],name,1)
                            times.append(time.perf_counter()-t)
                            hashes.append(snapshot(model,expr,frame))
                        durations[policy]=times;digests[policy]=hashes
                    assert digests['per-frame-v1']==digests['cached-program-v1']
                    row.update(status='verified-lowering',seconds=durations,
                               normalized_graph_sha256=digests['per-frame-v1'],
                               reuse_work=policies['cached-program-v1']._program_work)
                except (ValueError,TypeError,UnresolvedMath,RecursionError) as error:
                    row.update(status='unresolved',error=str(error),error_type=type(error).__name__)
            rows.append(row)
        if len(rows)%40==0:print(json.dumps({'phase':'static-program-check','presets':len(rows)//2}),flush=True)
good=[r for r in rows if r['status']=='verified-lowering']
seconds={policy:sum(sum(row['seconds'][policy]) for row in good) for policy in ['per-frame-v1','cached-program-v1']}
census={'scope':'Same fixed100 pack sources; five lowerings per parsed stage, complete contributing DAG+hidden loop/motion graphs normalized for explicit sampler-frame offsets; no numerical execution or target compilation',
        'count':len(rows)//2,'statuses':dict(Counter(r['status'] for r in rows)),
        'seconds':seconds,'phase_speedup':seconds['per-frame-v1']/seconds['cached-program-v1'],
        'source_zip_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'reader_sha256':hashlib.sha256(reader.read_bytes()).hexdigest(),
        'model_modules':model_hashes,'rows':rows,'total_seconds':time.perf_counter()-started,
        'limitations':['Parsed stage is not evidence of native stage acceptance','Timing excludes parsing, mesh/equations/shader execution/descriptors','No automatic corpus routing or appearance credit']}
Path('build/preset-corpus/program-reuse/phase-results.json').write_text(json.dumps(census,indent=2))
print(json.dumps({k:v for k,v in census.items() if k not in {'model_modules','rows'}}),flush=True)

profile=json.loads((root/'tools/milk-analyzer/profiles/published-core-v2.3.31.json').read_text())
aar=root/'build/preset-corpus/published31'/profile['asset']
assert hashlib.sha256(aar.read_bytes()).hexdigest()==profile['aar_sha256']
controls=[]
for preset,width,height,count in [('Geiss - Confetti (Kaleidoscope Mix).milk',128,72,3),
                                ('flexi - a julia fractal for hexcollie.milk',128,72,3),
                                ('Geiss - Confetti (Kaleidoscope Mix).milk',854,480,2)]:
    inputs=root/'build/preset-corpus/uniform-reduction'/('real-preset-480p-check' if width==854 else 'real-preset-check')/'inputs'
    manifest=json.loads((inputs/'manifest.json').read_text());audio=json.loads((inputs/'audio.json').read_text())
    assert len(audio['frames'])==count
    path=root/'core/src/main/assets/presets'/preset;source=read_source(path,reader=reader)
    assert source['parser_inputs']['engine']==profile['source_engine']
    compat,refs=compatibility_for(source,binaries,validator_path())
    materials=material_inputs(source,refs,manifest,binaries,inputs,12345)
    random=random_uniforms(source,compat,audio,binaries,12345)
    stages=resolve_stages(source,profile='gles300',compatibility=compat)
    domain={'width':width,'height':height,'mesh_x':48,'mesh_y':32,'profile':'gles300',
        'simulation_fps':15,'initial_rgba':[0]*4,'hue_offsets':[0]*4,'equation_seed':0x4141f00d,
        'equation_rng_policy':CORE_2331_EQUATION_RNG_POLICY,'equation_loader_policy':'projectmtv-core-2.2.8-v1',
        'equation_timeout_seconds':60,'blur_levels':native_blur_level(source,stages),'quantize':True,
        'line_rendering_profile':'projectmtv-gles-quad-lines-v1','warp_subpixel_bits':8,
        'triangle_subpixel_bits':8,'point_subpixel_bits':8,'composite_subpixel_bits':8,
        'texture_sampling_profile':'apple-m4pro-gles-unorm8-fixed8-fraction4-volume-v1',
        'motion_uv_storage_profile':'portable-half-nearest-v1','motion_uv_sampling_profile':'portable-half-bilinear-v1',
        'motion_uv_backend':'conditional','shader_numeric_policy':'gles300-highp-infinity-v1',
        'declared_random_profile':{'policy':'corpus-declared-inputs-v1','seed':12345,
            'lifecycle':'fresh isolated preset; explicit assets and independent deterministic shader uniform stream'}}
    reports={};times={};snapshots={}
    for policy in ['per-frame-v1','cached-program-v1']:
        times[policy]=[]
        for trial in range(3):
            t=time.perf_counter()
            report=forecast_source(source,audio=audio,binaries=binaries,
                domain={**domain,'shader_lowering_policy':policy},compatibility=compat,materials=materials,
                random_inputs=random,retain_surfaces=True)
            times[policy].append(time.perf_counter()-t)
        reports[policy]=report
        snapshots[policy]=[[hashlib.sha256(frame[key].tobytes()).hexdigest() for key in ['feedback','display']]
                           for frame in report['frames']]
    assert snapshots['per-frame-v1']==snapshots['cached-program-v1']
    assert reports['per-frame-v1']['source_features']['features']==reports['cached-program-v1']['source_features']['features']
    controls.append({'preset':preset,'preset_sha256':source['preset_sha256'],'width':width,'height':height,'frames':count,
        'seconds':times,'median_speedup':float(np.median(times['per-frame-v1'])/np.median(times['cached-program-v1'])),
        'pixel_bits_equal':True,'all47_feature_objects_equal':True,'pixel_hashes':snapshots['per-frame-v1'],
        'reuse_work':reports['cached-program-v1']['frames'][-1]['history']['shader_program_work'],
        'input_hashes':reports['per-frame-v1']['input_hashes'],'domain':domain})
    print(json.dumps(controls[-1]),flush=True)
assert model_file_hashes()==model_hashes
result={'scope':'Three short paired source-model forecasts, three trials each; no native capture or whole-corpus timing/appearance certification',
        'published_profile':profile,'profile_sha256':hashlib.sha256((root/'tools/milk-analyzer/profiles/published-core-v2.3.31.json').read_bytes()).hexdigest(),
        'model_modules':model_hashes,'python':platform.python_version(),'controls':controls,
        'measurement_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
Path('build/preset-corpus/program-reuse/forecast-results.json').write_text(json.dumps(result,indent=2))
