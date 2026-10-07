package com.example.projectm.visualizer;

import java.io.*;
import java.net.*;
import java.security.SecureRandom;
import java.util.*;
import java.util.concurrent.*;

/** A temporary HTTP endpoint with bounded request workers and one import at a time accepting a browser File as a length-delimited ZIP. */
final class PresetPackUploadServer implements Closeable {
    interface Commit {
        default void prepare(CustomPresetPack.Pack pack, CustomPresetPack.Cancellation cancellation) throws IOException {}
        void imported(CustomPresetPack.Pack pack) throws IOException;
        default void afterResponse() {}
        default void abandoned() {}
    }
    private final File root;
    private final Commit commit;
    private final CustomPresetPack.Progress progress;
    private final ServerSocket listener;
    private final Thread worker;
    private final ThreadPoolExecutor requests = new ThreadPoolExecutor(0, 3, 20, TimeUnit.SECONDS,
            new SynchronousQueue<>(), task -> new Thread(task, "PresetPackRequest"));
    private final Semaphore importing = new Semaphore(1);
    private final Set<Socket> clients = new HashSet<>(); // lifecycle lock
    private final String path;
    private final String url;
    private final Object lifecycle = new Object();
    private volatile boolean closed;

    PresetPackUploadServer(File root, InetAddress address, Commit commit, CustomPresetPack.Progress progress) throws IOException {
        this.root = root;
        this.commit = commit;
        this.progress = progress;
        byte[] token = new byte[16];
        new SecureRandom().nextBytes(token);
        StringBuilder hex = new StringBuilder();
        for (byte b : token) hex.append(String.format(Locale.ROOT, "%02x", b & 255));
        path = "/" + hex;
        listener = new ServerSocket(0, 2, address);
        url = "http://" + address.getHostAddress() + ":" + listener.getLocalPort() + path;
        worker = new Thread(this::serve, "PresetPackUpload");
        worker.start();
    }

    String url() { return url; }

    static InetAddress localAddress() throws SocketException {
        List<LanAddress> candidates = new ArrayList<>();
        Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();
        while (interfaces != null && interfaces.hasMoreElements()) {
            NetworkInterface network = interfaces.nextElement();
            if (!network.isUp() || network.isLoopback()) continue;
            Enumeration<InetAddress> addresses = network.getInetAddresses();
            while (addresses.hasMoreElements()) {
                InetAddress address = addresses.nextElement();
                if (address instanceof Inet4Address && address.isSiteLocalAddress())
                    candidates.add(new LanAddress(network.getName(), address, network.isPointToPoint()));
            }
        }
        return chooseAddress(candidates);
    }

    static final class LanAddress {
        final String network;
        final InetAddress address;
        final boolean pointToPoint;
        LanAddress(String network, InetAddress address, boolean pointToPoint) {
            this.network = network == null ? "" : network.toLowerCase(Locale.ROOT);
            this.address = address;
            this.pointToPoint = pointToPoint;
        }
        int priority() {
            if (pointToPoint || network.startsWith("tun") || network.startsWith("tap") || network.startsWith("utun")
                    || network.startsWith("wg") || network.startsWith("ppp") || network.startsWith("ipsec")) return 3;
            if (network.startsWith("wlan") || network.startsWith("wifi")) return 0;
            if (network.startsWith("eth") || network.startsWith("en")) return 1;
            return 2;
        }
    }

    static InetAddress chooseAddress(List<LanAddress> addresses) throws SocketException {
        LanAddress selected = null;
        for (LanAddress address : addresses)
            if (address.priority() < 3 && (selected == null || address.priority() < selected.priority())) selected = address;
        if (selected != null) return selected.address;
        throw new SocketException("Connect the TV to your local Wi-Fi or Ethernet network first");
    }

    private void serve() {
        while (!closed) {
            try {
                Socket socket = listener.accept();
                InetAddress peer = socket.getInetAddress();
                if (!peer.isLoopbackAddress() && !peer.isSiteLocalAddress()) { socket.close(); continue; }
                synchronized (lifecycle) {
                    if (closed) { socket.close(); break; }
                    clients.add(socket);
                    try {
                        requests.execute(() -> {
                            try (Socket connection = socket) {
                                connection.setSoTimeout(2000); // speculative browser connections send no headers
                                handle(connection);
                            } catch (IOException ignored) {
                                // Disconnect/cancellation does not stop other requests.
                            } finally { synchronized (lifecycle) { clients.remove(socket); } }
                        });
                    } catch (RejectedExecutionException busy) {
                        clients.remove(socket);
                        socket.close();
                    }
                }
            } catch (IOException ignored) {
                // A disconnected or canceled client must not stop the next attempt.
            }
        }
    }

