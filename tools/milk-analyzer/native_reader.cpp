// Native syntax bridge only. No renderer, OpenGL context, frames or music input.
#include "MilkdropPreset/PresetFileParser.hpp"
#include "Utils.hpp"
#include "HLSLParser.h"
#include "HLSLTree.h"
#include "Engine.h"
#include "vendor/json.hpp"
#include "reader_inputs.hpp"
extern "C" {
#include "CompileContext.h"
#include "TreeFunctions.h"
#include "TreeVariables.h"
}
#ifdef MILK_HAS_LEGACY_EQUATION_CODE
#include "MilkdropPreset/LegacyEquationCode.hpp"
#endif
#include <fstream>
#include <sstream>
#include <iostream>
#include <map>
#include <regex>
#include <set>
#include <stdexcept>
#include <chrono>
#include <cmath>
#include <unistd.h>
#include <memory>

using json=nlohmann::json;
using namespace M4;
using libprojectM::MilkdropPreset::PresetFileParser;

// The native HLSL parser logs to stdout. Keep diagnostics separate from machine-readable JSON.
class ParserDiagnostics {
    int saved;
public:
    ParserDiagnostics():saved(dup(STDOUT_FILENO)) {
        if(saved<0||dup2(STDERR_FILENO,STDOUT_FILENO)<0)throw std::runtime_error("cannot route parser diagnostics");
    }
    ~ParserDiagnostics(){std::fflush(stdout);dup2(saved,STDOUT_FILENO);close(saved);}
};

std::string milkdropEquationSource(const std::string& code) {
#ifdef MILK_HAS_LEGACY_EQUATION_CODE
    return libprojectM::MilkdropPreset::AssembleLegacyEquationCode(code);
#else
    // MilkDrop 2.25c state.cpp: ReadCode + StripLinefeedCharsAndComments.
    // Remove numbered-line boundaries, not other whitespace; preserve split identifiers/numbers.
    // The original implementation also recognizes both // and double-backslash line comments.
    std::string result;bool comment=false;
    for(size_t i=0;i<code.size();++i) {
        if(comment){if(code[i]=='\n')comment=false;continue;}
        if(i+1<code.size()&&((code[i]=='/'&&code[i+1]=='/')||(code[i]=='\\'&&code[i+1]=='\\'))){comment=true;continue;}
        if(code[i]!='\n'&&code[i]!='\r')result+=code[i];
    }
    return result;
#endif
}

json numericValue(PRJM_EVAL_F value) {
    if(std::isfinite(value))return value;
    return {{"ieee",std::isnan(value)?"nan":std::signbit(value)?"negative_infinity":"positive_infinity"}};
}

struct EquationContext {
    prjm_eval_compiler_context_t* context;
    explicit EquationContext(PRJM_EVAL_F (*registers)[100]):context(prjm_eval_create_compile_context(nullptr,registers)) {
        if(!context)throw std::runtime_error("cannot create equation execution context");
    }
    ~EquationContext(){prjm_eval_destroy_compile_context(context);}
};

struct EquationProgram {
    std::shared_ptr<EquationContext> owner;
    prjm_eval_compiler_context_t* context;
    prjm_eval_program_t* program=nullptr;
    explicit EquationProgram(std::shared_ptr<EquationContext> scope):owner(std::move(scope)),context(owner->context) {}
    ~EquationProgram(){if(program)prjm_eval_destroy_code(program);}
};

