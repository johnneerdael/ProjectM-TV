# Source and build qualification

The five renderer patches are separate commits29–33 on top of the unchanged28-patch audit baseline. Current controls pass63/63 on macOS normally and under ASan/UBSan, and63/63 on Linux Mesa through both normal discovery and explicit GL_LIBS/GL_CFLAGS. The latest normal Linux run also includes the actual partial-initialization failure controls. The GCC/aarch64 sanitizer startup noise path exceeded the original30s test window; isolated unchanged deformation and seam controls pass with a150s process limit. The first whole-Linux sanitizer run is not claimed as passing. macOS standalone EGL transition coverage remains unavailable.

Wrong-production-Y and wrong-exact-axis source mutants fail the retained controls. GLES observations use the unchanged mediump production shader and an independent same-backend equation reference with a query-based arithmetic/transport budget and discriminating counterfactuals. Common-driver oscillator reproducibility is a qualification premise, not a universal CPU/GPU trig-accuracy claim. CGL retains its strict CPU/UV checks.

I16 partial-failure controls force one incomplete status from a valid real framebuffer in the actual FeedbackDetail constructor: Standard first canvas check and High native-detail check after three successful canvas checks. They check constructor unwind, deletion, retained native UV ownership, continued real producer publication and the successor's previous-completed-field consumer. They do not claim actual hardware exhaustion.

The full production CustomShape.cpp was compiled by NDK27.3 for both ARM64 and ARMv7 with O3 and fast-math stress overrides. The archived IR excerpts retain unsigned integer domain checks and saved-style fallback; the raw equation value is unchanged. Command/source/full-IR identities are recorded separately. These stress flags do not relabel the actual shipping build flags.

Fresh329 host tests,137 release JVM tests and60 capture/helper tests plus24 subtests pass. Both-ABI core-release/debug-APK build hashes are recorded separately from source-instrumented Native capture workers. Final recursive build, analyzer/docs and PR CI remain separate gates.
