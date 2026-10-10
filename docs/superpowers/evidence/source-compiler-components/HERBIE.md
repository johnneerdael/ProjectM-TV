# Herbie: actual source-export acceptance, separate adaptation proposals

Date: 2026-10-10. Herbie2.3 checkout
`b1cc14c9ff243cc154131512a8c9ee42ccf3eccc` consumes the existing precision
exporter's FPCore files directly. It requires no new expression parser or changes
to Python source. This test produces separately labelled adaptation/generation
proposals; none is applied to authored prediction or the engine.

## Runtime and reproducibility

An official Minimal Racket9.3 ARM64 tarball is unpacked under
`/Users/jneerdael/Scripts/source-analysis-evaluation/racket`. Its SHA256 matches
the published checksum:
`93c498c54804945c53412395e9ec7b33c56834f541710c2b3e161182be0c2670`.
Packages are installed with `--scope installation` into this isolated runtime.
No shell profile, global environment or system package installation is changed.
The pinned clone's egg backend builds with `cargo build --release --locked`;
Herbie's standard backend is used. Optional egglog is not enabled.

Racket plus resolved packages occupy about693MiB, and the egg build115MiB.
Herbie's declared dependencies include documentation/GUI packages transitively;
the command-line experiment opens no GUI. Installed package checksums/source
snapshots, executable/library/Cargo-lock hashes and exact commands are retained
in [results](herbie/results.json) and [package inventory](herbie/packages.txt).

The first three requests fail during MPFR FFI initialization because installation
with `--no-setup` has not yet installed its supplied foreign libraries. Keep these
[initial failures](herbie/initialization-failures.json). Official
`raco setup --no-user --only-foreign-libs --pkgs math-aarch64-macosx` installs
the supplied MPFR/GMP libraries into the isolated runtime; compiling the two
local Herbie packages removes the approximately30-second source startup cost.
A direct `math/bigfloat` check then succeeds. The same fixed inputs are retried
after this specific environment correction.

## Fixed requests and outcomes

All use seed12345, one iteration, 128 training/256 test points, a20-second
Herbie deadline, 20,000 enodes and a60-second outer wall deadline.

| Input | Exact source/model | CLI outcome and proposal | Wall time |
|---|---|---|---:|
| `precision-consumed-0.fpcore` | Acid Mandala v4d consumed warp control; squared bass/mid/treb sum multiplied by `.0175`, declared common binary32 and band domains `[0,2]` | Exit0; sorts operands using min/max and proposes nested FMA operations |1.466s |
| `precision-consumed-1.fpcore` | placebo heal drift… consumed warp control; bass/mid/treb sum multiplied by `.1`, same declared common format/domains | Exit0; proposes sorted min/max and FMA, **with an unsound-egraph warning** |1.608s |
| Cancellation control | Declared binary32 `(1+x)-x`, `x` in `[1,16777216]` | Exit0; proposes constant `1.0` |1.352s |

Total measured CLI time is4.425s after setup. Inputs, proposals and exact
preset/typed-graph/domain joins are saved beside the result. The two actual
FPCore strings match their saved precision-export records exactly. The model is
the explicitly declared common binary32 expression model; it does not certify
the actual mixed-format native pipeline.

Herbie's official documentation identifies an unsound-egraph warning as a
failure in its algebraic rewrite phase, indicating a tool bug. Preserve the
warning and proposal as an unverified, quarantined outcome; do not remove the
case, change the seed to obtain a cleaner result or count it as a verified
improvement. No proposal here has an independent numerical certificate.
[Herbie warning documentation](https://herbie.uwplse.org/doc/latest/faq.html#unsound-egraph).

The cancellation control explains why this component belongs in a separate
adaptation/generation mode: at binary32 `x=16777216`, the original ordered
expression rounds to0, while the proposed constant is1. Changing authored
arithmetic would therefore change its specified finite-format result. The
source proposals also introduce FMA and different association/selection
operations; they cannot be silently substituted into authored analysis.

The useful acceptance is **three preserved proposal outputs from an existing
standard interface**, with one explicit library warning. This establishes
neither whole-domain error improvement nor native appearance/performance gain.
New predictor bounds and changed predictions remain zero. Future generated
effects can separately evaluate proposals with format/domain proofs, supported
operations and explicit discontinuity/rounding checks.

## Reproduction

Use explicit runtime paths; no PATH change is required:

```sh
racket/bin/raco pkg install --scope installation --auto --no-setup --name egg-herbie herbie/egg-herbie
racket/bin/raco pkg install --scope installation --auto --no-setup --name herbie herbie/src
racket/bin/raco setup --no-user --only-foreign-libs --pkgs math-aarch64-macosx
racket/bin/raco setup --no-user --no-docs --jobs 2 --pkgs herbie egg-herbie
racket/bin/racket -l herbie -- improve --seed 12345 --timeout 20 --num-iters 1 --num-points 128/256 --num-enodes 20000 INPUT.fpcore PROPOSAL.fpcore
```

Run from the external evaluation directory after the checksum-verified runtime
download and pinned egg build. Package inventory snapshots are essential because
some upstream package URLs resolve a current release; retain the recorded hashes.
The bounded outer subprocess command appears in the result record.

Official sources: [Racket9.3 installers/checksums](https://download.racket-lang.org/releases/9.3/),
[pinned Herbie source](https://github.com/herbie-fp/herbie/tree/b1cc14c9ff243cc154131512a8c9ee42ccf3eccc),
[FPCore specification](https://fpbench.org/spec/fpcore-1.2.html).

## DXC disposition

DXC's documented command-line route targets Shader Model6.0 and above. It is
not treated as a legacy native translator or target-equivalence oracle.
The exact fixed50 GLSL sections already have complete existing typed lowering,
exact GLES300 ASTs and the qualified auxiliary Naga bridge; this checkpoint
identifies no remaining frontend calculation that an additional DXC adapter
would recover. Defer DXC until a named modern-HLSL/DXIL/SPIR-V consumer or missing
frontend case exists, rather than installing a duplicate route without measured
contribution. No DXC build/acceptance claim is made.
[Official DXC features/goals](https://github.com/microsoft/DirectXShaderCompiler#features-and-goals).
