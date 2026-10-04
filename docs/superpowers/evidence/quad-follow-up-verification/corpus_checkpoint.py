"""Push immutable incremental backups of completed native corpus evidence.

Stdlib only. Never alters the live renderer or its records. A remote checkpoint
is acknowledged only when origin advertises the exact committed backup HEAD.
"""
import argparse
from collections import Counter
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import threading
import time
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[4]
WORK = ROOT / "build/follow-ups/corpus-baseline"
DEFAULT_BACKUP = ROOT.parents[1] / ".worktrees/quad-lines-corpus-backup"
BRANCH = "evidence/quad-lines-corpus-2026-10-04"
ARCHIVE_DIR = Path("docs/superpowers/evidence/quad-follow-up-verification/corpus-checkpoints")
PREFIX = Path("build/follow-ups/corpus-baseline")
MAX_ARCHIVE = 25 * 1024 * 1024
BATCH_INPUT_LIMIT = 20 * 1024 * 1024
MAX_FILE = 100 * 1024 * 1024
STOP = threading.Event()
ROLE = "supplementary-direct-patched-projectm-not-projectmtv-core"
TERMINAL = {"success", "failed", "timeout", "nondeterministic"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def sealed(value):
    return dict(value, payload_sha256=digest(value))


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n")
    os.replace(temp, path)


def read_payload(path, protocol_hash, record):
    if not path.is_file():
        raise ValueError(f"missing evidence file: {path}")
    row = json.loads(path.read_text())
    if row.get("payload_sha256") != digest({k: v for k, v in row.items() if k != "payload_sha256"}):
        raise ValueError(f"checksum mismatch: {path}")
    key = digest({"protocol_sha256": protocol_hash, "preset": record})
    if (row.get("key") != key or row.get("protocol_sha256") != protocol_hash
            or row.get("preset") != record or row.get("status") not in TERMINAL):
        raise ValueError(f"provenance/status mismatch: {path}")
    return row


def evidence_path(work, relative):
    path = work / relative
    if not path.resolve().is_relative_to(work.resolve()) or not path.is_file():
        raise ValueError(f"missing or unsafe evidence file: {relative}")
    return path


def validate_record(work, protocol, record):
    key = digest({"protocol_sha256": protocol["sha256"], "preset": record})
    target = work / "rows" / f"{key}.json"
    row = read_payload(target, protocol["sha256"], record)
    paths = {target}
    repeats = []
    links = row.get("runs", [])
    if not links and not (row["status"] == "failed" and row.get("error")):
        raise ValueError("missing terminal repeat links")
    if links and len(links) != 2:
        raise ValueError("missing terminal repeats")
    for index, relative in enumerate(links, 1):
        path = evidence_path(work, relative)
        run = read_payload(path, protocol["sha256"], record)
        if run.get("repeat") != index:
            raise ValueError("repeat provenance mismatch")
        repeats.append(run); paths.add(path)
        for field in ("manifest_path", "stderr_gzip", "bands_gzip"):
            if run.get(field):
                paths.add(evidence_path(work, run[field]))
        if run.get("manifest_path"):
            paths.add(evidence_path(work, str(Path(run["manifest_path"]).parent / "job.json")))
    for relative in row.get("thumbnails", []):
        paths.add(evidence_path(work, relative))
    successful = all(r["status"] == "success" for r in repeats) and len(repeats) == 2
    if row["status"] in ("success", "nondeterministic"):
        expected = protocol["frames_per_repeat"]
        if not successful or any(r.get("frames_observed") != expected
                or len(r.get("sha256_frames", [])) != expected
                or not all(isinstance(h, str) and len(h) == 64 for h in r["sha256_frames"])
                or len(r.get("sha256_all_frames", "")) != 64 for r in repeats):
            raise ValueError("incomplete native repeat hashes")
        exact = (repeats[0]["sha256_all_frames"] == repeats[1]["sha256_all_frames"]
                 and repeats[0]["sha256_frames"] == repeats[1]["sha256_frames"])
        if (row["status"] == "success") != exact or row.get("repeat_exact") != exact:
            raise ValueError("repeat status contradicts native hashes")
    # Include frozen job artifacts even when a worker raised before reporting paths.
    jobs = work / "jobs" / key
    if jobs.exists():
        for path in jobs.rglob("*"):
            if path.is_file() and path.suffix != ".tmp":
                paths.add(evidence_path(work, str(path.relative_to(work))))
    files = []
    for path in sorted(paths):
        if path.stat().st_size >= MAX_FILE:
            raise ValueError("individual evidence file exceeds GitHub limit")
        files.append({"path": (PREFIX / path.relative_to(work)).as_posix(),
                      "source_relative": path.relative_to(work).as_posix(),
                      "bytes": path.stat().st_size, "sha256": file_hash(path)})
    return {"key": key, "preset": record, "status": row["status"], "files": files}


def verified_archive(path, protocol_hash):
    with zipfile.ZipFile(path) as archive:
        manifest = json.loads(archive.read("checkpoint-manifest.json"))
        if manifest.get("protocol_sha256") != protocol_hash:
            raise ValueError("archive protocol provenance mismatch")
        expected = {f["path"] for f in manifest["files"]} | {"checkpoint-manifest.json"}
        if len(expected) != len(manifest["files"]) + 1 or set(archive.namelist()) != expected or len(archive.namelist()) != len(expected):
            raise ValueError("archive has missing, duplicate or unexpected members")
        row_keys = set()
        for member in manifest["files"]:
            name = member["path"]
            if Path(name).is_absolute() or ".." in Path(name).parts:
                raise ValueError("unsafe archive member")
            with archive.open(name) as stream:
                hashed, count = hashlib.sha256(), 0
                for data in iter(lambda: stream.read(1024*1024), b""):
                    hashed.update(data); count += len(data)
            if count != member["bytes"] or hashed.hexdigest() != member["sha256"]:
                raise ValueError(f"archive member checksum mismatch: {name}")
            if name.startswith((PREFIX / "rows").as_posix() + "/") and name.endswith(".json"):
                row = json.loads(archive.read(name))
                if row.get("payload_sha256") != digest({k: v for k, v in row.items() if k != "payload_sha256"}):
                    raise ValueError("archive row checksum mismatch")
                if row.get("protocol_sha256") != protocol_hash or row.get("status") not in TERMINAL:
                    raise ValueError("archive row provenance mismatch")
                expected_key = digest({"protocol_sha256": protocol_hash, "preset": row.get("preset")})
                if row.get("key") != expected_key:
                    raise ValueError("archive row key provenance mismatch")
                row_keys.add(row["key"])
        declared = set(manifest.get("covered_preset_keys", row_keys))
        if row_keys and declared != row_keys:
            raise ValueError("archive coverage differs from retained rows")
        return declared


def pending_records(records, covered):
    return [record for record in records if record["key"] not in covered]


def remote_confirmed(local_head, remote_head):
    return bool(local_head) and local_head == remote_head


def git(backup, *args):
    result = subprocess.run(["git", "-C", str(backup), *args], capture_output=True, text=True,
                            env=dict(os.environ, GIT_TERMINAL_PROMPT="0"), timeout=180)
    if result.returncode:
        # Authentication output may contain private information; retain category only.
        raise RuntimeError(f"git {args[0]} failed (exit {result.returncode}); retry required")
    return result.stdout.strip()


def push_and_confirm(backup):
    head = git(backup, "rev-parse", "HEAD")
    git(backup, "push", "origin", f"HEAD:refs/heads/{BRANCH}")
    advertised = git(backup, "ls-remote", "--heads", "origin", f"refs/heads/{BRANCH}")
    remote_head = advertised.split()[0] if advertised else None
    if not remote_confirmed(head, remote_head):
        raise RuntimeError("remote did not acknowledge backup HEAD; retry required")
    return head


def covered_archives(backup, protocol_hash, memo):
    covered = set()
    files = sorted((backup / ARCHIVE_DIR).glob("*.zip"))
    files += sorted((backup / ARCHIVE_DIR / "incremental").glob("*.zip"))
    for archive in files:
        stat = archive.stat()
        signature = (str(archive), stat.st_size, stat.st_mtime_ns)
        if signature not in memo:
            sidecar = json.loads(archive.with_suffix(".json").read_text())
            if sidecar.get("archive_sha256") != file_hash(archive):
                raise ValueError("archive outer checksum mismatch")
            memo[signature] = verified_archive(archive, protocol_hash)
        keys = memo[signature]
        if covered & keys:
            raise ValueError("duplicate preset coverage across archives")
        covered.update(keys)
    return covered


def write_batch(backup, work, protocol_hash, batch):
    keys = sorted(item["key"] for item in batch)
    name = "batch-" + digest({"protocol": protocol_hash, "keys": keys})[:20]
    directory = backup / ARCHIVE_DIR / "incremental"
    directory.mkdir(parents=True, exist_ok=True)
    archive_path = directory / (name + ".zip")
    if archive_path.exists():
        raise ValueError("immutable archive already exists unexpectedly")
    files = [file for item in batch for file in item["files"]]
    manifest = {"schema_version": 1, "evidence_role": ROLE, "protocol_sha256": protocol_hash,
                "covered_preset_keys": keys, "complete_coverage": False,
                "presets": [{"key": item["key"], "preset": item["preset"], "status": item["status"]} for item in batch],
                "files": [{k: v for k, v in file.items() if k != "source_relative"} for file in files]}
    temporary = archive_path.with_suffix(".zip.tmp")
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for file in files:
                source = work / file["source_relative"]
                if file_hash(source) != file["sha256"]:
                    raise ValueError("completed evidence changed before checkpoint")
                archive.write(source, file["path"])
            archive.writestr("checkpoint-manifest.json", json.dumps(manifest, sort_keys=True, ensure_ascii=False))
        if temporary.stat().st_size > MAX_ARCHIVE:
            raise ValueError("batch archive exceeds 25MiB; no commit made")
        if verified_archive(temporary, protocol_hash) != set(keys):
            raise ValueError("batch coverage verification failed")
        os.replace(temporary, archive_path)
        sidecar = {"evidence_role": ROLE, "protocol_sha256": protocol_hash, "archive": archive_path.name,
                   "archive_sha256": file_hash(archive_path), "archive_bytes": archive_path.stat().st_size,
                   "covered_preset_keys": keys, "verified_terminal_presets": len(keys),
                   "statuses": dict(Counter(item["status"] for item in batch))}
        atomic(archive_path.with_suffix(".json"), sidecar)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise
    relative = archive_path.relative_to(backup).as_posix()
    git(backup, "add", "--", relative, relative.removesuffix(".zip") + ".json")
    git(backup, "commit", "-m", f"evidence: checkpoint {len(keys)} additional native corpus presets")
    return archive_path


def checkpoint_cycle(backup, work, state_path, memo):
    if git(backup, "branch", "--show-current") != BRANCH:
        raise ValueError("backup worktree is on an unexpected branch")
    if git(backup, "status", "--porcelain"):
        raise ValueError("backup worktree contains uncommitted changes; refusing to mix evidence")
    protocol = json.loads((work / "protocol.json").read_text())
    protocol_hash = protocol["sha256"]
    if digest({k: v for k, v in protocol.items() if k != "sha256"}) != protocol_hash:
        raise ValueError("live protocol checksum mismatch")
    inventory = json.loads((work / "inventory.json").read_text())
    if digest(inventory["presets"]) != inventory["corpus_sha256"] or inventory["count"] != len(inventory["presets"]):
        raise ValueError("live inventory checksum mismatch")
    if protocol.get("corpus_sha256") != inventory["corpus_sha256"]:
        raise ValueError("inventory differs from immutable protocol corpus")
    covered = covered_archives(backup, protocol_hash, memo)
    expected_keys = {digest({"protocol_sha256": protocol_hash, "preset": record}) for record in inventory["presets"]}
    if not covered.issubset(expected_keys):
        raise ValueError("archive coverage contains keys outside the immutable corpus")
    previous = json.loads(state_path.read_text()) if state_path.exists() else {}
    state = {"pid": os.getpid(), "evidence_role": ROLE, "branch": BRANCH, "backup_worktree": str(backup),
             "protocol_sha256": protocol_hash, "inventory_count": inventory["count"],
             "remote_verified_presets": previous.get("remote_verified_presets", 0),
             "remote_verified_head": previous.get("remote_verified_head"),
             "locally_committed_presets": len(covered), "state": "checking", "integrity_issues": [],
             "updated_unix_seconds": time.time(), "complete_remote_coverage": False}
    atomic(state_path, state)
    # Retry any prior unpushed commit before creating another batch.
    head = push_and_confirm(backup)
    state.update(remote_verified_head=head, remote_verified_presets=len(covered), state="scanning")
    atomic(state_path, state)
    candidates, issues = [], []
    for record in inventory["presets"]:
        key = digest({"protocol_sha256": protocol_hash, "preset": record})
        if key in covered or not (work / "rows" / f"{key}.json").exists():
            continue
        try:
            candidates.append(validate_record(work, protocol, record))
        except (ValueError, OSError, KeyError, TypeError) as error:
            issues.append({"preset": record["path"], "error": str(error)})
    state.update(verified_pending_presets=len(candidates), integrity_issues=issues)
    atomic(state_path, state)
    batch, size = [], 0
    def publish(items):
        nonlocal covered, state
        path = write_batch(backup, work, protocol_hash, items)
        covered.update(item["key"] for item in items)
        state.update(locally_committed_presets=len(covered), state="pushing", last_archive=path.name)
        atomic(state_path, state)
        head = push_and_confirm(backup)
        state.update(remote_verified_head=head, remote_verified_presets=len(covered), state="backed_up",
                     updated_unix_seconds=time.time())
        atomic(state_path, state)
        print(f"remote checkpoint confirmed: {len(covered)}/{inventory['count']} presets; {path.name}; HEAD {head}", flush=True)
    for item in candidates:
        amount = sum(file["bytes"] for file in item["files"])
        if amount > BATCH_INPUT_LIMIT:
            raise ValueError("single preset exceeds conservative checkpoint batch budget")
        if batch and size + amount > BATCH_INPUT_LIMIT:
            publish(batch); batch, size = [], 0
        batch.append(item); size += amount
    if batch:
        publish(batch)
    state.update(state="waiting", complete_remote_coverage=len(covered) == inventory["count"] and not issues,
                 verified_pending_presets=0, updated_unix_seconds=time.time())
    if state["complete_remote_coverage"]:
        state["state"] = "complete"
    atomic(state_path, state)
    return state


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.work=Path(self.temp.name)
        self.protocol={"sha256":"protocol", "frames_per_repeat":2}
        self.record={"path":"x.milk", "sha256":"source", "size_bytes":1}
        self.key=digest({"protocol_sha256":"protocol","preset":self.record})
        self.base={"key":self.key,"protocol_sha256":"protocol","preset":self.record}
        for repeat in (1,2):
            value=sealed(dict(self.base,status="success",repeat=repeat,frames_observed=2,
                              sha256_frames=["a"*64,"b"*64],sha256_all_frames="c"*64,
                              window_mean_thumbnail={"count":1}))
            self.write(f"runs/{self.key}/repeat-{repeat}.json",value)
        self.write(f"rows/{self.key}.json",sealed(dict(self.base,status="success",repeat_exact=True,
                   runs=[f"runs/{self.key}/repeat-{i}.json" for i in (1,2)],thumbnails=[f"thumbnails/{self.key}/frame-001.png"])))
        thumb=self.work/f"thumbnails/{self.key}/frame-001.png";thumb.parent.mkdir(parents=True);thumb.write_bytes(b"png evidence")

    def tearDown(self):
        self.temp.cleanup()

    def write(self,path,value):
        target=self.work/path;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(value))

    def test_completed_record_retains_native_repeat_and_thumbnail_evidence(self):
        result=validate_record(self.work,self.protocol,self.record)
        self.assertEqual(result["key"],self.key)
        self.assertEqual(len(result["files"]),4)

    def test_corrupt_repeat_rejected(self):
        target=self.work/f"runs/{self.key}/repeat-2.json"
        value=json.loads(target.read_text());value["sha256_frames"][0]="changed";target.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError,"checksum"):
            validate_record(self.work,self.protocol,self.record)

    def test_missing_thumbnail_rejected(self):
        (self.work/f"thumbnails/{self.key}/frame-001.png").unlink()
        with self.assertRaisesRegex(ValueError,"missing"):
            validate_record(self.work,self.protocol,self.record)

    def test_wrong_provenance_rejected(self):
        with self.assertRaisesRegex(ValueError,"missing|provenance"):
            validate_record(self.work,dict(self.protocol,sha256="other"),self.record)

    def test_failed_terminal_presets_remain_checkpointable(self):
        target=self.work/f"rows/{self.key}.json"
        self.write(str(target.relative_to(self.work)),sealed(dict(self.base,status="failed",error="orchestration failure",warnings=[])))
        result=validate_record(self.work,self.protocol,self.record)
        self.assertEqual(result["status"],"failed")
        self.assertEqual(len(result["files"]),1)

    def test_partial_preset_without_terminal_row_is_not_checkpointable(self):
        (self.work/f"rows/{self.key}.json").unlink()
        with self.assertRaisesRegex(ValueError,"missing"):
            validate_record(self.work,self.protocol,self.record)

    def test_resume_never_packs_covered_keys_twice(self):
        records=[{"key":"a"},{"key":"b"}]
        self.assertEqual(pending_records(records,{"a"}),[{"key":"b"}])

    def test_failed_push_cannot_acknowledge_remote_backup(self):
        self.assertFalse(remote_confirmed("new","old"))
        self.assertFalse(remote_confirmed("new",None))
        self.assertTrue(remote_confirmed("new","new"))

    def test_real_git_push_failure_then_retry_preserves_remote_acknowledgement(self):
        repository=self.work/"git-repository";repository.mkdir()
        remote=self.work/"origin.git"
        def command(*args):
            return subprocess.run(["git",*args],check=True,capture_output=True,text=True).stdout.strip()
        command("init","--bare",str(remote))
        command("-C",str(repository),"init","-b",BRANCH)
        command("-C",str(repository),"config","user.name","Checkpoint test")
        command("-C",str(repository),"config","user.email","checkpoint-test@example.invalid")
        (repository/"evidence.txt").write_text("first")
        command("-C",str(repository),"add","evidence.txt")
        command("-C",str(repository),"commit","-m","first")
        command("-C",str(repository),"remote","add","origin",str(remote))
        first=push_and_confirm(repository)
        (repository/"evidence.txt").write_text("second")
        command("-C",str(repository),"commit","-am","second")
        second=command("-C",str(repository),"rev-parse","HEAD")
        command("-C",str(repository),"remote","set-url","origin",str(self.work/"missing.git"))
        with self.assertRaisesRegex(RuntimeError,"retry required"):
            push_and_confirm(repository)
        self.assertEqual(command("--git-dir",str(remote),"rev-parse",f"refs/heads/{BRANCH}"),first)
        command("-C",str(repository),"remote","set-url","origin",str(remote))
        self.assertEqual(push_and_confirm(repository),second)
        self.assertEqual(push_and_confirm(repository),second)

    def test_archive_corrupt_member_rejected(self):
        import zipfile
        path=self.work/"checkpoint.zip"
        manifest={"protocol_sha256":"protocol","covered_preset_keys":["a"],
                  "files":[{"path":"row.json","sha256":hashlib.sha256(b"correct").hexdigest(),"bytes":7}]}
        with zipfile.ZipFile(path,"w") as archive:
            archive.writestr("checkpoint-manifest.json",json.dumps(manifest))
            archive.writestr("row.json",b"changed")
        with self.assertRaisesRegex(ValueError,"checksum"):
            verified_archive(path,"protocol")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--backup-worktree", type=Path, default=DEFAULT_BACKUP)
    parser.add_argument("--work", type=Path, default=WORK)
    parser.add_argument("--interval", type=int, default=600)
    parser.add_argument("--state-dir", type=Path, default=ROOT / "build/follow-ups/corpus-checkpoint-monitor")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=[__file__]); return
    if args.interval < 30:
        parser.error("interval must be at least 30 seconds")
    args.state_dir.mkdir(parents=True, exist_ok=True)
    state_path = args.state_dir / "status.json"
    for number in (signal.SIGTERM, signal.SIGINT):
        signal.signal(number, lambda *_: STOP.set())
    memo = {}
    with (args.state_dir / "monitor.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while not STOP.is_set():
            try:
                state = checkpoint_cycle(args.backup_worktree, args.work, state_path, memo)
                print(json.dumps(state, sort_keys=True), flush=True)
                if state["complete_remote_coverage"] or args.once:
                    break
            except Exception as error:
                state = json.loads(state_path.read_text()) if state_path.exists() else {}
                state.update(state="retry_required", pid=os.getpid(),
                             error=f"{type(error).__name__}: {error}", updated_unix_seconds=time.time())
                atomic(state_path, state)
                print(f"checkpoint retry required: {type(error).__name__}: {error}", flush=True)
                if args.once:
                    raise SystemExit(1)
            STOP.wait(args.interval)


if __name__ == "__main__":
    main()
