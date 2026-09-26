#!/bin/bash

# ProjectM Android TV Installer Script for FireStick 4K
echo "ProjectM Android TV Installer"
echo "============================"

# Prefer the optimized release build; fall back to the debug build.
APK_PATH="app/build/outputs/apk/release/app-release.apk"
[ -f "$APK_PATH" ] || APK_PATH="app/build/outputs/apk/debug/app-debug.apk"

if [ ! -f "$APK_PATH" ]; then
    echo "Error: no APK found"
    echo "Please build the project first with: ./gradlew assembleRelease"
    exit 1
fi
echo "Using $APK_PATH"

# Check if adb is available
if ! command -v adb &> /dev/null; then
    echo "Error: adb (Android Debug Bridge) not found"
    echo "Please install Android SDK Platform Tools"
    exit 1
fi

# Check for connected devices
echo "Checking for connected devices..."
DEVICES=$(adb devices | grep -v "List of devices" | grep -v "^$" | wc -l)

if [ $DEVICES -eq 0 ]; then
    echo "No devices connected. Please:"
    echo "1. Enable Developer Options on your FireStick"
    echo "2. Enable USB Debugging"
    echo "3. Connect via WiFi with: adb connect FIRESTICK_IP:5555"
    exit 1
fi

echo "Found $DEVICES device(s)"
adb devices

echo ""
echo "Installing ProjectM Android TV..."
adb install -r "$APK_PATH"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation successful!"
    echo ""
    echo "Next steps:"
    echo "1. Find 'ProjectM TV' in your FireStick apps"
    echo "2. Grant audio recording permission when prompted"
    echo "3. Use D-pad left/right to change presets, center to open the menu"
    echo "4. Enjoy the visualizations!"
else
    echo ""
    echo "❌ Installation failed"
    echo "Please check the adb output above for errors"
fi
