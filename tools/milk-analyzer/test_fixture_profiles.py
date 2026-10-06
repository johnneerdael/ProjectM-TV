"""Historical regression profiles must never borrow current native semantics."""
import copy
import pytest
from analyzer_test_profiles import PROFILES, validate_identity


@pytest.mark.parametrize('profile', ['legacy_pre30', 'merged32', 'merged35', 'merged37'])
def test_profile_identity_rejects_borrowed_engine_and_archive(profile):
    metadata = copy.deepcopy(PROFILES[profile])
    validate_identity(profile, metadata)
    for path in [('engine_archive_sha256',), ('engine', 'patches_sha256'),
                 ('engine', 'instrumentation_sha256'), ('engine', 'commit'),
                 ('shader_header_sha256',)]:
        stale = copy.deepcopy(metadata)
        target = stale
        for name in path[:-1]:
            target = target[name]
        target[path[-1]] = '0' * 64
        with pytest.raises(AssertionError, match=profile):
            validate_identity(profile, stale)


def test_unknown_profile_is_not_a_latest_alias():
    with pytest.raises(ValueError, match='profile'):
        validate_identity('latest', {})



def test_historical_source_rejects_missing_request_instead_of_falling_back(tmp_path,monkeypatch):
    import analyzer_test_profiles as profiles
    monkeypatch.setattr(profiles,'FIXTURES',tmp_path)
    with pytest.raises(AssertionError,match='missing source-bound historical fixture'):
        profiles.historical_read('legacy_pre30','per_frame_1=q1=123456789;\n')


@pytest.mark.parametrize('mutation',['request','payload','archive'])
def test_historical_source_rejects_stale_record(tmp_path,monkeypatch,mutation):
    import hashlib,json
    import analyzer_test_profiles as profiles
    original=next((profiles.FIXTURES/'legacy_pre30').glob('reader-*.json'))
    record=json.loads(original.read_text())
    raw=bytes.fromhex(record['request']['source_hex'])
    if mutation=='request':
        record['request']['source_hex']='00'
    elif mutation=='payload':
        record['output']['syntax_complete']=not record['output']['syntax_complete']
    else:
        record['output']['parser_inputs']['engine_archive_sha256']='0'*64
        record['output_sha256']=hashlib.sha256(json.dumps(record['output'],sort_keys=True,
            separators=(',',':')).encode()).hexdigest()
    directory=tmp_path/'legacy_pre30';directory.mkdir()
    (directory/original.name).write_text(json.dumps(record))
    monkeypatch.setattr(profiles,'FIXTURES',tmp_path)
    with pytest.raises(AssertionError,match='mismatch|stale|mismatched'):
        profiles.historical_source('legacy_pre30',raw)
