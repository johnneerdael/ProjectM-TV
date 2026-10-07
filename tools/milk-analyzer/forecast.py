"""Compose source-only forecasts under explicitly declared state and inputs.

This executes a mathematical source model; it does not claim validated native
appearance accuracy. Inputs are parser output, source-generated audio/assets,
initial state and optional source random lifecycle. No reference frames enter.
"""
import hashlib
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import numpy as np
from builtin_wave import source_builtin_wave
from custom_wave import source_custom_waves
from descriptors import DescriptorStream
from pipeline_fields import SourcePipeline
from scene_draw import draw_source_scene
from scene_equations import execute_scene
from scene_warp import warp_fields
from shader_random import bind_random_uniforms
from shader_uniforms import source_uniforms
from spatial import sample2d
from sampling_policy import texture_settings
from geometry_features import scene_geometry_features
from materials import material_input_identity
from source_features import forecast_feature_record, SIMULATED
from engine_profiles import (CORE_2315_ENGINE,CORE_2316_ENGINE,CORE_2315_SHAPE,CORE_2315_BLUR,CORE_2315_ZOOM,
    CORE_2315_DISPLAY,CORE_2315_WAVE,LEGACY_BLUR,LEGACY_ZOOM,LEGACY_DISPLAY,LEGACY_WAVE,matches,select_policy)
from shape_sampling import LEGACY as LEGACY_SHAPE_POLICY,CORE_238 as CORE_238_SHAPE_POLICY,native_blur_level,shape_sampling_modes

# Patched projectM-eval TreeFunctions.c initializes MT19937 once per thread.
# This policy covers a cold evaluator thread, not a later preset switch.
PRODUCTION_EQUATION_SEED = 0x4141f00d
PRODUCTION_EQUATION_RNG_POLICY = 'projectmtv-core-2.3.4-cold-thread-v1'
PRODUCTION_EQUATION_ENGINE = {
    'commit': 'e0b0a967f0ffd7d332106c366668ed271718472b',
    'patches_sha256': 'd21d4e3d9725178c000fd6f7ea5cd331389fb1100b70fce51341ece65d3fd818',
}
CORE_235_EQUATION_RNG_POLICY = 'projectmtv-core-2.3.5-cold-thread-v1'
CORE_235_EQUATION_ENGINE = {
    'commit': 'e0b0a967f0ffd7d332106c366668ed271718472b',
    'patches_sha256': 'd73c955a26380a502516e6ba3a18baf753851244de4de2e5a3083930766a539a',
}
CORE_237_EQUATION_RNG_POLICY = 'projectmtv-core-2.3.7-cold-thread-v1'
CORE_237_EQUATION_ENGINE = {
    'commit': 'e0b0a967f0ffd7d332106c366668ed271718472b',
    'patches_sha256': 'd70f5b5ec3f3c0b4da764cb824153f142b88e17e27c2e9e71d2b481c19998c7d',
}
CORE_2310_EQUATION_RNG_POLICY = 'projectmtv-core-2.3.10-cold-thread-v1'
CORE_2310_EQUATION_ENGINE = {
    'commit': 'e0b0a967f0ffd7d332106c366668ed271718472b',
    'patches_sha256': '545ca48adad787f963f9b29c1fc4fd7e8a71fb910f586c8747f96a075d130ddf',
}
CORE_2315_EQUATION_RNG_POLICY = 'projectmtv-core-2.3.15-cold-thread-v1'
CORE_2316_EQUATION_RNG_POLICY = 'projectmtv-core-2.3.16-cold-thread-v1'
# Patch0044 changes literal formatting; equation RNG and sampler ownership
# retain the verified43-patch contracts. Keep44 as a distinct source identity.
# Keep historical 2.3.4 identity. Patch 0042 adds feedback and shader random caching;
# the equation RNG's cold-thread seed remains unchanged.
PRODUCTION_EQUATION_ENGINES = {
    PRODUCTION_EQUATION_RNG_POLICY: PRODUCTION_EQUATION_ENGINE,
    CORE_235_EQUATION_RNG_POLICY: CORE_235_EQUATION_ENGINE,
    CORE_237_EQUATION_RNG_POLICY: CORE_237_EQUATION_ENGINE,
    CORE_2310_EQUATION_RNG_POLICY: CORE_2310_EQUATION_ENGINE,
    CORE_2315_EQUATION_RNG_POLICY: CORE_2315_ENGINE,
    CORE_2316_EQUATION_RNG_POLICY: CORE_2316_ENGINE,
}


