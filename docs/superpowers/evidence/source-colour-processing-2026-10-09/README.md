# Ordered source colour-processing checkpoint

source_colour_processing.py exports perRGB known processing suffixes in execution
order, rooted at a constant, samplechannel or unresolved/sourceexpression. Supported
steps include abs/power/domainguard, inversion/constantminus, gain/bias/division,
clamp and saturate. Channel permutations are explicit. Alpha-only discarded code
is excluded. This is partialsource processing, not an executable shader, complete
palette/material or recognizable reconstruction certificate.

The patched native lowering inserts abs/domain requirements for mostpow calls;
those operations remain ordered, with the existing literalpow1 exception. Dynamic
exponents and combined/spatial bases stay opaque sourceprograms. Domains, texture
history, sampling, masks and storage remain conditions. No frame/audio/shader/
equation execution occurs. References: ShaderFields.lower's pinned target lowering
and source31 MilkdropShader.cpp484–505 returned RGBsink contract.

232 focused appearance/family/export controls pass. Independent narrowreview
has no findings and passed140appearance controls.
StrictMkDocs and whitespace checks pass. Prepared complete suite:2196tests and92subtests pass in137.28seconds.

Fixed100 census:100computed;47presets have known tone steps, meanelapsed.29046017s.
Occurrences byRGBchannel/stage:65bias,113gain,37one-minus,21domainguard,12abs,
9power,9constantminus. These are operation occurrences, not distinct visibleeffects.
Exact sources, model hashes and compact processing records are in census.json;
full base/coordinate programs remain in the raw pairedbatch and are hash-bound.

Raw batch:build/preset-corpus/source-colour-processing-2026-10-09/batch-000001.zip
SHA2566417310f03fb432c7b837daf4bf190f530b38842e59cb005d223f811802b9702.
Published full2.3.33/byte-equivalent31source remains the target; no librarypatch,
device, sharedcorpus or runtimecapture was operated. Existing47numeric output
is unchanged. Finalpalettes and recognizable approximateJSON look remain unverified.
