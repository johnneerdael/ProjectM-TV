# Per-fix real-driver proof exports

- `08-fresh-history-init.png`: actual 16×16 RGBA8 attachment reads, before/after initialization. Allocator contents are deliberately controlled to 0x7b. Before reads `[123,123,123,123]` in all256 pixels; after reads `[0,0,0,0]`. Raw `.rgba` files are retained.
- `09-context-fbo-ownership.png`: actual recreated-context framebuffer name collision. The old helper leaves attachment name0 (incomplete); the local-scratch helper preserves sentinel attachment1 (complete). The sentinel's painted pixel storage remains `[69,69,69,69]` in both cases; the old failure is lost framebuffer ownership, not destruction of sentinel storage.

These are explicitly labeled renderer diagnostic figures, not app/preset screenshots. They do not claim that a particular Mali startup outlier is resolved.

`ReadbackProofTest.cpp` is a copy of the regression fixture with read-only pixel/log export added. `red/` and `green/` contain its actual CGL logs, raw pixel reads and build logs. `manifest.json` contains renderer source, fixture, patch, raw data, log and image SHA256 values. The existing complete host-suite log hash is also preserved.

Reproduce from the owning worktree:

```sh
build/preset-lab-venv/bin/python build/follow-ups/core-initial-history-review/proof-export/export.py
```

The exporter verifies all raw pixel values, the actual framebuffer status codes, expected red/green exit codes and then renders the figures. Only this proof-export directory is written.