def source_main_binding_policy(engine: dict, requested: str | None) -> str:
    """Use the verified engine's unit-zero contract unless explicitly overridden.

    Unknown sources retain the historical default. An explicit historical policy
    remains available for labeled diagnostics, not current-AAR certification.
    """
    if requested is not None:
        if requested not in {'legacy-sorted-v1','projectmtv-core-2.2.6-v1'}:
            raise ValueError('unsupported main binding policy')
        return requested
    if any(all(engine.get(key)==value for key,value in expected.items())
           for expected in PRODUCTION_EQUATION_ENGINES.values()):
        return 'projectmtv-core-2.2.6-v1'
    return 'legacy-sorted-v1'


def source_shape_sampler_policy(engine: dict, requested: str | None) -> str:
    if matches(engine):
        if requested is None or requested == CORE_2315_SHAPE:return CORE_2315_SHAPE
    elif requested == CORE_2315_SHAPE:
        raise ValueError('shape sampler engine identity mismatch')
    verified=any(all(engine.get(key)==value for key,value in expected.items())
                 for expected in (CORE_237_EQUATION_ENGINE,CORE_2310_EQUATION_ENGINE,CORE_2315_ENGINE,CORE_2316_ENGINE))
    policy=requested if requested is not None else CORE_238_SHAPE_POLICY if verified else LEGACY_SHAPE_POLICY
    if policy not in {LEGACY_SHAPE_POLICY,CORE_238_SHAPE_POLICY}:
        raise ValueError('unsupported shape sampler policy')
    if policy==CORE_238_SHAPE_POLICY and not verified:
        raise ValueError('shape sampler engine identity mismatch')
    return policy


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def model_file_hashes():
    return {path.name:hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(Path(__file__).parent.glob('*.py'))
            if not path.name.startswith('test_')}


_MODEL_IMPORT_HASHES=model_file_hashes()


def read_source(path: Path, *, reader: Path, timeout=30) -> dict:
    path=Path(path);reader=Path(reader).resolve()
    raw=path.read_bytes()
    reader_bytes=reader.read_bytes()
    binary_sha=hashlib.sha256(reader_bytes).hexdigest()
    # Execute the exact bytes hashed here, even if the workspace file changes.
    with tempfile.TemporaryDirectory(prefix='milk-forecast-source-') as directory:
        frozen=Path(directory)/path.name
        frozen.write_bytes(raw)
        executable_dir=Path(directory)/'adapter';executable_dir.mkdir()
        executable=executable_dir/'reader';executable.write_bytes(reader_bytes);executable.chmod(0o700)
        process=subprocess.run([str(executable),str(frozen)],capture_output=True,text=True,timeout=timeout)
    if process.returncode:
        raise ValueError('source parser execution failed: '+process.stderr.strip())
    result=json.loads(process.stdout)
    result.update(preset=path.name,preset_sha256=hashlib.sha256(raw).hexdigest(),reader_sha256=binary_sha)
    return result


