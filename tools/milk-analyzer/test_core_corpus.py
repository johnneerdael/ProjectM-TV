import json
import pytest

from core_corpus import atomic_json


def test_atomic_result_rejects_nonfinite_scores_without_overwriting_valid_result(tmp_path):
    path=tmp_path/'result.json'
    atomic_json(path,{'score':30,'status':'scored'})
    with pytest.raises(ValueError):atomic_json(path,{'score':float('nan')})
    assert json.loads(path.read_text())=={'score':30,'status':'scored'}


def test_result_update_writes_complete_replacement(tmp_path):
    path=tmp_path/'result.json'
    atomic_json(path,{'status':'unscored','reason':'missing'})
    atomic_json(path,{'status':'scored','score':42})
    assert json.loads(path.read_text())=={'status':'scored','score':42}
    assert not path.with_suffix('.json.tmp').exists()
