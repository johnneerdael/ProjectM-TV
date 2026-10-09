# I07 — retain both-channel band analysis

**Disposition: retain upstream stereo averaging.** Production PCM controls and Native4K owner images qualify this retained policy. No engine patch or new stereo JNI bridge is added.

Original MilkDrop2 derives band analysis from the left channel. Current upstream analyzes both channels and averages their spectra, intentionally addressing right-weighted content. The TV app submits unsigned mono PCM; production PCM duplicates it into both channels. With fresh mono history, this particular combination difference is inactive at every output resolution.

## Executed producer evidence

[Actual production PCM controls](pcm_policy_controls.cpp) compile the current PCM, FFT, waveform aligner and Loudness sources directly. [Output](pcm-policy-controls.txt) and [identity](executed-pcm-identity.json) record the exact source and common transport. All480 mono frames use the576-sample queried-tail contract; every left/right spectrum bin and current/attenuated band is exactly equal between averaged and left-only combination stages.

Controlled stereo uses real PCM::Add(...,2,count), interleaved bounded floats,120frames and60warm frames at30Hz. Right-amplitude step, swapped channels and right-only inputs differ from the left-only combination oracle; equal stereo remains exact. The frame60 step gives averaged bass1.993457794 versus left-only1.004740357. This uses the current FFT/Loudness with only combination changed; it is not a Windows audio implementation or exact JNI clock-value oracle.

## Native4K images

[Results](native-results.json) and [artifact identity](native-identity.json) bind frozenac3/current27patches, API34ARM64, hostGPU/GLES3, Native3840×2160 output with Standard1280×720 reference, common PCM/seed12345/mesh48×32/30FPS. Six480frame jobs pass allGL/name/cleanup checks and final READ framebuffer0 verification; three repeat groups and48 PNG/RGB checks pass.

Two finite border presets explicitly freeze the executed stereo stage coefficients into q1 and `ob_size=.03+.03*q1`. This visualizes the coefficient difference on the unchanged Native renderer:

| Retained averaged stage | Left-only combination expectation |
|---|---|
| [Averaged bass coefficient](native-captures/stereopolicy-audit-stereo-i07-averaged-stage-current-0/frame-239.png) | [Left-only coefficient](native-captures/stereopolicy-audit-stereo-i07-left-only-stage-current-0/frame-239.png) |

These are labelled source-stage surrogates. They do not make the mono JNI route stereo or certify original Windows pixels. The unchanged Sjadoh - Fortune Teller preset is also captured twice under the production mono route; its source SHA and bass→geometry provenance are in [source design](SOURCE-DESIGN.md). Its repeated image is preservation evidence, not an affected-original claim.

## Limits and owner followup

Retain existing both-channel behavior for stereo AAR consumers and preserve mono TV transport. A host switching from stereo to a partial mono block can retain unequal ring history; require a fresh mono context or a filled576sample ring before asserting invariance. No new rendering work or performance improvement is claimed. Physical-TV measurements, hidden shipping stereo arrays, original Windows FFT equivalence and whole-corpus stereo exposure remain unmeasured. Any left-only compatibility option requires separate demonstrated consumer need and versioning. The supplied lexical candidate count is not an affected census.
