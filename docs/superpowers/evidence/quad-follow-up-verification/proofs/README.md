# Per-fix image proof

All charts and log images use Matplotlib. The Geiss image is a lossless export of actual recorded engine RGB output; no generative images were used.

Do not publish the isolated `venv/`, `.matplotlib/` cache or compiled allocation binaries as review attachments. The PNG/SVG files, manifest, raw excerpts, source copies and scripts are the review package.

## Images

### 01-diagnostic-preserved

Artifacts: `01-diagnostic-preserved.png`, `01-diagnostic-preserved.svg`

Proves: The RED assertion reports std::exception; the GREEN standard-handler assertion succeeds for the artificial owned message.

Limits:

- The string is artificial unit-test input, not a captured GPU driver diagnostic.
- GREEN log records assertion success, not a printed what() string.
- Historical unit logs contain no immutable build identity; current test source is provided and hashed separately.

Sources (full hashes and line ranges are in `manifest.json`):

- `build/follow-ups/shader-message-red.log` — SHA256 `86a78dd73bfe55d9142aa6e7fd5b8cf52f3c889ff855d0c863ea6f262ed260b7` — lines [(196, 203)]
- `build/follow-ups/shader-message-green.log` — SHA256 `a022b8e4f387f84ade11c8d958a3579c7618b308283ad62976d82c376284a776` — lines [(142, 145)]
- `third_party/projectm/tests/libprojectM/ShaderExceptionTest.cpp` — SHA256 `1162bd8182ee9923cf37f1ba6929ca2cf9af83a0c82b501137e19f4a3a8d9e03` — lines [(1, 17)]

### 02-vertex-shader-lifetime

Artifacts: `02-vertex-shader-lifetime.png`, `02-vertex-shader-lifetime.svg`

Proves: The pre-fix driver retains 1 shader after one fragment rejection and 16 after 16 repeated attempts; fixed driver retains zero at both measured endpoints.

Limits:

- Fresh CGL reproduction, not the unsaved original session transcript.
- Chart contains only two observed endpoints per build; it claims no intermediate trajectory, RSS size, or field failure rate.
- Copied fixture omits the separately-tested what() comparison and adds explicit endpoint printing; copied-source hashes and commands are recorded.
- Desktop macOS CGL driver; no Android GPU resource measurement.

Sources (full hashes and line ranges are in `manifest.json`):

- `build/follow-ups/proof-export/allocation/red/run.log` — SHA256 `3a7075e5afff33df1b31433e00ad53fce06d3e8d3f6a2dc381d1e902e09c9d66` — lines [(18, 18), (176, 176)]
- `build/follow-ups/proof-export/allocation/green/run.log` — SHA256 `bfa1e9a0ef7557dbafadea10e78bb45dc90647c5ca24819f0e2fd05c58093c98` — lines [(11, 11), (18, 18)]

Recorded build identities:

```json
[
  {
    "state": "red",
    "identity": {
      "commit": "e0b0a967f0ffd7d332106c366668ed271718472b",
      "patches_sha256": "c0ab5e137bfe151bd5da8e5b07befe5ccd844792194c6a72da849a6adcd5df16",
      "instrumentation_sha256": "5bc595dcca2b85a705ad491f8b2636c03968960ade5adea4a253abf79857b93e"
    },
    "snapshot": "build/follow-ups/lab-final/engines/9733b1ea4f38ade6c71fc6bfdcce317965b47883f2decbc8f4082c602dca1aea"
  },
  {
    "state": "green",
    "identity": {
      "commit": "e0b0a967f0ffd7d332106c366668ed271718472b",
      "patches_sha256": "839ea69b6a5b5fd94afa1b5d140c621b7af2b6dad7c53c849487d37bc4bb786d",
      "instrumentation_sha256": "5bc595dcca2b85a705ad491f8b2636c03968960ade5adea4a253abf79857b93e"
    },
    "snapshot": "build/follow-ups/lab-diagnostics-fixed/engines/8ca3d2d6929298e2614f58573e9a0006f6e37cfa93ebd0439207cd788d3d1297"
  }
]
```

### 03-optional-shader-fallback

Artifacts: `03-optional-shader-fallback.png`, `03-optional-shader-fallback.svg`, `03-fallback-geiss-frame-239.png`

Proves: The rejected-shader pre-fix worker failed before emitting any frame. The fallback worker emitted 240 frames and matches the baseline all-frame hash in this recorded case.

