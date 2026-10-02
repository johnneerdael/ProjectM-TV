from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict,replace
from pathlib import Path
import platform
import threading

import numpy as np

from .audio import describe_audio
from .cache import write_atomic
from .dependencies import trace_dependencies
from .identity import digest,file_digest,load_json
from .models import Corpus,EngineIdentity,Fingerprint,JobSpec,PipelineConfig,PipelineResult,PresetRecord,RunConfig
from .preset_parser import parse_preset
from .probes import make_probes
from .response import fingerprint
from .validation import collect_run


def analyze_library(records: list[PresetRecord], corpus: Corpus, config: RunConfig,
                    work: Path, worker: Path, *, repo: Path | None=None,
                    identity: EngineIdentity | None=None, concurrency: int=1,
                    timeout_seconds: float=120) -> list[Fingerprint]:
    repo=(repo or Path.cwd()).resolve()
    work=work.resolve()
    work.mkdir(parents=True,exist_ok=True)
    if concurrency<1 or timeout_seconds<=0:
        raise ValueError("positive concurrency and timeout required")
    if identity is None:
        identity=EngineIdentity(**load_json(worker.parent/"build-identity.json"))
    preset_root=repo/"core/src/main/assets/presets"
    texture_root=repo/"core/src/main/assets/textures"
    probes=make_probes(config,work/"probes")
    cues={p["id"]:describe_audio(np.fromfile(p["pcm_path"],dtype="<f4"),44100)["onsets"] for p in probes}
    lock=threading.Lock()
    state={"schema_version":1,"status":"running","requested_presets":len(records),
           "completed_presets":0,"render_jobs":0,"reused_jobs":0,"failed_jobs":0,
           "engine_identity":asdict(identity),"platform":platform.platform(),"host":platform.node(),
           "corpus_identity":corpus.identity,"presets":{}}
    write_atomic(work/"analysis-state.json",state)
    def characterize(record):
        path=preset_root/record.path
        if file_digest(path)!=record.sha256:
            raise ValueError(f"stale preset input: {record.path}")
        static=trace_dependencies(parse_preset(path))
        trajectories={}
        for probe in probes:
            job=JobSpec(record,probe["id"],Path(probe["pcm_path"]),config,identity,
                        preset_root,texture_root,work/"jobs")
            run=collect_run(worker,job,work/"render-features",cues[probe["id"]],timeout_seconds)
            trajectories[probe["id"]]=run
            with lock:
                state["reused_jobs" if run["reused"] else "render_jobs"]+=1
                state["failed_jobs"]+=run["status"]!="success"
                write_atomic(work/"analysis-state.json",state)
        result=fingerprint(record,trajectories,static)
        if result.quality["requires_extension"]:
            extended=replace(config,measurement_seconds=60)
            extended_runs={}
            for probe in make_probes(extended,work/"probes"):
                job=JobSpec(record,probe["id"],Path(probe["pcm_path"]),extended,identity,
                            preset_root,texture_root,work/"jobs")
                onsets=describe_audio(np.fromfile(probe["pcm_path"],dtype="<f4"),44100)["onsets"]
                run=collect_run(worker,job,work/"render-features",onsets,timeout_seconds)
                extended_runs[probe["id"]]=run
                with lock:
                    state["reused_jobs" if run["reused"] else "render_jobs"]+=1
                    state["failed_jobs"]+=run["status"]!="success"
                    write_atomic(work/"analysis-state.json",state)
            result=fingerprint(record,extended_runs,static)
        result=replace(result,evidence=dict(result.evidence,engine_identity=asdict(identity),
                       corpus_not_used_for_universal_rendering=True,
                       backend={key:trajectories["steady"].get("manifest",{}).get(key)
                                for key in ("gl_version","gl_renderer")},
                       preset_sha256=record.sha256))
        write_atomic(work/"fingerprints"/f"{digest(record.path)[:20]}-fingerprint.json",asdict(result))
        with lock:
            state["completed_presets"]+=1
            state["presets"][record.path]={"eligible":result.quality["eligible"],"reasons":result.quality["reasons"]}
            write_atomic(work/"analysis-state.json",state)
        return result
    try:
        if concurrency==1:
            results=[characterize(record) for record in records]
        else:
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                results=list(pool.map(characterize,records))
        state["status"]="complete_with_failures" if state["failed_jobs"] else "complete"
        write_atomic(work/"analysis-state.json",state)
        return results
    except BaseException:
        state["status"]="interrupted_or_failed"
        write_atomic(work/"analysis-state.json",state)
        raise


def run_pipeline(config: PipelineConfig, *, worker: Path | None=None) -> PipelineResult:
    from .audio import load_corpus
    from .build_worker import build_worker
    from .export import export_bundle
    from .inventory import inventory
    from .matching import match_presets
    from .report import write_report
    from .validation import validate_candidates
    import random
    repo=config.repo.resolve(); work=config.work.resolve()
    assets=repo/"core/src/main/assets"
    records,metadata=inventory(assets/"presets",assets/"presets.idx",assets/"textures")
    master=records
    if config.preset_limit is not None:
        if config.preset_limit<1: raise ValueError("positive preset limit required")
        records=list(records)
        random.Random(12345).shuffle(records)
        records=records[:config.preset_limit]
    corpus=load_corpus(config.audio_root,config.corpus_manifest,work/"audio")
    worker=worker or build_worker(repo,work/"engine")
    identity=EngineIdentity(**load_json(worker.parent/"build-identity.json"))
    fps=analyze_library(records,corpus,config.run,work/"analysis",worker,repo=repo,
                        identity=identity,concurrency=config.concurrency,timeout_seconds=config.timeout_seconds)
    profile_root=Path(__file__).parent/"profiles"
    genres=load_json(profile_root/"genres.json")
    audience=load_json(config.audience_config or profile_root/"audience-home.json")
    predictions=match_presets(fps,corpus,genres,audience)
    fps=validate_candidates(fps,predictions,corpus,repo,work/"validation",worker,identity,top_per_genre=3)
    decisions=match_presets(fps,corpus,genres,audience)
    evidence={"library_coverage":"full" if len(records)==len(master) else "partial",
              "candidate_pool":len(records),"corpus_recordings":len(corpus.tracks),
              "corpus_identity":corpus.identity,"genre_profile_sha256":digest(genres),
              "audience_profile_sha256":digest(audience),"engine_identity":asdict(identity),
              "app_patches_sha256":identity.patches_sha256,"texture_sha256":metadata["texture_sha256"],
              "excerpt_policy":"one thirty-second excerpt per recording in initial pass"}
    bundle=export_bundle(decisions,master,evidence,work/"genre-bundle")
    write_report(fps,decisions,work/"report")
    write_atomic(work/"matches.json",{"schema_version":1,"evidence":evidence,
                                     "decisions":[asdict(d) for d in decisions]})
    state=load_json(work/"analysis/analysis-state.json")
    return PipelineResult(state["render_jobs"],state["reused_jobs"],state["failed_jobs"],bundle)
