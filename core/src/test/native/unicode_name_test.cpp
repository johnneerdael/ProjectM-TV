// Reuse the engine harness fakes, then call the actual JNI getter with a real JNIEnv.
#define main unused_engine_test_main
#include "engine_test.cpp"
#undef main

extern "C" JNIEXPORT jstring JNICALL Java_UnicodeNameTest_name(JNIEnv* env, jclass, jbyteArray bytes) {
    jsize size = env->GetArrayLength(bytes);
    std::string name(static_cast<size_t>(size), '\0');
    if (size) env->GetByteArrayRegion(bytes, 0, size, reinterpret_cast<jbyte*>(&name[0]));
    {
        std::lock_guard<std::mutex> lock(g_published.mutex);
        g_published.currentPreset = name;
    }
    return Java_nl_neerdael_projectm_core_ProjectMJNI_getCurrentPresetName(env, nullptr);
}
