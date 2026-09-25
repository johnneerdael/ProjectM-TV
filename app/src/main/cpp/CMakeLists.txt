cmake_minimum_required(VERSION 3.22.1)

project(projectmtv)

find_library(log-lib log)
find_library(GLESv3-lib GLESv3)
find_library(android-lib android)

# Prebuilt projectM 4.1 core library (the playlist library is no longer used: the app manages
# its own shuffled preset list straight from the APK assets).
add_library(projectM-4 SHARED IMPORTED)
set_target_properties(projectM-4 PROPERTIES
    IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libprojectM-4.so
)

add_library(projectmtv SHARED native-lib.cpp snapshot_fade.cpp)

target_include_directories(projectmtv PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../jniLibs/include
)

# Always optimise the JNI layer, also in debug builds that are sideloaded onto TVs.
target_compile_options(projectmtv PRIVATE -O2 -Wall -Wextra -Wno-unused-parameter)

target_link_libraries(projectmtv
    projectM-4
    ${log-lib}
    ${GLESv3-lib}
    ${android-lib}
)

set_target_properties(projectmtv PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
)
