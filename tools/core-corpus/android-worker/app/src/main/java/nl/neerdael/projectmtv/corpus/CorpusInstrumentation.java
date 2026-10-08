package nl.neerdael.projectmtv.corpus;

import android.app.Instrumentation;
import android.content.Context;
import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.opengl.GLES30;
import android.os.Build;
import android.os.Bundle;
import android.os.SystemClock;
import android.util.Log;

import nl.neerdael.projectm.core.ProjectMJNI;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.Set;

/** One real ProjectMJNI preset job per fresh instrumentation process; no Activity is launched. */
public final class CorpusInstrumentation extends Instrumentation {
    private static final String TAG = "CoreCorpus";
    private static final int FRAMES = 480;
    private static final int FPS = 30;
    private static final int PCM_BLOCK = 1470;
    private static final int[] CAPTURES = {120, 150, 180, 210, 239, 300, 390, 479};
    private Bundle arguments;

    @Override public void onCreate(Bundle arguments) {
        super.onCreate(arguments);
        this.arguments = arguments;
        start();
    }

    @Override public void onStart() {
        JSONObject manifest = new JSONObject();
        EglSurface egl = new EglSurface();
        File output = null;
        boolean surfaceCreated = false;
        boolean succeeded = false;
        long started = SystemClock.elapsedRealtime();
        try {
            Context context = getTargetContext();
            File requestFile = privateFile(context, arguments.getString("job"));
            JSONObject job = new JSONObject(new String(readAll(new FileInputStream(requestFile)),
                    StandardCharsets.UTF_8));
            File requestedOutput = privateFile(context, job.optString("outputDir",
                    new File(requestFile.getParentFile(), "output").getAbsolutePath()));
            if (!requestedOutput.getPath().startsWith(requestFile.getParentFile().getPath() + File.separator))
                throw new IllegalArgumentException("Output must be below this job's request directory");
            if (!requestedOutput.mkdirs() && !requestedOutput.isDirectory())
                throw new IllegalStateException("Cannot create output directory");
            // Refuse accidental reuse; the host must use a fresh directory and process per job.
            if (new File(requestedOutput, "manifest.json").exists())
                throw new IllegalStateException("Output already contains a completed manifest");
            output = requestedOutput;
            manifest.put("protocol", "projectmtv-core-corpus-v1");
            manifest.put("applicationId", context.getPackageName());
            manifest.put("pid", android.os.Process.myPid());
            manifest.put("job", job);
            manifest.put("requestSha256", hex(sha256(readAll(new FileInputStream(requestFile)))));
            runJob(context, job, output, manifest, egl);
            surfaceCreated = true;
            succeeded = true;
        } catch (Throwable failure) {
            Log.e(TAG, "Corpus job failed", failure);
            putFailure(manifest, "error", failure);
        } finally {
            // runJob publishes this flag immediately before onSurfaceCreated, including its failure path.
            surfaceCreated |= manifest.optBoolean("coreSurfaceAttempted", false);
            try {
                if (surfaceCreated) {
                    ProjectMJNI.release(); // still on the same thread, with the real EGL context current
                    checkGl("ProjectMJNI.release");
                    manifest.put("coreReleased", true);
                }
            } catch (Throwable failure) {
                succeeded = false;
                putFailure(manifest, "releaseError", failure);
            }
            try {
                egl.close();
                manifest.put("eglDestroyed", true);
            } catch (Throwable failure) {
                succeeded = false;
                putFailure(manifest, "eglCleanupError", failure);
            }
            try {
                manifest.put("status", succeeded ? "ok" : "failed");
                manifest.put("wallDurationMs", SystemClock.elapsedRealtime() - started);
                if (output != null) writeManifest(output, manifest);
            } catch (Throwable failure) {
                succeeded = false;
                Log.e(TAG, "Cannot write atomic manifest", failure);
            }
            Bundle results = new Bundle();
            results.putString("status", succeeded ? "ok" : "failed");
            results.putString("manifest", output == null ? "" : new File(output, "manifest.json").getAbsolutePath());
            if (!succeeded) results.putString("error", manifest.optString("error", "Job cleanup or manifest failed"));
            finish(succeeded ? android.app.Activity.RESULT_OK : android.app.Activity.RESULT_CANCELED, results);
        }
    }

