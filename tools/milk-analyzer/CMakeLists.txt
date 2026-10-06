cmake_minimum_required(VERSION 3.22)
project(milk_code_reader LANGUAGES C CXX)
if(NOT ENGINE_BUILD OR NOT ENGINE_SOURCE)
    message(FATAL_ERROR "Pass the existing production preset-lab ENGINE_BUILD and ENGINE_SOURCE")
endif()
option(SANITIZERS "Match the host regression archive sanitizer setting" ON)
if(SANITIZERS)
    add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address,undefined)
endif()
find_library(ENGINE_ARCHIVE NAMES projectM-4d projectM-4
    PATHS "${ENGINE_BUILD}/projectm/src/libprojectM" NO_DEFAULT_PATH REQUIRED)
if(NOT ENGINE_IDENTITY_FILE)
    set(ENGINE_IDENTITY_FILE "${ENGINE_BUILD}/build-identity.json")
endif()
file(READ "${ENGINE_IDENTITY_FILE}" ENGINE_IDENTITY_TEXT)

add_executable(milk-audio-inputs native_audio.cpp)
target_compile_features(milk-audio-inputs PRIVATE cxx_std_17)
target_compile_definitions(milk-audio-inputs PRIVATE PROJECTM_STATIC_DEFINE)
target_include_directories(milk-audio-inputs PRIVATE
    "${CMAKE_CURRENT_BINARY_DIR}"
    "${CMAKE_CURRENT_SOURCE_DIR}/../preset-lab/src/preset_lab/native"
    "${ENGINE_SOURCE}/src/libprojectM" "${ENGINE_SOURCE}/src/api/include"
    "${ENGINE_SOURCE}/vendor/projectm-eval/projectm-eval"
    "${ENGINE_BUILD}/projectm/src/api/include")
target_link_libraries(milk-audio-inputs PRIVATE "${ENGINE_ARCHIVE}")
if(NOT APPLE)
    find_package(OpenSSL REQUIRED)
    target_link_libraries(milk-audio-inputs PRIVATE OpenSSL::Crypto)
endif()
add_executable(milk-native-reader native_reader.cpp)
if(EXISTS "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/LegacyEquationCode.hpp")
    target_compile_definitions(milk-native-reader PRIVATE MILK_HAS_LEGACY_EQUATION_CODE=1)
endif()
file(READ "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/Shaders/PresetShaderHeaderGlsl330.inc" SHADER_HEADER_TEXT)
file(SHA256 "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/Shaders/PresetShaderHeaderGlsl330.inc" SHADER_HEADER_SHA)
file(SHA256 "${ENGINE_ARCHIVE}" ENGINE_ARCHIVE_SHA)
file(READ "${ENGINE_SOURCE}/vendor/hlslparser/src/Engine.cpp" FLOAT_FORMATTER_TEXT)
file(SHA256 "${ENGINE_SOURCE}/vendor/hlslparser/src/Engine.cpp" FLOAT_FORMATTER_SHA)
string(FIND "${FLOAT_FORMATTER_TEXT}" "std::numeric_limits<float>::max_digits10" FLOAT_ROUNDTRIP_POSITION)
if(FLOAT_ROUNDTRIP_POSITION EQUAL -1)
    set(FLOAT_LITERAL_POLICY "six-significant-digits-v1")
else()
    set(FLOAT_LITERAL_POLICY "float32-roundtrip-v1")
endif()
file(READ "${ENGINE_SOURCE}/vendor/hlslparser/src/GLSLGenerator.cpp" ARRAY_GENERATOR_TEXT)
file(SHA256 "${ENGINE_SOURCE}/vendor/hlslparser/src/GLSLGenerator.cpp" ARRAY_GENERATOR_SHA)
string(FIND "${ARRAY_GENERATOR_TEXT}" "void GLSLGenerator::OutputArrayInitializer(" GROUPED_ARRAY_POSITION)
if(GROUPED_ARRAY_POSITION EQUAL -1)
    set(ARRAY_INITIALIZER_POLICY "legacy-layout-v1")
