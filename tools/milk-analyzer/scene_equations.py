"""Source-driven native equation orchestration for preset/main and custom shapes.

Initializers run in native wave-then-shape order, including disabled components.
Custom locals persist; main Q and shape T defaults reset at native boundaries.
Custom-wave points use native stateful execution and source audio preparation.
Complete drawing integration remains unresolved.
"""
import json
import ctypes
import errno
import os
import re
import subprocess
import tempfile
from pathlib import Path
import numpy as np
from spatial import mesh_inputs


# (preset-file key, native constructor default, scalar storage kind)
MAIN={
 'zoom':('zoom',1,'float'),'zoomexp':('fZoomExponent',1,'float'),'rot':('rot',0,'float'),
 'warp':('warp',1,'float'),'cx':('cx',.5,'float'),'cy':('cy',.5,'float'),
 'dx':('dx',0,'float'),'dy':('dy',0,'float'),'sx':('sx',1,'float'),'sy':('sy',1,'float'),
 'decay':('fDecay',.98,'float'),'wave_a':('fWaveAlpha',.8,'float'),
 'wave_r':('wave_r',1,'float'),'wave_g':('wave_g',1,'float'),'wave_b':('wave_b',1,'float'),
 'wave_x':('wave_x',.5,'float'),'wave_y':('wave_y',.5,'float'),'wave_mystery':('fWaveParam',0,'float'),
 'wave_mode':('nWaveMode',0,'int'),'gamma':('fGammaAdj',2,'float'),
 'echo_zoom':('fVideoEchoZoom',2,'float'),'echo_alpha':('fVideoEchoAlpha',0,'float'),
 'echo_orient':('nVideoEchoOrientation',0,'int'),'wrap':('bTexWrap',1,'bool'),
 'wave_usedots':('bWaveDots',0,'bool'),'wave_thick':('bWaveThick',0,'bool'),
 'wave_additive':('bAdditiveWaves',0,'bool'),'wave_brighten':('bMaximizeWaveColor',1,'bool'),
 'darken_center':('bDarkenCenter',0,'bool'),'invert':('bInvert',0,'bool'),
 'brighten':('bBrighten',0,'bool'),'darken':('bDarken',0,'bool'),'solarize':('bSolarize',0,'bool'),
 'ob_size':('ob_size',.01,'float'),'ib_size':('ib_size',.01,'float'),
 'mv_x':('nMotionVectorsX',12,'float'),'mv_y':('nMotionVectorsY',9,'float'),
 'mv_dx':('mv_dx',0,'float'),'mv_dy':('mv_dy',0,'float'),'mv_l':('mv_l',.9,'float'),
 'mv_r':('mv_r',1,'float'),'mv_g':('mv_g',1,'float'),'mv_b':('mv_b',1,'float'),'mv_a':('mv_a',0,'float')}
for channel in 'rgba':
 MAIN['ob_'+channel]=('ob_'+channel,0,'float')
 MAIN['ib_'+channel]=('ib_'+channel,0 if channel=='a' else .25,'float')
for i in range(1,4):
 MAIN[f'blur{i}_min']=(f'b{i}n',0,'float');MAIN[f'blur{i}_max']=(f'b{i}x',1,'float')
MAIN['blur1_edge_darken']=('b1ed',.25,'float')
SHAPE={'x':(.5,'float'),'y':(.5,'float'),'rad':(.1,'float'),'ang':(0,'float'),
       'sides':(4,'int'),'additive':(0,'bool'),'textured':(0,'bool'),'num_inst':(1,'int'),
       'tex_ang':(0,'float'),'tex_zoom':(1,'float'),
       'r':(1,'float'),'g':(0,'float'),'b':(0,'float'),'a':(1,'float'),
       'r2':(0,'float'),'g2':(1,'float'),'b2':(0,'float'),'a2':(0,'float'),
       'border_r':(1,'float'),'border_g':(1,'float'),'border_b':(1,'float'),'border_a':(0,'float')}
READONLY=('time','frame','fps','progress','bass','mid','treb','bass_att','mid_att','treb_att')
Q=[f'q{i}' for i in range(1,33)];T=[f't{i}' for i in range(1,9)]
WARP=('zoom','zoomexp','rot','warp','cx','cy','dx','dy','sx','sy')

# std::stof/std::stoi use these host C conversions. Reuse their prefix,
# hexadecimal and range rules rather than approximating the native grammar.
_LIBC=ctypes.CDLL(None,use_errno=True)
_LIBC.strtof.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_void_p)]
_LIBC.strtof.restype=ctypes.c_float
_LIBC.strtol.argtypes=[ctypes.c_char_p,ctypes.POINTER(ctypes.c_void_p),ctypes.c_int]
_LIBC.strtol.restype=ctypes.c_long


