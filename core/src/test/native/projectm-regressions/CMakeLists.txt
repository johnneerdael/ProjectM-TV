cmake_minimum_required(VERSION 3.22)
project(projectm_regressions VERSION 4.1.7 LANGUAGES C CXX)

if(NOT PROJECTM_SOURCE)
    message(FATAL_ERROR "PROJECTM_SOURCE must point to the patched projectM checkout")
endif()
option(SANITIZERS "Enable ASan/UBSan" ON)
if(SANITIZERS)
    add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address,undefined)
endif()
if(APPLE)
    # The app's GLES framebuffer-discard hint has no equivalent in macOS OpenGL 3.2.
    add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-include${CMAKE_CURRENT_SOURCE_DIR}/macos_gl.hpp>")
endif()
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(ENABLE_PLAYLIST OFF CACHE BOOL "" FORCE)
set(ENABLE_SYSTEM_PROJECTM_EVAL OFF CACHE BOOL "" FORCE)
set(ENABLE_SDL_UI OFF CACHE BOOL "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(CMAKE_DISABLE_FIND_PACKAGE_FLEX ON)
set(CMAKE_DISABLE_FIND_PACKAGE_BISON ON)
if(NOT APPLE)
    set(ENABLE_GLES ON CACHE BOOL "" FORCE)
    if(GL_LIBS)
        # projectM also calls find_package(OpenGL COMPONENTS GLES3). Use the same
        # supplied EGL/GLES flags for both consumers instead of system discovery.
        list(PREPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/gl-overrides")
        set(REGRESSION_GL_TARGET OpenGL::GLES3)
    else()
        find_package(PkgConfig REQUIRED)
        pkg_check_modules(EGL REQUIRED IMPORTED_TARGET egl)
        set(REGRESSION_GL_TARGET PkgConfig::EGL)
        if(GL_CFLAGS)
            add_compile_options("SHELL:${GL_CFLAGS}")
        endif()
    endif()
endif()
add_subdirectory("${PROJECTM_SOURCE}" projectm)
add_executable(projectm-regressions regression_test.cpp)
add_executable(random-texture-regressions random_texture_test.cpp)
target_compile_features(projectm-regressions PRIVATE cxx_std_17)
target_compile_definitions(projectm-regressions PRIVATE GL_SILENCE_DEPRECATION)
target_include_directories(projectm-regressions PRIVATE
    "${PROJECTM_SOURCE}/src/libprojectM"
    "${PROJECTM_SOURCE}/vendor/hlslparser/src"
    "${PROJECTM_SOURCE}/vendor"
    "${PROJECTM_SOURCE}/vendor/projectm-eval/projectm-eval/api")
target_link_libraries(projectm-regressions PRIVATE libprojectM::projectM)
if(NOT APPLE)
    target_compile_definitions(projectm-regressions PRIVATE USE_GLES)
    target_link_libraries(projectm-regressions PRIVATE ${REGRESSION_GL_TARGET})
endif()
enable_testing()
add_executable(float-literal-regressions float_literal_test.cpp)
target_compile_features(float-literal-regressions PRIVATE cxx_std_17)
target_include_directories(float-literal-regressions PRIVATE "${PROJECTM_SOURCE}/vendor/hlslparser/src")
target_link_libraries(float-literal-regressions PRIVATE libprojectM::projectM)
add_test(NAME float-literal-regressions COMMAND float-literal-regressions)
set_tests_properties(float-literal-regressions PROPERTIES TIMEOUT 10 ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0")
target_compile_features(random-texture-regressions PRIVATE cxx_std_17)
target_compile_definitions(random-texture-regressions PRIVATE GL_SILENCE_DEPRECATION)
target_compile_definitions(random-texture-regressions PRIVATE
    BUNDLED_ASSETS="${CMAKE_CURRENT_SOURCE_DIR}/../../../main/assets")
target_include_directories(random-texture-regressions PRIVATE
    "${PROJECTM_SOURCE}/src/libprojectM"
    "${PROJECTM_SOURCE}/src/libprojectM/MilkdropPreset"
    "${PROJECTM_SOURCE}/vendor"
    "${PROJECTM_SOURCE}/vendor/projectm-eval/projectm-eval/api")
target_include_directories(random-texture-regressions PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../../tools/preset-lab/src/preset_lab/native")
target_link_libraries(random-texture-regressions PRIVATE libprojectM::projectM)
if(NOT APPLE)
    target_compile_definitions(random-texture-regressions PRIVATE USE_GLES)
    target_link_libraries(random-texture-regressions PRIVATE ${REGRESSION_GL_TARGET})
endif()
foreach(control manager stages shorthand numerical lifecycle blur-framebuffers midgit-render)
    add_test(NAME random-texture-${control} COMMAND random-texture-regressions
        ${control} "${CMAKE_CURRENT_BINARY_DIR}/textures-${control}")
    set_tests_properties(random-texture-${control} PROPERTIES TIMEOUT 30
        ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0;EGL_PLATFORM=surfaceless")
endforeach()
find_package(Python3 REQUIRED COMPONENTS Interpreter)
add_executable(shader-parser-regressions shader_parser_test.cpp)
target_compile_features(shader-parser-regressions PRIVATE cxx_std_17)
target_include_directories(shader-parser-regressions PRIVATE "${PROJECTM_SOURCE}/vendor/hlslparser/src")
target_link_libraries(shader-parser-regressions PRIVATE libprojectM::projectM)
add_test(NAME shader-parser-regressions COMMAND shader-parser-regressions)
set_tests_properties(shader-parser-regressions PROPERTIES
    TIMEOUT 10 ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0")
add_test(NAME hlsl-self-reference COMMAND projectm-regressions macro)
add_test(NAME custom-waveform-bounds COMMAND projectm-regressions waveform)
add_test(NAME shader-render-regressions COMMAND projectm-regressions shader-render)
add_test(NAME float-literal-render COMMAND projectm-regressions float-render "${CMAKE_CURRENT_SOURCE_DIR}/float-literal-control.milk")
set_tests_properties(float-literal-render PROPERTIES TIMEOUT 30 ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0;EGL_PLATFORM=surfaceless")
add_test(NAME parser-presets COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/check_preset_hashes.py"
    "$<TARGET_FILE:projectm-regressions>" parser-presets
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../main/assets"
    "${CMAKE_CURRENT_SOURCE_DIR}/parser-presets.tsv")
# A broken self-referencing macro grows indefinitely; stop it before it exhausts memory.
set_tests_properties(hlsl-self-reference custom-waveform-bounds shader-render-regressions parser-presets PROPERTIES
    TIMEOUT 30 ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0;EGL_PLATFORM=surfaceless")

add_executable(implicit-global-regressions implicit_global_test.cpp)
target_compile_features(implicit-global-regressions PRIVATE cxx_std_17)
target_include_directories(implicit-global-regressions PRIVATE "${PROJECTM_SOURCE}/vendor/hlslparser/src")
target_link_libraries(implicit-global-regressions PRIVATE libprojectM::projectM)
add_test(NAME implicit-global-regressions COMMAND implicit-global-regressions)
set_tests_properties(implicit-global-regressions PROPERTIES TIMEOUT 10 ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0")

add_test(NAME implicit-input-bindings COMMAND projectm-regressions implicit-bindings)
set_tests_properties(implicit-input-bindings PROPERTIES TIMEOUT 30 ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0;EGL_PLATFORM=surfaceless")

add_test(NAME initialization-presets COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/check_preset_hashes.py"
    "$<TARGET_FILE:projectm-regressions>" initialization-presets
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../main/assets"
    "${CMAKE_CURRENT_SOURCE_DIR}/initialization-presets.tsv")
set_tests_properties(initialization-presets PROPERTIES TIMEOUT 30 ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0;EGL_PLATFORM=surfaceless")

add_test(NAME float-literal-presets COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/check_preset_hashes.py"
    "$<TARGET_FILE:projectm-regressions>" float-presets
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../main/assets"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../../../../tools/milk-analyzer/fixtures/float-literal-presets.json")
set_tests_properties(float-literal-presets PROPERTIES TIMEOUT 120 ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0;EGL_PLATFORM=surfaceless")