    private void runJob(Context context, JSONObject job, File output, JSONObject manifest,
                        EglSurface egl) throws Exception {
        String preset = job.getString("preset");
        int width = positive(job.getInt("width"), "width");
        int height = positive(job.getInt("height"), "height");
        int referenceWidth = job.getInt("referenceWidth");
        int referenceHeight = job.getInt("referenceHeight");
        if (!((referenceWidth == 0 && referenceHeight == 0)
                || (referenceWidth > 0 && referenceHeight > 0)))
            throw new IllegalArgumentException("Reference dimensions must be paired 0,0 (authored) or both positive");
        if ((long) width * height * 4 > Integer.MAX_VALUE)
            throw new IllegalArgumentException("Capture dimensions exceed ByteBuffer capacity");
        boolean instrumented = job.getBoolean("instrumented");
        long seed = job.getLong("seed");
        manifest.put("determinism", instrumented ? "instrumented-fixed-clock-seed" : "nondeterministic-real-clock-smoke");
        manifest.put("frameCountExpected", FRAMES);
        manifest.put("fps", FPS);
        manifest.put("audioBlockBytes", PCM_BLOCK);
        manifest.put("audioDelivery", "complete unsigned 8-bit mono blocks via ProjectMJNI.addWaveform; production FeedAudio retains latest 512 samples");
        manifest.put("captureSemantics", "eight selected final-output frames from read framebuffer zero, top-down RGB8 SHA256; sampled metrics under common 16-second audio; no all-frame image hash");
        manifest.put("settings", new JSONObject().put("autoChange", false).put("beatCuts", false)
                .put("blankDetection", false).put("musicCategory", "all").put("meshWidth", 48)
                .put("meshHeight", 32).put("presetDurationSeconds", 3600).put("softCutDurationSeconds", 0)
                .put("transitionMode", "CLASSIC").put("lowEndDevice", false));
        manifest.put("captures", new JSONArray());
        manifest.put("memoryPressureCalls", new JSONArray());
        manifest.put("device", device());
        byte[] pcm = readAll(new FileInputStream(privateFile(context, job.getString("pcmPath"))));
        if (pcm.length != FRAMES * PCM_BLOCK)
            throw new IllegalArgumentException("PCM must contain exactly 480 complete 1470-byte blocks, got " + pcm.length);
        manifest.put("pcmSha256", hex(sha256(pcm)));
        AssetManager assets = context.getAssets();
        byte[] index = readAll(assets.open("presets.idx"));
        Set<String> names = new HashSet<>();
        File mask = new File(output, "skip-mask.txt");
        try (BufferedReader lines = new BufferedReader(new InputStreamReader(
                new ByteArrayInputStream(index), StandardCharsets.UTF_8));
             OutputStreamWriter skip = new OutputStreamWriter(new FileOutputStream(mask), StandardCharsets.UTF_8)) {
            String line;
            while ((line = lines.readLine()) != null) {
                String name = line.split("\t", 2)[0];
                if (!name.toLowerCase(java.util.Locale.ROOT).endsWith(".milk")) continue;
                if (!names.add(name)) throw new IllegalArgumentException("Duplicate preset in bundled index: " + name);
                if (!name.equals(preset)) { skip.write(name); skip.write('\n'); }
            }
        }
        int expected = job.optInt("expectedPresetCount", 9606);
        if (names.size() != expected || !names.contains(preset))
            throw new IllegalArgumentException("Bundled index count/target mismatch: " + names.size() + ", target " + preset);
        manifest.put("bundledPresetCount", names.size());
        manifest.put("indexSha256", hex(sha256(index)));
        manifest.put("presetAssetSha256", hex(sha256(readAll(assets.open("presets/" + preset)))));
        String prefix = ProjectMJNI.getSystemProperty("debug.projectmtv.preset");
        if (prefix.isEmpty() || !preset.startsWith(prefix))
            throw new IllegalStateException("Host debug.projectmtv.preset prefix missing or inconsistent with target");
        manifest.put("forcedPresetPrefix", prefix);
        if (instrumented) {
            LabBridge.initialize(seed, referenceWidth, referenceHeight);
            LabBridge.setFrameClock(0.0);
        }
        egl.create(width, height);
        manifest.put("eglVendor", egl.vendor());
        manifest.put("eglVersion", egl.version());
        manifest.put("glVendor", GLES30.glGetString(GLES30.GL_VENDOR));
        manifest.put("glRenderer", GLES30.glGetString(GLES30.GL_RENDERER));
        String version = GLES30.glGetString(GLES30.GL_VERSION);
        manifest.put("glVersion", version);
        manifest.put("glShadingLanguageVersion", GLES30.glGetString(GLES30.GL_SHADING_LANGUAGE_VERSION));
        if (version == null || !version.startsWith("OpenGL ES 3"))
            throw new IllegalStateException("Expected an actual OpenGL ES 3 context: " + version);
        checkGl("EGL context initialization");
        File textures = new File(context.getFilesDir(), "corpus-textures");
        ProjectMJNI.init(assets, mask.getAbsolutePath(), textures.getAbsolutePath());
        ProjectMJNI.setAutoChange(false);
        ProjectMJNI.setBeatCuts(false);
        ProjectMJNI.setBlankDetection(false);
        ProjectMJNI.setMusicCategory("all");
        ProjectMJNI.setMeshSize(48, 32);
        ProjectMJNI.setPresetDuration(3600);
        ProjectMJNI.setSoftCutDuration(0);
        ProjectMJNI.setTransitionMode(ProjectMJNI.TRANSITION_CLASSIC, false);
        // Await asynchronous texture extraction and index construction without rendering idle frames.
        long waitStarted = SystemClock.elapsedRealtime();
        while (ProjectMJNI.getPresetCount() != 1) {
            if (SystemClock.elapsedRealtime() - waitStarted > 30_000)
                throw new IllegalStateException("Preset index did not become exactly one eligible target within 30s: "
                        + ProjectMJNI.getPresetCount());
            SystemClock.sleep(10);
        }
        manifest.put("startupIndexWaitMs", SystemClock.elapsedRealtime() - waitStarted);
        manifest.put("eligiblePresetCountBeforeFrame0", ProjectMJNI.getPresetCount());
        manifest.put("coreVersion", ProjectMJNI.getVersion());
        pausePrewarm(manifest, -1);
        manifest.put("coreSurfaceAttempted", true);
        ProjectMJNI.onSurfaceCreated();
        ProjectMJNI.onSurfaceChanged(width, height);
        checkGl("ProjectMJNI surface initialization");
        int[] framebuffer = new int[1];
        GLES30.glGetIntegerv(GLES30.GL_FRAMEBUFFER_BINDING, framebuffer, 0);
        if (framebuffer[0] != 0) throw new IllegalStateException("Surface did not leave framebuffer zero bound");
        byte[] waveform = new byte[PCM_BLOCK];
        ByteBuffer rgba = ByteBuffer.allocateDirect(width * height * 4);
        long renderStarted = SystemClock.elapsedRealtime();
        long lastPause = renderStarted;
        int nextCapture = 0;
        for (int frame = 0; frame < FRAMES; frame++) {
            if (SystemClock.elapsedRealtime() - lastPause >= 10_000) {
                pausePrewarm(manifest, frame);
                lastPause = SystemClock.elapsedRealtime();
            }
            if (instrumented) LabBridge.setFrameClock(frame / (double) FPS);
            else {
                long due = renderStarted + Math.round(frame * 1000.0 / FPS);
                long delay = due - SystemClock.elapsedRealtime();
                if (delay > 0) SystemClock.sleep(delay);
            }
            System.arraycopy(pcm, frame * PCM_BLOCK, waveform, 0, PCM_BLOCK);
            ProjectMJNI.addWaveform(waveform, waveform.length);
            GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER, 0);
            ProjectMJNI.onDrawFrame();
            checkGl("onDrawFrame " + frame);
            String actual = ProjectMJNI.getCurrentPresetName();
            if (!preset.equals(actual) || ProjectMJNI.getPresetCount() != 1
                    || ProjectMJNI.getPresetChangeCounter() != 1 || ProjectMJNI.isMusicCategoryPending()
                    || !"all".equals(ProjectMJNI.getMusicCategory()))
                throw new IllegalStateException("Exact preset/category invariant failed at frame " + frame + ": " + actual);
            GLES30.glGetIntegerv(GLES30.GL_FRAMEBUFFER_BINDING, framebuffer, 0);
            if (framebuffer[0] != 0)
                throw new IllegalStateException("Preset changed framebuffer binding at frame " + frame);
            manifest.put("framesRendered", frame + 1);
            if (nextCapture < CAPTURES.length && frame == CAPTURES[nextCapture]) {
                manifest.getJSONArray("captures").put(capture(output, frame, width, height, rgba));
                nextCapture++;
            }
        }
        checkGl("completed frame loop");
        manifest.put("renderWallDurationMs", SystemClock.elapsedRealtime() - renderStarted);
        manifest.put("verifiedPresetName", ProjectMJNI.getCurrentPresetName());
        manifest.put("presetNameChecks", FRAMES);
        manifest.put("glErrorChecks", FRAMES);
        manifest.put("presetChangeCounter", ProjectMJNI.getPresetChangeCounter());
        manifest.put("eligiblePresetCountAfterFrame479", ProjectMJNI.getPresetCount());
        if (nextCapture != CAPTURES.length) throw new IllegalStateException("Incomplete capture set");
    }

    private static JSONObject capture(File output, int frame, int width, int height,
                                      ByteBuffer rgba) throws Exception {
        rgba.clear();
        // The engine restores the draw target, but may leave its internal
        // feedback framebuffer bound for reads. Capture the presented output.
        int[] previousReadFramebuffer = new int[1];
        GLES30.glGetIntegerv(GLES30.GL_READ_FRAMEBUFFER_BINDING, previousReadFramebuffer, 0);
        GLES30.glBindFramebuffer(GLES30.GL_READ_FRAMEBUFFER, 0);
        int[] captureReadFramebuffer = new int[1];
        GLES30.glGetIntegerv(GLES30.GL_READ_FRAMEBUFFER_BINDING, captureReadFramebuffer, 0);
        if (captureReadFramebuffer[0] != 0)
            throw new IllegalStateException("Capture did not bind read framebuffer zero");
        GLES30.glPixelStorei(GLES30.GL_PACK_ALIGNMENT, 1);
        GLES30.glReadPixels(0, 0, width, height, GLES30.GL_RGBA, GLES30.GL_UNSIGNED_BYTE, rgba);
        GLES30.glBindFramebuffer(GLES30.GL_READ_FRAMEBUFFER, previousReadFramebuffer[0]);
        checkGl("glReadPixels " + frame);
        Bitmap bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
        File png = new File(output, String.format(java.util.Locale.ROOT, "frame-%03d.png", frame));
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        int[] pixels = new int[width];
        byte[] rgb = new byte[width * 3];
        long[] channelSums = new long[3];
        long blackPixels = 0;
        try {
            for (int y = 0; y < height; y++) {
                int row = (height - 1 - y) * width * 4;
                for (int x = 0; x < width; x++) {
                    int at = row + x * 4;
                    int r = rgba.get(at) & 255;
                    int g = rgba.get(at + 1) & 255;
                    int b = rgba.get(at + 2) & 255;
                    rgb[x * 3] = (byte) r;
                    rgb[x * 3 + 1] = (byte) g;
                    rgb[x * 3 + 2] = (byte) b;
                    pixels[x] = 0xff000000 | r << 16 | g << 8 | b;
                    channelSums[0] += r; channelSums[1] += g; channelSums[2] += b;
                    if (r == 0 && g == 0 && b == 0) blackPixels++;
                }
                digest.update(rgb);
                bitmap.setPixels(pixels, 0, width, 0, y, width, 1);
            }
            try (FileOutputStream stream = new FileOutputStream(png)) {
                if (!bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream))
                    throw new IllegalStateException("Lossless PNG encoding failed");
                stream.getFD().sync();
            }
        } finally { bitmap.recycle(); }
        JSONObject result = new JSONObject();
        result.put("frame", frame);
        result.put("previousReadFramebufferBinding", previousReadFramebuffer[0]);
        result.put("captureReadFramebufferBinding", captureReadFramebuffer[0]);
        result.put("simulatedSeconds", frame / (double) FPS);
        result.put("path", png.getAbsolutePath());
        result.put("width", width); result.put("height", height);
        result.put("rgbSha256", hex(digest.digest()));
        result.put("pngBytes", png.length());
        result.put("pngSha256", hex(fileSha256(png)));
        result.put("rgbMean", new JSONArray(new double[]{channelSums[0] / (double) (width * height),
                channelSums[1] / (double) (width * height), channelSums[2] / (double) (width * height)}));
        result.put("exactBlackFraction", blackPixels / (double) (width * height));
        return result;
    }

    private static void pausePrewarm(JSONObject manifest, int frame) throws Exception {
        ProjectMJNI.onMemoryPressure();
        manifest.getJSONArray("memoryPressureCalls").put(new JSONObject()
                .put("beforeFrame", frame).put("elapsedRealtimeMs", SystemClock.elapsedRealtime())
                .put("productionPauseSeconds", 20));
    }

    private static void checkGl(String operation) {
        int error = GLES30.glGetError();
        if (error != GLES30.GL_NO_ERROR)
            throw new IllegalStateException(operation + " GL error 0x" + Integer.toHexString(error));
    }

    private static JSONObject device() throws Exception {
        JSONObject result = new JSONObject();
        result.put("manufacturer", Build.MANUFACTURER); result.put("model", Build.MODEL);
        result.put("device", Build.DEVICE); result.put("fingerprint", Build.FINGERPRINT);
        result.put("sdk", Build.VERSION.SDK_INT); result.put("abis", new JSONArray(Build.SUPPORTED_ABIS));
        return result;
    }

    private static int positive(int value, String name) {
        if (value <= 0) throw new IllegalArgumentException(name + " must be positive");
        return value;
    }

    private static File privateFile(Context context, String path) throws Exception {
        if (path == null || !new File(path).isAbsolute())
            throw new IllegalArgumentException("Expected an absolute app-private path");
        File file = new File(path).getCanonicalFile();
        String root = context.getFilesDir().getCanonicalPath() + File.separator;
        if (!file.getPath().startsWith(root))
            throw new IllegalArgumentException("Path must be below app filesDir: " + path);
        return file;
    }

    private static byte[] readAll(InputStream stream) throws Exception {
        try (InputStream input = stream; ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[65536];
            int length;
            while ((length = input.read(buffer)) != -1) output.write(buffer, 0, length);
            return output.toByteArray();
        }
    }

    private static byte[] sha256(byte[] bytes) throws Exception {
        return MessageDigest.getInstance("SHA-256").digest(bytes);
    }

    private static byte[] fileSha256(File file) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        try (InputStream input = new FileInputStream(file)) {
            byte[] buffer = new byte[65536];
            int length;
            while ((length = input.read(buffer)) != -1) digest.update(buffer, 0, length);
        }
        return digest.digest();
    }

    private static String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder(bytes.length * 2);
        for (byte b : bytes) result.append(String.format(java.util.Locale.ROOT, "%02x", b & 255));
        return result.toString();
    }

    private static void writeManifest(File output, JSONObject manifest) throws Exception {
        File temporary = new File(output, "manifest.json.tmp");
        try (FileOutputStream stream = new FileOutputStream(temporary)) {
            stream.write((manifest.toString(2) + "\n").getBytes(StandardCharsets.UTF_8));
            stream.getFD().sync();
        }
        if (!temporary.renameTo(new File(output, "manifest.json")))
            throw new IllegalStateException("Atomic manifest rename failed");
    }

    private static void putFailure(JSONObject manifest, String key, Throwable failure) {
        try { manifest.put(key, failure.toString()); }
        catch (Exception ignored) { Log.e(TAG, "Cannot record failure", failure); }
    }
}
