"""Frozen cohort validation cannot substitute sources or compiler inputs."""
import pytest
from corpus_store import digest


def test_saved_compatibility_index_requires_valid_seals_and_unique_sources(tmp_path):
    from static_behaviour_validate import compatibility_index
    import json
    value={'preset':{'sha256':'a'*64},'reports':{},'engine':{},'engine_archive_sha256':'b'*64}
    value['record_sha256']=digest(value)
    (tmp_path/'one.json').write_text(json.dumps(value))
    indexed=compatibility_index(tmp_path)
    assert 'a'*64 in indexed
    (tmp_path/'two.json').write_text(json.dumps(value))
    with pytest.raises(ValueError,match='duplicate'):compatibility_index(tmp_path)


def test_saved_compatibility_mutation_is_rejected(tmp_path):
    from static_behaviour_validate import compatibility_index
    import json
    value={'preset':{'sha256':'a'*64},'reports':{}}
    value['record_sha256']=digest(value);value['reports']['composite']={}
    (tmp_path/'one.json').write_text(json.dumps(value))
    with pytest.raises(ValueError,match='seal'):compatibility_index(tmp_path)


def test_worker_initialization_activates_declared_math_components(tmp_path):
    import sys
    import static_behaviour_validate as runner
    from source_symbolic import active_identity as sympy_identity
    from source_proofs import active_identity as proof_identity
    reader=tmp_path/'reader';reader.write_bytes(b'isolated-reader')
    try:
        runner.initialize(reader,{}, {}, {}, sys.executable,sys.executable)
        assert sympy_identity()['policy']=='source-sympy-nominal-response-v1'
        assert proof_identity()['policy']=='source-z3-qualified-domain-evidence-v1'
    finally:
        if hasattr(runner,'_SESSIONS'):runner._SESSIONS.close()
