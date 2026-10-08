# I19 — Waveform sample counts: tradeoff investigation

Candidate patch0017 reproduces the source cap within the TV reference policy. Source-count regression fails before (160 versus85 at width256) and39 normal renderer controls pass after. Actual Native 4K before/expected captures, measured performance and final disposition remain pending.

MilkDrop2 `milkdropfs.cpp:3008–3011,3113–3121` caps raw mode4 points at `min(480, canvasWidth/3)` and raw mode6/7 points at `min(240, canvasWidth/3)`. Current projectM instead divides the raw sample budget by three when that budget exceeds the width limit. Width256 therefore gives160 rather than85 for mode4 and80 rather than85 for modes6/7. Width1024 gives160 rather than341 for mode4; modes6/7 agree at240.

Retain `SampleDecisionWidth`, which makes sample decisions follow the TV reference-equivalent width. Replacing it with physical4K width would undo earlier sample-density/brightness fixes. With active Native Standard at3840×2160 and authored/reference1280×720, the **source-corrected rule within the TV policy** gives426 raw mode4 points rather than160. With the fallback1024×768 reference it gives394 rather than160 (equivalent width1182). Modes6/7 already agree at240 in those contexts.

This is not automatically a safe production fix: mode4 smoothing output grows from319 to851 points at the Native authored width, and Native replay submits that geometry twice. Authored momentum and audio windows change, so matching the old pixels would defeat the requested source semantics. The user guide records earlier brightness measurements on `$$$ Royal - Mashup (103)` under a160-point reference policy; those old measurements cannot certify the new426-point rule.

The handoff identifies3,643 lexical candidates. The unchanged original `$$$ Royal - Mashup (103).milk`, SHA256 `08ead3db478aa81c0e29efccc0d9c38bbe69180435123531cbafbf2beb347463`, is the primary before/expected witness because it directly overlaps the documented earlier4K brightness repair. It is not yet confirmed affected in this audit by execution or rendering.

Next: add source-count execution controls at256/1024 and both4K reference contexts; build an isolated hypothetical count correction retaining the TV rule; capture the exact original and repeats with unchanged PCM/clock/seed; measure matched Native Standard4K costs. If the extra geometry creates measurable slowdown or fidelity loss, present those captures and measurements here for owner disposition and keep the shipping rule.

The candidate leaves spectrum mode8 unchanged and uses a two-point safety minimum for tiny widths below6, outside the original’s defined line-smoothing context. Native authored and presentation sample decisions are equal at1280×720 and3840×2160 with that reference. The source regression verifies those contexts as well as the fallback reference, matched canvases and unreferenced4K.
