# Automated preset corpus export implementation plan

**Goal:** A single self-executable offline command analyzes every bundled `.milk`
preset with60 simulated frames at15fps/854×480, exports existing47-field source
records and writes a matched-name ZIP after each100 completed cases in Downloads.

**Architecture:** A stdlib Python controller owns discovery, a checksum-bound run
manifest, single-owner lock, bounded subprocess workers, atomic result files and
atomic batchZIPs. A worker composes the existing predictor with offline shader
compatibility, declared synthetic audio/random inputs and decoded bundled/noise
textures. No AI/API, native rendering, devices or full-corpus capture is used.

**Execution:** User supplied concrete authorized parameters and wants runnable
software, not another approval round. Use the existing isolated predictor branch.
Do not merge main, change native library/presets, operate other agents' corpus or
silently weaken math guards. Support15fps as a declared simulation context, not a
claim of identical30fps production behavior. Verify latest29source/artifact pins.

## Deliverables

- [x] Add15fps native CPU audio export with tests; preserve30/60 and coldJNI guards.
- [x] Prepare separate exact16-patch source29/adapters and verify published29AAR.
- [x] Add corpus input preparation: deterministic4-second PCM, matching15fps audio,
  exact bundled textures/noise, declared random uniforms/texture slot associations.
- [x] Add one-preset worker with stage-specific failures, bounded child processes,
  exact preset/source/model/input IDs and existing47-key record on success.
- [x] Add controller/launcher: complete corpus inventory, bounded parallelism,
  resume without rerunning terminal cases, corruption/identity drift rejection,
  process-group timeouts and CtrlC recovery.
- [x] ZIP every100completed(successor explicitfailure) with pairedoriginal.milk+
  same-stem.json, manifest/hashes; flush final/interrupt partial batch; preserve
  original names/subdirs/UTF8 and never silently overwrite a sealed archive.
- [x] Test exact100boundary, >200 cases, failures/timeouts, crashbetween ZIP and
  index update, partial final batch, resume, input drift, names/collisions and lock.
- [x] Run bounded real15fps integration cases only, never launchfullcorpus here.
- [x] Document onecommand, prerequisites/defaultpaths, timing, failures/unknowns,
  signal/context semantics, disk/memory use and recovery; updateuserguide/AGENTS.
- [x] Validate focused+preparedsuite/strictdocs; review, commit/push; provide
  runnablelauncher and smallverified smoke-test archives in Downloads.

## Output contract

Each result JSON pairs with its original relative `.milk` path and includes its
name/full-byte hash, run identity, declared60/15/854×480settings, status, stage,
elapsed time and the existing source feature record when computed. Unsupported
math/compile/resource states get explicitfailure records with no fake zero-valued
47-feature export. Every preset is accounted for; total completion and usable
records are distinct counts. The run contains sampled simulation evidence only,
not a no-flash proof, universal mood certificate or native30fps certification.

## Defaults

Use current bundled assets and latest verified source29CPU adapters; defaulttwo
workers, per-preset300second deadline, batch100, resumeenabled, deterministicseed
12345 and fixedsynthetic audio. All options recorded inimmutable runidentity.
Parallel completion determines batchmembership; result names preserveidentity.
No automatic repeat of terminal failure. Retrying after a code/contextfix uses a
new run directory so earlier archived evidence remains reviewable.

## Setup and validation

The initial self-executabler targets this Mac/Linux prepared host environment;
no shell tool silently installs an unrelatedengine. Launcher locates the task's
Python environment and source29adapters, provides actionable prerequisite errors
and supports explicit paths. Rebuild only task-owned corpusadapter directories,
never mutate frozen source-pr59binaries. Package/reference the actual script and
inputs, not a manual AI-dependent workflow.
