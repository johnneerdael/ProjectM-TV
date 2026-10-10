# glsl-transformer: pinned source-only component validation

Date: 2026-10-10. This is an executed Java component experiment against the saved
fixed 32 / 50-section shader cohort, plus 22 positive/negative controls. It changes
no predictor code or classifications and runs no renderer, images or shader frames.
The production recommendation is to independently reproduce selected functionality
in the existing Python typed graph. The Java experiment remains an external
reference for behaviour and counterexamples.

## Result

The component builds and works. Its indexed AST and structural wildcard matcher
recover five explicit folded-coordinate expressions in three unchanged native
GLES300 translations. One section supplies a new structural candidate relative
to the frozen existing family output: `flexi - grind my glitch up [231].milk`.
That saved result has no Cartesian mirror family and five fold reports abstaining
on `fold scalar projection budget exceeded`. The AST finds three repeated
triangular-fold expressions directly, without expanding their large input programs.

This is a useful bounded route for source structure recovery. It has produced
**zero new numerical bounds and zero changed production predictions**. The AST
candidate still needs exact live-output/coordinate joins, types, finite-domain and
native interpolation/storage guards before contributing quantitative movement or
prominence. A repeated fold construction does not establish visible copies,
flashing, contrast or an activity band.

## Smallest useful functionality port

Implement an analysis-local operator/type index and a bounded structural matcher
with opaque captures over the existing `shader_fields.Field` graph. Apply it first
to `source_folded_sampling.folded_coordinate_map`: identify the outer fold before
recursively projecting the entire captured phase into scalar lanes. This directly
targets the measured projection-budget failure. Capturing a phase node does not
qualify that phase's derivative, finite range or visible contribution.

The code already has DAG-aware walks and memoized dependencies, component
projection and literals in `effect_families._CACHE`. Reuse these caches and the
existing semantic child policy; add the missing shared query/capture capability.
No grammar, JVM, Java AST, ANTLR parser or printer is needed in the predictor.

| Portable functionality | Concrete predictor implementation | Expected value and boundary |
|---|---|---|
| Node/operator and reverse-use indexes | Visit each distinct live stage node once; index `(op,dtype)` and record parent operand slots, sample-coordinate roles and source paths. Keep an explicit completeness flag. | Reuse a bounded discovery pass across fold, trig, threshold, colour and motion queries. An incomplete index can expose candidates but cannot prove absence. |
| Structural wildcard capture without expansion | Match only the local operator skeleton. Capture `(phase_node,lane)` by reference; memoize `(node,lane,rule)` and leave the large phase program intact. Require source operand identity and typed/native numeric guards before an algebraic interpretation. | Recognize outer folds or oscillator/mask constructions inside larger programs without rebuilding unrelated phase subgraphs. This is the smallest measured coverage opportunity. |
| Qualified helper summaries, later | Summarize the native reader's existing function bodies by source hash, signature, phase/global bindings and profile. Preserve argument/result roles, conversions, writes, loops and sample resources. Match body structure independently of the helper name. | Share classification work across equivalent helpers and callers. Type resolution and side effects must remain authoritative; the experimental name-only overload graph must not be ported as a semantic resolver. |

Build the first index with the same live-output and sample-coordinate policies as
current analysis. A single index cannot silently combine traversals that differ
in clipping, discarded lanes or preserved zero products. Keep unknown branches,
loop plans, native-stage selection and visited-node budgets explicit. Invalidate
its analysis-local cache with the source/model/context identity already used by
the exporter; do not persist graph-object identities between presets.

The matcher can return a small source record containing the rule, captured typed
nodes, use path, premises and unresolved causes. Pass any successfully qualified
capture to the existing scalar range, SymPy derivative and Z3 predicate machinery.
Do not substitute a structural match for a finite-domain or rate proof. Shader
casts, EEL numeric conversions, persistent state and native producer order keep
their current semantics.

This is estimated at **one to two focused engineer-days** for the shared index,
one fold consumer, provenance/cache integration and the frozen positive/negative
controls. This is an implementation estimate, not measured work or a completion
promise. Qualified helper summaries and additional consumers are separate scope;
porting the whole Java AST transformation framework is unnecessary for the first
useful change.

