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

    @Test public void idleBrowserPreconnectionCannotBlockAnUpload() throws Exception {
        AtomicInteger imported = new AtomicInteger();
        try (PresetPackUploadServer server = new PresetPackUploadServer(temp.newFolder(), InetAddress.getLoopbackAddress(),
                pack -> imported.incrementAndGet(), n -> {})) {
            URL url = new URL(server.url());
            try (Socket idle = new Socket(url.getHost(), url.getPort())) {
                Thread.sleep(100); // let the server accept the browser's speculative connection
                byte[] zip = zip();
                assertTrue(request(url, url.getPath(), "Content-Length: " + zip.length + "\r\n", zip).startsWith("HTTP/1.1 200"));
                assertEquals(1, imported.get());
            }
        }
    }

    @Test public void cancellationDuringReplacementPreparationPreservesOldPack() throws Exception {
        File root = temp.newFolder();
        CustomPresetPack.Pack old = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip()), () -> false, n -> {});
        CustomPresetPack.activate(root, old);
        java.util.concurrent.CountDownLatch preparing = new java.util.concurrent.CountDownLatch(1);
        AtomicInteger imported = new AtomicInteger();
        PresetPackUploadServer server = new PresetPackUploadServer(root, InetAddress.getLoopbackAddress(), new PresetPackUploadServer.Commit() {
            @Override public void prepare(CustomPresetPack.Pack pack, CustomPresetPack.Cancellation cancel) throws IOException {
                preparing.countDown();
                CustomPresetPack.awaitStatus(1, 1, request -> 0, cancel, 30000);
            }
            @Override public void imported(CustomPresetPack.Pack pack) throws IOException {
                imported.incrementAndGet();
                CustomPresetPack.activate(root, pack);
            }
        }, n -> {});
        URL url = new URL(server.url());
        Thread upload = new Thread(() -> {
            try { byte[] body = zip(); request(url, url.getPath(), "Content-Length: " + body.length + "\r\n", body); }
            catch (IOException expected) { }
        });
        upload.start();
        assertTrue(preparing.await(3, java.util.concurrent.TimeUnit.SECONDS));
        server.close();
        server.awaitStopped(3000);
        upload.join(3000);
        assertEquals(0, imported.get());
        assertEquals(old.directory, CustomPresetPack.current(root));
        assertEquals(2, root.list().length); // old generation and its pointer, no staging ZIP/directory
    }

    @Test public void prefersWifiOverAVpnAddress() throws Exception {
        java.util.List<PresetPackUploadServer.LanAddress> addresses = java.util.Arrays.asList(
                new PresetPackUploadServer.LanAddress("tun0", InetAddress.getByName("10.8.0.2"), true),
                new PresetPackUploadServer.LanAddress("wlan0", InetAddress.getByName("192.168.1.20"), false));
        assertEquals("192.168.1.20", PresetPackUploadServer.chooseAddress(addresses).getHostAddress());
    }

    @Test public void uploadBodyHasATotalDeadline() throws Exception {
        InputStream body = new PresetPackUploadServer.Body(new ByteArrayInputStream(new byte[]{1}), 1, System.nanoTime() - 1);
        try { body.read(new byte[10]); fail("expired upload accepted another byte"); }
        catch (SocketTimeoutException expected) { }
    }

    @Test public void dripFedHeadersCannotExtendTheTotalDeadline() throws Exception {
        try (PresetPackUploadServer server = new PresetPackUploadServer(temp.newFolder(), InetAddress.getLoopbackAddress(),
                pack -> {}, n -> {})) {
            URL url = new URL(server.url());
            try (Socket socket = new Socket(url.getHost(), url.getPort())) {
                socket.setSoTimeout(9000);
                Thread sender = new Thread(() -> {
                    try {
                        for (int i = 0; i < 12; i++) {
                            socket.getOutputStream().write('G');
                            socket.getOutputStream().flush();
                            Thread.sleep(750); // always below the per-read timeout
                        }
                    } catch (IOException | InterruptedException expected) { }
                });
                sender.setDaemon(true);
                sender.start();
                assertEquals(-1, socket.getInputStream().read());
                sender.join(1500);
            }
        }
    }

    @Test public void disconnectAfterCommitDoesNotReportImportFailure() throws Exception {
        File root = temp.newFolder();
        java.util.concurrent.CountDownLatch committed = new java.util.concurrent.CountDownLatch(1);
        java.util.concurrent.CountDownLatch deliver = new java.util.concurrent.CountDownLatch(1);
        java.util.concurrent.CountDownLatch finished = new java.util.concurrent.CountDownLatch(1);
        AtomicInteger failures = new AtomicInteger();
        try (PresetPackUploadServer server = new PresetPackUploadServer(root, InetAddress.getLoopbackAddress(), new PresetPackUploadServer.Commit() {
            @Override public void imported(CustomPresetPack.Pack pack) throws IOException {
                CustomPresetPack.activate(root, pack);
                committed.countDown();
                try { deliver.await(3, java.util.concurrent.TimeUnit.SECONDS); }
                catch (InterruptedException interrupted) { throw new IOException(interrupted); }
            }
            @Override public void afterResponse() { finished.countDown(); }
        }, count -> { if (count < 0) failures.incrementAndGet(); })) {
            URL url = new URL(server.url());
            Socket socket = new Socket(url.getHost(), url.getPort());
            byte[] data = zip();
            socket.getOutputStream().write(("POST " + url.getPath() + " HTTP/1.1\r\nHost: " + url.getAuthority()
                    + "\r\nContent-Length: " + data.length + "\r\n\r\n").getBytes("US-ASCII"));
            socket.getOutputStream().write(data);
            socket.getOutputStream().flush();
            assertTrue(committed.await(3, java.util.concurrent.TimeUnit.SECONDS));
            socket.setSoLinger(true, 0);
            socket.close();
            deliver.countDown();
            assertTrue(finished.await(3, java.util.concurrent.TimeUnit.SECONDS));
            assertNotNull(CustomPresetPack.current(root));
            assertEquals(0, failures.get());
        }
    }
}
