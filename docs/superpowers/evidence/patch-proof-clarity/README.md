# Readable, isolated patch comparisons

The catalog now leads with matched close-ups of unchanged real presets for
0021, 0023, 0028, 0030, 0032 and 0033. The existing upstream-master comparisons
remain available below them. Their full-series brightness differences were
poor evidence for an individual repair.

The new pairs hold every other repair constant. They use native 3840×2160
final output on Apple M4 Pro, OpenGL 4.1/Metal, a 1280×720 Native Standard
line/shader reference, antialiasing enabled, feedback detail 0, mesh48×32,
seed12345, frozen float32 mono PCM and time=(frame+1)/30. Both independent
runs of each role have identical selected RGB hashes and no reported GL errors.
Crop images reserve their 16:9 source aspect ratio before lazy loading; without that intrinsic height, offscreen positioned images could remain blank. Browser checks confirm visible dots and outline differences at desktop and390px mobile width. The selected-frame observer restores the caller's read framebuffer, read
buffer and pack alignment after reading the explicit RGBA8 output attachment.

These are instrumented source workers, not shipping binaries, Windows
reference screenshots or physical-TV performance measurements. The unchanged
[I31 cost experiment](../i31-benefit/README.md) remains the gamma repair's
performance evidence; this task does not rerun that benchmark.

## What to look for

| Patch | Real preset | Visible criterion |
|---|---|---|
|0021|Flexi - crush ice38; Carnival|Feedback strands and colour phase using the original equation inputs; no overall brightness ranking|
|0023|Geiss - Mega Swirl2(2)|A denser central curl from the restored oscillator direction, with the same authored warp strength|
|0028|Dbleja - Escape (Red Mix)|Matching crossed bands rather than a side pinched into a diagonal|
|0030|phat + EoS - … nebula3|Preserved authored dots beside removed extra interpolated dots|
|0032|martin - city lights v2(1)|The restored thick outline is plainly visible at a corner|
|0033|Seizure Salad|Beat-gated vectors use the latest completed distortion; the changed injection develops through feedback|

Full-frame PNGs are unchanged lossless final captures. Crop PNGs contain the exact unresized pixels from the documented rectangle. Browser close-ups are exact lossless crops with identical rectangles and
nearest-pixel display. They load the small crop first, with the full 4K frame
available on click, avoiding decoding every full frame just to display a detail. Labels and explanations sit outside the
pixels. Full frames remain clickable. Captions identify the original filenames,
frame indices, crop sizes and coordinates. No exposure or colour adjustment is
used to make the patched role appear more favourable.

Original MilkDrop2 `milkdropfs.cpp` SHA256:
`68749d31bb6b3020ca89b1e7630fd704e58a5de8dd6275c9f5ea005c6586a7d9`.
Its aspect inputs (655–656), wave-point snapshot order (2613–2624), physical
oscillator Y (1882–1898), dot-only smoothing exclusion (2722–2726) and evaluated
shape thickness (2454) supply the source contracts. The screenshots expose their
effects; they do not establish that every corrected frame is aesthetically
preferable.

## Source isolation and custody

The full source is the frozen 34-patch catalog checkpoint from app source
`8a15996e8510533113a44e26feaddc3a7d6e85f5`, engine6f648074/evaluator22fb0cfd.
Its inventory must equal the independently reconstructed published catalog
inventory before private copies are built. Neither that cache nor production
patch bytes are modified.

0021, 0028, 0030, 0032 and 0033 are exact patch reversals in private copies.
For0023, subsequent packed-motion shader selection overlaps the old patch
hunk. Removing only the `PROJECTM_LEGACY_WARP` define selects the unchanged
uncorrected four-oscillator branch while retaining later capability guards.
That is a behavioural ablation, not an exact textual reversal of0023.
Patch-created `.orig` backups are recorded, byte-identical to their full-source
files and never compiled.

`workers.json` records actual worker/harness hashes, full source inventories,
configure commands and source deltas. `source-deltas/` preserves the changed
files on both sides, bound to those inventories; the verifier independently
reapplies each reversal (or the0023 define removal). `gallery.json` retains
both original requests and independent result records for each selected pair.
`identity.worker_ref` is a deduplicated reference to `workers.json`, replacing
the otherwise identical embedded worker identity. Original absolute paths are
historical provenance; preset/PCM verification resolves committed filenames.

## Real-preset search and limits

The bounded source search scanned all 9,606 packaged presets and evaluated six
unchanged candidates with the existing historical source29 adapter. It was
candidate discovery, not current renderer certification. See
`discovery.json` and `discovery.md` for exact identities and inputs.

Current34-patch rendering confirms real0033 effects in Slowflowers, Seizure
Salad and Harlequin, and a real0028 effect in Dbleja Escape. Slowflowers repeats
exactly across roles through frame131; the first selected divergence is132
when vectors re-enable. Its immediate line-position change is small, so the
catalog leads with the clearer Seizure Salad feedback consequence.

Traversal discovery illustrates why lexical hits alone are insufficient:
the promising Reaction Diffusion candidate uses a custom warp and has identical
selected RGB with0025 disabled. The legacy glow/neon and snakeskin examples
change, but remain weak visual illustrations under this audio/profile. They
are not presented as clear stock improvements. The synthetic traversal proof
therefore remains explicitly labelled.

No packaged preset contains the named constant tokens needed for0020. No
negative-odd echo activation was confirmed in the bounded evaluated contexts
for0022. Those diagnostic examples remain synthetic; this is not proof that
no real preset or custom pack can activate either repair. Affected-preset
counts remain unconfirmed. `search-captures.json` records all scoped rendering
attempts, including unchanged and visually weak candidates.

## Reproduce and verify

Install the existing catalog Python dependencies (Pillow/numpy) and native
SDL2/CMake/Ninja toolchain. Reconstruct the frozen catalog source cache using
its [preparation workflow](../patch-visual-catalog/README.md), then run:

```sh
python docs/superpowers/evidence/patch-proof-clarity/prepare.py --catalog CATALOG_WORK --repo REPO --work NEW_WORK
python docs/superpowers/evidence/patch-proof-clarity/capture.py --repo REPO --work NEW_WORK --name CASE --patch NUMBER --preset ORIGINAL_PRESET --selected FRAMES
python docs/superpowers/evidence/patch-proof-clarity/publish.py --repo REPO --work NEW_WORK
python docs/superpowers/evidence/patch-proof-clarity/verify.py
python docs/superpowers/evidence/patch-visual-catalog/verify_images.py --repo REPO
```

Use each retained request's original frame count and selected frames when
replaying it. Frozen PCM bytes are reused, never regenerated from a signal
formula. `prepare.py` accepts resuming completed roles, but use a fresh directory
when changing harness/source inputs; recorded workers must remain immutable.

The guide figures must match the retained generated HTML exactly. Required PR
review, CI and deployed-site verification remain separate from local artifact
checks.
