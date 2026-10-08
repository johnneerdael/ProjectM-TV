#include <projectm-eval.h>
#include <cmath>
#include <iostream>
#include <iomanip>
#include <limits>
#include <string>
#include <vector>
#include <algorithm>
#include <stdexcept>
struct Case { std::string name, code; double a,b,expected; bool unsafe=false; };
static int Run(const std::string& issue,bool baseline) {
    static_assert(sizeof(PRJM_EVAL_F)==sizeof(double),"canonical production controls require the double evaluator");
    const double inf=std::numeric_limits<double>::infinity(), nan=std::numeric_limits<double>::quiet_NaN();
    std::vector<Case> cases;
    if(issue=="I03") {
        cases.push_back({"literal division witness","q=1/.000001;",0,0,1e6});
        cases.push_back({"literal power witness","q=pow(.000001,-1);",0,0,1e6});
        for(auto op: {std::string("q=a/b;"),std::string("q=_div(a,b);"),std::string("q=(a/=b);"),std::string("q=_divop(a,b);")}) {
            cases.push_back({op+" tiny positive",op,1,1e-6,1e6});
            cases.push_back({op+" tiny negative",op,1,-1e-6,-1e6});
            cases.push_back({op+" zero",op,1,0,0});
            cases.push_back({op+" negative zero",op,1,-0.0,0});
            cases.push_back({op+" boundary",op,1,1e-5,1/1e-5});
            cases.push_back({op+" ordinary",op,1,1e-4,1e4});
            cases.push_back({op+" suppressed overflow",op,1e308,1e-6,0});
            cases.push_back({op+" outside overflow",op,1e308,1e-4,inf});
            cases.push_back({op+" invalid numerator",op,inf,1e-6,0});
            cases.push_back({op+" nan numerator",op,nan,1e-6,0});
            cases.push_back({op+" tiny/tiny",op,1e-300,1e-300,1});
        }
        for(auto op: {std::string("q=pow(a,b);"),std::string("q=a^b;"),std::string("q=(a^=b);"),std::string("q=_powop(a,b);")}) {
            cases.push_back({op+" reciprocal",op,1e-6,-1,1e6});
            cases.push_back({op+" negative reciprocal",op,-1e-6,-1,-1e6});
            cases.push_back({op+" negative square",op,-1e-6,-2,1e12});
            cases.push_back({op+" positive exponent",op,1e-6,1,1e-6});
            cases.push_back({op+" zero",op,0,-1,0});
            cases.push_back({op+" invalid fraction",op,-1e-6,-.5,0});
            cases.push_back({op+" suppressed overflow",op,1e-300,-2,0});
            cases.push_back({op+" outside overflow",op,1e-4,-100,inf});
            cases.push_back({op+" negative infinity exponent",op,1e-6,-inf,0});
            cases.push_back({op+" boundary",op,1e-5,-1,std::pow(1e-5,-1)});
        }
        cases.push_back({"division RHS assignment alias","q=(a/=a);",1e-6,0,1});
        cases.push_back({"power RHS assignment alias","q=(a^=a);",1e-6,0,std::pow(1e-6,1e-6)});
        cases.push_back({"division argument side effect","q=_div(a,b=b+.000001);",1,1e-6,5e5});
    } else if(issue=="boundaries") {
        for(auto op:{std::string("q=pow(a,b);"),std::string("q=a^b;"),std::string("q=(a^=b);"),std::string("q=_powop(a,b);")}) {
            cases.push_back({op+" outside invalid fraction restored",op,-1,.5,0});
            cases.push_back({op+" outside NaN exponent restored",op,2,nan,0});
            cases.push_back({op+" outside overflow retained",op,2,1024,inf});
            cases.push_back({op+" outside finite unchanged",op,2,3,8});
        }
        cases.push_back({"outside division NaN retained","q=a/b;",nan,2,nan});
        cases.push_back({"outside division Infinity retained","q=a/b;",inf,2,inf});
        cases.push_back({"invsqrt NaN guard restored","q=invsqrt(a);",nan,0,0});
        cases.push_back({"invsqrt ordinary unchanged","q=invsqrt(a);",1,0,0.99830814271181434});
    } else {
        cases.push_back({"literal remainder witness","q=(-5)%2;",0,0,1});
        cases.push_back({"literal assignment witness","a=-5;q=(a%=2);",0,0,1});
        for(auto op: {std::string("q=a%b;"),std::string("q=_mod(a,b);"),std::string("q=(a%=b);"),std::string("q=_modop(a,b);")}) {
            for(double a: {-5.0,5.0}) for(double b: {-2.0,2.0}) cases.push_back({op+" signs",op,a,b,1});
            cases.push_back({op+" exact multiple",op,-4,2,0});
            cases.push_back({op+" fraction truncation",op,-5.9,2.9,1});
            cases.push_back({op+" fraction divisor zero",op,-5,.9,0});
            cases.push_back({op+" upper original boundary",op,-2147483647.9,2,1});
            cases.push_back({op+" excluded original boundary",op,-2147483648.0,3,-2});
            cases.push_back({op+" wide unchanged",op,-4294967297.0,2,-1});
            cases.push_back({op+" wide denominator unchanged",op,-5,4294967296.0,-5});
            cases.push_back({op+" signed minimum safe",op,-9223372036854775808.0,3,-2});
            cases.push_back({op+" signed minimum/-1",op,-9223372036854775808.0,-1,0,true});
            cases.push_back({op+" out of range",op,9223372036854775808.0,2,0,true});
            cases.push_back({op+" infinite",op,inf,2,0,true});
            cases.push_back({op+" nan",op,nan,2,0,true});
            cases.push_back({op+" infinite divisor",op,5,inf,0,true});
            cases.push_back({op+" nan divisor",op,5,nan,0,true});
        }
        cases.push_back({"remainder assignment alias","q=(a%=a);",-5,0,0});
        cases.push_back({"remainder argument side effect","q=_mod(a,b=b+1);",-5,1,1});
    }
    int failed=0, executed=0, skipped=0;
    std::cout << std::setprecision(17);
    for(const auto& c:cases) {
        if(baseline&&c.unsafe) { skipped++; continue; }
        auto memory=projectm_eval_memory_buffer_create(); PRJM_EVAL_F registers[100]{};
        auto* context=projectm_eval_context_create(memory,&registers);
        auto* a=projectm_eval_context_register_variable(context,"a"); auto* b=projectm_eval_context_register_variable(context,"b");
        auto* q=projectm_eval_context_register_variable(context,"q"); *a=c.a; *b=c.b;
        auto* code=projectm_eval_code_compile(context,c.code.c_str());
        if(!code) { std::cout<<"COMPILE FAIL "<<c.code<<'\n';failed++; }
        else {
            projectm_eval_code_execute(code);executed++;
            bool pass=std::isnan(c.expected)?std::isnan(*q):(std::isinf(c.expected)?*q==c.expected:std::isfinite(*q)&&std::abs(*q-c.expected)<=1e-12*std::max(1.0,std::abs(c.expected)));
            if(c.code.find("a/=")!=std::string::npos||c.code.find("a^=")!=std::string::npos||c.code.find("a%=")!=std::string::npos||c.code.find("op(a,b)")!=std::string::npos) pass=pass&&*a==*q;
            if(c.code.find("b=b+")!=std::string::npos) pass=pass&&*b==(c.b+(issue=="I03"?1e-6:1));
            if(!pass) failed++;
            std::cout<<(pass?"PASS ":"FAIL ")<<c.name<<" q="<<*q<<" a="<<*a<<" b="<<*b<<" expected="<<c.expected<<'\n';
            projectm_eval_code_destroy(code);
        }
        projectm_eval_context_destroy(context);projectm_eval_memory_buffer_destroy(memory);
    }
    std::cout<<issue<<" executed="<<executed<<" failures="<<failed<<" unsafe_baseline_skips="<<skipped<<'\n';return failed?1:0;
}

