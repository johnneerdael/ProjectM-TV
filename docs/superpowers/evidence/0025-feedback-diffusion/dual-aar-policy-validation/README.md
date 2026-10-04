# Dual core policy verification

Exact implementation source: `d5787390c3b6cfec875fa0caede9352a3c6bf0a0`, including main parser/random-texture fixes plus diffusion0038 and cappedopt-out0039. Later cca93566 changes documentation only.

A fresh source export applied and reversed all39 patches. Both Native and capped release AARs build forARMv7/ARM64; Native appdebug builds. JNI cap/disabled-diffusion compiler flags and packagedJava policy constants are verified forbothABIs. Native and capped JVM suites pass20 tests each. DefaultmacOSBash runner passes generalJNI engine, bothpolicy sizing/presentation/fallback checks and10 realCGL regressions. GLEStransitionoverlay is skipped onmacOS because EGL/GLES development files are unavailable.

The initial scopedexport omitted a tracked auxiliary JSONheader used by tests. Restoring exact same-commit tools/preset-lab sources fixed the export; no productioninclude changed. Source identities retain this distinction.

These builds and component checks verify policy implementation; no newTV FPS, fullfidelity or size-noise acceptance is claimed. Historical0e3 renderer measurements have separate source identities.
