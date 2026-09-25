package com.example.projectm.visualizer;

/**
 * Turns captured 16-bit PCM into the waveform the engine takes from the Visualizer: 8-bit unsigned
 * mono (128 = silence), scaled like the Visualizer's default normalized mode, which sums the
 * channels and scales every buffer so its peak reaches 0.99 of full range (EffectVisualizer.cpp).
 * Presets then react the same to either audio source.
 */
final class PcmConverter {
    private PcmConverter() {}

    /**
     * @param in interleaved samples; {@code samples} of them are used
     * @param out receives one byte per frame
     * @return number of frames written
     */
    static int toUnsignedMono8(short[] in, int samples, int channels, byte[] out) {
        int frames = Math.min(samples / channels, out.length);
        int peak = 0;
        for (int f = 0; f < frames; f++) peak = Math.max(peak, Math.abs(sum(in, f, channels)));
        float scale = peak > 0 ? 0.99f / peak : 0f;
        for (int f = 0; f < frames; f++) {
            int value = Math.round(128f + sum(in, f, channels) * scale * 128f);
            out[f] = (byte) Math.max(0, Math.min(255, value));
        }
        return frames;
    }

    private static int sum(short[] in, int frame, int channels) {
        int total = 0;
        for (int c = 0; c < channels; c++) total += in[frame * channels + c];
        return total;
    }
}
