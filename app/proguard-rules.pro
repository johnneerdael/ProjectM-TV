# R8 shrinks and optimizes the release build. The app is open source, so obfuscation buys nothing
# and would make crash traces in logcat and tools/tv-diagnostics.sh unreadable.
-dontobfuscate

# The engine's JNI entry points are kept by core/consumer-rules.pro.
