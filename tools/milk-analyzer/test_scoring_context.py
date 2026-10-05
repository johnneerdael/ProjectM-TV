import hashlib
import json
from pathlib import Path


def facts(scorer_hash):
    value={'scorer_sha256':scorer_hash,'aar_sha256':'a'*64,'profile':{'frames':420},
           'model_sha256':'b'*64,'descriptor_sha256':'c'*64,'runtime_sha256':{'input.f32':'d'*64}}
    value['identity']=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
    return value


def test_io_only_fix_can_keep_original_measurement_provenance(tmp_path):
    from scoring_context import compatible_previous
    root=Path(__file__).parent
    old=(root/'profiles/scorers/beta-score-v1.py.txt').read_bytes()
    new=old.replace(b'timer.cancel()',b'timer.cancel()\n        row["diagnostic_errors"]=[]')
    (tmp_path/'profiles/scorers').mkdir(parents=True)
    (tmp_path/'profiles/scorers/beta-score-v1.py.txt').write_bytes(old)
    (tmp_path/'beta_score.py').write_bytes(new)
    previous=facts(hashlib.sha256(old).hexdigest())
    current=facts(hashlib.sha256(new).hexdigest())
    assert compatible_previous(previous,current,tmp_path)


def test_changed_numerical_program_or_inputs_cannot_borrow_old_scores(tmp_path):
    from scoring_context import compatible_previous
    root=Path(__file__).parent
    old=(root/'profiles/scorers/beta-score-v1.py.txt').read_bytes()
    (tmp_path/'profiles/scorers').mkdir(parents=True)
    (tmp_path/'profiles/scorers/beta-score-v1.py.txt').write_bytes(old)
    previous=facts(hashlib.sha256(old).hexdigest())
    for new in [old.replace(b'FRAMES=420',b'FRAMES=300'),old.replace(b'raw=max(base,flash)',b'raw=base')]:
        (tmp_path/'beta_score.py').write_bytes(new)
        assert not compatible_previous(previous,facts(hashlib.sha256(new).hexdigest()),tmp_path)
    (tmp_path/'beta_score.py').write_bytes(old)
    changed=facts(hashlib.sha256(old).hexdigest());changed['aar_sha256']='0'*64
    changed['identity']=hashlib.sha256(json.dumps({k:v for k,v in changed.items() if k!='identity'},sort_keys=True).encode()).hexdigest()
    assert not compatible_previous(previous,changed,tmp_path)
