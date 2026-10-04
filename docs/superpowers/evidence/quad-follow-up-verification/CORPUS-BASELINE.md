# Shared Mac corpus baseline

This scan is owned by `/Users/jneerdael/Scripts/Projectm-TV/.worktrees/quad-lines-follow-ups`, branch `followup/quad-lines`. Keep its worker, runner and inputs unchanged while it runs. Other investigations can read completed records without waiting for the entire corpus. Do not launch another instance: the runner holds an exclusive scan lock.

The evidence directory is `build/follow-ups/corpus-baseline/` in that worktree. `progress.json` gives current coverage and process ID; `protocol.json` and `inventory.json` freeze the configuration and all 9,606 preset byte hashes. `launch.json` records the original command. A `complete_coverage: false` record is a partial scan.

## Exact comparison identity

- Protocol: `db30e933df242896ab72e5889623a1c48ca0e4ff2fd0a2ec42c9d8e2f061587f`.
- Upstream: `e0b0a967f0ffd7d332106c366668ed271718472b`, projectM 4.1.7.
- Engine patch series: 0001–0025, before the custom-warp sampler fix 0026; patch digest `839ea69b6a5b5fd94afa1b5d140c621b7af2b6dad7c53c849487d37bc4bb786d`.
- Deterministic analyzer instrumentation: `254db5d7418da6162c8db449ed400df19e9b6391ba405c0d20a0e19c3a005ef8`.
- Render: 2364×1330, line reference 1024×768, 30 fps, 4 seconds warm-up plus 4 seconds measurement, bass-0.30, seed 12345, two repeats.
- PCM SHA256: `f31d76c4a6fb286768d01c37cc6951f2e83dc46bb42b46e286bc88e808525c1b`.

This is the shipping-cap comparison baseline. Authored-fidelity comparisons still require classic GL lines at 1182×665. This scan does not cover a 16-second window or establish compatibility with the other investigation's diffusion workers. Match preset bytes, texture/PCM inputs, dimensions, engine patch identity and instrumentation before comparing results.

## Reading and verifying results

`rows/<key>.json` contains the preset SHA256, status, repeat links, metrics and thumbnails. `runs/<key>/repeat-N.json` retains every native frame SHA256 and the concatenated native RGB stream SHA256. Each repeat renders and captures all 240 frames. Successful pairs must match exactly. Failed, timed-out and nondeterministic presets remain explicit in coverage.

Only three 256×144 lossless PNG thumbnails are saved, at zero-based frames 120, 180 and 239. Full-size image bytes are not retained; rerender exact jobs for native-resolution PR images. Window RGB/luma/motion metrics use all 120 measurement thumbnails; native RGB/luma/fraction metrics use the three sampled native frames. They are screening measurements, not naked-eye fidelity verdicts. Compiler rejection can fall back silently in this worker, so GL success alone does not establish custom-shader compilation success.

Run from this worktree to validate saved row checksums, provenance, complete repeat hashes and the exact full-corpus join to source families:

```sh
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/corpus_audit.py
```

This writes `build/follow-ups/corpus-baseline/verified-family-index.json`, an advancing snapshot with matching preset/source hashes, shader groups, overlapping feature memberships, statuses and integrity issues. All 9,606 preset hashes were independently checked against the source-family inventory. Static feature membership identifies comparison groups; it does not establish a runtime defect.

## Resuming

First verify that the PID in `progress.json` is no longer running. Then use the original command from this worktree:

```sh
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/corpus_baseline.py --run --workers 3
```

The runner reuses checksum-valid records only when their preset bytes and immutable protocol match. It refuses an altered protocol or inventory. Preserve failed records for investigation; do not treat them as missing coverage or silently delete them. The audit index must be refreshed after the scan finishes before making corpus-wide claims.
