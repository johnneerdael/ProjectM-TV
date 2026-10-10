"""Refresh existing source-only controls after the producer modules are frozen."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    root = args.repo_root.resolve()
    os.chdir(root)
    os.environ.update(json.loads((root / 'build/preset-corpus/source-components-qualification-env.json').read_text()))
    sys.path.insert(0, str(root / 'tools/milk-analyzer'))
    from test_source_prominence import evidence
    import source_prominence

    fixture_path = root / 'tools/milk-analyzer/fixtures/static-prominence-controls-2026-10-10.json'
    fixture = json.loads(fixture_path.read_text())
    model_paths = [root / 'tools/milk-analyzer' / name for name in
                   ('source_prominence.py', 'source_colour_modulus.py')]
    identities = {path.name: sha256(path) for path in model_paths}
    assert sha256(root / 'build/preset-corpus/source34/adapters/milk-native-reader') == fixture['reader_sha256']
    for reference in fixture['source_references']:
        assert sha256(Path(reference['path'])) == reference['sha256'], reference['purpose']

    assert source_prominence.MODEL_SOURCE_SHA256 == identities['source_prominence.py']
    model_identity = None
    for control in fixture['controls']:
        component, report = evidence(control['body'], **control['arguments'])
        assert component['provenance']['preset_sha256'] == control['component']['provenance']['preset_sha256'], control['name']
        current_identity = report['provenance']['model_sha256']
        assert model_identity is None or current_identity == model_identity
        model_identity = current_identity
        control['component'] = component
    assert identities == {path.name: sha256(path) for path in model_paths}, 'producer changed during refresh'
    fixture['model_sha256'] = model_identity
    fixture['model_dependency_sha256'] = identities
    fixture_path.write_text(json.dumps(fixture, sort_keys=True, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'controls': len(fixture['controls']), 'model_sha256': model_identity,
                      'model_dependency_sha256': identities}, sort_keys=True))


if __name__ == '__main__':
    main()
