# projectM for Android TV 1.8

A ground-up rebuild of the engine behind the visualizer. Visuals start almost immediately, presets that show nothing are skipped, and the picture now scales from Fire TV sticks up to 4K on NVIDIA Shield and high-end TVs.

## Highlights

- **Starts in seconds.** Presets are read directly from the app instead of being copied to storage (~130 MB) on every launch. Visuals appear as soon as the screen is up.
- **No more black screens.** Fixed the causes of presets staying black:
  - remote-control preset changes ran on the wrong thread;
  - the graphics context was OpenGL ES 2.0 instead of the 3.0 projectM needs;
  - audio was decoded in the wrong format.
- **Real 4K.** Many TVs run their menus at 1080p on a 4K panel. The app now detects the physical panel and can render at up to full 4K on Shield and similar TVs.
- **Automatic resolution.** *Auto* picks the highest resolution your device can run smoothly and adjusts between presets, so a change never interrupts a preset.
- **Self-cleaning playlist.** Presets that fail to load, render nothing while music plays, or (optionally) are too slow for your device are skipped and remembered.
- **New TV-style menu.** A compact panel with now-playing info, previous/shuffle/next controls and settings rows you change with the remote's arrows. Long preset names scroll.

## Settings

| Setting | What it does |
|---|---|
| Resolution | **Auto** (recommended), or a fixed 720p / 1080p / 1440p / 4K, limited to what your panel supports |
| Frame rate | Full refresh rate or an even fraction (e.g. 60 or 30 fps; 120/60/30 on 120 Hz TVs). A steady 30 is smoother than an unsteady 45 |
| Transition | Blend time between presets. Shorter is faster on slow devices, because two presets render during a blend |
| **Advanced ›** | **Detail** (Minimal–Ultra per-vertex mesh, the main CPU cost), **Skip slow presets**, **Skip blank presets**, skipped-preset reset, and live diagnostics (render size, panel, refresh rate, FPS) |

## Performance on low-end devices (e.g. Fire TV sticks)

On devices with little memory, the defaults now favour smoothness:
- 30 fps
- a lighter mesh
- short transitions
- Auto resolution that can drop to 360p when needed
- slow presets skipped automatically

All of these can be changed in the menu.

## Good to know

- **OpenGL ES 3.0 is now required.** projectM 4 always needed it; devices without it never showed correct visuals.
- **Settings reset:** resolution and frame-rate settings start from the new defaults.
- **Uninstall first:** if you installed an earlier build yourself, uninstall it before installing this one, because the signing key differs.
- **Skipped-preset list:** resetting it under **Advanced ›** brings all presets back.

## Remote control

| Button | Action |
|---|---|
| Right / Left | Random preset / previous preset |
| Up / Down / Info | Show the current preset name |
| Center / Menu | Open the menu; ↑↓ select a row, ‹ › change its value |
| Back | Close the panel (or return from Advanced) / exit |

---

# projectM Android TV 1.6 - Complete Viewport Fix & Device-Tier Performance

## Revolutionary Viewport Resolution & Smart Performance Optimization

Version 1.6 represents a major breakthrough in projectM Android TV, delivering the definitive solution to viewport scaling issues while introducing intelligent device-tier performance optimization. This release ensures perfect fullscreen visualization on all resolutions while automatically optimizing performance based on your specific Android TV hardware.

### ✨ Major Improvements in 1.6

- **🎯 DEFINITIVE VIEWPORT SCALING FIX** - Completely eliminated the root cause of viewport scaling issues
  - **Always Full Resolution Rendering**: ProjectM now always renders at native screen dimensions (1920x1080, etc.)
  - **Quality-Based Performance**: Performance optimization through preset complexity and quality settings instead of resolution reduction
  - **Universal Screen Coverage**: 720p/480p performance modes now maintain perfect fullscreen display
  
- **🚀 Intelligent Device-Tier Performance System** - Automatic hardware detection and optimization
  - **PREMIUM Tier** (NVIDIA Shield/Tegra): Maximum quality, extended transitions, full native resolution
  - **HIGH-END Tier** (Fire TV 4K, Mi Box S): High quality settings optimized for powerful Android TV boxes
  - **MID-RANGE Tier** (Standard Android TV): Balanced quality with moderate optimizations
  - **LOW-END Tier** (Budget devices): Optimized settings for smooth performance on older hardware
  
- **⚡ Eliminated Auto-Resolution Switching** - Replaced problematic resolution scaling with smart defaults
  - **Device-Appropriate Defaults**: Automatic selection of optimal settings based on detected hardware
  - **Consistent User Experience**: No more jarring resolution changes during use
  - **User Override Available**: Manual resolution controls still available for advanced users

### 🔧 Technical Enhancements

- **Native-Level Performance Optimization** - Enhanced C++ performance monitoring and memory management
- **Quality-First Approach** - Maintains visual fidelity while optimizing computational complexity
- **Advanced Device Detection** - GPU model recognition, RAM analysis, and Android version consideration
- **Adaptive FPS Management** - Real-time performance monitoring with automatic quality adjustment

---

# projectM Android TV 1.5 - Complete Viewport Scaling Resolution

## Definitive Viewport Scaling Fix

We're excited to announce version 1.5 of projectM for Android TV, which completely resolves the long-standing viewport scaling issues. This release ensures that all render resolutions (720p, 480p, etc.) properly stretch to fill the entire TV screen, providing a true fullscreen experience regardless of the internal rendering resolution used for performance optimization.c### ✨ New Features & Fixes in 1.3droid TV 1.3 - Resolution Scaling & Viewport Fixes

## Enhanced Visualization & Resolution Fixes

We're excited to announce version 1.3 of projectM for Android TV, focusing on fixing viewport scaling issues and resolution-related artifacts. This update ensures visualizations properly stretch to fill the entire screen at all resolutions while eliminating visual artifacts during resolution changes.

