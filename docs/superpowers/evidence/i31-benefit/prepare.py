"""Prepare a private I31 benchmark from a frozen catalog engine; never edit shipping sources."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

from source_observer import observe

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo', type=Path, required=True)
parser.add_argument('--catalog-work', type=Path, required=True)
parser.add_argument('--work', type=Path, required=True)
args = parser.parse_args()
repo, catalog, work = (p.resolve() for p in (args.repo, args.catalog_work, args.work))
evidence = Path(__file__).resolve().parent
if work.exists():
    raise SystemExit('Refuse existing benchmark output directory')
identity = json.loads((catalog / 'patched/identity.json').read_text())
if (identity['source_commit'] != '8a15996e8510533113a44e26feaddc3a7d6e85f5' or
        identity['engine']['patches_sha256'] != '78a3d98ed16b8209edf4e0d5bf709ca2f5be11cfae796875745c5045bff69321'):
    raise SystemExit('Expected frozen 34-patch catalog engine')
work.mkdir(parents=True)
shutil.copytree(evidence / 'harness', work / 'harness')
shutil.copytree(catalog / 'harness/vendor', work / 'harness/vendor')
shutil.copytree(evidence / 'image-harness', work / 'image-harness')
shutil.copytree(catalog / 'harness/vendor', work / 'image-harness/vendor')
shutil.copyfile(evidence / 'link_images.py', work / 'link_images.py')
patch = subprocess.check_output(['git', '-C', str(repo), 'show',
    '8a15996e8510533113a44e26feaddc3a7d6e85f5:tools/projectm-patches/0019-gamma-only-pass-epsilon.patch'])
(work / '0019.patch').write_bytes(patch)
hooks = (work / 'harness/analysis_hooks.hpp').read_text()
for role in ('with-0019', 'without-0019'):
    source = work / role / 'engine'
    shutil.copytree(Path(identity['source']), source)
    if role == 'without-0019':
        subprocess.run(['git', 'apply', '--reverse', str(work / '0019.patch')],
            cwd=source, check=True,
            env=dict(os.environ, GIT_CEILING_DIRECTORIES=str(source.parent)))
    (source / 'src/libprojectM/analysis_hooks.hpp').write_text(hooks)
    video = source / 'src/libprojectM/MilkdropPreset/VideoEcho.cpp'
    video.write_text(observe(video.read_text()))
for name in ('original.milk', 'inactive-gamma2.milk', 'protocol.md', 'benchmark.py', 'source_observer.py', 'capture_visual.py'):
    shutil.copyfile(evidence / name, work / name)
for name in ('build.py', 'run.py', 'analyze.py', 'verify_visual.py'):
    content = (evidence / ('executed-' + name)).read_text()
    # Executed scripts derived the repo from repo/build/i31-benefit. The portable
    # adapter supplies that same value explicitly, leaving the render recipe intact.
    content = content.replace('repo=Path(__file__).resolve().parents[2];root=',
                              "repo=Path(os.environ['I31_PROOF_REPO']).resolve();root=")
    (work / name).write_text(content)
subprocess.run([os.sys.executable, str(work / 'build.py')], check=True)
print(f'Prepared {work}; set I31_PROOF_REPO={repo} when running run.py')
