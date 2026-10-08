# I05 — Per-pixel inverse aspect

Candidate0021 changes only per-pixel aspectx/aspecty assignments to the existing inverse factors, matching MilkDrop2 `milkdropfs.cpp:655–656` and current main-frame inputs. Keep TV shader-canvas pixels, mesh, Q/state inputs and geometry unchanged. No new operation count, vertex, pass, texture or evaluation is introduced.

The real evaluator context test fails baseline inverse-factor assignment and passes after at landscape, portrait, square and Native4K reference contexts. It executes dx=aspecty/10 and dy=aspectx/10, checks main-frame agreement and preserves1280×720 shader-canvas inputs. All45 normal controls pass;21 patches apply.

Handoff248 lexical candidates remain unconfirmed. Exact original163.milk is the primary runtime witness: its per-pixel terms directly consume pixelsx*aspectx and pixelsy*aspecty. Preserve its init RNG and original bytes; Native4K before/expected captures and timings remain pending. Do not infer Windows pixel identity from source factor agreement.

## Corrected original4K comparison

The first controller’s shared-package before/after rows were invalid: installing both APKs before rendering left only the second artifact installed. No comparison conclusion is taken from those rows. A new controller now installs the selected role immediately before every run, checks the captured-user package and exact installed base.apk SHA256, then preserves all strict runtime checks. Four verified480-frame original runs complete with Native Standard1280×720 canvas and exact selected RGB repeats.

![Verified original before, Native4K](verified-before-4k-frame479.png)

![Verified source-corrected original, Native4K](verified-after-4k-frame479.png)

The source correction visibly changes the admitted original; numerical extent and run timings are in the verified records. Timing variability is substantial; no universal or physical-TV speed claim follows. A separate finite diagnostic overlay is running with unique before/after package IDs. Final acceptance/integration remains pending.
