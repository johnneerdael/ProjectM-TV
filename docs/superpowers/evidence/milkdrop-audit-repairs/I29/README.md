# I29 — Negative odd echo orientation

Candidate0022 restores original horizontal U flip whenever signed orientation%2 is nonzero, including−1/−3 and equivalent finite negative values. Preserve signed modulo4, original vertical predicate, truncation/valid-input guard, zoom, alpha, gamma/tint and float diffuse policies. No pass, resource or added vertex is introduced.

The actual textured GL test fails before at orientation−7 and passes after across−7/−5/−3/−1/0/1/2/3/4/5. A known64×64 field has left red64 and right red192; active echo1/zoom1 must swap those halves for any odd orientation. All46 normal controls pass,22 patches apply. No literal-negative bundled orientation was found in the original scan; dynamic values remain possible. Native4K finite edge-field diagnostic and final integration remain pending; do not invent an affected-original census.
