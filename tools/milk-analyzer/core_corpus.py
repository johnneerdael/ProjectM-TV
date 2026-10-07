"""Resume pinned published-core numerical measurements by preset identity."""
import argparse
import hashlib
import json
import shlex
import subprocess
import threading
import time
import uuid
import zipfile
from pathlib import Path

import numpy as np

from audience_policy import labels_for_intensity
from core_backend import read_header, read_frames, reusable_result, write_selection_overlay, core_run_identity
from core_backend import freeze_scorer_sources,verify_scorer_sources
from descriptors import DescriptorStream, LUMA
from intensity_calibration import predict_intensity
from intensity_evidence import combine_activity, coherent_flash_proxy


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_runtime_library(aar,library):
    with zipfile.ZipFile(aar) as archive:
        try:published=archive.read('jni/armeabi-v7a/libprojectmtv.so')
        except KeyError as error:
            raise ValueError('Supplied AAR has no armeabi-v7a runtime library') from error
    native_sha=hashlib.sha256(published).hexdigest()
    if digest(library)!=native_sha:
        raise ValueError('Runtime library is not the supplied AAR armeabi-v7a library')
    return native_sha


def atomic_json(path, data):
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    temporary.replace(path)


def measure(case, *, device, remote, output, model, identity, timeout=180,source_hashes=None):
    key=case['sha256'];overlay=output/'overlays'/f'{key}.apk'
    write_selection_overlay(overlay,case['preset'])
    remote_overlay=f'{remote}/selection-{key}.apk'
    subprocess.run(['adb','-s',device,'push',str(overlay),remote_overlay],capture_output=True,check=True)
    prefix=f'{remote}/result-{uuid.uuid4().hex}'
    command=['env',f'CLASSPATH={remote}/classes.dex',f'LD_PRELOAD={remote}/libbackendclock.so',
             '/system/bin/app_process',f'-Djava.library.path={remote}','/system/bin',
             'nl.neerdael.projectm.analysis.CoreBackendRunner',f'{remote}/libprojectmtv.so',
             f'{remote}/projectM-TV-core-2.2.4.aar|{remote_overlay}',f'{remote}/work',prefix,
             f'{remote}/libbackendclock.so',f'{remote}/running.f32','420','stream']
    process=subprocess.Popen(['adb','-s',device,'exec-out',shlex.join(command)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    state={'pid':None,'timed_out':False};started=time.monotonic()
    def expire():
        if process.poll() is not None:return
        state['timed_out']=True
        if state['pid']:
            subprocess.run(['adb','-s',device,'shell','kill','-9',str(state['pid'])],capture_output=True,timeout=10)
        process.kill()
    timer=threading.Timer(timeout,expire);timer.start()
    result={**case,'identity':identity,'backend':'published-core-jni','status':'unscored','score':None}
    try:
        header=read_header(process.stdout,expected_frames=420);state['pid']=header['pid']
        stream=DescriptorStream(warmup_frames=60);uniform=True;stationary=True;previous=None;uniform_changes=[]
        for i,rgb in enumerate(read_frames(process.stdout,expected_frames=420,header=header)):
            values=rgb.astype(np.float32)/255
            stream.add({'time':(i+1)/30,'display':np.concatenate((values,np.ones((72,128,1),dtype=np.float32)),axis=-1)})
            if i>=60:
                uniform &= bool(np.all(rgb==rgb[0,0]))
                if previous is not None:
                    stationary &= bool(np.array_equal(rgb,previous))
                    uniform_changes.append(abs(float((values@LUMA).mean())-float((previous.astype(np.float32)/255@LUMA).mean())))
                previous=rgb.copy()
        if process.wait(timeout=15)!=0:raise RuntimeError('Native runner failed')
        metadata_file=output/'metadata'/f'{key}.json'
        subprocess.run(['adb','-s',device,'pull',prefix+'.json',str(metadata_file)],capture_output=True,check=True)
        metadata=json.loads(metadata_file.read_text())
        if metadata['preset']!=case['preset']:raise ValueError('Core did not render the selected preset')
        desc=stream.report();m=desc['motion'];f=desc['flashing']
        features=[(f['coherent_brightening_transitions']+f['coherent_darkening_transitions'])/12,
                  m['median_speed_viewports_per_second'],m['mean_acceleration_viewports_per_second_squared'],m['matched_brightness_change_p95']]
        result.update(descriptors=desc,metadata=metadata,features=features,all_uniform=uniform,all_stationary=stationary)
        if uniform or stationary:
            # Absence of displayed spatial structure or any displayed change is
            # observed directly; this is not unknown flow imputed as calmness.
            features[1:]=[0,0,float(np.percentile(uniform_changes,95)) if uniform_changes else 0]
            result['motion_basis']='Uniform fields or byte-identical stationary fields; no visible spatial motion'
        if any(v is None for v in features):raise ValueError('Visible motion measurement unresolved; correspondence needs diagnosis')
        base=float(predict_intensity(model,[features])[0])
        score=combine_activity(base,coherent_flash=coherent_flash_proxy(desc,fps=30))
        result.update(status='scored',score=score,labels=labels_for_intensity(score),features=features,
                      descriptors=desc,metadata=metadata,all_uniform=uniform,all_stationary=stationary)
    except Exception as error:
        result['reason']='Runner timeout' if state['timed_out'] else str(error)
        if process.poll() is None:expire()
        process.wait(timeout=15)
    finally:
        timer.cancel();result['elapsed_seconds']=time.monotonic()-started
        for suffix in ('.log','.java.log','.skip'):
            subprocess.run(['adb','-s',device,'pull',prefix+suffix,str(output/'logs'/f'{key}{suffix}')],capture_output=True,timeout=15)
        subprocess.run(['adb','-s',device,'shell',shlex.join(['rm','-f',remote_overlay,prefix+'.json',prefix+'.log',prefix+'.java.log',prefix+'.skip'])],capture_output=True,timeout=15)
        process.stdout.close();process.stderr.close()
    if source_hashes is not None:verify_scorer_sources(source_hashes)
    atomic_json(output/'results'/f'{key}.json',result)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--aar',type=Path,required=True);parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--device',default='192.168.50.80:5555')
    parser.add_argument('--remote',default='/data/local/tmp/projectmtv-audience/published')
    parser.add_argument('--runtime',type=Path,required=True)
    parser.add_argument('--pcm',type=Path,required=True)
    parser.add_argument('--limit',type=int);parser.add_argument('--retry-unscored',action='store_true')
    args=parser.parse_args()
    from java_runtime import snapshot_runtime
    with snapshot_runtime(args,('dex/classes.dex','libbackendclock.so','jni/armeabi-v7a/libprojectmtv.so')) as frozen:
        return run(frozen)


def run(args):
    output=args.output
    source_hashes=freeze_scorer_sources()
    model_bytes=args.model.read_bytes();model_sha=hashlib.sha256(model_bytes).hexdigest()
    candidate=json.loads(model_bytes);model=candidate['model']
    native_library=args.runtime/'jni/armeabi-v7a/libprojectmtv.so'
    native_sha=verify_runtime_library(args.aar,native_library)
    from java_runtime import verify_runtime_classes
    java_identity=verify_runtime_classes(args.aar,args.runtime,args.runtime/'dex/classes.dex')
    verify_scorer_sources(source_hashes)
    for folder in ('results','overlays','metadata','logs'):(output/folder).mkdir(parents=True,exist_ok=True)
    runtime_files={'classes.dex':args.runtime/'dex/classes.dex',
                   'libbackendclock.so':args.runtime/'libbackendclock.so',
                   'libprojectmtv.so':native_library,
                   'running.f32':args.pcm,'projectM-TV-core-2.2.4.aar':args.aar}
    runtime_hashes={name:digest(path) for name,path in runtime_files.items()}
    for name,expected in runtime_hashes.items():
        command=shlex.join(['sha256sum',f'{args.remote}/{name}'])
        actual=subprocess.check_output(['adb','-s',args.device,'shell',command],text=True).split()[0]
        if actual!=expected:raise ValueError('Deployed runtime differs: '+name)
    fingerprint=subprocess.check_output(['adb','-s',args.device,'shell','getprop','ro.build.fingerprint'],text=True).strip()
    verify_scorer_sources(source_hashes)
    code_hashes=source_hashes
    identity_data={'aar_sha256':digest(args.aar),'native_armeabi_v7a_sha256':native_sha,
                   'java_runtime_binding':java_identity,
                   'model_sha256':model_sha,'python_hashes':code_hashes,
                   'runner_java_sha256':digest(Path(__file__).with_name('CoreBackendRunner.java')),
                   'clock_source_sha256':digest(Path(__file__).with_name('core_backend_clock.cpp')),
                   'profile':{'frames':420,'warmup':60,'fps':30,'width':128,'height':72},'device':args.device,
                   'runtime_hashes':runtime_hashes,'device_fingerprint':fingerprint}
    identity=core_run_identity(identity_data)
    atomic_json(output/'run-identity.json',{'identity':identity,**identity_data})
    with zipfile.ZipFile(args.aar) as archive:
        cases=[{'preset':name.removeprefix('assets/presets/'),'sha256':hashlib.sha256(archive.read(name)).hexdigest()}
               for name in sorted(archive.namelist()) if name.startswith('assets/presets/') and name.lower().endswith('.milk')]
    atomic_json(output/'corpus.json',{'count':len(cases),'cases':cases})
    if args.limit is not None:cases=cases[:args.limit]
    for index,case in enumerate(cases,1):
        existing=output/'results'/f"{case['sha256']}.json"
        if existing.exists():
            old=json.loads(existing.read_text())
            if reusable_result(old,identity):continue
            if old.get('identity')==identity and not args.retry_unscored:continue
        verify_scorer_sources(source_hashes)
        result=measure(case,device=args.device,remote=args.remote,output=output,model=model,identity=identity,source_hashes=source_hashes)
        print(json.dumps({'completed_case':index,'selected':len(cases),'preset':case['preset'],'status':result['status'],
                          'score':result['score'],'reason':result.get('reason'),'elapsed_seconds':round(result['elapsed_seconds'],2)}),flush=True)
    verify_scorer_sources(source_hashes)


if __name__=='__main__':main()