### Reach beyond the tested shaders

Indexing and non-expanding capture operate on the existing typed graph, so they
can serve translated shaders and already-lowered EEL/shape/control expressions.
The algorithm does not depend on the 50 filenames or GLSL helper names. Likely
follow-on consumers are nested `frac/abs` coordinate kernels, trig phase graphs,
clamp/threshold masks and nonlinear colour-transfer expressions that repeatedly
scan the same large DAG. This expected reach is an inference from the shared IR
and current traversal/projection paths, not a new corpus measurement.

The measured gain remains **one additional structural candidate in the fixed
50-section comparison**, with zero new quantitative predictions. There is no
basis yet for extrapolating a corpus coverage percentage or an end-to-end speedup.
Functionality that the library does not provide—typed live-output influence,
interprocedural state/loop proofs, texture-history bounds and motion/prominence
math—still requires the current predictor machinery. Recognition may improve
without a preset acquiring a narrower activity interval.

### Porting and license implications

The official implementation is AGPL-3.0. Copying or adapting its Java classes,
grammar, matcher implementation or substantial source expression into Python is
covered-code reuse; changing language or removing the runtime dependency does not
by itself settle those obligations. The license's sections 4–6 set conditions for
conveying covered source/modifications and corresponding source. The repository
currently carries LGPL 2.1 text, so compatibility of a copied-code port has not been
established by this experiment. [Pinned upstream license](https://github.com/IrisShaders/glsl-transformer/blob/9d26f0f660498ed725ae2077db1c3c637c143921/LICENSE).

The proposed path is original predictor code implementing the general indexing,
opaque-capture and memoization algorithms described here, using observed behaviour
and independently authored controls as its specification. Keep source provenance
and avoid transcription of upstream code or documentation. EU case law separates
program functionality/underlying principles from protected source expression,
while also warning that reproduction of source-derived elements can infringe;
this distinction supports treating algorithm reuse and a literal source port as
different engineering choices, not declaring a proposed implementation legally
cleared. [SAS Institute v World Programming, paragraphs 31–43](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62010CJ0406).

## Build and backend identity

Pinned official shallow clone:
`https://github.com/IrisShaders/glsl-transformer`, commit
`9d26f0f660498ed725ae2077db1c3c637c143921`, version `3.0.0-pre3`.
External workspace:
`/Users/jneerdael/Scripts/source-analysis-evaluation/glsl-transformer`.

The Gradle 8.12 wrapper compiled successfully under Homebrew OpenJDK 21.0.11 with
ANTLR 4.13.1. The dependency cache is task-local. HTTPS used a copied OS-trusted
certificate store inside the external workspace; global stores were unchanged
and TLS verification remained enabled. No build failure or retry was needed.

The upstream indexed-query, matcher and transformer suites pass **31/31**.
The experiment's independent suite passes **12/12** test methods, including all
50 source round trips and 22 targeted input controls. Backend, Java, ANTLR, probe,
source and compiler hashes are stored in the evidence.

The repository declares **AGPL-3.0** and describes additional/commercial licensing
options. No library/runtime dependency was added to the predictor or Android app.
[Official licensing and usage](https://github.com/IrisShaders/glsl-transformer/blob/9d26f0f660498ed725ae2077db1c3c637c143921/README.md).

## Experiment and source preservation

Freeze the same 32 preset identities and 50 authored sections used in the existing
compiler/Naga experiment. Load their original saved native GLES300 translations
from `source-shape-flash-size-2000-2026-10-10/compatibility`; verify each translated
GLSL SHA against the previous compiler evidence before parsing. Do not rewrite
versions, bindings, numeric wrappers or native source bodies.

Use the library's node/identifier indexes to retrieve functions, calls, returns, 
loops, selections and casts. Build a conservative syntactic call graph rooted at
`main`. Exclude explicit literal-dead branches from structural candidates; mark
ambiguous overloads rather than guessing call types. Preserve generated native
zero-gated multiplication helpers and verify their scalar/vector bodies before
recognizing them as a product construction. A renamed `safe` helper with matching
bodies qualifies; a function called `mult0` that performs addition does not.

Use actual wildcard matchers and captured AST subtrees for nested
`abs(fract(input)-constant)` constructions, including the verified generated
product wrapper. Match `x-floor(x)` only when both captured operands have the same
plain-reference syntax. Instantiate a library template proposing `fract(x)` as
an inspection artifact; do not replace the production program or erase cast/native
rounding obligations. Generic body queries also recover vector trig helper
structure independently of helper names.

The preliminary `abs`/`clamp`/`fract` co-occurrence scan was discarded: it proposed
six sections, but source inspection showed unrelated expressions in four. The final
nested structural query detects five nodes across three sections and rejects
co-occurrence, integer-cast, misleading-name, dead-helper, dead-branch and overload
counterexamples. No family is inferred from an identifier or filename alone.

All **50/50** original sections parse and AST-reprint/reparse structurally.
All **50/50** originals and **50/50** reprints pass glslang 16.6.0 on their original
GLES300 profile. Calls and explicit integer/boolean constructors survive the
round trip. A `#line 123 9` control preserves the line mapping. Comments and textual
formatting are not preserved byte-for-byte.

## Measured limits and comparison

The library is a syntactic parser/transformer, not a semantic GLSL validator. Its
official documentation explicitly leaves type checking and preprocessing outside
its scope. [Official limitations](https://github.com/IrisShaders/glsl-transformer/blob/9d26f0f660498ed725ae2077db1c3c637c143921/README.md#what-glsl-transformer-is-not).

These limits were exercised rather than assumed:

| Control | Executed outcome |
|---|---|
| `int n=true` | AST accepts; glslang rejects the semantic type error. |
| `#define PHASE(x) cos(x)` | Original validates; AST reprint silently drops the definition and keeps the invocation; reprint fails glslang. |
| Unused trig helper / literal-dead call | Parsed structure retained; no live structural colour candidate. |
| `float(int(p))` | Cast remains explicit; no trig-family or fractional-part promotion. |
| Two `paint` overloads | Name-only call graph is ambiguous; no colour candidate selected. |
| Function named `hsv2rgb`, body `vec3(p)` | No colour-transformation inference from its name. |
| Loop in trig helper | Loop is preserved; no unrolling, value range or time derivative is inferred. |

The existing paired ShaderFields graph was already complete for **50/50** sections.
Existing compiler/Naga evidence already supplies typed resource, conversion and
sample structure. The AST includes all syntactic adapter overloads and dead
functions; its counts cannot replace live typed IR counts. Two of the three fold
sections already have a saved Cartesian mirror family. The third is the concrete
projection-budget candidate described above. Numeric range, output influence,
texture history and native projection remain the existing analyzer's job.

## Cost and artifacts

In one Java process, the 72-case run took **0.5225s**. For the fixed 50 sections,
parsing totalled **0.1948s**, indexed/structural queries **0.1001s**; median parsing
was **1.535ms**, with a **112.43ms** cold first parse. These numbers measure the AST
experiment, not end-to-end predictor acceleration. The earlier compiler/Naga
experiment has different subprocess/compiler/validation work and is not a fair
speedup baseline for this scan.

Full source joins, preset hashes, controls, AST summaries, paired historical fields,
compiler diagnostics and backend identity are in
[evidence](evidence/glsl-transformer-validation-2026-10-10.json.gz).
The frozen experiment sources and report are also packaged under
`~/Downloads/ProjectM-TV-glsl-transformer-validation-2026-10-10`.

Reproduce after the pinned checkout's build:

```sh
python3 /Users/jneerdael/Scripts/source-analysis-evaluation/glsl-transformer/experiment/run-experiment.py
```

The experiment source, control inputs and test suite remain external. Reproduce
the selected indexing and non-expanding match functionality over the current
typed graph, retaining exact source/profile joins and the existing math/proof
machinery for any classification credit.
