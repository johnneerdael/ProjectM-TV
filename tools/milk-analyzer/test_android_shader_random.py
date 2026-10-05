"""Target random banks must retain Android identity and explicit lifecycle."""
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from shader_random import bind_random_uniforms,execute_ledger
from test_shader_random import BINARY,create,load,run


def test_android_execution_requires_an_explicit_safe_device_identifier():
    for serial in [None,'','device;echo wrong']:
        with pytest.raises(ValueError,match='serial'):
            execute_ledger(BINARY,seed=12345,events=[],adb=Path('/unused/adb'),serial=serial)


def test_android_execution_rejects_a_host_rng_profile(monkeypatch):
    result=run([create('warp'),load('warp')])
    monkeypatch.setattr('shader_random.subprocess.run',lambda *a,**k:
                        SimpleNamespace(returncode=0,stdout=json.dumps(result),stderr=''))
    with pytest.raises(ValueError,match='Android/bionic'):
        execute_ledger(BINARY,seed=12345,events=[create('warp'),load('warp')],
                       adb=Path('/unused/adb'),serial='emulator-5582')


@pytest.mark.parametrize('phase',['prepare','execute','cleanup'])
def test_android_command_failure_is_not_accepted_as_a_uniform_bank(monkeypatch,phase):
    result=run([create('warp'),load('warp')])
    result['profile']['platform']='Android/bionic'
    def command(args,**kwargs):
        failed=((phase=='prepare' and 'mkdir' in args) or
                (phase=='execute' and args[-2].endswith('/adapter')) or
                (phase=='cleanup' and 'rm' in args))
        # Model the observed ADB protocol distinction: exec-out reports success
        # after copying valid output even when the remote command exits 7.
        return SimpleNamespace(returncode=7 if failed and 'exec-out' not in args else 0,
                               stdout=json.dumps(result),stderr='reference failure' if failed else '')
    monkeypatch.setattr('shader_random.subprocess.run',command)
    with pytest.raises(ValueError,match='command failed'):
        execute_ledger(BINARY,seed=12345,events=[create('warp'),load('warp')],
                       adb=Path('/unused/adb'),serial='emulator-5582')


def test_recorded_android_bank_uses_target_profile_and_reaches_shader_math():
    proof=json.loads((Path(__file__).parent/'fixtures/android-shader-random-proof-2026-10-04.json').read_text())
    ledger=proof['ledger'];profile=ledger['profile']
    assert profile['platform']=='Android/bionic'
    bank=bind_random_uniforms(ledger,event_index=2,shader_id='warp',time=0,profile=profile)
    np.testing.assert_array_equal(bank['rand_preset'],
        [.6715447306632996,.16747967898845673,.5043360590934753,.33265581727027893])
    with pytest.raises(ValueError,match='profile'):
        bind_random_uniforms(ledger,event_index=2,shader_id='warp',time=0,profile=proof['host_profile'])
    from test_pipeline_fields import trees
    from shader_fields import ShaderFields
    from field_math import evaluate
    from grid_math import evaluate_grid
    _,tree=trees('ret=.5;','ret=mul(float4(.2,.3,.4,1),rot_s1);')
    model=ShaderFields(stage='composite',frame=0,warp_reads_blur=False)
    field=model.lower(tree)
    assert model.complete,model.unknown
    expected=np.array([.2,.3,.4,1],dtype=np.float32)@np.array(bank['rot_s1'],dtype=np.float32)
    np.testing.assert_allclose(evaluate(field,inputs=bank),expected,atol=1e-7)
    np.testing.assert_allclose(evaluate_grid(field,batch_shape=(2,),inputs=bank),[expected,expected],atol=1e-7)