def _scalar(values,key,default,kind):
    text=ctypes.create_string_buffer(str(values.get(key,default)).encode('utf-8'))
    end=ctypes.c_void_p()
    ctypes.set_errno(0)
    if kind in {'int','bool'}:
        value=_LIBC.strtol(text,ctypes.byref(end),10)
        if end.value==ctypes.addressof(text) or ctypes.get_errno()==errno.ERANGE or not -(2**31)<=value<2**31:
            value=int(default)
        return int(value>0) if kind=='bool' else value
    value=_LIBC.strtof(text,ctypes.byref(end))
    if end.value==ctypes.addressof(text) or ctypes.get_errno()==errno.ERANGE:
        value=float(np.float32(default))
    if not np.isfinite(value):raise ValueError('nonfinite source default: '+key)
    return value


def _code(source,name,policy='strict-raw-v1'):
    from equation_loading import select_equation
    section=source.get('sections',{}).get(name)
    selected=select_equation(section,name,policy=policy)
    if selected['compile_status']=='omitted':return '0;'
    if selected['compile_status']!='accepted' or selected['tree_status']!='parsed':
        raise ValueError('target equation compatibility unresolved: '+name)
    return selected['code'] or '0;'


def _variables(tree):
    result=set()
    def visit(node):
        if isinstance(node,dict):
            if node.get('kind')=='variable':result.add(node['name'])
            for child in node.values():visit(child)
        elif isinstance(node,list):
            for child in node:visit(child)
    visit(tree);return result


def _frame_input(frame):
    if any(name not in frame or not np.isfinite(frame[name]) for name in READONLY):
        raise ValueError('finite explicit audio/time inputs required')
    if int(frame['frame'])!=frame['frame'] or not -(2**31)<=frame['frame']<2**31:
        raise ValueError('native frame counter must be int32')
    with np.errstate(over='ignore'):
        result={name:float(np.float32(frame[name])) for name in READONLY if name!='frame'}
    result['frame']=int(frame['frame'])
    if not all(np.isfinite(v) for v in result.values()):raise ValueError('input exceeds native float32 range')
    return result


