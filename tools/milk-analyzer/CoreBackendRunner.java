package nl.neerdael.projectm.analysis;

import android.content.res.AssetManager;
import android.opengl.EGL14;
import android.opengl.EGLConfig;
import android.opengl.EGLContext;
import android.opengl.EGLDisplay;
import android.opengl.EGLSurface;
import android.opengl.GLES20;
import java.io.FileOutputStream;
import java.io.FileInputStream;
import java.lang.reflect.Method;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import nl.neerdael.projectm.core.ProjectMJNI;

/** Headless test host for the unchanged, published core JNI interface. */
public final class CoreBackendRunner {
    private static native void configureClock(String corePath);
    private static native void setClock(long nanoseconds);
    public static void main(String[] args) throws Exception {
        if (args.length != 4 && args.length != 7) throw new IllegalArgumentException("LIB ASSETS WORK OUTPUT [CLOCK_LIB PCM FRAMES]");
        System.load(args[0]);
        AssetManager assets = AssetManager.class.getDeclaredConstructor().newInstance();
        Method add = AssetManager.class.getDeclaredMethod("addAssetPath", String.class);
        int cookie = (Integer) add.invoke(assets, args[1]);
        if (cookie == 0) throw new IllegalStateException("Asset archive rejected");
        ProjectMJNI.init(assets, args[2] + "/skip.txt", args[2] + "/textures");
        ProjectMJNI.setAutoChange(false);
        ProjectMJNI.setBeatCuts(false);
        ProjectMJNI.setBlankDetection(false);
        ProjectMJNI.setMeshSize(48,32);
        ProjectMJNI.setTransitionMode(ProjectMJNI.TRANSITION_CLASSIC,false);
        long deadline = System.nanoTime() + 30_000_000_000L;
        while (ProjectMJNI.getPresetCount() == 0) {
            if (System.nanoTime() > deadline) throw new IllegalStateException("Preset indexing timed out");
            Thread.sleep(10);
        }
        EGLDisplay display = EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY);
        int[] versions = new int[2];
        if (!EGL14.eglInitialize(display,versions,0,versions,1)) throw new IllegalStateException("EGL init failed");
        EGLConfig[] configs = new EGLConfig[1];int[] count = new int[1];
        int[] config = {EGL14.EGL_SURFACE_TYPE,EGL14.EGL_PBUFFER_BIT,EGL14.EGL_RENDERABLE_TYPE,0x40,
                EGL14.EGL_RED_SIZE,8,EGL14.EGL_GREEN_SIZE,8,EGL14.EGL_BLUE_SIZE,8,EGL14.EGL_ALPHA_SIZE,8,EGL14.EGL_NONE};
        if (!EGL14.eglChooseConfig(display,config,0,configs,0,1,count,0) || count[0] != 1)
            throw new IllegalStateException("No GLES3 config");
        EGLContext context = EGL14.eglCreateContext(display,configs[0],EGL14.EGL_NO_CONTEXT,
                new int[]{EGL14.EGL_CONTEXT_CLIENT_VERSION,3,EGL14.EGL_NONE},0);
        EGLSurface surface = EGL14.eglCreatePbufferSurface(display,configs[0],
                new int[]{EGL14.EGL_WIDTH,128,EGL14.EGL_HEIGHT,72,EGL14.EGL_NONE},0);
        if (!EGL14.eglMakeCurrent(display,surface,surface,context)) throw new IllegalStateException("EGL context failed");
        boolean simulated=args.length==7;
        if (simulated) { System.load(args[4]);configureClock(args[0]); }
        ProjectMJNI.onSurfaceCreated();ProjectMJNI.onSurfaceChanged(128,72);
        ByteBuffer rgba = ByteBuffer.allocateDirect(128*72*4);
        int frames=simulated?Integer.parseInt(args[6]):30;
        if (frames<1 || frames>36000) throw new IllegalArgumentException("Invalid frame schedule");
        FileInputStream pcm=simulated?new FileInputStream(args[5]):null;
        byte[] inputBytes=new byte[1470*4];byte[] waveform=new byte[1470];
        try (FileOutputStream output = new FileOutputStream(args[3])) {
            for (int frame=0;frame<frames;++frame) {
                if (simulated) {
                    int received=0;
                    while (received<inputBytes.length) { int n=pcm.read(inputBytes,received,inputBytes.length-received);if(n<0)throw new IllegalStateException("PCM ended before complete schedule");received+=n; }
                    ByteBuffer samples=ByteBuffer.wrap(inputBytes).order(ByteOrder.LITTLE_ENDIAN);
                    for(int i=0;i<waveform.length;++i) { float value=samples.getFloat();if(Float.isNaN(value)||Float.isInfinite(value)||Math.abs(value)>1)throw new IllegalArgumentException("Invalid PCM");waveform[i]=(byte)Math.max(0,Math.min(255,Math.round(value*128+128))); }
                    ProjectMJNI.addWaveform(waveform,waveform.length);
                    setClock(Math.round((frame+1)*1_000_000_000.0/30));
                }
                ProjectMJNI.onDrawFrame();
                if (frame==0) {
                    int[] binding=new int[1];GLES20.glGetIntegerv(0x8CAA,binding,0);
                    int[] viewport=new int[4];GLES20.glGetIntegerv(GLES20.GL_VIEWPORT,viewport,0);
                    System.out.println("readFbo="+binding[0]+" viewport="+java.util.Arrays.toString(viewport));
                }
                GLES20.glBindFramebuffer(GLES20.GL_FRAMEBUFFER,0);
                GLES20.glReadPixels(0,0,128,72,GLES20.GL_RGBA,GLES20.GL_UNSIGNED_BYTE,rgba);
                if (GLES20.glGetError()!=GLES20.GL_NO_ERROR) throw new IllegalStateException("GL readback failed");
                byte[] bytes = new byte[rgba.capacity()];rgba.position(0);rgba.get(bytes);rgba.position(0);output.write(bytes);
            }
        }
        if (pcm!=null) {if(pcm.read()!=-1)throw new IllegalStateException("PCM exceeds frame schedule");pcm.close();}
        System.out.println("core="+ProjectMJNI.getVersion()+" preset="+ProjectMJNI.getCurrentPresetName()+" count="+ProjectMJNI.getPresetCount());
        ProjectMJNI.release();EGL14.eglMakeCurrent(display,EGL14.EGL_NO_SURFACE,EGL14.EGL_NO_SURFACE,EGL14.EGL_NO_CONTEXT);
        EGL14.eglDestroySurface(display,surface);EGL14.eglDestroyContext(display,context);EGL14.eglTerminate(display);
        System.exit(0);
    }
}
