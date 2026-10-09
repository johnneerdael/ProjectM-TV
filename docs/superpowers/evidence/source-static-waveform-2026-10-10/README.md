# Static built-in waveform source constructions

source_waveform.py describes target mode selection, source form/channel roles,
controls, preprocessing and nominal geometry factors without executing any
waveform/audio/native math body. Mode conversion uses checked truncation and
signed remainder modulo16. Invalid known modes do not draw. Dynamic mode retains
unknown form and conditional control routes. Extended star/flower/lasso names
identify source bodies, not verified wholeframe silhouettes.

Two source-predictor omissions are corrected: rawmode16.9is effectivecircle0,
and authoredwave_a=0cannot exclude native mode3, which replacesalpha with a
reference coefficient*1.3*treb². Dynamic mode can reach3, so remains a candidate.
source_composition uses the sameadmission rule. Evaluatednegative nonzero dot/
additive flags are kept. Nonfinite float32control narrowing leaves derived
geometry fieldsnull without erasing other descriptor data.

Review additionally corrected unusedcontrol audio routes and a topology/renderer
conflation. Known modes suppress ignored wave_a/mystery/x/ycontrols according to
their source bodies; dynamic modes retain explicit consumption conditions. Source
strip/loop topology is separate from context-dependent GLline/quadtriangle draw
candidates. Native mode9's allocatedunassigned secondary storage remains an open
investigation: actualpathcountnull,primary-generatedpathcount1. Noenginebug is
asserted or authoredpreset changed.

References: source31Waveform.cpp90–110/246–295, WaveformMode.hpp, Factory.cpp,
mode-specific Waveforms/GenerateVertices, common WaveformMath/IIR/smoothing and
LineRenderer.cpp158. OriginalMilkDrop2legacy wave math remains a separate
reference;targetextendedmodes/reference-sized sampling and repairs are retained.
Currentfull published2.3.33AAR/source31 is still the qualifiedreference.

14newwave controls pass.242wave/family/appearance controls pass independently;
initialreview's twoP2findings are resolved and finalreview hasno remaining
findings. The complete prepared suite passes2315tests and92subtests in
139.47seconds. Strict MkDocs and whitespace checks pass. These are interpretation
checkpoints, not measured wholepresetappearance accuracy or permanent ceilings.

Finalfixed100originals:100computed,87presets have known-mode waveform recipes.
Twoearlier omitted waveform candidates are nowretained;no earlier descriptor
waslost. Exactfilenames/source/record/modelhashes, controls and correctioncases
arein census.json;fullprograms remain in the hash-boundrawbatch. Noimage/audio/
frameexecution, devices, sharedcorpus, native/presetedits or47numericchanges.
Whole-scene geometry, footprint, flashing/motion, palettes and mood/reconstruction
validation remain open work.

Raw paired batch:
`build/preset-corpus/source-static-waveform-qualified-2026-10-10/batch-000001.zip`

SHA256: `55d800a8819f426e7997c204d9d632e2cfb26aef5a5affb712571d869cbfcea3`.
ZIPCRC and all100original source bytes/hash joins verified. Mean per-preset
sourceexport.31325579s,sum31.325579s; no performance improvement is claimed.
