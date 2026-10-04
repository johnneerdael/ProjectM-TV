package nl.neerdael.projectm.core;

/** Rendering policy compiled into this Core artifact. */
public final class RenderingPolicy {
    public static final String NAME = BuildConfig.RENDERING_POLICY;
    public static final boolean NATIVE_ENABLED = BuildConfig.SUPPORTS_NATIVE_RENDERING;

    private RenderingPolicy() {}
}