def forecast_source(source: dict, *, audio: dict, binaries: Path, domain: dict,
                    compatibility: dict, random_inputs=None, noise_bank=None, materials=None,
                    retain_surfaces=True, on_frame=None) -> dict:
    model_hashes=model_file_hashes()
    if model_hashes!=_MODEL_IMPORT_HASHES:
        raise ValueError('forecast model files changed since import; start a fresh process')
    source=copy.deepcopy(source);audio=copy.deepcopy(audio);domain=copy.deepcopy(domain)
    compatibility=copy.deepcopy(compatibility)
    random_inputs=copy.deepcopy(random_inputs)
    noise_bank,materials=copy.deepcopy((noise_bank,materials))
    descriptors=DescriptorStream(warmup_frames=domain.get('descriptor_warmup_frames',0),
                                 settings=domain.get('descriptor_settings'),
                                 motion_window_policy=domain.get('motion_window_policy','legacy-supported-subset-v1'))
    required = {'width','height','mesh_x','mesh_y','profile','initial_rgba',
                'hue_offsets','equation_seed','blur_levels','quantize'}
    if not required.issubset(domain):
        raise ValueError('forecast domain missing explicit settings: ' + ', '.join(sorted(required-set(domain))))
    if domain.get('numeric_profile')=='apple-m4pro-gl41-nan-mesh-v1' and domain['profile']!='glsl330':
        raise ValueError('Apple numeric profile requires glsl330 shader backend')
    if type(domain['quantize']) is not bool or type(retain_surfaces) is not bool:
        raise ValueError('explicit boolean quantization/retention settings required')
    if domain.get('feedback_detail_alpha',-1.0)!=-1.0:
        raise ValueError('feedback detail alpha passes are not implemented in source forecasts')
    if type(domain['equation_seed']) is not int or not 0<=domain['equation_seed']<2**32:
        raise ValueError('explicit uint32 equation seed required')
    rng_policy = domain.get('equation_rng_policy', 'declared-seed-v1')
    if rng_policy != 'declared-seed-v1' and rng_policy not in PRODUCTION_EQUATION_ENGINES:
        raise ValueError('unknown equation RNG policy: ' + str(rng_policy))
    production_engine = PRODUCTION_EQUATION_ENGINES.get(rng_policy)
    if production_engine is not None and domain['equation_seed'] != PRODUCTION_EQUATION_SEED:
        raise ValueError('production equation RNG seed must be 0x4141f00d')
    engine = source.get('parser_inputs', {}).get('engine', {})
    main_binding_policy=source_main_binding_policy(engine,domain.get('main_binding_policy'))
    shape_sampler_policy=source_shape_sampler_policy(engine,domain.get('shape_sampler_policy'))
    blur_range_policy=select_policy(engine,domain.get('blur_range_policy'),current=CORE_2315_BLUR,legacy=LEGACY_BLUR)
    warp_zoom_policy=select_policy(engine,domain.get('warp_zoom_policy'),current=CORE_2315_ZOOM,legacy=LEGACY_ZOOM)
    legacy_control_policy=select_policy(engine,domain.get('legacy_control_policy'),current=CORE_2315_DISPLAY,legacy=LEGACY_DISPLAY)
    wave_control_policy=select_policy(engine,domain.get('wave_control_policy'),current=CORE_2315_WAVE,legacy=LEGACY_WAVE)
    if production_engine is not None:
        if any(engine.get(key) != value for key, value in production_engine.items()):
            raise ValueError('production equation RNG engine identity mismatch')
    if any(type(domain[k]) is not int or domain[k]<=0 for k in ['width','height']):
        raise ValueError('positive integer forecast viewport required')
    for version, expected in [('2.3.5',CORE_235_EQUATION_ENGINE),('2.3.7',CORE_237_EQUATION_ENGINE),
                              ('2.3.10',CORE_2310_EQUATION_ENGINE),('2.3.15',CORE_2315_ENGINE),('2.3.16',CORE_2316_ENGINE)]:
        # JNI enables patch 0042 only above height 1330 and changes the line reference
        # to 1280x720 there. Neither that feedback path nor scaled lines is modeled.
        if (all(engine.get(key)==value for key,value in expected.items()) and
                (domain['height']>1330 or domain['width']*domain['height']>1024*768)):
            raise ValueError(version+' higher-resolution lines/native feedback detail are not implemented')
    from quad_lines import PROFILE as quad_profile
    line_profile=domain.get('line_rendering_profile','canonical-gl-lines-v1')
    if line_profile not in {'canonical-gl-lines-v1',quad_profile}:
        raise ValueError('unknown line rendering profile')
    if line_profile==quad_profile:
        if domain['profile']!='gles300' or domain['width']*domain['height']>1024*768:
            raise ValueError('quad-line profile requires GLES within reference area')
        if not any(all(engine.get(key)==value for key,value in expected.items())
                   for expected in PRODUCTION_EQUATION_ENGINES.values()):
            raise ValueError('quad-line engine identity mismatch')
    colour = np.asarray(domain['initial_rgba'], dtype=np.float32)
    hue = np.asarray(domain['hue_offsets'], dtype=np.float32)
    if colour.shape!=(4,) or not np.all(np.isfinite(colour)) or np.any((colour<0)|(colour>1)):
        raise ValueError('explicit finite UNORM initial RGBA colour required')
    if hue.shape!=(4,) or not np.all(np.isfinite(hue)):
        raise ValueError('four finite source hue offsets required')
    if audio.get('uses_rendered_reference') is not False or not audio.get('frames'):
        raise ValueError('source-generated nonempty audio inputs required')
    archive = source.get('parser_inputs',{}).get('engine_archive_sha256')
    if not archive or audio.get('engine_archive_sha256')!=archive:
        raise ValueError('source/audio engine identity mismatch')
    reader = Path(binaries)/'milk-native-reader'
    reader_sha = hashlib.sha256(reader.read_bytes()).hexdigest()
    if source.get('reader_sha256')!=reader_sha:
        raise ValueError('source parser binary identity mismatch')
    width, height = domain['width'], domain['height']
    shader_numeric_policy=domain.get('shader_numeric_policy','strict')
    if shader_numeric_policy!='strict' and domain['profile']!='gles300':
        raise ValueError('highp shader numeric policy requires GLES300')
    initial = np.broadcast_to(colour,(height,width,4)).copy()
    warp_code = source.get('sections',{}).get('warp_',{}).get('source','')
    # Native MilkdropPreset uses this literal substring test, including comments.
    warp_reads_blur = 'blur' in warp_code.lower()
    pipeline = SourcePipeline.from_source(source, profile=domain['profile'], compatibility=compatibility,
        equation_loader_policy=domain.get('equation_loader_policy','strict-raw-v1'),
        main_binding_policy=main_binding_policy,
        blur_range_policy=blur_range_policy,legacy_control_policy=legacy_control_policy,
        initial_feedback=initial, warp_reads_blur=warp_reads_blur, blur_levels=domain['blur_levels'],
        quantize=domain['quantize'],coordinate_profile=domain.get('coordinate_profile','strict'),
        composite_subpixel_bits=domain.get('composite_subpixel_bits'),
        main_sampling_profile=domain.get('main_sampling_profile','portable'),shader_numeric_policy=shader_numeric_policy)
    required_blur_level=native_blur_level(source,pipeline.stage_resolution)
    if shape_sampler_policy in {CORE_238_SHAPE_POLICY,CORE_2315_SHAPE} and domain['blur_levels']<required_blur_level:
        raise ValueError('declared blur levels omit native required resources')
    if materials is not None and noise_bank is not None:
        if materials.noise_bank is None or digest(material_input_identity(materials.noise_bank))!=digest(material_input_identity(noise_bank)):
            raise ValueError('combine procedural noise into the declared material bank')
    texture_bank=materials if materials is not None else noise_bank
    material_identity=material_input_identity(texture_bank)
    material_sha=None if material_identity is None else digest(material_identity)
    procedural=noise_bank if materials is None else materials.noise_bank
    if procedural is not None:
        from noise_inputs import validate_noise_clock
        validate_noise_clock(procedural,domain.get('declared_random_profile'),profile=domain['profile'])
        expected_upload = 'RGBA' if domain['profile']=='gles300' else 'BGRA'
        if procedural.upload_format!=expected_upload:
            raise ValueError('procedural material upload profile mismatch')
    material_uniforms={} if texture_bank is None else texture_bank.uniforms()
    # Lookup names are case-insensitive; generated uniform identifiers retain
    # their original spelling and sampler qualifiers.
    if texture_bank is not None:
        for prefix in ('warp_','comp_'):
            section=source.get('sections',{}).get(prefix,{})
            for node in section.get('tree',[]) or []:
                if node.get('kind')!='declarations':continue
                for declaration in node['values']:
                    name=declaration['name']
                    if not name.startswith('texsize_'):continue
                    texture=texture_settings(name.removeprefix('texsize_'))['texture'].lower()
                    if texture not in texture_bank.textures:continue
                    field=texture_bank.textures[texture]
                    h,w=field.shape[-3:-1]
                    material_uniforms[name]=[w,h,1/w,1/h]
    scene = execute_scene(source,audio['frames'],reader=reader,expected_reader_sha256=reader_sha,width=width,height=height,
        mesh_x=domain['mesh_x'],mesh_y=domain['mesh_y'],seed=domain['equation_seed'],
        timeout_seconds=domain.get('equation_timeout_seconds',60),
        equation_loader_policy=domain.get('equation_loader_policy','strict-raw-v1'))
    geometry_features = scene_geometry_features(scene)
    builtin = source_builtin_wave(source,scene,audio,binary=Path(binaries)/'milk-wave-inputs',
                                  line_rendering_profile=line_profile,control_policy=wave_control_policy)
    if builtin['engine_archive_sha256']!=archive:
        raise ValueError('builtin-wave source engine identity mismatch')
    custom = source_custom_waves(source,scene)
    if random_inputs is not None:
        if random_inputs.get('ledger',{}).get('rendered_frames_consumed') is not False:
            raise ValueError('source-generated random input ledger required')
        if len(random_inputs.get('bindings',[]))!=len(scene['frames']):
            raise ValueError('random bindings must cover the exact frame schedule')
    frames = []
    for index, frame in enumerate(scene['frames']):
        main = frame['main']
        render_time=audio['frames'][index]['time']
        unused_warp_uv_domain=None
        try:
            mesh = warp_fields(source,scene,index,numeric_profile=domain.get('numeric_profile','portable'),
                               raster_subpixel_bits=domain.get('warp_subpixel_bits'),zoom_policy=warp_zoom_policy)
        except ValueError as error:
            if str(error) not in {'unresolved warp numeric domain','unresolved warp power domain','zero spatial divisor'}:raise
            if pipeline.requires_warp_uv(frame_wrap=main['wrap'],motion_state=main):raise
            unused_warp_uv_domain=str(error)
            mesh=warp_fields(source,scene,index,raster_subpixel_bits=domain.get('warp_subpixel_bits'),
                             omit_transformed_uv=True,zoom_policy=warp_zoom_policy)
        common = source_uniforms(scene,index)
        if texture_bank is not None:
            common.update(material_uniforms)
        random_banks = {}
        if random_inputs is not None:
            bindings = random_inputs['bindings'][index]
            if set(bindings)-{'warp','composite'}:
                raise ValueError('random binding stage must be warp/composite')
            for stage, binding in bindings.items():
                cache_context = ({'frame':int(frame['render_inputs']['frame']),
                                  'feedback_detail_alpha':-1.0}
                                 if 'frame_cache_policy' in random_inputs['ledger'] else {})
                random_banks[stage] = bind_random_uniforms(random_inputs['ledger'],
                    event_index=binding['event_index'],shader_id=binding['shader_id'],
                    time=render_time,profile=random_inputs['profile'],**cache_context)

        def draw(destination, frame_index, previous_main):
            textures = {}; texture_aspects = {}
            images={shape['index']:source['values'].get(f"shapecode_{shape['index']}_image",'') for shape in frame['shapes']}
            modes=shape_sampling_modes(frame['shapes'],image_names=images,policy=shape_sampler_policy,
                                       warp_reads_blur=warp_reads_blur,blur_level=required_blur_level,frame_wrap=main['wrap'])
            for ordinal,shape in enumerate(frame['shapes']):
                if not int(shape['values'].get('textured',0)):
                    continue
                shape_index = shape['index']
                binding_key=(shape_index,ordinal)
                image = source['values'].get(f'shapecode_{shape_index}_image','')
                if image:
                    # Named-image loading/missing-image fallback needs a bound
                    # material registry; do not pretend an unknown image is main.
                    policy=texture_settings(image);name=policy['texture'].lower()
                    if texture_bank is None or name not in texture_bank.textures:
                        raise ValueError('source shape image binding unresolved: ' + image)
                    if texture_bank.textures[name].ndim!=3:
                        raise ValueError('source shape image must be a two-dimensional texture')
                    detail={'canonical_texture':name,'sampling_policy':{'wrap':policy['wrap'],'linear':policy['linear']}}
                    textures[binding_key]=lambda uv, detail=detail:texture_bank.sample(detail,uv)
                    texture_aspects[shape_index]=1
                else:
                    textures[binding_key]=lambda uv, mode=modes[ordinal]:sample2d(previous_main,uv,wrap=mode['wrap'],linear=mode['linear'],origin='top')
            return draw_source_scene(destination,source,frame,builtin['frames'][index],custom['frames'][index],
                quantize=domain['quantize'],shape_textures=textures,shape_texture_aspects=texture_aspects,
                motion_vectors_prewarped=True,line_rendering_profile=line_profile,
                point_subpixel_bits=domain.get('point_subpixel_bits'),
                triangle_subpixel_bits=domain.get('triangle_subpixel_bits'))

        result = pipeline.step(warp_uv=mesh['original_uv'] if mesh['uv'] is None else mesh['uv'],warp_original_uv=mesh['original_uv'],warp_polar=mesh['polar'],uniforms=common,
            frame_wrap=main['wrap'],stage_uniforms=random_banks,decay=main['decay'],
            minimum=[main[f'blur{i}_min'] for i in range(1,4)],
            maximum=[main[f'blur{i}_max'] for i in range(1,4)],edge_darken=main['blur1_edge_darken'],
            motion_state=main,draw_scene=draw,render_time=render_time,
            hue_offsets=hue.tolist(),external_sample=None if texture_bank is None else texture_bank.sample)
        predicted = dict(frame=frame['render_inputs']['frame'],time=render_time,
                         display=result.display,feedback=result.feedback,warp_uv=mesh['uv'],history=result.history)
        if unused_warp_uv_domain is not None:
            predicted['history']['unused_warp_uv_domain']=unused_warp_uv_domain
        descriptors.add(predicted)
        if on_frame is not None:
            on_frame(copy.deepcopy(predicted))
        frames.append(predicted if retain_surfaces else
                      {key:value for key,value in predicted.items() if key not in {'display','feedback','warp_uv'}})
    if model_file_hashes()!=model_hashes:
        raise ValueError('forecast model files changed during evaluation')
    if material_input_identity(texture_bank)!=material_identity:
        raise ValueError('forecast sampled material inputs changed during evaluation')
    report = dict(status='computed',frames=frames,domain=domain,stage_resolution=pipeline.stage_resolution,
        feature_basis=SIMULATED,geometry_features=geometry_features,
        descriptors=descriptors.report(),
        uses_rendered_reference=False,appearance_accuracy_verified=False,
        input_hashes=dict(preset_sha256=source['preset_sha256'],pcm_sha256=audio['pcm_sha256'],
                          parsed_source_sha256=digest({key:source[key] for key in ['values','sections','parser_inputs']}),
                          domain_sha256=digest(domain),audio_sha256=digest(audio),
                          compatibility_sha256=digest(compatibility),
                          random_sha256=None if random_inputs is None else digest(random_inputs),
                          materials_sha256=material_sha),
        provenance=dict(engine=copy.deepcopy(engine),reader_sha256=reader_sha,wave_binary_sha256=builtin['native_binary_sha256'],
                        material_input_policy=None if material_identity is None else material_identity['policy'],
                        shader_numeric_policy=shader_numeric_policy,
                        main_binding_policy=main_binding_policy,
                        shape_sampler_policy=shape_sampler_policy,native_required_blur_level=required_blur_level,
                        blur_range_policy=blur_range_policy,warp_zoom_policy=warp_zoom_policy,
                        legacy_control_policy=legacy_control_policy,wave_control_policy=wave_control_policy,
                        render_context_source_sha256=builtin['render_context_source_sha256'],
                        render_context_time_bits=builtin['render_context_time_bits'],
                        engine_archive_sha256=archive,model_sha256=digest(model_hashes),model_modules=model_hashes,
                        equation_rng=dict(policy=rng_policy,seed=domain['equation_seed'],
                            lifecycle='fresh evaluator thread; no previous equation draws',
                            native_sequence_verified=False)),
        limitations=['GPU rasterization, sampling and arithmetic precision not validated',
                     'Target shader compilation/linking and fallback remain profile conditions',
                     'Initial state and RNG/resource lifecycle are declared inputs, not inferred engine startup'])
    report['source_features'] = forecast_feature_record(report)
    return report
