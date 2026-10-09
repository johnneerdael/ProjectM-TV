# Native roaming-time source formulas

The source descriptor now expands16native components behind roam_cos/sin and
slow_roam_cos/sin (_c8–_c11) into typed symbolic programs. All rates/offsets are
float32packed and each formula is.5+.5*cos(rate*t+offset) or sine. The private
t input denotes float32(renderContext.time) before the separately wrapped shader
time. No clock origin, value, reset or render context is invented.

Source31 MilkdropShader.cpp247–268 and original MilkDrop2.25c milkdropfs.cpp3975–3994
agree on functions/rates/offsets. Native/transcendental rounding, CPU contraction,
frame sampling and clock discontinuities remain excluded from nominal rates.
ShaderFields injects symbolic component fields only for float4uniforms, keeping
numeric precedence, scalarfloat lane0–3 checks and authored local shadows.
The source-only shader producer does not execute any frame or shader/image/audio.

Palette timing now identifies per-channel native_render_time_float32 versus
shader_time_wrapped clocks. Native-only phases do not receive a10000-second
shader reset claim; shader-only scope metadata remains compatible. The time-
dependency flag recognizes the native input. Periods/slopes stay unmasked nominal
formula estimates, not visible flash rates, final brightness or mood predictions.

Six new controls cover source rates/functions, long periods, clock distinction,
local shadows, complex-palette abstention and independent numerical formula
values at0,1and10001seconds. Independent review checked all16formula constants
and clock/precedence/type/shadowing guards;170focused controls pass. Full-suite
passes2293tests and92subtests in136.35seconds. Strict MkDocs and whitespace
checks pass.

Fixed100originals:100computed,15presets consume native-clock formulas in retained
programs outside the binding inventory. None gains a complete RGB palette-cycle
record: combined/nonlinear/masked programs still exceed the current single-
oscillator colour rule. No earlier descriptor was lost. This is source input
understanding, not palette/appearance accuracy or a claim that all100use the new
inputs. Exact names/source/record/model hashes and occurrence paths are in
census.json. Raw source/programs remain in the paired batch; no image labels or
rendered-reference data feed the record.

The qualified full published2.3.33AAR/source31 remains the target. No engine or
preset changes, devices or shared corpus were used. Existing47numeric export is
unchanged. Clock formulas support further static modulation understanding, but
complete palette, visible activity and independently recognizable reconstruction
remain unverified; the requested notification gate is unmet.

Raw paired batch:
`build/preset-corpus/source-native-time-2026-10-09/batch-000001.zip`

SHA256: `d05e6694b2fed8dab36af858c5d8c4463225617054f032c2220811ec9795c016`.
ZIP CRC and all100original source bytes/hash joins were verified. Mean per-preset
source export.31452839s,sum31.452839s; no performance claim is inferred.
