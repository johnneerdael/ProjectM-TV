# Native 4K development ledger

## 2026-10-04: continue on the corrected renderer

The full corpus is ongoing, not a prerequisite for implementation or targeted
validation. Its last inspected progress had 3,894 successful repeated presets
and 40 explicit failures (3,934 terminal rows). Partial coverage supports
bounded estimates; it does not establish complete absence of regressions.

PR #23 is merged as `0625587f12b9cd38c852e2517eb109b027fd6526`.
This branch incorporates its sampler-binding, diagnostic, fresh-history,
framebuffer-ownership and per-frame parsing fixes. Diffusion moves from
historical patch 0025 to **0030**, after the new 0025–0029 prerequisites.
The duplicate shader-compilation cleanup hunk is removed because main now
provides it. The CMake test-list hunk is adapted to retain all new main tests.
The diffusion implementation itself is unchanged in this port.

Fresh isolated sources apply all thirty patches. Host and JVM validation are
running under `build/native-4k-current-main/`; results remain pending.
The original exact recovery hash remains historical evidence for recovery
commit `cc3ca34`, not the identity of the new thirty-patch series.

Ruling: use corrected main as the immediate 4K comparator — explicit sampler
settings and initialized feedback history affect the same recurrence being
compensated. Comparing only to the older corpus would conflate those fixes
with diffusion. Cost if wrong: targeted measurement attribution would be
incorrect; keep baseline29, candidate30 and old corpus identities separate.

Next work proceeds without waiting for corpus completion:

1. Complete host/JVM checks and publish the integration checkpoint.
2. Build matched actual-core baseline29/candidate30 workers and perform targeted
   1330/2160 comparisons, including known regressions and representative
   unaffected shaders, with exact repeats and stage diagnostics.
3. Examine brightness, colour, motion and feedback detail independently.
   Root-cause remaining regressions against the corrected sampler path.
4. Use the existing corpus's family/source evidence to choose broader samples
   and reuse compatible baseline measurements where input signatures agree.
5. Extend shader-failure/off-path/resize verification and app documentation;
   keep 1330 as the default while evidence for Native matures.

Do not install on the corpus owner's active emulator or alter that worktree.
Use isolated local measurement resources or the already approved physical TV.
Commit/push code checkpoints and preserve ignored measurement data separately.
