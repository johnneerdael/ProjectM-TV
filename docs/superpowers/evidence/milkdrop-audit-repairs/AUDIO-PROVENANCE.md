# Capture audio provenance correction

Frozen capture workers describe `audioDelivery` as retaining the latest512 samples. That prose is stale for upstream4.2. The actual JNI implementation calls `projectm_pcm_get_max_samples()` and submits the resulting tail; current/frozen engine `ProjectMCWrapper.cpp` returns `Audio::AudioBufferSamples`, which is576. SpectrumSamples is separately512.

The frozen sourceac3dd034 used by I01/I21/colour-policy captures contains this same576-sample constant and API-backed FeedAudio. The transport remains complete1470-byte unsigned mono blocks, PCM SHA25614a59e75249dee0dd15d74487688c248c6a4a4b24a843b6d6f612ccc5c408dbc. Actual engine audio behavior, frozen native bytes and images are unchanged. Do not reconstruct the JNI input using512-tail prose or claim512-tail host parity. Future manifests state the queried API boundary without hardcoding a value.

Archived manifests retain their original bytes and hashes. Source-instrumented producer traces must record the queried sample count and qualify exact decoding/analysis independently. Host float32 latest512 diagnostics are a different transport and retain their explicit numerical-parity limits.
