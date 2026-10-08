# Global flat-array initializer compatibility

![Upstream, current-minus0002 and current execute the same unchanged preset](comparison.png)

Unchanged original: `ORB - Quicksand Lab.milk`, SHA256
`80f11873f7e81063020a9d21f58e255d2efd4bcddb183d05c8b41dd16215ffeb`.
The composite initializes five `float4` samples from twenty scalar values and
uses their `.x`, `.y` and `.w` components in a five-tap filter.

**What to look for:** upstream and current-minus0002 display the brighter cyan
input through a generic fallback composite. Our current library executes the
authored filter, leaving dimmer cyan regions with sharper edge emphasis. The
selected frame29 is bright enough to show the difference in the full frame;
the aligned nearest-neighbour crop uses unchanged source pixels.

**Why the corrected output is darker:** the authored weights are `11/3` at the
centre and `-2/3` at each of four neighbours, then multiplied by0.2. Their sum is
0.2, so smooth regions are intentionally reduced to about one fifth of the input.
This is shader execution, not a brightness adjustment applied to the screenshot.

**Code-level cause:** HLSL fills vector arrays component by component. GLSL needs
five vector-valued array elements, not twenty scalar-valued elements. Current0002
groups the flat list into typed constructors and assigns global arrays as whole
arrays. Both upstream and the removal control record an array-index/type mismatch
while compiling the fragment shader, followed by `Using fallback shader`. Current
records no shader warnings/errors. The driver log directly identifies the array
path; the successful load status alone would not establish authored execution.

All three roles have two exact120-frame RGB repeats at512×288 and zero GL-error
frames. Source reconstruction, canonical NDK executable rebuild and all decoded
RGB payload checks pass. All120 frames differ between current-minus0002 and current.
[Complete capture receipt](results.json), [verification](verification.json),
[selected-frame audit](figure-audit.json).

This original demonstrates global flat vector layout and global-array assignment.
It does not demonstrate local flat layout, which needs its own labeled control.
The source adjustment/instrumentation and Android TV GPU protocol are inherited
from the parent evidence. No Windows/MilkDrop image or universal preset claim is made.