    private void handle(Socket socket) throws IOException {
        InputStream input = new BufferedInputStream(socket.getInputStream());
        boolean committed = false;
        boolean uploading = false;
        try {
            int[] remainingHeaders = {8192};
            long headerDeadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
            String[] request = line(input, remainingHeaders, headerDeadline).split(" ");
            if (request.length != 3 || !request[2].equals("HTTP/1.1")) throw new IOException("Invalid HTTP request");
            Map<String, String> headers = new HashMap<>();
            for (;;) {
                String row = line(input, remainingHeaders, headerDeadline);
                if (row.isEmpty()) break;
                int colon = row.indexOf(':');
                if (colon <= 0) throw new IOException("Invalid HTTP header");
                String name = row.substring(0, colon).toLowerCase(Locale.ROOT);
                if (headers.put(name, row.substring(colon + 1).trim()) != null)
                    throw new IOException("Duplicate HTTP header");
            }
            String host = socket.getLocalAddress().getHostAddress() + ":" + listener.getLocalPort();
            if (!host.equals(headers.get("host"))) throw new IOException("Use the address shown on the TV");
            if (!path.equals(request[1])) { respond(socket, 404, "text/plain", "Upload page not found"); return; }
            if (request[0].equals("GET")) { respond(socket, 200, "text/html", page()); return; }
            if (!request[0].equals("POST")) { respond(socket, 405, "text/plain", "Use the upload page"); return; }
            if (headers.containsKey("transfer-encoding")) throw new IOException("Length-delimited ZIP required");
            String lengthHeader = headers.get("content-length");
            if (lengthHeader == null || !lengthHeader.matches("[0-9]{1,10}")) throw new IOException("ZIP length required");
            long length = Long.parseLong(lengthHeader);
            if (length <= 0 || length > CustomPresetPack.MAX_ZIP_BYTES) throw new IOException("Choose a ZIP of up to 2 GiB");
            String origin = headers.get("origin");
            if (origin != null && !origin.equals("http://" + host)) throw new IOException("Upload from this page only");
            if (!importing.tryAcquire()) { respond(socket, 409, "text/plain", "Another ZIP is being imported. Wait for it to finish."); return; }
            uploading = true;
            try {
            socket.setSoTimeout(30000);
            synchronized (CustomPresetPack.STORE_LOCK) {
                long bodyDeadline = System.nanoTime() + TimeUnit.HOURS.toNanos(1);
                CustomPresetPack.Pack pack = CustomPresetPack.prepare(root, new Body(input, length, bodyDeadline), () -> closed, progress);
                try {
                    commit.prepare(pack, () -> closed);
                    synchronized (lifecycle) {
                        if (closed) throw new IOException("Upload canceled");
                        commit.imported(pack);
                        committed = true;
                    }
                    respond(socket, 200, "text/plain", "Imported " + pack.count + " presets and " + pack.textureCount
                            + " textures. Custom is now selected on the TV.");
                } finally {
                    if (!committed) { commit.abandoned(); CustomPresetPack.delete(pack.directory); }
                    else commit.afterResponse();
                }
            }
            } finally { importing.release(); }
        } catch (SocketTimeoutException idle) {
            // Close idle speculative sockets silently so browsers can reconnect, rather than
            // mistaking a timeout response for the response to a subsequent real upload.
            if (uploading && !committed && !closed) progress.updated(-1);
        } catch (IOException | IllegalArgumentException failure) {
            if (committed) return; // response delivery cannot undo or mislabel a committed import
            if (!closed) progress.updated(-1);
            respond(socket, 400, "text/plain", failure.getMessage() == null ? "Cannot import this ZIP" : failure.getMessage());
        }
    }

    private static void checkDeadline(long deadline) throws SocketTimeoutException {
        if (System.nanoTime() >= deadline) throw new SocketTimeoutException("Upload timed out");
    }

    private static String line(InputStream input, int[] remaining, long deadline) throws IOException {
        StringBuilder text = new StringBuilder();
        for (;;) {
            if (--remaining[0] < 0) throw new IOException("HTTP headers too large");
            checkDeadline(deadline);
            int b = input.read();
            checkDeadline(deadline);
            if (b == -1) throw new EOFException("Incomplete request");
            if (b == '\r') {
                if (--remaining[0] < 0 || input.read() != '\n') throw new IOException("Invalid HTTP line");
                return text.toString();
            }
            if (b < 32 || b > 126) throw new IOException("Invalid HTTP header character");
            text.append((char)b);
        }
    }

    static final class Body extends InputStream {
        private final InputStream input;
        private long remaining;
        private final long deadline;
        Body(InputStream input, long remaining, long deadline) { this.input = input; this.remaining = remaining; this.deadline = deadline; }
        @Override public int read() throws IOException {
            byte[] one = new byte[1];
            return read(one, 0, 1) == -1 ? -1 : one[0] & 255;
        }
        @Override public int read(byte[] bytes, int offset, int length) throws IOException {
            if (remaining == 0) return -1;
            checkDeadline(deadline);
            int n = input.read(bytes, offset, (int)Math.min(remaining, length));
            checkDeadline(deadline);
            if (n == -1) throw new EOFException("Upload ended before the whole ZIP arrived");
            remaining -= n;
            return n;
        }
    }

