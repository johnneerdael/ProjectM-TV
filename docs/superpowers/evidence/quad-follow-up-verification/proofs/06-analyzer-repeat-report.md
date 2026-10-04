# Echasketch repeat determinism

Exact preset: `A Remixed Digital Echasketch  Again 2 martin - no religion  + disco Fruits Machine + Raron + mstress + 8.milk`.

The nondeterminism is in the analyzer's use of process-global C rand. Seed initialization covers floatRand, but the observed call sequence has untracked consumption between engine calls. A private shader RNG removes the drift. No production engine patch is warranted by these results.

## Evidence

- Source SHA256: `c4175d09cdc563337287a1bef32d5cbebf301acbecbf03b1c3a649fb70bb721f`.
- Original 8-second PCM SHA256: `f31d76c4a6fb286768d01c37cc6951f2e83dc46bb42b46e286bc88e808525c1b`. Short tests use its byte-exact first 2 seconds; full tests use the original file directly.
- Original samplers worker SHA256: `c3c05bb6fe168e596dc9113a4912532eb6a6bd7cb9b9df8990c0ec9c0cb2df53`.
- Portable private-RNG worker SHA256: `31d63a05e8e1ce2d035851c5f5f843e4bdfcb9bd93f4a137e7d2c150f8334b99`.
- All audio bands in each repeated pair are byte-identical. Full band trace SHA256: `65c86adf788d9cb5fb5683f842fd3433d631b540630346bc9206a61aa4bfbee7`.
- Original c665 serial full pair: frame 0 is identical; first divergence is frame 1, MAE .000952913, 138274 changed pixels, maximum channel delta 7/255. At frame 239, MAE .023753209, 751820 changed pixels, maximum delta 216/255. Mean final-four-second luma is .106275008 versus .106377809. Small luma drift alone was not treated as degradation evidence.
- Private trace worker preserves original frame-0 hash. C-rand logs have identical first 592 values, then one repeat skips six values. Log SHA256 (only LAB_C_RAND lines joined by newline): `5abbad1d474b654e6fa685fd42d861a7f93ff0fd09627fd68b63a5b4500d875e` versus `f7c5fa606480065e55f37bb5b58359380410fe25082e1df16e794f1dfe33782a`. Frame drift follows at frame 4. The precise external consumer has not been stack-attributed.

## Private instrumentation candidate

`analyzer-private-shader-random.patch` changes analyzer hooks and source-copy instrumentation only. Park-Miller uses explicit uint64 arithmetic modulo 2147483647, resets at instrumented engine initialization, and makes shader randomness independent of unrelated libc rand calls. Zero state uses a fixed fallback seed, verified by the known-vector test. The first 1000 values match this macOS libc sequence; a portable known-vector test plus injected unrelated libc calls checks isolation and reset. This intentionally creates a new oracle on other platforms: prior Linux/Windows C-rand sequences are not claimed equivalent. Worker identity must be regenerated through normal prepare_engine/build_worker; the scratch metadata identity labels are not the canonical integration identity.

`git apply --check` passes. `build/preset-lab-venv/bin/python -m pytest build/follow-ups/echasketch-determinism/test_candidate_random.py -q`: 1 passed. The old hooks fail this test at compile time because the private API does not exist; a global-rand adapter would fail the injected-consumption assertions.

Full 240-frame pairs at 30fps and seed12345 use the original 8-second PCM. The scratch worker config expresses the same total as warmup0 + measurement8; reported luma excludes the first120 frames, giving the required 4-second warm-up and 4-second measured window. The worker only uses the sum when rendering, so this does not change engine inputs or output.

| Render | Repeated full-frame hashes | Final-four-second luma |
|---|---|---|
| classic1182x665 | all 240 exact | .10628068309541645 both |
| quad2364x1330 | all 240 exact | .12036880075091513 both |
| quad3840x2160 | all 240 exact | .12079995784387562 both |

The corrected byte-exact uncut-copy control has source hash parity and all 240 frame hashes equal to classic1182x665 private-RNG output. The q2160 output also matches all120 prior measurement frame hashes exactly. Private rand_r and portable Park-Miller workers produce identical classic full outputs. These are instrumentation controls, not proof that all production fidelity changes are complete.

## Actual image proof

`repeat-delta-proof.png` shows final-frame repeat1, repeat2, and absolute difference times4, before versus after. It was visually inspected. The old difference image shows widespread detail movement; the new difference image is entirely black. Raw selected PNGs and frame hashes are retained per run. No invented art or generated image is used.

## Invalid exploratory material

The first `uncut-short`, `square-short`, `rand-constant-short`, `no-noise-short`, `no-noise2-short`, `no-noise3-short`, `no-blur-short`, `lod-noise-short` experiments accidentally selected a different Echasketch variant with a broad glob (source hash d5f07139...). Those shader-ablation results must not be used for this exact target. They are retained only to make the mistake visible. Exact-name serial, trace, private-RNG, portable, and corrected `portable-uncut-control` evidence is valid.

## Next action

Integrate analyzer patch and test, regenerate both production-patch identities, invalidate affected caches, rerun the full33-preset sweep with repeated-frame hash validation. Keep feedback/reference-grid experiments separate and validate their images with these deterministic workers.
