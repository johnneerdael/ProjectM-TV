import subprocess
import sys
import time
from pathlib import Path
import pytest


def test_stop_process_terminates_own_process_group(tmp_path):
    from preset_corpus import stop_process
    marker=tmp_path/'child-finished'
    child="import time;from pathlib import Path;time.sleep(2);Path("+repr(str(marker))+").write_text('unexpected')"
    parent="import subprocess,sys,time;subprocess.Popen([sys.executable,'-c',"+repr(child)+"]);print('ready',flush=True);time.sleep(30)"
    process=subprocess.Popen([sys.executable,'-c',parent],stdout=subprocess.PIPE,text=True,start_new_session=True)
    assert process.stdout.readline().strip()=='ready'
    stop_process(process)
    assert process.poll() is not None
    time.sleep(2.1)
    assert not marker.exists()
    stop_process(process) # completed handle is safe and cannot target another process


def test_defaults_are_requested_corpus_settings_and_unsupported_sizes_reject():
    from preset_corpus import parse_args
    args=parse_args([])
    assert (args.frames,args.fps,args.width,args.height,args.batch_size)==(60,15,854,480,100)
    assert args.output.name=='ProjectM-TV-preset-corpus-15fps-480p'
    with pytest.raises(SystemExit):parse_args(['--width','1280','--height','720'])
    with pytest.raises(SystemExit):parse_args(['--workers','0'])


def test_worker_exit_without_result_is_preserved_as_failure(tmp_path):
    from preset_corpus import finish_process
    out=tmp_path/'out';err=tmp_path/'err';stdout=out.open('wb');stderr=err.open('wb')
    process=subprocess.Popen([sys.executable,'-c',"import sys;print('failure',file=sys.stderr);raise SystemExit(4)"],stdout=stdout,stderr=stderr,start_new_session=True)
    process.wait()
    task=dict(process=process,stdout=stdout,stderr=stderr,stdout_path=out,stderr_path=err,
        result=tmp_path/'absent',started=time.monotonic(),configuration={'simulation':{'frames':60,'fps':15}})
    result=finish_process(task)
    assert result['status']=='error' and result['feature_record'] is None
    assert result['exit_code']==4 and 'failure' in result['stderr_tail']


def test_nonfinite_deadlines_are_rejected():
    from preset_corpus import parse_args
    for name,value in [('--timeout','nan'),('--timeout','inf'),('--equation-timeout','nan')]:
        with pytest.raises(SystemExit):parse_args([name,value])


def test_stop_process_cleans_descendants_after_leader_exit(tmp_path):
    from preset_corpus import stop_process
    marker=tmp_path/'escaped';ready=tmp_path/'ready'
    child="import signal,time;from pathlib import Path;signal.signal(signal.SIGTERM,signal.SIG_IGN);Path("+repr(str(ready))+").touch();time.sleep(2);Path("+repr(str(marker))+").touch()"
    parent="import subprocess,sys;subprocess.Popen([sys.executable,'-c',"+repr(child)+"])"
    process=subprocess.Popen([sys.executable,'-c',parent],start_new_session=True)
    process.wait(timeout=5)
    deadline=time.monotonic()+5
    while not ready.exists() and time.monotonic()<deadline:time.sleep(.02)
    assert ready.exists()
    stop_process(process);time.sleep(2)
    assert not marker.exists()


def test_preparation_identity_survives_before_run_manifest(tmp_path):
    from preset_corpus import preparation_guard
    from corpus_store import atomic_json
    inputs=tmp_path/'inputs';identity={'pcm_sha256':'old','adapter':'one'}
    preparation_guard(inputs,identity)
    atomic_json(inputs/'manifest.json',{'frames':60,'fps':15,'seed':12345})
    preparation_guard(inputs,identity)
    with pytest.raises(ValueError,match='preparation identity changed'):
        preparation_guard(inputs,{**identity,'pcm_sha256':'new'})
    (inputs/'preparation-identity.json').unlink()
    with pytest.raises(ValueError,match='unattributed'):
        preparation_guard(inputs,identity)


def test_frozen_manifest_validator_and_assets_reject_drift(tmp_path):
    from preset_corpus import verify_frozen
    from forecast import model_file_hashes
    from corpus_store import atomic_json,file_hash
    inputs=tmp_path/'inputs';adapter=tmp_path/'adapter';validator=tmp_path/'validator';asset=tmp_path/'texture'
    adapter.write_text('adapter');validator.write_text('validator');asset.write_text('asset')
    atomic_json(inputs/'manifest.json',{'files':{},'textures':{'one':{'path':str(asset),'sha256':file_hash(asset)}}})
    config=dict(model_modules=model_file_hashes(),binaries=str(tmp_path),binary_sha256={'adapter':file_hash(adapter)},
        validator=str(validator),validator_sha256=file_hash(validator),inputs=str(inputs),prepared_inputs_sha256=file_hash(inputs/'manifest.json'))
    verify_frozen(config)
    validator.write_text('changed')
    with pytest.raises(ValueError,match='validator'):verify_frozen(config)
    validator.write_text('validator');asset.write_text('changed')
    with pytest.raises(ValueError,match='texture'):verify_frozen(config)
    asset.write_text('asset');(inputs/'manifest.json').write_text('{}')
    with pytest.raises(ValueError,match='manifest'):verify_frozen(config)
