// Optional runner-side clock interposition. The published AAR is untouched.
#include <jni.h>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <dlfcn.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

namespace {
std::atomic<bool> enabled{false};
std::atomic<int64_t> nanoseconds{1000000000000000LL};
char corePath[4096]={0};
}

extern "C" int clock_gettime(clockid_t clock,timespec* value) {
    Dl_info info{};
    if (enabled.load() && (clock==CLOCK_REALTIME || clock==CLOCK_MONOTONIC) &&
        dladdr(__builtin_return_address(0),&info) && info.dli_fname &&
        std::strcmp(info.dli_fname,corePath)==0) {
        int64_t ns=nanoseconds.load();value->tv_sec=ns/1000000000LL;value->tv_nsec=ns%1000000000LL;return 0;
    }
    return static_cast<int>(syscall(SYS_clock_gettime,clock,value));
}

extern "C" JNIEXPORT void JNICALL
Java_nl_neerdael_projectm_analysis_CoreBackendRunner_configureClock(JNIEnv* env,jclass,jstring path) {
    const char* text=env->GetStringUTFChars(path,nullptr);
    if (!text) return;
    if (std::strlen(text)<sizeof(corePath)) {
        std::strcpy(corePath,text);nanoseconds.store(1000000000000000LL);std::srand(12345);enabled.store(true);
    }
    env->ReleaseStringUTFChars(path,text);
}

extern "C" JNIEXPORT void JNICALL
Java_nl_neerdael_projectm_analysis_CoreBackendRunner_setClock(JNIEnv*,jclass,jlong ns) {
    nanoseconds.store(1000000000000000LL+ns);
}