json executeEquations(const json& request) {
    ParserDiagnostics diagnostics;
    PRJM_EVAL_F registers[100]{};
    std::map<std::string,std::shared_ptr<EquationContext>> scopes;
    std::map<std::string,std::unique_ptr<EquationProgram>> programs;
    for(const auto& entry:request.at("programs").items()) {
        auto scopeName=entry.value().is_string()?entry.key():entry.value().value("scope",entry.key());
        if(scopeName.empty())throw std::runtime_error("empty equation scope");
        auto& scope=scopes[scopeName];
        if(!scope)scope=std::make_shared<EquationContext>(&registers);
        auto compiled=std::make_unique<EquationProgram>(scope);
        auto source=entry.value().is_string()?entry.value().get<std::string>():entry.value().at("code").get<std::string>();
        auto assembly=entry.value().is_string()?std::string("legacy"):entry.value().value("assembly",std::string("legacy"));
        if(assembly=="legacy")source=milkdropEquationSource(source);
        else if(assembly!="raw")throw std::runtime_error("unsupported equation assembly policy: "+assembly);
        compiled->program=prjm_eval_compile_code(compiled->context,source.c_str());
        if(!compiled->program)throw std::runtime_error("equation execution compile error: "+entry.key());
        programs.emplace(entry.key(),std::move(compiled));
    }
    auto inputValue=[&programs](const json& value)->PRJM_EVAL_F {
        if(value.is_number())return value.get<PRJM_EVAL_F>();
        auto& source=*programs.at(value.at("program").get<std::string>());
        auto name=value.at("variable").get<std::string>();
        return *prjm_eval_register_variable(source.context,name.c_str());
    };
    json result={{"steps",json::array()},{"numeric_bits",sizeof(PRJM_EVAL_F)*8},{"basis","native equation execution; no rendered input"}};
    for(const auto& step:request.at("steps")) {
        auto& selected=*programs.at(step.at("program").get<std::string>());
        auto variables=step.value("variables",json::object());
        for(const auto& entry:variables.items())
            *prjm_eval_register_variable(selected.context,entry.key().c_str())=inputValue(entry.value());
        if(step.contains("wave_points")) {
            const auto& wave=step.at("wave_points");auto& frame=*programs.at(wave.at("frame_program").get<std::string>());
            auto frameValue=[&](const char* name){return *prjm_eval_register_variable(frame.context,name);};
            double requested=frameValue("samples");
            if(!std::isfinite(requested)||requested<INT32_MIN||requested>INT32_MAX)throw std::runtime_error("custom wave sample count domain unresolved");
            bool spectrum=wave.at("spectrum").get<bool>();int maximum=spectrum?512:480;
            int count=std::min(maximum,static_cast<int>(requested));
            json group={{"sample_count",count},{"points",json::array()}};
            if(count<2){result["steps"].push_back(group);continue;}
            auto left=wave.at("left").get<std::vector<float>>(),right=wave.at("right").get<std::vector<float>>();
            if(left.size()!=maximum||right.size()!=maximum)throw std::runtime_error("custom wave native audio array size mismatch");
            for(float value:left)if(!std::isfinite(value))throw std::runtime_error("nonfinite custom wave audio");
            for(float value:right)if(!std::isfinite(value))throw std::runtime_error("nonfinite custom wave audio");
            int separation=wave.at("separation").get<int>();
            int offset1=spectrum?0:(maximum-count)/2-separation/2;
            int offset2=spectrum?0:(maximum-count)/2+separation/2;
            int64_t spectrumSpan=static_cast<int64_t>(maximum)-separation;
            if(spectrum&&(spectrumSpan<INT32_MIN||spectrumSpan>INT32_MAX))throw std::runtime_error("custom wave spectrum span overflow");
            float stride=spectrum?static_cast<float>(spectrumSpan)/count:1.f;
            float mix1=std::pow(wave.at("smoothing").get<float>()*.98f,.5f),mix2=1.f-mix1;
            float multiplier=wave.at("scaling").get<float>()*wave.at("preset_wave_scale").get<float>()*(spectrum?.15f:.004f);
            if(!std::isfinite(stride)||!std::isfinite(mix1)||!std::isfinite(multiplier))throw std::runtime_error("custom wave audio domain unresolved");
            auto read=[&](const std::vector<float>& data,int index){if(index<0||index>=maximum)throw std::runtime_error("custom wave audio index out of bounds");return data[index];};
            std::vector<float> smoothL(count),smoothR(count);smoothL[0]=read(left,offset1);smoothR[0]=read(right,offset2);
            for(int i=1;i<count;++i) {
                float coordinate=static_cast<float>(i)*stride;
                if(!std::isfinite(coordinate)||static_cast<double>(coordinate)<INT32_MIN||static_cast<double>(coordinate)>INT32_MAX)throw std::runtime_error("custom wave audio index domain unresolved");
                smoothL[i]=read(left,static_cast<int>(coordinate)+offset1)*mix2+smoothL[i-1]*mix1;
                smoothR[i]=read(right,static_cast<int>(coordinate)+offset2)*mix2+smoothR[i-1]*mix1;
            }
            for(int i=count-2;i>=0;--i){smoothL[i]=smoothL[i]*mix2+smoothL[i+1]*mix1;smoothR[i]=smoothR[i]*mix2+smoothR[i+1]*mix1;}
            float sampleScale=1.f/static_cast<float>(count-1);
            for(int i=0;i<count;++i) {
                float value1=smoothL[i]*multiplier,value2=smoothR[i]*multiplier;
                if(!std::isfinite(value1)||!std::isfinite(value2))throw std::runtime_error("nonfinite smoothed custom wave input");
                for(auto entry:std::initializer_list<std::pair<const char*,double>>{{"sample",static_cast<float>(i)*sampleScale},{"value1",value1},{"value2",value2},{"x",.5f+value1},{"y",.5f+value2}})
                    *prjm_eval_register_variable(selected.context,entry.first)=entry.second;
                for(auto name:{"r","g","b","a"})*prjm_eval_register_variable(selected.context,name)=frameValue(name);
                PRJM_EVAL_F value=0,*returned=&value;if(selected.program->program)selected.program->program->func(selected.program->program,&returned);
                json captured=json::object();for(const auto& name:step.value("capture",json::array())) {
                    std::string key=name;captured[key]=numericValue(*prjm_eval_register_variable(selected.context,key.c_str()));
                }group["points"].push_back(captured);
            }
            result["steps"].push_back(group);continue;
        }
        int repeat=step.value("repeat",1);
        if(repeat<1||repeat>4096)throw std::runtime_error("equation repeat count outside 1..4096");
        for(int iteration=0;iteration<repeat;++iteration) {
            auto resets=step.value("reset_variables",json::object());
            for(const auto& entry:resets.items())
                *prjm_eval_register_variable(selected.context,entry.key().c_str())=inputValue(entry.value());
            if(step.contains("instance_variable"))
                *prjm_eval_register_variable(selected.context,step.at("instance_variable").get<std::string>().c_str())=iteration;
            PRJM_EVAL_F value=0,*returned=&value;
            if(selected.program->program)selected.program->program->func(selected.program->program,&returned);
            json values=json::object();
            for(const auto& name:step.value("capture",json::array())) {
                std::string key=name;
                values[key]=numericValue(*prjm_eval_register_variable(selected.context,key.c_str()));
            }
            result["steps"].push_back(values);
        }
    }
    return result;
}