else()
    set(ARRAY_INITIALIZER_POLICY "grouped-elements-v1")
endif()
file(READ "${ENGINE_SOURCE}/vendor/hlslparser/src/HLSLTree.h" TREE_HEADER_TEXT)
string(FIND "${TREE_HEADER_TEXT}" "HLSLTypeFlag_ImplicitUniform" IMPLICIT_POSITION)
if(IMPLICIT_POSITION EQUAL -1)
    set(IMPLICIT_GLOBAL_POLICY "strict-v1")
else()
    set(IMPLICIT_GLOBAL_POLICY "projectmtv-implicit-extern-zero-v1")
endif()
file(GLOB RANDOM_CONTRACT_SOURCES "${ENGINE_SOURCE}/src/libprojectM/Renderer/Texture*.cpp"
    "${ENGINE_SOURCE}/src/libprojectM/Renderer/Texture*.hpp"
    "${ENGINE_SOURCE}/src/libprojectM/Renderer/Sampler.cpp"
    "${ENGINE_SOURCE}/src/libprojectM/Renderer/Sampler.hpp"
    "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/MilkdropShader.hpp"
    "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/PresetState.hpp"
    "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/MilkdropShader.cpp"
    "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/MilkdropPreset.cpp"
    "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/PerPixelMesh.cpp"
    "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/PerPixelMesh.hpp")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${RANDOM_CONTRACT_SOURCES}
    "${CMAKE_CURRENT_SOURCE_DIR}/random_binding_contract.py" "${CMAKE_CURRENT_SOURCE_DIR}/sampling_policy.py"
    "${ENGINE_ARCHIVE}")
find_package(Python3 REQUIRED COMPONENTS Interpreter)
execute_process(COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/random_binding_contract.py"
    --engine "${ENGINE_SOURCE}" OUTPUT_VARIABLE RANDOM_BINDING_CONTRACT_TEXT
    OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ERROR_IS_FATAL ANY)
configure_file(reader_inputs.hpp.in reader_inputs.hpp @ONLY)
target_compile_features(milk-native-reader PRIVATE cxx_std_17)
target_compile_definitions(milk-native-reader PRIVATE PROJECTM_STATIC_DEFINE ENGINE_SOURCE_DIR="${ENGINE_SOURCE}")
target_include_directories(milk-native-reader PRIVATE
    "${CMAKE_CURRENT_BINARY_DIR}"
    "${CMAKE_CURRENT_SOURCE_DIR}/../preset-lab/src/preset_lab/native"
    "${ENGINE_SOURCE}/src/libprojectM" "${ENGINE_SOURCE}/vendor/hlslparser/src"
    "${ENGINE_SOURCE}/vendor/projectm-eval/projectm-eval" "${ENGINE_SOURCE}/src/api/include"
    "${ENGINE_SOURCE}/vendor/projectm-eval/projectm-eval/api"
    "${ENGINE_BUILD}/projectm/src/api/include")
target_link_libraries(milk-native-reader PRIVATE "${ENGINE_ARCHIVE}")
if(APPLE)
    target_link_libraries(milk-native-reader PRIVATE "-framework CoreFoundation" "-framework OpenGL")
endif()

find_package(Python3 REQUIRED COMPONENTS Interpreter)
file(SHA256 "${ENGINE_SOURCE}/vendor/SOIL2/stb_image.h" IMAGE_DECODER_SHA)
file(SHA256 "${ENGINE_SOURCE}/vendor/SOIL2/SOIL2.c" SOIL_SOURCE_SHA)
file(SHA256 "${ENGINE_SOURCE}/src/libprojectM/Renderer/TextureManager.cpp" TEXTURE_MANAGER_SHA)
configure_file(image_inputs.hpp.in image_inputs.hpp @ONLY)
add_executable(milk-image-inputs native_image.cpp "${ENGINE_SOURCE}/vendor/SOIL2/etc1_utils.c")
target_compile_features(milk-image-inputs PRIVATE cxx_std_17)
target_include_directories(milk-image-inputs PRIVATE "${CMAKE_CURRENT_BINARY_DIR}"
    "${ENGINE_SOURCE}/vendor/SOIL2" "${CMAKE_CURRENT_SOURCE_DIR}/../preset-lab/src/preset_lab/native")
