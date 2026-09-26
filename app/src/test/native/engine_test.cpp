// Host test harness for app/src/main/cpp/native-lib.cpp. Run via run_native_tests.sh.
// Compiles native-lib.cpp against fakes of projectM, AAssetManager and GL.
#include <cstring>
#include <cstdarg>
#include <cstdlib>
#include <jni.h>
#include <cassert>
#include <cstdio>
#include <dirent.h>
#include <map>
#include <string>
#include <vector>
#include <set>
#include <thread>
#include <chrono>
#include <sys/types.h>
#include "android/asset_manager.h"
#include "GLES3/gl3.h"
#include "projectM-4/projectM.h"

// ---- fake asset manager backed by a directory ----
struct AAssetManager { std::string root; };
struct AAssetDir { std::vector<std::string> names; size_t i = 0; };
struct AAsset { std::string data; };
extern "C" {
AAssetDir* AAssetManager_openDir(AAssetManager* am, const char* dir) {
  auto* d = new AAssetDir; DIR* h = opendir((am->root + "/" + dir).c_str());
  while (dirent* e = readdir(h)) if (e->d_name[0] != '.' || strlen(e->d_name) > 2) { std::string n = e->d_name; if (n != "." && n != "..") d->names.push_back(n); }
  closedir(h); return d; }
const char* AAssetDir_getNextFileName(AAssetDir* d) { return d->i < d->names.size() ? d->names[d->i++].c_str() : nullptr; }
void AAssetDir_close(AAssetDir* d) { delete d; }
AAsset* AAssetManager_open(AAssetManager* am, const char* p, int) {
  FILE* f = fopen((am->root + "/" + p).c_str(), "rb"); if (!f) return nullptr;
  auto* a = new AAsset; char buf[4096]; size_t n; while ((n = fread(buf, 1, sizeof buf, f)) > 0) a->data.append(buf, n); fclose(f); return a; }
const void* AAsset_getBuffer(AAsset* a) { return a->data.data(); }
off_t AAsset_getLength(AAsset* a) { return a->data.size(); }
void AAsset_close(AAsset* a) { delete a; }
AAssetManager* AAssetManager_fromJava(JNIEnv*, jobject) { return nullptr; }
std::vector<std::string> g_logLines;
int __android_log_print(int, const char* tag, const char* fmt, ...) {
  char buf[2048]; va_list ap; va_start(ap, fmt); vsnprintf(buf, sizeof buf, fmt, ap); va_end(ap);
  fprintf(stderr, "%s\n", buf); g_logLines.push_back(buf); return 0; }
int __system_property_get(const char* name, char* value) {
  if (strcmp(name, "vendor.display-size") == 0) { strcpy(value, "3840x2160"); return 9; }
  value[0] = 0; return 0; }
// ---- fake GL ----
unsigned char g_pixel = 0;
int g_readFbo = -1;  // framebuffer bound for reading during glReadPixels
unsigned char g_noise = 0;  // when set, pixels alternate between g_pixel and g_pixel + g_noise
GLuint g_packBuffer = 0; std::vector<unsigned char> g_pbo; int g_fences = 0, g_mapped = 0;
void glViewport(GLint, GLint, GLsizei, GLsizei) {}
void glBindFramebuffer(GLenum target, GLuint fbo) { if (target != GL_DRAW_FRAMEBUFFER) g_readFbo = (int)fbo; }
int g_blits = 0; int g_blitSrcW = 0, g_blitSrcH = 0, g_blitDstW = 0, g_blitDstH = 0;
void glGenFramebuffers(GLsizei, GLuint* f) { *f = 77; }
void glDeleteFramebuffers(GLsizei, const GLuint*) {}
void glGenTextures(GLsizei, GLuint* t) { *t = 78; }
void glDeleteTextures(GLsizei, const GLuint*) {}
void glBindTexture(GLenum, GLuint) {}
void glTexImage2D(GLenum, GLint, GLint, GLsizei, GLsizei, GLint, GLenum, GLenum, const void*) {}
void glTexParameteri(GLenum, GLenum, GLint) {}
void glFramebufferTexture2D(GLenum, GLenum, GLenum, GLuint, GLint) {}
GLenum glCheckFramebufferStatus(GLenum) { return GL_FRAMEBUFFER_COMPLETE; }
void glBlitFramebuffer(GLint, GLint, GLint sw, GLint sh, GLint, GLint, GLint dw, GLint dh, GLbitfield, GLenum) {
  ++g_blits; g_blitSrcW = sw; g_blitSrcH = sh; g_blitDstW = dw; g_blitDstH = dh; }
void glGetIntegerv(GLenum e, GLint* v) { *v = e == GL_PIXEL_PACK_BUFFER_BINDING ? (GLint)g_packBuffer : e == GL_PACK_ALIGNMENT ? 4 : 7; }
void glGenBuffers(GLsizei, GLuint* b) { *b = 42; }
void glDeleteBuffers(GLsizei, const GLuint*) {}
void glBindBuffer(GLenum, GLuint b) { g_packBuffer = b; }
void glBufferData(GLenum, GLsizeiptr n, const void*, GLenum) { g_pbo.assign((size_t)n, 0); }
void glPixelStorei(GLenum, GLint) {}
void* glMapBufferRange(GLenum, GLintptr, GLsizeiptr, GLbitfield) { ++g_mapped; return g_pbo.data(); }
unsigned char glUnmapBuffer(GLenum) { return 1; }
GLsync glFenceSync(GLenum, GLbitfield) { ++g_fences; return (GLsync)(intptr_t)g_fences; }
GLenum glClientWaitSync(GLsync, GLbitfield, GLuint64) { return GL_ALREADY_SIGNALED; }
void glDeleteSync(GLsync) { --g_fences; }
void glFlush() {}
void glReadPixels(GLint, GLint, GLsizei w, GLsizei h, GLenum, GLenum, GLvoid* out) {
  if (g_readFbo != 0) { fprintf(stderr, "FAIL glReadPixels not reading the window\n"); exit(1); }
  if (g_packBuffer != 42) { fprintf(stderr, "FAIL glReadPixels without the pixel pack buffer (would stall)\n"); exit(1); }
  size_t offset = (size_t)(intptr_t)out;
  if (offset + (size_t)w * h * 4 > g_pbo.size()) { fprintf(stderr, "FAIL glReadPixels past the buffer\n"); exit(1); }
  unsigned char* p = g_pbo.data() + offset;
  for (size_t i = 0; i < (size_t)w * h; ++i) memset(p + i * 4, (i / 4) % 2 ? g_pixel + g_noise : g_pixel, 4); }
}
// ---- fake transition overlay (the real one is tested on Mesa by fade_gl_test.cpp) ----
#include "snapshot_fade.h"
int g_captures = 0, g_fadeStarts = 0, g_fadeDraws = 0; double g_fadeSeconds = 0; bool g_captureOk = true;
bool SnapshotFade::Capture(int, int) { Stop(); ++g_captures; texture_ = g_captureOk ? 1 : 0; return g_captureOk; }
void SnapshotFade::Start(double now, double seconds) { if (!texture_) return; ++g_fadeStarts; active_ = true; start_ = now; duration_ = seconds; g_fadeSeconds = seconds; }
void SnapshotFade::Draw(double now) { if (!active_) return; ++g_fadeDraws; if (now - start_ >= duration_) Stop(); }
void SnapshotFade::Stop() { active_ = false; texture_ = 0; }
void SnapshotFade::Forget() { Stop(); }
void SnapshotFade::Release() { Stop(); }
// ---- fake shader prewarmer (the real one needs EGL) ----
#include "preset_prewarm.h"
std::vector<std::string> g_prewarmRequests; std::string g_prewarmTextureDir; int g_prewarmStarts = 0, g_prewarmStops = 0;
void PresetPrewarmer::Start(const std::string& dir, Reader) { ++g_prewarmStarts; g_prewarmTextureDir = dir; }
void PresetPrewarmer::Stop() { ++g_prewarmStops; }
void PresetPrewarmer::Request(const std::string& name) { g_prewarmRequests.push_back(name); }
extern "C" {
// ---- fake projectM ----
struct projectm {};
static projectm_preset_switch_failed_event g_failCb; static projectm_preset_switch_requested_event g_reqCb;
std::vector<std::string> g_loaded; bool g_locked = false; size_t g_pcmFed = 0;
bool g_lastSmooth = false; int g_meshCalls = 0;
std::vector<std::string> g_texturePathCalls; size_t g_loadsAtTextureCall = 0;
projectm_handle projectm_create() { return new projectm; }
void projectm_destroy(projectm_handle p) { delete p; }
int g_loadSleepMs = 0;
void projectm_load_preset_data(projectm_handle, const char* data, bool smooth) {
  g_lastSmooth = smooth;
  if (g_loadSleepMs) std::this_thread::sleep_for(std::chrono::milliseconds(g_loadSleepMs));
  if (strstr(data, "BROKEN")) { g_failCb("", "compile error", nullptr); return; }
  g_loaded.push_back(data); }
void projectm_set_preset_switch_requested_event_callback(projectm_handle, projectm_preset_switch_requested_event cb, void*) { g_reqCb = cb; }
void projectm_set_preset_switch_failed_event_callback(projectm_handle, projectm_preset_switch_failed_event cb, void*) { g_failCb = cb; }
void projectm_set_hard_cut_enabled(projectm_handle, bool) {}
void projectm_set_beat_sensitivity(projectm_handle, float) {}
void projectm_set_preset_duration(projectm_handle, double) {}
void projectm_set_soft_cut_duration(projectm_handle, double) {}
void projectm_set_preset_locked(projectm_handle, bool l) { g_locked = l; }
void projectm_set_mesh_size(projectm_handle, size_t, size_t) { ++g_meshCalls; }
void projectm_set_texture_search_paths(projectm_handle, const char** paths, size_t count) {
  g_texturePathCalls.push_back(count ? paths[0] : "");
  g_loadsAtTextureCall = g_loaded.size(); }
size_t g_windowW = 0, g_windowH = 0; int g_windowSizeCalls = 0;
void projectm_set_window_size(projectm_handle, size_t w, size_t h) { g_windowW = w; g_windowH = h; ++g_windowSizeCalls; }
void projectm_set_fps(projectm_handle, int32_t) {}
unsigned int projectm_pcm_get_max_samples() { return 576; }
void projectm_pcm_add_uint8(projectm_handle, const uint8_t*, unsigned int n, projectm_channels) { g_pcmFed += n; }
int g_renderSleepMs = 0, g_renderSleepMsSmooth = 0;  // simulated render cost (smooth: during a soft cut)
int g_renderSpinMsSmooth = 0;  // simulated CPU-bound render cost during a soft cut (busy, not waiting)
bool g_requestInRender = false;  // like projectM: the timed switch request fires inside the render call
void projectm_opengl_render_frame(projectm_handle) {
  if (g_requestInRender) { g_requestInRender = false; g_reqCb(false, nullptr); }
  int ms = g_renderSleepMs; if (g_lastSmooth && g_renderSleepMsSmooth) ms = g_renderSleepMsSmooth;
  if (ms) std::this_thread::sleep_for(std::chrono::milliseconds(ms));
  if (g_lastSmooth && g_renderSpinMsSmooth) {
    auto until = std::chrono::steady_clock::now() + std::chrono::milliseconds(g_renderSpinMsSmooth);
    while (std::chrono::steady_clock::now() < until) {}
  } }
int g_fboFrames = 0;
void projectm_opengl_render_frame_fbo(projectm_handle p, uint32_t) { ++g_fboFrames; projectm_opengl_render_frame(p); }
uint32_t g_outgoingDivisor = 1;
void projectm_opengl_set_outgoing_preset_frame_divisor(projectm_handle, uint32_t d) { g_outgoingDivisor = d; }
uint32_t g_cacheHits = 0, g_cacheMisses = 0;
void projectm_opengl_program_cache_stats(uint32_t* hits, uint32_t* misses) { *hits = g_cacheHits; *misses = g_cacheMisses; }
char* projectm_get_version_string() { return strdup("4.1.0"); }
void projectm_free_string(const char* s) { free((void*)s); }
}

