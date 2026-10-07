package com.example.projectm.visualizer;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;
import java.io.*;
import java.nio.file.Files;
import java.util.Base64;
import java.util.zip.*;
import static org.junit.Assert.*;

public class CustomPresetPackTest {
    @Rule public TemporaryFolder temp = new TemporaryFolder();
    // A valid 1x1 PNG. Native SOIL decoding remains the renderer's responsibility.
    private static final byte[] IMAGE = Base64.getDecoder().decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=");

    private byte[] zip(String... names) throws IOException {
        return zipWithTextureData(IMAGE, names);
    }

    private byte[] zipWithTextureData(byte[] image, String... names) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (ZipOutputStream zip = new ZipOutputStream(bytes)) {
            for (String name : names) {
                zip.putNextEntry(new ZipEntry(name));
                zip.write(name.toLowerCase(java.util.Locale.ROOT).endsWith(".milk")
                        ? "[preset00]\nfRating=3\n".getBytes("UTF-8") : image);
                zip.closeEntry();
            }
        }
        return bytes.toByteArray();
    }

    @Test public void importsNestedMilkAndTexturesButIgnoresUnsupportedFiles() throws Exception {
        File root = temp.newFolder();
        CustomPresetPack.Pack pack = CustomPresetPack.prepare(root, new ByteArrayInputStream(
                zip("one/test.milk", "two/test.MILK", "readme.txt", "textures/a.png")), () -> false, n -> {});
        assertEquals(2, pack.count);
        assertNull(CustomPresetPack.current(root));
        CustomPresetPack.activate(root, pack);
        assertEquals(pack.directory, CustomPresetPack.current(root));
        String index = new String(Files.readAllBytes(new File(pack.directory, "presets.idx").toPath()), "UTF-8");
        assertTrue(index.contains("\tone/test.milk\n"));
        assertTrue(index.contains("\ttwo/test.MILK\n"));
        assertFalse(index.contains("readme"));
        assertEquals(2, index.split("\n").length);
        assertArrayEquals(IMAGE, Files.readAllBytes(new File(pack.directory, "textures/a.png").toPath()));
        assertFalse(new File(pack.directory, "readme.txt").exists());
    }

    @Test public void preservesTextureBasenamesAndBytesForEveryNativeExtension() throws Exception {
        File root = temp.newFolder();
        // Content sniffing/decoding is native; this test exercises the import extension allowlist.
        CustomPresetPack.Pack pack = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip(
                "test.milk", "one/A.JPG", "two/B.jpeg", "C.png", "D.tga", "E.bmp", "F.dib", "G.dds",
                "ignored.gif", "ignored.svg")), () -> false, n -> {});
        File textures = new File(pack.directory, "textures");
        assertEquals(7, pack.textureCount);
        assertEquals(7, textures.list().length);
        for (String name : new String[]{"A.JPG", "B.jpeg", "C.png", "D.tga", "E.bmp", "F.dib", "G.dds"})
            assertArrayEquals(IMAGE, Files.readAllBytes(new File(textures, name).toPath()));
    }

    private void rejectsKeepingActivePack(byte[] bytes, String message) throws Exception {
        File root = temp.newFolder();
        CustomPresetPack.Pack old = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("old.milk")), () -> false, n -> {});
        CustomPresetPack.activate(root, old);
        try {
            CustomPresetPack.prepare(root, new ByteArrayInputStream(bytes), () -> false, n -> {});
            fail("invalid texture pack accepted");
        } catch (IOException expected) {
            assertTrue(expected.getMessage(), expected.getMessage().contains(message));
        }
        assertEquals(old.directory, CustomPresetPack.current(root));
        assertEquals(2, root.list().length); // active generation and pointer only
    }

    @Test public void rejectsAmbiguousCaseInsensitiveTextureStems() throws Exception {
        for (String other : new String[]{"two/foo.png", "two/FOO.jpg", "Foo.jpeg"})
            rejectsKeepingActivePack(zip("test.milk", "one/Foo.png", other), "texture name");
    }

    @Test public void rejectsUnsafeTexturePathsAndUnrepresentableBasenames() throws Exception {
        for (String name : new String[]{"../escape.png", "/escape.png", "a\\escape.png", "a\n.png",
                "a/./escape.png", "a//escape.png", "C:/escape.png", ".png", new String(new char[252]).replace('\0', 'a') + ".png"})
            rejectsKeepingActivePack(zip("test.milk", name), "texture name");
    }

    @Test public void acceptsFiveThousandTexturesAndRejectsTheNext() throws Exception {
        String[] names = new String[5002];
        names[0] = "test.milk";
        for (int i = 1; i < names.length; i++) names[i] = "textures/texture" + i + ".png";
        File root = temp.newFolder();
        CustomPresetPack.Pack pack = CustomPresetPack.prepare(root, new ByteArrayInputStream(
                zip(java.util.Arrays.copyOf(names, 5001))), () -> false, n -> {});
        assertEquals(5000, new File(pack.directory, "textures").list().length);
        rejectsKeepingActivePack(zip(names), "5,000");
    }

    private static void centralField(byte[] bytes, int entry, int field, long value) {
        int seen = 0;
        for (int i = 0; i <= bytes.length - 46; i++) {
            if (bytes[i] == 0x50 && bytes[i + 1] == 0x4b && bytes[i + 2] == 1 && bytes[i + 3] == 2) {
                if (seen++ == entry) {
                    for (int n = 0; n < 4; n++) bytes[i + field + n] = (byte) (value >>> (8 * n));
                    return;
                }
            }
        }
        throw new AssertionError("Missing central directory entry");
    }

    @Test public void rejectsOversizedTextureAndCountsImagesInExpandedLimit() throws Exception {
        byte[] oversized = zip("test.milk", "oversized.png");
        centralField(oversized, 1, 24, 64L * 1024 * 1024 + 1);
        rejectsKeepingActivePack(oversized, "64 MiB");
        String[] names = new String[66];
        names[0] = "test.milk";
        for (int i = 1; i < names.length; i++) names[i] = i + ".png";
        byte[] total = zip(names);
        for (int i = 1; i < names.length; i++) centralField(total, i, 24, 64L * 1024 * 1024);
        rejectsKeepingActivePack(total, "4 GiB");
    }

    @Test public void acceptsExactlySixtyFourMiBAndBoundsActualTextureExpansion() throws Exception {
        for (int extra : new int[]{0, 1}) {
            File root = temp.newFolder();
            File archive = temp.newFile();
            try (ZipOutputStream out = new ZipOutputStream(new FileOutputStream(archive))) {
                out.putNextEntry(new ZipEntry("test.milk"));
                out.write("[preset00]\nfRating=3\n".getBytes("UTF-8"));
                out.closeEntry();
                out.putNextEntry(new ZipEntry("image.png"));
                out.write(IMAGE);
                byte[] padding = new byte[1024 * 1024];
                long remaining = 64L * 1024 * 1024 + extra - IMAGE.length;
                while (remaining > 0) {
                    int n = (int) Math.min(remaining, padding.length);
                    out.write(padding, 0, n);
                    remaining -= n;
                }
                out.closeEntry();
            }
            byte[] bytes = Files.readAllBytes(archive.toPath());
            if (extra == 1) {
                // A dishonest declared size must not bypass the streaming expansion bound.
                centralField(bytes, 1, 24, 1);
                rejectsKeepingActivePack(bytes, "file size limit");
            } else {
                CustomPresetPack.Pack pack = CustomPresetPack.prepare(root, new ByteArrayInputStream(bytes), () -> false, n -> {});
                assertEquals(64L * 1024 * 1024, new File(pack.directory, "textures/image.png").length());
            }
        }
    }

    @Test public void rejectsCorruptTextureCrcOrSize() throws Exception {
        for (int field : new int[]{16, 24}) {
            byte[] bytes = zip("test.milk", "bad.png");
            centralField(bytes, 1, field, 1);
            rejectsKeepingActivePack(bytes, "Corrupt");
        }
    }

    @Test public void materializesZipLinkMetadataAsRegularFilesWithoutFollowingTargets() throws Exception {
        byte[] targetName = "../../outside.png".getBytes("UTF-8");
        byte[] bytes = zipWithTextureData(targetName, "test.milk", "link.png");
        centralField(bytes, 1, 4, 0x0314); // ZIP made by Unix
        centralField(bytes, 1, 38, 0120777L << 16);
        File root = temp.newFolder();
        CustomPresetPack.Pack pack = CustomPresetPack.prepare(root, new ByteArrayInputStream(bytes), () -> false, n -> {});
        File image = new File(pack.directory, "textures/link.png");
        assertFalse(Files.isSymbolicLink(image.toPath()));
        assertArrayEquals(targetName, Files.readAllBytes(image.toPath()));
        assertFalse(new File(root, "outside.png").exists());
    }

    @Test public void cancellationDuringTextureExtractionKeepsTheActiveGeneration() throws Exception {
        File root = temp.newFolder();
        CustomPresetPack.Pack old = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("old.milk", "old.png")), () -> false, n -> {});
        CustomPresetPack.activate(root, old);
        try {
            CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("new.milk", "new.png")),
                    () -> {
                        for (File child : root.listFiles())
                            if (new File(child, "textures/new.png").isFile()) return true;
                        return false;
                    }, n -> {});
            fail("canceled import succeeded");
        } catch (IOException expected) {
            assertEquals(old.directory, CustomPresetPack.current(root));
            assertArrayEquals(IMAGE, Files.readAllBytes(new File(old.directory, "textures/old.png").toPath()));
            assertEquals(2, root.list().length);
        }
    }

    @Test public void keepsTextureFilesWithinTheirImmutablePackGeneration() throws Exception {
        File root = temp.newFolder();
        CustomPresetPack.Pack old = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("old.milk", "same.png")), () -> false, n -> {});
        CustomPresetPack.activate(root, old);
        byte[] black = Base64.getDecoder().decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNg+A8AAQIBAEK+vGgAAAAASUVORK5CYII=");
        CustomPresetPack.Pack next = CustomPresetPack.prepare(root, new ByteArrayInputStream(
                zipWithTextureData(black, "new.milk", "same.png")), () -> false, n -> {});
        assertNotEquals(old.directory, next.directory);
        assertEquals(old.directory, CustomPresetPack.current(root));
        assertArrayEquals(IMAGE, Files.readAllBytes(new File(old.directory, "textures/same.png").toPath()));
        assertArrayEquals(black, Files.readAllBytes(new File(next.directory, "textures/same.png").toPath()));
        CustomPresetPack.activate(root, next);
        CustomPresetPack.restore(root, old.directory);
        assertEquals(old.directory, CustomPresetPack.current(root));
    }

    private static long littleInt(byte[] bytes, int offset) {
        long value = 0;
        for (int i = 0; i < 4; i++) value |= (bytes[offset + i] & 255L) << (8 * i);
        return value;
    }

    private static void littleLong(byte[] bytes, int offset, long value) {
        for (int i = 0; i < 8; i++) bytes[offset + i] = (byte) (value >>> (8 * i));
    }

    @Test public void importsExplicitZip64CentralDirectoryOffsets() throws Exception {
        byte[] original = zip("test.milk", "nested/image.png");
        int end = original.length - 22;
        byte[] bytes = new byte[original.length + 76];
        System.arraycopy(original, 0, bytes, 0, end);
        System.arraycopy(original, end, bytes, end + 76, 22);
        littleLong(bytes, end, 0x06064b50L);
        littleLong(bytes, end + 4, 44);
        bytes[end + 12] = 45;
        bytes[end + 14] = 45;
        littleLong(bytes, end + 24, 2);
        littleLong(bytes, end + 32, 2);
        littleLong(bytes, end + 40, littleInt(original, end + 12));
        littleLong(bytes, end + 48, littleInt(original, end + 16));
        littleLong(bytes, end + 56, 0x07064b50L);
        littleLong(bytes, end + 64, end);
        bytes[end + 72] = 1; // total disks
        for (int i = 0; i < 4; i++) bytes[end + 76 + 16 + i] = (byte) 0xff;
        File root = temp.newFolder();
        CustomPresetPack.Pack pack = CustomPresetPack.prepare(root, new ByteArrayInputStream(bytes), () -> false, n -> {});
        assertEquals(1, pack.textureCount);
        assertArrayEquals(IMAGE, Files.readAllBytes(new File(pack.directory, "textures/image.png").toPath()));
    }

    @Test public void supportsExactlyFiftyThousandPresets() throws Exception {
        File root = temp.newFolder();
        File archive = temp.newFile();
        try (ZipOutputStream out = new ZipOutputStream(new FileOutputStream(archive))) {
            for (int i = 0; i < 50000; i++) {
                out.putNextEntry(new ZipEntry("nested/preset-" + i + ".milk"));
                out.write("[preset00]\nfRating=3\n".getBytes("UTF-8"));
                out.closeEntry();
            }
            out.putNextEntry(new ZipEntry("nested/image.png"));
            out.write(IMAGE);
            out.closeEntry();
        }
        try (InputStream in = new FileInputStream(archive)) {
            CustomPresetPack.Pack pack = CustomPresetPack.prepare(root, in, () -> false, n -> {});
            assertEquals(50000, pack.count);
            assertEquals(1, pack.textureCount);
            assertEquals(50000, Files.readAllLines(new File(pack.directory, "presets.idx").toPath()).size());
        }
    }

    @Test public void rejectsTooManyPresetsWithoutChangingCurrentPack() throws Exception {
        File root = temp.newFolder();
        CustomPresetPack.Pack old = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("old.milk")), () -> false, n -> {});
        CustomPresetPack.activate(root, old);
        File archive = temp.newFile();
        try (ZipOutputStream out = new ZipOutputStream(new FileOutputStream(archive))) {
            for (int i = 0; i <= 50000; i++) {
                out.putNextEntry(new ZipEntry(i + ".milk"));
                out.closeEntry();
            }
        }
        try (InputStream in = new FileInputStream(archive)) {
            try {
                CustomPresetPack.prepare(root, in, () -> false, n -> {});
                fail("too many presets accepted");
            } catch (IOException expected) {
                assertTrue(expected.getMessage().contains("50,000"));
            }
        }
        assertEquals(old.directory, CustomPresetPack.current(root));
    }

    @Test public void cancellationLeavesNoStagingPack() throws Exception {
        File root = temp.newFolder();
        try {
            CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("a.milk")), () -> true, n -> {});
            fail("canceled import succeeded");
        } catch (IOException expected) {
            assertEquals(0, root.list().length);
        }
    }

    @Test public void rejectsEmptyAndInvalidArchives() throws Exception {
        for (byte[] data : new byte[][]{zip("readme.txt"), "not a zip".getBytes("UTF-8")}) {
            File root = temp.newFolder();
            try {
                CustomPresetPack.prepare(root, new ByteArrayInputStream(data), () -> false, n -> {});
                fail("invalid pack accepted");
            } catch (IOException expected) {
                assertEquals(0, root.list().length);
            }
        }
    }

    @Test public void rejectsUnsafeMilkNamesWithoutExtractingThem() throws Exception {
        for (String name : new String[]{"../escape.milk", "/escape.milk", "a\\escape.milk", "a\n.milk"}) {
            File root = temp.newFolder();
            try {
                CustomPresetPack.prepare(root, new ByteArrayInputStream(zip(name)), () -> false, n -> {});
                fail("unsafe path accepted: " + name);
            } catch (IOException expected) {
                assertEquals(0, root.list().length);
            }
        }
    }

    @Test public void replacingPackKeepsOnlyOneActiveGeneration() throws Exception {
        File root = temp.newFolder();
        CustomPresetPack.Pack old = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("old.milk")), () -> false, n -> {});
        CustomPresetPack.activate(root, old);
        CustomPresetPack.Pack next = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("new.milk")), () -> false, n -> {});
        CustomPresetPack.activate(root, next);
        CustomPresetPack.cleanUnused(root, next.directory);
        assertEquals(next.directory, CustomPresetPack.current(root));
        assertFalse(old.directory.exists());
        assertTrue(next.directory.exists());
    }

    @Test public void rejectedAndStalledNativePreparationLeaveTheActivePointerAlone() throws Exception {
        File root = temp.newFolder();
        CustomPresetPack.Pack old = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("old.milk")), () -> false, n -> {});
        CustomPresetPack.activate(root, old);
        for (int status : new int[]{-1, 0}) {
            try {
                CustomPresetPack.awaitStatus(1, 1, request -> status, () -> false, 20);
                fail("failed/stalled indexing accepted");
            } catch (IOException expected) {
                assertEquals(old.directory, CustomPresetPack.current(root));
            }
        }
    }

    @Test public void committedCleanupFinishesIndependentlyOfTheUploadWorker() throws Exception {
        File root = temp.newFolder();
        CustomPresetPack.Pack old = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("old.milk")), () -> false, n -> {});
        CustomPresetPack.activate(root, old);
        CustomPresetPack.Pack next = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("new.milk")), () -> false, n -> {});
        CustomPresetPack.activate(root, next);
        java.util.concurrent.Future<?> cleanup = CustomPresetPack.scheduleCleanup(root);
        cleanup.get(3, java.util.concurrent.TimeUnit.SECONDS);
        assertFalse(old.directory.exists());
        assertEquals(next.directory, CustomPresetPack.current(root));
    }

    @Test public void cleanupKeepsTextureGenerationUntilNativeReadersReleaseIt() throws Exception {
        File root = temp.newFolder();
        CustomPresetPack.Pack old = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("old.milk", "old.png")), () -> false, n -> {});
        CustomPresetPack.activate(root, old);
        CustomPresetPack.Pack next = CustomPresetPack.prepare(root, new ByteArrayInputStream(zip("new.milk", "new.png")), () -> false, n -> {});
        CustomPresetPack.activate(root, next);
        java.util.concurrent.atomic.AtomicBoolean leased = new java.util.concurrent.atomic.AtomicBoolean(true);
        CustomPresetPack.scheduleCleanup(root, dir -> leased.get()).get(3, java.util.concurrent.TimeUnit.SECONDS);
        assertTrue(old.directory.exists());
        assertEquals(next.directory, CustomPresetPack.current(root));
        leased.set(false);
        CustomPresetPack.retryPendingCleanups(dir -> leased.get());
        CustomPresetPack.scheduleCleanup(root, dir -> leased.get()).get(3, java.util.concurrent.TimeUnit.SECONDS);
        assertFalse(old.directory.exists());
    }
}