class EquationTree {
    PRJM_EVAL_F registers[100]{};
    prjm_eval_compiler_context_t* context;
    std::map<prjm_eval_expr_func_t*,std::string> functions;
    std::map<PRJM_EVAL_F*,std::string> variables;
    json node(prjm_eval_exptreenode_t* expr) {
        if(!expr) return nullptr;
        if(expr->func==prjm_eval_func_const) {
            json value=numericValue(expr->value);
            return {{"kind","constant"},{"value",value}};
        }
        if(expr->func==prjm_eval_func_var) {
            auto found=variables.find(expr->var);
            if(found==variables.end()) throw std::runtime_error("unresolved native equation variable");
            return {{"kind","variable"},{"name",found->second}};
        }
        auto found=functions.find(expr->func);
        if(found==functions.end()) throw std::runtime_error("unresolved native equation opcode");
        json result={{"kind","call"},{"function",found->second},{"args",json::array()},{"instructions",json::array()}};
        if(expr->args) for(auto p=expr->args;*p;++p) result["args"].push_back(node(*p));
        for(auto item=expr->list;item;item=item->next) result["instructions"].push_back(node(item->expr));
        if(expr->func==prjm_eval_func_mem) result["memory_space"]=expr->memory_buffer==context->global_memory?"global":"local";
        return result;
    }
public:
    EquationTree() :context(prjm_eval_create_compile_context(nullptr,&registers)) {
        if(!context) throw std::runtime_error("cannot create native equation context");
        prjm_eval_intrinsic_function_list list; uint32_t count;
        prjm_eval_intrinsic_functions(&list,&count);
        for(uint32_t i=0;i<count;++i) functions[list[i].func]=list[i].name;
        functions[prjm_eval_func_execute_list]="sequence";
        functions[prjm_eval_func_execute_loop]="loop";
        functions[prjm_eval_func_execute_while]="while";
        functions[prjm_eval_func_set]="assign";
        functions[prjm_eval_func_mem]="mem";
        for(int i=0;i<100;++i) variables[&registers[i]]="reg"+(i<10?std::string("0"):std::string())+std::to_string(i);
    }
    ~EquationTree(){prjm_eval_destroy_compile_context(context);}
    json parse(const std::string& code) {
        ParserDiagnostics diagnostics;
        auto program=prjm_eval_compile_code(context,code.c_str());
        if(!program) {
            int line=0,columnStart=0,columnEnd=0;
            auto message=prjm_eval_compiler_get_error(context,&line,&columnStart,&columnEnd);
            const std::string reason=message?message:"native equation compilation failed without diagnostic";
            return {{"status","unknown"},{"reason",reason},{"compile_status","rejected"},
                    {"compile_error",{{"message",reason},{"line",line},
                                      {"column_start",columnStart},{"column_end",columnEnd}}}};
        }
        for(auto item=context->variables.first;item;item=item->next) variables[&item->variable->value]=item->variable->name;
        json result;
        try {result={{"status","parsed"},{"tree",node(program->program)},{"numeric_bits",sizeof(PRJM_EVAL_F)*8}};}
        catch(const std::exception& error){result={{"status","unknown"},{"reason",error.what()}};}
        result["compile_status"]="accepted";
        prjm_eval_destroy_code(program);
        return result;
    }
};

