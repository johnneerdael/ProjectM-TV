import numpy as np
from pathlib import Path
import pytest


def test_synthetic_signal_is_finite_repeatable_and_has_exact_cadence():
    from corpus_inputs import synthetic_pcm
    a=synthetic_pcm(frames=60,fps=15,seed=12345)
    b=synthetic_pcm(frames=60,fps=15,seed=12345)
    assert len(a)==176400 and a.dtype==np.dtype('<f4')
    np.testing.assert_array_equal(a,b)
    assert np.all(np.isfinite(a)) and np.max(np.abs(a))<=1 and np.std(a)>.05
    with pytest.raises(ValueError):synthetic_pcm(frames=60,fps=17,seed=1)


def test_descriptor_types_and_random_slots_are_declared_consistently(tmp_path):
    from corpus_inputs import texture_index,declared_random_assets,sampler_request
    for name in ['clouds.png','clouds2.jpg','fire.png']:(tmp_path/name).write_bytes(b'image')
    images=texture_index(tmp_path)
    refs={'warp':['main','rand00_clouds'],'composite':['fw_rand00_fire','rand01']}
    selected,aliases=declared_random_assets(refs,images,preset_sha='1'*64,seed=12345)
    assert selected['rand00']['name'].startswith('clouds')
    assert aliases['rand00_clouds']==aliases['rand00_fire']==aliases['rand00']
    assert declared_random_assets(refs,images,preset_sha='1'*64,seed=12345)==(selected,aliases)
    request=sampler_request(['main','noisevol_hq','fc_clouds','rand00_clouds'])
    assert request['sampler_noisevol_hq']=='sampler3D'
    assert request['sampler_fc_clouds']=='sampler2D'
    assert request['sampler_rand00_clouds']=='sampler2D'


def test_missing_filtered_pool_and_ambiguous_names_remain_errors(tmp_path):
    from corpus_inputs import texture_index,declared_random_assets
    (tmp_path/'fire.png').write_bytes(b'1')
    with pytest.raises(ValueError,match='prefix'):
        declared_random_assets({'warp':['rand00_clouds']},texture_index(tmp_path),preset_sha='1'*64,seed=1)
    (tmp_path/'fire.jpg').write_bytes(b'2')
    with pytest.raises(ValueError,match='ambiguous'):texture_index(tmp_path)
