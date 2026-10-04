"""Verified incremental remote backup of actual-core records, without device operations.

Archives store content-addressed 8MiB chunks. File aliases reconstruct exact
original paths, so repeated PNGs have one payload. Push acknowledgement is exact
remote HEAD; locally committed data is never labelled remote before that check.
"""
import argparse
from contextlib import contextmanager
import copy
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import threading
import time
import zipfile

import run

ROOT = run.ROOT
BRANCH = "evidence/quad-lines-core-corpus"
BACKUP = ROOT.parents[1] / ".worktrees/quad-lines-core-corpus-backup"
STORE = Path("docs/superpowers/evidence/quad-follow-up-verification/core-corpus/remote-checkpoints")
CHUNK_SIZE = 8 * 1024 * 1024
BATCH_LIMIT = 20 * 1024 * 1024
ARCHIVE_LIMIT = 25 * 1024 * 1024
STOP = threading.Event()


def verify_protocol(work):
    protocol = json.loads((work / "protocol.json").read_text())
    if run.digest({k:v for k,v in protocol.items() if k!="sha256"}) != protocol["sha256"]:
        raise ValueError("protocol checksum mismatch")
    if protocol.get("backend") != "production-projectm-tv-core-ProjectMJNI-EGL-GLES3":
        raise ValueError("backup requires actual projectm-tv:core backend")
    inventory = json.loads((work / "inventory.json").read_text())
    if (inventory["count"] != 9606 or len(inventory["presets"]) != 9606
            or run.digest(inventory["presets"]) != inventory["corpus_sha256"]
            or protocol["corpus_sha256"] != inventory["corpus_sha256"]):
        raise ValueError("immutable full corpus mismatch")
    for role in protocol["roles"].values():
        if run.file_hash(role["apk_path"]) != role["apk_sha256"]:
            raise ValueError("immutable APK checksum mismatch")
        with zipfile.ZipFile(role["apk_path"]) as archive:
            embedded=json.loads(archive.read("assets/backend-identity.json"))
            if embedded!=role["backend_identity"]:
                raise ValueError("APK embedded source identity differs from protocol")
            core = archive.read(role["backend_identity"]["core_library_entry"])
            if hashlib.sha256(core).hexdigest() != role["core_sha256"]:
                raise ValueError("compiled APK core provenance mismatch")
    for pcm in protocol["pcm"].values():
        if run.file_hash(pcm["path"]) != pcm["sha256"]:
            raise ValueError("immutable PCM checksum mismatch")
    return protocol, inventory


def verify_terminal_producer(directory, row, protocol, record):
    packet_path=directory/"job.json"
    packet=json.loads(packet_path.read_text()) if packet_path.exists() else None
    expected={"schema_version":2,"job_id":row["key"],"protocol_sha256":protocol["sha256"],
              "preset_filename":record["path"],"preset_sha256":record["sha256"],
              "capture_mode":row["capture_mode"],"measurement_frames":row["measurement_frames"],
              "expected_core_sha256":protocol["roles"][row["role"]]["core_sha256"]}
    if packet is not None:
        for field,value in expected.items():
            if packet.get(field)!=value:raise ValueError("input job provenance mismatch: "+field)
        for field in ("width","height","fps","seed"):
            if field in protocol["config"] and packet.get(field)!=protocol["config"][field]:
                raise ValueError("input configuration provenance mismatch: "+field)
    relative=row.get("result_path","output/result.json")
    result_path=directory/relative
    if not result_path.resolve().is_relative_to(directory.resolve()):raise ValueError("unsafe producer result path")
    available=[p for p in [directory/"output/result.json",*directory.glob("attempts/*/output/result.json")] if p.is_file()]
    if any(p.resolve()!=result_path.resolve() for p in available):raise ValueError("available current producer result is not attributed to the row")
    if "result_path" in row and not result_path.is_file():raise ValueError("claimed producer result path is missing")
    result=row.get("result")
    if not result_path.exists() and result is None:
        if row["status"] not in ("failed","timeout") or not isinstance(row.get("error"),str) or not row["error"].strip():
            raise ValueError("missing producer result without explicit host failure")
        return
    if packet is None or not result_path.is_file() or not isinstance(result,dict):
        raise ValueError("missing producer result or input job provenance")
    if not any(f["path"]==relative for f in row["retained_files"]):
        raise ValueError("producer result is not retained evidence")
    if json.loads(result_path.read_text())!=result:raise ValueError("producer result differs from terminal row")
    for field in ("schema_version","job_id","protocol_sha256"):
        if result.get(field)!=packet[field]:raise ValueError("producer provenance mismatch: "+field)
    if result.get("status") not in ("success","failed"):raise ValueError("invalid producer status")
    if result["status"]=="failed":
        if row["status"]=="success" or not result.get("error"):raise ValueError("invalid producer failure status")
    elif row["status"] in ("failed","timeout") and not row.get("error"):
        raise ValueError("successful producer lacks explicit host failure reason")
    required=("capture_mode","capture_frames","width","height","fps","seed")
    if result["status"]=="success":
        for field in required:
            if field not in packet:raise ValueError("input job provenance missing: "+field)
    available={"core_sha256":expected["expected_core_sha256"],"requested_preset_sha256":record["sha256"]}
    available.update({field:packet[field] for field in ("preset_filename",*required) if field in packet})
    for field,value in available.items():
        # The preset hash establishes identity; a supplied filename must also match.
        mandatory=result["status"]=="success" and field!="preset_filename"
        if (field in result or mandatory) and result.get(field)!=value:
            raise ValueError("producer provenance mismatch: "+field)


