"""Run the complete offline47-field corpus export; publish a ZIP every100 cases."""
import argparse
import fcntl
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback

from corpus_store import RunStore,atomic_json,discover,file_hash
from engine_profiles import CORE_2329_ENGINE,CORE_2331_ENGINE

ROOT=Path(__file__).resolve().parents[2]
ADAPTERS=('milk-native-reader','milk-shader-translate','milk-audio-inputs','milk-wave-inputs',
          'milk-image-inputs','milk-noise-inputs','milk-composite-inputs','milk-shader-random')
CORE_2331_AAR_SHA256='13290b486d08569f229f1f684e57aba849a31a2506270a4d305777322d8d7377'


def verify_target(configuration):
    """Verify publication bytes independently from the prepared source archive."""
    engine=configuration.get('source_engine',CORE_2329_ENGINE)
    if engine not in (CORE_2329_ENGINE,CORE_2331_ENGINE):raise ValueError('unsupported corpus source engine')
    publication={'published_aar','published_aar_sha256','engine_profile','engine_profile_sha256'}
    if engine==CORE_2329_ENGINE:
        if publication & configuration.keys():raise ValueError('historical diagnostic cannot claim published31 AAR binding')
        return
    if not publication<=configuration.keys():raise ValueError('published31 AAR/profile identity required')
    if file_hash(configuration['engine_profile'])!=configuration['engine_profile_sha256']:
        raise ValueError('engine profile identity changed')
    profile=json.loads(Path(configuration['engine_profile']).read_text())
    if profile.get('source_engine')!=CORE_2331_ENGINE or profile.get('release')!='v2.3.31':
        raise ValueError('published profile source engine mismatch')
    if (profile.get('aar_sha256')!=CORE_2331_AAR_SHA256 or
            configuration['published_aar_sha256']!=CORE_2331_AAR_SHA256 or
            file_hash(configuration['published_aar'])!=CORE_2331_AAR_SHA256):
        raise ValueError('exact full published31 AAR identity mismatch')
    if profile.get('qualification',{}).get('published_bytes_verified') is not True:
        raise ValueError('published profile lacks verified byte identity')
    archive=configuration.get('source_engine_archive_sha256','')
    if not isinstance(archive,str) or re.fullmatch('[0-9a-f]{64}',archive) is None:
        raise ValueError('source adapter archive identity required')


def target_identity(args,binaries):
    """Probe the actual parser before preparing or admitting a new corpus run."""
    from forecast import read_source
    engine=CORE_2331_ENGINE if args.target=='core2331' else CORE_2329_ENGINE
    identity={'source_engine':engine,'corpus_target':args.target}
    if engine==CORE_2331_ENGINE:
        profile=Path(args.engine_profile).resolve(strict=True);aar=Path(args.aar).resolve(strict=True)
        identity.update(published_aar=str(aar),published_aar_sha256=file_hash(aar),
                        engine_profile=str(profile),engine_profile_sha256=file_hash(profile))
    elif args.aar is not None or args.engine_profile is not None:
        raise ValueError('core2329 diagnostic has no published AAR/profile qualification')
    with tempfile.TemporaryDirectory(prefix='corpus-source-identity-') as directory:
        preset=Path(directory)/'identity.milk';preset.write_text('[preset00]\nfDecay=1\n')
        source=read_source(preset,reader=Path(binaries)/'milk-native-reader')
    if source['parser_inputs']['engine']!=engine:raise ValueError('configured corpus source engine differs from actual parser')
    identity['source_engine_archive_sha256']=source['parser_inputs']['engine_archive_sha256']
    verify_target(identity)
    return identity


def stop_process(process):
    # The session/process group belongs to this task even after its leader exits.
    try:os.killpg(process.pid,signal.SIGTERM)
    except ProcessLookupError:
        process.wait(timeout=10);return
    time.sleep(.5)
    process.poll()  # Reap an exited leader before probing/killing its remaining group.
    try:os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    process.wait(timeout=10)


def preparation_guard(inputs,identity):
    path=inputs/'preparation-identity.json'
    if path.exists():
        if json.loads(path.read_text())!=identity:
            raise ValueError('input preparation identity changed; choose a new output directory')
    else:
        if (inputs/'manifest.json').exists():
            raise ValueError('unattributed prepared inputs; choose a new output directory')
        atomic_json(path,identity)


