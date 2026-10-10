# Custom-shape vertex motion bounds

The source-only `vertex_motion` descriptor combines authored centre paths with
radius and rotation curves. For fixed viewport/aspect and constant effective
sides, native polygon vertices obey
`P=(2*x-1,1-2*y)+r*(aspectY*cos(theta),sin(theta))`.
Radial and angular derivatives are orthogonal before aspect scaling; since
`0<aspectY<=1`, a conservative continuous nominal NDC speed bound is
`2*centre_speed + hypot(max_abs_dr_dt,max_abs_r*max_abs_dang_dt)`.
Individual derivative maxima need not coincide, so the total is an upper bound.

Source references:
- Patched source34 `src/libprojectM/MilkdropPreset/CustomShape.cpp`, lines230–259.
- Original MilkDrop2.25c `vis_milk2/milkdropfs.cpp`, lines2401–2402,
  under `/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/`.

No native implementation was copied or changed. Derivation controls include
independently differentiated breathing/rotating vertices, centre projection,
negative radius, finite linear-radius speed with static angle and unresolved
rotating linear radius. Audio/state/nonlinear controls and changing sides keep
combined speed unknown. Known invalid native float32 conversions are rejected,
including projected centre overflow, collapsed radius with infinite angle and
zero-frequency trigonometric formulas that become invalid constants.

Twenty-four test-first controls pass; independent review passed 186 focused
motion/appearance tests and checked four further direct degenerate controls.
The conversion regressions were observed failing before fixes. Fixed aspect
is an explicit prerequisite rather than an assumption about changing viewport.
The prepared full suite and strict MkDocs results are recorded below.

The fixed 100 original presets all exported without equation/shader execution
or frame inspection. Twenty-nine shapes across 18 presets have a complete
nominal speed bound; five presets have a nonzero bound. Unknown paths stay
unknown, including 85 shape centres and 68 radius derivative cases. These are
coverage counts, not mood/appearance accuracy. `census.json` records the exact
per-preset results, parser/model hashes, ZIP identity and unchanged source joins.

The bound excludes floating-point/trig error, discrete frames, clipping,
rasterization, material/texture changes, later composite and feedback. It holds
only while source intermediates and native conversions are finite. It neither
certifies smooth visible motion nor authorizes Chill eligibility.

Raw paired batch:
`build/preset-corpus/source-vertex-motion-final-2026-10-10/batch-000001.zip`.
Source34 matches the latest v2.3.35 AAR bytes by whole-AAR identity; runtime
qualification remains pending independently. No shared device or corpus run
was operated, and authored presets are unchanged.

Final raw ZIP SHA256:
`0c0231b01e1cb9bda3fcec13bb0691678e91ec076fc4d429ec4d30a4b2cc58ce`.
ZIP CRC and all 100 full-file source hashes match the preceding trajectory batch.

Final verification: **2,454 tests and 92 subtests passed in 141.89 seconds**.
Strict MkDocs and whitespace checks pass. These are source-math regression
checks, not whole-preset mood or visual accuracy measurements.
