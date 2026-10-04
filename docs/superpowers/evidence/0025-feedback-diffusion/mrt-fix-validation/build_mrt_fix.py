"""Build the unmodified bug/native-4k-feedback-fidelity product candidate (MRT exact+filtered copies)
through the shared provider: same private RNG/time instrumentation, no private source edits."""
import importlib.util
import json
from pathlib import Path
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
assert (ROOT / 'build/native-4k-current-main' / HERE.name) == HERE, 'adapter must stay at this depth'
PROVIDER = ROOT / 'docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/build.py'
spec = importlib.util.spec_from_file_location('shared_core_builder', PROVIDER)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
assert b.ROOT.resolve() == ROOT
b.WORK = HERE / 'worker'
b.WORK.mkdir(parents=True, exist_ok=True)
original_prepare = b.prepare
ADAPTER = Path(__file__).resolve()


def prepare(variant, commit):
    destination, source, identity = original_prepare(variant, commit)
    identity['private_mrt_fix_validation'] = {
        'product_source': 'bug/native-4k-feedback-fidelity product patch 0030 unchanged; no private renderer edits',
        'production_source_commit': commit, 'adapter_sha256': b.sha(ADAPTER),
        'shipping_byte_identity': False, 'instrumentation': 'shared provider private RNG/time only'}
    (source / 'corpus-app/src/main/assets/backend-identity.json').write_text(b.canonical(identity) + '\n')
    (destination / 'identity.json').write_text(b.canonical(identity) + '\n')
    return destination, source, identity


if __name__ == '__main__':
    b.prepare = prepare
    commit = subprocess.check_output(['git', 'rev-parse', '25e6aa83^{commit}'], cwd=ROOT, text=True).strip()
    b.build('candidate', commit)
    metadata_path = b.WORK / 'worker-candidate.json'
    metadata = json.loads(metadata_path.read_text())
    destination = Path(metadata['apk']).parent
    source = destination / 'repo'
    with (destination / 'core-aar.log').open('w') as log:
        b.run([str(source / 'gradlew'), '--no-daemon', ':core:bundleReleaseAar'], source, log)
    aar = source / 'core/build/outputs/aar/core-release.aar'
    with zipfile.ZipFile(aar) as archive:
        core_sha = b.hashlib.sha256(archive.read('jni/arm64-v8a/libprojectmtv.so')).hexdigest()
    if core_sha != metadata['backend_identity']['core_sha256']:
        raise ValueError('actual core AAR ELF differs from worker APK ELF')
    metadata['actual_core_aar'] = {'path': str(aar), 'sha256': b.sha(aar), 'core_sha256': core_sha, 'apk_elf_identity': True}
    metadata_path.write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps({'metadata': str(metadata_path), 'apk_sha256': metadata['apk_sha256'], 'actual_core_aar': metadata['actual_core_aar']}))
