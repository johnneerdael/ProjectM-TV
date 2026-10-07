import importlib
import json
import hashlib
from pathlib import Path

import numpy as np
import pytest

def identity():
    return json.loads((Path(__file__).parent/'fixtures/measured-motion-operator-qualification-2026-10-07.json').read_text())['identity']

def sha(values):
    return hashlib.sha256(np.asarray(values,dtype='<f4').tobytes()).hexdigest()

def executor(field, queries, **settings):
    values=queries.copy()
    values[:,1]=1-values[:,1]
    return values,dict(identity=identity(),core_frame_serial_before=0,core_frame_serial_after=0,
        preset_draws=0,input_map_sha256=sha(field),input_queries_sha256=sha(queries),output_sha256=sha(values))

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
    {'input_map_sha256':'0'*64},{'identity':{}},{'core_frame_serial_before':False}])
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
