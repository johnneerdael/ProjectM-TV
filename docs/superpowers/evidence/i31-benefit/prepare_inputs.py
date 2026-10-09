"""Validate the actual frozen preparation inputs before creating output or building."""
import hashlib
import json
from pathlib import Path

SOURCE_COMMIT = "8a15996e8510533113a44e26feaddc3a7d6e85f5"
ENGINE_IDENTITY = {"commit": "6f64807467e312034883a4389e6aa80a675458bc",
                   "patches_sha256": "78a3d98ed16b8209edf4e0d5bf709ca2f5be11cfae796875745c5045bff69321",
                   "instrumentation_sha256": "2efc3d43b8061ef60a42be22e47e1b86a781c15c1a5494a9a417b4bb43b3d57e"}
EVALUATOR_COMMIT = "22fb0cfd8f2dfbcd2b68f2443e7f44e19b32c09a"
SOURCE_DIGEST = "5e48da2b8a47f160a1884a648cae19127d833e69f5b5f3c55ffb5c64eff66533"
CATALOG_HARNESS_DIGEST = "4564d428fe613bbcc41c503bc04599d86812cb7dbf5f8b9374f695394b22182f"
TIMING_TEMPLATE_DIGEST = "aaf2753f5ed9100ea83083404a08f42af918dbb32c761f530695cf066edc70c2"
IMAGE_TEMPLATE_DIGEST = "b2fc47391bad62962d73227f26964b2ba51e447044b342aa7692b2312e933d98"
VENDOR_DIGEST = "f041449773c733d3e1d00a7d617899c397d2cad006e219743b48ea71f74461ad"

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def inventory(root):
    if not root.is_dir():
        raise ValueError(f"missing input directory: {root}")
    return {p.relative_to(root).as_posix(): file_hash(p)
            for p in sorted(root.rglob("*")) if p.is_file()}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate_source(source, expected):
    actual = inventory(source)
    require(actual == expected and digest(actual) == SOURCE_DIGEST,
            "actual engine source differs from the independently frozen 987-file inventory")

def validate_inputs(repo, catalog, evidence):
    canonical = repo / "docs/superpowers/evidence/patch-visual-catalog"
    expected = json.loads((canonical / "patched-source-tree.json").read_text())
    frozen_worker = json.loads((canonical / "workers.json").read_text())["patched"]
    require(len(expected) == 987 and digest(expected) == SOURCE_DIGEST,
            "canonical frozen repository source inventory differs")
    require(frozen_worker["source_commit"] == SOURCE_COMMIT and frozen_worker["engine"] == ENGINE_IDENTITY
            and frozen_worker["evaluator_commit"] == EVALUATOR_COMMIT
            and frozen_worker["source_tree_sha256"] == SOURCE_DIGEST,
            "canonical repository engine/evaluator/instrumentation identity differs")
    require(digest(frozen_worker["harness"]) == CATALOG_HARNESS_DIGEST,
            "canonical catalog harness identity differs")
    patches = [(patch["filename"], patch["sha256"]) for patch in frozen_worker["ordered_patches"]]
    require(len(patches) == 34 and digest(patches) == ENGINE_IDENTITY["patches_sha256"],
            "canonical ordered patch inventory differs")
    identity = json.loads((catalog / "patched/identity.json").read_text())
    require(identity["role"] == "patched" and identity["source_commit"] == SOURCE_COMMIT
            and identity["engine"] == ENGINE_IDENTITY and identity["harness"] == frozen_worker["harness"],
            "catalog engine/pins/harness identity differs")
    # Older catalog builders wrote compact identities; newer builders add these
    # fields. Validate every supported supplemental binding when present.
    for field, value in (("evaluator_commit", EVALUATOR_COMMIT), ("source_tree_sha256", SOURCE_DIGEST)):
        if field in identity:
            require(identity[field] == value, f"catalog {field} differs")
    if "ordered_patches" in identity:
        require([(p.get("filename", p.get("name")), p["sha256"]) for p in identity["ordered_patches"]] == patches,
                "catalog ordered patch receipt differs")
    manifest = catalog / "patched/source-tree.json"
    if manifest.exists():
        require(json.loads(manifest.read_text()) == expected, "catalog preserved source manifest differs")
        if "source_tree_manifest_sha256" in identity:
            require(identity["source_tree_manifest_sha256"] == file_hash(manifest), "catalog source manifest bytes differ")
    elif "source_tree_manifest_sha256" in identity:
        raise ValueError("catalog source manifest receipt exists but manifest is missing")
    source = Path(identity["source"]).resolve()
    validate_source(source, expected)
    require(inventory(catalog / "harness") == frozen_worker["harness"], "actual catalog harness differs")
    require(digest({"vendor/" + name: value for name, value in inventory(catalog / "harness/vendor").items()}) == VENDOR_DIGEST,
            "actual catalog vendor inputs differ")
    require(digest(inventory(evidence / "harness")) == TIMING_TEMPLATE_DIGEST,
            "actual timing observer template differs")
    require(digest(inventory(evidence / "image-harness")) == IMAGE_TEMPLATE_DIGEST,
            "actual image observer template differs")
    require(file_hash(Path(identity["worker"])) == identity["worker_sha256"], "catalog worker bytes differ from receipt")
    return identity, expected

def validate_copied_templates(work, vendor):
    for name, expected_digest in (("harness", TIMING_TEMPLATE_DIGEST), ("image-harness", IMAGE_TEMPLATE_DIGEST)):
        actual = inventory(work / name)
        copied_vendor = {key: value for key, value in actual.items() if key.startswith("vendor/")}
        template = {key: value for key, value in actual.items() if not key.startswith("vendor/")}
        require(digest(template) == expected_digest and copied_vendor == vendor and digest(copied_vendor) == VENDOR_DIGEST,
                f"copied {name}/vendor inputs changed during preparation")