## � Enhanced Visualization Controls

We're excited to announce version 1.2 of projectM for Android TV, featuring improved performance adaptation, an enhanced loading experience, and better control navigation. This update provides a more responsive and stable visualization experience, especially on lower-end devices.

### ✨ New Features & Fixes in 1.5

- **COMPLETELY RESOLVED: Viewport Scaling Issue** - All render resolutions now properly stretch to fill the entire TV screen (720p, 480p no longer appear as partial screen)
- **Advanced Viewport Management System** - Implemented multi-layered viewport control that prevents any library override of display scaling
- **Native-Level Viewport Persistence** - C++ code maintains display dimensions and aggressively restores viewport after every ProjectM operation
- **Real-time Viewport Verification** - Added diagnostic system that detects and corrects viewport changes immediately
- **Performance-Optimized Scaling** - Lower render resolutions for performance while maintaining perfect fullscreen display

### 🎵 Existing Features

- **Complete Cream of the Crop Preset Collection** - All 9,795 handpicked presets included
- **System Audio Visualization** - Visualizes any audio playing on your Android TV
- **Android TV Remote Control**
  - Left/Right buttons to change presets (now with instant transitions)
  - Center/Menu button to toggle settings overlay
  - Back button to exit or hide overlay
- **Auto Preset Switching** - Configurable timing with new extended range
- **Performance Monitoring** - Adaptive rendering with improved transition handling
- **Full Screen Immersive Mode** - Complete Android TV visual experience

### 🔧 Technical Details

- Built on projectM-4 native visualization library
- OpenGL ES 2.0 hardware-accelerated rendering
- FPS monitoring with performance mode switching
- Preset count and current preset name display
- Version information accessible in settings menu

### 📱 Device Compatibility

- **Minimum Android Version**: Android 5.0 (Lollipop)
- **Target Devices**: Android TV boxes and TVs with Android TV OS
- **GPU Requirement**: OpenGL ES 2.0 capable GPU
- **Performance**: Now better optimized for lower-end devices with automatic quality adjustments

### 📋 Permissions Required

- `RECORD_AUDIO` - Required for capturing system audio
- `MODIFY_AUDIO_SETTINGS` - Required for audio visualization processing

### 🐛 Known Issues

- Some complex presets may still cause performance issues, but are now automatically managed
- Occasional black screen when switching between certain presets
- Audio capture may not work on all devices depending on manufacturer restrictions
- Navigation in the settings menu may require multiple button presses on some remote controls

### 🎮 Usage Tips

- **Classic Experience**: Keep transitions at 7s and preset duration around 30s
- **Dynamic Show**: Try shorter preset durations (10-15s) with shorter transitions (2-3s)
- **Manual Control**: Disable auto-change and use the remote for immediate transitions
- **Performance Mode**: Lower transition duration and resolution on less powerful devices

### 🔜 Upcoming Features

- Preset search and filtering
- Custom preset categories
- Background audio playback
- Beat detection sensitivity adjustment
- Preset rating system

### 🚀 Installation

1. Download the APK file from this release
2. Install on your Android TV using one of these methods:
   - Sideload with adb: `adb install projectm-androidtv-1.5.apk`
   - Transfer via USB and install with a file manager
   - Use a sideloading app like Downloader or Send Files to TV
   
If you're updating from any previous version, your preferences will be preserved.

### 🙏 Credits

- projectM Development Team for the visualization library
- Jason Fletcher for the incredible Cream of the Crop preset collection
- The entire Milkdrop community for creating thousands of amazing presets

### 📄 License

This application is released under the GPL v2 license, the same as the core projectM library.

---

## SHA-256 Checksums
```
projectm-androidtv-1.5.apk: [checksum will be generated after building the final APK]
```

## Full Changelog for v1.5

### Fixed
- **DEFINITIVE FIX: Complete viewport scaling resolution** - 720p, 480p, and all lower resolutions now perfectly stretch to fill the entire TV screen
- **Eliminated ProjectM viewport interference** - Completely prevented ProjectM library from overriding display viewport settings
- **Multi-layer viewport restoration** - Added viewport control at Java, JNI, and native C++ levels with real-time verification
- **Perfect aspect ratio maintenance** - All internal render resolutions maintain flawless fullscreen display scaling
- **Enhanced OpenGL state consistency** - Bulletproof viewport management during all rendering operations and transitions

### Added
- Added real-time viewport verification and correction system
- Added comprehensive viewport diagnostic logging throughout rendering pipeline
- Added native-level display dimension storage and management
- Added aggressive viewport restoration after every ProjectM operation
- Added fallback viewport correction mechanisms for maximum reliability

### Changed
- Updated version information to 1.5 throughout the application
- Enhanced all viewport management systems for maximum reliability
- Improved logging and diagnostic capabilities for viewport troubleshooting
- Optimized viewport restoration performance with minimal overhead
- Strengthened OpenGL state management during all rendering scenarios

---

## Previous Versions

### v1.4 - Resolution Scaling & Viewport Enhancements
- Enhanced viewport scaling implementation
- Added native viewport persistence
- Improved OpenGL state management

### v1.3 - Initial Viewport Fixes  
- First attempt at viewport scaling resolution
- Added viewport handling system
- Enhanced OpenGL viewport management

### v1.2 - Performance & User Experience Update
- Modern loading screen with progress feedback
- Automatic resolution adjustment based on performance
- Enhanced low performance mode with quality adjustments
- Improved navigation and visual feedback

### v1.1 - Transition & Stability Improvements
- New transition duration slider (0-10 seconds)
- Hard cut support for manual preset changes
- Extended preset duration range (10-90 seconds)
- Improved error handling and stability fixes
