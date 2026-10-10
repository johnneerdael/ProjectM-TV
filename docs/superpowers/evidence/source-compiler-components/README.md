# Optional compiler components: source-bound auxiliary inventories

Date: 2026-10-10. These additions supplement the existing native reader, typed
lowering and domain calculus. The normal effect exporter does not invoke them.
No rendering, shader execution, Android dependency or device was used.

## Components and measured contribution

| Addition | Functioning interface | Qualified result | Numerical/prediction change |
|---|---|---|---|
| glslang / SPIR-V Tools / SPIRV-Cross | `source_shader_compiler.py` API/CLI | Exact GLES300 AST; labelled GLES310 OpenGL inspection; function/call/CFG/loop/conversion/sample inventories and reflection joined to original request and translated source | Zero new numerical calculations, tighter estimates or changed predictions |
| Naga | optional `--naga-worker`, pinned Rust CLI | Full typed IR, expression uniformity, function/global use and sampling pairs on an explicit Vulkan/HLSL inspection bridge | Additional compiler metadata; zero new numerical bounds or changed predictions |
| Slang | `source_shader_slang.export_derivative` and explicit CLI | Generated derivative program for exact authored `sigmoid`/`vortex` helpers in `flexi - target practice-5-liquid-2-twitch-2.milk` | Larger derivative program available; input/domain/native/clamp obligations prevent any new bounded response claim |
| Crab | `source_state_crab.infer_clamp_candidate`, C++ worker | Rational fixpoint candidate for a source-joined actual clamped state recurrence | Candidate `y0` interval `[-1/2,1/2]`; no complete source/native-state proof or changed prediction |

Herbie subsequently consumes two actual precision-export FPCore cases and a
cancellation control, producing separate adaptation proposals in4.425 seconds.
One case emits an unsound-egraph warning; retain it as unverified. No authored
arithmetic is replaced. See [Herbie acceptance and DXC disposition](HERBIE.md).

The fixed selection is the first 32 entries of the unchanged seeded 2,000
selection, SHA256 `6ef58b92fa758019c4b041ce8e498dcda81999430d5295f3c972e5f0c4342d7c`.
All 50 authored shader sections are retained; no failed section was replaced.
Exact preset/request/translation/source/compiler hashes appear in
[compiler baseline evidence](compiler-baseline-32.json) and
[compiler plus Naga evidence](compiler-naga-32.json).

The compiler view exports 257 emitted functions, 1,343 calls, two loops, 99
selection merges, five conversions, 363 samples and 368 reflected resources.
All sample and conversion sites join to actual translated source lines on these
50 sections. Selective dead-function removal and compact IDs retain 42,961
instruction records, all sample counts and all conversion counts. No blanket
inlining, aggressive dead-code pass or custom binary parser is used.

Existing `ShaderFields` also constructs complete typed graphs for all 50 exact
source34 sections: 0.389 seconds for graph lowering alone in the comparison run.
This addition supplies compiler audit structure and source/resource cross-checks;
it does not rescue a previously unsupported numerical calculation in this sample.
The compiler-only stage work costs 6.55 seconds (median 0.129, worst 0.159 seconds
per section). Its paired benchmark wall time is 21.55 seconds including native
reader processes and evidence writing. These are different workloads and must
not be presented as a speed ratio.

The final compiler plus Naga run costs 12.61 seconds wall, 12.35 seconds summed
stage work (median 0.248, worst 0.291 seconds). It includes prior-profile rejection
attempts and serialization/process startup. All 50 final Naga modules validate
with **all** validation flags; all preserve sample and conversion counts. No
native arithmetic equivalence follows from those counts.

## Profile and source boundaries

GLES300 AST input is byte-identical to the saved native translation. SPIR-V input
changes only the first version directive to GLES310 and automatically maps
inspection locations/bindings. `-g` retains source locations. The original
function summaries remain available alongside the selectively normalized ones.
Resources carry exact request sampler names/types and physically enumerated
translated declaration lines; reflected bindings remain inspection identities.

`#line` directives make the simple physical-text join unqualified. The exporter
retains compiler acceptance and raw logical source/file IDs, but attaches null
text with an explicit reason. It never labels an unrelated physical line as the
sample/conversion source. Hash/seal checks reject changed requests, sources,
engine profiles and tampered results. A seal identifies bytes, not a producer.

Naga's original GLES300 frontend rejects version300; the original OpenGL SPIR-V
frontend rejects `OriginLowerLeft`. A GLSL450/relaxed Vulkan attempt also exposes
combined-sampler limitations. The functioning auxiliary bridge uses official
SPIRV-Cross HLSL50 output and glslang's Vulkan HLSL frontend with `-Od`:

- Separate texture/sampler descriptors through SPIRV-Cross.
- Shift inspection sampler bindings by64 and uniform-block bindings by128.
- Scalarize only the generated fixed `float4` fragment-output wrapper (one or two
  elements) into the corresponding `SV_Target0/1` fields. Retain the original
  global array, authored expressions and each value copied to its original index.
- Reject other shapes, duplicate/missing assignments and dynamic/out-of-range
  array accesses. Validate the final module using SPIR-V Tools and **all** Naga
  flags. Future descriptor collisions remain validator failures.

[Original rejection evidence](naga-original-rejections.json) retains the earlier
25 resource-binding and 25 output-array location failures. Exploratory validation
without binding checks helped identify them; the shipped worker does not weaken
validation. Naga spans refer to the generated inspection module, joined through
every bridge hash, rather than pretending to be authored source offsets.

