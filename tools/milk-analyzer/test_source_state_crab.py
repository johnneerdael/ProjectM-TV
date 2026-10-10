"""Actual fixed-source clamp fragment and transfer-removal counterexample."""
import os
from pathlib import Path

import pytest

from source_state_crab import infer_clamp_candidate


@pytest.fixture
def actual_fragment():
    from forecast import read_source
    root=Path(__file__).resolve().parents[2];worker=os.environ.get('SOURCE_STATE_CRAB_WORKER')
    if not worker:pytest.skip('optional Crab candidate worker not configured')
    source=read_source(root/'core/src/main/assets/presets/Martin - Pixies Party (Hakan mash-up) 6-10.milk',
                       reader=root/'build/preset-corpus/source34/adapters/milk-native-reader')
    return source,dict(frame_fragment='y0 = max(-.5,min(0.5,y0 + vy0*dt)) ; reg05 = y0;',
                       init_fragment='x0 = (rand(10)-5)*.03; y0 = (rand(10)-5)*.03; z0 = (rand(10)-5)*.03;',
                       initial_interval=['-3/20','3/25'],clamp_bounds=['-1/2','1/2'],worker=worker)


def test_actual_clamp_fixpoint_is_a_candidate_and_removed_clamp_is_unbounded(actual_fragment):
    source,kwargs=actual_fragment;r=infer_clamp_candidate(source,**kwargs)
    assert r['inference']['header_interval']=='[-1/2, 1/2]'
    assert r['inference']['postframe_interval']=='[-1/2, 1/2]'
    assert r['source_model_mapping_verified'] is False
    assert r['candidate_only'] is True
    mutation=infer_clamp_candidate(source,**kwargs,mutate_clamp=True)
    assert mutation['inference']['postframe_interval']=='[-oo, +oo]'


def test_source_and_domain_mutations_rejected(actual_fragment):
    source,kwargs=actual_fragment
    with pytest.raises(ValueError,match='source fragment'):
        infer_clamp_candidate(source,**{**kwargs,'frame_fragment':'y0=y0+1;'})
    with pytest.raises(ValueError,match='ordered'):
        infer_clamp_candidate(source,**{**kwargs,'clamp_bounds':['1','-1']})
