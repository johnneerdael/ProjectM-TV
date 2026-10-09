#include "WaveformPerPointContext.hpp"

#include "CustomWaveform.hpp"
#include "LegacyEquationCode.hpp"
#include "MilkdropPresetExceptions.hpp"
#include "WaveformPerFrameContext.hpp"

#include <Logging.hpp>

#define REG_VAR(var) \
    var = projectm_eval_context_register_variable(perPointCodeContext, #var);

namespace libprojectM {
namespace MilkdropPreset {

WaveformPerPointContext::WaveformPerPointContext(projectm_eval_mem_buffer gmegabuf, PRJM_EVAL_F (*globalRegisters)[100])
    : perPointCodeContext(projectm_eval_context_create(gmegabuf, globalRegisters))
{
}

WaveformPerPointContext::~WaveformPerPointContext()
{
    if (perPointCodeHandle != nullptr)
    {
        projectm_eval_code_destroy(perPointCodeHandle);
    }

    if (perPointCodeContext != nullptr)
    {
        projectm_eval_context_destroy(perPointCodeContext);
    }
}

void WaveformPerPointContext::RegisterBuiltinVariables()
{
    projectm_eval_context_reset_variables(perPointCodeContext);

    REG_VAR(time);
    REG_VAR(fps);
    REG_VAR(frame);
    REG_VAR(progress);

    for (int q = 0; q < QVarCount; q++)
    {
        std::string const qvar = "q" + std::to_string(q + 1);
        q_vars[q] = projectm_eval_context_register_variable(perPointCodeContext, qvar.c_str());
    }

    for (int t = 0; t < TVarCount; t++)
    {
        std::string const tvar = "t" + std::to_string(t + 1);
        t_vars[t] = projectm_eval_context_register_variable(perPointCodeContext, tvar.c_str());
    }

    REG_VAR(bass);
    REG_VAR(mid);
    REG_VAR(treb);
    REG_VAR(bass_att);
    REG_VAR(mid_att);
    REG_VAR(treb_att);
    REG_VAR(sample);
    REG_VAR(value1);
    REG_VAR(value2);
    REG_VAR(x);
    REG_VAR(y);
    REG_VAR(r);
    REG_VAR(g);
    REG_VAR(b);
    REG_VAR(a);
}

void WaveformPerPointContext::LoadReadOnlyStateVariables(const WaveformPerFrameContext& wavePerFrameContext)
{
    *time = *wavePerFrameContext.time;
    *frame = *wavePerFrameContext.frame;
    *fps = *wavePerFrameContext.fps;
    *progress = *wavePerFrameContext.progress;
    *bass = *wavePerFrameContext.bass;
    *mid = *wavePerFrameContext.mid;
    *treb = *wavePerFrameContext.treb;
    *bass_att = *wavePerFrameContext.bass_att;
    *mid_att = *wavePerFrameContext.mid_att;
    *treb_att = *wavePerFrameContext.treb_att;
}

void WaveformPerPointContext::CompilePerPointCode(const std::string& perPointCode,
                                                  const CustomWaveform& waveform)
{
    if (perPointCode.empty())
    {
        return;
    }

    std::string error;
    perPointCodeHandle = CompileEquationCode(perPointCodeContext, perPointCode, error);
    if (perPointCodeHandle == nullptr)
    {
        LOG_DEBUG("[WaveformPerPointContext] Failed custom wave " + std::to_string(waveform.m_index) + " per-point code:\n" + perPointCode);
        throw MilkdropCompileException("Could not compile custom wave " + std::to_string(waveform.m_index) + " per-point code: " + error);
    }
}

void WaveformPerPointContext::ExecutePerPointCode()
{
    if (perPointCodeHandle != nullptr)
    {
        projectm_eval_code_execute(perPointCodeHandle);
    }
}

} // namespace MilkdropPreset
} // namespace libprojectM
