# Independent texture-input colour envelopes

The source inventory of77unresolved feedback cases shows35blur1users,29noise_lq,
22blur2,21blur3and16noisevol_hq. The operator counts include coordinate subgraphs,
so they are not exclusively colour blockers. Mixed texture inputs are a common
reason the main-only feedback model abstains. blocker-inventory.json preserves
exact original names/hashes, used operators and declared texture identities.

The additive texture_colour_envelopes record consumes existing affine texture-
colour matrices, supplying independent unit-RGBA raw RGB boxes and per-output-row
absolute weight norms. All-texture, main/blur-history and external input norms
stay separate. These are declared source identities, not observed bindings or
missing-texture fallback choices. Different blur histories/normalization and
kernel/coordinate dependence prevent a shared recurrence or whole-feedback gain
claim. Unknown coordinate terms/offsets withhold RGB boxes without discarding
valid input norms. Nonlinear mixture failures remain explicit unknowns.

Exact binary-rational sums are outward-rounded once. Independent review found
outward nextafter could overflow despite a finite pre-round value; a failing
max-float plus smallest-subnormal fixture preceded the finite recheck. Eight new
controls cover main/blur signs, external noise separation, decode coefficients,
coordinate/offset premises, image-driven lookup, nonlinear mixing and overflow.
Independent final review passed38texture/colour-mix/feedback controls with no
remaining actionable findings. Whole-loop contraction/persistence, full image-
coordinate sensitivity and actual brightness/palette/moods remain null.

All100source exports retain structured descriptions, exact byte/hash joins and
ZIP CRC.37stage records are bounded (28warp,9composite), across36presets;34stage
RGB boxes across33presets.36bounded stage records read history textures and8
read external textures; groups overlap.26presets with envelopes still have
unknown point-feedback models. This is useful independent colour-input data,
not26resolved recurrences or a classification accuracy claim.

No image/audio/time sample or shader/equation execution feeds the producer.
Source-operation time totals38.438932seconds, maximum2.409318seconds on this
host; no corpus/hardware guarantee. No native/preset/shared device/full corpus
was changed. Census keeps exact names/hashes, stage gains/boxes and unknowns.

Raw paired archive: `build/preset-corpus/source-texture-envelopes-2026-10-10/batch-000001.zip`.
SHA256ad547a300b7396ec2bf080a75a289ff8968f8e94abdafe652581480b062b3e0a.
Reader SHA256754e4f4129db585cb4f7d5bee915d6bb24ac10ab25901ee7ef0832ce50744afc.
Compile-manifest file SHA25601e97e69283242d039ad2925e1845b41aa81a96418c758e12a086ca3a899e32f.
Matching source34targets published2.3.36bytes; runtime qualification remains
independently pending. Visible appearance and mood accuracy are still unverified.

Final prepared suite: **2,713tests and92subtests pass in155.86seconds**.
Strict MkDocs and whitespace checks pass. These are source/colour-input
checks, not whole-loop or visible/mood accuracy certification.
