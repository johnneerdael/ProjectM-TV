import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .inventory import inventory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="preset-lab", allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("inventory", help="Identify presets, weights and textures")
    for name in ("presets", "textures", "index"):
        command.add_argument(f"--{name}", type=Path, required=True)
    command = commands.add_parser("doctor", help="Build and verify deterministic native rendering")
    command.add_argument("--repo", type=Path, default=Path.cwd())
    command.add_argument("--work", type=Path, default=Path("build/preset-lab"))
    command.add_argument("--worker", type=Path)
    command = commands.add_parser("corpus", help="Decode music samples and measure audio descriptors")
    command.add_argument("--audio", type=Path, required=True)
    command.add_argument("--work", type=Path, default=Path("build/preset-lab/audio"))
    command.add_argument("--manifest", type=Path)
    command = commands.add_parser("trace", help="Trace static audio dependencies in one preset")
    command.add_argument("preset", type=Path)
    command = commands.add_parser("match", help="Automatically rank cached fingerprints without rendering")
    command.add_argument("--fingerprints", type=Path, required=True)
    music = command.add_mutually_exclusive_group(required=True)
    music.add_argument("--corpus", type=Path)
    music.add_argument("--audio", type=Path)
    command.add_argument("--work", type=Path, default=Path("build/preset-lab/audio"))
    command.add_argument("--genre-config", type=Path, default=Path(__file__).parent / "profiles/genres.json")
    command.add_argument("--audience-config", type=Path, default=Path(__file__).parent / "profiles/audience-home.json")
    command.add_argument("--overrides", type=Path)
    command = commands.add_parser("analyze", help="Automatically measure new/changed presets and reuse cached runs")
    command.add_argument("--repo",type=Path,default=Path.cwd())
    command.add_argument("--work",type=Path,default=Path("build/preset-lab/analysis"))
    command.add_argument("--limit",type=int)
    command.add_argument("--preset",action="append",default=[])
    command.add_argument("--worker",type=Path)
    command.add_argument("--concurrency",type=int,default=1)
    command = commands.add_parser("bass-screen", help="Rank bass-caused pixel change and screen area using the native engine")
    command.add_argument("--repo", type=Path, default=Path.cwd())
    command.add_argument("--work", type=Path, default=Path("build/preset-lab/bass-screen"))
    command.add_argument("--worker", type=Path)
    command.add_argument("--preset", action="append", default=[])
    command.add_argument("--priority", action="append", default=[])
    command = commands.add_parser("bass-select", help="Export a requested-size Dance collection from cached screen measurements")
    command.add_argument("--repo", type=Path, default=Path.cwd())
    command.add_argument("--measurements", type=Path, required=True)
    command.add_argument("--count", type=int, default=500)
    command.add_argument("--worker", type=Path)
    command.add_argument("--destination", type=Path, default=Path("build/preset-lab/dance-selection"))
    command.add_argument("--import", dest="import_to_app", action="store_true")
    command.add_argument("--dance-only", action="store_true", help="Publish only Dance; leave other experimental categories unavailable")
    command=commands.add_parser("run",help="Automatically analyze, match, music-test and export genre collections")
    command.add_argument("--repo",type=Path,default=Path.cwd())
    command.add_argument("--audio",type=Path,required=True)
    command.add_argument("--work",type=Path,default=Path("build/preset-lab/run"))
    command.add_argument("--audience-config",type=Path)
    command.add_argument("--limit",type=int)
    command.add_argument("--worker",type=Path)
    command.add_argument("--concurrency",type=int,default=1)
    args = parser.parse_args(argv)
    try:
        if args.command == "bass-select":
            from .dance_selection import export_dance_selection, current_experiment, matches_experiment
            from .export import import_bundle
            from .identity import load_json
            repo = args.repo.resolve()
            records, metadata = inventory(repo/"core/src/main/assets/presets",repo/"core/src/main/assets/presets.idx",
                                          repo/"core/src/main/assets/textures")
            measurements = [load_json(p) for p in sorted(args.measurements.glob('*.json'))]
            state_path = args.measurements.parent/'ranking.json'
            state = load_json(state_path) if state_path.exists() else {}
            experiment = current_experiment(repo, args.measurements.resolve(), state, args.worker)
            compatible = [r for r in measurements if matches_experiment(r, experiment)]
            known_records = {record.path:asdict(record) for record in records}
            covered = {r.get('preset', {}).get('path') for r in compatible
                       if r.get('preset') == known_records.get(r.get('preset', {}).get('path'))}
            evidence = {'measurement_method':'bass-screen-v1', 'measured_presets':len(measurements),
                        'scan_status':state.get('status','unknown'),
                        'requested_presets':state.get('requested_presets'),
                        'unknown_presets':state.get('unknown_presets'),
                        'library_coverage':'full' if covered == {r.path for r in records} else 'partial'}
            bundle = export_dance_selection(measurements, records, repo/'core/src/main/assets/preset-genres',
                                            args.destination, evidence, args.count, experiment=experiment,
                                            preserve_other_categories=not args.dance_only)
            result = import_bundle(bundle,repo) if args.import_to_app else bundle
            json.dump({'count':args.count,'destination':str(result),'scan_status':evidence['scan_status'],
                       'render_jobs':0},sys.stdout)
            sys.stdout.write("\n")
            return 0
        if args.command == "bass-screen":
            from .bass_screen import scan_bass_screen
            from .build_worker import build_worker
            from .identity import load_json
            from .models import EngineIdentity
            repo = args.repo.resolve()
            records, metadata = inventory(repo/"core/src/main/assets/presets", repo/"core/src/main/assets/presets.idx",
                                          repo/"core/src/main/assets/textures")
            requested = set(args.preset) | set(args.priority)
            missing = requested - {r.path for r in records}
            if missing:
                raise ValueError(f"unknown presets: {sorted(missing)}")
            if args.preset:
                records = [r for r in records if r.path in set(args.preset)]
            priority = {name: i for i, name in enumerate(args.priority)}
            records.sort(key=lambda r: (priority.get(r.path, len(priority)), r.path))
            worker = (args.worker or build_worker(repo, args.work / "engine")).resolve()
            identity = EngineIdentity(**load_json(worker.parent / "build-identity.json"))
            report = scan_bass_screen(records, repo, args.work, worker, identity)
            json.dump({k:v for k,v in report.items() if k not in ('ranking','unknown')}, sys.stdout, allow_nan=False)
            sys.stdout.write("\n")
            return 0 if not report['unknown_presets'] else 1
        if args.command=="run":
            from .models import PipelineConfig
            from .pipeline import run_pipeline
            result=run_pipeline(PipelineConfig(args.repo,args.audio,args.work,args.audience_config,
                                               concurrency=args.concurrency,preset_limit=args.limit),worker=args.worker)
            json.dump(dict(asdict(result),export_path=str(result.export_path)),sys.stdout,allow_nan=False)
            sys.stdout.write("\n")
            return 1 if result.failed_jobs else 0
        if args.command == "analyze":
            from .build_worker import build_worker
            from .identity import load_json
            from .models import Corpus,EngineIdentity,RunConfig
            from .pipeline import analyze_library
            import random
            repo=args.repo.resolve()
            records,metadata=inventory(repo/"core/src/main/assets/presets",repo/"core/src/main/assets/presets.idx",
                                       repo/"core/src/main/assets/textures")
            total=len(records)
            if args.preset:
                wanted=set(args.preset)
                missing=wanted-{r.path for r in records}
                if missing: raise ValueError(f"unknown presets: {sorted(missing)}")
                records=[r for r in records if r.path in wanted]
            elif args.limit is not None:
                if args.limit<1: raise ValueError("preset limit must be positive")
                random.Random(12345).shuffle(records)
                records=records[:args.limit]
            worker=args.worker or build_worker(repo,args.work/"engine")
            identity=EngineIdentity(**load_json(worker.parent/"build-identity.json"))
            fps=analyze_library(records,Corpus((),{},"universal"),RunConfig(),args.work,worker,
                               repo=repo,identity=identity,concurrency=args.concurrency)
            state=load_json(args.work/"analysis-state.json")
            json.dump({"schema_version":1,"library_total":total,"analyzed_presets":len(fps),
                       "coverage":"full" if len(records)==total else "partial",
                       "render_jobs":state["render_jobs"],"reused_jobs":state["reused_jobs"],
                       "failed_jobs":state["failed_jobs"],"fingerprint_directory":str(args.work/"fingerprints")},
                      sys.stdout,allow_nan=False)
            sys.stdout.write("\n")
            return 1 if state["failed_jobs"] else 0
        if args.command == "match":
            from .identity import load_json
            from .matching import load_cached_corpus, load_fingerprints, match_presets
            if args.corpus:
                corpus = load_cached_corpus(args.corpus)
            else:
                from .audio import load_corpus
                corpus = load_corpus(args.audio, None, args.work)
            decisions = match_presets(load_fingerprints(args.fingerprints), corpus,
                                      load_json(args.genre_config), load_json(args.audience_config),
                                      load_json(args.overrides) if args.overrides else None)
            json.dump({"schema_version": 1, "corpus_identity": corpus.identity, "render_jobs": 0,
                       "decisions": [asdict(decision) for decision in decisions]},
                      sys.stdout, ensure_ascii=False, allow_nan=False)
            sys.stdout.write("\n")
            return 0
        if args.command == "trace":
            from .preset_parser import parse_preset
            from .dependencies import trace_dependencies
            evidence = trace_dependencies(parse_preset(args.preset))
            json.dump(dict(asdict(evidence), schema_version=1), sys.stdout,
                      ensure_ascii=False, allow_nan=False)
            sys.stdout.write("\n")
            return 0
        if args.command == "corpus":
            from .audio import load_corpus
            corpus = load_corpus(args.audio, args.manifest, args.work)
            records = [dict(asdict(track), path=str(track.path)) for track in corpus.tracks]
            json.dump({"identity": corpus.identity, "tracks": records, "descriptors": corpus.descriptors},
                      sys.stdout, ensure_ascii=False, allow_nan=False)
            sys.stdout.write("\n")
            return 0
        if args.command == "doctor":
            from .doctor import doctor
            report = doctor(args.repo.resolve(), args.work.resolve(), args.worker)
            json.dump(report, sys.stdout, ensure_ascii=False, allow_nan=False)
            sys.stdout.write("\n")
            return 0 if report["healthy"] else 1
        records, metadata = inventory(args.presets, args.index, args.textures)
        json.dump({"presets": [asdict(record) for record in records], "metadata": metadata},
                  sys.stdout, ensure_ascii=False, allow_nan=False)
        sys.stdout.write("\n")
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
