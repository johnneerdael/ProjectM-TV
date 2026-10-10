# Source shader channel threshold resets

The source-only flashing model now reports nominal limiting channel jumps for a
top-level scalar select between a continuous signal and a constant reset. This
checkpoint uses no rendered frames or equation/shader execution.

## Math and references

For a signal approaching a literal threshold `t`, and a reset value `r`, the
two branch limits differ by `abs(t-r)`. The signal must pass the existing nominal
continuous calculus with every contributing input varied. A value range alone
does not establish continuity or threshold reachability. Finite arithmetic,
selected custom-stage and declared sample/input assumptions remain explicit.

Microsoft's [HLSL if reference](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-if)
defines conditional branches; its [floor reference](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-floor)
confirms that a floating-point return type can still produce integer-valued steps.
The original MilkDrop2 reference `vis_milk2/plugin.cpp` lines 3598–3670 prepares
and compiles the authored shader, rather than replacing its branch math with
equations. `milkdropfs.cpp` lines 3913–3934 binds texture/sampling inputs separately.
The local authoring guide's `5.shaders/3.built-in-textures.md` explains those
feedback inputs and sampler prefixes. This detector analyzes the translated
typed source graph under the source34 patched-engine identity; it changes no
renderer, preset or native patch.

## Fixed sample and review correction

All 100 fixed sample records retain structured descriptions and validate the
JSON Schema. Source hashes and execution-unknown inventories remain unchanged.
One preset gains six records: three default and three declared-scenario channel
resets. `Zylot - The Sound plays the Sights.milk` warp lines 245–252 reset RGB
channels above authored `.7` to zero. The nominal limiting gap is 0.699999988.
Exact preset/shader hashes and all six records are in `threshold-reset-census.json`.
Sample-driven frequency remains null; no whole-frame blackout or visible flash
is certified.

Independent review found a false-positive path: `int(sample.r*4)` and
`floor(sample.r*4)` can skip a `.7` threshold entirely. A `>=2` floor reset has
an actual source transition of 1 to 0, rather than the claimed gap of 2. Five
regression cases failed before the continuity requirement was added, and then
passed. Quantized casts, floor, raw frac, boolean and unsupported signals now
receive no limiting-jump claim. Modeling their discrete transitions is separate
work. Original-graph domain checks survive equivalent-branch normalization.

Fourteen threshold controls and 100 focused nonlinear/time/lookup controls pass.
Independent final review passes 36 focused controls including exact-profile Grind
and reports no remaining actionable finding. No traversal budgets were raised.
The full prepared analyzer suite passes 3,040 tests and 92 subtests in 176.81
seconds. Strict MkDocs and diff whitespace checks pass.

Local qualification outputs:

- `build/preset-corpus/source-threshold-resets-2026-10-10/`
- `build/preset-corpus/source-threshold-resets-export.log`
- `build/preset-corpus/source-threshold-resets-suite.log`
- `build/preset-corpus/source-threshold-resets-docs.log`

These are local source mechanisms. Threshold reachability, texture history,
affected screen area, later passes, native/storage rounding and displayed flash
timing remain separate from this conditional limiting estimate. This checkpoint
does not certify Chill/Normal/Intense labels or whole-preset appearance accuracy.
