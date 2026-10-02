from dataclasses import replace
from pathlib import Path
import hashlib
import json
import os
import tempfile
import sys

import numpy as np

from .features import measure_frame
from .identity import canonical_json, digest, file_digest, load_json
from .models import Fingerprint, JobSpec, PresetRecord, RunConfig, StaticEvidence
from .response import _effect, _series, beat_coupling, fingerprint
from .worker import render_job
from .cache import read_cached_run,write_atomic


def assess_music_run(run: dict, control: dict, onset_times: list[float]) -> dict:
    reasons = []
    if run.get("status") != "success" or control.get("status") != "success":
        reasons.append("render_failure")
    if run.get("prefix_sha256") != control.get("prefix_sha256"):
        reasons.append("pre_intervention_drift")
    if reasons:
        return {"status":"failed", "reasons":reasons}
    response, variation = _effect(run, control)
    fps = run["fps"]
    warmup = run.get("warmup_frames", 0)
    cue_frames = [round(t * fps) - warmup for t in onset_times]
    events = np.r_[0, np.maximum(np.diff(variation), 0)] if len(variation) else variation
    coupling = beat_coupling(events, cue_frames, fps)
    observed = fingerprint(PresetRecord("observed.milk","0"*64,0),
                           {"steady":run}, StaticEvidence(True,[],[])).normalized
    observed["beat_lock"] = coupling["strength"]
    density = len(cue_frames) / max(len(variation) / fps, 1e-8)
    need = min(1.0, density / 3)
    musical_fit = .65 * response + .35 * (1 - need + need * coupling["strength"])
    return {"status":"success", "response":response, "music_fit":musical_fit,
            "beat_evidence":coupling, "observed_features":observed, "reasons":[],
            "coverage":float(np.mean(_series(run,"coverage"))),
            "method":"matched carrier control, causal feature trajectories, fixed-lag shuffled/shifted cue controls"}


def collect_run(worker: Path, job: JobSpec, cache: Path, onsets: list[float], timeout_seconds: float=120) -> dict:
    from dataclasses import asdict
    cache.mkdir(parents=True, exist_ok=True)
    key = digest({"preset":job.preset.sha256, "name":job.preset.path,
                  "pcm":file_digest(job.pcm_path), "config":asdict(job.config),
                  "worker":file_digest(worker), "identity":asdict(job.identity),
                  "textures":[(p.name,file_digest(p)) for p in sorted(job.texture_root.iterdir())
                              if p.is_file() and p.name != ".DS_Store"],
                  "feature_code":file_digest(Path(__file__).parent/"features.py")})
    target = cache/f"{key}.json"
    stored=read_cached_run(target,key)
    if stored is not None:
        return dict(stored,reused=True,onsets=onsets)
    previous = None
    frames = []
    prefix = hashlib.sha256()
    warmup = round(job.config.warmup_seconds * job.config.fps)
    def observe(frame):
        nonlocal previous
        if len(frames)<warmup:
            prefix.update(frame.tobytes())
        frames.append(measure_frame(frame,previous,job.config.fps))
        previous=frame.copy()
    result=render_job(worker,job,observe,timeout_seconds)
    log=result.diagnostics_path.read_text(errors="replace")
    warnings=[line for line in log.splitlines() if any(term in line.lower()
              for term in ("unable to load","could not load","failed to load","warning"))]
    run={"status":result.status,"fps":job.config.fps,"warmup_frames":warmup,
         "prefix_sha256":prefix.hexdigest(),"frames":frames,"onsets":onsets,
         "warnings":warnings,"manifest":result.manifest,"reused":False,
         "raw_frames_retained":False}
    if result.status=="success":
        stored={"schema_version":1,"key":key,"run":run,"payload_sha256":digest(run)}
        write_atomic(target,stored)
    return run


def validate_candidates(fingerprints: list[Fingerprint], decisions: list, corpus,
                        repo: Path, work: Path, worker: Path, identity, top_per_genre: int=1) -> list[Fingerprint]:
    from .probes import make_probes
    work.mkdir(parents=True,exist_ok=True)
    config=RunConfig(measurement_seconds=30)
    steady=next(p for p in make_probes(config,work/"probes") if p["id"]=="steady")
    carrier=np.fromfile(steady["pcm_path"],dtype="<f4")[:round(config.warmup_seconds*44100)]
    records={fp.preset.path:fp for fp in fingerprints}
    selected={}
    for genre_id in sorted({d.genre_id for d in decisions}):
        ranked=[d for d in decisions if d.genre_id==genre_id and d.included][:top_per_genre]
        selected[genre_id]=[d.preset.path for d in ranked]
    texture_root=repo/"core/src/main/assets/textures"
    preset_root=repo/"core/src/main/assets/presets"
    controls={}
    observations={name:list(fp.evidence.get("music_validation",[])) for name,fp in records.items()}
    for genre_id,names in selected.items():
        tracks=[t for t in corpus.tracks if genre_id in t.genre_ids]
        for name in names:
            record=records[name].preset
            if file_digest(preset_root/name)!=record.sha256:
                raise ValueError(f"stale preset fingerprint: {name}")
            if name not in controls:
                control_job=JobSpec(record,"music-control",Path(steady["pcm_path"]),config,identity,
                                    preset_root,texture_root,work/"jobs")
                controls[name]=collect_run(worker,control_job,work/"cache",[])
            for track in tracks:
                source=corpus.descriptors[track.id]
                start,end=track.excerpts[0]
                count=round(config.measurement_seconds*44100)
                audio=np.memmap(source["pcm_path"],dtype="<f4",mode="r")
                segment=np.asarray(audio[round(start*44100):round(start*44100)+count])
                if len(segment)!=count:
                    raise ValueError("initial candidate validation requires a full thirty-second excerpt")
                pcm=work/f"music-{digest([track.sha256,start,end])[:20]}.f32"
                np.concatenate([carrier,segment]).astype("<f4").tofile(pcm)
                onsets=[t-start+config.warmup_seconds for t in source["onsets"] if start<=t<start+30]
                job=JobSpec(record,track.id,pcm,config,identity,preset_root,texture_root,work/"jobs")
                run=collect_run(worker,job,work/"cache",onsets)
                assessment=assess_music_run(run,controls[name],onsets)
                assessment.update(genre_id=genre_id,track_id=track.id,track_sha256=track.sha256,
                                  excerpt=[start,start+30],renderer_identity=run["manifest"].get("identity"),
                                  reused=run["reused"])
                observations[name]=[o for o in observations[name] if not
                                    (o.get("genre_id")==genre_id and o.get("track_sha256")==track.sha256)]+[assessment]
                print(f"validated {genre_id}: {track.id} / {name}: {assessment['status']}",file=sys.stderr,flush=True)
                evidence=dict(records[name].evidence,music_validation=observations[name])
                current=replace(records[name],evidence=evidence)
                from dataclasses import asdict
                (work/f"{digest(name)[:12]}-fingerprint.json").write_text(canonical_json(asdict(current)))
    return [replace(fp,evidence=dict(fp.evidence,music_validation=observations[fp.preset.path])) for fp in fingerprints]
