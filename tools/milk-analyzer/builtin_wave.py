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


def source_builtin_wave(source,scene,audio,*,binary:Path,timeout_seconds=60):
    if len(scene['frames'])!=len(audio['frames']):raise ValueError('wave/audio frame schedule mismatch')
    values=source['values'];width,height=scene['viewport']
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
    dot=bool(_scalar(values,'bWaveDots',0,'bool'));thick=dot or bool(_scalar(values,'bWaveThick',0,'bool'))
    offsets=[[0,0],[1/width,0],[1/width,-1/height],[0,-1/height]] if thick else [[0,0]]
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
                       'additive':bool(_scalar(values,'bAdditiveWaves',0,'bool')),'copy_offsets':offsets})
    return {'basis':native['basis'],'mode':native['mode'],'frames':result,'source_hashes':native['source_hashes'],
            'adapter_sha256':native['adapter_sha256'],
            'native_binary_sha256':hashlib.sha256(Path(binary).read_bytes()).hexdigest(),
            'engine_archive_sha256':native['engine_archive_sha256'],'uses_rendered_reference':False,
            'appearance_prediction_complete':False,'remaining':['hardware line/point rasterization and full draw integration']}
