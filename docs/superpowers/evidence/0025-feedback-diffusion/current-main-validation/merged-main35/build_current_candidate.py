"""Build PR28 after actual integration of merged PR26/27, without source edits."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[3]
PROVIDER=ROOT/"docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/build.py"
spec=importlib.util.spec_from_file_location("current_mrt_core_builder",PROVIDER)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
assert module.ROOT==ROOT
module.WORK=Path(__file__).resolve().parent
module.build("candidate","1b2c266331c9624ef7027da86d825096d243e86a")
