from dataclasses import asdict
from pathlib import Path
import json
import shutil
import tempfile

from .identity import canonical_json,digest,file_digest,load_json
from .inventory import valid_filename,read_index,inventory as read_inventory
from .models import MatchDecision,PresetRecord


def _catalog() -> list[dict]:
    return load_json(Path(__file__).parent/"profiles/genres.json")["genres"]


def _library_identity(records: list[PresetRecord]) -> str:
    return digest([asdict(r) for r in sorted(records,key=lambda r:r.path.encode())])


def export_bundle(decisions: list[MatchDecision], inventory: list[PresetRecord],
                  evidence: dict, destination: Path) -> Path:
    catalog=_catalog()
    known={r.path:r for r in inventory}
    if len(known)!=len(inventory) or any(not valid_filename(r.path) or r.weight_mb<0 for r in inventory):
        raise ValueError("unsafe or duplicate library records")
    ids={g["id"] for g in catalog}
    for decision in decisions:
        if decision.genre_id not in ids or decision.preset.path not in known:
            raise ValueError("unknown genre or preset reference")
        master=known[decision.preset.path]
        if decision.preset.sha256!=master.sha256:
            raise ValueError("stale preset hash")
        if decision.preset.weight_mb!=master.weight_mb:
            raise ValueError("preset memory weight differs from master index")
        canonical_json(asdict(decision))
    selected=[d for d in decisions if d.included and d.evidence_state in ("music-tested","reviewed")]
    grouped={g["id"]:[] for g in catalog}
    seen=set()
    for d in selected:
        key=(d.genre_id,d.preset.path)
        if key in seen: raise ValueError("duplicate category member")
        seen.add(key)
        grouped[d.genre_id].append(d.preset)
    if any(not members for members in grouped.values()):
        raise ValueError("each required genre must have eligible music-tested members")
    destination=destination.resolve()
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
        staged=Path(temporary)/"bundle"
        (staged/"genres").mkdir(parents=True)
        checksums={}
        for g in catalog:
            members=sorted(grouped[g["id"]],key=lambda r:r.path.encode())
            path=staged/"genres"/(g["id"]+".idx")
            path.write_text("".join(f"{r.path}\t{r.weight_mb}\n" for r in members),encoding="utf-8")
            checksums[path.relative_to(staged).as_posix()]=file_digest(path)
        rows=sorted(selected,key=lambda d:(d.preset.path.encode(),d.genre_id))
        result=staged/"presets.jsonl"
        result.write_text("".join(canonical_json(asdict(d))+"\n" for d in rows),encoding="utf-8")
        checksums["presets.jsonl"]=file_digest(result)
        used={d.preset.path:d.preset for d in selected}
        manifest={"schema_version":1,"library_sha256":_library_identity(inventory),
                  "presets":[asdict(used[n]) for n in sorted(used,key=lambda s:s.encode())],
                  "genres":[{"id":g["id"],"label":g["label"],"count":len(grouped[g["id"]])} for g in catalog],
                  "checksums":checksums,"evidence":evidence,
                  "evidence_level":"music-tested suggestions; subjective genre suitability remains provisional"}
        manifest["generation_identity"]=digest(manifest)
        (staged/"manifest.json").write_text(canonical_json(manifest),encoding="utf-8")
        verify_bundle(staged,inventory)
        backup=destination.with_name(destination.name+".previous")
        if backup.exists():
            raise ValueError("unfinished prior export publication exists")
        if destination.exists(): destination.rename(backup)
        try:
            staged.rename(destination)
        except BaseException:
            if backup.exists(): backup.rename(destination)
            raise
        if backup.exists(): shutil.rmtree(backup)
    return destination


