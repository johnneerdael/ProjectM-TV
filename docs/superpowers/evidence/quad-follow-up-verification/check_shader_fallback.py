"""Test real shader rejection and byte-exact fallback, plus unchanged successful diffusion."""
import json
from concurrent.futures import ThreadPoolExecutor

from measure import ROOT, RunConfig, bass_signals, run_one


def main():
    work = ROOT / "build/follow-ups/verification/shader-fallback"
    work.mkdir(parents=True, exist_ok=True)
    pcm = bass_signals(RunConfig(fps=30, warmup_seconds=4, measurement_seconds=4), work / "signals")["bass-0.30"]
    cases = (("c665", 1182, 665, False), ("q540", 960, 540, True),
             ("q768", 1024, 768, True), ("q1080", 1920, 1080, True), ("q2160", 3840, 2160, True))
    names = ("Geiss - Surface (1-02 Version).milk", "TonyMilkdrop - I Like Cartoon --- Isosceles edit.milk")
    workers = ("final", "diagnostic-on", "diffusion-safe-on", "diffusion-reject-safe-on")
    jobs = [(name, None, *case, worker, repeat, work, pcm)
            for name in names for case in cases for worker in workers for repeat in (1, 2)]
    results, pending = [], []
    for job in jobs:
        name, _, key, _, _, _, worker, repeat, *_ = job
        path = work / "jobs" / f"{name}-{key}-{worker}-r{repeat}" / "metrics.json"
        if path.exists():
            results.append(json.loads(path.read_text()))
        else:
            pending.append(job)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for row in pool.map(run_one, pending):
            results.append(row)
            (work / "raw.json").write_text(json.dumps(results, indent=2))
    (work / "raw.json").write_text(json.dumps(results, indent=2))
    indexed = {(r["name"], r["key"], r["worker"], r["repeat"]): r for r in results}
    errors = []
    for name in names:
        for key, *_ in cases:
            def digest(worker, repeat=1):
                return indexed[(name, key, worker, repeat)]["sha256_all_frames"]
            for worker in workers:
                if digest(worker, 1) != digest(worker, 2):
                    errors.append([name, key, worker, "nondeterministic"])
            if digest("final") != digest("diffusion-reject-safe-on"):
                errors.append([name, key, "fallback changed baseline pixels"])
            if digest("diagnostic-on") != digest("diffusion-safe-on"):
                errors.append([name, key, "successful diffusion changed pixels"])
    summary = {"render_jobs": len(results), "fallback_comparisons": len(names)*len(cases),
               "successful_diffusion_comparisons": len(names)*len(cases), "errors": errors}
    output = __file__.replace("check_shader_fallback.py", "results-shader-fallback.json")
    with open(output, "w") as file:
        json.dump(summary, file, indent=2)
    print(json.dumps(summary, indent=2), flush=True)
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
