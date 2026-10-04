"""Compose current main35 with the immutable PR28 renderer; never edit a worktree patch."""
import argparse, hashlib, importlib.util, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
WORK=Path(__file__).resolve().parent
PROVIDER=ROOT/"docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/build.py"
BASE="f435dd7c58ea1f16d9d182ecfc5632b77f5b6f98"
RENDERER="d6170278bec04cf3bbfeccbfe29977233bc4064b"
PATCH="tools/projectm-patches/0036-feedback-diffusion-compensation.patch"
parser=argparse.ArgumentParser();parser.add_argument("role",choices=["baseline","candidate"]);args=parser.parse_args()
spec=importlib.util.spec_from_file_location("merged_core_builder",PROVIDER);provider=importlib.util.module_from_spec(spec);spec.loader.exec_module(provider)
assert provider.ROOT.resolve()==ROOT
provider.WORK=WORK
patch=subprocess.check_output(["git","show",RENDERER+":"+PATCH],cwd=ROOT)
sha=hashlib.sha256(patch).hexdigest()
(WORK/"source-0036.patch").write_bytes(patch)
original_archive=provider._archive
def archive(checkout,destination,temporary):
 original_archive(checkout,destination,temporary)
 if args.role=="candidate" and destination.name=="projectm":
  target=destination.parents[1]/PATCH
  assert not target.exists()
  target.write_bytes(patch)
provider._archive=archive
original_prepare=provider.prepare
def prepare(variant,commit):
 destination,source,identity=original_prepare(variant,commit)
 expected=36 if variant=="candidate" else 35
 assert len(identity["ordered_patches"])==expected
 identity["source_composition"]={"base_commit":BASE,"renderer_commit":RENDERER if variant=="candidate" else None,
   "unmodified_renderer_patch":PATCH if variant=="candidate" else None,"renderer_patch_sha256":sha if variant=="candidate" else None,
   "adapter_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
   "scope":"Actual production core source and assets from main35; candidate adds unchanged PR28 renderer patch before instrumentation; no feature-branch-only app code"}
 (destination/"identity.json").write_text(provider.canonical(identity)+"\n")
 return destination,source,identity
provider.prepare=prepare
provider.build(args.role,BASE)
