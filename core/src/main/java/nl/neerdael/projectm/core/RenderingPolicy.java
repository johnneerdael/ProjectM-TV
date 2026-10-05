package nl.neerdael.projectm.core;

/** Native rendering capability of the Core artifact; field names remain API-compatible. */
public final class RenderingPolicy {
    public static final String NAME = BuildConfig.RENDERING_POLICY;
    public static final boolean NATIVE_ENABLED = BuildConfig.SUPPORTS_NATIVE_RENDERING;

    private RenderingPolicy() {}
}
