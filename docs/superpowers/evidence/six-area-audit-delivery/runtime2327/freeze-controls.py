import datetime, hashlib, json, subprocess, sys, zipfile
from pathlib import Path
import numpy as np
sys.path.insert(0,'tools/milk-analyzer')
from forecast import read_source,forecast_source,CORE_2327_EQUATION_RNG_POLICY,model_file_hashes
from shader_compat import check_shader
from core_backend import write_selection_overlay,validate_jni_audio_context
ROOT=Path('build/visual-loop/runtime2327/detail-qualification')
B=Path('build/visual-loop/source-pr59/adapters')
RUNTIME=ROOT.parent
# This is transported signed PCM, then the published JNI's U8 conversion.
request=json.loads(Path('build/visual-loop/source2322/audio-request.json').read_text())
request.update(output=str((ROOT/'audio-context.json').resolve()),preset_progress_policy='projectmtv-core-2.3.27-cold-jni-v1')
(ROOT/'audio-request.json').write_text(json.dumps(request))
subprocess.run([str(B/'milk-audio-inputs'),str(ROOT/'audio-request.json')],check=True,capture_output=True)
audio=json.loads((ROOT/'audio-context.json').read_text())
validate_jni_audio_context(np.fromfile(RUNTIME/'transport30.f32',dtype='<f4'),audio)
context=json.loads((RUNTIME/'configurable/deployment.json').read_text())
for name,level,width,height,body in [
 ('canvas-standard-4k',0,3840,2160,'per_frame_init_1=q1=pixelsx;q2=pixelsy;\nPSVERSION_COMP=2\ncomp_1=`shader_body {ret=float3(q1/5120,q2/1440,texsize_main.x/2560); }\n'),
 ('grating-medium-4k',1,3840,2160,'PSVERSION_WARP=2\nwarp_1=`shader_body { ret=float3(.5+.3*sin(uv_orig.x*texsize_main.x*3.141592653589793),.5+.3*cos(uv_orig.y*texsize_main.y*3.141592653589793),.25); }\n'),
 ('grating-high-4k',2,3840,2160,'PSVERSION_WARP=2\nwarp_1=`shader_body { ret=float3(.5+.3*sin(uv_orig.x*texsize_main.x*3.141592653589793),.5+.3*cos(uv_orig.y*texsize_main.y*3.141592653589793),.25); }\n')]:
 case=ROOT/name;case.mkdir(exist_ok=True)
 if (case/'freeze.json').exists():raise RuntimeError('do not replace an existing freeze')
 text='MILKDROP_PRESET_VERSION=201\n[preset00]\nwarp=0\nfDecay=1\nfWaveAlpha=0\nfGammaAdj=1\nfShader=0\nfVideoEchoAlpha=0\n'+body
 preset=case/(name+'.milk');preset.write_text(text)
 source=read_source(preset,reader=B/'milk-native-reader')
 (case/'source.json').write_text(json.dumps(source))
 compatibility={}
 for stage,prefix in [('warp','warp_'),('composite','comp_')]:
  section=source.get('sections',{}).get(prefix,{})
  if not section.get('source'):continue
  compatibility[stage]=check_shader(section['source'],stage=stage,profile='gles300',translator=B/'milk-shader-translate',validator=Path('/opt/homebrew/bin/glslangValidator'),samplers={'sampler_main':'sampler2D'},texture_sizes=['texsize_main'])
  assert compatibility[stage]['offline_accepted'],compatibility[stage]
 (case/'compatibility.json').write_text(json.dumps(compatibility))
 domain=dict(width=width,height=height,physical_size=[width,height],native_trails_level=level,
  authored_canvas_policy='projectmtv-authored-native-detail-v1',feedback_detail_resource_status='allocated',
  mesh_x=48,mesh_y=32,profile='gles300',initial_rgba=[0]*4,hue_offsets=[0]*4,
  equation_seed=0x4141f00d,equation_rng_policy=CORE_2327_EQUATION_RNG_POLICY,
  blur_levels=0,quantize=True,warp_subpixel_bits=8,composite_subpixel_bits=8,
  point_subpixel_bits=8,triangle_subpixel_bits=8,line_rendering_profile='projectmtv-gles-quad-lines-v1',
  texture_sampling_profile='apple-m4pro-gles-unorm8-fixed8-fraction4-volume-v1',
  equation_loader_policy='projectmtv-core-2.2.8-v1')
 rows=[];unique={}
 def save(frame):
  pixels=np.rint(np.clip(frame['display'][...,:3],0,1)*255).astype(np.uint8)
  sha=hashlib.sha256(pixels.tobytes()).hexdigest()
  if sha not in unique:
   file='predicted-'+sha+'.npz';np.savez_compressed(case/file,pixels=pixels);unique[sha]=file
  rows.append(dict(frame=frame['frame'],time=frame['time'],sha256=sha,file=unique[sha],history=frame['history'],visibility=frame['visibility']))
 result=forecast_source(source,audio=audio,binaries=B,domain=domain,compatibility=compatibility,retain_surfaces=False,on_frame=save)
 (case/'prediction.json').write_text(json.dumps(result,indent=2))
 (case/'frames.json').write_text(json.dumps(rows,indent=2))
 write_selection_overlay(case/'selection.apk',preset.name)
 with zipfile.ZipFile(case/'selection.apk','a',zipfile.ZIP_DEFLATED) as z:z.writestr('assets/presets/'+preset.name,preset.read_bytes())
 files=[p for p in case.iterdir() if p.is_file()]
 freeze=dict(frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),context=context,
  width=width,height=height,trails=level,frames=30,tolerance=dict(maximum_rgb8_error=1),
  model_modules=model_file_hashes(),sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
  scope='Source-only frozen U01 numerical controls before full publishedAAR capture; zero random streak credit')
 (case/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
 print('Frozen',name,len(rows),'frames',len(unique),'unique pixel fields',flush=True)
