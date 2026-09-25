package com.example.projectm.visualizer;

import android.content.Context;
import android.graphics.Point;
import android.opengl.GLSurfaceView;
import android.util.AttributeSet;
import android.util.Log;
import android.view.WindowManager;

/**
 * GLSurfaceView that renders projectM continuously.
 *
 * Render resolution is set with {@link android.view.SurfaceHolder#setFixedSize}: the surface
 * buffer gets the requested size and the display hardware scaler stretches it to the full screen
 * at no GPU cost. This is what makes 480p/720p modes both fast and full-screen.
 */
public class VisualizerView extends GLSurfaceView {
    private static final String TAG = "VisualizerView";

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
