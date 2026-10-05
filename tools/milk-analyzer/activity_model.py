"""Explicit direct-delta beta calibration, separate from measurement producers."""
import hashlib
import json
import math
from pathlib import Path

MODEL_PATH='profiles/audience-model-direct-delta-v2.json'
FEATURE_NAMES=['coherent_luma_transitions_per_second','median_motion_viewports_per_second',
               'mean_acceleration_viewports_per_second_squared',
               'same_pixel_luma_delta_p95_over_30Hz_frame_pairs']


def load_model():
    source=Path(__file__).parent
    profile=json.loads((source/MODEL_PATH).read_text())
    if profile['feature_names']!=FEATURE_NAMES:raise ValueError('Activity feature semantics differ')
    for relative,expected in profile['calibration_sha256'].items():
        if hashlib.sha256((source/relative).read_bytes()).hexdigest()!=expected:
            raise ValueError('Calibration evidence/fitter differs')
    return profile


def scoring_identity():
    source=Path(__file__).parent
    facts={'model_path':MODEL_PATH,'model_sha256':hashlib.sha256((source/MODEL_PATH).read_bytes()).hexdigest(),
           'scoring_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'feature_names':FEATURE_NAMES,'policy':'offline derivation from retained numerical features; original producer identities retained'}
    facts['identity']=hashlib.sha256(json.dumps(facts,sort_keys=True).encode()).hexdigest()
    return facts


def activity(model,features,up,down,peak):
    raw=model['intercept']+sum(w*math.log1p(x)/s for w,x,s in zip(model['weights'],features,model['feature_scale']))
    return max(raw,100*math.sqrt(peak)*min(1,min(up,down)/12))
