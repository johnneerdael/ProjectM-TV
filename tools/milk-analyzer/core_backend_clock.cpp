// Optional runner-side clock interposition. The published AAR is untouched.
#include <jni.h>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <dlfcn.h>
#include <cerrno>
#include <fcntl.h>
#include <vector>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

namespace {
std::atomic<bool> enabled{false};
std::atomic<int64_t> nanoseconds{1000000000000000LL};
char corePath[4096]={0};
int frameOutput=-1;
bool writeAll(const void* bytes,size_t length) {
    const auto* data=static_cast<const uint8_t*>(bytes);
    while(length) {ssize_t n=write(frameOutput,data,length);if(n<0&&errno==EINTR)continue;if(n<=0)return false;data+=n;length-=n;}return true;
}
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

extern "C" JNIEXPORT void JNICALL
Java_nl_neerdael_projectm_analysis_CoreBackendRunner_startStream(JNIEnv* env,jclass,jstring path,jint frames) {
    const char* text=env->GetStringUTFChars(path,nullptr);if(!text)return;
    frameOutput=dup(STDOUT_FILENO);int log=open(text,O_WRONLY|O_CREAT|O_TRUNC,0600);
    env->ReleaseStringUTFChars(path,text);
    if(frameOutput<0||log<0||dup2(log,STDOUT_FILENO)<0||dup2(log,STDERR_FILENO)<0) {
        env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),"Cannot isolate frame transport");return;
    }
    close(log);
    const uint32_t fields[]={128,72,static_cast<uint32_t>(frames),30,static_cast<uint32_t>(getpid())};
    if(!writeAll("PMCORE01",8)||!writeAll(fields,sizeof(fields)))
        env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),"Frame transport header failed");
}

extern "C" JNIEXPORT void JNICALL
Java_nl_neerdael_projectm_analysis_CoreBackendRunner_writeFrame(JNIEnv* env,jclass,jobject buffer) {
    auto* rgba=static_cast<uint8_t*>(env->GetDirectBufferAddress(buffer));
    if(!rgba||env->GetDirectBufferCapacity(buffer)!=128*72*4) {
        env->ThrowNew(env->FindClass("java/lang/IllegalArgumentException"),"Wrong RGBA frame buffer");return;
    }
    std::vector<uint8_t> rgb(128*72*3);
    for(int y=0;y<72;++y)for(int x=0;x<128;++x)for(int c=0;c<3;++c)
        rgb[(y*128+x)*3+c]=rgba[((71-y)*128+x)*4+c];
    if(!writeAll(rgb.data(),rgb.size()))
        env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),"Frame consumer closed");
}
