"""Fresh subprocesses verify loaded scorer code cannot receive newer disk identities."""
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


@pytest.mark.parametrize('runner',['core_corpus','beta_score'])
def test_preflight_source_edit_fails_before_device_or_output(tmp_path,runner):
    source=Path(__file__).parent
    for path in source.glob('*.py'):
        if not path.name.startswith('test_'):shutil.copy2(path,tmp_path/path.name)
    (tmp_path/'profiles').mkdir()
    shutil.copy2(source/'profiles/audience-model-direct-delta-v2.json',tmp_path/'profiles')
    code='''
import argparse,json,zipfile
from pathlib import Path
import RUNNER as runner
import java_runtime
root=Path.cwd();runtime=root/'runtime';runtime.mkdir()
for name in ('classes.dex','libprojectmtv.so','libbackendclock.so'):(runtime/name).write_bytes(b'runtime')
(runtime/'jni/armeabi-v7a').mkdir(parents=True)
(runtime/'jni/armeabi-v7a/libprojectmtv.so').write_bytes(b'runtime')
(runtime/'dex').mkdir();(runtime/'dex/classes.dex').write_bytes(b'runtime')
aar=root/'core.aar'
with zipfile.ZipFile(aar,'w') as z:
    for abi in ('arm64-v8a','armeabi-v7a'):z.writestr('jni/'+abi+'/libprojectmtv.so',b'runtime')
pcm=root/'pcm';pcm.write_bytes(b'pcm')
model=root/'model';model.write_text('{"model":{}}')
args=argparse.Namespace(aar=aar,runtime=runtime,pcm=pcm,model=model,output=root/'output',
    owner=root/'owner',device='emulator-test',remote='/unused',limit=0,retry_unscored=False,only_preset=None)
def preflight(*args):
    path=root/'descriptors.py';path.write_text(path.read_text()+'\\n# replaced during preflight\\n')
    return {'policy':'test-only-java-boundary'}
java_runtime.verify_runtime_classes=preflight
def forbidden(*args,**kwargs):raise AssertionError('Changed source reached device')
runner.subprocess.check_output=forbidden
if hasattr(runner,'verify_owner'):runner.verify_owner=forbidden
try:runner.run(args)
except ValueError as error:
    assert 'source' in str(error) and 'changed' in str(error),str(error)
else:raise AssertionError('Changed source accepted')
assert not args.output.exists()
'''.replace('RUNNER',runner)
    result=subprocess.run([sys.executable,'-c',code],cwd=tmp_path,capture_output=True,text=True)
    assert result.returncode==0,result.stderr


def test_scorer_source_edit_before_execution_requires_fresh_import(tmp_path):
    source=Path(__file__).with_name('core_backend.py')
    shutil.copy2(source,tmp_path/source.name)
    code='''
from pathlib import Path
import core_backend
p=Path('core_backend.py');p.write_text(p.read_text()+'\\n# changed after import\\n')
try:core_backend.freeze_scorer_sources()
except ValueError as error:assert 'fresh process' in str(error)
else:raise AssertionError('Old loaded scorer accepted new source')
'''
    result=subprocess.run([sys.executable,'-c',code],cwd=tmp_path,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
