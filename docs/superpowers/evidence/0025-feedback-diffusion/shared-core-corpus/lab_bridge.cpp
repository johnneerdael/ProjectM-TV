#include <jni.h>
#include <GLES3/gl3.h>
#include <cstdlib>
#include <cstdio>
#include <string>
#include <vector>
#include "analysis_hooks.hpp"

extern "C" {
JNIEXPORT void JNICALL Java_nl_neerdael_projectm_corecorpus_LabBridge_configureSeed(JNIEnv*, jclass, jint seed) {
    char value[32]; std::snprintf(value, sizeof(value), "%u", static_cast<unsigned>(seed));
    setenv("PRESET_LAB_SEED", value, 1);
}
JNIEXPORT void JNICALL Java_nl_neerdael_projectm_corecorpus_LabBridge_setClock(JNIEnv*, jclass, jdouble seconds) {
    lab::clock_seconds.store(seconds);
}
JNIEXPORT void JNICALL Java_nl_neerdael_projectm_corecorpus_LabBridge_prepareDefaultReadBuffer(JNIEnv*, jclass) {
    GLint previous{}; glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING, &previous);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, 0); glReadBuffer(GL_BACK);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, static_cast<GLuint>(previous));
}
JNIEXPORT jbyteArray JNICALL Java_nl_neerdael_projectm_corecorpus_LabBridge_captureRgba(JNIEnv* env, jclass, jint width, jint height) {
    if (width <= 0 || height <= 0 || width > 4096 || height > 4096) return nullptr;
    std::vector<jbyte> pixels(static_cast<size_t>(width) * height * 4);
    GLint framebuffer{}, packBuffer{}, alignment{};
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING, &framebuffer);
    glGetIntegerv(GL_PIXEL_PACK_BUFFER_BINDING, &packBuffer);
    glGetIntegerv(GL_PACK_ALIGNMENT, &alignment);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, 0);
    glBindBuffer(GL_PIXEL_PACK_BUFFER, 0);
    glPixelStorei(GL_PACK_ALIGNMENT, 1);
    glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    glPixelStorei(GL_PACK_ALIGNMENT, alignment);
    glBindBuffer(GL_PIXEL_PACK_BUFFER, static_cast<GLuint>(packBuffer));
    glBindFramebuffer(GL_READ_FRAMEBUFFER, static_cast<GLuint>(framebuffer));
    auto result = env->NewByteArray(static_cast<jsize>(pixels.size()));
    if (result) env->SetByteArrayRegion(result, 0, static_cast<jsize>(pixels.size()), pixels.data());
    return result;
}
JNIEXPORT void JNICALL Java_nl_neerdael_projectm_corecorpus_LabBridge_clearDefaultFramebuffer(JNIEnv*, jclass) {
    glBindFramebuffer(GL_FRAMEBUFFER, 0); glClearColor(0.0f, 0.0f, 0.0f, 1.0f); glClear(GL_COLOR_BUFFER_BIT);
}
JNIEXPORT jint JNICALL Java_nl_neerdael_projectm_corecorpus_LabBridge_glError(JNIEnv*, jclass) { return static_cast<jint>(glGetError()); }
JNIEXPORT jstring JNICALL Java_nl_neerdael_projectm_corecorpus_LabBridge_glInfo(JNIEnv* env, jclass) {
    const char* vendor = reinterpret_cast<const char*>(glGetString(GL_VENDOR));
    const char* renderer = reinterpret_cast<const char*>(glGetString(GL_RENDERER));
    const char* version = reinterpret_cast<const char*>(glGetString(GL_VERSION));
    std::string result = std::string(vendor ? vendor : "") + "\n" + (renderer ? renderer : "") + "\n" + (version ? version : "");
    return env->NewStringUTF(result.c_str());
}
}
