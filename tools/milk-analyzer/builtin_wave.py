"""Source-derived built-in waveform geometry and draw specifications, no images.

Native CPU math bodies run in an isolated data-only adapter. Colour, opacity,
projection and static renderer flags follow the pinned Waveform draw source.
Hardware line/point coverage remains a separate unresolved rendering stage.
"""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
import numpy as np
from scene_equations import _scalar
from quad_lines import PROFILE


_CORE235_ENGINE = {
    'commit': 'e0b0a967f0ffd7d332106c366668ed271718472b',
    'patches_sha256': 'd73c955a26380a502516e6ba3a18baf753851244de4de2e5a3083930766a539a',
}
_CORE237_ENGINE = {
    'commit': 'e0b0a967f0ffd7d332106c366668ed271718472b',
    'patches_sha256': 'd70f5b5ec3f3c0b4da764cb824153f142b88e17e27c2e9e71d2b481c19998c7d',
}

_CORE2310_ENGINE = {
    'commit': 'e0b0a967f0ffd7d332106c366668ed271718472b',
    'patches_sha256': '545ca48adad787f963f9b29c1fc4fd7e8a71fb910f586c8747f96a075d130ddf',
}


def _colour(source,main,frame,mode,alpha,width,height):
    values=source['values'];base=np.float32(alpha);result=base
    largest=max(width,height)
    if mode in {2,5}:
        result*=np.float32(.07 if largest<=256 else .09 if largest<=512 else .11 if largest<=1024 else .13 if largest<=2048 else .15)
    elif mode==3:
        result*=np.float32(.075 if largest<=256 else .15 if largest<=512 else .22 if largest<=1024 else .33 if largest<=2048 else .44)
        result*=np.float32(1.3);result*=np.float32(frame['treb'])**np.float32(2)
    if _scalar(values,'bModWaveAlphaByVolume',0,'bool'):
        start=_scalar(values,'fModWaveAlphaStart',.75,'float');end=_scalar(values,'fModWaveAlphaEnd',.95,'float')
        volume=np.float32(frame['vol'])
        if volume<=start:result=np.float32(0)
        elif volume>=end:result=base
        else:result=base*((volume-np.float32(start))/(np.float32(end)-np.float32(start)))
    rgb=np.asarray([main['wave_'+channel] for channel in 'rgb'],dtype=np.float32)
    if main['wave_brighten']>0 and np.max(rgb)>.01:rgb=rgb/np.max(rgb)
    rgba=np.concatenate((rgb,[np.clip(result,0,1)])).astype(np.float32)
    if not np.all(np.isfinite(rgba)):raise ValueError('unresolved waveform colour/opacity domain')
    return rgba.tolist()


def source_builtin_wave(source,scene,audio,*,binary:Path,timeout_seconds=60,
                        line_rendering_profile='canonical-gl-lines-v1'):
    if len(scene['frames'])!=len(audio['frames']):raise ValueError('wave/audio frame schedule mismatch')
    values=source['values'];width,height=scene['viewport']
    if line_rendering_profile not in {'canonical-gl-lines-v1',PROFILE}:
        raise ValueError('unknown builtin wave line rendering profile')
    # Published core through source44 reads these controls from PresetState in
    # Waveform::Draw/DrawPrepared. PerFrameUpdate never copies their live EEL
    # counterparts back to state. Model that engine, not ideal MilkDrop behavior;
    # a future native compatibility repair requires a separately versioned policy.
    dot=bool(_scalar(values,'bWaveDots',0,'bool'))
    scaled_dots=dot and line_rendering_profile==PROFILE
    if scaled_dots:
        engine=source.get('parser_inputs',{}).get('engine',{})
        if not any(all(engine.get(key)==value for key,value in expected.items())
                   for expected in [_CORE235_ENGINE,_CORE237_ENGINE,_CORE2310_ENGINE]):
            raise ValueError('GLES builtin dot engine identity mismatch')
        if width<=0 or height<=0 or width*height>1024*768 or height>1330:
            raise ValueError('GLES builtin dot profile requires viewport within reference area')
    mode=_scalar(values,'nWaveMode',0,'int')
    request_frames=[]
    for frame,data in zip(scene['frames'],audio['frames']):
        inputs=frame['render_inputs'];main=frame['main']
        if data['frame']!=inputs['frame'] or np.float32(data['time'])!=np.float32(inputs['time']) or data['fps']!=inputs['fps']:
            raise ValueError('wave/audio frame schedule mismatch')
        request_frames.append({**{name:data[name] for name in ['waveform_left','waveform_right','spectrum_left','spectrum_right','vol']},
                               'time':data['time'],**{name:main[name] for name in ['wave_x','wave_y','wave_mystery','wave_a']}})
    request={'mode':mode,'width':width,'height':height,'wave_scale':_scalar(values,'fWaveScale',1,'float'),
             'wave_smoothing':_scalar(values,'fWaveSmoothing',.75,'float'),
             'modulate_alpha_by_volume':bool(_scalar(values,'bModWaveAlphaByVolume',0,'bool')),'frames':request_frames}
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary);output=root/'wave.json';path=root/'request.json'
        request['output']=str(output);path.write_text(json.dumps(request))
        process=subprocess.run([str(binary),str(path)],capture_output=True,text=True,timeout=timeout_seconds)
        if process.returncode:raise ValueError('native waveform execution unresolved: '+process.stderr)
        native=json.loads(output.read_text())
    if native.get('render_context_time_bits')!=32:
        raise ValueError('prepared native waveform adapter with float32 render context required')
    thick=dot or bool(_scalar(values,'bWaveThick',0,'bool'))
    # Waveform::Draw uses one DotStyleFor(MainWave) point when quad mode is on.
    # At/below the reference area LineScale=1, hence size=2 and alphaScale=1.
    offsets=[[0,0]] if scaled_dots or not thick else [[0,0],[1/width,0],[1/width,-1/height],[0,-1/height]]
    result=[]
    for frame,data,geometry in zip(scene['frames'],audio['frames'],native['frames']):
        waves=[]
        for vertices in geometry['vertex_waves']:
            if not vertices:waves.append([]);continue
            points=np.asarray(vertices,dtype=np.float32)
            # Native builtin wave uses orthogonalProjectionFlipped (normal Y).
            screen=points*np.array([.5,-.5],dtype=np.float32)+np.float32(.5)
            waves.append(screen.tolist())
        result.append({'positions':waves,'clip_positions':geometry['vertex_waves'],
                       'rgba':_colour(source,frame['main'],data,native['mode'],geometry['wave_a_after_geometry'],width,height),
                       'draw_mode':'points' if dot else 'loop' if geometry['closed_loop'] else 'strip',
                       'point_size':2 if scaled_dots else 1,
                       'additive':bool(_scalar(values,'bAdditiveWaves',0,'bool')),'copy_offsets':offsets})
    return {'basis':native['basis'],'mode':native['mode'],'frames':result,'source_hashes':native['source_hashes'],
            'adapter_sha256':native['adapter_sha256'],
            'native_binary_sha256':hashlib.sha256(Path(binary).read_bytes()).hexdigest(),
            'engine_archive_sha256':native['engine_archive_sha256'],'uses_rendered_reference':False,
            'render_context_source_sha256':native['render_context_source_sha256'],
            'render_context_time_bits':native['render_context_time_bits'],
            'appearance_prediction_complete':False,'remaining':['hardware line/point rasterization and full draw integration']}