Limits:

- Shader rejection is deliberately injected by a test-only invalid fragment token; not an observed retail-driver incompatibility.
- The failed worker emitted zero frames; no before-rendered image exists or was fabricated.
- Displayed frame is engine frame 239 from a recorded classic-size case; it demonstrates successful fallback rather than visual diffusion quality.
- Recorded artifacts identify a research diffusion PoC build; these are not screenshots of the final APK.
- Image proof is one Geiss case; separate matrix summary records the broader byte-parity checks.

Sources (full hashes and line ranges are in `manifest.json`):

- `build/follow-ups/verification/shader-reject-red/jobs/Geiss - Surface (1-02 Version).milk-c665-diffusion-reject-r1/worker/run-en_sw9nr/stderr.log` — SHA256 `cc8cdec44631c2084745bd6c933304fe9e9ca7c045089b25b1c677650ee35c9e` — lines [(1, 1)]
- `build/follow-ups/verification/shader-reject-red/jobs/Geiss - Surface (1-02 Version).milk-c665-diffusion-reject-r1/worker/run-en_sw9nr/manifest.json` — SHA256 `a5d15db2be16a650bf43ddc36ffa85697f3131874cd01d04325f5611186ba6ad`
- `build/follow-ups/verification/shader-reject-red/jobs/Geiss - Surface (1-02 Version).milk-c665-diffusion-reject-r1/worker/run-en_sw9nr/job.json` — SHA256 `aec339bb4fd20b869b65f2d1913bfebaed472f78106d59a6429bffefbf7b2b6d`
- `build/follow-ups/shader-reject-red.log` — SHA256 `9bdf7d942a824b2b396764752f0d9f37316e87e3f13820032665b274bc386b39` — lines [(1, 7)]
- `build/follow-ups/verification/shader-fallback/jobs/Geiss - Surface (1-02 Version).milk-c665-diffusion-reject-safe-on-r1/worker/run-kz2hc_17/manifest.json` — SHA256 `996c499b8ad7cd0cb7dc8025a2974a4a15b837062fe2de4656955a3d3cbcf620`
- `build/follow-ups/verification/shader-fallback/jobs/Geiss - Surface (1-02 Version).milk-c665-diffusion-reject-safe-on-r1/worker/run-kz2hc_17/job.json` — SHA256 `41e0fa6c6ee79f373820d7239b301328dc7ef68409905360b459d0edf03e9400`
- `build/follow-ups/verification/shader-fallback/jobs/Geiss - Surface (1-02 Version).milk-c665-diffusion-reject-safe-on-r1/metrics.json` — SHA256 `40d935cb44ed0712c208902860dc2e05c5713d1db135b278be8c447373222772`
- `build/follow-ups/verification/shader-fallback/jobs/Geiss - Surface (1-02 Version).milk-c665-final-r1/metrics.json` — SHA256 `4020e188e71bedb4d0fd8bc83db3c9481734af1b1d854766d48dda09fe42e65b`
- `docs/superpowers/evidence/quad-follow-up-verification/results-shader-fallback.json` — SHA256 `98b874d9ab8add8c1c68b7cb030a3f5d2eda98e7cb6228cafc9fcc15418db2e0`
- `build/follow-ups/verification/shader-fallback/jobs/Geiss - Surface (1-02 Version).milk-c665-diffusion-reject-safe-on-r1/five.npz` — SHA256 `3656423f8290d90ab6700a776208f055c6098dbf02e57a6300fc79f72f169b97`
- `build/follow-ups/verification/shader-fallback/jobs/Geiss - Surface (1-02 Version).milk-c665-final-r1/five.npz` — SHA256 `3656423f8290d90ab6700a776208f055c6098dbf02e57a6300fc79f72f169b97`

Recorded build identities:

