# I24 actual per-instance control and conservative Native grouping

**Prepared source only: uncompiled, unexecuted, unaccepted.** No canonical source/patch/helper/test/build configuration, git, GPU or device was changed or operated. The initial uncompiled `i24-live-shape-thick.patch` remains intact as the simpler alternative.

## Why naive batching is incorrect

Current LineBatch stores each closed strip with its own padded previous/next points. Combining strip segment counts on that buffer introduces false connector segments. Drawing all pass0 outlines together, then all pass1 outlines, changes alpha order when differently coloured/alpha outlines overlap. Moving later fills ahead of earlier outlines can also change appearance. Neither shortcut is an acceptable thickness fix.

The refined `i24-grouped-live-shape-thick.patch` first captures evaluated finite int-nonzero thick per instance, preserving static GetBool positive-only defaults and reset-before-evaluation. Fractional±.5 remain thin;±1/2 are thick. No assignment retains each instance's saved flag. Out-of-int-range/nonfinite flag conversion remains outside qualification; no invented sanitization is added.

## Bounded safe grouping

Group only contiguous instances that are all thick, untextured, have an active border, have exact zero emitted center/edge fill alpha and finite position/colour inputs, and use the same blend destination. Require pairwise disjoint conservatively expanded AABBs; stop at the first incompatible/overlapping instance. Limit groups to16. Thin, opaque/textured, missing-border, different-blend and overlapping cases keep their per-instance order/calls.

The shader permits miter length below1/.49; bounds include a3× half-width/AA envelope, pass offsets and pixel/tie margin. Bounds include fill geometry too. Thus the limited fill/border reordering and pass-major grouping are admitted only where different instances have disjoint raster support. Native backend raster/precision validation is still required; the source envelope is not a measured cross-GPU bound.

Pack each actual disconnected segment's four previous/A/B/next ColoredPoints. Preserve each instance's float RGBA, including distinct alpha, and keep the existing line shader unchanged. Append only confirmed group data to the existing line VBO after its unchanged padded-point prefix. Existing individual strips continue to use their original offsets; grouped strips use96-byte segment stride and the same existing attributes/program.

No new shader or persistent GPU buffer is introduced. No-group callers keep their original one-call upload path. Grouped uploads use one orphan plus two subdata calls, adding2 calls compared with the old one-call upload. The common DrawPasses routine preserves current I23 widths, pass offsets/order, tie bias and alpha; it does not restore original1-pixel offsets. Fill calls remain, including transparent fills. Geometry/equations are prepared once and both target draws retain each instance's flag.

## Independent exact49 source trace

`original49-finite-trace.json` derives each city-lights instance from the original shape source at frozen q2=q3=0,q32=1. It is source arithmetic, not an original Windows execution. Original milkdropfs.cpp2454 chooses4/1 passes from evaluated thick; its instance loader resets thick from saved thickOutline before every instance. The current instance loader still resets thick, so the fix must retain each evaluated flag rather than read only the final context.

City-lights shape0 has49 instances and static thick0. Equation sides becomes4. Instances0–44 remain thin with fill alpha1. Instances45–48 use thick1, zero fill alpha and separated centers(.25,.75),(.75,.25),(.75,.75),(.25,.25). Border alpha remains floating.2.

| Work per target | Baseline | Simple proposal | Grouped proposal |
|---|---:|---:|---:|
| Filled calls | 49 | 49 | 49 |
| Authored outline calls | 49 | 61 | 61 |
| Native outline calls | 49 | 61 | 49 |
| Native segment instances | 196 | 244 | 244 |

The four final outlines form16 segments. Four grouped Native passes replace16 per-outline calls; preceding45 thin calls remain. City group suffix is16×96=1536 bytes. These are source operation counts, not cost measurements. Root must test actual grouping at real sizes/styles and inspect resolved per-instance properties.

## Actual-production CGL controls

`shape_thick_grouped_controls.cpp` uses the existing CGL harness, real PresetFileParser/CustomShape/GeometryTargets and observational array/instanced draw hooks. `shape_attribute_probe.hpp` reuses the actual mapped-attribute reader prepared for the colour owner packet, without editing that helper.

It constructs three independent outlines, executes their actual frame code and captures actual positions, RGB/alpha, pass offsets, target bindings and counts. Cases cover alternating styles; all thick;±1/±.5; static1→equation0; no assignment; negative saved file flag remaining false; zero border; overlapping or opaque cases rejecting grouping; authored-only and prepared Native replay over two frames.

Assertions match each colour-labelled instance separately, current I23 authored offsets and Native pass_offset values. Native endpoint A/B identity and expected corners reject false connectors. Fractional per-instance alpha(.2,.3,.4) stays floating, protecting I25. Register counters require3 evaluations per frame and init once, preventing last-instance/context copying or Native reevaluation.

An optional exact `martin - city lights v2 c.milk` argument executes only its actual shape0 code at the explicitly frozen Q stage and compares all49 emitted fill centers/alphas and source counts, requiring authored61/Native49 calls and244 Native segment instances. This is a source-bound shape-stage witness, not the preset's full frame/audio/image execution.

Compile against an isolated source tree with the refined patch applied, using the same includes/macOS shim/OpenGL linkage as the existing projectm-regressions controls. Add the target only in a root-owned isolated harness; no CMake file is changed here. Target source is the new.cpp, C++17, include the current regressions directory plus patched libprojectM/MilkdropPreset/vendor/evaluator API directories, and link libprojectM::projectM/OpenGL as existing controls do.

Future invocation (not run here):

```text
shape-thick-grouped-controls ".../core/src/main/assets/presets/martin - city lights v2 c.milk"
```

Baseline should fail on live flag/style disagreements. The refined candidate must pass before any source acceptance claim. Remaining focused controls include forced batch flushes, mixed/textured/missing borders, unusable-line Native fallback, antialias on/off and different aspects, I23 style/half-pixel/sampler controls, current mesh-cache controls and exact Native images. Existing alternate/unaffected city-lights variants remain useful source-bound witnesses.

## Runtime/resource limits and acceptance

The suffix contains only confirmed group segments and is bounded by the existing batch point cap8192. Worst-case logical segment storage is8192×96=786432 bytes of scratch plus a same-size suffix in the existing GPU allocation, in addition to existing points. Vectors retain capacity; allocator rounding/orphaned GPU residency needs measurement. New per-instance bounds/group metadata and overlap checks add CPU work. At most16 candidates are checked pairwise per admitted run; no unbounded search or concurrency is added.

The transparent/disjoint case avoids the city-lights extra Native calls but cannot guarantee lower total time or memory. Authored still gains12 loops, fallback cannot use grouped quads, and additional uploads/packing may offset savings. Preserve pressure/lifecycle/resource ownership and measure original-versus-candidate under the same frozen Native4K scene/audio/context before adopting. Do not mix these observational controls into timing.

Actual Native screenshots, repeat/source controls, memory and isolated cost remain root-owned gates. **I24 remains open; no affected census, physical-TV, whole-corpus or acceptance claim is made.**
