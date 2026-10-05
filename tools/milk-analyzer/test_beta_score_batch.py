import hashlib
import json
import shlex
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
import beta_score as scorer


@pytest.fixture
def batch(tmp_path,monkeypatch):
    runtime=tmp_path/'runtime';runtime.mkdir()
    files={name:runtime/name for name in ('classes.dex','libbackendclock.so','libprojectmtv.so')}
    for name,path in files.items():path.write_bytes(name.encode())
    aar=tmp_path/'core.aar'
    with zipfile.ZipFile(aar,'w') as z:
        z.writestr('jni/arm64-v8a/libprojectmtv.so',files['libprojectmtv.so'].read_bytes())
        for name in ('a.milk','b.milk'):z.writestr('assets/presets/'+name,name)
    pcm=tmp_path/'input.f32';pcm.write_bytes(b'pcm')
    files.update({'core.aar':aar,'input.f32':pcm})
    output=tmp_path/'output'
    argv=['scorer','--aar',str(aar),'--runtime',str(runtime),'--pcm',str(pcm),
          '--owner',str(tmp_path/'owner'),'--device','emulator-test','--remote','/owned','--output',str(output)]
    monkeypatch.setattr(sys,'argv',argv)
    monkeypatch.setattr(scorer,'verify_owner',lambda *args:{})
    monkeypatch.setattr(scorer.subprocess,'run',lambda *args,**kwargs:subprocess.CompletedProcess(args,0))
    def remote_hash(command,**kwargs):
        name=Path(shlex.split(command[-1])[-1]).name
        return hashlib.sha256(files[name].read_bytes()).hexdigest()+'  '+name
    monkeypatch.setattr(scorer.subprocess,'check_output',remote_hash)
    calls=[]
    def measure(case,args,identity,model):
        calls.append(case['preset'])
        row={**case,'identity':identity,'status':'unscored','raw_activity':None,'reason':'controlled failure'}
        scorer.write_json(output/'results'/(case['sha256']+'.json'),row)
        return row
    monkeypatch.setattr(scorer,'measure',measure)
    return output,argv,calls


def test_first_failed_measurement_stops_batch_immediately(batch):
    output,argv,calls=batch
    with pytest.raises(RuntimeError,match='diagnose'):scorer.main()
    assert calls==['a.milk']
    assert json.loads((output/'progress.json').read_text())['unscored']==1


def test_unresolved_failure_cannot_be_skipped_to_continue_original_goal(batch):
    output,argv,calls=batch
    with pytest.raises(RuntimeError):scorer.main()
    calls.clear()
    with pytest.raises(ValueError,match='Resolve retained failures'):scorer.main()
    assert calls==[]


def test_diagnosed_single_case_retry_precedes_remaining_batch(batch,monkeypatch):
    output,argv,calls=batch
    with pytest.raises(RuntimeError):scorer.main()
    calls.clear()
    def repaired(case,args,identity,model):
        calls.append(case['preset'])
        row={**case,'identity':identity,'status':'scored','raw_activity':1.}
        scorer.write_json(output/'results'/(case['sha256']+'.json'),row)
        return row
    monkeypatch.setattr(scorer,'measure',repaired)
    monkeypatch.setattr(sys,'argv',argv+['--retry-unscored','--only-preset','a.milk'])
    scorer.main()
    assert calls==['a.milk']
    assert json.loads((output/'progress.json').read_text())['unscored']==0
    monkeypatch.setattr(sys,'argv',argv)
    scorer.main()
    assert calls==['a.milk','b.milk']
    assert json.loads((output/'progress.json').read_text())['complete'] is True


def test_retry_cannot_select_unmeasured_case_while_failure_remains(batch,monkeypatch):
    output,argv,calls=batch
    with pytest.raises(RuntimeError):scorer.main()
    calls.clear()
    monkeypatch.setattr(sys,'argv',argv+['--retry-unscored','--only-preset','b.milk'])
    with pytest.raises(ValueError,match='unresolved'):scorer.main()
    assert calls==[]


def test_retry_without_selection_only_repairs_existing_failures(batch,monkeypatch):
    output,argv,calls=batch
    monkeypatch.setattr(sys,'argv',argv+['--only-preset','b.milk'])
    with pytest.raises(RuntimeError):scorer.main()
    calls.clear()
    def repaired(case,args,identity,model):
        calls.append(case['preset'])
        row={**case,'identity':identity,'status':'scored','raw_activity':1.}
        scorer.write_json(output/'results'/(case['sha256']+'.json'),row)
        return row
    monkeypatch.setattr(scorer,'measure',repaired)
    monkeypatch.setattr(sys,'argv',argv+['--retry-unscored'])
    scorer.main()
    assert calls==['b.milk']
    assert json.loads((output/'progress.json').read_text())['complete'] is False