json expression(const HLSLExpression*);
json type(const HLSLType& value) {
    return {{"name",value.typeName?value.typeName:baseTypeDescriptions[value.baseType].typeName},
            {"array",value.array},{"array_size",value.array?expression(value.arraySize):json(nullptr)},{"flags",value.flags}};
}

json expression(const HLSLExpression*);
json expressions(const HLSLExpression* expr) {
    json result=json::array(); for(;expr;expr=expr->nextExpression) result.push_back(expression(expr)); return result;
}
json expression(const HLSLExpression* expr) {
    if(!expr) return nullptr;
    json result={{"type",type(expr->expressionType)},{"line",expr->line}};
    switch(expr->nodeType) {
    case HLSLNodeType_UnaryExpression: {auto p=static_cast<const HLSLUnaryExpression*>(expr); result.update({{"kind","unary"},{"operator",p->unaryOp},{"operand",expression(p->expression)}});break;}
    case HLSLNodeType_BinaryExpression: {auto p=static_cast<const HLSLBinaryExpression*>(expr);result.update({{"kind","binary"},{"operator",p->binaryOp},{"left",expression(p->expression1)},{"right",expression(p->expression2)}});break;}
    case HLSLNodeType_ConditionalExpression: {auto p=static_cast<const HLSLConditionalExpression*>(expr);result.update({{"kind","conditional"},{"condition",expression(p->condition)},{"yes",expression(p->trueExpression)},{"no",expression(p->falseExpression)}});break;}
    case HLSLNodeType_CastingExpression: {auto p=static_cast<const HLSLCastingExpression*>(expr);result.update({{"kind","cast"},{"target_type",type(p->type)},{"operand",expression(p->expression)}});break;}
    case HLSLNodeType_LiteralExpression: {
        auto p=static_cast<const HLSLLiteralExpression*>(expr);result["kind"]="constant";
        if(p->type==HLSLBaseType_Float){
            result["value"]=numericValue(p->fValue);
            char buffer[64];String_FormatFloat(buffer,sizeof(buffer),p->fValue);
            result["renderer_literal"]=buffer;
        }else result["value"]=p->type==HLSLBaseType_Bool?json(p->bValue):json(p->iValue);
        break;
    }
    case HLSLNodeType_IdentifierExpression: {auto p=static_cast<const HLSLIdentifierExpression*>(expr);result.update({{"kind","variable"},{"name",p->name},{"global",p->global}});break;}
    case HLSLNodeType_ConstructorExpression: {auto p=static_cast<const HLSLConstructorExpression*>(expr);result.update({{"kind","construct"},{"args",expressions(p->argument)}});break;}
    case HLSLNodeType_MemberAccess: {auto p=static_cast<const HLSLMemberAccess*>(expr);result.update({{"kind","member"},{"object",expression(p->object)},{"field",p->field},{"swizzle",p->swizzle}});break;}
    case HLSLNodeType_ArrayAccess: {auto p=static_cast<const HLSLArrayAccess*>(expr);result.update({{"kind","index"},{"object",expression(p->array)},{"index",expression(p->index)}});break;}
    case HLSLNodeType_FunctionCall: {auto p=static_cast<const HLSLFunctionCall*>(expr);result.update({{"kind","call"},{"function",p->function->name},{"args",expressions(p->argument)},{"signature",json::array()}});for(auto a=p->function->argument;a;a=a->nextArgument)result["signature"].push_back({{"type",type(a->type)},{"modifier",a->modifier},{"default",expression(a->defaultValue)}});break;}
    case HLSLNodeType_SamplerState: {auto p=static_cast<const HLSLSamplerState*>(expr);result["kind"]="sampler_state";result["states"]=json::array();for(auto s=p->stateAssignments;s;s=s->nextStateAssignment)result["states"].push_back({{"name",s->stateName},{"state_id",s->d3dRenderState},{"value",s->d3dRenderState==8?json(s->fValue):json(s->iValue)}});break;}
    default: throw std::runtime_error("unexported native shader expression "+std::to_string(expr->nodeType));
    }
    return result;
}
json statements(const HLSLStatement* statement) {
    json result=json::array();
    for(;statement;statement=statement->nextStatement) {
        json item={{"line",statement->line}};
        switch(statement->nodeType) {
        case HLSLNodeType_Declaration: {
            item["kind"]="declarations";item["values"]=json::array();
            for(auto p=static_cast<const HLSLDeclaration*>(statement);p;p=p->nextDeclaration) {
                json value=expression(p->assignment);
                if(p->assignment&&(p->type.array||p->assignment->nextExpression))
                    value={{"kind","aggregate"},{"type",type(p->type)},{"elements",expressions(p->assignment)}};
                item["values"].push_back({{"name",p->name},{"type",type(p->type)},{"value",value}});
            }
            break;}
        case HLSLNodeType_Function: {
            auto p=static_cast<const HLSLFunction*>(statement);item.update({{"kind","function"},{"name",p->name},{"return_type",type(p->returnType)},{"body",statements(p->statement)},{"args",json::array()}});
            for(auto arg=p->argument;arg;arg=arg->nextArgument)item["args"].push_back({{"name",arg->name},{"type",type(arg->type)},{"modifier",arg->modifier},{"default",expression(arg->defaultValue)}});
            break;}
        case HLSLNodeType_ExpressionStatement: item.update({{"kind","expression"},{"value",expression(static_cast<const HLSLExpressionStatement*>(statement)->expression)}});break;
        case HLSLNodeType_ReturnStatement: item.update({{"kind","return"},{"value",expression(static_cast<const HLSLReturnStatement*>(statement)->expression)}});break;
        case HLSLNodeType_IfStatement: {auto p=static_cast<const HLSLIfStatement*>(statement);item.update({{"kind","if"},{"condition",expression(p->condition)},{"yes",statements(p->statement)},{"no",statements(p->elseStatement)}});break;}
        case HLSLNodeType_ForStatement: {auto p=static_cast<const HLSLForStatement*>(statement);item.update({{"kind","for"},{"initialization",statements(p->initialization)},{"initial_expression",p->initialization?json(nullptr):expression(p->initializationWithoutType)},{"condition",expression(p->condition)},{"increment",expression(p->increment)},{"body",statements(p->statement)}});break;}
        case HLSLNodeType_WhileStatement: {auto p=static_cast<const HLSLWhileStatement*>(statement);item.update({{"kind","while"},{"condition",expression(p->condition)},{"body",statements(p->statement)}});break;}
        case HLSLNodeType_BlockStatement: item.update({{"kind","block"},{"body",statements(static_cast<const HLSLBlockStatement*>(statement)->statement)}});break;
        case HLSLNodeType_BreakStatement:item["kind"]="break";break;
        case HLSLNodeType_ContinueStatement:item["kind"]="continue";break;
        case HLSLNodeType_DiscardStatement:item["kind"]="discard";break;
        case HLSLNodeType_Struct: {auto p=static_cast<const HLSLStruct*>(statement);item.update({{"kind","struct"},{"name",p->name},{"fields",json::array()}});for(auto f=p->field;f;f=f->nextField)item["fields"].push_back({{"name",f->name},{"type",type(f->type)}});break;}
        default:throw std::runtime_error("unexported native shader statement "+std::to_string(statement->nodeType));
        }
        result.push_back(item);
    }
    return result;
}