def verify_frozen(configuration):
    from forecast import model_file_hashes
    from corpus_inputs import verify_inputs
    if model_file_hashes()!=configuration['model_modules']:raise ValueError('model source identity changed')
    verify_target(configuration)
    for name,sha in configuration['binary_sha256'].items():
        if file_hash(Path(configuration['binaries'])/name)!=sha:raise ValueError('adapter identity changed: '+name)
    if file_hash(configuration['validator'])!=configuration['validator_sha256']:raise ValueError('validator identity changed')
    inputs=Path(configuration['inputs']);path=inputs/'manifest.json'
    if file_hash(path)!=configuration['prepared_inputs_sha256']:raise ValueError('input manifest identity changed')
    verify_inputs(inputs,json.loads(path.read_text()))


def memory_failure(footprint,limit):
    return {'status':'error','stage':'worker_memory','feature_record':None,
        'error_type':'MemoryLimitExceeded','error':'owned worker group exceeded declared memory budget',
        'peak_worker_bytes':footprint,'memory_limit_bytes':limit}


def finish_process(task,*,timed_out=False):
    process=task['process'];process.wait(timeout=10)
    task['stdout'].close();task['stderr'].close()
    result_path=task['result']
    if task.get('memory_exceeded'):
        result=memory_failure(task['peak_worker_bytes'],task['configuration']['memory_limit_bytes'])
    elif timed_out:
        result={'status':'timeout','stage':'worker','feature_record':None,'error':'per-preset deadline exceeded'}
    elif process.returncode!=0 or not result_path.exists():
        result={'status':'error','stage':'worker','feature_record':None,
                'error':'worker exited without a complete result','exit_code':process.returncode}
    else:
        try:result=json.loads(result_path.read_text())
        except (ValueError,OSError) as error:
            result={'status':'error','stage':'worker','feature_record':None,'error':'invalid worker result: '+str(error)}
    if result.get('status')!='computed':
        result['stderr_tail']=task['stderr_path'].read_text(errors='replace')[-12000:]
        result['stdout_tail']=task['stdout_path'].read_text(errors='replace')[-2000:]
    result['elapsed_seconds']=time.monotonic()-task['started']
    result['observed_peak_worker_bytes']=task.get('peak_worker_bytes') if task.get('memory_sample_count') else None
    result.setdefault('simulation',task['configuration']['simulation'])
    result['uses_rendered_reference']=False;result['appearance_accuracy_verified']=False
    return result