// New integrated alias/side-effect cases have explicit storage expectations.
// No predicate relies on relaxed/finite-only compiler assumptions in this test TU.
static bool Equal(double actual,double expected){return std::isnan(expected)?std::isnan(actual):std::isinf(expected)?actual==expected:std::isfinite(actual)&&std::abs(actual-expected)<=1e-12*std::max(1.,std::abs(expected));}
static int Aliases()
{
    struct Alias{const char* name;const char* code;double a,b,q,storedA,storedB;};
    const Alias cases[]={
      {"division both argument effects once","q=_div(a=a+1,b=b+.000001);",0,1e-6,5e5,1,2e-6},
      {"division RHS updates prior variable pointer","q=_div(a,b=(a=a+.000001));",1e-6,0,1,2e-6,2e-6},
      {"division assignment RHS mutates lhs","q=(a/=(a=a+.000001));",1e-6,0,1,1,0},
      {"power argument effect once","q=pow(a,b=b-1);",1e-6,0,1e6,1e-6,-1},
      {"power assignment argument effect once","q=(a^=(b=b-1));",1e-6,0,1e6,1e6,-1},
      {"power RHS mutates lhs alias","q=(a^=(a=-1));",1e-6,0,-1,-1,0},
      {"remainder both argument effects once","q=_mod(a=a-1,b=b+1);",-4,1,1,-5,2},
      {"remainder assignment RHS mutates lhs","q=(a%=(a=-2));",-5,1,0,0,1},
      {"remainder RHS updates prior variable pointer","q=_mod(a,b=(a=-2));",-5,1,0,-2,-2},
      {"combined divide assignment then remainder","q=(a/=.000001)%2;",1,0,0,1e6,0},
      {"combined reciprocal then remainder","q=pow(.000001,-1)%3;",0,0,1,0,0},
      {"combined signed remainder then division","q=(-5)%2/.000001;",0,0,1e6,0,0},
      {"combined remainder assignment effect then division","q=(a%=(b=b+1))/.000001;",-5,1,1e6,1,2}
    };
    int failures=0;
    for(const auto& test:cases){
        auto memory=projectm_eval_memory_buffer_create();PRJM_EVAL_F registers[100]{};
        auto* context=projectm_eval_context_create(memory,&registers);
        if(!context)throw std::runtime_error("real evaluator context allocation failed");
        auto* a=projectm_eval_context_register_variable(context,"a");auto* b=projectm_eval_context_register_variable(context,"b");auto* q=projectm_eval_context_register_variable(context,"q");
        *a=test.a;*b=test.b;auto* code=projectm_eval_code_compile(context,test.code);
        bool pass=code!=nullptr;
        if(code){projectm_eval_code_execute(code);pass=Equal(*q,test.q)&&Equal(*a,test.storedA)&&Equal(*b,test.storedB);projectm_eval_code_destroy(code);}
        std::cout<<(pass?"PASS ":"FAIL ")<<test.name<<" q="<<*q<<" a="<<*a<<" b="<<*b<<'\n';
        failures+=!pass;projectm_eval_context_destroy(context);projectm_eval_memory_buffer_destroy(memory);
    }
    std::cout<<"aliases executed=13 failures="<<failures<<'\n';return failures?1:0;
}
int main(int argc,char** argv)
{
    try{
        const std::string family=argc>1?argv[1]:"all";const bool baseline=argc>2&&std::string(argv[2])=="baseline";
        if(argc>3||(argc>2&&!baseline))throw std::runtime_error("usage:eel-arithmetic-controls [all|I03|I04|boundaries|aliases] [baseline]");
        int failed=0;
        if(family=="all"){for(const auto& group:{"I03","I04","boundaries"})failed|=Run(group,baseline);failed|=Aliases();}
        else if(family=="aliases")failed=Aliases();
        else if(family=="I03"||family=="I04"||family=="boundaries")failed=Run(family,baseline);
        else throw std::runtime_error("unknown arithmetic control family");
        return failed?1:0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
