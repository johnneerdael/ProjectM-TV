package com.example.projectm.visualizer;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;
import java.io.*;
import java.nio.file.Files;
import java.util.zip.*;
import static org.junit.Assert.*;

public class CustomPresetPackTest {
    @Rule public TemporaryFolder temp = new TemporaryFolder();

    private byte[] zip(String... names) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (ZipOutputStream zip = new ZipOutputStream(bytes)) {
            for (String name : names) {
                zip.putNextEntry(new ZipEntry(name));
                zip.write("[preset00]\nfRating=3\n".getBytes("UTF-8"));
                zip.closeEntry();
            }
        }
        return bytes.toByteArray();
    }

    @Test public void importsNestedMilkAndIgnoresEveryOtherFile() throws Exception {
        File root = temp.newFolder();
        CustomPresetPack.Pack pack = CustomPresetPack.prepare(root, new ByteArrayInputStream(
                zip("one/test.milk", "two/test.MILK", "readme.txt", "textures/a.jpg")), () -> false, n -> {});
        assertEquals(2, pack.count);
        assertNull(CustomPresetPack.current(root));
        CustomPresetPack.activate(root, pack);
        assertEquals(pack.directory, CustomPresetPack.current(root));
        String index = new String(Files.readAllBytes(new File(pack.directory, "presets.idx").toPath()), "UTF-8");
        assertTrue(index.contains("\tone/test.milk\n"));
        assertTrue(index.contains("\ttwo/test.MILK\n"));
        assertFalse(index.contains("readme"));
        assertEquals(2, index.split("\n").length);
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
        }
        try (InputStream in = new FileInputStream(archive)) {
            CustomPresetPack.Pack pack = CustomPresetPack.prepare(root, in, () -> false, n -> {});
            assertEquals(50000, pack.count);
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
}