def verify_job(work, protocol, inventory, job_id):
    directory = work / "jobs" / job_id
    path = directory / "row.json"
    if not path.exists():
        return None
    row = run.read_cached(path, job_id, protocol["sha256"])
    if row is None:
        raise ValueError("terminal row checksum/provenance or retained file missing")
    if row.get("role") not in protocol["roles"] or row.get("repeat") not in (1,2):
        raise ValueError("job role/repeat provenance mismatch")
    record = next((r for r in inventory["presets"] if r==row.get("preset")), None)
    if record is None:
        raise ValueError("preset byte provenance differs from immutable corpus")
    expected = run.job_key(protocol["sha256"],record,row["role"],row["capture_mode"],row["repeat"],row["measurement_frames"])
    if expected != job_id:
        raise ValueError("job key provenance mismatch")
    verify_terminal_producer(directory,row,protocol,record)
    if row["status"] == "success":
        job = json.loads((directory / "job.json").read_text())
        result = json.loads((directory / "output/result.json").read_text())
        if result != row.get("result"):
            raise ValueError("APK result differs from terminal row")
        if result.get("core_sha256") != protocol["roles"][row["role"]]["core_sha256"]:
            raise ValueError("runtime core provenance differs from role")
        frames = run.read_frames(directory / "output")
        trace = directory / "output/frames.jsonl"
        if trace.exists():
            raw_trace = trace.read_bytes()
        else:
            trace = directory / "output/frames.jsonl.gz"
            raw_trace = gzip.decompress(trace.read_bytes())
        original_sha = hashlib.sha256(raw_trace).hexdigest()
        if original_sha != result.get("frames_metadata_sha256"):
            raise ValueError("producer frame trace checksum mismatch")
        if row.get("frame_trace"):
            info = row["frame_trace"]
            if info["uncompressed_sha256"] != original_sha or info["compressed_sha256"] != run.file_hash(trace):
                raise ValueError("compressed frame trace provenance mismatch")
        discarded = {item["path"]:item["sha256"] for item in row.get("native_files_discarded_after_independent_verification",[])}
        # Re-run the shared observer validator with a plaintext trace in a read-only
        # temporary view. Verify available raw native files separately; intentional
        # pilot compaction preserves historical verification hashes, not raw bytes.
        normalized_job, normalized_result = dict(job,retain_native_frames=False), copy.deepcopy(result)
        with tempfile.TemporaryDirectory() as name:
            view = Path(name)
            (view/"frames.jsonl").write_bytes(raw_trace)
            for sample in normalized_result.get("selected_files",[]):
                if sample.get("path"):
                    relative = "output/"+sample["path"]
                    native = directory/relative
                    if native.exists():
                        if native.stat().st_size != sample["bytes"] or run.file_hash(native) != sample["sha256"]:
                            raise ValueError("native pilot checksum mismatch")
                    elif discarded.get(relative) != sample["sha256"] or row.get("native_verified") is not True:
                        raise ValueError("missing native pilot evidence without verified compaction")
                    sample.pop("path")
                thumbnail = run.safe_member(directory/"output",sample["thumbnail_path"])
                (view/sample["thumbnail_path"]).symlink_to(thumbnail.resolve())
            # Shared validation forbids escaping symlinks; copy tiny PNGs instead.
            for child in list(view.iterdir()):
                if child.is_symlink():
                    data=child.read_bytes();child.unlink();child.write_bytes(data)
            if run.validate_result(normalized_job,normalized_result,frames,view)!="success":
                raise ValueError("successful row does not satisfy core observer protocol")
    paths=[path]
    for file in row.get("retained_files",[]):
        target=run.safe_member(directory,file["path"])
        if run.file_hash(target)!=file["sha256"]:
            raise ValueError("retained file checksum changed")
        paths.append(target)
    return {"key":job_id,"status":row["status"],"preset":record,"role":row["role"],"repeat":row["repeat"],
            "capture_mode":row["capture_mode"],"measurement_frames":row["measurement_frames"],
            "files":[{"source":str(p),"path":p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.relative_to(work).as_posix()} for p in paths]}


