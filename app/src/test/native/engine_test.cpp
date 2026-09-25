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
#include "GLES2/gl2.h"
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
int __android_log_print(int, const char* tag, const char* fmt, ...) { va_list ap; va_start(ap, fmt); vfprintf(stderr, fmt, ap); fputc('\n', stderr); va_end(ap); return 0; }
int __system_property_get(const char* name, char* value) {
  if (strcmp(name, "vendor.display-size") == 0) { strcpy(value, "3840x2160"); return 9; }
  value[0] = 0; return 0; }
// ---- fake GL ----
unsigned char g_pixel = 0;
void glViewport(GLint, GLint, GLsizei, GLsizei) {}
void glReadPixels(GLint, GLint, GLsizei w, GLsizei h, GLenum, GLenum, GLvoid* out) { memset(out, g_pixel, (size_t)w * h * 4); }
// ---- fake projectM ----
struct projectm {};
static projectm_preset_switch_failed_event g_failCb; static projectm_preset_switch_requested_event g_reqCb;
std::vector<std::string> g_loaded; bool g_locked = false; size_t g_pcmFed = 0;
bool g_lastSmooth = false; int g_meshCalls = 0;
std::vector<std::string> g_texturePathCalls; size_t g_loadsAtTextureCall = 0;
projectm_handle projectm_create() { return new projectm; }
void projectm_destroy(projectm_handle p) { delete p; }
void projectm_load_preset_data(projectm_handle, const char* data, bool smooth) {
  g_lastSmooth = smooth;
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
void projectm_set_window_size(projectm_handle, size_t, size_t) {}
void projectm_set_fps(projectm_handle, int32_t) {}
unsigned int projectm_pcm_get_max_samples() { return 576; }
void projectm_pcm_add_uint8(projectm_handle, const uint8_t*, unsigned int n, projectm_channels) { g_pcmFed += n; }
void projectm_opengl_render_frame(projectm_handle) {}
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

  printf("indexing\n");
  CHECK(g_library.Ready());
  CHECK(g_library.ActiveCount() == 12);   // 13 .milk files (incl. .MILK), .DS_Store/.txt ignored, 1 pre-skipped
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
  std::string before = current(); g_reqCb(false, nullptr); frame();
  CHECK(current() != before);
  CHECK(g_lastSmooth);
  Java_com_example_projectm_visualizer_ProjectMJNI_setForceHardCut(nullptr, nullptr, true);
  before = current(); g_reqCb(false, nullptr); frame();
  CHECK(current() != before && !g_lastSmooth);
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

  printf("audio is fed on the GL thread, capped to projectM's buffer\n");
  g_pcmFed = 0; feedAudio(60); frame(); CHECK(g_pcmFed == 576);

  printf("dark preset during silence is NOT skipped\n");
  g_pixel = 0; int skippedBefore = g_library.SkippedCount();
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  std::string dark = current();
  g_inputs.audioLevel = 0.f;
  for (int i = 0; i < 300; ++i) { frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }  // 6s
  CHECK(g_library.SkippedCount() == skippedBefore && current() == dark);

  printf("visible preset with music is NOT skipped\n");
  g_pixel = 200;
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  std::string bright = current();
  for (int i = 0; i < 300; ++i) { feedAudio(60); frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }
  CHECK(g_library.SkippedCount() == skippedBefore && current() == bright);

  printf("black preset with music IS skipped and replaced\n");
  g_pixel = 5;
  Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  std::string black = current();
  for (int i = 0; i < 300 && current() == black; ++i) { feedAudio(60); frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }
  CHECK(current() != black);
  CHECK(g_library.SkippedCount() == skippedBefore + 1);

  printf("skip current preset (too slow) and blank-detection toggle\n");
  g_pixel = 200; int beforeSkip = g_library.SkippedCount(); std::string slow = current();
  Java_com_example_projectm_visualizer_ProjectMJNI_skipCurrentPreset(nullptr, nullptr); frame();
  CHECK(current() != slow && g_library.SkippedCount() == beforeSkip + 1);
  Java_com_example_projectm_visualizer_ProjectMJNI_setBlankDetection(nullptr, nullptr, false);
  g_pixel = 5; Java_com_example_projectm_visualizer_ProjectMJNI_nextPreset(nullptr, nullptr, true); frame();
  std::string dim = current();
  for (int i = 0; i < 300; ++i) { feedAudio(60); frame(); std::this_thread::sleep_for(std::chrono::milliseconds(20)); }
  CHECK(current() == dim && g_library.SkippedCount() == beforeSkip + 1);
  Java_com_example_projectm_visualizer_ProjectMJNI_setBlankDetection(nullptr, nullptr, true);

  printf("reset skip list\n");
  Java_com_example_projectm_visualizer_ProjectMJNI_resetSkippedPresets(nullptr, nullptr);
  CHECK(g_library.SkippedCount() == 0 && g_library.ActiveCount() == 13);

  printf("context loss: new instance resumes the same preset, textures re-applied\n");
  g_pixel = 200; std::string shown = current();
  Java_com_example_projectm_visualizer_ProjectMJNI_onSurfaceCreated(nullptr, nullptr); frame();
  CHECK(current() == shown);
  CHECK(g_texturePathCalls.size() == 2);

  printf("audio level getter\n");
  feedAudio(60);
  CHECK(Java_com_example_projectm_visualizer_ProjectMJNI_getAudioLevel(nullptr, nullptr) > 0.4f);
  g_inputs.audioLevelTime = NowSeconds() - 5;
  CHECK(Java_com_example_projectm_visualizer_ProjectMJNI_getAudioLevel(nullptr, nullptr) == 0.f);
  printf("ALL TESTS PASSED\n");
}
