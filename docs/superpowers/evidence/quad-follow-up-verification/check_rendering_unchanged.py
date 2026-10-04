"""Verify diagnostic-only changes preserve classic and scaled rendering on identical frames."""
import json
from concurrent.futures import ThreadPoolExecutor

from measure import ROOT, RunConfig, bass_signals, run_one


def main():
    work = ROOT / "build/follow-ups/verification/diagnostics-rendering"
    work.mkdir(parents=True, exist_ok=True)
    pcm = bass_signals(RunConfig(fps=30, warmup_seconds=4, measurement_seconds=4), work / "signals")["bass-0.30"]
    names = ("$$$ Royal - Mashup (103).milk", "$$$ Royal - Mashup (191).milk",
             "TonyMilkdrop - I Like Cartoon --- Isosceles edit.milk", "Serge circles005b.milk")
    configurations = (("c665", 1182, 665, False), ("q1080", 1920, 1080, True),
                      ("q2160", 3840, 2160, True))
    jobs = [(name, None, *config, worker, repeat, work, pcm)
            for name in names for config in configurations
            for worker in ("final", "diagnostics-fixed") for repeat in (1, 2)]
    results = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for row in pool.map(run_one, jobs):
            results.append(row)
            (work / "raw.json").write_text(json.dumps(results, indent=2))
    indexed = {(r["name"], r["key"], r["worker"], r["repeat"]): r for r in results}
    changed = []
    for name in names:
        for key, *_ in configurations:
            hashes = {indexed[(name, key, worker, repeat)]["sha256_all_frames"]
                      for worker in ("final", "diagnostics-fixed") for repeat in (1, 2)}
            if len(hashes) != 1:
                changed.append([name, key])
    summary = {"render_jobs": len(results), "compared_pairs": len(names)*len(configurations), "changed": changed}
    target = __file__.replace("check_rendering_unchanged.py", "results-diagnostics-rendering.json")
    with open(target, "w") as file:
        json.dump(summary, file, indent=2)
    print(json.dumps(summary, indent=2), flush=True)
    if changed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
