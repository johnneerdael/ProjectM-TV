package com.example.projectm.visualizer;

import android.content.Context;
import android.graphics.Point;
import android.opengl.GLSurfaceView;
import android.util.AttributeSet;
import android.util.Log;
import android.view.Choreographer;
import android.view.WindowManager;

/**
 * GLSurfaceView that renders projectM.
 *
 * Render resolution is set with {@link android.view.SurfaceHolder#setFixedSize}: the surface
 * buffer gets the requested size and the display hardware scaler stretches it to the full screen
 * at no GPU cost. This is what makes 480p/720p modes both fast and full-screen.
 *
 * Frame rate: full rate renders continuously; half rate renders on every second vsync, driven by
 * {@link Choreographer}. On devices that cannot sustain the full refresh rate, an even 30 (or 25)
 * fps looks much smoother than an uneven 40-50 fps and leaves GPU headroom for heavy presets.
 */
public class VisualizerView extends GLSurfaceView {
    private static final String TAG = "VisualizerView";

    private int frameDivisor = 1;
    private boolean paced;
    private long vsyncCount;
    private final Choreographer.FrameCallback vsync = new Choreographer.FrameCallback() {
        @Override
        public void doFrame(long frameTimeNanos) {
            if (!paced) return;
            if (++vsyncCount % frameDivisor == 0) requestRender();
            Choreographer.getInstance().postFrameCallback(this);
        }
    };

    public VisualizerView(Context context, AttributeSet attrs) {
        super(context, attrs);
        // projectM 4 uses GLSL "300 es" shaders and links against GLESv3: ask for an ES 3 context.
        setEGLContextClientVersion(3);
        // RGB888 without alpha, depth or stencil: projectM renders to its own framebuffers.
        setEGLConfigChooser(8, 8, 8, 0, 0, 0);
        setPreserveEGLContextOnPause(true);
    }

    public void start(Renderer renderer) {
        setRenderer(renderer);
        setRenderMode(RENDERMODE_CONTINUOUSLY);
    }

    /** Display refresh rate in Hz (typically 60 or 50 on TVs). */
    public float displayRefreshRate() {
        WindowManager wm = (WindowManager) getContext().getSystemService(Context.WINDOW_SERVICE);
        float rate = wm.getDefaultDisplay().getRefreshRate();
        return rate > 1 ? rate : 60f;
    }

    /** Renders on every vsync ({@code halfRate == false}) or every second vsync. Call from the UI thread. */
    public void setHalfFrameRate(boolean halfRate) {
        frameDivisor = halfRate ? 2 : 1;
        stopPacing();
        if (halfRate) {
            setRenderMode(RENDERMODE_WHEN_DIRTY);
            startPacing();
        } else {
            setRenderMode(RENDERMODE_CONTINUOUSLY);
        }
        Log.i(TAG, "Frame rate: " + (halfRate ? "half" : "full") + " of " + displayRefreshRate() + " Hz");
    }

    @Override
    public void onResume() {
        super.onResume();
        if (frameDivisor > 1) startPacing();
    }

    @Override
    public void onPause() {
        stopPacing();
        super.onPause();
    }

    private void startPacing() {
        if (paced) return;
        paced = true;
        Choreographer.getInstance().postFrameCallback(vsync);
    }

    private void stopPacing() {
        paced = false;
        Choreographer.getInstance().removeFrameCallback(vsync);
    }

    /**
     * @param targetHeight render height in pixels, or 0 for the display's native resolution.
     */
    public void setRenderHeight(int targetHeight) {
        Point display = new Point();
        WindowManager wm = (WindowManager) getContext().getSystemService(Context.WINDOW_SERVICE);
        wm.getDefaultDisplay().getRealSize(display);
        int displayWidth = Math.max(display.x, display.y);
        int displayHeight = Math.min(display.x, display.y);

        if (targetHeight <= 0 || targetHeight >= displayHeight) {
            getHolder().setSizeFromLayout();
            Log.i(TAG, "Render resolution: native " + displayWidth + "x" + displayHeight);
            return;
        }
        int width = Math.round(targetHeight * (float) displayWidth / displayHeight) & ~1;
        getHolder().setFixedSize(width, targetHeight);
        Log.i(TAG, "Render resolution: " + width + "x" + targetHeight + " scaled to "
                + displayWidth + "x" + displayHeight);
    }
}
