import hashlib,json,shlex,subprocess,sys,threading,uuid
from pathlib import Path
import numpy as np
sys.path.insert(0,'tools/milk-analyzer')
from core_backend import read_header,read_frames
ROOT=Path('build/visual-loop/runtime2327/detail-qualification')
DEP=json.loads((ROOT.parent/'configurable/deployment.json').read_text());REMOTE=DEP['remote']
ADB='/Users/jneerdael/Library/Android/sdk/platform-tools/adb'
CASES=['feedback-shape-standard-4k']
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def owned():
 command=subprocess.check_output(['ps','-p','24651','-o','command='],text=True,timeout=10)
 assert 'projectmtv-predictor-visual-loop-api34' in command and '-port 5596' in command
 assert subprocess.check_output([ADB,'-s','emulator-5596','emu','avd','name'],text=True,timeout=10).splitlines()[0].strip()=='projectmtv-predictor-visual-loop-api34'
def adb(*args):
 owned();return subprocess.run([ADB,'-s','emulator-5596',*args],capture_output=True,check=True,timeout=30)
# All three predictions must be frozen before the first published-AAR draw.
for name in CASES:
 case=ROOT/name;freeze=json.loads((case/'freeze.json').read_text())
 for path,digest in freeze['sha256'].items():assert sha(case/path)==digest,(name,path)
 assert freeze['context']==DEP
for path,digest in DEP['sha256'].items():assert adb('shell','sha256sum',REMOTE+'/'+path).stdout.decode().split()[0]==digest
report_path=ROOT/'qualification-report.json'
rows=json.loads(report_path.read_text())['rows'] if report_path.exists() else []
for name in CASES:
 if any(row['case']==name and row['passed'] for row in rows):
  print(name,'already captured; preserving saved results',flush=True);continue
 case=ROOT/name;freeze=json.loads((case/'freeze.json').read_text());predictions=json.loads((case/'frames.json').read_text())
 output=case/'native';output.mkdir()
 prefix=REMOTE+'/detail-'+uuid.uuid4().hex;work=prefix+'-work'
 adb('shell','mkdir','-p',work+'/textures');adb('push',str(case/'selection.apk'),prefix+'.apk')
 cmd=shlex.join(['env','CLASSPATH='+REMOTE+'/classes.dex','LD_PRELOAD='+REMOTE+'/libbackendclock.so',
 'PROJECTMTV_TEST_RANDOM_SEED=12345','PROJECTMTV_TEST_CORE_PATH='+REMOTE+'/libprojectmtv.so',
 'PROJECTMTV_TEST_RANDOM_LOG='+prefix+'.random.jsonl','app_process','-Djava.library.path='+REMOTE,
 '/system/bin','nl.neerdael.projectm.analysis.CoreBackendRunner',REMOTE+'/libprojectmtv.so',
 REMOTE+'/published-core.aar|'+prefix+'.apk',work,prefix,REMOTE+'/libbackendclock.so',REMOTE+'/transport30.f32',
 '30','stream',REMOTE+'/config-4k-trails'+str(freeze['trails'])+'.json'])
 owned();process=subprocess.Popen([ADB,'-s','emulator-5596','exec-out',cmd],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 watchdog=threading.Timer(180,process.kill);watchdog.start()
 frames=[];unique={};maximum=0;total_error=0;total_channels=0
 try:
  header=read_header(process.stdout,expected_frames=30,width=3840,height=2160)
  (output/'stream-header.json').write_text(json.dumps(header,indent=2)+'\n')
  for index,pixels in enumerate(read_frames(process.stdout,expected_frames=30,width=3840,height=2160,header=header)):
   expected=np.load(case/predictions[index]['file'])['pixels']
   delta=np.abs(pixels.astype(np.int16)-expected.astype(np.int16))
   error=int(delta.max());maximum=max(maximum,error);total_error+=int(delta.sum());total_channels+=delta.size
   digest=hashlib.sha256(pixels.tobytes()).hexdigest()
   if digest not in unique:
    file='native-'+digest+'.npz';np.savez_compressed(output/file,pixels=pixels);unique[digest]=file
   frames.append(dict(frame=index,sha256=digest,file=unique[digest],max_rgb8_error=error))
   if index%10==0:print(name,'frame',index,'maxerror',error,flush=True)
  code=process.wait(timeout=30);assert code==0,process.stderr.read()
 finally:
  watchdog.cancel()
  if process.poll() is None:process.kill();process.wait(timeout=10)
 (output/'frames.json').write_text(json.dumps(frames,indent=2)+'\n')
 for suffix,file in [('.json','metadata.json'),('.log','native.log'),('.java.log','java.log')]:
  adb('pull',prefix+suffix,str(output/file))
 metadata=json.loads((output/'metadata.json').read_text())
 assert metadata['frames']==metadata['rendered_frame_serial_delta']==30
 assert metadata['indexed_count']==1 and metadata['skipped_count']==0
 assert metadata['physical_surface_width']==3840 and metadata['physical_surface_height']==2160
 assert metadata['gl_viewport_after_last_draw']==[0,0,3840,2160]
 assert '1280×720 canvas' in metadata['native_trails_status'],metadata
 assert metadata['requested_trails']==freeze['trails']
 row=dict(case=name,header=header,metadata=metadata,max_rgb8_error=maximum,
  mean_rgb8_error=total_error/total_channels,passed=maximum<=freeze['tolerance']['maximum_rgb8_error'])
 rows.append(row)
 (ROOT/'qualification-report.json').write_text(json.dumps(dict(deployment=DEP,rows=rows,scope='Full unchanged published2.3.27 AAR/JNI; frozen30frame U01 numerical controls; no random streak credit'),indent=2)+'\n')
 print(name,'finished','maxerror',maximum,'passed',row['passed'],flush=True)
 if not row['passed']:raise RuntimeError('stop on mismatch; fix or explain before a new capture')