def execute_scene(source:dict,frames:list[dict],*,reader:Path,width:int=128,height:int=72,
                  mesh_x:int=48,mesh_y:int=32,timeout_seconds:float=60,seed:int|None=None,
                  equation_loader_policy='strict-raw-v1')->dict:
    from equation_loading import select_equation
    def code(name):return _code(source,name,equation_loader_policy)
    def tree(name):return select_equation(source.get('sections',{}).get(name),name,policy=equation_loader_policy)['tree']
    warnings=[{'section':prefix,'warning':selected['warning']} for prefix,section in source.get('sections',{}).items()
              if prefix not in {'warp_','comp_'}
              for selected in [select_equation(section,prefix,policy=equation_loader_policy)]
              if selected['compile_status']=='omitted']
    if not frames:raise ValueError('explicit input frames required')
    if any(type(n) is not int or n<=0 for n in [width,height]):raise ValueError('positive integer viewport required')
    if seed is not None and (type(seed) is not int or not 0<=seed<2**32):
        raise ValueError('equation RNG seed must be uint32')
    audio_frames=frames
    frames=[_frame_input(frame) for frame in frames]
    values=source['values']
    for index in range(4):
        if _scalar(values,f'wavecode_{index}_enabled',0,'int'):
            for frame in audio_frames:
                if any(name not in frame for name in ['waveform_left','waveform_right','spectrum_left','spectrum_right']):
                    raise ValueError('active wave requires explicit native waveform/spectrum audio arrays')
    defaults={name:_scalar(values,key,value,kind) for name,(key,value,kind) in MAIN.items()}
    legacy_motion=_scalar(values,'bMotionVectorsOn',0,'bool')
    defaults['mv_a']=_scalar(values,'mv_a',legacy_motion,'float')
    aspect_x=float(np.float32(min(1,width/height)));aspect_y=float(np.float32(min(1,height/width)))
    mesh=mesh_inputs(mesh_x,mesh_y,aspect_x=aspect_x,aspect_y=aspect_y)
    pixel_code=code('per_pixel_')
    has_pixel_code=pixel_code!='0;'
    defaults.update(meshx=mesh_x,meshy=mesh_y,pixelsx=width,pixelsy=height,
                    aspectx=float(np.float32(1)/np.float32(aspect_x)),
                    aspecty=float(np.float32(1)/np.float32(aspect_y)))
    programmes={'main_init':{'scope':'main','code':code('per_frame_init_')},
                'main_frame':{'scope':'main','code':code('per_frame_')},'main_defaults':'0;'}
    if has_pixel_code:
        programmes['pixel']={'scope':'pixel','code':pixel_code}
        programmes['pixel_inputs']={'scope':'pixel','code':'0;'}
    custom=set()
    for name in ['per_frame_init_','per_frame_']:
        custom|=_variables(tree(name))
    custom-=set(defaults)|set(READONLY)|set(Q)
    custom={name for name in custom if not re.fullmatch(r'reg\d\d',name)}
    capture=list(defaults)+list(READONLY)+Q+sorted(custom)
    initial={name:0 for name in READONLY};initial['fps']=frames[0]['fps']
    steps=[{'program':'main_init','variables':{**defaults,**initial,**{q:0 for q in Q}}},
           {'program':'main_defaults','variables':{q:{'program':'main_init','variable':q} for q in Q}}]
    layout=[]
    output_count=len(steps)
    def append(step,label=None,count=1):
        nonlocal output_count
        first=output_count;output_count+=step.get('repeat',1)
        steps.append(step)
        if label is not None:layout.append((first,count,label))
    # Initializers still have memory/register effects when drawing is disabled.
    waves={}
    for index in range(4):
        name=f'wave{index}_init';programmes[name]={'scope':f'wave{index}','code':code(f'wave_{index}_init')}
        wave={c:_scalar(values,f'wavecode_{index}_{c}',1,'float') for c in 'rgba'}
        wave['samples']=_scalar(values,f'wavecode_{index}_samples',512,'int')
        waves[index]=wave
        programmes[f'wave{index}_frame']={'scope':f'wave{index}','code':code(f'wave_{index}_per_frame')}
        programmes[f'wave{index}_point']={'scope':f'wave{index}_point','code':code(f'wave_{index}_per_point')}
        programmes[f'wave{index}_defaults']='0;'
        append({'program':name,'variables':{**initial,**wave,**{t:0 for t in T},
               **{q:{'program':'main_init','variable':q} for q in Q}}})
        append({'program':f'wave{index}_defaults','variables':{t:{'program':name,'variable':t} for t in T}})
    shapes={}
    for index in range(4):
        shape={name:_scalar(values,f'shapecode_{index}_{name}',value,kind) for name,(value,kind) in SHAPE.items()}
        shape['thick']=_scalar(values,f'shapecode_{index}_thickOutline',0,'bool')
        shapes[index]=shape
        for phase in ['init','frame']:
            programmes[f'shape{index}_{phase}']={'scope':f'shape{index}','code':code(f'shape_{index}_'+('init' if phase=='init' else 'per_frame'))}
        programmes[f'shape{index}_defaults']='0;'
        append({'program':f'shape{index}_init','variables':{**initial,**shape,'instance':0,**{t:0 for t in T},
                **{q:{'program':'main_init','variable':q} for q in Q}}})
        append({'program':f'shape{index}_defaults','variables':{t:{'program':f'shape{index}_init','variable':t} for t in T}})
    for frame_index,frame in enumerate(frames):
        inputs={name:float(frame[name]) for name in READONLY}
        append({'program':'main_frame','variables':inputs,'reset_variables':{**defaults,
                **{q:{'program':'main_defaults','variable':q} for q in Q}},'capture':capture},(frame_index,'main'))
        if has_pixel_code:
            # Read-only inputs are loaded before main code; Q is copied after it.
            # Q/custom/memory changes then carry through vertices, in row order.
            append({'program':'pixel_inputs','variables':{**inputs,'meshx':mesh_x,'meshy':mesh_y,
                    'pixelsx':width,'pixelsy':height,'aspectx':aspect_x,'aspecty':aspect_y,
                    **{q:{'program':'main_frame','variable':q} for q in Q}}})
            coordinates={name:mesh[key].ravel() for name,key in
                         [('x','equation_x'),('y','equation_y'),('rad','radius'),('ang','equation_ang')]}
            for vertex in range((mesh_x+1)*(mesh_y+1)):
                append({'program':'pixel','variables':{**{k:float(v[vertex]) for k,v in coordinates.items()},
                        **{k:{'program':'main_frame','variable':k} for k in WARP}},
                        'capture':list(WARP)},(frame_index,'mesh'))
        for index,shape in shapes.items():
            if not _scalar(values,f'shapecode_{index}_enabled',0,'bool') or shape['num_inst']<=0:continue
            count=shape['num_inst']
            if count>4096:raise ValueError('shape instance trace exceeds native executor limit')
            append({'program':f'shape{index}_frame','repeat':count,'instance_variable':'instance',
                    'variables':inputs,'reset_variables':{**shape,
                        **{q:{'program':'main_frame','variable':q} for q in Q},
                        **{t:{'program':f'shape{index}_defaults','variable':t} for t in T}},
                    'capture':list(shape)+T+['instance']},(frame_index,'shape',index),count)
        for index,wave in waves.items():
            if not _scalar(values,f'wavecode_{index}_enabled',0,'int'):continue
            frame_program=f'wave{index}_frame';point_program=f'wave{index}_point'
            frame_custom=_variables(tree(f'wave_{index}_per_frame'))-set(READONLY)-set(wave)-set(Q)-set(T)
            append({'program':frame_program,'variables':inputs,'reset_variables':{**wave,
                    **{q:{'program':'main_frame','variable':q} for q in Q},
                    **{t:{'program':f'wave{index}_defaults','variable':t} for t in T}},
                    'capture':list(wave)+Q+T+sorted(frame_custom)},(frame_index,'wave_frame',index))
            spectrum=bool(_scalar(values,f'wavecode_{index}_bSpectrum',0,'bool'))
            settings={'frame_program':frame_program,'spectrum':spectrum,
                      'separation':_scalar(values,f'wavecode_{index}_sep',0,'int'),
                      'scaling':_scalar(values,f'wavecode_{index}_scaling',1,'float'),
                      'smoothing':_scalar(values,f'wavecode_{index}_smoothing',.5,'float'),
                      'preset_wave_scale':_scalar(values,'fWaveScale',1,'float'),
                      'left':audio_frames[frame_index]['spectrum_left' if spectrum else 'waveform_left'],
                      'right':audio_frames[frame_index]['spectrum_right' if spectrum else 'waveform_right']}
            point_custom=_variables(tree(f'wave_{index}_per_point'))-set(READONLY)-set(Q)-set(T)-set('rgba')-{'sample','value1','value2','x','y'}
            append({'program':point_program,'variables':{
                        **{name:{'program':'main_frame','variable':name} for name in READONLY},
                        **{name:{'program':frame_program,'variable':name} for name in Q+T}},
                    'wave_points':settings,'capture':['x','y','r','g','b','a','sample','value1','value2']+sorted(point_custom)},
                   (frame_index,'wave_points',index))
    for program in programmes.values():
        if isinstance(program,dict):program['assembly']='raw'
    request={'programs':programmes,'steps':steps}
    with tempfile.TemporaryDirectory() as temporary:
        path=Path(temporary)/'scene.json';path.write_text(json.dumps(request))
        environment=os.environ.copy()
        environment.pop('PRESET_LAB_SEED',None)
        if seed is not None:environment['PRESET_LAB_SEED']=str(seed)
        process=subprocess.run([str(reader),'--equations',str(path)],capture_output=True,text=True,
                               timeout=timeout_seconds,env=environment)
        if process.returncode:raise ValueError('native scene execution failed: '+process.stderr)
        native=json.loads(process.stdout)
    result=[{'main':{},'main_custom':{},'mesh':[],'shapes':[],'waves':[],'render_inputs':frame} for frame in frames]
    for first,count,label in layout:
        frame_index,kind,*tail=label;rows=native['steps'][first:first+count]
        if kind=='main':
            result[frame_index]['main']={k:v for k,v in rows[0].items() if k not in custom}
            result[frame_index]['main_custom']={k:v for k,v in rows[0].items() if k in custom}
        elif kind=='mesh':result[frame_index]['mesh']+=rows
        elif kind=='wave_frame':result[frame_index]['waves'].append({'index':tail[0],'frame':rows[0]})
        elif kind=='wave_points':
            target=next(w for w in result[frame_index]['waves'] if w['index']==tail[0]);target.update(rows[0])
        else:
            result[frame_index]['shapes'] += [{'index':tail[0],'values':row} for row in rows]
    if not has_pixel_code:
        for frame in result:
            frame['mesh']=[{k:frame['main'][k] for k in WARP} for _ in range((mesh_x+1)*(mesh_y+1))]
    for frame in result:
        for name,low,high in [('gamma',0,8),('echo_zoom',.001,1000)]:
            value=frame['main'][name]
            if isinstance(value,(int,float)):frame['main'][name]=max(low,min(high,value))
    return {'basis':'native source equation orchestration; no rendered inputs','frames':result,
            'equation_rng_seed':seed,
            'equation_loader_policy':equation_loader_policy,
            'equation_warnings':warnings,
            'viewport':[width,height],'mesh_size':[mesh_x,mesh_y],
            'appearance_prediction_complete':False,'remaining':['drawing/runtime precision']}
