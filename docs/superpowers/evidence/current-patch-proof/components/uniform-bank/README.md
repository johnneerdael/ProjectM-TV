# Initialized writable uniform-bank control

![Writing q18 preserves the incoming q19 component only with the retained fix](comparison.png)

This [generated diagnostic](bank-components.milk) supplies `q18=0.2` and `q19=0.8`
through preset equations. Its shader changes only `q18` and outputs
`float3(q18, q19, 0.25)`. Those q variables occupy different components of the same
packed `_qe` uniform bank.

The expected RGB8 output is `(255, 204, 64)`: red from the shader write, green
from the unchanged incoming0.8 component, and blue from0.25. Actual upstream and
current-minus0002 render `(255, 0, 64)` at the centre; current renders the expected
value. All three compile without shader warnings. The upstream translator's
writable replacement lacks the required incoming initialization; current copies
the uniform bank before any write, preserving the other components.

This is a numerical activation control, not an artist preset or a universal
prediction for unspecified shader-local values. The selected frame59 has the
same unaltered pixels as the other retained frames. Each role has two exact
120-frame RGB repeats at512×288 and zero GL-error frames. Source, canonical
executable and full decoded-stream checks pass: [results](results.json),
[verification](verification.json), [frame/figure audit](figure-audit.json).