A divergent implicit texture-sample control is accepted by this Naga route.
Its typed IR retains nonuniform expressions and an Auto sample. The control
therefore verifies the boundary: validator success is insufficient to establish
defined native derivative/sampling behaviour. Native arithmetic, runtime texture
bindings and appearance remain explicitly unverified.

## Slang and Crab follow-up acceptance

Slang2026.19 compiles the exact authored `sigmoid`/`vortex` bodies after attaching
`Differentiable` attributes and adding a separate explicit differential compute
entry. The source-bound wrapper requires unique resource-free compiler function
summaries, exact authored helper substrings, a restricted compute-main entry, an
actual forward derivative invocation and a retained generated derivative function.
It rejects rewritten/unbound helpers, helper shadow declarations, comment-only
requests and derivative overrides. An independently checked dead-unused derivative
request returns unsupported. A texture differentiation control fails with Slang's
non-differentiable-call diagnostic; no `no_diff` or zero-derivative override hides it.
See [the actual vortex record](slang-vortex.json). No new nominal range bound is
established: length/normalization, clamp regions and native rounding still need
their own models and domains.

Crab checkout `b1eeb1a9402ab0664e962f26f89d923f8514284c` builds successfully. The
actual fixed sample `Martin - Pixies Party (Hakan mash-up) 6-10.milk` initializes
`y0=(rand(10)-5)*.03` and writes
`y0=max(-.5,min(.5,y0+vy0*dt));reg05=y0` in main-frame line50. The declared
nominal model now conservatively uses initialization `[-.15,.15]` and safely overapproximates the
increment as an arbitrary finite real each frame. Crab's rational interval CFG
fixpoint returns `[-.5,.5]` at the loop header and postframe; removing the clamp
returns `[-oo,+oo]`. See [widened-initialization evidence](crab-widened-initialization.json).
The [earlier candidate](crab-actual-clamp.json) used an explicitly unverified
`[-.15,.12]` caller premise; it is preserved, not treated as native rand proof.
The wider premise avoids assuming an integer-only exclusive rand range and
reproduces the same bounded/unbounded clamp controls.
These are candidates for separate initialization, full ordered phase, reset and
native-FP proofs. The wrapper explicitly leaves source-model mapping unverified.
It does not silently interpret this fragment as a proof of the complete preset.

A separate rational relational-domain probe preserves `x-y=0` as constraints,
but direct assignment to a `difference` variable still yields the independent
interval `[-1,1]`. The integer-oriented octagon instantiation does not support
the chosen rational arithmetic without changing domain configuration. Those
failures are retained under the external evaluation directory; no relational
numerical improvement is claimed or promoted from them.

## Reproduction and validation

Install official glslang, SPIR-V Tools and SPIRV-Cross CLIs for the optional
exporter. The normal analyzer requirements remain sufficient without these tools.

```sh
python tools/milk-analyzer/source_shader_compiler.py SAVED-COMPATIBILITY.json --output OUT
cargo build --locked --release --manifest-path tools/milk-analyzer/compiler_components/naga/Cargo.toml
python tools/milk-analyzer/source_shader_compiler.py SAVED-COMPATIBILITY.json --output OUT --naga-worker tools/milk-analyzer/compiler_components/naga/target/release/source-shader-naga-worker
python tools/milk-analyzer/source_shader_compiler_validate.py build/preset-corpus/source-shape-flash-size-2000-2026-10-10 --limit 32 --output OUT
```

The canonical Naga Cargo manifest builds its pinned git revision; Cargo.lock
locks transitive packages. The verified build used an external `--target-dir`.
Build the Crab worker against the pinned checkout's configured headers and
`libCrab`, linking GMP/GMPXX; the verified macOS compiler command used C++14.
The wrapper receives its worker path explicitly, as does Slang's CLI/API.

Focused controls run with explicitly configured optional binaries:

```sh
SOURCE_SHADER_NAGA_WORKER=PATH-TO-NAGA-WORKER SOURCE_SHADER_SLANG_COMPILER=PATH-TO-SLANGC SOURCE_STATE_CRAB_WORKER=PATH-TO-CRAB-WORKER build/preset-lab-venv/bin/python -m pytest tools/milk-analyzer/test_source_shader_compiler.py tools/milk-analyzer/test_source_shader_naga.py tools/milk-analyzer/test_source_shader_slang.py tools/milk-analyzer/test_source_state_crab.py -q
```

**31 pass**, including actual compiler calls, canonical pinned Naga build,
source/hash/profile mutation, compiler crash/timeout, numeric conversion,
samples/loops/functions, source directives, output-wrapper negatives, actual
vortex derivatives and actual clamp/removal candidates. Optional workers are
explicitly skipped when unconfigured. Whole-analyzer checks and integration
remain recorded by the parent component-adoption task.

Official API references: [SPIR-V Tools](https://github.com/KhronosGroup/SPIRV-Tools),
[SPIRV-Cross](https://github.com/KhronosGroup/SPIRV-Cross),
[Naga pinned source](https://github.com/gfx-rs/wgpu/tree/14dd4e8f717cd8c4381908895495ea19ef924c35/naga),
[Slang automatic differentiation](https://shader-slang.org/slang/user-guide/autodiff.html),
[Crab pinned source](https://github.com/seahorn/crab/tree/b1eeb1a9402ab0664e962f26f89d923f8514284c).
