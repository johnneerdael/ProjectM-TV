import os
import tempfile
from pathlib import Path

from .identity import canonical_json, digest, load_json


def read_cached_run(path: Path, key: str) -> dict | None:
    try:
        stored=load_json(path)
        if (isinstance(stored,dict) and stored.get("key")==key
                and stored.get("payload_sha256")==digest(stored.get("run"))
                and stored["run"].get("status")=="success"):
            return stored["run"]
    except (OSError,ValueError,KeyError,TypeError):
        pass
    return None


def write_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(dir=path.parent,suffix=".tmp")
    try:
        with os.fdopen(fd,"w") as output:
            output.write(canonical_json(value))
        os.replace(name,path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