def plan_payloads(files, known):
    payloads, aliases = {}, []
    for item in files:
        path=Path(item["source"])
        sha=hashlib.sha256();size=0;chunks=[]
        with path.open("rb") as stream:
            for data in iter(lambda:stream.read(CHUNK_SIZE),b""):
                checksum=hashlib.sha256(data).hexdigest();sha.update(data);size+=len(data)
                chunks.append({"sha256":checksum,"bytes":len(data)})
                if checksum not in known and checksum not in payloads:
                    payloads[checksum]={"source":str(path),"offset":size-len(data),"bytes":len(data)}
        aliases.append({"path":item["path"],"sha256":sha.hexdigest(),"bytes":size,"chunks":chunks})
    return {"payloads":payloads,"files":aliases}


def coalesce_units(units,known_blobs,known_files):
    known=set(known_blobs);aliases=dict(known_files)
    pending={"payloads":{},"files":[],"jobs":[],"bootstrap":False};size=0
    for unit in units:
        plan=plan_payloads(unit["files"],known|set(pending["payloads"]))
        new_files=[]
        for alias in plan["files"]:
            if alias["path"] in aliases:
                if aliases[alias["path"]]!=alias:raise ValueError("immutable backed-up file changed")
            else:new_files.append(alias);aliases[alias["path"]]=alias
        for checksum,payload in plan["payloads"].items():
            if pending["payloads"] and size+payload["bytes"]>BATCH_LIMIT:
                known.update(pending["payloads"])
                yield pending
                pending={"payloads":{},"files":[],"jobs":[],"bootstrap":False};size=0
            pending["payloads"][checksum]=payload;size+=payload["bytes"]
        pending["files"].extend(new_files);pending["jobs"].extend(unit["jobs"])
        pending["bootstrap"]=pending["bootstrap"] or unit.get("bootstrap",False)
    if pending["payloads"] or pending["files"] or pending["jobs"]:yield pending


def remote_acknowledged(local, remote):
    return bool(local) and local==remote


def git(backup,*args):
    result=subprocess.run(["git","-C",str(backup),*args],capture_output=True,text=True,
                          env=dict(os.environ,GIT_TERMINAL_PROMPT="0"),timeout=180)
    if result.returncode:
        raise RuntimeError(f"git {args[0]} failed exit{result.returncode}; retry required")
    return result.stdout.strip()


@contextmanager
def backup_writer_lock(backup):
    backup=Path(backup).resolve()
    lock_path=Path(git(backup,"rev-parse","--git-path","core-corpus-writer.lock"))
    if not lock_path.is_absolute():lock_path=backup/lock_path
    with lock_path.open("a+") as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("another core backup writer owns this checkout; retry required") from error
        try:
            yield
        finally:
            fcntl.flock(lock,fcntl.LOCK_UN)


