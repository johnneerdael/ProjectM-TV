package com.example.projectm.visualizer;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;
import java.io.*;
import java.net.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.zip.*;
import static org.junit.Assert.*;

public class PresetPackUploadServerTest {
    @Rule public TemporaryFolder temp = new TemporaryFolder();

    private byte[] zip() throws IOException {
        ByteArrayOutputStream data = new ByteArrayOutputStream();
        try (ZipOutputStream out = new ZipOutputStream(data)) {
            out.putNextEntry(new ZipEntry("nested/a.milk"));
            out.write("[preset00]\nfRating=3\n".getBytes("UTF-8"));
            out.closeEntry();
        }
        return data.toByteArray();
    }

    private String request(URL url, String path, String headers, byte[] body) throws IOException {
        try (Socket socket = new Socket(url.getHost(), url.getPort())) {
            socket.setSoTimeout(10000);
            OutputStream out = socket.getOutputStream();
            out.write(("POST " + path + " HTTP/1.1\r\nHost: " + url.getAuthority() + "\r\n" + headers + "\r\n").getBytes("US-ASCII"));
            out.write(body);
            out.flush();
            socket.shutdownOutput();
            ByteArrayOutputStream response = new ByteArrayOutputStream();
            byte[] buffer = new byte[2048]; int n;
            while ((n = socket.getInputStream().read(buffer)) != -1) response.write(buffer, 0, n);
            return response.toString("UTF-8");
        }
    }

    @Test public void acceptsRawBrowserZipAndCallsCommitOnce() throws Exception {
        File root = temp.newFolder();
        AtomicInteger imported = new AtomicInteger();
        try (PresetPackUploadServer server = new PresetPackUploadServer(root, InetAddress.getLoopbackAddress(),
                pack -> { CustomPresetPack.activate(root, pack); imported.addAndGet(pack.count); }, n -> {})) {
            URL url = new URL(server.url());
            String page;
            try (InputStream in = url.openStream()) {
                ByteArrayOutputStream bytes = new ByteArrayOutputStream(); byte[] buffer = new byte[4096]; int n;
                while ((n = in.read(buffer)) != -1) bytes.write(buffer, 0, n);
                page = bytes.toString("UTF-8");
            }
            assertTrue(page.contains("Upload preset pack"));
            byte[] zip = zip();
            assertTrue(request(url, url.getPath(), "Content-Length: " + zip.length + "\r\n", zip).startsWith("HTTP/1.1 200"));
            assertEquals(1, imported.get());
            assertNotNull(CustomPresetPack.current(root));
        }
    }

    @Test public void rejectsMissingTokenChunkedAndDuplicateLengthsWithoutImporting() throws Exception {
        AtomicInteger imported = new AtomicInteger();
        try (PresetPackUploadServer server = new PresetPackUploadServer(temp.newFolder(), InetAddress.getLoopbackAddress(),
                pack -> imported.incrementAndGet(), n -> {})) {
            URL url = new URL(server.url());
            byte[] zip = zip();
            assertTrue(request(url, "/", "Content-Length: " + zip.length + "\r\n", zip).startsWith("HTTP/1.1 404"));
            assertTrue(request(url, url.getPath(), "Transfer-Encoding: chunked\r\n", new byte[0]).startsWith("HTTP/1.1 400"));
            assertTrue(request(url, url.getPath(), "Content-Length: 10\r\nContent-Length: 10\r\n", new byte[0]).startsWith("HTTP/1.1 400"));
            assertEquals(0, imported.get());
        }
    }

    @Test public void truncatedUploadDoesNotReplaceExistingPack() throws Exception {
        File root = temp.newFolder();
        CustomPresetPack.Pack old = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip()), () -> false, n -> {});
        CustomPresetPack.activate(root, old);
        try (PresetPackUploadServer server = new PresetPackUploadServer(root, InetAddress.getLoopbackAddress(),
                pack -> CustomPresetPack.activate(root, pack), n -> {})) {
            URL url = new URL(server.url());
            assertTrue(request(url, url.getPath(), "Content-Length: 1000\r\n", new byte[]{1,2}).startsWith("HTTP/1.1 400"));
            assertEquals(old.directory, CustomPresetPack.current(root));
        }
    }

    @Test public void closingListenerStopsAnIncompleteUpload() throws Exception {
        File root = temp.newFolder();
        AtomicInteger imported = new AtomicInteger();
        PresetPackUploadServer server = new PresetPackUploadServer(root, InetAddress.getLoopbackAddress(),
                pack -> imported.incrementAndGet(), n -> {});
        URL url = new URL(server.url());
        try (Socket socket = new Socket(url.getHost(), url.getPort())) {
            socket.getOutputStream().write(("POST " + url.getPath() + " HTTP/1.1\r\nHost: " + url.getAuthority()
                    + "\r\nContent-Length: 1000\r\n\r\n").getBytes("US-ASCII"));
            Thread.sleep(100);
            server.close();
            server.awaitStopped(3000);
            assertEquals(0, imported.get());
            assertEquals(0, root.list().length);
        }
    }
}
