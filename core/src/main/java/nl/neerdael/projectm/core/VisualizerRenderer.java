package nl.neerdael.projectm.core;

import android.opengl.GLES20;
import android.opengl.GLSurfaceView;
import android.util.Log;

import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/**
 * Thin GL-thread bridge to the native engine. The render size equals the surface size, which
 * {@link VisualizerView} controls through the hardware scaler, so no viewport tricks are needed.
 */
public class VisualizerRenderer implements GLSurfaceView.Renderer {
    private static final String TAG = "VisualizerRenderer";

    /** Called on the GL thread; implementations should hand off to the UI thread. */
    public interface StatsListener {
        void onFpsSample(float fps);
        void onPresetChanged();
    }

    /** Managed clients acknowledge fresh memory budgets before the first frame of a new GL context. */
    public interface BudgetStatsListener extends StatsListener {
        void onRenderBudgetRequested(long generation);
        default void onBudgetFpsSample(float fps, long generation, int width, int height) {
            onFpsSample(fps);
        }
    }

    private final StatsListener listener;
    private int lastPresetChange = Integer.MIN_VALUE;
    private int statsCountdown;
    private static final int STATS_LOG_INTERVAL_S = 5;

    public VisualizerRenderer(StatsListener listener) {
        this.listener = listener;
    }

    private volatile float currentFps;
    private volatile int surfaceWidth;
    private volatile int surfaceHeight;
    private long fpsWindowStart;
    private int framesInWindow;
    private long lastRenderedFrameSerial;

    @Override
    public void onSurfaceCreated(GL10 gl, EGLConfig config) {
        Log.i(TAG, "GL: " + GLES20.glGetString(GLES20.GL_VERSION) + " | "
                + GLES20.glGetString(GLES20.GL_RENDERER));
        try {
            // The render thread is the app's critical path; keep it ahead of background work.
            android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_DISPLAY);
        } catch (RuntimeException e) {
            Log.w(TAG, "Could not raise render thread priority", e);
        }
        ProjectMJNI.onSurfaceCreated();
        if (listener instanceof BudgetStatsListener) {
            long generation = ProjectMJNI.requireRenderBudget();
            ((BudgetStatsListener) listener).onRenderBudgetRequested(generation);
        }
        fpsWindowStart = System.nanoTime();
        framesInWindow = 0;
        lastRenderedFrameSerial = ProjectMJNI.getRenderedFrameSerial();
    }

    @Override
    public void onSurfaceChanged(GL10 gl, int width, int height) {
        Log.i(TAG, "Surface " + width + "x" + height);
        surfaceWidth = width;
        surfaceHeight = height;
        ProjectMJNI.onSurfaceChanged(width, height);
        fpsWindowStart = System.nanoTime();
        framesInWindow = 0;
        lastRenderedFrameSerial = ProjectMJNI.getRenderedFrameSerial();
    }

    @Override
    public void onDrawFrame(GL10 gl) {
        ProjectMJNI.onDrawFrame();

        int change = ProjectMJNI.getPresetChangeCounter();
        if (change != lastPresetChange) {
            boolean first = lastPresetChange == Integer.MIN_VALUE;
            lastPresetChange = change;
            if (!first) listener.onPresetChanged();
        }

        long serial = ProjectMJNI.getRenderedFrameSerial();
        framesInWindow += (int) Math.max(0, serial - lastRenderedFrameSerial);
        lastRenderedFrameSerial = serial;
        long now = System.nanoTime();
        long elapsed = now - fpsWindowStart;
        if (elapsed >= 1_000_000_000L) {
            currentFps = framesInWindow * 1e9f / elapsed;
            framesInWindow = 0;
            fpsWindowStart = now;
            if (listener instanceof BudgetStatsListener) {
                ((BudgetStatsListener) listener).onBudgetFpsSample(currentFps,
                        ProjectMJNI.getCompletedRenderBudgetGeneration(), surfaceWidth, surfaceHeight);
            } else listener.onFpsSample(currentFps);
            // Machine-readable line for tools/tv-diagnostics.sh (cheap: once every 5 s).
            if (--statsCountdown <= 0) {
                statsCountdown = STATS_LOG_INTERVAL_S;
                Log.i(TAG, String.format(java.util.Locale.US, "STATS fps=%.1f surface=%dx%d audio=%.3f",
                        currentFps, surfaceWidth, surfaceHeight, ProjectMJNI.getAudioLevel()));
            }
        }
    }

    /** Must run on the GL thread (use GLSurfaceView.queueEvent). */
    public void release() {
        ProjectMJNI.release();
    }

    public float getCurrentFps() {
        return currentFps;
    }

    public int getSurfaceWidth() {
        return surfaceWidth;
    }

    public int getSurfaceHeight() {
        return surfaceHeight;
    }
}
