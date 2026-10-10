"""Preserve source operation order when exporting optional precision queries."""
import os
from pathlib import Path
import pytest
from shader_fields import Field


def value(number):
    return Field('constant', (), 'float', {'value': number})


def test_precision_export_preserves_cancellation_order_and_domains():
    from source_precision_export import export_precision_query
    x = Field('input', (), 'float', {'name': 'bass'})
    first = Field('add', (value(1), x), 'float')
    result = export_precision_query(Field('subtract', (first, x), 'float'),
                                    input_domains={'bass': [0, 16777216]}, precision='binary32')
    assert result['symbols'] == {'bass': 'x0'}
    assert 'rnd32' in result['fptaylor']
    assert ' - x0' in result['fptaylor']
    assert ':precision binary32' in result['fpcore']
    assert result['authored_program_changed'] is False
    assert result['native_numeric_certified'] is False
    assert result['input_domains']['bass'] == [0, 16777216]


def test_precision_export_rejects_unbound_domains_and_storage():
    from source_precision_export import export_precision_query
    x = Field('input', (), 'float', {'name': 'time'})
    with pytest.raises(ValueError, match='domain'):
        export_precision_query(x, input_domains={}, precision='binary64')
    qualified = Field('input', (), 'float', {'name': 'x', 'phase': 'per_frame_'})
    with pytest.raises(ValueError):
        export_precision_query(qualified, input_domains={'x': [0, 1]}, precision='binary64')


def test_precision_export_keeps_exact_existing_literal():
    from source_precision_export import export_precision_query
    result = export_precision_query(value(.1), input_domains={}, precision='binary64')
    assert '0.1000000000000000055511151231257827021181583404541015625' in result['fpcore']
    assert '0.1000000000000000055511151231257827021181583404541015625' in result['fptaylor']


@pytest.mark.parametrize('op', ['divide', 'cast', 'sample', 'sequence', 'floor'])
def test_precision_export_rejects_unqualified_native_operations(op):
    from source_precision_export import export_precision_query
    with pytest.raises(ValueError):
        export_precision_query(Field(op, (value(1), value(2)), 'float'),
                               input_domains={}, precision='binary32')


def test_optional_fptaylor_runtime_bounds_cancellation_roundoff():
    from source_precision_export import export_precision_query, run_fptaylor_js
    paths = [os.environ.get(n) for n in ('MILK_FPTAYLOR_JS', 'MILK_JAVASCRIPT_RUNTIME', 'MILK_FPTAYLOR_CONFIG')]
    if not all(paths):
        pytest.skip('prepared optional FPTaylor JS bundle/runtime/config not supplied')
    x = Field('input', (), 'float', {'name': 'bass'})
    field = Field('subtract', (Field('add', (value(1), x), 'float'), x), 'float')
    query = export_precision_query(field, input_domains={'bass': [0, 16777216]}, precision='binary32')
    result = run_fptaylor_js(query, bundle=Path(paths[0]), runtime=Path(paths[1]), default_config=Path(paths[2]))
    assert result['status'] == 'computed_under_tool_model'
    assert 1 <= result['upper_absolute_roundoff_error'] <= 1.1
    assert result['native_numeric_certified'] is False
    assert result['query_sha256'] == query['record_sha256']


def test_precision_worker_executes_hash_identified_bundle_snapshot(tmp_path, monkeypatch):
    import hashlib
    import subprocess
    import shutil
    from source_precision_export import export_precision_query, run_fptaylor_js
    runtime = shutil.which('bun')
    if runtime is None:
        pytest.skip('JavaScript runtime unavailable')
    bundle = tmp_path / 'fixture.js'
    source = 'onmessage=()=>postMessage([{name:"result",elapsedTime:0,errors:[{errorName:"absolute error (exact)",error:[0,1]}]}]);'
    bundle.write_text(source)
    config = tmp_path / 'default.cfg'; config.write_text('verbosity=0')
    original = subprocess.run
    def race(*args, **kwargs):
        bundle.write_text(source.replace('error:[0,1]', 'error:[0,99]'))
        return original(*args, **kwargs)
    monkeypatch.setattr(subprocess, 'run', race)
    query = export_precision_query(value(1), input_domains={}, precision='binary32')
    result = run_fptaylor_js(query, bundle=bundle, runtime=Path(runtime), default_config=config)
    assert result['backend']['bundle_sha256'] == hashlib.sha256(source.encode()).hexdigest()
    assert result['upper_absolute_roundoff_error'] == 1
