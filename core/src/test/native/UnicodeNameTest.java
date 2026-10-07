import java.nio.charset.StandardCharsets;

public final class UnicodeNameTest {
    private static native String name(byte[] utf8);

    public static void main(String[] args) {
        System.load(args[0]);
        for (String expected : new String[]{"", "nested/café.milk", "custom/emoji-😀.MILK"}) {
            String actual = name(expected.getBytes(StandardCharsets.UTF_8));
            if (!expected.equals(actual)) throw new AssertionError("Preset name changed: " + actual);
        }
        System.out.println("JNI UTF-8 PRESET NAME TESTS PASSED");
    }
}