def verify_bundle(bundle: Path, inventory: list[PresetRecord]) -> dict:
    manifest=load_json(bundle/"manifest.json")
    if manifest.get("schema_version")!=1:
        raise ValueError("unsupported genre bundle schema")
    check=dict(manifest)
    identity=check.pop("generation_identity",None)
    if identity!=digest(check): raise ValueError("manifest checksum mismatch")
    expected_ids={g["id"] for g in _catalog()}
    actual_ids=[g["id"] for g in manifest["genres"]]
    if set(actual_ids)!=expected_ids or len(actual_ids)!=len(expected_ids):
        raise ValueError("missing, duplicate or unknown genre catalog entries")
    required_checksums={f"genres/{genre}.idx" for genre in expected_ids}|{"presets.jsonl"}
    if set(manifest["checksums"])!=required_checksums:
        raise ValueError("missing or unexpected bundle checksums")
    known={r.path:r for r in inventory}
    used=set()
    for row in manifest["presets"]:
        r=PresetRecord(**row)
        if r.path in used:
            raise ValueError("duplicate preset catalog entry")
        used.add(r.path)
        if r.path not in known or r.sha256!=known[r.path].sha256:
            raise ValueError("stale preset reference")
        if r.weight_mb!=known[r.path].weight_mb:
            raise ValueError("stale memory weight")
    if manifest["library_sha256"]!=_library_identity(inventory):
        raise ValueError("stale library identity")
    for name,expected in manifest["checksums"].items():
        if name.startswith("/") or ".." in Path(name).parts or "\\" in name:
            raise ValueError("unsafe bundle path")
        if file_digest(bundle/name)!=expected:
            raise ValueError("bundle checksum mismatch")
    evidence_members={genre:set() for genre in expected_ids}
    for line in (bundle/"presets.jsonl").read_text(encoding="utf-8").splitlines():
        if not line: continue
        row=json.loads(line)
        canonical_json(row)
        genre=row.get("genre_id")
        record=row.get("preset",{})
        name=record.get("path")
        if (genre not in expected_ids or name not in used or record!=asdict(known[name])
                or row.get("included") is not True
                or row.get("evidence_state") not in ("music-tested","reviewed","bass-screen-tested")):
            raise ValueError("invalid category evidence record")
        if name in evidence_members[genre]:
            raise ValueError("duplicate category evidence record")
        evidence_members[genre].add(name)
    if used!=set().union(*evidence_members.values()):
        raise ValueError("preset catalog differs from category evidence")
    for genre in manifest["genres"]:
        index=read_index(bundle/"genres"/(genre["id"]+".idx"))
        if len(index)!=genre["count"]:
            raise ValueError("category count mismatch")
        if any(name not in known or known[name].weight_mb!=weight for name,weight in index.items()):
            raise ValueError("invalid category membership or memory weight")
        if set(index)!=evidence_members[genre["id"]]:
            raise ValueError("category index differs from evidence membership")
    return manifest


def import_bundle(bundle: Path, repo: Path, check: bool=False) -> Path:
    assets=repo/"core/src/main/assets"
    records,metadata=read_inventory(assets/"presets",assets/"presets.idx",assets/"textures")
    manifest=verify_bundle(bundle,records)
    expected=manifest.get("evidence",{}).get("texture_sha256")
    if expected is None or expected!=metadata["texture_sha256"]:
        raise ValueError("stale or missing texture-pack identity")
    patches=repo/"tools/projectm-patches"
    expected_patches=manifest.get("evidence",{}).get("app_patches_sha256")
    if patches.is_dir():
        actual=digest([(p.name,file_digest(p)) for p in sorted(patches.glob("*.patch"))])
        if expected_patches is None or expected_patches!=actual:
            raise ValueError("stale or missing app-patch identity")
    if check: return bundle
    destination=assets/"preset-genres"
    with tempfile.TemporaryDirectory(dir=assets) as temporary:
        staged=Path(temporary)/"preset-genres"
        shutil.copytree(bundle,staged)
        verify_bundle(staged,records)
        backup=assets/"preset-genres.previous"
        if backup.exists(): raise ValueError("unfinished previous genre import")
        if destination.exists(): destination.rename(backup)
        try:
            staged.rename(destination)
        except BaseException:
            if backup.exists(): backup.rename(destination)
            raise
        if backup.exists(): shutil.rmtree(backup)
    return destination
