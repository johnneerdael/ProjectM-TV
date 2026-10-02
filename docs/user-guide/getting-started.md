# Install and get started

## Requirements

- Android TV or Google TV running Android 5.0 or later.
- OpenGL ES 3.0.
- At least 2 GB RAM is highly recommended.
- A music app playing on the same device.

ProjectM TV visualizes another app's music. It does not play music itself or use the microphone.

## Install on the TV

1. Install **Downloader by AFTVnews** from the TV's app store.
2. Open Downloader and enter **4821216**.
3. Allow Android to install apps from Downloader when asked.
4. Confirm installation of the downloaded APK.

The code points to the [latest signed APK](https://github.com/johnneerdael/ProjectM-TV/releases/latest/download/projectM-TV.apk). Specific versions are available under [Releases](https://github.com/johnneerdael/ProjectM-TV/releases).

## Install from a computer

```sh
curl -LO https://github.com/johnneerdael/ProjectM-TV/releases/latest/download/projectM-TV.apk
adb install -r projectM-TV.apk
```

Production releases use the same permanent signing key. An APK built with your own debug key cannot update a production installation directly.

## First launch

1. Start music in your music player.
2. Open ProjectM TV.
3. Grant **Record audio** permission. Android requires it for the visualizer API; the app attaches to the music player's audio session.
4. Wait for the player session to be found. Visuals usually begin responding within a second or two.

**All** is the default music category. To choose the 500-preset collection, open the settings panel and set **Music category → Dance**.

## Track titles

Track title and artist are optional. In **Settings → Advanced → Track titles**, follow the instructions to allow notification access in Android's settings. This lets the app read the music player's media session. Without access, the visualizer still works and titles are omitted.

## Updates

**Settings → Advanced → Auto-update** is off by default. When enabled, the app checks GitHub at launch and every six hours while open, downloads a new release and offers an Install row. Android asks you to confirm installation. F-Droid installations use F-Droid for updates.

Audio is processed in memory. The app makes no network connections while its auto-update setting is off.
