"""Frozen inputs and exact-frame validation; importing this module performs no device I/O."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import re
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SCHEMA = "projectmtv-random100-frame-rgb-v1"
SEED = 12345
CANDIDATE_ENGINE = "6f64807467e312034883a4389e6aa80a675458bc"
MIDGIT = "midgitstraights of majillaen - featy sweet.milk"
PACKAGES = {role: "nl.neerdael.projectmtv.corpusrandom100" + role
            for role in ("baseline", "candidate", "released")}
SUPPLEMENTAL_PACKAGES = {role: "nl.neerdael.projectmtv.corpusrandom100supp" + role for role in PACKAGES}
PROFILES = {
    "1080p": {"width": 1920, "height": 1080, "referenceWidth": 1024,
              "referenceHeight": 768, "nativeTrails": 0,
              "expected_level": "standard", "expected_trails": "inactive (render 1080p)"},
    "native4k": {"width": 3840, "height": 2160, "referenceWidth": 1024,
                 "referenceHeight": 768, "nativeTrails": 0,
                 "expected_level": "standard", "expected_trails": "1280×720"},
    "native4k-medium": {"width": 3840, "height": 2160, "referenceWidth": 1280,
                        "referenceHeight": 720, "nativeTrails": 1,
                        "expected_level": "medium", "expected_trails": "1280×720"},
    "native4k-high": {"width": 3840, "height": 2160, "referenceWidth": 1280,
                      "referenceHeight": 720, "nativeTrails": 2,
                      "expected_level": "high", "expected_trails": "1280×720"},
}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(canonical(value) + "\n")
    temporary.replace(path)


def immutable_json(path, value):
    path = Path(path)
    if path.exists() and json.loads(path.read_text()) != value:
        raise ValueError("Frozen inputs changed; use a new work directory: " + str(path))
    if not path.exists():
        write(path, value)


def catalog():
    source = HERE.parent / "patch-impact/impact.json.gz"
    report = json.loads(gzip.decompress(source.read_bytes()))
    records = [{"filename": row["filename"], "asset_sha256": row["asset_sha256"]}
               for row in report["preset_catalog"]]
    records.sort(key=lambda row: row["filename"].encode("utf-8"))
    if len(records) != 9606 or len({row["filename"] for row in records}) != 9606:
        raise ValueError("Expected the exact complete 9,606-preset catalog")
    return records


def select(records, seed=SEED, count=100):
    prefix = str(seed).encode("ascii") + b"\0"
    ranked = [dict(row, selection_rank_sha256=sha(prefix + row["filename"].encode("utf-8")))
              for row in records]
    ranked.sort(key=lambda row: (row["selection_rank_sha256"], row["filename"].encode("utf-8")))
    random = ranked[:count]
    regression = [] if any(row["filename"] == MIDGIT for row in random) else [
        dict(next(row for row in records if row["filename"] == MIDGIT), reason="required midgit regression")]
    return random, regression


def zip_hashes(path, prefix):
    with zipfile.ZipFile(path) as archive:
        return {row.filename: sha(archive.read(row)) for row in archive.infolist()
                if row.filename.startswith(prefix) and not row.is_dir()}


def release_manifest(path):
    path = Path(path).resolve()
    record = json.loads(path.read_text())
    required = ("release_tag", "source_commit", "engine_commit", "aar_path", "aar_sha256", "ordered_patches")
    if any(key not in record for key in required):
        raise ValueError("Release manifest must identify exact source, engine, AAR and ordered patches")
    if (record.get("schema") != "projectmtv-verified-release-v1"
            or record.get("status") != "verified"
            or 49 not in record.get("includes_prs", [])
            or not re.fullmatch(r"[0-9a-f]{40}", record["source_commit"])
            or not re.fullmatch(r"[0-9a-f]{40}", record["engine_commit"])
            or not re.fullmatch(r"[0-9a-f]{64}", record["aar_sha256"])):
        raise ValueError("Final baseline must be an explicitly verified release containing PR #49")
    patches = record["ordered_patches"]
    if (not isinstance(patches, list) or len(patches) < 49
            or any(not re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256", "")))
                   or not str(row.get("name", "")).startswith(f"{index:04d}-")
                   for index, row in enumerate(patches, 1))):
        raise ValueError("Release manifest requires the full consecutive post-#49 patch list")
    aar = Path(record["aar_path"])
    if not aar.is_absolute():
        aar = path.parent / aar
    if file_sha(aar) != record["aar_sha256"]:
        raise ValueError("Verified released AAR bytes changed")
    return dict(record, aar_path=str(aar.resolve()), manifest_path=str(path), manifest_sha256=file_sha(path))


def verify_published(release, records):
    if file_sha(release["aar_path"]) != release["aar_sha256"]:
        raise ValueError("Released AAR bytes changed")
    wanted = {"assets/presets/" + row["filename"]: row["asset_sha256"] for row in records}
    if zip_hashes(release["aar_path"], "assets/presets/") != wanted:
        raise ValueError("Full catalog differs from the released AAR")


def regression_inventory(path, records):
    path = Path(path).resolve()
    data = json.loads(path.read_text())
    if (data.get("schema") != "projectmtv-regression-presets-v1"
            or data.get("completeness") != "all_original_patch_regression_presets"
            or not re.fullmatch(r"[0-9a-f]{64}", str(data.get("source_inventory_sha256", "")))):
        raise ValueError("Require the complete named original-patch regression inventory with provenance")
    known = {row["filename"]: row["asset_sha256"] for row in records}
    selected = {}
    for row in data["presets"]:
        name = row["filename"]
        if name not in known or row["asset_sha256"] != known[name] or not row.get("reasons"):
            raise ValueError("Unknown/modified regression preset or missing reason: " + name)
        reasons = selected.setdefault(name, {})
        for reason in row["reasons"]:
            reasons[canonical(reason)] = reason
    reason = {"category": "owner-required-control", "basis": "known midgit regression"}
    selected.setdefault(MIDGIT, {})[canonical(reason)] = reason
    rows = [{"filename": name, "asset_sha256": known[name], "reasons": [reasons[key] for key in sorted(reasons)]}
            for name, reasons in sorted(selected.items(), key=lambda pair: pair[0].encode("utf-8"))]
    return data, rows


def frozen_selection(release, inventory_path):
    records = catalog()
    verify_published(release, records)
    inventory, named = regression_inventory(inventory_path, records)
    random, _ = select(records)
    chosen = {row["filename"] for row in random}
    additional = [row for row in named if row["filename"] not in chosen]
    external = []
    for row in inventory.get("required_external_presets", []):
        path = Path(inventory_path).resolve().parent / row["asset_path"]
        if (row["filename"] in {item["filename"] for item in records}
                or file_sha(path) != row["asset_sha256"] or path.stat().st_size != row["asset_bytes"]):
            raise ValueError("External fixture is changed or overlaps the bundled catalog")
        external.append(dict(row, resolved_asset_path=str(path.resolve())))
    return {"schema": "projectmtv-random100-selection-v1", "selection_seed": SEED,
            "catalog_size": len(records), "catalog_sha256": sha(canonical(records).encode()),
            "random_count": 100,
            "algorithm": "SHA256(ASCII decimal seed + NUL + exact UTF8 filename), ascending hash then UTF8 filename",
            "released_baseline": release,
            "regression_inventory_sha256": file_sha(inventory_path),
            "regression_source_inventory_sha256": inventory["source_inventory_sha256"],
            "named_regressions": named, "random_presets": random, "additional_regressions": additional,
            "required_external_presets": external,
            "synthetic_or_unbundled_controls": inventory.get("synthetic_or_nonbundled_fixtures", inventory.get("synthetic_or_unbundled_controls", [])),
            "missing_external_witnesses": inventory.get("missing_external_witnesses", []),
            "unresolved_name_aliases": inventory.get("unresolved_name_aliases", []),
            "optional_historical_sampled_controls_count": len(inventory.get("optional_historical_sampled_controls", []))}


def named_profile_extensions(selected):
    """Freeze activation-sensitive profiles from source reasons, never from image success."""
    result = {}
    native_patches = {"0038", "0042", "0043"}
    for row in selected.get("named_regressions", []):
        reasons = [reason for reason in row["reasons"] if isinstance(reason, dict)]
        owner = [reason for reason in reasons if reason.get("category") == "owner-required-control"
                 and native_patches.intersection(reason.get("patches", []))]
        issue = [reason for reason in reasons if reason.get("category") == "required-issue-witness"
                 and native_patches.intersection(reason.get("patches", []))]
        profiles = ["native4k", "native4k-medium", "native4k-high"] if owner else ["native4k"] if issue else []
        if profiles:
            result[row["filename"]] = {"profiles": profiles, "activation_reasons": owner or issue}
    evidence = json.loads((HERE / "q2160-profile-evidence.json").read_text())
    for path, expected in evidence["source_files_sha256"].items():
        if file_sha(ROOT / path) != expected:
            raise ValueError("Original q2160 profile evidence changed")
    named = {row["filename"]: row for row in selected.get("named_regressions", [])}
    for row in evidence["presets"]:
        if row["filename"] not in named:
            continue
        if named[row["filename"]]["asset_sha256"] != row["asset_sha256"]:
            raise ValueError("Original q2160 regression asset changed")
        record = result.setdefault(row["filename"], {"profiles": [], "activation_reasons": []})
        if evidence["current_profile"] not in record["profiles"]:
            record["profiles"].append(evidence["current_profile"])
        record["activation_reasons"].append({"category": "explicit-original-q2160-control",
                                           "evidence_sha256": file_sha(HERE / "q2160-profile-evidence.json"),
                                           "original_profile": evidence["original_profile"],
                                           "mapping_note": evidence["mapping_note"]})
    return result


def selection(path, release, inventory_path):
    frozen = json.loads(Path(path).read_text())
    if frozen != frozen_selection(release, inventory_path):
        raise ValueError("Frozen sample/release/regression union changed")
    return frozen



def bridge_is_reset_after_seed(text):
    start = text.index("Java_nl_neerdael_projectmtv_corpus_LabBridge_initialize")
    end = text.index("Java_nl_neerdael_projectmtv_corpus_LabBridge_setFrameClock", start)
    body = text[start:end]
    seed = body.find('setenv("PRESET_LAB_SEED"')
    reset = body.find("lab::ResetShaderRandom();")
    return seed >= 0 and reset > seed


def frame_hashes(directory, manifest, request):
    path = Path(directory) / "frame-hashes.jsonl"
    count = request["frameLimit"]
    if manifest.get("frameHashCount") != count or manifest.get("frameHashesSha256") != file_sha(path):
        raise ValueError("Incomplete or modified every-frame hash stream")
    if path.stat().st_size > count * 256:
        raise ValueError("Frame hash stream exceeds its bounded size")
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    if len(rows) != count:
        raise ValueError("Missing frame hashes")
    for frame, row in enumerate(rows):
        if (type(row.get("frame")) is not int or row["frame"] != frame
                or row.get("width") != request["width"] or row.get("height") != request["height"]
                or not re.fullmatch(r"[0-9a-f]{64}", str(row.get("rgbSha256", "")))):
            raise ValueError("Frame order, dimensions or RGB hash are invalid")
    return [row["rgbSha256"] for row in rows]


def first_difference(first, second):
    if len(first) != len(second):
        raise ValueError("Sequences have different frame coverage")
    return next((frame for frame, pair in enumerate(zip(first, second)) if pair[0] != pair[1]), None)
