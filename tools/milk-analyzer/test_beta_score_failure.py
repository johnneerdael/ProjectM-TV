import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import beta_score as scorer


@pytest.mark.parametrize('status',['scored','unscored'])
@pytest.mark.parametrize('operation',['pull','cleanup'])
def test_diagnostic_timeout_preserves_primary_outcome(tmp_path,monkeypatch,status,operation):
    for folder in ('overlays','logs','metadata','results'):(tmp_path/folder).mkdir()
    case={'preset':'control.milk','sha256':'a'*64}
    args=SimpleNamespace(output=tmp_path,remote='/task-owned',device='emulator-test')
    class Process:
        stdout=io.BytesIO()
        stderr=io.BytesIO()
        def poll(self):return 0
        def wait(self,**kwargs):return 0
        def kill(self):raise AssertionError('Finished process must not be killed')
    monkeypatch.setattr(scorer.subprocess,'Popen',lambda *a,**kw:Process())
    if status=='scored':
        monkeypatch.setattr(scorer,'read_header',lambda *a,**kw:{'pid':123})
        monkeypatch.setattr(scorer,'read_frames',lambda *a,**kw:iter([np.zeros((72,128,3),dtype=np.uint8)]*420))
    def run(command,**kwargs):
        if command[3]=='pull' and command[4].endswith('.json'):
            Path(command[5]).write_text(json.dumps({'preset':case['preset'],'frames':420}))
        elif (operation=='pull' and command[3]=='pull'
              or operation=='cleanup' and command[-1].startswith('rm -f ')):
            raise subprocess.TimeoutExpired(command,kwargs.get('timeout'))
        return subprocess.CompletedProcess(command,0,stdout=b'',stderr=b'')
    monkeypatch.setattr(scorer.subprocess,'run',run)
    model={'intercept':1.,'weights':[1.]*4,'feature_scale':[1.]*4}
    row=scorer.measure(case,args,'frozen-identity',model)
    assert row['status']==status
    assert row['diagnostic_errors']
    saved=json.loads((tmp_path/'results'/(case['sha256']+'.json')).read_text())
    assert saved==row
    if status=='unscored':
        assert saved['raw_activity'] is None and 'Truncated' in saved['reason']


@pytest.mark.parametrize('error_kind',['timeout','oserror'])
def test_runner_timeout_kills_local_child_even_when_remote_kill_fails(tmp_path,monkeypatch,error_kind):
    for folder in ('overlays','logs','metadata','results'):(tmp_path/folder).mkdir()
    case={'preset':'control.milk','sha256':'a'*64}
    args=SimpleNamespace(output=tmp_path,remote='/task-owned',device='emulator-test')
    class Process:
        stdout=io.BytesIO()
        stderr=io.BytesIO()
        killed=False
        def poll(self):return -9 if self.killed else None
        def wait(self,**kwargs):return -9
        def kill(self):self.killed=True
    process=Process()
    callbacks=[]
    class Timer:
        def __init__(self,seconds,callback):callbacks.append(callback)
        def start(self):pass
        def cancel(self):pass
        def join(self):pass
    monkeypatch.setattr(scorer.threading,'Timer',Timer)
    monkeypatch.setattr(scorer.subprocess,'Popen',lambda *a,**kw:process)
    monkeypatch.setattr(scorer,'read_header',lambda *a,**kw:{'pid':123})
    def frames(*a,**kw):
        callbacks[0]()
        assert process.killed
        raise ValueError('Truncated after timeout')
    monkeypatch.setattr(scorer,'read_frames',frames)
    def run(command,**kwargs):
        if command[-1]=='kill 123':
            if error_kind=='timeout':raise subprocess.TimeoutExpired(command,10)
            raise OSError('ADB unavailable')
        return subprocess.CompletedProcess(command,0,stdout=b'',stderr=b'')
    monkeypatch.setattr(scorer.subprocess,'run',run)
    row=scorer.measure(case,args,'frozen-identity',{})
    assert process.killed
    assert row['status']=='unscored' and row['reason']=='Runner timeout'
    assert any(e['operation']=='timeout remote kill' for e in row['diagnostic_errors'])


def test_required_metadata_pull_has_timeout_and_records_failure(tmp_path,monkeypatch):
    for folder in ('overlays','logs','metadata','results'):(tmp_path/folder).mkdir()
    case={'preset':'control.milk','sha256':'a'*64}
    args=SimpleNamespace(output=tmp_path,remote='/task-owned',device='emulator-test')
    class Process:
        stdout=io.BytesIO()
        stderr=io.BytesIO()
        def poll(self):return 0
        def wait(self,**kwargs):return 0
        def kill(self):raise AssertionError('Runner already exited')
    monkeypatch.setattr(scorer.subprocess,'Popen',lambda *a,**kw:Process())
    monkeypatch.setattr(scorer,'read_header',lambda *a,**kw:{'pid':123})
    monkeypatch.setattr(scorer,'read_frames',lambda *a,**kw:iter([np.zeros((72,128,3),dtype=np.uint8)]*420))
    def run(command,**kwargs):
        if command[3]=='pull' and command[4].endswith('.json'):
            assert kwargs.get('timeout')==15
            raise subprocess.TimeoutExpired(command,15)
        return subprocess.CompletedProcess(command,0,stdout=b'',stderr=b'')
    monkeypatch.setattr(scorer.subprocess,'run',run)
    row=scorer.measure(case,args,'frozen-identity',{})
    assert row['status']=='unscored' and row['raw_activity'] is None
    assert 'timed out' in row['reason']
    assert json.loads((tmp_path/'results'/(case['sha256']+'.json')).read_text())==row
