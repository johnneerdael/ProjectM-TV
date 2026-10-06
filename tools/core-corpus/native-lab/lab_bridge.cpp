#include "lab_bridge.hpp"

#include <jni.h>
#include <cstdio>
#include <cstdlib>

namespace core_corpus {
int reference_width = 1024;
int reference_height = 768;
}

extern "C" JNIEXPORT void JNICALL
Java_nl_neerdael_projectmtv_corpus_LabBridge_initialize(
        JNIEnv*, jclass, jlong seed, jint reference_width, jint reference_height) {
    char configured_seed[32];
    std::snprintf(configured_seed, sizeof(configured_seed), "%u", static_cast<unsigned>(seed));
    setenv("PRESET_LAB_SEED", configured_seed, 1);
    // New upstream no longer seeds libc rand in ProjectM's constructor. Reset
    // the private shader stream here so both source roles use the requested seed.
    lab::ResetShaderRandom();
    lab::clock_seconds = 0.0;
    core_corpus::reference_width = reference_width;
    core_corpus::reference_height = reference_height;
}

extern "C" JNIEXPORT void JNICALL
Java_nl_neerdael_projectmtv_corpus_LabBridge_setFrameClock(JNIEnv*, jclass, jdouble seconds) {
    lab::clock_seconds = seconds;
}
