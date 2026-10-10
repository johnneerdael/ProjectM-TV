# Fixed textured-material partial recheck — 2026-10-10

Frozen input: `static-behaviour-2000-2026-10-10-v2/rows.jsonl.gz`, SHA256
`1e92ca3ebded773c5f57a29983e0a61460a18e2da0de5b1f0341487a194cb867`. No source selections were changed or rerolled.
The producer consumes frozen descriptors and current unchanged original preset
hashes, without executing equations, shaders, rendered frames or audio sequences.

Producer SHA256: `3e555069eaac396adb472c1698c0e3aba27255a50f4878003b3aec53b2982e70`.

- 809 textured presets /1309 component descriptors rechecked.
- 592 presets have finite fixed-texture material partial rates;28 have positive
  rate ceilings.643 have finite two-state difference ceilings;97 have positive
  difference ceilings. Counts overlap and include zero bounds.
- No source-hash mismatches or producer failures;0 new total-rate-known records.
- Elapsed10.62s including gzip JSON traversal, source hashing and
  material calculus; this is a local probe timing, not incremental exporter cost.

Assume sampled texture RGBA fixed in[0,1] at a fixed geometry/barycentric/sample
site, asset selection, destination and other audio/state inputs. The exported
partial does not supply texture/history movement or an audio time trajectory.
Positive upper bounds do not prove an attained or visible flash.

The rate reuses existing incoming alpha*RGB calculus plus the over-blend
alpha-rate×destination ceiling1. The two-state difference uses additive incoming
difference plus clamped alpha difference for over blending. This retains the
black-texture/D1 case that cannot borrow positive untextured RGB as a lower bound.
Native endpoint-domain, modulo and blend failures remain null/explicit unknowns.

`recheck_fixed_texture.py` is the repeatable saved-descriptor probe;
`fixed-texture-recheck-rows.jsonl.gz` preserves every component/source identity and
result. `ranking.json`, `input-causes.json` and `texture-modulation.json` are the
preceding unchanged-cohort diagnostics; they are not classifications or observed
flash measurements.136 focused/neighboring production tests pass with the pinned
optional SymPy/Z3 environment, including8 new positive/negative partial controls.
