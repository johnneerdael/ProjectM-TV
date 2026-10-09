import sys,json,time,hashlib,copy,platform
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/milk-analyzer').resolve()))
from forecast import read_source,model_file_hashes,forecast_source,CORE_2331_EQUATION_RNG_POLICY
from corpus_inputs import prepare_inputs
from corpus_worker import compatibility_for,material_inputs,random_uniforms
from shape_sampling import native_blur_level
from stage_resolution import resolve_stages
from analyzer_test_profiles import validator_path
root=Path.cwd();binaries=root/'build/preset-corpus/source31/adapters';models=model_file_hashes()
inputs=root/'build/preset-corpus/program-reuse/long-inputs'
manifest=prepare_inputs(inputs,binaries=binaries,textures=root/'core/src/main/assets/textures',frames=60,fps=15,seed=12345)
manifest=json.loads((inputs/'manifest.json').read_text());audio=json.loads((inputs/'audio.json').read_text())
profile=json.loads((root/'tools/milk-analyzer/profiles/published-core-v2.3.31.json').read_text())
aar=root/'build/preset-corpus/published31'/profile['asset']
assert hashlib.sha256(aar.read_bytes()).hexdigest()==profile['aar_sha256']
path=root/'core/src/main/assets/presets/Geiss - Confetti (Kaleidoscope Mix).milk'
source=read_source(path,reader=binaries/'milk-native-reader')
assert source['parser_inputs']['engine']==profile['source_engine']
compat,refs=compatibility_for(source,binaries,validator_path())
materials=material_inputs(source,refs,manifest,binaries,inputs,12345)
random=random_uniforms(source,compat,audio,binaries,12345)
stages=resolve_stages(source,profile='gles300',compatibility=compat)
domain={'width':854,'height':480,'mesh_x':48,'mesh_y':32,'profile':'gles300','simulation_fps':15,
        'initial_rgba':[0]*4,'hue_offsets':[0]*4,'equation_seed':0x4141f00d,
        'equation_rng_policy':CORE_2331_EQUATION_RNG_POLICY,'equation_loader_policy':'projectmtv-core-2.2.8-v1',
        'equation_timeout_seconds':60,'blur_levels':native_blur_level(source,stages),'quantize':True,
        'line_rendering_profile':'projectmtv-gles-quad-lines-v1','warp_subpixel_bits':8,'triangle_subpixel_bits':8,
        'point_subpixel_bits':8,'composite_subpixel_bits':8,
        'texture_sampling_profile':'apple-m4pro-gles-unorm8-fixed8-fraction4-volume-v1',
        'motion_uv_storage_profile':'portable-half-nearest-v1','motion_uv_sampling_profile':'portable-half-bilinear-v1',
        'motion_uv_backend':'conditional','shader_numeric_policy':'gles300-highp-infinity-v1',
        'declared_random_profile':{'policy':'corpus-declared-inputs-v1','seed':12345,
           'lifecycle':'fresh isolated preset; explicit assets and independent deterministic shader uniform stream'}}
reports={};trials=[];reference_hashes=None;reference_features=None
for trial,policy in enumerate(['per-frame-v1','cached-program-v1','cached-program-v1','per-frame-v1']):
    hashes=[];start=time.perf_counter()
    def capture(frame):
        hashes.append([hashlib.sha256(frame[key].tobytes()).hexdigest() for key in ['feedback','display']])
        if len(hashes)%30==0:print(json.dumps({'trial':trial,'policy':policy,'updates':len(hashes),'seconds':time.perf_counter()-start}),flush=True)
    report=forecast_source(source,audio=audio,binaries=binaries,domain={**domain,'shader_lowering_policy':policy},
        compatibility=compat,materials=materials,random_inputs=random,retain_surfaces=False,on_frame=capture)
    elapsed=time.perf_counter()-start
    features=report['source_features']['features']
    if reference_hashes is None:reference_hashes=hashes;reference_features=features
    assert hashes==reference_hashes and features==reference_features
    trials.append({'trial':trial,'policy':policy,'seconds':elapsed,
                   'program_work':report['frames'][-1]['history']['shader_program_work']})
    reports[policy]={'input_hashes':report['input_hashes'],'provenance':report['provenance']}
    print(json.dumps(trials[-1]),flush=True)
assert model_file_hashes()==models
seconds={policy:[r['seconds'] for r in trials if r['policy']==policy] for policy in reports}
result={'scope':'One authored preset,60source updates at15fps854x480, four order-balanced trials; no native capture or corpus speed claim',
        'preset':path.name,'preset_sha256':source['preset_sha256'],'domain':domain,'trials':trials,
        'median_speedup':float(np.median(seconds['per-frame-v1'])/np.median(seconds['cached-program-v1'])),
        'pixel_bits_equal_all_trials':True,'all47_feature_objects_equal_all_trials':True,
        'pixel_hashes':reference_hashes,'features':reference_features,'reports':reports,
        'published_profile':profile,'python':platform.python_version(),'model_modules':models,
        'measurement_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
Path('build/preset-corpus/program-reuse/forecast-long-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:result[k] for k in ['scope','median_speedup','pixel_bits_equal_all_trials','all47_feature_objects_equal_all_trials']}),flush=True)
