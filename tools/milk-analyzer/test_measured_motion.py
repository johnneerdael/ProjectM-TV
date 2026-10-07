import importlib
import json
import hashlib
from pathlib import Path

import numpy as np
import pytest

def identity():
    return json.loads((Path(__file__).parent/'fixtures/measured-motion-operator-bound-v2-2026-10-07.json').read_text())['identity']

def sha(values):
    return hashlib.sha256(np.asarray(values,dtype='<f4').tobytes()).hexdigest()

def executor(field, queries, **settings):
    values=queries.copy()
    values[:,1]=1-values[:,1]
    return values,dict(identity=identity(),core_frame_serial_before=0,core_frame_serial_after=0,
        preset_draws=0,input_map_sha256=sha(field),input_queries_sha256=sha(queries),output_sha256=sha(values),physical_map_sha256=sha(field[::-1]),
        executor_source_sha256=identity()['executor_source_sha256'])

def test_sampler_seals_exact_inputs_outputs_and_declares_measured_basis(tmp_path):
    module=importlib.import_module('measured_motion')
    sampler=module.MeasuredMotionSampler(executor,identity=identity(),directory=tmp_path/'operator')
    field=np.zeros((8,8,2),np.float32);queries=np.array([[.25,.75]],np.float32)
    actual=sampler(field,queries,wrap=False,linear=True,origin='bottom')
    np.testing.assert_array_equal(actual,[[.25,.25]])
    report=sampler.report()
    assert report['basis']=='source-with-measured-operator'
    assert report['call_count']==1
    assert report['calls'][0]['input_map_sha256']==sha(field)
    assert report['calls'][0]['input_queries_sha256']==sha(queries)
    for name,digest in report['calls'][0]['files'].items():
        assert hashlib.sha256((tmp_path/'operator'/name).read_bytes()).hexdigest()==digest

@pytest.mark.parametrize('change',[{'core_frame_serial_after':1},{'preset_draws':1},
    {'input_map_sha256':'0'*64},{'identity':{}},{'core_frame_serial_before':False},{'physical_map_sha256':'0'*64},
    {'executor_source_sha256':'0'*64}])
def test_sampler_rejects_unbound_or_rendered_results(tmp_path,change):
    module=importlib.import_module('measured_motion')
    def invalid(field,queries,**settings):
        values,proof=executor(field,queries,**settings);proof.update(change);return values,proof
    sampler=module.MeasuredMotionSampler(invalid,identity=identity(),directory=tmp_path/'operator')
    with pytest.raises(ValueError,match='operator'):
        sampler(np.zeros((8,8,2),np.float32),np.array([[.25,.75]],np.float32),
                wrap=False,linear=True,origin='bottom')
    assert sampler.report()['call_count']==0

def test_sampler_rejects_nonhalf_inputs_and_wrong_addressing(tmp_path):
    module=importlib.import_module('measured_motion')
    sampler=module.MeasuredMotionSampler(executor,identity=identity(),directory=tmp_path/'operator')
    for field in [np.full((8,8,2),.123456,np.float32),np.full((8,8,2),np.inf,np.float32)]:
        with pytest.raises(ValueError,match='half'):
            sampler(field,np.array([[.25,.75]],np.float32),wrap=False,linear=True,origin='bottom')
    with pytest.raises(ValueError,match='addressing'):
        sampler(np.zeros((8,8,2),np.float32),np.array([[.25,.75]],np.float32),
                wrap=True,linear=True,origin='bottom')

def test_operator_identity_is_pinned_to_published_core_and_source(tmp_path):
    module=importlib.import_module('measured_motion')
    for key in ['aar_sha256','native_sha256','classes_dex_sha256','operator_source_sha256']:
        altered=identity();altered[key]='0'*64
        with pytest.raises(ValueError,match='identity'):
            module.MeasuredMotionSampler(executor,identity=altered,directory=tmp_path/key)


def test_runtime_hashes_cannot_relabel_new_deployment_as_old_qualified_core():
    module=importlib.import_module('native_motion_executor')
    ident=identity()
    observed={'published-core.aar':ident['aar_sha256'],'libprojectmtv.so':ident['native_sha256'],
              'classes.dex':ident['classes_dex_sha256'],'motion-operator.dex':ident['operator_dex_sha256']}
    module.verify_runtime_hashes(ident,observed)
    for name in observed:
        changed=dict(observed);changed[name]='0'*64
        with pytest.raises(ValueError,match='qualified'):
            module.verify_runtime_hashes(ident,changed)

def test_consumed_native_input_hashes_are_required():
    module=importlib.import_module('native_motion_executor')
    with pytest.raises(ValueError,match='consumed'):
        module.verify_consumed_inputs({},map_sha256='a'*64,queries_sha256='b'*64,output_sha256='c'*64)
    correct={'physical_map_sha256':'a'*64,'input_queries_sha256':'b'*64,'output_sha256':'c'*64}
    module.verify_consumed_inputs(correct,map_sha256='a'*64,queries_sha256='b'*64,output_sha256='c'*64)


def test_owned_executors_use_distinct_remote_namespaces(tmp_path):
    from native_motion_executor import Executor
    kwargs=dict(adb='adb',serial='task-owned-device',owner_pid=123,owner_avd='task-owned-avd',
                remote='/data/local/tmp/task',identity=identity(),deployment={'sha256':{}})
    first=Executor(directory=tmp_path/'first',**kwargs)
    second=Executor(directory=tmp_path/'second',**kwargs)
    assert first.namespace!=second.namespace

def test_saved_operator_evidence_cannot_be_changed_after_sampling(tmp_path):
    from measured_motion import MeasuredMotionSampler
    sampler=MeasuredMotionSampler(executor,identity=identity(),directory=tmp_path/'operator')
    sampler(np.zeros((8,8,2),np.float32),np.array([[.25,.75]],np.float32),
            wrap=False,linear=True,origin='bottom')
    (tmp_path/'operator/000000/output.f32').write_bytes(b'changed')
    with pytest.raises(ValueError,match='evidence changed'):
        sampler.report()