def parse_args(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--presets',type=Path,default=ROOT/'core/src/main/assets/presets')
    p.add_argument('--textures',type=Path,default=ROOT/'core/src/main/assets/textures')
    p.add_argument('--target',choices=('core2331','core2329-diagnostic'),default='core2331')
    p.add_argument('--binaries',type=Path)
    p.add_argument('--aar',type=Path,help='full published31 core AAR; verified separately from source adapters')
    p.add_argument('--engine-profile',type=Path,help='published31 engine qualification profile')
    p.add_argument('--validator',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--frames',type=int,default=60);p.add_argument('--fps',type=int,choices=[15,30,60],default=15)
    p.add_argument('--width',type=int,default=854);p.add_argument('--height',type=int,default=480)
    p.add_argument('--workers',type=int,default=2);p.add_argument('--batch-size',type=int,default=100)
    p.add_argument('--timeout',type=float,default=300);p.add_argument('--equation-timeout',type=float,default=60)
    p.add_argument('--seed',type=int,default=12345);p.add_argument('--pcm',type=Path)
    p.add_argument('--memory-limit-gib',type=float,default=6,help='maximum owned worker group footprint; monitored every second')
    p.add_argument('--limit',type=int);p.add_argument('--check',action='store_true',help='prepare/verify inputs and print inventory without simulating')
    args=p.parse_args(argv)
    release31=args.target=='core2331'
    args.binaries=args.binaries or ROOT/('build/preset-corpus/source31/adapters' if release31 else 'build/preset-corpus/source29/adapters')
    args.output=args.output or Path.home()/('Downloads/ProjectM-TV-preset-corpus-15fps-480p-core2331' if release31 else
                                          'Downloads/ProjectM-TV-preset-corpus-15fps-480p-core2329-diagnostic')
    if release31:
        args.aar=args.aar or ROOT/'build/preset-corpus/published31/projectM-TV-core-2.3.31.aar'
        args.engine_profile=args.engine_profile or Path(__file__).with_name('profiles')/'published-core-v2.3.31.json'
    if not 1<=args.workers<=32:p.error('workers must be1..32')
    if args.frames<1 or args.width<1 or args.height<1 or args.width*args.height>1024*768:
        p.error('positive dimensions/frames within the currently supported reference area required')
    if not 0<=args.seed<2**32 or args.batch_size<1 or not math.isfinite(args.timeout) or args.timeout<=0 or not math.isfinite(args.equation_timeout) or not 0<args.equation_timeout<=3600:
        p.error('invalid seed, batch size or deadlines')
    if not math.isfinite(args.memory_limit_gib) or args.memory_limit_gib<=0:p.error('positive finite worker memory budget required')
    if args.limit is not None and args.limit<1:p.error('positive limit required')
    return args


def run(args):
    # Imports happen after argument validation; the launcher selects the prepared Python environment.
    from forecast import model_file_hashes
    from corpus_inputs import prepare_inputs,verify_inputs
    from process_memory import policy,group_bytes,exceeded
    args.output=args.output.expanduser().resolve();args.output.mkdir(parents=True,exist_ok=True)
    lock=(args.output/'controller.lock').open('a+')
    try:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as error:raise RuntimeError('corpus controller already running in this output directory') from error
        binaries=args.binaries.resolve(strict=True)
        missing=[n for n in ADAPTERS if not (binaries/n).is_file()]
        if missing:raise ValueError('prepare configured source adapters first; missing: '+','.join(missing))
        target=target_identity(args,binaries)
        validator=args.validator or shutil.which('glslangValidator')
        if validator is None:raise ValueError('glslangValidator required for offline shader compatibility')
        validator=Path(validator).resolve(strict=True)
        cases=discover(args.presets)
        if args.limit is not None:cases=cases[:args.limit]
        modules=model_file_hashes()
        identity={**target,'export_kind':'offline-source-field-corpus-v1','model_modules':modules,
            'binary_sha256':{n:file_hash(binaries/n) for n in ADAPTERS},'validator_sha256':file_hash(validator),
            'simulation':{'frames':args.frames,'fps':args.fps,'width':args.width,'height':args.height},
            'seed':args.seed,'signal_policy':'fixed-kick-chord-hat-v1' if args.pcm is None else 'supplied-mono-f32',
            'pcm_sha256':None if args.pcm is None else file_hash(args.pcm),
            'textures':str(args.textures.resolve()),'equation_timeout':args.equation_timeout,
            'worker_timeout':args.timeout,'memory_limit_bytes':int(args.memory_limit_gib*2**30),
            'memory_measurement_policy':policy(),'sampling_profile':'apple-m4pro-gles-unorm8-fixed8-fraction4-volume-v1'}
        # Input preparation is durable, bounded and separate from the exported result ZIPs.
        inputs=args.output/'inputs';manifest_path=inputs/'manifest.json'
        old_manifest=args.output/'run-manifest.json'
        if old_manifest.exists():
            old=json.loads(old_manifest.read_text())['configuration']
            if any(old.get(k)!=v for k,v in identity.items()):raise ValueError('run identity changed; choose a new output directory')
        preparation_guard(inputs,identity)
        if manifest_path.exists():
            manifest=json.loads(manifest_path.read_text());verify_inputs(inputs,manifest)
            if (manifest['fps'],manifest['frames'],manifest['seed'])!=(args.fps,args.frames,args.seed):
                raise ValueError('prepared input cadence/seed differs; choose a new output directory')
        else:manifest=prepare_inputs(inputs,binaries=binaries,textures=args.textures,frames=args.frames,fps=args.fps,seed=args.seed,pcm=args.pcm)
        identity['prepared_inputs_sha256']=file_hash(manifest_path)
        configuration={**identity,'binaries':str(binaries),'inputs':str(inputs),'validator':str(validator),
                       'effect_cache':str(args.output/'effect-cache')}
        worker=Path(__file__).with_name('corpus_worker.py')
        with RunStore(args.output,identity,cases,batch_size=args.batch_size) as store:
            print(json.dumps({'event':'ready','presets':len(cases),'pending':len(store.pending()),'simulation':identity['simulation'],
                'workers':args.workers,'output':str(args.output),'resume':True,'AI_involved':False}),flush=True)
            if args.check:return 0
            pending=iter(store.pending());active={};exhausted=False;interrupted=False;last_verified=0
            with tempfile.TemporaryDirectory(prefix='preset-corpus-workers-') as scratch:
                scratch=Path(scratch)
                try:
                    while active or not exhausted:
                        if time.monotonic()-last_verified>=5:
                            verify_frozen(configuration);last_verified=time.monotonic()
                        while len(active)<args.workers and not exhausted:
                            try:case=next(pending)
                            except StopIteration:exhausted=True;break
                            key=file_hash(Path(case['path']))[:16]+'-'+str(len(active))+'-'+str(time.time_ns())
                            job=scratch/(key+'.job.json');result=scratch/(key+'.result.json')
                            atomic_json(job,{'case':case,'configuration':configuration})
                            stdout_path=scratch/(key+'.stdout');stderr_path=scratch/(key+'.stderr')
                            stdout=stdout_path.open('wb');stderr=stderr_path.open('wb')
                            worker_env={**os.environ,**{name:'1' for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS')}}
                            process=subprocess.Popen([sys.executable,str(worker),'--job',str(job),'--output',str(result)],
                                stdout=stdout,stderr=stderr,start_new_session=True,env=worker_env)
                            active[process.pid]={'process':process,'case':case,'result':result,'stdout':stdout,'stderr':stderr,
                                'stdout_path':stdout_path,'stderr_path':stderr_path,'started':time.monotonic(),'configuration':configuration,'last_memory_check':0,'peak_worker_bytes':0,'memory_sample_count':0}
                        progressed=False
                        for pid,task in list(active.items()):
                            timed_out=time.monotonic()-task['started']>args.timeout
                            if task['process'].poll() is None and time.monotonic()-task['last_memory_check']>=1:
                                footprint=group_bytes(task['process'].pid);task['last_memory_check']=time.monotonic()
                                task['memory_sample_count']+=1
                                task['peak_worker_bytes']=max(task['peak_worker_bytes'],footprint)
                                task['memory_exceeded']=exceeded(footprint,configuration['memory_limit_bytes'])
                            if task['process'].poll() is None and not timed_out and not task.get('memory_exceeded'):continue
                            stop_process(task['process'])
                            result=finish_process(task,timed_out=timed_out)
                            if result.get('stage')=='identity':
                                raise ValueError('worker integrity check failed; case stays pending: '+str(result.get('error')))
                            verify_frozen(configuration)
                            store.complete(task['case'],result)
                            del active[pid];progressed=True
                            counts=store.counts();print(json.dumps({'event':'preset_completed','completed':sum(counts.values()),
                                'total':len(cases),'preset':task['case']['relative_path'],'status':result['status'],
                                'stage':result.get('stage'),'elapsed_seconds':round(result['elapsed_seconds'],2),'counts':counts},ensure_ascii=False),flush=True)
                            atomic_json(args.output/'progress.json',{'completed':sum(counts.values()),'total':len(cases),'counts':counts})
                        if not progressed:time.sleep(.2)
                except KeyboardInterrupt:interrupted=True;print('Interrupted: finished results are preserved; active presets will resume.',flush=True)
                finally:
                    for task in active.values():
                        stop_process(task['process']);task['stdout'].close();task['stderr'].close()
                    store.flush(partial=True)
            counts=store.counts();print(json.dumps({'event':'interrupted' if interrupted else 'complete',
                'completed':sum(counts.values()),'total':len(cases),'counts':counts,'output':str(args.output)}),flush=True)
            return 130 if interrupted else 0
    finally:lock.close()


def main():
    args=None
    try:
        args=parse_args()
        return run(args)
    except Exception as error:
        kind=type(error).__name__
        print('Corpus runner stopped: '+kind+(': '+str(error) if str(error) else ''),file=sys.stderr)
        # Preserve fatal diagnostics when a Terminal window is closed. Reporting
        # failure must not replace the original exception/exit status.
        if args is not None:
            try:
                detail=''.join(traceback.format_exception(error))
                path=args.output.expanduser()/f'controller-error-{time.time_ns()}-{os.getpid()}.json'
                atomic_json(path,{
                    'error_type':kind,'message':str(error),'traceback':detail,
                    'timestamp_unix':time.time(),'pid':os.getpid()})
                print('Controller diagnostics: '+str(path),file=sys.stderr)
            except Exception as diagnostic_error:
                print('Could not save controller diagnostics: '+type(diagnostic_error).__name__,file=sys.stderr)
        return 1

if __name__=='__main__':raise SystemExit(main())
