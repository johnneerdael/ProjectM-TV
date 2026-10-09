cmake_minimum_required(VERSION 3.22)
project(shader_input_controls VERSION 4.2.0 LANGUAGES C CXX)
if(NOT PROJECTM_SOURCE)
    message(FATAL_ERROR "PROJECTM_SOURCE must name the already-patched production engine")
endif()
set(REGRESSION_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../../core/src/test/native/projectm-regressions")
option(SANITIZERS "Use the repository native-control sanitizer policy" ON)
# Reuse repository engine configuration/platform shims without modifying its CMake or helpers.
add_subdirectory("${REGRESSION_ROOT}" existing-controls EXCLUDE_FROM_ALL)
add_executable(shader-input-controls shader_input_controls.cpp)
target_compile_features(shader-input-controls PRIVATE cxx_std_17)
target_compile_definitions(shader-input-controls PRIVATE GL_SILENCE_DEPRECATION)
target_include_directories(shader-input-controls PRIVATE
    "${REGRESSION_ROOT}"
    "${PROJECTM_SOURCE}/src/libprojectM"
    "${PROJECTM_SOURCE}/vendor/glad/include"
    "${PROJECTM_SOURCE}/vendor"
    "${PROJECTM_SOURCE}/vendor/projectm-eval/projectm-eval/api")
target_link_libraries(shader-input-controls PRIVATE libprojectM::projectM ${CMAKE_DL_LIBS})
if(SANITIZERS)
    target_compile_options(shader-input-controls PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer)
    target_link_options(shader-input-controls PRIVATE -fsanitize=address,undefined)
endif()
if(APPLE)
    find_library(SHADER_INPUT_OPENGL_FRAMEWORK OpenGL REQUIRED)
    target_compile_options(shader-input-controls PRIVATE "-include${REGRESSION_ROOT}/macos_gl.hpp")
    target_link_libraries(shader-input-controls PRIVATE "${SHADER_INPUT_OPENGL_FRAMEWORK}")
else()
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(SHADER_INPUT_EGL REQUIRED IMPORTED_TARGET egl)
    target_compile_definitions(shader-input-controls PRIVATE USE_GLES)
    target_link_libraries(shader-input-controls PRIVATE PkgConfig::SHADER_INPUT_EGL)
    if(GL_CFLAGS)
        target_compile_options(shader-input-controls PRIVATE "SHELL:${GL_CFLAGS}")
    endif()
endif()
enable_testing()
add_test(NAME shader-input-controls COMMAND shader-input-controls
    "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_BINARY_DIR}/compiled-proof")
set_tests_properties(shader-input-controls PROPERTIES TIMEOUT 60
    ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0;EGL_PLATFORM=surfaceless")
