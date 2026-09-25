package com.example.projectm.visualizer;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.View;

/**
 * Thin level bar that shows the audio the visualizer hears. Rises immediately and falls back
 * smoothly, like a VU meter.
 */
public class AudioMeterView extends View {
    private static final float DECAY_PER_UPDATE = 0.85f;

    private final Paint track = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint fill = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF rect = new RectF();
    private float shown;

    public AudioMeterView(Context context, AttributeSet attrs) {
        super(context, attrs);
        track.setColor(getResources().getColor(R.color.divider));
        fill.setColor(getResources().getColor(R.color.accent));
    }

    /** @param rms recent audio level (RMS of normalized samples, 0..1) */
    public void setLevel(float rms) {
        // Music is typically 0.05-0.3 RMS; the square root spreads quiet levels over the bar.
        float target = Math.min(1f, (float) Math.sqrt(Math.max(0f, rms)) * 1.6f);
        float next = target >= shown ? target : Math.max(target, shown * DECAY_PER_UPDATE);
        if (Math.abs(next - shown) > 0.002f) {
            shown = next;
            invalidate();
        }
    }

    @Override
    protected void onDraw(Canvas canvas) {
        float h = getHeight();
        float radius = h / 2f;
        rect.set(0, 0, getWidth(), h);
        canvas.drawRoundRect(rect, radius, radius, track);
        if (shown > 0f) {
            rect.set(0, 0, Math.max(h, getWidth() * shown), h);
            canvas.drawRoundRect(rect, radius, radius, fill);
        }
    }
}
