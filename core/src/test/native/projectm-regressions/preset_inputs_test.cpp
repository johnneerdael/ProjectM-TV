#include "gl_context.hpp"
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PerPixelContext.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <cmath>
#include <iostream>
#include <stdexcept>

using namespace libprojectM::MilkdropPreset;
static void Check(bool ok, const char* message)
{
    if (!ok) throw std::runtime_error(message);
}
int main()
{
    try {
        GLContext gl;
        PresetState state;
        auto& render = state.renderContext;
        render.perPixelMeshX = 48; render.perPixelMeshY = 32;
        PerFrameContext frame(state.globalMemory, &state.globalRegisters);
        frame.RegisterBuiltinVariables();
        PerPixelContext pixel(state.globalMemory, &state.globalRegisters);
        pixel.RegisterBuiltinVariables(); pixel.CompilePerPixelCode("dx=aspecty/10;dy=aspectx/10;");
        for (int profile : {0,1,2,3})
        {
            render.viewportSizeX = profile == 1 ? 144 : profile == 2 ? 256 : profile == 3 ? 3840 : 256;
            render.viewportSizeY = profile == 1 ? 256 : profile == 2 ? 256 : profile == 3 ? 2160 : 144;
            render.aspectX = profile == 1 ? .5625f : 1;
            render.aspectY = profile == 0 || profile == 3 ? .5625f : 1;
            render.invAspectX = 1.f/render.aspectX; render.invAspectY = 1.f/render.aspectY;
            render.lineReferenceWidth = profile == 3 ? 1280 : 0;
            render.lineReferenceHeight = profile == 3 ? 720 : 0;
            frame.LoadStateVariables(state); pixel.LoadStateReadOnlyVariables(state, frame);
            pixel.ExecutePerPixelCode();
            Check(*pixel.aspectx == render.invAspectX && *pixel.aspecty == render.invAspectY,
                  "per-pixel aspect inputs omit original inverse factors");
            Check(*frame.aspectx == *pixel.aspectx && *frame.aspecty == *pixel.aspecty,
                  "per-frame and per-pixel aspect contracts disagree");
            Check(std::abs(*pixel.dx - render.invAspectY/10.) < 1e-12 &&
                  std::abs(*pixel.dy - render.invAspectX/10.) < 1e-12, "equation did not consume inverse aspect");
            Check(*pixel.meshx == 48 && *pixel.meshy == 32, "mesh inputs changed");
            if (profile == 3) Check(*pixel.pixelsx == 1280 && *pixel.pixelsy == 720,
                                   "Native shader-canvas inputs changed");
            else Check(*pixel.pixelsx == render.viewportSizeX && *pixel.pixelsy == render.viewportSizeY,
                       "authored pixel inputs changed");
        }
        std::cout << "Per-pixel inverse aspect and retained canvas inputs pass\n"; return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
