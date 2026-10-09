# Reuse static shader programs

Experimental opt-in `shader_lowering_policy: cached-program-v1` reuses one
successful lowered program per stage. The default remains `per-frame-v1`.
This removes repeated static lowering; equations, inputs, loops, texture reads,
feedback, drawing and descriptors still execute for each update.

Source inspection establishes that `ShaderFields.frame` appears only in
main/blur sample-history attribution. Runtime time/audio/Q/matrix inputs remain
symbolic. The reusable program retains its compilation frame; a per-invocation
sample-detail binding rebases explicit history frames before domain/LOD checks,
observers and sampling. This also covers texture reads inside hidden loop plans
and the motion-output graph. No new native engine patch is involved.

## Cache contract

The in-memory key covers the tree, stage, effective wrap predicate, blur order,
main-sampler policy, known uniforms/components/domains, global initialization,
array initialization, language extensions and native sampler declarations.
Unsupported/nonfinite serialization contexts bypass reuse. The original wrap
predicate type is retained; NumPy booleans cannot silently gain builtin-bool
sampler-domain credit.

JSON verifies the finite supported data domain. SHA256 of standard-library
pickle serialization preserves key/value types for the process-local identity,
including integer component0 versus string"0". Those bytes are neither persisted
nor deserialized. Mapping-order changes can cause safe misses. No general
persistent object cache or new dependency is introduced.

Cached lowering snapshots literal/context data. Replacing a context with an
equal new mapping then mutating the detached original cannot alter the compiled
constant. Source/context edits invalidate the affected program. Only one entry
per stage is retained; input tensors, loop state and evaluated values are not
stored in it. Owner/model weak-reference controls verify collection.

A shared deepcopy memo preserves sampler-policy aliases across sample sites
within one stage invocation while isolating the template. Observer mutations
remain visible to sampling and other aliased sites in that invocation, then
reset for the next update. Coordinate mutability and numerical/lazy-domain
guards remain under the existing grid interpreter.

## Verification

20 focused controls cover repeated program reuse with live audio/time/UV,
main/blur history, callback edits, shared policy aliases, wrap thresholds/types,
source edits, every keyed context category, unsupported contexts, detached
literal storage, integer/string keys, owner collection, legacy default and
forecast-domain/provenance integration. Independent review found the alias,
key-type and wrap-type cases; their red reproductions and fixes are retained.

The same fixed100 exact source files from the static-review ZIP yielded
172 lowered sections,26 absent parsed trees and two retained unresolved
sections. For each successful section, five fresh-versus-reused program graphs
match after normalizing only explicit sampler-frame offsets. The graph inventory
includes hidden loop updates/conditions/effects and motion outputs. No equations,
shader numerics, textures or target compilation execute in this phase.

Measured static-lowering time: **6.45s fresh versus1.61s reused**, **4.01×**.
Parsing and graph comparison are outside that timing. A lowered section is not
evidence of native stage acceptance or appearance.

Three short authored source-forecast controls preserve feedback/display pixel
hashes and all47 feature objects exactly. Three trials each give ratios1.05×,
1.014× and0.926×; the last is a two-update480p case. These mixed whole-forecast
results do not justify enabling reuse automatically or projecting corpus gains.
A separate order-balanced60-update480p Confetti control retains identical pixel
hashes and all47 feature objects across four trials. Fresh times55.47/57.95s
versus reused56.04/58.95s give median ratio**0.986×**: no observed whole-forecast
speed gain. Lowerings drop120→2, with118 cache hits, but this source's spatial
execution/descriptors dominate cost. Keep this result rather than projecting
the4× phase improvement onto end-to-end processing. Exact domain, input hashes,
per-frame hashes and feature objects are in `forecast-long-results.json`.

Reference identity is the full published core2.3.31AAR/profile, with its matching
34-patch source adapters. These numerical comparisons execute the independent
CPU source model; they are not native AAR captures or visual accuracy tests.
No shared corpus, device, authored preset or production default is modified.

Reproduction requires prepared adapters, exact input folders and the fixed
review ZIP named in `measure.py`/`forecast_long.py`. Start a fresh process after
model edits. Local outputs: `build/preset-corpus/program-reuse/`.
