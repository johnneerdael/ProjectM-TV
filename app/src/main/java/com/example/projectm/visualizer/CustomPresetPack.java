package com.example.projectm.visualizer;

import java.io.*;
import java.util.*;
import java.util.zip.*;

/** ZIP staging and an atomic active-pack pointer. Call only from a background worker. */
final class CustomPresetPack {
    static final Object STORE_LOCK = new Object();
    static final long MAX_ZIP_BYTES = 2L * 1024 * 1024 * 1024;
    private static final long MAX_PRESET_BYTES = 8L * 1024 * 1024;
    private static final long MAX_EXPANDED_BYTES = 4L * 1024 * 1024 * 1024;
    interface Cancellation { boolean canceled(); }
    interface Progress { void updated(int presets); }

    static final class Pack {
        final File directory;
        final int count;
        Pack(File directory, int count) { this.directory = directory; this.count = count; }
    }

    static Pack prepare(File root, InputStream input, Cancellation cancellation, Progress progress) throws IOException {
        if (!root.isDirectory() && !root.mkdirs()) throw new IOException("Cannot create pack storage");
        File archive = new File(root, "incoming.zip");
        File directory = new File(root, UUID.randomUUID().toString());
        boolean success = false;
        byte[] buffer = new byte[32768];
        try {
            try (FileOutputStream out = new FileOutputStream(archive)) {
                long length = 0;
                int n;
                while ((n = input.read(buffer)) != -1) {
                    checkCanceled(cancellation);
                    length += n;
                    if (length > MAX_ZIP_BYTES) throw new IOException("ZIP exceeds 2 GiB");
                    out.write(buffer, 0, n);
                }
            }
            checkCanceled(cancellation);
            try (ZipFile zip = new ZipFile(archive)) {
                ArrayList<ZipEntry> presets = new ArrayList<>();
                HashSet<String> names = new HashSet<>();
                Enumeration<? extends ZipEntry> entries = zip.entries();
                int entryCount = 0;
                while (entries.hasMoreElements()) {
                    checkCanceled(cancellation);
                    if (++entryCount > 250000) throw new IOException("ZIP contains too many entries");
                    ZipEntry entry = entries.nextElement();
                    String name = entry.getName();
                    // ZipFile skips the compressed data of ignored entries, including textures.
                    if (entry.isDirectory() || !name.toLowerCase(Locale.ROOT).endsWith(".milk")) continue;
                    if (!safeName(name) || !names.add(name)) throw new IOException("Invalid or duplicate preset name");
                    presets.add(entry);
                    if (presets.size() > 50000) throw new IOException("A pack may contain up to 50,000 presets");
                    if (entry.getSize() > MAX_PRESET_BYTES) throw new IOException("A preset exceeds 8 MiB");
                }
                if (presets.isEmpty()) throw new IOException("No .milk presets found in the ZIP");
                if (!directory.mkdir()) throw new IOException("Cannot create pack directory");
                long expanded = 0;
                try (Writer index = new BufferedWriter(new OutputStreamWriter(
                        new FileOutputStream(new File(directory, "presets.idx")), "UTF-8"))) {
                    for (int i = 0; i < presets.size(); i++) {
                        checkCanceled(cancellation);
                        ZipEntry entry = presets.get(i);
                        // Generated storage names avoid ZIP paths, filename limits and basename collisions.
                        String storage = (i / 1000) + "/" + i + ".milk";
                        File target = new File(directory, storage);
                        File parent = target.getParentFile();
                        if (!parent.isDirectory() && !parent.mkdir()) throw new IOException("Cannot create preset directory");
                        CRC32 crc = new CRC32();
                        long size = 0;
                        try (InputStream in = zip.getInputStream(entry);
                             OutputStream out = new BufferedOutputStream(new FileOutputStream(target))) {
                            int n;
                            while ((n = in.read(buffer)) != -1) {
                                checkCanceled(cancellation);
                                size += n;
                                expanded += n;
                                if (size > MAX_PRESET_BYTES || expanded > MAX_EXPANDED_BYTES)
                                    throw new IOException("Pack exceeds the 8 MiB preset or 4 GiB expanded limit");
                                crc.update(buffer, 0, n);
                                out.write(buffer, 0, n);
                            }
                        }
                        if (size != entry.getSize() || crc.getValue() != entry.getCrc())
                            throw new IOException("Corrupt preset in ZIP");
                        index.write(storage + "\t" + entry.getName() + "\n");
                        if ((i + 1) % 500 == 0 || i + 1 == presets.size()) progress.updated(i + 1);
                    }
                }
                checkCanceled(cancellation);
                success = true;
                return new Pack(directory, presets.size());
            }
        } finally {
            archive.delete();
            if (!success) delete(directory);
        }
    }

    private static boolean safeName(String name) throws UnsupportedEncodingException {
        if (name.startsWith("/") || name.contains("\\") || name.getBytes("UTF-8").length > 1024) return false;
        for (int i = 0; i < name.length(); i++) if (Character.isISOControl(name.charAt(i))) return false;
        for (String part : name.split("/", -1))
            if (part.isEmpty() || part.equals(".") || part.equals("..")) return false;
        return true;
    }

    private static void checkCanceled(Cancellation cancellation) throws IOException {
        if (cancellation.canceled()) throw new IOException("Upload canceled");
    }

    static void activate(File root, Pack pack) throws IOException {
        File temp = new File(root, "current.tmp");
        try (FileOutputStream out = new FileOutputStream(temp)) {
            out.write(pack.directory.getName().getBytes("UTF-8"));
            out.getFD().sync();
        }
        if (!temp.renameTo(new File(root, "current"))) throw new IOException("Cannot save the active pack");
    }

    static File current(File root) {
        try (BufferedReader in = new BufferedReader(new InputStreamReader(
                new FileInputStream(new File(root, "current")), "UTF-8"))) {
            String id = in.readLine();
            if (id == null || !id.matches("[a-f0-9-]{36}")) return null;
            File directory = new File(root, id);
            return new File(directory, "presets.idx").isFile() ? directory : null;
        } catch (IOException ignored) { return null; }
    }

    /** After the engine has switched its index, old readers may fail harmlessly or finish an open file. */
    static void cleanUnused(File root, File active) {
        File[] children = root.listFiles();
        if (children == null) return;
        for (File child : children)
            if (child.isDirectory() && !child.equals(active)) delete(child);
    }

    static void delete(File file) {
        File[] children = file.listFiles();
        if (children != null) for (File child : children) delete(child);
        file.delete();
    }

    private CustomPresetPack() {}
}
