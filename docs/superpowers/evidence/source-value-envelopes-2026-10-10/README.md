# Conditional scalar value envelopes

The source model separates value support from temporal support. If the
source-time rules cannot bound a scalar control's value, `value_envelope`
reuses the bounded walker in value-only mode. Named scalar inputs are
arbitrary finite values, and their names are explicit premises. Internal
extended intervals are mathematical bounds, not supplied infinities or
zero initialization. No narrower audio/state domain is invented.

Understood trig, nested min/max clamps, comparisons/conditional unions,
square and safe arithmetic can provide finite output ranges. Missing
rate/continuity remain unknown. Known overflow domains, uninitialized/opaque
operations, random calls, effectful loops, unsupported typed casts and
unseparated denominators retain gaps. Exported ranges contain finite
endpoints only, with no expression-program execution or input/time samples.
Native numeric/appearance certification is false and remains separate.

This reuses `source_control_bounds`, not a second parser or execution engine.
The existing shader-envelope walker has a different float32/sampler/storage
contract and was deliberately not used as an EEL interval engine. The
separate scalar value mode preserves the source target/domain boundaries.

Thirteen controls cover audio/state sine, clamped inputs, branch unions,
square, safe versus singular division, zero-times-unbounded input, opaque
random/uninitialized nodes, arithmetic overflow and finite-premise exports.
Nine tests failed before implementation; the known-overflow-inside-sine
regression also failed before its guard. Producer and independent review
both passed195focused value/material/compound/appearance tests.

The unchanged100source sample gains102conditional material channels across
20presets. Supported wrap-domain results increase1122→1224, while unknown
channels decrease378→276. Newly supported channels retain unknown rates;
no temporal/Chill/Intense credit is inferred. This is conditional ingredient
coverage, not measured native appearance or mood accuracy.

The100preset operations total35.30seconds, maximum1.75seconds for one preset
on this host. Sample timings are not a corpus/hardware guarantee. All sources
and full-file hashes join the preceding material-temporal archive exactly;
ZIP CRC passes. `census.json` preserves per-preset new ranges, finite-input
premises and source/parser/model/engine identities.

Raw paired batch:
`build/preset-corpus/source-value-envelope-2026-10-10/batch-000001.zip`
SHA256 `daf7dc17c966a783f9b165440ae68c6e1cf6d7dbbdfd20c4d23779f947540fd0`.
The explicit source34adapter matches observed latest2.3.36full AAR bytes.
Published-AAR runtime qualification remains pending independently; no
native code, presets, shared corpus or device was changed or operated.

Final prepared suite: **2,530tests and92subtests pass in143.95seconds**.
Strict MkDocs and whitespace checks pass. This is a source-math checkpoint.
