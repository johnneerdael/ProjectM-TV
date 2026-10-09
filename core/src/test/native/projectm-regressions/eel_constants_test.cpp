#include <projectm-eval.h>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string>

static void Check(bool ok, const std::string& message)
{
    if (!ok) throw std::runtime_error(message);
}
int main()
{
    auto memory = projectm_eval_memory_buffer_create();
    PRJM_EVAL_F registers[100]{};
    auto* context = projectm_eval_context_create(memory, &registers);
    try {
        static_assert(sizeof(PRJM_EVAL_F) == sizeof(double), "production evaluator must use double");
        Check(context != nullptr, "could not create real evaluator context");
        auto* result = projectm_eval_context_register_variable(context, "result");
        struct Case { const char* token; double expected; };
        for (const auto& c : {Case{"$pi",3.141592653589793}, Case{"$PI",3.141592653589793},
                             Case{"$e",2.71828183}, Case{"$E",2.71828183},
                             Case{"$phi",1.61803399}, Case{"$PHI",1.61803399},
                             Case{"3.141592653589793",3.141592653589793},
                             Case{"2.71828183",2.71828183}, Case{"1.61803399",1.61803399},
                             Case{".5",.5}, Case{".",0}})
        {
            const std::string source = std::string("result=") + c.token + ";";
            auto* code = projectm_eval_code_compile(context, source.c_str());
            Check(code != nullptr, "compile failed: " + source);
            projectm_eval_code_execute(code);
            projectm_eval_code_destroy(code);
            Check(*result == c.expected, std::string(c.token) + " rounded before double evaluation");
        }
        projectm_eval_context_destroy(context); projectm_eval_memory_buffer_destroy(memory);
        std::cout << "Named constants match exact original decimal expansions\n"; return 0;
    } catch (const std::exception& error) {
        if (context) projectm_eval_context_destroy(context);
        projectm_eval_memory_buffer_destroy(memory);
        std::cerr << error.what() << '\n'; return 1;
    }
}
