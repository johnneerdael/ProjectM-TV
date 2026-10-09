"""Release31 raw noise admission preserves the unchanged source generator."""
import hashlib,json,subprocess
from pathlib import Path
import pytest
from test_core2331_warp import BINARIES,ROOT
from engine_profiles import CORE_2331_ENGINE

NAMES=['noise_lq','noise_lq_lite','noise_mq','noise_hq','noisevol_lq','noisevol_hq']


def generate(folder,tmp_path,label,policy='production-clock-seed-v1'):
    output=tmp_path/label;request=tmp_path/(label+'.json')
    request.write_text(json.dumps({'seed':12345,'seed_policy':policy,'names':NAMES,'output':str(output)}))
    result=subprocess.run([str(folder/'milk-noise-inputs'),str(request)],capture_output=True,text=True)
    return result,output


def test_exact31_raw_seed_and_all_six_noise_banks_match_unchanged29(tmp_path):
    source=ROOT/'build/preset-corpus'
    path=Path('src/libprojectM/Renderer/MilkdropNoise.cpp')
    assert (source/'source31/production-engine'/path).read_bytes()==(source/'source29/production-engine'/path).read_bytes()
    result,new=generate(BINARIES,tmp_path,'new')
    assert result.returncode==0,result.stderr
    result,old=generate(source/'source29/adapters',tmp_path,'old')
    assert result.returncode==0,result.stderr
    manifest=json.loads((new/'manifest.json').read_text())
    assert manifest['engine_identity']==CORE_2331_ENGINE
    assert manifest['seed_model']=='raw-declared-native-noise-v1'
    for name in NAMES:
        assert (new/(name+'.u32le')).read_bytes()==(old/(name+'.u32le')).read_bytes()
        assert manifest['textures'][name]['generator_seed']==12345


@pytest.mark.parametrize('policy',['lab-subsystem-seed-v1','invented'])
def test_source31_noise_rejects_unqualified_seed_policy(tmp_path,policy):
    result,output=generate(BINARIES,tmp_path,'bad',policy)
    assert result.returncode!=0
    assert not (output/'manifest.json').exists()