execute_process(COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/generate_random_adapter.py"
    --engine "${ENGINE_SOURCE}" --output "${CMAKE_CURRENT_BINARY_DIR}/cpu_random_adapter.hpp"
    COMMAND_ERROR_IS_FATAL ANY)
add_executable(milk-shader-random native_random.cpp)
target_compile_features(milk-shader-random PRIVATE cxx_std_17)
target_include_directories(milk-shader-random PRIVATE "${CMAKE_CURRENT_BINARY_DIR}"
    "${ENGINE_SOURCE}/vendor" "${CMAKE_CURRENT_SOURCE_DIR}/../preset-lab/src/preset_lab/native")
execute_process(COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/generate_composite_adapter.py"
    --engine "${ENGINE_SOURCE}" --output "${CMAKE_CURRENT_BINARY_DIR}/cpu_composite_adapter.hpp"
    COMMAND_ERROR_IS_FATAL ANY)
add_executable(milk-composite-inputs native_composite.cpp)
target_compile_features(milk-composite-inputs PRIVATE cxx_std_17)
target_include_directories(milk-composite-inputs PRIVATE "${CMAKE_CURRENT_BINARY_DIR}"
    "${ENGINE_SOURCE}/src/libprojectM"
    "${CMAKE_CURRENT_SOURCE_DIR}/../preset-lab/src/preset_lab/native")
execute_process(COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/generate_shader_adapter.py"
    --engine "${ENGINE_SOURCE}" --output "${CMAKE_CURRENT_BINARY_DIR}/cpu_shader_adapter.hpp"
    COMMAND_ERROR_IS_FATAL ANY)
add_executable(milk-shader-translate native_shader.cpp)
target_compile_features(milk-shader-translate PRIVATE cxx_std_17)
target_compile_definitions(milk-shader-translate PRIVATE PROJECTM_STATIC_DEFINE)
target_include_directories(milk-shader-translate PRIVATE "${CMAKE_CURRENT_BINARY_DIR}"
    "${CMAKE_CURRENT_SOURCE_DIR}/../preset-lab/src/preset_lab/native"
    "${ENGINE_SOURCE}/src/libprojectM" "${ENGINE_SOURCE}/vendor/hlslparser/src"
    "${ENGINE_SOURCE}/src/api/include" "${ENGINE_BUILD}/projectm/src/api/include")
target_link_libraries(milk-shader-translate PRIVATE "${ENGINE_ARCHIVE}")
if(APPLE)
    target_link_libraries(milk-shader-translate PRIVATE "-framework CoreFoundation" "-framework OpenGL")
endif()

# Compile unchanged native CPU math bodies, replacing only GL-owning state
# includes and the namespace. Keep originals and adapted content identities.
set(CPU_WAVE_DIR "${CMAKE_CURRENT_BINARY_DIR}/cpu-wave-source")
file(MAKE_DIRECTORY "${CPU_WAVE_DIR}/Waveforms")
file(GLOB WAVE_INPUTS CONFIGURE_DEPENDS "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/Waveforms/*.cpp"
    "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/Waveforms/*.hpp")
list(APPEND WAVE_INPUTS "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/WaveformMode.hpp"
    "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/Constants.hpp")
# Patched waveform CPU math also uses the shared quad-line geometry helper.
# Copy/hash it with the same namespace adaptation as the waveform bodies.
if(EXISTS "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/LineGeometry.hpp")
    list(APPEND WAVE_INPUTS "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/LineGeometry.hpp"
        "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset/LineGeometry.cpp")
