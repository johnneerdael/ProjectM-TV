"""Shared engine-pin and frame-clock helpers for focused Native trails validation.

The historical bulk AAR producer has been retired. Its original implementation
is preserved in Git history for reproducing archived source identities.
"""
from __future__ import annotations

import re
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

def run(command: list[str], *, cwd: Path | None = None) -> str:
    return subprocess.check_output(command, cwd=cwd, text=True).strip()

def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"expected exactly one {label}; found {text.count(old)}")
    return text.replace(old, new)

def set_native_frame_time(text: str, clock: str) -> str:
    pattern = r"(?m)^([ \t]*)(projectm_opengl_render_frame(?:_fbo)?\(g_engine\.pm(?:,[^;\n]+)?\);)$"
    text, count = re.subn(pattern, lambda match: match[1] +
                         "projectm_set_frame_time(g_engine.pm, " + clock + ");\n" +
                         match[1] + match[2], text)
    if count == 0:
        raise ValueError("No actual Core render call found for frame time")
    return text

def gitlink(repo: Path, revision: str, path: str) -> str:
    row = run(["git", "-C", str(repo), "ls-tree", revision, "--", path]).split()
    if len(row) != 4 or row[0:2] != ["160000", "commit"] or row[3] != path:
        raise ValueError(f"missing pinned submodule {path} in {revision}")
    return row[2]

def checkout_pinned_engine(repo: Path, commit: str, destination: Path) -> tuple[Path, str, str]:
    """Resolve requested gitlinks without changing either live submodule checkout."""
    source = repo / "third_party/projectm"
    engine_pin = gitlink(repo, commit, "third_party/projectm")
    subprocess.run(["git", "clone", "--shared", "--no-checkout", str(source), str(destination)],
                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def checkout(cached: Path, private: Path, pin: str) -> None:
        present = subprocess.run(["git", "-C", str(private), "cat-file", "-e", pin + "^{commit}"],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if present.returncode:
            url = run(["git", "-C", str(cached), "remote", "get-url", "origin"])
            subprocess.run(["git", "-C", str(private), "fetch", url, pin], check=True)
        subprocess.run(["git", "-C", str(private), "checkout", "--detach", pin],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    checkout(source, destination, engine_pin)
    evaluator_pin = gitlink(destination, engine_pin, "vendor/projectm-eval")
    evaluator = destination / "vendor/projectm-eval"
    subprocess.run(["git", "clone", "--shared", "--no-checkout",
                    str(source / "vendor/projectm-eval"), str(evaluator)],
                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    checkout(source / "vendor/projectm-eval", evaluator, evaluator_pin)
    return destination, engine_pin, evaluator_pin


if __name__ == "__main__":
    raise SystemExit("Legacy core-corpus CLI retired; use focused Native trails tools or the recorded historical Git revision.")
