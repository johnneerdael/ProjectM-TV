package com.example.projectm.visualizer;

import android.app.UiModeManager;
import android.content.Context;
import android.content.res.Configuration;
import android.graphics.Point;
import android.os.Build;
import android.util.Log;
import android.view.Display;
import android.view.WindowManager;

/**
 * Physical display capabilities.
 *
 * Android TVs commonly drive the UI at 1080p on a 4K panel, while a SurfaceView can still be
 * shown at the panel's full physical resolution. The physical size is detected the same way
 * AndroidX Media3 does it (Util.getCurrentDisplayModeSize): vendor/system display-size property,
 * Sony's 4K panel feature, then Display.Mode.
 */
public final class DisplayInfo {
    private static final String TAG = "DisplayInfo";

    /** Panel resolution, landscape (e.g. 3840x2160 on a 4K TV even when the UI runs at 1080p). */
    public final int physicalWidth;
    public final int physicalHeight;
    /** Resolution the UI/window system uses. */
    public final int uiWidth;
    public final int uiHeight;
    public final float refreshRate;

    private DisplayInfo(int pw, int ph, int uw, int uh, float refreshRate) {
        this.physicalWidth = pw;
        this.physicalHeight = ph;
        this.uiWidth = uw;
        this.uiHeight = uh;
        this.refreshRate = refreshRate;
    }

    public static DisplayInfo detect(Context context) {
        WindowManager wm = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
        Display display = wm.getDefaultDisplay();
        Point ui = new Point();
        display.getRealSize(ui);
        Point physical = physicalSize(context, display, ui);
        float refresh = display.getRefreshRate() > 1 ? display.getRefreshRate() : 60f;

        DisplayInfo info = new DisplayInfo(
                Math.max(physical.x, physical.y), Math.min(physical.x, physical.y),
                Math.max(ui.x, ui.y), Math.min(ui.x, ui.y), refresh);
        Log.i(TAG, "Panel " + info.physicalWidth + "x" + info.physicalHeight + ", UI " + info.uiWidth
                + "x" + info.uiHeight + " @ " + refresh + " Hz");
        return info;
    }

    private static Point physicalSize(Context context, Display display, Point fallback) {
        if (isTv(context)) {
            String property = ProjectMJNI.getSystemProperty(
                    Build.VERSION.SDK_INT < 28 ? "sys.display-size" : "vendor.display-size");
            Point parsed = parseSize(property);
            if (parsed != null) return parsed;
            if ("Sony".equals(Build.MANUFACTURER) && Build.MODEL.startsWith("BRAVIA")
                    && context.getPackageManager().hasSystemFeature("com.sony.dtv.hardware.panel.qfhd")) {
                return new Point(3840, 2160);
            }
        }
        if (Build.VERSION.SDK_INT >= 23) {
            Display.Mode mode = display.getMode();
            if (mode.getPhysicalWidth() > 0 && mode.getPhysicalHeight() > 0) {
                return new Point(mode.getPhysicalWidth(), mode.getPhysicalHeight());
            }
        }
        return fallback;
    }

    private static Point parseSize(String value) {
        if (value == null) return null;
        String[] parts = value.trim().split("x");
        if (parts.length != 2) return null;
        try {
            int w = Integer.parseInt(parts[0].trim());
            int h = Integer.parseInt(parts[1].trim());
            return w > 0 && h > 0 ? new Point(w, h) : null;
        } catch (NumberFormatException e) {
            Log.w(TAG, "Invalid display size property: " + value);
            return null;
        }
    }

    private static boolean isTv(Context context) {
        UiModeManager ui = (UiModeManager) context.getSystemService(Context.UI_MODE_SERVICE);
        return ui != null && ui.getCurrentModeType() == Configuration.UI_MODE_TYPE_TELEVISION;
    }

    /** Width for a render height, keeping the panel's aspect ratio (even number of pixels). */
    public int widthForHeight(int height) {
        return Math.round(height * (float) physicalWidth / physicalHeight) & ~1;
    }
}
