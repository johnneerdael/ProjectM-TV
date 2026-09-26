cmake_minimum_required(VERSION 3.22.1)

project(projectmtv)

find_library(log-lib log)
find_library(GLESv3-lib GLESv3)
find_library(android-lib android)

# projectM is built from source: the git submodule third_party/projectm (pinned release, see
# docs/THIRD_PARTY.md) plus the patches in tools/projectm-patches. It is linked statically into
# libprojectmtv.so, so the APK holds one native library and one C++ runtime. The playlist library
# is not built: the app manages its own shuffled preset list straight from the APK assets.
set(REPO_ROOT ${CMAKE_CURRENT_SOURCE_DIR}/../../../..)
set(PROJECTM_SOURCE ${REPO_ROOT}/third_party/projectm)
if(NOT EXISTS ${PROJECTM_SOURCE}/CMakeLists.txt OR NOT EXISTS ${PROJECTM_SOURCE}/vendor/projectm-eval/CMakeLists.txt)
    message(FATAL_ERROR "projectM sources missing: run `git submodule update --init --recursive`")
endif()

# Apply our patches once (a patch that already applies in reverse is in place).
find_package(Git REQUIRED)
file(GLOB PROJECTM_PATCHES ${REPO_ROOT}/tools/projectm-patches/*.patch)
list(SORT PROJECTM_PATCHES)
foreach(patch IN LISTS PROJECTM_PATCHES)
    execute_process(COMMAND ${GIT_EXECUTABLE} apply --reverse --check ${patch}
        WORKING_DIRECTORY ${PROJECTM_SOURCE} RESULT_VARIABLE applied OUTPUT_QUIET ERROR_QUIET)
    if(NOT applied EQUAL 0)
        execute_process(COMMAND ${GIT_EXECUTABLE} apply ${patch}
            WORKING_DIRECTORY ${PROJECTM_SOURCE} RESULT_VARIABLE result)
        if(NOT result EQUAL 0)
            message(FATAL_ERROR "projectM patch does not apply: ${patch}")
        endif()
        message(STATUS "Applied projectM patch ${patch}")
    endif()
endforeach()

set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(ENABLE_PLAYLIST OFF CACHE BOOL "" FORCE)
set(ENABLE_SYSTEM_PROJECTM_EVAL OFF CACHE BOOL "" FORCE)
set(ENABLE_SYSTEM_GLM OFF CACHE BOOL "" FORCE)
set(ENABLE_SDL_UI OFF CACHE BOOL "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)  # static projectM ends up in a shared library
add_subdirectory(${PROJECTM_SOURCE} projectm EXCLUDE_FROM_ALL)

add_library(projectmtv SHARED native-lib.cpp snapshot_fade.cpp)

# Always optimise the JNI layer, also in debug builds that are sideloaded onto TVs.
target_compile_options(projectmtv PRIVATE -O2 -Wall -Wextra -Wno-unused-parameter)

target_link_libraries(projectmtv
    libprojectM::projectM
    ${log-lib}
    ${GLESv3-lib}
    ${android-lib}
)

set_target_properties(projectmtv PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
)
