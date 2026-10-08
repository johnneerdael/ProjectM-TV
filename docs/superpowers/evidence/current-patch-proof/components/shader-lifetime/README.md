# Fragment-rejection shader lifetime

![Actual library frames and measured driver shader-object counts](comparison.png)

Both libraries compile a valid vertex shader followed by an intentionally invalid
fragment shader, sixteen times. A shared observer records actual `glCreateShader`
objects; `glIsShader` queries determine which vertex objects remain alive after
each rejected program and its `Renderer::Shader` destructor.

Upstream retains one unattached vertex object per rejection: the live count grows
from1 to16. Current retains zero after every attempt. The current-minus0002 control
also retains zero, confirming that this behavior is in current0001, not the HLSL
translator patch. All three observations repeat exactly in fresh processes.

**Code-level cause:** upstream compiles the vertex stage, then lets fragment-stage
rejection throw before the vertex is attached or deleted. Deleting the empty
program cannot free that unattached object. Current0001 catches that failure,
deletes the successful vertex shader and rethrows the original diagnostic.

Both roles subsequently compile and bind a valid retry. The diagnostic releases
its observed leaked objects before the normal preset render, so it does not leave
extra GPU state behind. The top panels are actual512×288 frames of unchanged
`Geiss - 3D - Shockwaves.milk` after that sequence. Their nearly identical look
demonstrates rendering still works; it does not depict the resource leak. The
lower panels are measured diagnostic data, not framebuffer pixels or timing claims.

The probe uses the actual linked library `Renderer::Shader`, not a copied test
implementation. It restores the shared GL entry point before rendering. There are
34 observed shader creations, sixteen recorded fragment rejections, a linked retry
and no GL API errors in each process. Each role has two exact120-frame RGB repeats.
Source reconstruction, rebuilt/canonical executable comparison and complete decoded
stream checks pass: [results](results.json), [verification](verification.json),
[frame and measurement audit](figure-audit.json).

This is a resource-correctness proof. It does not claim improved preset appearance,
measured GPU memory savings, frame-time improvement or a Windows/MilkDrop render.