// ReplaceUniformsAssignments retains the input AST's global marker even though
// GLSL resolves its generated names to function-local declarations. Export that
// target binding explicitly, rather than treating these names as new uniforms.
void targetLocalBindings(json& node,const std::set<std::string>& locals) {
    if(node.is_object()) {
        if(node.value("kind",std::string())=="variable"&&locals.count(node.value("name",std::string()))) {
            node["native_global_marker"]=node.value("global",false);
            node["global"]=false;
            node["target_binding"]="function-local uniform replacement";
        }
        for(auto& item:node.items())targetLocalBindings(item.value(),locals);
    } else if(node.is_array())for(auto& item:node)targetLocalBindings(item,locals);
}

void targetGlobalBindings(json& node,const std::map<std::string,json>& declarations) {
    if(node.is_object()) {
        auto found=declarations.find(node.value("name",std::string()));
        if(node.value("kind",std::string())=="variable"&&node.value("global",false)&&found!=declarations.end()) {
            node["native_type_flags"]=node["type"].value("flags",0);
            node["type"]=found->second;
            node["target_binding"]="global initialized uniform copy";
        }
        for(auto& item:node.items())targetGlobalBindings(item.value(),declarations);
    }else if(node.is_array())for(auto& item:node)targetGlobalBindings(item,declarations);
}

