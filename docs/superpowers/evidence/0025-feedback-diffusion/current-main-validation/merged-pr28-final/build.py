"""Build final PR28 feature-branch merge through actual TV core; no source edits."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[3]
PROVIDER=ROOT/"docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/build.py"
spec=importlib.util.spec_from_file_location("final_mrt_core_builder",PROVIDER)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
assert module.ROOT==ROOT
module.WORK=Path(__file__).resolve().parent
module.build("candidate","0e3f948e8cf0244b1f27c846bcb5b8b9fc3a26a0")
