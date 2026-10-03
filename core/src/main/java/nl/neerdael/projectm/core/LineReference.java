package nl.neerdael.projectm.core;

/**
 * Line thickness: the render size at which waveforms, custom waves and shape outlines are 1 px
 * wide (see {@link ProjectMJNI#setLineReferenceSize}). Above it they widen with the square root of
 * the area ratio, so they keep their share of the picture.
 *
 * MilkDrop's authoring resolution (1024x768) keeps presets closest to how they were made: their
 * lines cover the same share of the picture as on the author's screen (1.62 px at 1080p, 3.25 px at
 * 4K). 1080p draws them 1 px at 1080p and 2 px at 4K.
 */
public final class LineReference {
    public static final String[] LABELS = {"MilkDrop (1024×768)", "1080p"};
    private static final int[][] SIZES = {{1024, 768}, {1920, 1080}};
    public static final int DEFAULT_INDEX = 0;

    private LineReference() {}

    /** A saved option index, or the default if it is not a known option. */
    public static int validIndex(int index) {
        return index >= 0 && index < SIZES.length ? index : DEFAULT_INDEX;
    }

    /** Reference {width, height} for an option index (the default for an unknown one). */
    public static int[] size(int index) {
        return SIZES[validIndex(index)].clone();
    }
}
