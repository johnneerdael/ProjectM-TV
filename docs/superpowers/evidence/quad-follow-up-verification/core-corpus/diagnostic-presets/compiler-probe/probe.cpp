#include <projectm-eval.h>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
extern "C" void projectm_eval_memory_host_lock_mutex() {}
extern "C" void projectm_eval_memory_host_unlock_mutex() {}
std::string legacy(const std::string& input) {
    std::string output; bool comment=false;
    for (size_t i=0;i<input.size();++i) {
        const char c=input[i];
        if (comment) { if(c=='\n')comment=false; continue; }
        if (i+1<input.size() && ((c=='/'&&input[i+1]=='/') || (c=='\\'&&input[i+1]=='\\'))) { comment=true; continue; }
        if(c!='\n')output+=c;
    }
    return output;
}
void compile(const std::string& mode,const std::string& source) {
    auto* context=projectm_eval_context_create(nullptr,nullptr);
    auto* code=projectm_eval_code_compile(context,source.c_str());int line=0,column=0;
    const char* error=projectm_eval_get_error(context,&line,&column);
    std::cout<<"{\"mode\":"<<std::quoted(mode)<<",\"compiled\":"<<(code?"true":"false")<<",\"error\":"<<std::quoted(error?error:"")<<",\"line\":"<<line<<",\"column\":"<<column<<"}\n";
    if(code)projectm_eval_code_destroy(code);projectm_eval_context_destroy(context);
}
int main(int argc,char** argv) {
    if(argc!=2)return 2;
    std::ifstream input(argv[1]);if(!input)return 3;std::ostringstream data;data<<input.rdbuf();
    compile("projectM_newlines",data.str());compile("MilkDrop_record_join",legacy(data.str()));
}
