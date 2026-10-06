package nl.neerdael.projectmtv.corpus;

import android.opengl.GLES30;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/** Private test readback only. Stores hashes, with one reusable RGBA row and RGB row. */
final class EveryFrameHashes implements AutoCloseable {
    private final FileOutputStream stream;
    private final int width, height;
    private final byte[] rgbaRow, rgbRow;
    private final MessageDigest digest;

    EveryFrameHashes(File file, int width, int height) throws Exception {
        this.width = width;
        this.height = height;
        stream = new FileOutputStream(file);
        rgbaRow = new byte[width * 4];
        rgbRow = new byte[width * 3];
        digest = MessageDigest.getInstance("SHA-256");
    }

    void writeFrame(int frame, ByteBuffer rgba) throws Exception {
        rgba.clear();
        GLES30.glPixelStorei(GLES30.GL_PACK_ALIGNMENT, 1);
        // RGBA/UNSIGNED_BYTE is the GLES readback contract; RGB readback is not portable.
        GLES30.glReadPixels(0, 0, width, height, GLES30.GL_RGBA, GLES30.GL_UNSIGNED_BYTE, rgba);
        int error = GLES30.glGetError();
        if (error != GLES30.GL_NO_ERROR) throw new IllegalStateException("Frame hash readback GL error " + error);
        digest.reset();
        for (int y = height - 1; y >= 0; --y) {
            rgba.position(y * width * 4);
            rgba.get(rgbaRow);
            for (int x = 0, source = 0, target = 0; x < width; ++x, source += 4) {
                rgbRow[target++] = rgbaRow[source];
                rgbRow[target++] = rgbaRow[source + 1];
                rgbRow[target++] = rgbaRow[source + 2];
            }
            digest.update(rgbRow);
        }
        String row = "{\"frame\":" + frame + ",\"width\":" + width + ",\"height\":" + height
                + ",\"rgbSha256\":\"" + hex(digest.digest()) + "\"}\n";
        stream.write(row.getBytes(StandardCharsets.US_ASCII));
    }

    static int[] captures(JSONObject job, int frameLimit) throws Exception {
        JSONArray requested = job.optJSONArray("captureFrames");
        if (requested == null) return new int[0];
        if (requested.length() > 2) throw new IllegalArgumentException("At most two diagnostic frame captures");
        int[] result = new int[requested.length()];
        for (int i = 0; i < result.length; ++i) {
            result[i] = requested.getInt(i);
            if (result[i] < 0 || result[i] >= frameLimit || (i > 0 && result[i] <= result[i - 1]))
                throw new IllegalArgumentException("Capture frames must be ordered, unique and in range");
        }
        return result;
    }

    private static String hex(byte[] bytes) {
        char[] characters = new char[bytes.length * 2];
        final char[] digits = "0123456789abcdef".toCharArray();
        for (int i = 0; i < bytes.length; ++i) {
            characters[i * 2] = digits[(bytes[i] & 255) >>> 4];
            characters[i * 2 + 1] = digits[bytes[i] & 15];
        }
        return new String(characters);
    }

    @Override public void close() throws Exception {
        stream.flush();
        stream.getFD().sync();
        stream.close();
    }
}
