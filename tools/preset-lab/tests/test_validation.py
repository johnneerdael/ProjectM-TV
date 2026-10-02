import numpy as np
import pytest

from preset_lab.validation import assess_music_run


def run(levels, warmup=0, coverage=1):
    return {"status":"success","fps":30,"warmup_frames":warmup,"prefix_sha256":"a"*64,
            "frames":[{"brightness":float(level),"coverage":coverage,"contrast":.2,
                       "saturation":.5,"motion_speed":.1,"motion_density":.4,
                       "edge_energy":.01,"frame_change":.01,"clipping_ratio":0}
                       for level in levels]}


def test_actual_music_comparison_records_observed_features_and_causal_evidence():
    baseline=run(np.ones(300)*.2)
    levels=np.ones(300)*.2
    onsets=[20,61,103,150,202,261]
    levels[np.array(onsets)+3]+=.5
    result=assess_music_run(run(levels),baseline,[i/30 for i in onsets])
    assert result["status"]=="success"
    assert result["response"]>0
    assert result["beat_evidence"]["strength"]>.8
    assert result["observed_features"]["beat_lock"]>.8
    assert result["music_fit"]>0


def test_unrelated_intrinsic_motion_does_not_earn_music_response():
    levels=.4+.2*np.sin(np.arange(300)/4)
    result=assess_music_run(run(levels),run(levels),[1,2,3,4,5])
    assert result["response"]==pytest.approx(0)
    assert result["beat_evidence"]["strength"]==0


def test_warmup_pixel_drift_blocks_actual_music_validation():
    baseline=run(np.ones(300)*.2,warmup=120)
    candidate=run(np.ones(300)*.3,warmup=120)
    candidate["prefix_sha256"]="b"*64
    result=assess_music_run(candidate,baseline,[5,6,7])
    assert result["status"]=="failed"
    assert "pre_intervention_drift" in result["reasons"]