json shaderTree(std::string code,bool warp,const std::string& header) {
    try {
        ParserDiagnostics diagnostics;
        std::string stripped=libprojectM::Utils::StripComments(code);
        auto start=stripped.find("shader_body");
        if(start==std::string::npos) throw std::runtime_error("missing shader_body");
        auto body=stripped.find('{',start);
        if(body==std::string::npos)throw std::runtime_error("missing shader opening brace");
        int depth=1;size_t end=body+1;
        for(;end<stripped.size()&&depth;++end){if(stripped[end]=='{')++depth;else if(stripped[end]=='}')--depth;}
        if(depth)throw std::runtime_error("missing shader closing brace");
        code.resize(end); // MilkDrop shader bodies can be followed by author/footer text.
        std::string signature=warp?"void PS(float4 _vDiffuse:COLOR,float4 _uv:TEXCOORD0,float2 _rad_ang:TEXCOORD1,out float4 _return_value:COLOR0,out float4 _mv_tex_coords:COLOR1)":
            "void PS(float4 _vDiffuse:COLOR,float2 _uv:TEXCOORD0,float2 _rad_ang:TEXCOORD1,out float4 _return_value:COLOR)";
        code.replace(start,11,signature);
        auto opening=code.find('{',start),closing=code.rfind('}');
        if(opening==std::string::npos||closing==std::string::npos)throw std::runtime_error("missing shader braces");
        code.insert(closing,"_return_value=float4(ret.xyz,1.0);\n");
        code.insert(opening+1,"\nfloat3 ret=0;\n"+(warp?std::string("_mv_tex_coords.xy=_uv.xy;\n"):std::string()));
        std::string macros="#define rad _rad_ang.x\n#define ang _rad_ang.y\n#define uv _uv.xy\n";
        macros+=warp?"#define uv_orig _uv.zw\n":"#define uv_orig _uv.xy\n#define hue_shader _vDiffuse.xyz\n";
        Allocator allocator;HLSLTree tree(&allocator);HLSLParser parser(&allocator,&tree);std::string preprocessed;
        std::string full=header+macros+code;
        std::vector<std::string> extensions;
        // Standard HLSL all is absent; any is already in the intrinsic table.
        // Preserve the language meaning while explicitly exposing this runtime-compatibility gap.
        // https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-all
        for(const auto& name:{std::string("all")}) {
            if(!std::regex_search(code,std::regex("\\b"+name+"\\s*\\(")))continue;
            if(std::regex_search(code,std::regex("\\b(bool|float[1-4]?|int[1-4]?)\\s+"+name+"\\s*\\(")))continue;
            extensions.push_back(name);
            std::string prototypes;
            for(const auto& scalar:{"float","int","bool","uint"})for(int size=1;size<=4;++size)
                prototypes+="bool "+name+"("+scalar+(size==1?std::string():std::to_string(size))+" value);\n";
            for(int rows=2;rows<=4;++rows)for(int cols=2;cols<=4;++cols)
                prototypes+="bool "+name+"(float"+std::to_string(rows)+"x"+std::to_string(cols)+" value);\n";
            full=prototypes+full;
        }
        if(!parser.ApplyPreprocessor("milk",full.c_str(),full.size(),preprocessed))throw std::runtime_error("native shader preprocessing failed");
        // Object macros wrap aliases in parentheses, including declaration names.
        // Native translation discards these declarations and rebuilds bindings.
        // Drop plain named texture declarations and the rest of their line,
        // matching native translation's deletion span. Retain sampler_state
        // initializers for the independent language model and compatibility gate.
        std::regex plainSamplerDeclarations(
            "\\bsampler(?:[23]D)?(?:\\s+|\\s*\\()\\(*\\s*(sampler_[A-Za-z_][A-Za-z_0-9]*)\\s*\\)*\\s*;[^\\r\\n]*");
        std::set<std::string> declaredSamplers,declaredSizes;
        std::regex deletedReferences("\\b(sampler_|texsize_)([A-Za-z_][A-Za-z_0-9]*)");
        auto retainReferences=[&](const std::regex& declarations) {
            auto uncommented=libprojectM::Utils::StripComments(preprocessed);
            for(auto i=std::sregex_iterator(preprocessed.begin(),preprocessed.end(),declarations);i!=std::sregex_iterator();++i) {
                auto removed=uncommented.substr(i->position(),i->length());
                for(auto j=std::sregex_iterator(removed.begin(),removed.end(),deletedReferences);j!=std::sregex_iterator();++j) {
                    if((*j)[2]=="state")continue;
                    declaredSamplers.insert((*j)[2]);
                    if((*j)[1]=="texsize_")declaredSizes.insert((*j)[2]);
                }
            }
        };
        retainReferences(plainSamplerDeclarations);
        preprocessed=std::regex_replace(preprocessed,plainSamplerDeclarations,"");
        // Match native texture-size declaration removal, including trailing
        // statements and leading qualifier spillover. Rebuild as uniforms.
        std::regex textureSizeDeclarations("float4\\s+texsize_.*");
        retainReferences(textureSizeDeclarations);
        preprocessed=std::regex_replace(preprocessed,textureSizeDeclarations,"");
        // Retain the language's sampler-state declarations. projectM's GLSL preparation drops them.
        // Resolve generic samplers to the dimensions of the built-in binding they reference.
        std::regex generic("\\bsampler\\s+(sampler_[A-Za-z_][A-Za-z_0-9]*)");
        std::smatch declaration;
        while(std::regex_search(preprocessed,declaration,generic)) {
            std::string name=declaration[1];
            preprocessed.replace(declaration.position(),declaration.length(),
                std::string(name.find("noisevol_")!=std::string::npos?"sampler3D ":"sampler2D ")+name);
        }
        std::set<std::string> samplers=declaredSamplers,sizes=declaredSizes;
        std::regex names("\\b(sampler_|texsize_)([A-Za-z_][A-Za-z_0-9]*)");
        auto referenceSource=libprojectM::Utils::StripComments(preprocessed);
        for(auto i=std::sregex_iterator(referenceSource.begin(),referenceSource.end(),names);i!=std::sregex_iterator();++i)
            ((*i)[1]=="sampler_"?samplers:sizes).insert((*i)[2]);
        for(const auto& name:samplers) {
            if(name=="state")continue; // sampler_state is a language keyword, not a texture binding.
            if(std::regex_search(preprocessed,std::regex("\\bsampler[23]D\\s+sampler_"+name+"\\b")))continue;
            bool volume=name.find("noisevol_")!=std::string::npos;
            preprocessed.insert(0,std::string(volume?"uniform sampler3D ":"uniform sampler2D ")+"sampler_"+name+";\n");
        }
        for(const auto& name:sizes)if(!std::regex_search(preprocessed,std::regex("\\bfloat4\\s+texsize_"+name+"\\b")))preprocessed.insert(0,"uniform float4 texsize_"+name+";\n");
        if(!parser.Parse("milk",preprocessed.c_str(),preprocessed.size()))throw std::runtime_error("native shader parsing failed");
        // This is the same pre-generation AST rewrite called by GLSLGenerator.
        // Generated locals have no initializer; preserve component validity.
        tree.ReplaceUniformsAssignments();
        auto target=statements(tree.GetRoot()->statement);
        std::map<std::string,json> globalCopies;
        for(const auto& node:target)if(node["kind"]=="declarations")for(const auto& declaration:node["values"]) {
            const auto& value=declaration["value"];
            if(!(declaration["type"].value("flags",0)&HLSLTypeFlag_Uniform)&&value.is_object()&&
               value.value("kind",std::string())=="variable"&&value.value("global",false)&&
               (value["type"].value("flags",0)&HLSLTypeFlag_Uniform))
                globalCopies.emplace(declaration["name"].get<std::string>(),declaration["type"]);
        }
        targetGlobalBindings(target,globalCopies);
        json replacements=json::array();
        for(auto& function:target)if(function["kind"]=="function") {
            std::set<std::string> locals;
            for(const auto& statement:function["body"]) {
                if(statement["kind"]!="declarations")break;
                for(const auto& declaration:statement["values"])
                    if(declaration["type"].value("flags",0)&HLSLTypeFlag_Uniform) {
                        auto name=declaration["name"].get<std::string>();locals.insert(name);
                        replacements.push_back({{"function",function["name"]},{"local",name},
                                                {"initialization","uninitialized"}});
                    }
            }
            targetLocalBindings(function["body"],locals);
        }
        return {{"status","parsed"},{"tree",target},
                {"implicit_global_input_policy",kImplicitGlobalPolicy},{"array_initializer_policy",kArrayInitializerPolicy},{"array_generator_sha256",kArrayGeneratorSha},
                {"target_transforms",{"HLSLTree::ReplaceUniformsAssignments"}},
                {"uniform_local_replacements",replacements},
                {"language_extensions",extensions},{"runtime_compatibility","not established by syntax parsing"}};
    }catch(const std::exception& error){return {{"status","unknown"},{"reason",error.what()}};}
}

