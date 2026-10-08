# I05 — Per-pixel inverse aspect

Candidate0021 changes only per-pixel aspectx/aspecty assignments to the existing inverse factors, matching MilkDrop2 `milkdropfs.cpp:655–656` and current main-frame inputs. Keep TV shader-canvas pixels, mesh, Q/state inputs and geometry unchanged. No new operation count, vertex, pass, texture or evaluation is introduced.

The real evaluator context test fails baseline inverse-factor assignment and passes after at landscape, portrait, square and Native4K reference contexts. It executes dx=aspecty/10 and dy=aspectx/10, checks main-frame agreement and preserves1280×720 shader-canvas inputs. All45 normal controls pass;21 patches apply.

Handoff248 lexical candidates remain unconfirmed. Exact original163.milk is the primary runtime witness: its per-pixel terms directly consume pixelsx*aspectx and pixelsy*aspecty. Preserve its init RNG and original bytes; Native4K before/expected captures and timings remain pending. Do not infer Windows pixel identity from source factor agreement.
