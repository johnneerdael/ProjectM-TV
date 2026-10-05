import hashlib
import json
import math
from pathlib import Path

from activity_model import FEATURE_NAMES,activity,load_model


def test_refit_uses_actual_native_direct_delta_vectors_and_original_judgments():
    root=Path(__file__).parent
    profile=load_model()
    records=json.loads((root/'profiles/direct-delta-calibration/training-records.json').read_text())['rows']
    feedback=json.loads((root/'profiles/direct-delta-calibration/human-feedback.json').read_text())
    cases={c['sample']:c for c in feedback['cases']}
    assert [r['sample'] for r in records]==[1,2,3,5,6,7,8,10]
    assert profile['feature_names']==FEATURE_NAMES
    assert 'same_pixel' in FEATURE_NAMES[3] and 'matched' not in FEATURE_NAMES[3]
    for record in records:
        row=record['measurement'];case=cases[record['sample']]
        assert row['sha256']==case['preset_sha256'] and row['preset']==case['preset']
        assert record['judgment']==case['human_fit']
        assert row['status']=='scored' and len(row['features'])==4
        value=activity(profile['model'],row['features'],0,0,0)
        lo,hi={'Chill':(0,30),'Normal':(25,75),'Party':(70,math.inf)}[record['judgment']]
        assert lo-1e-6<=value<=hi+1e-6
    assert profile['appearance_accuracy_verified'] is False
    assert profile['leave_one_out']['strict_band_matches']==4
    assert profile['leave_one_out']['within_five_points']==6
