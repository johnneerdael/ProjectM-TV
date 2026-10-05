// Opt-in test-host random inputs. Link beside the clock helper; never into core.
// Only calls originating in the explicitly named core receive supplied inputs.
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <dlfcn.h>
#include <fcntl.h>
#include <random>
#include <sys/syscall.h>
#include <unistd.h>

namespace {
char corePath[4096]{};
uint32_t seed{};
int logFd{-1};
std::atomic<bool> enabled{false};
std::atomic<uint64_t> entropyCalls{0},randCalls{0};
thread_local std::mt19937 inputGenerator;
thread_local bool streamInitialized=false;

bool fromCore(void* caller) {
    Dl_info info{};
    return enabled.load() && dladdr(caller,&info) && info.dli_fname &&
           std::strcmp(info.dli_fname,corePath)==0;
}
void record(const char* kind,uint64_t index,uint32_t value) {
    if(logFd<0)return;
    char line[160];
    const int size=std::snprintf(line,sizeof(line),"{\"kind\":\"%s\",\"index\":%llu,\"value\":%u,\"tid\":%ld}\n",
                                 kind,static_cast<unsigned long long>(index),value,static_cast<long>(syscall(SYS_gettid)));
    if(size>0 && size<static_cast<int>(sizeof(line))) {
        const int saved=errno;
        ssize_t result;
        do {result=write(logFd,line,static_cast<size_t>(size));} while(result<0 && errno==EINTR);
        errno=saved;
    }
}
__attribute__((constructor)) void configure() {
    const char* requested=std::getenv("PROJECTMTV_TEST_RANDOM_SEED");
    if(!requested)return;
    const char* core=std::getenv("PROJECTMTV_TEST_CORE_PATH");
    const char* log=std::getenv("PROJECTMTV_TEST_RANDOM_LOG");
    char* end{};errno=0;
    const auto value=std::strtoull(requested,&end,10);
    if(!*requested || !end || *end || errno || value>UINT32_MAX ||
       !core || !*core || std::strlen(core)>=sizeof(corePath) || !log || !*log) {
        std::fputs("Invalid declared core random-input contract\n",stderr);std::abort();
    }
    logFd=open(log,O_WRONLY|O_CREAT|O_TRUNC|O_APPEND,0600);
    if(logFd<0) {std::fputs("Cannot record core random-input contract\n",stderr);std::abort();}
    std::strcpy(corePath,core);seed=static_cast<uint32_t>(value);enabled.store(true);
    record("declared_seed",0,seed);
}
}

extern "C" void projectmtv_test_clock_seed(int64_t nanoseconds) {
    record("clock_low32_microseconds",0,static_cast<uint32_t>(nanoseconds/1000));
}

extern "C" ssize_t read(int fd,void* buffer,size_t size) {
    using Function=ssize_t(*)(int,void*,size_t);
    static auto real=reinterpret_cast<Function>(dlsym(RTLD_NEXT,"read"));
    if(fromCore(__builtin_return_address(0)) && size==sizeof(seed)) {
        char path[64],target[128];
        std::snprintf(path,sizeof(path),"/proc/self/fd/%d",fd);
        const auto count=readlink(path,target,sizeof(target)-1);
        if(count>0) {
            target[count]='\0';
            if(std::strcmp(target,"/dev/urandom")==0 || std::strcmp(target,"/dev/random")==0) {
                std::memcpy(buffer,&seed,sizeof(seed));
                record("entropy_seed",entropyCalls.fetch_add(1),seed);
                return sizeof(seed);
            }
        }
    }
    if(!real) {errno=ENOSYS;return -1;}
    return real(fd,buffer,size);
}

extern "C" void srand(unsigned int requested) {
    using Function=void(*)(unsigned int);
    static auto real=reinterpret_cast<Function>(dlsym(RTLD_NEXT,"srand"));
    const bool scoped=fromCore(__builtin_return_address(0));
    if(!real)std::abort();
    if(scoped) {inputGenerator.seed(seed);streamInitialized=true;record("c_seed",0,seed);}
    else real(requested);
}

extern "C" int rand() {
    using Function=int(*)();
    static auto real=reinterpret_cast<Function>(dlsym(RTLD_NEXT,"rand"));
    if(!real)std::abort();
    if(fromCore(__builtin_return_address(0))) {
        if(!streamInitialized) {inputGenerator.seed(seed);streamInitialized=true;}
        const auto value=static_cast<int>(inputGenerator()&0x7fffffffU);
        record("c_rand",randCalls.fetch_add(1),static_cast<uint32_t>(value));
        return value;
    }
    return real();
}