def push(backup):
    head=git(backup,"rev-parse","HEAD")
    git(backup,"push","origin",f"HEAD:refs/heads/{BRANCH}")
    advertised=git(backup,"ls-remote","--heads","origin",f"refs/heads/{BRANCH}")
    remote=advertised.split()[0] if advertised else None
    if not remote_acknowledged(head,remote):
        raise RuntimeError("remote did not acknowledge exact core checkpoint HEAD")
    return head


def load_archives(backup,protocol_hash,memo):
    blobs,jobs,files=set(),{},{}
    all_archives=sorted((backup/STORE).glob("*/*.zip"))
    archives=sorted((backup/STORE/protocol_hash).glob("*.zip"))
    for path in all_archives:
        signature=(str(path),path.stat().st_size,path.stat().st_mtime_ns)
        if signature not in memo:
            sidecar=json.loads(path.with_suffix(".json").read_text())
            if run.file_hash(path)!=sidecar["archive_sha256"]:
                raise ValueError("checkpoint outer archive checksum mismatch")
            with zipfile.ZipFile(path) as archive:
                manifest=json.loads(archive.read("checkpoint-manifest.json"))
                expected={"blobs/"+s for s in manifest["blobs"]}|{"checkpoint-manifest.json"}
                if set(archive.namelist())!=expected or len(archive.namelist())!=len(expected):
                    raise ValueError("checkpoint archive member coverage mismatch")
                if manifest["protocol_sha256"]!=path.parent.name:
                    raise ValueError("checkpoint protocol partition provenance mismatch")
                for checksum in manifest["blobs"]:
                    with archive.open("blobs/"+checksum) as stream:
                        if hashlib.file_digest(stream,"sha256").hexdigest()!=checksum:
                            raise ValueError("checkpoint blob checksum mismatch")
                memo[signature]=manifest
        manifest=memo[signature]
        if blobs.intersection(manifest["blobs"]):
            raise ValueError("duplicate stored core blob payload")
        blobs.update(manifest["blobs"])
    for path in archives:
        signature=(str(path),path.stat().st_size,path.stat().st_mtime_ns)
        manifest=memo[signature]
        for file in manifest["files"]:
            if Path(file["path"]).is_absolute() or ".." in Path(file["path"]).parts:
                raise ValueError("unsafe checkpoint alias path")
            if any(c["sha256"] not in blobs for c in file["chunks"]):
                raise ValueError("checkpoint alias references missing payload")
            if file["path"] in files and files[file["path"]]!=file:
                raise ValueError("immutable checkpoint file changed")
            files[file["path"]]=file
        for job in manifest["jobs"]:
            if job["key"] in jobs:
                raise ValueError("duplicate covered core job")
            jobs[job["key"]]=job
    return blobs,jobs,files,len(archives)


def restore_files(backup,protocol_hash,destination):
    _,_,files,_=load_archives(backup,protocol_hash,{})
    locations={}
    for path in sorted((backup/STORE).glob("*/*.zip")):
        with zipfile.ZipFile(path) as archive:
            manifest=json.loads(archive.read("checkpoint-manifest.json"))
            for checksum in manifest["blobs"]:locations[checksum]=path
    for alias in files.values():
        target=destination/alias["path"]
        if not target.resolve().is_relative_to(destination.resolve()):raise ValueError("unsafe restore alias")
        if target.exists():
            if run.file_hash(target)==alias["sha256"]:continue
            raise ValueError("refusing to overwrite different/newer restored file")
        target.parent.mkdir(parents=True,exist_ok=True)
        temporary=target.with_name(target.name+".restore.tmp")
        sha,size=hashlib.sha256(),0
        with temporary.open("wb") as output:
            for chunk in alias["chunks"]:
                with zipfile.ZipFile(locations[chunk["sha256"]]) as archive:
                    data=archive.read("blobs/"+chunk["sha256"])
                if len(data)!=chunk["bytes"]:raise ValueError("restore chunk length mismatch")
                output.write(data);sha.update(data);size+=len(data)
        if sha.hexdigest()!=alias["sha256"] or size!=alias["bytes"]:raise ValueError("restored full-file checksum mismatch")
        os.replace(temporary,target)


