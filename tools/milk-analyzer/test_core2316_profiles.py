"""The additive texture-ownership patch shares established scalar/geometry math."""
import pytest
from engine_profiles import CORE_2315_ENGINE,CORE_2315_BLUR,LEGACY_BLUR,matches,select_policy
from forecast import source_main_binding_policy,source_shape_sampler_policy
from engine_profiles import CORE_2315_SHAPE

ENGINE50={'commit':'e0b0a967f0ffd7d332106c366668ed271718472b',
          'patches_sha256':'cd01f0f3cce4f6be05d781b06192dadadbd8254a6fa1c03ea52394d3e48f9ded'}


def test_exact50_patch_source_uses_shared_verified_math_without_relabelling49():
    assert matches(ENGINE50)
    assert not matches(ENGINE50,CORE_2315_ENGINE)
    assert matches(CORE_2315_ENGINE)
    assert select_policy(ENGINE50,None,current=CORE_2315_BLUR,legacy=LEGACY_BLUR)==CORE_2315_BLUR


def test_new_cold_load_keeps_current_main_and_shape_sampler_policies():
    assert source_main_binding_policy(ENGINE50,None)=='projectmtv-core-2.2.6-v1'
    assert source_shape_sampler_policy(ENGINE50,None)==CORE_2315_SHAPE


def test_unknown_source_does_not_inherit_new_compatibility_from_version_label():
    unknown={**ENGINE50,'patches_sha256':'0'*64}
    assert not matches(unknown)
    assert select_policy(unknown,None,current=CORE_2315_BLUR,legacy=LEGACY_BLUR)==LEGACY_BLUR
    with pytest.raises(ValueError,match='engine identity'):
        select_policy(unknown,CORE_2315_BLUR,current=CORE_2315_BLUR,legacy=LEGACY_BLUR)


def test_prepared50_adapter_executes_live_wave_controls_without_static_fallback(tmp_path):
    import os,json,subprocess
    from pathlib import Path
    from test_native_wave import frame
    folder=Path(os.environ.get('MILK_TEST_2316_BINARIES',Path(__file__).resolve().parents[2]/'build/visual-loop/source50/adapters'))
    if not (folder/'milk-wave-inputs').is_file():pytest.skip('prepared50-patch adapters required')
    settings=frame();settings.update(wave_mode=6,wave_a=.5)
    request=tmp_path/'wave.json';output=tmp_path/'out.json'
    request.write_text(json.dumps({'mode':0,'mode_policy':'evaluated-live-v1','frames':[settings],'output':str(output)}))
    result=subprocess.run([str(folder/'milk-wave-inputs'),str(request)],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    report=json.loads(output.read_text())
    assert report['engine_identity']['patches_sha256']==ENGINE50['patches_sha256']
    assert report['frames'][0]['mode']==6
    assert not report['frames'][0]['omitted']