```json
[
  {
    "state": "rejected-before-fallback",
    "identity": {
      "commit": "e0b0a967f0ffd7d332106c366668ed271718472b",
      "instrumentation_sha256": "5bc595dcca2b85a705ad491f8b2636c03968960ade5adea4a253abf79857b93e",
      "patches_sha256": "a34f537973f4d8f4a12383e9cdf5dedc28824c58b5dce01d73674c8df53b7bf5"
    }
  },
  {
    "state": "fallback",
    "identity": {
      "commit": "e0b0a967f0ffd7d332106c366668ed271718472b",
      "patches_sha256": "fbf8855469a52aae89e26a6c7c2ff336deaedb00eb82ba21e98bdde01be54370",
      "instrumentation_sha256": "5bc595dcca2b85a705ad491f8b2636c03968960ade5adea4a253abf79857b93e"
    }
  },
  {
    "state": "baseline",
    "identity": {
      "commit": "e0b0a967f0ffd7d332106c366668ed271718472b",
      "patches_sha256": "c0ab5e137bfe151bd5da8e5b07befe5ccd844792194c6a72da849a6adcd5df16",
      "instrumentation_sha256": "5bc595dcca2b85a705ad491f8b2636c03968960ade5adea4a253abf79857b93e"
    }
  }
]
```

### 04-deterministic-transition-test

Artifacts: `04-deterministic-transition-test.png`, `04-deterministic-transition-test.svg`

Proves: Recorded old harness failed its width assertion; deterministic CPU/low-CPU inputs exercise the real policy and the full subsequent harness passes.

Limits:

- Test-only fix: no claim that production engine policy changed.
- CPU percentages and frame rates in the deterministic control are consequences of supplied synthetic timings, not benchmark measurements.
- One observed flaky failure and one passing full run do not measure statistical flake rate.
- Historical native logs do not carry immutable build identities; current test source is hashed separately.
- Concurrent-load observation is a point-in-time worker inventory, not a continuous utilization trace.

Sources (full hashes and line ranges are in `manifest.json`):

- `build/follow-ups/native-shader-failure.log` — SHA256 `aad6a044adc1243c6b06704a8b71f114173cc60b38c7e6201ab2cb501a0358a6` — lines [(365, 366), (446, 447)]
- `build/follow-ups/native-deterministic-policy-green.log` — SHA256 `4beb046fe5eb7abaffa02178fda3e1606a67726752b599f0bdd3a485e6eea6af` — lines [(365, 385), (415, 415), (416, 425)]
- `build/follow-ups/native-deterministic-policy-positive.log` — SHA256 `4fdb06fc6cbe83ced83ef1b78625483eb9a5079106a97804efbb8392c437e433` — lines [(1, 5), (27, 27)]
- `build/follow-ups/native-deterministic-policy-negative.log` — SHA256 `a469a0d3bfdcbb5ae1d3d8560cf7ca077cb4ab0b73cb4930014e7a0b2c019aac` — lines [(1, 4)]
- `build/follow-ups/native-deterministic-policy-concurrent-load.json` — SHA256 `a5158cc87b1b07bf1adf992a28208b8e69744cab365f51b521022f915e758b2d`
- `core/src/test/native/engine_test.cpp` — SHA256 `5ef0e8cbf8fc0b1866132dfaf415561bb261de30929a8438396232b99fd093a7` — lines [(575, 611)]

## Reproduction

Run from the workspace root:

```sh
python3 build/follow-ups/proof-export/reproduce_allocations.py
build/follow-ups/proof-export/venv/bin/python build/follow-ups/proof-export/export_proof.py
```

`allocation-builds.json` records exact compile/run commands and hashes for the fresh real CGL RED/GREEN runs. Both builds use copied source from the immutable engine snapshot identified by the corresponding worker configuration. Endpoint output is printed by the copied production fixture after querying real GL objects. The separately-tested `what()` comparison is omitted in this copied allocation fixture so diagnostic behavior does not contaminate allocation isolation.

The standalone native focused controls and complete host harness are pre-existing recorded evidence. Their exact full-run command was:

```sh
JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home bash core/src/test/native/run_native_tests.sh > build/follow-ups/native-deterministic-policy-green.log 2>&1
```

For the Geiss frame, the native size and measurement snapshot size are both 1182 × 665. Array index 4 is engine frame 239 (zero-based): 120 warm-up frames and 120 measurement frames at 30 FPS. Exported RGB bytes match the last measurement-frame SHA256 and the baseline snapshot exactly. Both complete 240-frame recordings also share the same all-frame SHA256. The unsuccessful RED worker has `observed_frames: 0`; its panel intentionally contains only the actual log evidence.

## Proof gaps

- Original allocation RED console output was not saved; proof uses explicitly-labeled fresh snapshot reruns.
- No before-rendered frame exists for failed shader loading (zero frames emitted).
- No historical immutable build ID is embedded in diagnostic unit logs or native host logs.
- No retail-device screenshot or quantitative field/performance claim is established by these host/research artifacts.
