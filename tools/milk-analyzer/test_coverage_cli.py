"""The corpus audit keeps stdout as one machine-readable JSON document."""
import json
from pathlib import Path
import sys

import coverage_audit


def test_progress_does_not_mix_with_json_stdout(tmp_path, monkeypatch, capsys):
    preset = tmp_path / 'one.milk'
    preset.write_bytes(b'[preset00]\n')
    summary = tmp_path / 'summary.json'
    summary.write_text(json.dumps({'reader_sha256': 'reader', 'rows': []}))
    output = tmp_path / 'audit.json'
    monkeypatch.setattr(Path, 'glob', lambda self, pattern: [preset] * 1000)
    monkeypatch.setattr(coverage_audit, 'audit_source', lambda *args, **kwargs: {
        'preset_sha256': 'source', 'cache_identity_matches': False,
        'source_tokens': 0, 'code_tokens': 0, 'parsed_code_tokens': 0,
        'unvisited_code_tokens': 0, 'stages': {}, 'lexical_calls': {},
        'lowering_unknowns': {},
    })
    monkeypatch.setattr(sys, 'argv', ['coverage_audit.py', '--presets', str(tmp_path),
                                     '--summary', str(summary), '--output', str(output)])
    coverage_audit.main()
    captured = capsys.readouterr()
    assert json.loads(captured.out)['presets'] == 1000
    assert 'Audited 1000/1000' in captured.err