    private static void respond(Socket socket, int status, String type, String text) throws IOException {
        byte[] body = text.getBytes("UTF-8");
        String reason = status == 200 ? "OK" : status == 404 ? "Not Found" : status == 405 ? "Method Not Allowed"
                : status == 409 ? "Conflict" : "Bad Request";
        OutputStream out = socket.getOutputStream();
        out.write(("HTTP/1.1 " + status + " " + reason + "\r\nContent-Type: " + type
                + "; charset=utf-8\r\nContent-Length: " + body.length + "\r\nConnection: close"
                + "\r\nCache-Control: no-store\r\nReferrer-Policy: no-referrer"
                + "\r\nContent-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'"
                + "\r\nX-Content-Type-Options: nosniff\r\n\r\n").getBytes("US-ASCII"));
        out.write(body);
        out.flush();
    }

    private static String page() {
        return "<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
                + "<title>ProjectM TV · Custom presets</title><style>"
                + "body{margin:0;background:#121212;color:#fafafa;font:18px system-ui,sans-serif;line-height:1.5}"
                + "main{max-width:36rem;margin:6vh auto;padding:24px}h1{font-size:32px;line-height:1.2}"
                + "label{display:block;margin:24px 0 10px;font-weight:600}input{display:block;max-width:100%;margin-bottom:24px}"
                + "button{background:#fafafa;color:#121212;border:0;border-radius:4px;padding:12px 20px;font:inherit;cursor:pointer}"
                + "button:disabled{opacity:.5}button:focus-visible,input:focus-visible{outline:3px solid #5ad4ff;outline-offset:4px}"
                + "progress{width:100%;margin-top:24px}small{color:#bbb}#status{min-height:3em}</style>"
                + "<main><small>ProjectM TV</small><h1>Upload preset pack</h1>"
                + "<p>Choose one ZIP with up to 50,000 MilkDrop presets and their textures. PNG, JPG, JPEG, TGA, BMP, DIB and DDS images are imported. Other files are ignored.</p>"
                + "<p>This replaces your previous custom pack and selects <strong>Custom</strong> on the TV. A failed upload keeps your previous pack.</p>"
                + "<form id='form'><label for='zip'>Preset ZIP</label><input id='zip' type='file' accept='.zip,application/zip' required>"
                + "<button id='upload'>Upload ZIP</button></form><progress id='progress' hidden></progress>"
                + "<p id='status' role='status' aria-live='polite'></p>"
                + "<small>Keep the TV upload dialog open. Limits: 2 GiB ZIP, 4 GiB combined presets/textures, 8 MiB per preset, 64 MiB per texture, 5,000 textures. Use your trusted local network.</small></main>"
                + "<script>const form=document.getElementById('form'),file=document.getElementById('zip'),button=document.getElementById('upload'),"
                + "status=document.getElementById('status'),progress=document.getElementById('progress');"
                + "form.onsubmit=e=>{e.preventDefault();const zip=file.files[0];if(!zip)return;"
                + "if(zip.size>2147483648){status.textContent='Choose a ZIP of up to 2 GiB.';return;}"
                + "button.disabled=true;file.disabled=true;progress.hidden=false;progress.removeAttribute('value');status.textContent='Uploading…';"
                + "const req=new XMLHttpRequest();req.open('POST',location.pathname);req.setRequestHeader('Content-Type','application/zip');"
                + "req.upload.onprogress=e=>{if(e.lengthComputable){progress.max=e.total;progress.value=e.loaded;"
                + "status.textContent=e.loaded===e.total?'Importing presets…':'Uploading '+Math.round(e.loaded/e.total*100)+'%';}};"
                + "const done=()=>{button.disabled=false;file.disabled=false;progress.hidden=true;};"
                + "req.onload=()=>{status.textContent=req.responseText;done();};req.onerror=()=>{status.textContent='Connection lost. Check the TV, then reopen its upload address.';done();};req.send(zip);};</script></html>";
    }

    @Override public void close() {
        synchronized (lifecycle) {
            closed = true;
            try { listener.close(); } catch (IOException ignored) {}
            for (Socket socket : clients) try { socket.close(); } catch (IOException ignored) {}
            requests.shutdownNow();
        }
    }

    void awaitStopped(long milliseconds) throws InterruptedException {
        worker.join(milliseconds);
        if (worker.isAlive() || !requests.awaitTermination(milliseconds, TimeUnit.MILLISECONDS))
            throw new IllegalStateException("Upload workers did not stop");
    }
}
