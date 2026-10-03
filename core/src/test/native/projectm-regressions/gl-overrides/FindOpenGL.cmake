# Used only when the regression harness receives explicit EGL/GLES link flags.
# Keep the target global so the parent regression executable can share it.
if(NOT TARGET OpenGL::GLES3)
    add_library(OpenGL::GLES3 INTERFACE IMPORTED GLOBAL)
    if(GL_CFLAGS)
        target_compile_options(OpenGL::GLES3 INTERFACE "SHELL:${GL_CFLAGS}")
    endif()
    separate_arguments(GL_LINK_FLAGS NATIVE_COMMAND "${GL_LIBS}")
    target_link_libraries(OpenGL::GLES3 INTERFACE ${GL_LINK_FLAGS})
endif()
set(OpenGL_FOUND TRUE)
set(OpenGL_GLES3_FOUND TRUE)
