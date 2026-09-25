#pragma once
#include <sys/types.h>
typedef struct AAssetManager AAssetManager; typedef struct AAssetDir AAssetDir; typedef struct AAsset AAsset;
enum { AASSET_MODE_BUFFER = 3 };
extern "C" { AAssetDir* AAssetManager_openDir(AAssetManager*, const char*); const char* AAssetDir_getNextFileName(AAssetDir*); void AAssetDir_close(AAssetDir*);
AAsset* AAssetManager_open(AAssetManager*, const char*, int); const void* AAsset_getBuffer(AAsset*); off_t AAsset_getLength(AAsset*); void AAsset_close(AAsset*); }
