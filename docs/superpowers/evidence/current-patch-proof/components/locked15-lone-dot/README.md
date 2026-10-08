# Locked15 lone-dot preset and rejection evidence

![Upstream rejection and our library](upstream-current.png)

The unchanged witness is **Stahlregen – funky Blur (lotus mix) the genius in me
lies right at the heart of the flacc**. Its per-pixel zoom code contains
`zoom=zoom+.10*sin(rad+.+15.15);`. Upstream rejects the lone dot at L9 C23 and
exits1 in both runs ([actual log](upstream/0/render.log),
[execution receipt](upstream/0/execution.json)). The left tile is an explicit rejection panel; no upstream
framebuffer is claimed.

The tolerant loader without0003 omits that equation. Current0003 accepts the dot
as zero and applies the authored zoom, changing the petal curves. The
[three-role comparison](comparison.png) keeps that omission control visible.
All120 frames differ between the successful roles; each role repeats exactly.

Fresh source120547f3 uses all15 locked patches. The owned GPU TV emulator5630
renders512×288 at seed12345/frame30 with frozen PCM. Both successful roles have
zero GL-error frames. The verifier checks the failed upstream execution receipts,
jobs, logs and artifact hashes, plus full source/canonical-binary/input/pixel
checks for the successful roles. [Results](results.json),
[verification](verification.json) and [figure audit](figure-audit.json) retain
these identities. The [complete evaluator control](../locked15-evaluator/README.md)
separately verifies thread-state and lone-dot semantics.

Full streams, uploaded inputs and retained binaries remain in ignored
build/patch-proof/locked15-lone-dot-rejection-v2. The exploratory shorter Lotus
mix capture at locked15-lone-dot-rejection-v1 loaded in all three roles and is
not credited as a rejection witness. Earlier13-patch receipts/images remain
preserved; they are not relabeled as current certification.
