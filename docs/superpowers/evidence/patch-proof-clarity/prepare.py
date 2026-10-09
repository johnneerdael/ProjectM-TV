"""Build private single-repair ablations from the frozen catalog source receipt.

Only private copies are changed. The catalog cache and shipping patches stay intact.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): digest(p)
            for p in sorted(root.rglob('*')) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    for name in ('catalog', 'repo', 'work'):
        setattr(args, name, getattr(args, name).expanduser().resolve())
    if args.work.exists() and not (args.work / 'harness').is_dir():
        raise ValueError('Existing directory is not a prepared run')
    original = json.loads((args.catalog / 'patched/identity.json').read_text())
    source = Path(original['source'])
    expected = json.loads((args.repo / 'docs/superpowers/evidence/patch-visual-catalog/patched-source-tree.json').read_text())
    if inventory(source) != expected:
        raise ValueError('Frozen source inventory mismatch')
    args.work.mkdir(parents=True, exist_ok=True)
    harness = args.work / 'harness'
    if not harness.exists():
        shutil.copytree(args.catalog / 'harness', harness)
    observer = args.repo / 'docs/superpowers/evidence/i31-benefit/image-harness'
    for name in ('worker.cpp', 'gl_capture.hpp'):
        shutil.copyfile(observer / name, harness / name)
    worker = harness / 'worker.cpp'
    text = worker.read_text().replace(
        'if (frame == 119 || frame == 239 || frame == 479) {',
        'if (std::find(selected.begin(), selected.end(), frame) != selected.end()) {')
    text = text.replace('int error_frames = 0;',
                        'auto selected = cfg.at("selected_frames").get<std::vector<int>>();\n'
                        '        int error_frames = 0;')
    worker.write_text(text)
    for role in ('full', 'without-0021', 'without-0023', 'without-0030',
                 'without-0032', 'without-0033', 'without-0025', 'without-0028'):
        target = args.work / role
        private = target / 'source'
        if (target / 'identity.json').exists():
            prior=json.loads((target/'identity.json').read_text())
            if prior['harness']!=inventory(harness) or prior['worker_sha256']!=digest(Path(prior['worker'])):
                raise ValueError('Completed role inputs changed; use a fresh directory')
            print(role, 'already built', flush=True)
            continue
        if private.exists():
            shutil.rmtree(private)
        shutil.copytree(source, private)
        reversal = None
        if role != 'full':
            number = role.removeprefix('without-')
            patch = next((args.repo / 'tools/projectm-patches').glob(number + '-*.patch'))
            frozen = subprocess.check_output(['git', '-C', str(args.repo), 'show', original['source_commit'] + ':tools/projectm-patches/' + patch.name])
            recorded = {'name': patch.name, 'sha256': hashlib.sha256(frozen).hexdigest()}
            if digest(patch) != recorded['sha256']:
                raise ValueError('Patch bytes differ from frozen series')
            if number == '0023':
                # Later packed-motion shader selection overlaps the original reversal.
                # Disable only its compile-time oscillator branch; leave later guards intact.
                getter = private / 'src/libprojectM/MilkdropPreset/MilkdropStaticShaders.cpp.in'
                content = getter.read_text()
                before = '#define PROJECTM_LEGACY_WARP\\n'
                if content.count(before) != 1:
                    raise ValueError('Unexpected legacy shader getter')
                getter.write_text(content.replace(before, ''))
                recorded['method'] = 'Remove PROJECTM_LEGACY_WARP define only; retains subsequent packed-motion guard and all other code'
            else:
                subprocess.run(['patch', '-p1', '-R', '--dry-run', '-i', str(patch)], cwd=private, check=True)
                subprocess.run(['patch', '-p1', '-R', '-i', str(patch)], cwd=private, check=True)
            reversal = recorded
        tree = inventory(private)
        changed = {name: {'full': expected.get(name), 'role': tree.get(name)}
                   for name in expected.keys() | tree.keys() if expected.get(name) != tree.get(name)}
        if (role == 'full') != (len(changed) == 0):
            raise ValueError('Ablation source delta was not applied')
        build = target / 'native-build'
        configure = ['cmake', '-S', str(harness), '-B', str(build), '-G', 'Ninja',
                     '-DCMAKE_BUILD_TYPE=Release', '-DCATALOG_TV=ON', f'-DPROJECTM_SOURCE={private}']
        with (target / 'build.log').open('w') as log:
            subprocess.run(configure, stdout=log, stderr=subprocess.STDOUT, check=True)
            subprocess.run(['cmake', '--build', str(build), '-j', '6'], stdout=log,
                           stderr=subprocess.STDOUT, check=True)
        binary = build / 'preset-lab-worker'
        receipt = {'role': role, 'catalog_identity': original, 'reversed_patch': reversal,
                   'source_delta': changed, 'source_tree': tree,
                   'harness': inventory(harness), 'worker': str(binary), 'worker_sha256': digest(binary),
                   'configure': configure, 'qualification': 'source-instrumented native desktop witness'}
        (target / 'identity.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(role, 'built', len(changed), 'changed source files', flush=True)


if __name__ == '__main__':
    main()