#include "native-lib.cpp"

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL %s:%d %s\n", __FILE__, __LINE__, #c); exit(1); } else printf("  ok: %s\n", #c); } while (0)
static void frame() { Java_com_example_projectm_visualizer_ProjectMJNI_onDrawFrame(nullptr, nullptr); }
static void feedAudio(uint8_t amp) { std::lock_guard<std::mutex> l(g_inputs.pcmMutex); for (int i = 0; i < 1024; ++i) g_inputs.pcm.push_back(128 + ((i & 1) ? amp : -amp)); g_inputs.audioLevel = amp / 128.f; g_inputs.audioLevelTime = NowSeconds(); }
static std::string current() { std::lock_guard<std::mutex> l(g_published.mutex); return g_published.currentPreset; }

int main(int argc, char** argv) {
  setvbuf(stdout, nullptr, _IONBF, 0);
  std::string root = argv[1], skip = root + "/skip.txt", texdir = root + "/extracted_textures";
  static AAssetManager am{root};
  g_library.Start(&am, skip, texdir);
  for (int i = 0; i < 200 && !g_library.Ready(); ++i) std::this_thread::sleep_for(std::chrono::milliseconds(5));

  printf("indexing from presets.idx\n");
  CHECK(g_library.Ready());
  CHECK(g_library.ActiveCount() == 13);   // 14 .milk entries (incl. .MILK and a CRLF line), others ignored, 1 pre-skipped

  printf("preset weights from presets.idx\n");
  CHECK(g_library.Weight("good 3.milk") == 40 && g_library.Weight("good 2.milk") == 2);
  CHECK(g_library.Weight("good 1.milk") == 0 && g_library.Weight("good 4.milk") == 0);
  CHECK(g_library.Weight("crlf.milk") == 7);  // CRLF line

  printf("indexing falls back to listing the folder without presets.idx\n");
  { std::string root2 = argv[2]; static AAssetManager am2{root2}; PresetLibrary& other = *new PresetLibrary();
    other.Start(&am2, root2 + "/skip.txt", "");  // never destroyed, like the app's library
    for (int i = 0; i < 200 && !other.Ready(); ++i) std::this_thread::sleep_for(std::chrono::milliseconds(5));
    CHECK(other.Ready() && other.ActiveCount() == 3); }
  CHECK(g_library.SkippedCount() == 1);

  printf("texture pack extracted before the index is ready\n");
  { FILE* f = fopen((texdir + "/worms.jpg").c_str(), "rb"); CHECK(f != nullptr); if (f) { fseek(f, 0, SEEK_END); CHECK(ftell(f) == 9); fclose(f); } }
  { FILE* f = fopen((texdir + "/clouds.jpg").c_str(), "rb"); CHECK(f != nullptr); if (f) fclose(f); }

  printf("first frame loads a preset (hard cut, no wait)\n");
  Java_com_example_projectm_visualizer_ProjectMJNI_onSurfaceCreated(nullptr, nullptr);
  Java_com_example_projectm_visualizer_ProjectMJNI_onSurfaceChanged(nullptr, nullptr, 1280, 720);
  frame();
  CHECK(!current().empty());
  CHECK(current() != "preskipped.milk");
  CHECK(g_texturePathCalls.size() == 1 && g_texturePathCalls[0] == texdir);
  CHECK(g_loadsAtTextureCall == 0);  // search path set before the first preset loaded
  CHECK(!g_locked);

  printf("settings from any thread\n");
  Java_com_example_projectm_visualizer_ProjectMJNI_setAutoChange(nullptr, nullptr, false); frame();
  CHECK(g_locked);
  Java_com_example_projectm_visualizer_ProjectMJNI_setAutoChange(nullptr, nullptr, true); frame();

  printf("commands\n");
  std::string a = current();
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  std::string b = current(); CHECK(b != a);
  Java_com_example_projectm_visualizer_ProjectMJNI_randomPreset(nullptr, nullptr, true); frame();
  std::string c = current(); CHECK(c != b);
  Java_com_example_projectm_visualizer_ProjectMJNI_previousPreset(nullptr, nullptr, true); frame();
  CHECK(current() == b);
  Java_com_example_projectm_visualizer_ProjectMJNI_previousPreset(nullptr, nullptr, true); frame();
  CHECK(current() == a);

  printf("projectM-requested auto switch (smooth), and forced hard cut before a resize\n");
  // A switch shows up as a successful load: after a reshuffle the same preset may legally come next.
  size_t loads = g_loaded.size(); g_reqCb(false, nullptr); frame();
  CHECK(g_loaded.size() == loads + 1);
  CHECK(g_lastSmooth);
  Java_com_example_projectm_visualizer_ProjectMJNI_setForceHardCut(nullptr, nullptr, true);
  loads = g_loaded.size(); g_reqCb(false, nullptr); frame();
  CHECK(g_loaded.size() == loads + 1 && !g_lastSmooth);
  g_reqCb(false, nullptr); frame();
  CHECK(g_lastSmooth);  // flag is one-shot

  printf("mesh size only re-applied when it changes\n");
  int meshCalls = g_meshCalls;
  Java_com_example_projectm_visualizer_ProjectMJNI_setSoftCutDuration(nullptr, nullptr, 5); frame();
  CHECK(g_meshCalls == meshCalls);
  Java_com_example_projectm_visualizer_ProjectMJNI_setMeshSize(nullptr, nullptr, 64, 48); frame();
  CHECK(g_meshCalls == meshCalls + 1);

  printf("broken presets are skipped and persisted, playback continues\n");
  for (int i = 0; i < 40; ++i) { Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame(); }
  CHECK(g_library.SkippedCount() == 3);    // pre-skipped + 2 broken
  CHECK(current().find("broken") == std::string::npos);
  { FILE* f = fopen(skip.c_str(), "r"); char line[256]; int n = 0; while (fgets(line, sizeof line, f)) ++n; fclose(f); CHECK(n == 3); }

  printf("next never shows the preset on screen again, also across reshuffles\n");
  { std::string before = current(); int repeats = 0;
    for (int i = 0; i < 200; ++i) {  // ~18 passes through the shuffled order
      Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
      if (current() == before) ++repeats;
      before = current();
    }
    CHECK(repeats == 0); }

  printf("audio is fed on the GL thread, capped to projectM's buffer\n");
  g_pcmFed = 0; feedAudio(60); frame(); CHECK(g_pcmFed == 576);

  printf("blank-preset skipping is off by default: a black preset with music stays\n");
  g_pixel = 5; int skippedAtStart = g_library.SkippedCount();
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  std::string unproven = current();
  for (int i = 0; i < 400; ++i) { feedAudio(60); frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }
  CHECK(current() == unproven && g_library.SkippedCount() == skippedAtStart);
  Java_com_example_projectm_visualizer_ProjectMJNI_setBlankDetection(nullptr, nullptr, true);

  printf("dark preset during silence is NOT skipped\n");
  g_pixel = 0; int skippedBefore = g_library.SkippedCount();
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  std::string dark = current();
  g_inputs.audioLevel = 0.f;
  for (int i = 0; i < 400; ++i) { frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }  // 8s
  CHECK(g_library.SkippedCount() == skippedBefore && current() == dark);

  printf("visible preset with music is NOT skipped\n");
  g_pixel = 200;
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  std::string bright = current();
  for (int i = 0; i < 400; ++i) { feedAudio(60); frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }
  CHECK(g_library.SkippedCount() == skippedBefore && current() == bright);

  printf("black preset with music is replaced at once, but only skipped for good the 2nd time\n");
  g_pixel = 5;
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  std::string black = current();
  for (int i = 0; i < 400 && current() == black; ++i) { feedAudio(60); frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }
  CHECK(current() != black);
  CHECK(g_library.SkippedCount() == skippedBefore);  // first strike: moved on, not listed
  { FILE* f = fopen((skip + ".blank").c_str(), "r"); CHECK(f != nullptr); char line[256] = {0}; CHECK(fgets(line, sizeof line, f) != nullptr); fclose(f);
    line[strcspn(line, "\r\n")] = 0; CHECK(black == line); }  // strike persisted
  Java_com_example_projectm_visualizer_ProjectMJNI_previousPreset(nullptr, nullptr, true); frame();
  CHECK(current() == black);  // shown again
  for (int i = 0; i < 400 && current() == black; ++i) { feedAudio(60); frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }
  CHECK(current() != black);
  CHECK(g_library.SkippedCount() == skippedBefore + 1);  // second strike: skipped

  printf("skip current preset (too slow) and blank-detection toggle\n");
  g_pixel = 200; int beforeSkip = g_library.SkippedCount(); std::string slow = current();
  Java_com_example_projectm_visualizer_ProjectMJNI_skipCurrentPreset(nullptr, nullptr); frame();
  CHECK(current() != slow && g_library.SkippedCount() == beforeSkip + 1);
  Java_com_example_projectm_visualizer_ProjectMJNI_setBlankDetection(nullptr, nullptr, false);
  g_pixel = 5; Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  std::string dim = current();
  for (int i = 0; i < 400; ++i) { feedAudio(60); frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }
  CHECK(current() == dim && g_library.SkippedCount() == beforeSkip + 1);
  Java_com_example_projectm_visualizer_ProjectMJNI_setBlankDetection(nullptr, nullptr, true);

  printf("everything black (rendering fault): after 3 black presets in a row nothing more is struck\n");
  g_pixel = 200;  // a visible preset resets the run of black ones
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  for (int i = 0; i < 200; ++i) { feedAudio(60); frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }
  g_pixel = 5; int skippedBeforeRun = g_library.SkippedCount();
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  int changes = 0; std::string onScreen = current();
  for (int i = 0; i < 2000 && changes < 4; ++i) {
    feedAudio(60); frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20));
    if (current() != onScreen) { ++changes; onScreen = current(); }
  }
  CHECK(changes == 3);  // three black presets moved on, the fourth stays
  CHECK(g_library.SkippedCount() <= skippedBeforeRun + 3);

  printf("reset skip list\n");
  Java_com_example_projectm_visualizer_ProjectMJNI_resetSkippedPresets(nullptr, nullptr);
  CHECK(g_library.SkippedCount() == 0 && g_library.ActiveCount() == 14);
  { FILE* f = fopen((skip + ".blank").c_str(), "r"); CHECK(f != nullptr); CHECK(fgetc(f) == EOF); fclose(f); }  // strikes cleared

  printf("context loss: new instance resumes the same preset, textures re-applied\n");
  g_pixel = 200; std::string shown = current();
  Java_com_example_projectm_visualizer_ProjectMJNI_onSurfaceCreated(nullptr, nullptr);
  Java_com_example_projectm_visualizer_ProjectMJNI_onSurfaceChanged(nullptr, nullptr, 1280, 720); frame();
  CHECK(current() == shown);
  CHECK(g_texturePathCalls.size() == 2);

  printf("black detection reads the window framebuffer, not projectM's\n");
  CHECK(g_readFbo == 7);  // the previous read binding is restored after sampling
  CHECK(g_packBuffer == 0 && g_mapped > 0);  // pixel pack buffer unbound again; results were collected
  CHECK(g_fences <= 1);                      // at most one read in flight, fences are deleted

  auto settle = [](int ms) { for (int i = 0; i < ms / 2; ++i) { frame(); std::this_thread::sleep_for(std::chrono::milliseconds(2)); } };
  Java_com_example_projectm_visualizer_ProjectMJNI_setSoftCutDuration(nullptr, nullptr, 5); frame();

  printf("lightweight: outgoing frame captured, projectM hard-cuts, overlay fades for min(transition, 3 s)\n");
  Java_com_example_projectm_visualizer_ProjectMJNI_setTransitionMode(nullptr, nullptr, 1, false);
  CHECK(Java_com_example_projectm_visualizer_ProjectMJNI_isLightweightTransition(nullptr, nullptr));
  int captures = g_captures, starts = g_fadeStarts; loads = g_loaded.size();
  g_requestInRender = true; frame();          // request fires during this frame's render
  CHECK(g_captures == captures + 1 && g_loaded.size() == loads);  // no switch yet
  frame();                                    // next frame switches
  CHECK(g_loaded.size() == loads + 1 && !g_lastSmooth);
  CHECK(g_fadeStarts == starts + 1 && g_fadeSeconds == 3.0 && g_engine.fade.Active());
  int draws = g_fadeDraws; frame(); CHECK(g_fadeDraws == draws + 1);

  printf("a remote-control switch ends the fade immediately\n");
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  CHECK(!g_engine.fade.Active());

  printf("beat-triggered hard cuts and forced hard cuts are never faded\n");
  captures = g_captures; starts = g_fadeStarts;
  g_reqCb(true, nullptr); frame(); frame();
  Java_com_example_projectm_visualizer_ProjectMJNI_setForceHardCut(nullptr, nullptr, true);
  g_requestInRender = true; frame(); frame();
  CHECK(g_captures == captures && g_fadeStarts == starts && !g_lastSmooth);

  printf("capture failure falls back to projectM's classic transition\n");
  g_captureOk = false; loads = g_loaded.size();
  g_requestInRender = true; frame(); frame();
  CHECK(g_loaded.size() == loads + 1 && g_lastSmooth && !g_engine.fade.Active());
  g_captureOk = true;

  printf("classic mode: projectM soft cut, no capture\n");
  Java_com_example_projectm_visualizer_ProjectMJNI_setTransitionMode(nullptr, nullptr, 2, true);
  CHECK(!Java_com_example_projectm_visualizer_ProjectMJNI_isLightweightTransition(nullptr, nullptr));
  captures = g_captures; loads = g_loaded.size();
  g_requestInRender = true; frame(); frame();
  CHECK(g_captures == captures && g_loaded.size() == loads + 1 && g_lastSmooth);

  printf("classic mode blends at the full render size\n");
  CHECK(g_windowW == 1280 && g_windowH == 720);

  // Waits until the running transition has ended and the render size is back to full.
  auto finishTransition = [&](int before) {
    for (int i = 0; i < 1500 && Java_com_example_projectm_visualizer_ProjectMJNI_getTransitionCounter(nullptr, nullptr) == before; ++i) frame();
    settle(400); };
  // Starts an automatic blend; returns the transition counter before it.
  auto startBlend = [&]() {
    int before = Java_com_example_projectm_visualizer_ProjectMJNI_getTransitionCounter(nullptr, nullptr);
    g_requestInRender = true; frame(); frame();
    return before; };

  printf("auto: blends render at 75%% into the off-screen target, stretched onto the surface\n");
  Java_com_example_projectm_visualizer_ProjectMJNI_setTransitionMode(nullptr, nullptr, 0, false);
  Java_com_example_projectm_visualizer_ProjectMJNI_setSoftCutDuration(nullptr, nullptr, 1);
  g_renderSleepMs = 1; g_renderSleepMsSmooth = 0;
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();  // hard cut: full size
  settle(1500);
  CHECK(!Java_com_example_projectm_visualizer_ProjectMJNI_isLightweightTransition(nullptr, nullptr));
  CHECK(g_windowW == 1280 && g_windowH == 720);
  int fboFrames = g_fboFrames, blits = g_blits;
  int transitions = startBlend();
  CHECK(g_lastSmooth && g_windowW == 960 && g_windowH == 540);
  CHECK(g_fboFrames > fboFrames && g_blits > blits);
  CHECK(g_blitSrcW == 960 && g_blitSrcH == 540 && g_blitDstW == 1280 && g_blitDstH == 720);
  finishTransition(transitions);
  CHECK(g_windowW == 1280 && g_windowH == 720);  // back to full size after the blend
  CHECK(Java_com_example_projectm_visualizer_ProjectMJNI_getBlendScalePercent(nullptr, nullptr) == 75);
  fboFrames = g_fboFrames; frame();
  CHECK(g_fboFrames == fboFrames);  // full size renders straight to the surface

  printf("auto: a blend far slower than before is lowered at once, and stays lower\n");
  settle(1500);
  g_renderSleepMsSmooth = 15;
  transitions = startBlend();
  CHECK(g_windowW == 960);
  for (int i = 0; i < 200 && g_windowW == 960; ++i) frame();
  CHECK(g_windowW == 768 && g_windowH == 432);  // 60%, during the same blend
  finishTransition(transitions);
  CHECK(Java_com_example_projectm_visualizer_ProjectMJNI_getBlendScalePercent(nullptr, nullptr) == 60);
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();  // fast frames before it
  settle(1500);
  transitions = startBlend();
  CHECK(g_windowW == 768);  // the next blend starts at the lower size
  finishTransition(transitions);
  CHECK(Java_com_example_projectm_visualizer_ProjectMJNI_getBlendScalePercent(nullptr, nullptr) == 50);
  g_renderSleepMs = g_renderSleepMsSmooth = 0;

  printf("auto: blends with frames to spare raise the resolution again (low-end devices start at 60%%)\n");
  Java_com_example_projectm_visualizer_ProjectMJNI_setTransitionMode(nullptr, nullptr, 0, true);
  g_renderSleepMs = g_renderSleepMsSmooth = 2;
  settle(1500);
  transitions = startBlend();
  CHECK(g_windowW == 768);
  finishTransition(transitions);
  for (int i = 0; i < 2; ++i) { settle(1500); finishTransition(startBlend()); }
  CHECK(Java_com_example_projectm_visualizer_ProjectMJNI_getBlendScalePercent(nullptr, nullptr) == 75);
  CHECK(!Java_com_example_projectm_visualizer_ProjectMJNI_isLightweightTransition(nullptr, nullptr));
  CHECK(Java_com_example_projectm_visualizer_ProjectMJNI_getLastTransitionFps(nullptr, nullptr) > 0.f);
  g_renderSleepMs = g_renderSleepMsSmooth = 0;

  printf("auto: a slow blend that is CPU-bound keeps its resolution (a lower one would not help)\n");
  Java_com_example_projectm_visualizer_ProjectMJNI_setTransitionMode(nullptr, nullptr, 0, false);
  g_renderSleepMs = 1; g_renderSleepMsSmooth = 0; g_renderSpinMsSmooth = 15;
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  settle(1500);
  transitions = startBlend();
  CHECK(g_windowW == 960);
  for (int i = 0; i < 40; ++i) frame();  // ~0.65 s: past the point where a slow blend is lowered
  CHECK(g_windowW == 960);  // not lowered during the blend
  CHECK(g_outgoingDivisor == 2);  // instead the outgoing preset renders every 2nd frame
  finishTransition(transitions);
  CHECK(Java_com_example_projectm_visualizer_ProjectMJNI_getBlendScalePercent(nullptr, nullptr) == 100);  // sharper instead
  g_renderSleepMs = g_renderSpinMsSmooth = 0;

  printf("the next preset's shaders are compiled in the background\n");
  CHECK(g_prewarmStarts >= 1 && !g_prewarmTextureDir.empty());
  CHECK(!g_prewarmRequests.empty() && g_prewarmRequests.back() == g_library.PeekNext());

  printf("output measurements: flat and still are logged, never skipped\n");
  {
    auto outputLine = [](const std::string& preset) {
      for (auto it = g_logLines.rbegin(); it != g_logLines.rend(); ++it)
        if (it->rfind("OUTPUT preset='" + preset + "'", 0) == 0) return *it;
      return std::string(); };
    g_pixel = 230; g_noise = 3;  // near-white with faint, unchanging texture
    Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
    std::string white = current();
    int skipped = g_library.SkippedCount();  // after the switch: it may skip a broken preset on the way
    for (int i = 0; i < 400; ++i) { feedAudio(60); frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }
    CHECK(current() == white && g_library.SkippedCount() == skipped);
    g_pixel = 60; g_noise = 120;  // varied picture (luma range > 12) that does not move
    Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
    std::string frozen = current();
    skipped = g_library.SkippedCount();
    std::string whiteLine = outputLine(white);
    printf("    %s\n", whiteLine.c_str());
    CHECK(whiteLine.find("flat=") != std::string::npos && whiteLine.find("flat=0/") == std::string::npos);
    CHECK(whiteLine.find("skipped=no") != std::string::npos);
    for (int i = 0; i < 400; ++i) { feedAudio(60); frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }
    CHECK(current() == frozen && g_library.SkippedCount() == skipped);
    g_noise = 0; g_pixel = 200;
    Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
    std::string frozenLine = outputLine(frozen);
    printf("    %s\n", frozenLine.c_str());
    CHECK(frozenLine.find("flat=0/") != std::string::npos && frozenLine.find("still=0/") == std::string::npos);
    CHECK(frozenLine.find("change_pct_avg=0.0") != std::string::npos);
  }

  printf("LOAD lines carry size, weight, shader size/loops and the memory taken\n");
  {
    Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
    std::string load;
    for (auto it = g_logLines.rbegin(); it != g_logLines.rend() && load.empty(); ++it)
      if (it->rfind("LOAD preset=", 0) == 0) load = *it;
    printf("    %s\n", load.c_str());
    CHECK(load.find(" size=1280x720 weight_mb=") != std::string::npos);
    CHECK(load.find(" shader_kb=") != std::string::npos && load.find(" loops=") != std::string::npos);
    CHECK(load.find(" avail_drop_mb=") != std::string::npos && load.find(" rss_growth_mb=") != std::string::npos);
    size_t bytes = 0; int loops = 0;
    ShaderStats("warp_1=`for (int i=0;i<3;i++) x+=1; // for(\ncomp_1=`y = tex2D(a,b); for(;;){}\nper_frame_1=for(\n",
                bytes, loops);
    CHECK(loops == 2 && bytes > 40 && bytes < 90);  // comments and non-shader lines ignored
    ShaderStats("warp_1=/*\r\nwarp_2=for(;;) {}\r\nwarp_3=*/\r\n", bytes, loops);
    CHECK(loops == 0 && bytes == 0);  // a loop inside a block comment spanning lines
    ShaderStats("warp_1=`a;\r\nwarpx=for(\ncomp_2=`for\ncomp_3=(;;)\n", bytes, loops);
    CHECK(loops == 1 && bytes == std::string("a;\nfor\n(;;)").size());  // same rules as gen-preset-index.py
  }

  printf("audio level getter\n");
  feedAudio(60);
  CHECK(Java_com_example_projectm_visualizer_ProjectMJNI_getAudioLevel(nullptr, nullptr) > 0.4f);
  g_inputs.audioLevelTime = NowSeconds() - 5;
  CHECK(Java_com_example_projectm_visualizer_ProjectMJNI_getAudioLevel(nullptr, nullptr) == 0.f);
  printf("ALL TESTS PASSED\n");
}