int main(int argc,char** argv) {
    try {
        if(argc==3&&std::string(argv[1])=="--equations") {
            std::ifstream input(argv[2]);auto request=json::parse(input);
            auto result=executeEquations(request);
            std::cout<<result.dump(-1,' ',false,json::error_handler_t::replace)<<'\n';return 0;
        }
        if(argc!=2)throw std::runtime_error("usage: milk-native-reader preset.milk");
        auto begin=std::chrono::steady_clock::now();PresetFileParser file;
        if(!file.Read(argv[1]))throw std::runtime_error("preset file could not be read");
        json report={{"schema_version",1},{"syntax_complete",true},{"semantics_complete",false},
            {"reader","pinned projectM native EEL/HLSL frontends"},{"sections",json::object()},{"values",file.PresetValues()}};
        const std::string header=kShaderHeader;
        report["parser_inputs"]={{"shader_header_sha256",kShaderHeaderSha},{"engine_archive_sha256",kEngineArchiveSha},
                                 {"engine",json::parse(kEngineIdentity)},
                                 {"random_binding_contract",json::parse(kRandomBindingContract)}};
#ifdef MILK_HAS_LEGACY_EQUATION_CODE
        report["equation_assembly_policy"]="projectmtv-core-2.2.8-v1";
#else
        report["equation_assembly_policy"]="milkdrop-records-v1";
#endif
        int version=file.GetInt("MILKDROP_PRESET_VERSION",100);
        bool warpActive=version>=200&&file.GetInt(version==200?"PSVERSION":"PSVERSION_WARP",2)>0;
        bool compActive=version>=200&&file.GetInt(version==200?"PSVERSION":"PSVERSION_COMP",2)>0;
        std::vector<std::pair<std::string,bool>> prefixes={{"per_frame_init_",true},{"per_frame_",true},{"per_pixel_",true},{"warp_",warpActive},{"comp_",compActive}};
        for(int i=0;i<4;++i)for(const auto& kind:{std::string("wave"),std::string("shape")}) {
            bool active=file.GetBool(kind+"code_"+std::to_string(i)+"_enabled",false);
            for(const auto& phase:{"init","per_frame","per_point"})
                if(kind=="wave"||std::string(phase)!="per_point")prefixes.emplace_back(kind+"_"+std::to_string(i)+"_"+phase,active);
        }
        report["requested_code_prefixes"]=json::array();
        for(const auto& [prefix,active]:prefixes) {
            report["requested_code_prefixes"].push_back(prefix);
            auto code=file.GetCode(prefix);if(code.empty())continue;
            json section;
            if(prefix=="warp_"||prefix=="comp_")section=shaderTree(code,prefix=="warp_",header);
            else {
                EquationTree nativeContext;auto native=nativeContext.parse(code);
                EquationTree milkdropContext;std::string assembled=milkdropEquationSource(code);
                section=milkdropContext.parse(assembled);
                section["dialect"]="MilkDrop 2.25c numbered equation assembly";
                section["assembled_source"]=assembled;
#ifdef MILK_HAS_LEGACY_EQUATION_CODE
                section["target_assembly_policy"]="projectmtv-core-2.2.8-v1";
#else
                section["target_assembly_policy"]="milkdrop-records-v1";
#endif
                section["projectm_native_status"]=native["status"];
                section["projectm_native_compile_status"]=native["compile_status"];
                if(native.contains("tree"))section["projectm_raw_tree"]=native["tree"];
                if(native.contains("compile_error"))section["projectm_native_compile_error"]=native["compile_error"];
                if(native["status"]!="parsed")section["projectm_native_reason"]=native["reason"];
            }
            section["active"]=active;section["source"]=code;
            if(section["status"]!="parsed")report["syntax_complete"]=false;
            report["sections"][prefix]=section;
        }
        report["elapsed_ms"]=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-begin).count();
        report["text_encoding"]="original byte input; invalid UTF-8 replaced for JSON display only";
        std::cout<<report.dump(-1,' ',false,json::error_handler_t::replace)<<'\n';return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
