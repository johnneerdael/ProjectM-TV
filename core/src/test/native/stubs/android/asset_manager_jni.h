#pragma once
#include <jni.h>
#include "asset_manager.h"
extern "C" AAssetManager* AAssetManager_fromJava(JNIEnv*, jobject);
