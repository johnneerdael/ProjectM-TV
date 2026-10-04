# Fresh color history initialization: isolated red/green proof

Candidate integration patch: `0028-initialize-fresh-color-history.patch`. It initializes fresh color allocations and makes the existing clear helper context-safe in `src/libprojectM/Renderer/TextureAttachment.cpp`, with five real-driver regression tests and the host-suite CMake entry. `git apply --check` passes on the current pre28 engine tree. No production files or APKs were modified by this investigation.

## Proven renderer defect

In the actual frozen core baseline source:

1. Core creates projectM while its window dimensions are zero. The idle preset is initialized at 0×0.
2. `ProjectM::SetWindowSize()` stores the requested dimensions; it does not initialize or draw the existing idle image.
3. When the first requested preset loads, `MilkdropPreset::Initialize()` calls `Framebuffer::SetSize()` at the native dimensions.
4. `TextureAttachment::ReplaceTexture()` creates fresh color storage with `glTexImage2D(..., nullptr)`, without a clear. Its contents are undefined. In contrast, the pooled-texture path explicitly clears to transparent black.
5. `StartPresetTransition()` calls `DrawInitialImage()` with the idle output. The idle attachment has a default **empty Texture, ID 0**, and `CopyTexture::Draw(..., Framebuffer&, ...)` returns when `originalTexture->Empty()` is true.
6. The requested preset's first warp can therefore sample the undefined previous-frame color history. A composite/warp discard can also preserve undefined target contents. Clearing EGL framebuffer 0 beforehand does not initialize these separate internal textures.

This is a concrete initialization contract hole. The real app can take this path when its preset index becomes ready before the idle preset has rendered. Clearing fresh color attachments makes that initial history match the existing pooled contract and also protects the first idle render. Restricting the change to an empty-previous-image copy would leave the idle/other fresh color paths dependent on unspecified allocation contents.

## Real-driver proof and minimal correction

The test compiles the production `TextureAttachment.cpp` under a distinct class name. Only `glTexImage2D`'s unspecified initial storage is controlled: fresh RGBA8 storage receives a legal nonzero byte pattern (`0x7b`). All attachment construction, clear operations, state queries and framebuffer reads execute against a real CGL driver. This avoids a false pass caused by a driver that happens to return zeroed allocation memory.

RED (`red/test.log`): four expected failures, one existing-contract control passes:

- Fresh color history still contains 1024 nonzero bytes before any render.
- Scissor/color-mask caller state must be preserved while all color pixels initialize; history remains uninitialized on baseline.
- Clearing a separate display target does not initialize later internal history.
- Pooled history is already transparent black and passes baseline.
- The recreated-context name-collision test detaches a foreign framebuffer attachment with the cached helper. Its painted sentinel storage survives, but the owner's attachment is replaced/detached, which is still a real corruption of framebuffer state.

GREEN (`green/test.log`): all five tests pass, zero skips. Read and draw framebuffer bindings, clear color, color write mask, scissor box/enabled state are preserved. The whole attachment is transparent black despite the caller's scissor/mask. The pooled contract remains unchanged. The change calls the clear helper only in the new **COLOR** allocation branch and uses a local scratch framebuffer for fresh/pooled allocation-time clears; depth/stencil paths are unchanged. Existing resize blits still copy old content over the initialized target.

The focused cache review has its own preserved red evidence in `cached-helper-red.log`: the initial fresh-clear-only candidate passes four history/state checks but fails the context-collision test. After a first real CGL context warms the helper's framebuffer, a new context deliberately allocates a foreign live framebuffer with the same numeric name and a painted sentinel attachment. Calling fresh/pooled clear then detaches that attachment with the cache. Replacing the cache with one locally generated framebuffer per clear, and deleting it only after restoring previous bindings, preserves the foreign attachment and pixels. No platform context-identity API or private GL interface is needed.

Full integration proof: `host-suite/source` is a fresh pinned upstream/evaluator archive plus patches 1–27 and the final28 patch. `host-suite/suite.log` reports **174 tests passed from21 suites, zero skips**. The build is isolated and uninstrumented apart from the existing host GLES discard shim; the production sources and live baseline remain unchanged.

