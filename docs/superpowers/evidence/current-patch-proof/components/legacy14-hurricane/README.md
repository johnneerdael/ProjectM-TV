# Patch0014: unchanged Hurricane on the current14-patch GPU endpoint

![Matched upstream/current-minus0014/current library frames](comparison.png)

The preset is unchanged `Geiss - Hurricane (1-02 Version).milk`, SHA256
`e1941fe7f4a8a2112ee9faf4660289b82748019d963864be4022f5771e9eb614`.
It sets `fShader=0`, mode1 and waveform alpha0.3. Its audio equations, warp,
colors, feedback and assets are preserved.

**Visible difference:** upstream and current-minus0014 have green-tinted rotating
trails. Current0014 removes that additional hue modulation and presents cooler,
nearly neutral trails; it also restores the waveform alpha/topology behavior.
The lower panels are aligned source crops `(120,105,265,210)`, enlarged3× using
nearest sampling without changing brightness. These colors are actual rendered
RGB, not screenshot normalization or a new palette.

**Why:** `VideoEcho::Draw` previously always applied animated shade to the legacy
composite, even when authored `fShader` was zero. Patch0014 uses white modulation
at or below0.001 and mixes shade with white above that threshold. It also gives
mode1 its MilkDrop1.25 alpha multiplier before the final clamp and renders its
spiral as an open strip instead of adding a closing segment. In this original,
0.3 becomes0.375 before clamping. The screenshot demonstrates the combined patch;
it does not independently attribute every changed pixel to each of those three
operations. Separate source/GL controls remain in the
[main investigation](../../../brainstain-dark-output/README.md).

At frame119, upstream versus current-minus0014 RGB MAE is0.000321 (maximum channel
difference2); current-minus0014 versus current is9.386165 (maximum166). The very
small baseline/control difference separates other retained patch effects from
this clear single-patch change. These values describe this frame and input only.

All three roles use the synchronized main source `41ec3fc1`, identified by
[current-series.json](../../current-series.json). Upstream applies no TV patches;
the control applies all14 then removes0014; current retains all14. The engine and
evaluator pins remain unchanged. Shared deterministic hooks and explicit capture
adjustments remain: upstream admits GLES3.0, while current/control disable the
API36 program-binary export. No Windows/MilkDrop GPU frame is claimed.

Each role renders120 frames twice in fresh processes on the task-owned API36
Android TV emulator5630, M4 Pro host GPU/GLES3.0. All repeats are exact, with zero
GL errors and no shader warnings/errors. Verification reconstructs the selected
source roles, independently rebuilds/canonical-compares workers and checks all720
decoded RGB frames plus PNG/comparison payloads. See
[results](results.json), [verification](verification.json) and
[figure hashes/measurements](figure-audit.json).

This is new14-patch evidence. Earlier13-patch component captures keep their own
identities and are not relabeled; affected old witnesses still need revalidation.
Complete compressed streams and workers are retained under ignored
`build/patch-proof/legacy14-hurricane-v1` and
`build/patch-proof/current14-workers-v1`.