endif()
set(WAVE_SOURCE_HASHES "{")
set(CPU_WAVE_SOURCES)
foreach(INPUT IN LISTS WAVE_INPUTS)
    file(RELATIVE_PATH RELATIVE "${ENGINE_SOURCE}/src/libprojectM/MilkdropPreset" "${INPUT}")
    file(READ "${INPUT}" CONTENT)
    file(SHA256 "${INPUT}" SOURCE_SHA)
    string(REPLACE "libprojectM" "milk_wave_cpu" CONTENT "${CONTENT}")
    string(REGEX REPLACE "#include \"(PresetState.hpp|PerFrameContext.hpp|Renderer/RenderItem.hpp)\""
        "#include \"cpu_wave_state.hpp\"" CONTENT "${CONTENT}")
    if(RELATIVE STREQUAL "LineGeometry.cpp")
        string(PREPEND CONTENT "#include \"cpu_wave_state.hpp\"\n")
    endif()
    file(WRITE "${CPU_WAVE_DIR}/${RELATIVE}" "${CONTENT}")
    file(SHA256 "${CPU_WAVE_DIR}/${RELATIVE}" ADAPTED_SHA)
    string(APPEND WAVE_SOURCE_HASHES "\"${RELATIVE}\":{\"original\":\"${SOURCE_SHA}\",\"adapted\":\"${ADAPTED_SHA}\"},")
    if(RELATIVE MATCHES "\\.cpp$")
        list(APPEND CPU_WAVE_SOURCES "${CPU_WAVE_DIR}/${RELATIVE}")
    endif()
endforeach()
string(REGEX REPLACE ",$" "}" WAVE_SOURCE_HASHES "${WAVE_SOURCE_HASHES}")
file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/cpu_wave_state.hpp" CPU_WAVE_ADAPTER_SHA)
file(SHA256 "${ENGINE_SOURCE}/src/libprojectM/Renderer/RenderContext.hpp" RENDER_CONTEXT_SHA)
configure_file(cpu_wave_inputs.hpp.in cpu_wave_inputs.hpp @ONLY)
add_executable(milk-wave-inputs native_wave.cpp ${CPU_WAVE_SOURCES})
target_compile_features(milk-wave-inputs PRIVATE cxx_std_17)
target_compile_definitions(milk-wave-inputs PRIVATE PROJECTM_STATIC_DEFINE)
target_include_directories(milk-wave-inputs PRIVATE "${CMAKE_CURRENT_BINARY_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}"
    "${CPU_WAVE_DIR}" "${CPU_WAVE_DIR}/Waveforms" "${ENGINE_SOURCE}/src/libprojectM"
    "${ENGINE_SOURCE}/src/api/include" "${ENGINE_BUILD}/projectm/src/api/include"
    "${CMAKE_CURRENT_SOURCE_DIR}/../preset-lab/src/preset_lab/native")

# Public/protected native CPU generators, linked to the exact existing archive.
# OpenGL resolves the archive's unused texture-upload symbols; no GL context or
# GL function is used by this executable's generation path.
add_executable(milk-noise-inputs native_noise.cpp)
target_compile_features(milk-noise-inputs PRIVATE cxx_std_17)
target_compile_definitions(milk-noise-inputs PRIVATE PROJECTM_STATIC_DEFINE)
target_include_directories(milk-noise-inputs PRIVATE
    "${CMAKE_CURRENT_BINARY_DIR}"
    "${CMAKE_CURRENT_SOURCE_DIR}/../preset-lab/src/preset_lab/native"
    "${ENGINE_SOURCE}/src/libprojectM" "${ENGINE_SOURCE}/src/api/include"
    "${ENGINE_BUILD}/projectm/src/api/include")
target_link_libraries(milk-noise-inputs PRIVATE "${ENGINE_ARCHIVE}")
if(APPLE)
    target_link_libraries(milk-noise-inputs PRIVATE "-framework CoreFoundation" "-framework OpenGL")
else()
    find_package(OpenGL REQUIRED)
    find_package(OpenSSL REQUIRED)
    target_link_libraries(milk-noise-inputs PRIVATE OpenGL::GL OpenSSL::Crypto)
endif()

if(NOT APPLE)
    find_package(OpenGL REQUIRED)
    target_link_libraries(milk-native-reader PRIVATE OpenGL::GL)
    target_link_libraries(milk-shader-translate PRIVATE OpenGL::GL)
endif()