The frozen baseline renderer source matches the current pre28 source byte-for-byte, SHA256 `afe6b090986845377ec66b0b7ce4beb7d7c91b6d556d85bf727d77eed7c702ae`.

## Actual core outlier: do not claim a hardware fix yet

The original apparent full-versus-selected capture failure is not systematic. Re-reading completed v4 pilot records shows:

- Baseline FULL1 key `38d01dc240c4b4e081f04cd4296c63836b3da45497361f3eed5862b1a8c40b6d`, stream `9a587191e66064810b3a2644f64848dcdedc6900c7a177ba992492f8db3da277`, differs from baseline FULL2 in **all 480 frames, including frame 0**.
- Baseline FULL2 key `0a8aad9d4e88d9f5b5c3783de02d77833bd581488bb09aac55984f0344d5952f`, stream `04a41b5f11f1114a2e54b2989626577ca5538137a2ea66b6173b6c686e81ce95`, matches all 16 selected captures.
- Both candidate FULL repetitions have that same `04a41b5f...` stream and match all 16 selected captures.

Thus the first baseline FULL run is an initialization/startup outlier, not evidence that later full readback cadence changes the trajectory. Frame0 divergence precedes any difference in prior capture cadence or the blank detector's delayed collection. The undefined-history hole is a valid candidate mechanism; it has **not** been proven to be the sole cause of that particular Mali run. Root must rebuild the actual candidate core and repeat strict hardware/emulator pilots before attributing outlier resolution to 28. The original failed baseline must remain preserved and quarantined, not relabeled as a passing baseline.

## Eliminated paths and narrow remaining diagnostics

Read-only inspection confirms core audio feeding consumes the queued 1470-byte input block on each frame; core FPS updates use the instrumented logical `NowSeconds`; CPU-time sampling affects transitions only, which are inactive. The frozen evaluator uses fixed `PRESET_LAB_SEED` and thread-local MT state. The prewarmer creates an EGL context but no engine until a queued request; the logical memory-pressure pause blocks requests throughout the 16 s pilot.

An additional passive observer exists: `setBlankDetection(false)` gates reactions, but core still calls `detector.Update()` and arms it at load. It issues async PBO readbacks/fences and collects on GPU completion. This should be audited in later capture-mode diagnostics if needed, but it cannot account for a FULL1-versus-FULL2 difference already present at frame 0.

Smallest next actual-core diagnostic is a private rebuilt candidate with defined fresh color history, unchanged seed/clock/preset/audio and strict full/selected/repeat hashes. Add selected captures at frames0/1 as initialization proof. A before-first-warp history read can establish whether storage is black, but note that the read itself synchronizes GPU initialization; the poisoned-storage regression is the non-accidental renderer proof. Do not loosen hash gates.

The inherited thread-local helper framebuffer cache is removed in the final28 candidate because the deterministic collision test proves it unsafe across recreated contexts. A local `glGenFramebuffers`/`glDeleteFramebuffers` pair runs only when a texture allocation/reuse is cleared, not per rendered frame. No startup-performance figures are claimed.

## Reproduce

```sh
build/preset-lab-venv/bin/python build/follow-ups/core-initial-history-review/build.py red
build/preset-lab-venv/bin/python build/follow-ups/core-initial-history-review/build.py green
build/preset-lab-venv/bin/python build/follow-ups/core-initial-history-review/full_suite.py
```

RED exits 1 with four assertion failures; GREEN exits 0 with five passed tests; the full suite exits0 with174 passed tests. Build logs and full test logs are preserved in `red/`, `green/` and `host-suite/`. `candidate.patch` is the local minimal code diff; the numbered integration patch uses engine-root paths and includes durable tests/CMake. Earlier fresh-only proposal artifacts and the cached-helper red log are retained for provenance.

No device operations, live runner edits, worker API changes, production writes, commits, pushes or removals occurred.
