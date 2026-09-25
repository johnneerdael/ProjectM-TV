package com.example.projectm.visualizer;

import android.content.Context;
import android.opengl.GLSurfaceView;
import android.util.AttributeSet;
import android.util.Log;
import android.view.Choreographer;

/**
 * GLSurfaceView that renders projectM.
 *
 * Render resolution is set with {@link android.view.SurfaceHolder#setFixedSize}: the surface
 * buffer gets the requested size and the display hardware scaler stretches it to the full screen
 * at no GPU cost, so lower resolutions are both fast and full-screen.
 *
 * Frame rate: rendering can be paced to every n-th vsync with {@link Choreographer}. On devices
 * that cannot sustain the full refresh rate, an even 30 fps looks much smoother than an uneven
 * 40-50 fps and leaves GPU headroom for heavy presets.
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

    /**
     * Renders on every {@code divisor}-th vsync: 1 = full refresh rate, 2 = half (e.g. 30 fps at
     * 60 Hz, 60 fps at 120 Hz). Call from the UI thread.
     */
    public void setFrameDivisor(int divisor) {
        frameDivisor = Math.max(1, divisor);
        stopPacing();
        if (frameDivisor > 1) {
            setRenderMode(RENDERMODE_WHEN_DIRTY);
            startPacing();
        } else {
            setRenderMode(RENDERMODE_CONTINUOUSLY);
        }
        Log.i(TAG, "Rendering every " + frameDivisor + " vsync(s)");
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
     * Sets the render (surface buffer) size. It may exceed the UI resolution: on TVs that drive
     * the UI at 1080p, a 3840x2160 SurfaceView buffer is still shown at the panel's full 4K.
     */
    public void setRenderSize(int width, int height) {
        getHolder().setFixedSize(width, height);
        Log.i(TAG, "Render size " + width + "x" + height);
    }
}