def write_archive(backup,protocol_hash,sequence,payloads,files,jobs,bootstrap=False):
    directory=backup/STORE/protocol_hash;directory.mkdir(parents=True,exist_ok=True)
    name=f"batch-{sequence:06d}-"+run.digest({"blobs":sorted(payloads),"files":files,"jobs":jobs})[:16]
    path=directory/(name+".zip");temporary=path.with_suffix(".zip.tmp")
    if path.exists():raise ValueError("immutable archive already exists")
    manifest={"schema_version":2,"backend":"actual-projectm-tv-core","protocol_sha256":protocol_hash,
              "sequence":sequence,"blobs":sorted(payloads),"files":files,"jobs":jobs,
              "bootstrap":bootstrap,"complete_corpus_coverage":False,
              "restore":"For every file alias concatenate ordered blobs, verify fullSHA/bytes, write exact original relative path; one blob may serve many aliases"}
    with zipfile.ZipFile(temporary,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for checksum,source in sorted(payloads.items()):
            with Path(source["source"]).open("rb") as stream:
                stream.seek(source["offset"]);data=stream.read(source["bytes"])
            if len(data)!=source["bytes"] or hashlib.sha256(data).hexdigest()!=checksum:
                raise ValueError("source payload changed during checkpoint")
            archive.writestr("blobs/"+checksum,data)
        archive.writestr("checkpoint-manifest.json",run.canonical(manifest))
    if temporary.stat().st_size>ARCHIVE_LIMIT:raise ValueError("archive exceeds25MiB; no commit made")
    with zipfile.ZipFile(temporary) as archive:
        for checksum in payloads:
            if hashlib.sha256(archive.read("blobs/"+checksum)).hexdigest()!=checksum:
                raise ValueError("written archive blob checksum failed")
    os.replace(temporary,path)
    run.atomic(path.with_suffix(".json"),{"archive_sha256":run.file_hash(path),"archive_bytes":path.stat().st_size,
               "protocol_sha256":protocol_hash,"jobs":len(jobs),"blobs":len(payloads),"sequence":sequence})
    relative=path.relative_to(backup).as_posix()
    git(backup,"add","--",relative,relative.removesuffix(".zip")+".json")
    git(backup,"commit","-m",f"evidence: checkpoint core payload batch{sequence} with {len(jobs)} verified jobs")
    return path


def snapshot_files(work,protocol):
    paths=[work/"protocol.json",work/"inventory.json"]
    for audio in protocol["pcm"].values():paths.append(Path(audio["path"]))
    for role in protocol["roles"].values():
        apk=Path(role["apk_path"]);paths.append(apk)
        expected_diffs={role["backend_identity"].get(key) for key in ("clock_instrumentation_diff_sha256","engine_instrumentation_diff_sha256","cmake_instrumentation_diff_sha256")}
        matched=set()
        for path in apk.parent.glob("private-*-diff.patch"):
            checksum=run.file_hash(path)
            if checksum not in expected_diffs:raise ValueError("build diff snapshot does not match embedded provenance")
            matched.add(checksum);paths.append(path)
        if expected_diffs-{None}-matched:raise ValueError("missing reviewable private-core instrumentation diff")
        for path in (apk.parent/"harness-source").rglob("*"):
            if path.is_file():paths.append(path)
    # Freeze the runner matching this protocol even when later source epochs exist.
    runners=[Path(__file__).with_name(name) for name in ("run.py","run_v2.py")]
    found=False
    for runner in runners:
        if runner.is_file() and run.file_hash(runner)==protocol["runner_sha256"]:
            paths.append(runner);found=True;break
    if not found:
        for runner in runners:
            relative=runner.relative_to(ROOT).as_posix()
            for commit in git(ROOT,"log","--format=%H","--",relative).splitlines():
                data=subprocess.run(["git","-C",str(ROOT),"show",commit+":"+relative],capture_output=True,check=True).stdout
                if hashlib.sha256(data).hexdigest()==protocol["runner_sha256"]:
                    frozen=work/"snapshot-source"/runner.name;frozen.parent.mkdir(exist_ok=True);frozen.write_bytes(data);paths.append(frozen);found=True;break
            if found:break
    if not found:raise ValueError("historical protocol runner source not available")
    return [{"source":str(path),"path":path.relative_to(ROOT).as_posix()} for path in sorted(set(paths))]


def checkpoint_cycle(args,memo):
    args.work=Path(args.work).resolve()
    args.backup=Path(args.backup).resolve()
    with backup_writer_lock(args.backup):
        return _checkpoint_cycle(args,memo)


def _checkpoint_cycle(args,memo):
    backup,work,state_path=args.backup,args.work,args.state_dir/"status.json"
    if git(backup,"branch","--show-current")!=BRANCH:raise ValueError("unexpected backup worktree branch")
    if git(backup,"status","--porcelain"):raise ValueError("dirty backup requires manual archive verification/commit; no automatic data discard")
    protocol,inventory=verify_protocol(work);protocol_hash=protocol["sha256"]
    blobs,covered,files,sequence=load_archives(backup,protocol_hash,memo)
    expected={run.job_key(protocol_hash,r,role,"selected",repeat,360) for r in inventory["presets"] for role in protocol["roles"] for repeat in (1,2)}
    baseline_expected={run.job_key(protocol_hash,r,"baseline","selected",repeat,360) for r in inventory["presets"] for repeat in (1,2)}
    previous=json.loads(state_path.read_text()) if state_path.exists() else {}
    if previous.get("protocol_sha256") not in (None,protocol_hash):raise ValueError("monitor state belongs to another protocol")
    state={"pid":os.getpid(),"protocol_sha256":protocol_hash,"branch":BRANCH,"dataset":str(work),
           "expected_corpus_jobs":len(expected),"locally_committed_jobs":len(covered),
           "remote_verified_jobs":previous.get("remote_verified_jobs",0),
           "remote_verified_head":previous.get("remote_verified_head"),"state":"pushing_prior_commits",
           "integrity_issues":[],"complete_corpus_remote_coverage":False}
    run.atomic(state_path,state)
    head=push(backup)
    state.update(remote_verified_head=head,remote_verified_jobs=len(covered),remote_corpus_jobs=len(set(covered)&expected),remote_baseline_jobs=len(set(covered)&baseline_expected),
                 complete_baseline_remote_coverage=baseline_expected.issubset(covered))
    run.atomic(state_path,state)
    def publish(payloads,aliases,jobs,bootstrap=False):
        nonlocal sequence,blobs,covered,files,head,state
        path=write_archive(backup,protocol_hash,sequence,payloads,aliases,jobs,bootstrap)
        sequence+=1;blobs.update(payloads)
        for alias in aliases:files[alias["path"]]=alias
        for job in jobs:covered[job["key"]]=job
        state.update(state="pushing",locally_committed_jobs=len(covered),last_archive=path.name)
        run.atomic(state_path,state)
        head=push(backup)
        state.update(state="remote_confirmed",remote_verified_head=head,remote_verified_jobs=len(covered),
                     remote_corpus_jobs=len(set(covered)&expected),remote_baseline_jobs=len(set(covered)&baseline_expected),
                     complete_baseline_remote_coverage=baseline_expected.issubset(covered),updated_unix_seconds=time.time())
        run.atomic(state_path,state)
        print(f"remote core checkpoint confirmed: {len(covered)} jobs; {len(set(covered)&expected)}/{len(expected)} corpus jobs; {path.name}; HEAD{head}",flush=True)
    def store_unit(unit_files,jobs,bootstrap=False):
        plan=plan_payloads(unit_files,blobs)
        new_aliases=[f for f in plan["files"] if f["path"] not in files]
        for alias in plan["files"]:
            if alias["path"] in files and files[alias["path"]]!=alias:
                raise ValueError("immutable already-backed-up file content changed")
        batch,size={},0
        for checksum,payload in plan["payloads"].items():
            if batch and size+payload["bytes"]>BATCH_LIMIT:
                publish(batch,[],[],bootstrap);batch,size={},0
            batch[checksum]=payload;size+=payload["bytes"]
        if batch or new_aliases or jobs:
            publish(batch,new_aliases,jobs,bootstrap)
    units=[{"files":snapshot_files(work,protocol),"jobs":[],"bootstrap":True}]
    validated=0;validation_start=time.monotonic()
    for path in sorted((work/"jobs").glob("*/row.json")):
        key=path.parent.name
        if key in covered:continue
        try:
            item=verify_job(work,protocol,inventory,key)
            if item is None:continue
            job={k:v for k,v in item.items() if k!="files"}
            units.append({"files":item["files"],"jobs":[job]});validated+=1
        except (ValueError,OSError,KeyError,TypeError) as error:
            state["integrity_issues"].append({"key":key,"error":str(error)})
            run.atomic(state_path,state)
    validation_seconds=time.monotonic()-validation_start
    batches=0;publish_start=time.monotonic()
    for batch in coalesce_units(units,blobs,files):
        publish(batch["payloads"],batch["files"],batch["jobs"],batch["bootstrap"]);batches+=1
    state["cycle_measurement"]={"validated_new_jobs":validated,"validation_seconds":validation_seconds,
                                "cross_job_archives":batches,"publish_seconds":time.monotonic()-publish_start}
    state.update(state="finite_backup_finished" if args.once else "waiting",locally_committed_jobs=len(covered),
                 remote_verified_jobs=len(covered),remote_corpus_jobs=len(set(covered)&expected),
                 complete_corpus_remote_coverage=expected.issubset(covered) and not state["integrity_issues"],
                 remote_baseline_jobs=len(set(covered)&baseline_expected),
                 complete_baseline_remote_coverage=baseline_expected.issubset(covered) and not state["integrity_issues"],
                 updated_unix_seconds=time.time())
    for name in ("pilot-report.json","independent-pilot-audit.json","full-repeat-diagnostic.json","baseline-scan-launch.json","baseline-completion-index.json","baseline-progress.json","progress.json"):
        path=work/name
        if path.exists():
            # Mutable live reports are retained as immutable versioned snapshots.
            data=path.read_bytes()
            snapshot=work/"checkpoint-report-snapshots"/(hashlib.sha256(data).hexdigest()+"-"+name)
            snapshot.parent.mkdir(exist_ok=True)
            if not snapshot.exists():snapshot.write_bytes(data)
            store_unit([{"source":str(snapshot),"path":snapshot.relative_to(ROOT).as_posix()}],[])
    state["state"]="finite_backup_finished" if args.once else "waiting"
    run.atomic(state_path,state)
    return state


def final_checkpoint_ready(work,state):
    path=work/"baseline-completion-index.json"
    if not path.exists() or state.get("complete_baseline_remote_coverage"):
        return False
    index=json.loads(path.read_text())
    return (index.get("protocol_sha256")==state.get("protocol_sha256")
            and index.get("complete_coverage") is True and index.get("terminal_presets")==9606)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work",type=Path,required=True)
    parser.add_argument("--backup",type=Path,default=BACKUP)
    parser.add_argument("--state-dir",type=Path,required=True)
    parser.add_argument("--once",action="store_true")
    parser.add_argument("--interval",type=int,default=600)
    args=parser.parse_args();args.state_dir.mkdir(parents=True,exist_ok=True)
    if args.interval<30:parser.error("interval must be at least30seconds")
    for value in (signal.SIGINT,signal.SIGTERM):signal.signal(value,lambda *_:STOP.set())
    memo={}
    with (args.state_dir/"monitor.lock").open("a+") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        while not STOP.is_set():
            try:
                state=checkpoint_cycle(args,memo);print(run.canonical(state),flush=True)
                if args.once or state["complete_corpus_remote_coverage"]:break
            except Exception as error:
                path=args.state_dir/"status.json"
                state=json.loads(path.read_text()) if path.exists() else {}
                state.update(state="retry_required",error=f"{type(error).__name__}: {error}",pid=os.getpid(),updated_unix_seconds=time.time())
                run.atomic(path,state);print(run.canonical(state),flush=True)
                if args.once:raise SystemExit(1)
            deadline=time.monotonic()+args.interval
            while not STOP.is_set() and time.monotonic()<deadline:
                if final_checkpoint_ready(args.work,state):break
                STOP.wait(min(30,max(0,deadline-time.monotonic())))


if __name__=="__main__":main()
