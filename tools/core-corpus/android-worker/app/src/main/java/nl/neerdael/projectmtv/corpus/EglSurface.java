package nl.neerdael.projectmtv.corpus;

import android.opengl.EGL14;
import android.opengl.EGLConfig;
import android.opengl.EGLContext;
import android.opengl.EGLDisplay;
import android.opengl.EGLSurface;

/** A real GLES 3 context with an RGBA8 pbuffer, rendering to framebuffer zero. */
final class EglSurface implements AutoCloseable {
    private EGLDisplay display = EGL14.EGL_NO_DISPLAY;
    private EGLContext context = EGL14.EGL_NO_CONTEXT;
    private EGLSurface surface = EGL14.EGL_NO_SURFACE;

    void create(int width, int height) {
        display = EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY);
        require(display != EGL14.EGL_NO_DISPLAY, "eglGetDisplay");
        int[] versions = new int[2];
        require(EGL14.eglInitialize(display, versions, 0, versions, 1), "eglInitialize");
        require(EGL14.eglBindAPI(EGL14.EGL_OPENGL_ES_API), "eglBindAPI");
        int[] attributes = {
                EGL14.EGL_SURFACE_TYPE, EGL14.EGL_PBUFFER_BIT,
                EGL14.EGL_RENDERABLE_TYPE, 0x0040, // EGL_OPENGL_ES3_BIT_KHR
                EGL14.EGL_RED_SIZE, 8, EGL14.EGL_GREEN_SIZE, 8,
                EGL14.EGL_BLUE_SIZE, 8, EGL14.EGL_ALPHA_SIZE, 8,
                EGL14.EGL_DEPTH_SIZE, 0, EGL14.EGL_STENCIL_SIZE, 0,
                EGL14.EGL_NONE};
        EGLConfig[] configs = new EGLConfig[1];
        int[] count = new int[1];
        require(EGL14.eglChooseConfig(display, attributes, 0, configs, 0, 1, count, 0)
                && count[0] > 0, "eglChooseConfig GLES3 RGBA8 pbuffer");
        int[] channelBits = new int[1];
        for (int attribute : new int[]{EGL14.EGL_RED_SIZE, EGL14.EGL_GREEN_SIZE,
                EGL14.EGL_BLUE_SIZE, EGL14.EGL_ALPHA_SIZE}) {
            require(EGL14.eglGetConfigAttrib(display, configs[0], attribute, channelBits, 0)
                    && channelBits[0] == 8, "pbuffer channel precision must be exactly 8 bits");
        }
        context = EGL14.eglCreateContext(display, configs[0], EGL14.EGL_NO_CONTEXT,
                new int[]{EGL14.EGL_CONTEXT_CLIENT_VERSION, 3, EGL14.EGL_NONE}, 0);
        require(context != EGL14.EGL_NO_CONTEXT, "eglCreateContext");
        surface = EGL14.eglCreatePbufferSurface(display, configs[0],
                new int[]{EGL14.EGL_WIDTH, width, EGL14.EGL_HEIGHT, height, EGL14.EGL_NONE}, 0);
        require(surface != EGL14.EGL_NO_SURFACE, "eglCreatePbufferSurface");
        require(EGL14.eglMakeCurrent(display, surface, surface, context), "eglMakeCurrent");
        int[] size = new int[1];
        require(EGL14.eglQuerySurface(display, surface, EGL14.EGL_WIDTH, size, 0)
                && size[0] == width, "pbuffer width");
        require(EGL14.eglQuerySurface(display, surface, EGL14.EGL_HEIGHT, size, 0)
                && size[0] == height, "pbuffer height");
    }

    String vendor() { return EGL14.eglQueryString(display, EGL14.EGL_VENDOR); }
    String version() { return EGL14.eglQueryString(display, EGL14.EGL_VERSION); }

    private static void require(boolean success, String operation) {
        if (!success) throw new IllegalStateException(operation + " failed, EGL error 0x"
                + Integer.toHexString(EGL14.eglGetError()));
    }

    @Override public void close() {
        if (display == EGL14.EGL_NO_DISPLAY) return;
        String failure = null;
        if (!EGL14.eglMakeCurrent(display, EGL14.EGL_NO_SURFACE, EGL14.EGL_NO_SURFACE,
                EGL14.EGL_NO_CONTEXT)) failure = "eglMakeCurrent cleanup";
        if (surface != EGL14.EGL_NO_SURFACE && !EGL14.eglDestroySurface(display, surface))
            failure = "eglDestroySurface";
        if (context != EGL14.EGL_NO_CONTEXT && !EGL14.eglDestroyContext(display, context))
            failure = "eglDestroyContext";
        if (!EGL14.eglTerminate(display)) failure = "eglTerminate";
        if (!EGL14.eglReleaseThread()) failure = "eglReleaseThread";
        display = EGL14.EGL_NO_DISPLAY;
        context = EGL14.EGL_NO_CONTEXT;
        surface = EGL14.EGL_NO_SURFACE;
        if (failure != null) throw new IllegalStateException(failure + " failed");
    }
}
