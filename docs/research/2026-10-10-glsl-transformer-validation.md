# glsl-transformer: pinned source-only component validation

Date: 2026-10-10. This is an executed Java component experiment against the saved
fixed 32 / 50-section shader cohort, plus 22 positive/negative controls. It changes
no predictor code or classifications and runs no renderer, images or shader frames.

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

The upstream indexed-query,matcher and transformer suites pass **31/31**.
The experiment's independent suite passes **12/12** test methods,including all
50 source round trips and 22 targeted input controls. Backend,Java,ANTLR,probe,
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
`abs(fract(input)-constant)` constructions,including the verified generated
product wrapper. Match `x-floor(x)` only when both captured operands have the same
plain-reference syntax. Instantiate a library template proposing `fract(x)` as
an inspection artifact; do not replace the production program or erase cast/native
rounding obligations. Generic body queries also recover vector trig helper
structure independently of helper names.

The preliminary `abs`/`clamp`/`fract` co-occurrence scan was discarded: it proposed
six sections, but source inspection showed unrelated expressions in four. The final
nested structural query detects five nodes across three sections and rejects
co-occurrence,integer-cast,misleading-name,dead-helper,dead-branch and overload
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
Existing compiler/Naga evidence already supplies typed resource,conversion and
sample structure. The AST includes all syntactic adapter overloads and dead
functions; its counts cannot replace live typed IR counts. Two of the three fold
sections already have a saved Cartesian mirror family. The third is the concrete
projection-budget candidate described above. Numeric range, output influence,
texture history and native projection remain the existing analyzer's job.

## Cost and artifacts

In one Java process, the 72-case run took **0.5225s**. For the fixed 50 sections,
parsing totalled **0.1948s**,indexed/structural queries **0.1001s**; median parsing
was **1.535ms**,with a **112.43ms** cold first parse. These numbers measure the AST
experiment,not end-to-end predictor acceleration. The earlier compiler/Naga
experiment has different subprocess/compiler/validation work and is not a fair
speedup baseline for this scan.

Full source joins,preset hashes,controls,AST summaries,paired historical fields,
compiler diagnostics and backend identity are in
[evidence](evidence/glsl-transformer-validation-2026-10-10.json.gz).
The frozen experiment sources and report are also packaged under
`~/Downloads/ProjectM-TV-glsl-transformer-validation-2026-10-10`.

Reproduce after the pinned checkout's build:

```sh
python3 /Users/jneerdael/Scripts/source-analysis-evaluation/glsl-transformer/experiment/run-experiment.py
```

The experiment source,control inputs and test suite remain external. Use this
backend as a candidate structure/index provider with exact source/profile joins;
retain the current typed math/proof machinery for any actual classification credit.
