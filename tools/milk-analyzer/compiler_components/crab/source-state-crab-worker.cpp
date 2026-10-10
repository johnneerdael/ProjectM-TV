#include <crab/cfg/cfg.hpp>
#include <crab/cfg/basic_block_traits.hpp>
#include <crab/config.h>
#include <crab/types/varname_factory.hpp>
#include <iostream>
namespace crab { namespace cfg_impl {
using variable_factory_t=var_factory_impl::str_variable_factory;
using varname_t=variable_factory_t::varname_t;
using q_cfg_t=cfg::cfg<std::string,varname_t,ikos::q_number>;
using q_cfg_ref_t=cfg::cfg_ref<q_cfg_t>;
using q_var=variable<ikos::q_number,varname_t>;
}
template<> class variable_name_traits<std::string> { public: static std::string to_string(std::string name){return name;} };
template<> class basic_block_traits<cfg_impl::q_cfg_t::basic_block_t> {
public:static std::string to_string(const std::string &label){return label;}
}; }
#include <crab/domains/intervals.hpp>
#include <crab/analysis/fwd_analyzer.hpp>
using namespace crab;using namespace crab::cfg_impl;using namespace crab::domains;using namespace ikos;
using Domain=interval_domain<q_number,varname_t>;
int main(int argc,char**argv) {
 if(argc==2 && std::string(argv[1])=="--version") { std::cout<<"source-state-crab-worker/1 crabb1eeb1a9402ab0664e962f26f89d923f8514284c\n";return 0;}
 if(argc<5) return 2;
 q_number init_lower(argv[1]),init_upper(argv[2]),lower(argv[3]),upper(argv[4]);bool mutate=argc>5;variable_factory_t names;
 q_var y(names["y0"],REAL_TYPE),delta(names["delta"],REAL_TYPE),tmp(names["tmp"],REAL_TYPE);
 q_cfg_t cfg("entry","exit");auto &entry=cfg.insert("entry"),&header=cfg.insert("header"),&low=cfg.insert("low"),&middle=cfg.insert("middle"),&high=cfg.insert("high"),&join=cfg.insert("join"),&exit=cfg.insert("exit");
 entry>>header;header>>low;header>>middle;header>>high;low>>join;middle>>join;high>>join;join>>header;join>>exit;
 entry.havoc(y);entry.assume(y>=init_lower);entry.assume(y<=init_upper);
 header.havoc(delta);header.assign(tmp,y+delta);
 if(mutate) {low.assign(y,tmp);middle.assign(y,tmp);high.assign(y,tmp);}
 else {low.assume(tmp<=lower);low.assign(y,lower);middle.assume(tmp>=lower);middle.assume(tmp<=upper);middle.assign(y,tmp);high.assume(tmp>=upper);high.assign(y,upper);}
 q_cfg_ref_t reference(cfg);Domain initial;fixpoint_parameters parameters;parameters.get_widening_delay()=1;parameters.get_descending_iterations()=2;
 analyzer::intra_fwd_analyzer<q_cfg_ref_t,Domain> analysis(reference,initial.make_top(),nullptr,parameters);
 analysis.run(initial);
 auto h=analysis.get_pre("header").at(y);auto post=analysis.get_pre("exit").at(y);
 outs()<<"{\"header_interval\":\""<<h<<"\",\"postframe_interval\":\""<<post<<"\"}\n";
}
