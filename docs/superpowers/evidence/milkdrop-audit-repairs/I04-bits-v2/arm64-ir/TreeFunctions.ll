; ModuleID = '/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit/i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c'
source_filename = "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit/i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c"
target datalayout = "e-m:e-i8:8:32-i16:16:32-i64:64-i128:128-n32:64-S128"
target triple = "aarch64-none-linux-android21"

%struct.prjm_eval_function_def = type { ptr, ptr, i32, i8, i8 }
%struct.prjm_eval_exptreenode = type { ptr, double, %union.anon, ptr, ptr }
%union.anon = type { ptr }
%struct.prjm_eval_exptreenode_list_item = type { ptr, ptr }

@intrinsic_function_table = internal global [72 x %struct.prjm_eval_function_def] [%struct.prjm_eval_function_def { ptr @.str, ptr @prjm_eval_func_const, i32 0, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.1, ptr @prjm_eval_func_var, i32 0, i8 0, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.2, ptr @prjm_eval_func_execute_list, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.3, ptr @prjm_eval_func_bitwise_or, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.4, ptr @prjm_eval_func_bitwise_and, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.5, ptr @prjm_eval_func_if, i32 3, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.6, ptr @prjm_eval_func_if, i32 3, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.7, ptr @prjm_eval_func_boolean_and_op, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.8, ptr @prjm_eval_func_boolean_or_op, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.9, ptr @prjm_eval_func_execute_loop, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.10, ptr @prjm_eval_func_execute_while, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.11, ptr @prjm_eval_func_bnot, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.12, ptr @prjm_eval_func_bnot, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.13, ptr @prjm_eval_func_equal, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.14, ptr @prjm_eval_func_equal, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.15, ptr @prjm_eval_func_notequal, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.16, ptr @prjm_eval_func_below, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.17, ptr @prjm_eval_func_below, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.18, ptr @prjm_eval_func_above, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.19, ptr @prjm_eval_func_above, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.20, ptr @prjm_eval_func_beloweq, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.21, ptr @prjm_eval_func_aboveeq, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.22, ptr @prjm_eval_func_set, i32 2, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.23, ptr @prjm_eval_func_set, i32 2, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.24, ptr @prjm_eval_func_add, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.25, ptr @prjm_eval_func_sub, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.26, ptr @prjm_eval_func_mul, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.27, ptr @prjm_eval_func_div, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.28, ptr @prjm_eval_func_mod, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.29, ptr @prjm_eval_func_mul_op, i32 2, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.30, ptr @prjm_eval_func_div_op, i32 2, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.31, ptr @prjm_eval_func_bitwise_or_op, i32 2, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.32, ptr @prjm_eval_func_bitwise_and_op, i32 2, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.33, ptr @prjm_eval_func_add_op, i32 2, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.34, ptr @prjm_eval_func_sub_op, i32 2, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.35, ptr @prjm_eval_func_mod_op, i32 2, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.36, ptr @prjm_eval_func_sin, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.37, ptr @prjm_eval_func_cos, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.38, ptr @prjm_eval_func_tan, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.39, ptr @prjm_eval_func_asin, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.40, ptr @prjm_eval_func_acos, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.41, ptr @prjm_eval_func_atan, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.42, ptr @prjm_eval_func_atan2, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.43, ptr @prjm_eval_func_sqr, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.44, ptr @prjm_eval_func_sqrt, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.45, ptr @prjm_eval_func_pow, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.46, ptr @prjm_eval_func_pow_op, i32 2, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.47, ptr @prjm_eval_func_exp, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.48, ptr @prjm_eval_func_neg, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.49, ptr @prjm_eval_func_log, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.50, ptr @prjm_eval_func_log10, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.51, ptr @prjm_eval_func_abs, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.52, ptr @prjm_eval_func_min, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.53, ptr @prjm_eval_func_max, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.54, ptr @prjm_eval_func_sign, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.55, ptr @prjm_eval_func_rand, i32 1, i8 0, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.56, ptr @prjm_eval_func_floor, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.57, ptr @prjm_eval_func_floor, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.58, ptr @prjm_eval_func_ceil, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.59, ptr @prjm_eval_func_invsqrt, i32 1, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.60, ptr @prjm_eval_func_sigmoid, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.61, ptr @prjm_eval_func_boolean_and_func, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.62, ptr @prjm_eval_func_boolean_or_func, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.63, ptr @prjm_eval_func_exec2, i32 2, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.64, ptr @prjm_eval_func_exec3, i32 3, i8 1, i8 0 }, %struct.prjm_eval_function_def { ptr @.str.65, ptr @prjm_eval_func_mem, i32 1, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.66, ptr @prjm_eval_func_mem, i32 1, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.67, ptr @prjm_eval_func_mem, i32 1, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.68, ptr @prjm_eval_func_mem, i32 1, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.69, ptr @prjm_eval_func_freembuf, i32 1, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.70, ptr @prjm_eval_func_memcpy, i32 3, i8 0, i8 1 }, %struct.prjm_eval_function_def { ptr @.str.71, ptr @prjm_eval_func_memset, i32 3, i8 0, i8 1 }], align 8, !dbg !0
@.str = private unnamed_addr constant [10 x i8] c"/*const*/\00", align 1, !dbg !65
@.str.1 = private unnamed_addr constant [8 x i8] c"/*var*/\00", align 1, !dbg !71
@.str.2 = private unnamed_addr constant [9 x i8] c"/*list*/\00", align 1, !dbg !76
@.str.3 = private unnamed_addr constant [7 x i8] c"/*or*/\00", align 1, !dbg !81
@.str.4 = private unnamed_addr constant [8 x i8] c"/*and*/\00", align 1, !dbg !86
@.str.5 = private unnamed_addr constant [3 x i8] c"if\00", align 1, !dbg !88
@.str.6 = private unnamed_addr constant [4 x i8] c"_if\00", align 1, !dbg !93
@.str.7 = private unnamed_addr constant [5 x i8] c"_and\00", align 1, !dbg !98
@.str.8 = private unnamed_addr constant [4 x i8] c"_or\00", align 1, !dbg !103
@.str.9 = private unnamed_addr constant [5 x i8] c"loop\00", align 1, !dbg !105
@.str.10 = private unnamed_addr constant [6 x i8] c"while\00", align 1, !dbg !107
@.str.11 = private unnamed_addr constant [5 x i8] c"_not\00", align 1, !dbg !112
@.str.12 = private unnamed_addr constant [5 x i8] c"bnot\00", align 1, !dbg !114
@.str.13 = private unnamed_addr constant [7 x i8] c"_equal\00", align 1, !dbg !116
@.str.14 = private unnamed_addr constant [6 x i8] c"equal\00", align 1, !dbg !118
@.str.15 = private unnamed_addr constant [7 x i8] c"_noteq\00", align 1, !dbg !120
@.str.16 = private unnamed_addr constant [7 x i8] c"_below\00", align 1, !dbg !122
@.str.17 = private unnamed_addr constant [6 x i8] c"below\00", align 1, !dbg !124
@.str.18 = private unnamed_addr constant [7 x i8] c"_above\00", align 1, !dbg !126
@.str.19 = private unnamed_addr constant [6 x i8] c"above\00", align 1, !dbg !128
@.str.20 = private unnamed_addr constant [7 x i8] c"_beleq\00", align 1, !dbg !130
@.str.21 = private unnamed_addr constant [7 x i8] c"_aboeq\00", align 1, !dbg !132
@.str.22 = private unnamed_addr constant [5 x i8] c"_set\00", align 1, !dbg !134
@.str.23 = private unnamed_addr constant [7 x i8] c"assign\00", align 1, !dbg !136
@.str.24 = private unnamed_addr constant [5 x i8] c"_add\00", align 1, !dbg !138
@.str.25 = private unnamed_addr constant [5 x i8] c"_sub\00", align 1, !dbg !140
@.str.26 = private unnamed_addr constant [5 x i8] c"_mul\00", align 1, !dbg !142
@.str.27 = private unnamed_addr constant [5 x i8] c"_div\00", align 1, !dbg !144
@.str.28 = private unnamed_addr constant [5 x i8] c"_mod\00", align 1, !dbg !146
@.str.29 = private unnamed_addr constant [7 x i8] c"_mulop\00", align 1, !dbg !148
@.str.30 = private unnamed_addr constant [7 x i8] c"_divop\00", align 1, !dbg !150
@.str.31 = private unnamed_addr constant [6 x i8] c"_orop\00", align 1, !dbg !152
@.str.32 = private unnamed_addr constant [7 x i8] c"_andop\00", align 1, !dbg !154
@.str.33 = private unnamed_addr constant [7 x i8] c"_addop\00", align 1, !dbg !156
@.str.34 = private unnamed_addr constant [7 x i8] c"_subop\00", align 1, !dbg !158
@.str.35 = private unnamed_addr constant [7 x i8] c"_modop\00", align 1, !dbg !160
@.str.36 = private unnamed_addr constant [4 x i8] c"sin\00", align 1, !dbg !162
@.str.37 = private unnamed_addr constant [4 x i8] c"cos\00", align 1, !dbg !164
@.str.38 = private unnamed_addr constant [4 x i8] c"tan\00", align 1, !dbg !166
@.str.39 = private unnamed_addr constant [5 x i8] c"asin\00", align 1, !dbg !168
@.str.40 = private unnamed_addr constant [5 x i8] c"acos\00", align 1, !dbg !170
@.str.41 = private unnamed_addr constant [5 x i8] c"atan\00", align 1, !dbg !172
@.str.42 = private unnamed_addr constant [6 x i8] c"atan2\00", align 1, !dbg !174
@.str.43 = private unnamed_addr constant [4 x i8] c"sqr\00", align 1, !dbg !176
@.str.44 = private unnamed_addr constant [5 x i8] c"sqrt\00", align 1, !dbg !178
@.str.45 = private unnamed_addr constant [4 x i8] c"pow\00", align 1, !dbg !180
@.str.46 = private unnamed_addr constant [7 x i8] c"_powop\00", align 1, !dbg !182
@.str.47 = private unnamed_addr constant [4 x i8] c"exp\00", align 1, !dbg !184
@.str.48 = private unnamed_addr constant [5 x i8] c"_neg\00", align 1, !dbg !186
@.str.49 = private unnamed_addr constant [4 x i8] c"log\00", align 1, !dbg !188
@.str.50 = private unnamed_addr constant [6 x i8] c"log10\00", align 1, !dbg !190
@.str.51 = private unnamed_addr constant [4 x i8] c"abs\00", align 1, !dbg !192
@.str.52 = private unnamed_addr constant [4 x i8] c"min\00", align 1, !dbg !194
@.str.53 = private unnamed_addr constant [4 x i8] c"max\00", align 1, !dbg !196
@.str.54 = private unnamed_addr constant [5 x i8] c"sign\00", align 1, !dbg !198
@.str.55 = private unnamed_addr constant [5 x i8] c"rand\00", align 1, !dbg !200
@.str.56 = private unnamed_addr constant [6 x i8] c"floor\00", align 1, !dbg !202
@.str.57 = private unnamed_addr constant [4 x i8] c"int\00", align 1, !dbg !204
@.str.58 = private unnamed_addr constant [5 x i8] c"ceil\00", align 1, !dbg !206
@.str.59 = private unnamed_addr constant [8 x i8] c"invsqrt\00", align 1, !dbg !208
@.str.60 = private unnamed_addr constant [8 x i8] c"sigmoid\00", align 1, !dbg !210
@.str.61 = private unnamed_addr constant [5 x i8] c"band\00", align 1, !dbg !212
@.str.62 = private unnamed_addr constant [4 x i8] c"bor\00", align 1, !dbg !214
@.str.63 = private unnamed_addr constant [6 x i8] c"exec2\00", align 1, !dbg !216
@.str.64 = private unnamed_addr constant [6 x i8] c"exec3\00", align 1, !dbg !218
@.str.65 = private unnamed_addr constant [5 x i8] c"_mem\00", align 1, !dbg !220
@.str.66 = private unnamed_addr constant [8 x i8] c"megabuf\00", align 1, !dbg !222
@.str.67 = private unnamed_addr constant [6 x i8] c"_gmem\00", align 1, !dbg !224
@.str.68 = private unnamed_addr constant [9 x i8] c"gmegabuf\00", align 1, !dbg !226
@.str.69 = private unnamed_addr constant [9 x i8] c"freembuf\00", align 1, !dbg !228
@.str.70 = private unnamed_addr constant [7 x i8] c"memcpy\00", align 1, !dbg !230
@.str.71 = private unnamed_addr constant [7 x i8] c"memset\00", align 1, !dbg !232
@prjm_eval_genrand_int32.mag01 = internal unnamed_addr constant [2 x i32] [i32 0, i32 -1727483681], align 4, !dbg !234
@prjm_eval_genrand_int32.mt = internal thread_local global [624 x i32] zeroinitializer, align 4, !dbg !253
@prjm_eval_genrand_int32.mti = internal thread_local global i32 0, align 4, !dbg !258

; Function Attrs: mustprogress nofree norecurse nosync nounwind sspstrong willreturn memory(argmem: write) uwtable
define hidden void @prjm_eval_intrinsic_functions(ptr nocapture noundef writeonly %0, ptr nocapture noundef writeonly %1) local_unnamed_addr #0 !dbg !281 {
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !291, metadata !DIExpression()), !dbg !293
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !292, metadata !DIExpression()), !dbg !293
  store i32 72, ptr %1, align 4, !dbg !294, !tbaa !295
  store ptr @intrinsic_function_table, ptr %0, align 8, !dbg !299, !tbaa !300
  ret void, !dbg !302
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind sspstrong willreturn memory(write, argmem: readwrite, inaccessiblemem: none) uwtable
define hidden void @prjm_eval_func_const(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #1 !dbg !303 {
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !305, metadata !DIExpression()), !dbg !307
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !306, metadata !DIExpression()), !dbg !307
  %3 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !308
  %4 = load double, ptr %3, align 8, !dbg !308, !tbaa !309
  %5 = load ptr, ptr %1, align 8, !dbg !308, !tbaa !300
  store double %4, ptr %5, align 8, !dbg !308, !tbaa !312
  ret void, !dbg !313
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind sspstrong willreturn memory(argmem: readwrite) uwtable
define hidden void @prjm_eval_func_var(ptr nocapture noundef readonly %0, ptr nocapture noundef writeonly %1) #2 !dbg !314 {
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !316, metadata !DIExpression()), !dbg !318
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !317, metadata !DIExpression()), !dbg !318
  %3 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 2, !dbg !319
  %4 = load ptr, ptr %3, align 8, !dbg !319, !tbaa !320
  store ptr %4, ptr %1, align 8, !dbg !319, !tbaa !300
  ret void, !dbg !321
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_execute_list(ptr noundef %0, ptr nocapture noundef writeonly %1) #3 !dbg !322 {
  %3 = alloca ptr, align 8, !DIAssignID !328
  call void @llvm.dbg.assign(metadata i1 undef, metadata !326, metadata !DIExpression(), metadata !328, metadata ptr %3, metadata !DIExpression()), !dbg !329
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !324, metadata !DIExpression()), !dbg !329
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !325, metadata !DIExpression()), !dbg !329
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !330
  store double 0.000000e+00, ptr %4, align 8, !dbg !331, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !332
  call void @llvm.dbg.assign(metadata ptr %4, metadata !326, metadata !DIExpression(), metadata !333, metadata ptr %3, metadata !DIExpression()), !dbg !329
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 4, !dbg !334
  tail call void @llvm.dbg.value(metadata ptr poison, metadata !327, metadata !DIExpression()), !dbg !329
  %6 = load ptr, ptr %5, align 8, !dbg !329, !tbaa !300
  tail call void @llvm.dbg.value(metadata ptr %6, metadata !327, metadata !DIExpression()), !dbg !329
  %7 = icmp eq ptr %6, null, !dbg !335
  br i1 %7, label %17, label %8, !dbg !335

8:                                                ; preds = %2, %8
  %9 = phi ptr [ %13, %8 ], [ %6, %2 ]
  store double 0.000000e+00, ptr %4, align 8, !dbg !336, !tbaa !309
  store ptr %4, ptr %3, align 8, !dbg !338, !tbaa !300, !DIAssignID !339
  call void @llvm.dbg.assign(metadata ptr %4, metadata !326, metadata !DIExpression(), metadata !339, metadata ptr %3, metadata !DIExpression()), !dbg !329
  %10 = load ptr, ptr %9, align 8, !dbg !340, !tbaa !341
  %11 = load ptr, ptr %10, align 8, !dbg !343, !tbaa !344
  call void %11(ptr noundef nonnull %10, ptr noundef nonnull %3) #9, !dbg !345
  %12 = getelementptr inbounds %struct.prjm_eval_exptreenode_list_item, ptr %9, i64 0, i32 1, !dbg !346
  tail call void @llvm.dbg.value(metadata ptr poison, metadata !327, metadata !DIExpression()), !dbg !329
  %13 = load ptr, ptr %12, align 8, !dbg !329, !tbaa !300
  tail call void @llvm.dbg.value(metadata ptr %13, metadata !327, metadata !DIExpression()), !dbg !329
  %14 = icmp eq ptr %13, null, !dbg !335
  br i1 %14, label %15, label %8, !dbg !335, !llvm.loop !347

15:                                               ; preds = %8
  %16 = load ptr, ptr %3, align 8, !dbg !350, !tbaa !300
  br label %17, !dbg !350

17:                                               ; preds = %15, %2
  %18 = phi ptr [ %16, %15 ], [ %4, %2 ], !dbg !350
  store ptr %18, ptr %1, align 8, !dbg !350, !tbaa !300
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !351
  ret void, !dbg !351
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #4

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #4

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_execute_loop(ptr noundef %0, ptr nocapture noundef writeonly %1) #3 !dbg !352 {
  %3 = alloca ptr, align 8, !DIAssignID !360
  call void @llvm.dbg.assign(metadata i1 undef, metadata !356, metadata !DIExpression(), metadata !360, metadata ptr %3, metadata !DIExpression()), !dbg !361
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !354, metadata !DIExpression()), !dbg !361
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !355, metadata !DIExpression()), !dbg !361
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !362
  store double 0.000000e+00, ptr %4, align 8, !dbg !363, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !364
  store ptr %4, ptr %3, align 8, !dbg !365, !tbaa !300, !DIAssignID !366
  call void @llvm.dbg.assign(metadata ptr %4, metadata !356, metadata !DIExpression(), metadata !366, metadata ptr %3, metadata !DIExpression()), !dbg !361
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !367
  %6 = load ptr, ptr %5, align 8, !dbg !367, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !367, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !367, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !367
  %9 = load ptr, ptr %3, align 8, !dbg !369, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !370, !tbaa !312
  %11 = fptosi double %10 to i64, !dbg !371
  tail call void @llvm.dbg.value(metadata i64 %11, metadata !357, metadata !DIExpression()), !dbg !361
  %12 = call i64 @llvm.smin.i64(i64 %11, i64 1048576), !dbg !372
  tail call void @llvm.dbg.value(metadata i64 %12, metadata !357, metadata !DIExpression()), !dbg !361
  tail call void @llvm.dbg.value(metadata i64 0, metadata !358, metadata !DIExpression()), !dbg !373
  %13 = icmp sgt i64 %11, 0, !dbg !374
  br i1 %13, label %18, label %16, !dbg !376

14:                                               ; preds = %18
  %15 = load ptr, ptr %3, align 8, !dbg !377, !tbaa !300
  br label %16, !dbg !377

16:                                               ; preds = %14, %2
  %17 = phi ptr [ %15, %14 ], [ %9, %2 ], !dbg !377
  store ptr %17, ptr %1, align 8, !dbg !377, !tbaa !300
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !378
  ret void, !dbg !378

18:                                               ; preds = %2, %18
  %19 = phi i64 [ %24, %18 ], [ 0, %2 ]
  tail call void @llvm.dbg.value(metadata i64 %19, metadata !358, metadata !DIExpression()), !dbg !373
  store double 0.000000e+00, ptr %4, align 8, !dbg !379, !tbaa !309
  store ptr %4, ptr %3, align 8, !dbg !381, !tbaa !300, !DIAssignID !382
  call void @llvm.dbg.assign(metadata ptr %4, metadata !356, metadata !DIExpression(), metadata !382, metadata ptr %3, metadata !DIExpression()), !dbg !361
  %20 = load ptr, ptr %5, align 8, !dbg !383, !tbaa !368
  %21 = getelementptr inbounds ptr, ptr %20, i64 1, !dbg !383
  %22 = load ptr, ptr %21, align 8, !dbg !383, !tbaa !300
  %23 = load ptr, ptr %22, align 8, !dbg !383, !tbaa !344
  call void %23(ptr noundef nonnull %22, ptr noundef nonnull %3) #9, !dbg !383
  %24 = add nuw nsw i64 %19, 1, !dbg !384
  tail call void @llvm.dbg.value(metadata i64 %24, metadata !358, metadata !DIExpression()), !dbg !373
  %25 = icmp eq i64 %24, %12, !dbg !374
  br i1 %25, label %14, label %18, !dbg !376, !llvm.loop !385
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_execute_while(ptr noundef %0, ptr nocapture noundef writeonly %1) #3 !dbg !387 {
  %3 = alloca ptr, align 8, !DIAssignID !393
  call void @llvm.dbg.assign(metadata i1 undef, metadata !391, metadata !DIExpression(), metadata !393, metadata ptr %3, metadata !DIExpression()), !dbg !394
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !389, metadata !DIExpression()), !dbg !394
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !390, metadata !DIExpression()), !dbg !394
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !395
  store double 0.000000e+00, ptr %4, align 8, !dbg !396, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !397
  store ptr %4, ptr %3, align 8, !dbg !398, !tbaa !300, !DIAssignID !399
  call void @llvm.dbg.assign(metadata ptr %4, metadata !391, metadata !DIExpression(), metadata !399, metadata ptr %3, metadata !DIExpression()), !dbg !394
  tail call void @llvm.dbg.value(metadata i64 1048576, metadata !392, metadata !DIExpression()), !dbg !394
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3
  br label %6, !dbg !400

6:                                                ; preds = %6, %2
  %7 = phi i64 [ 1048576, %2 ], [ %15, %6 ], !dbg !394
  tail call void @llvm.dbg.value(metadata i64 %7, metadata !392, metadata !DIExpression()), !dbg !394
  %8 = load ptr, ptr %5, align 8, !dbg !401, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !401, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !401, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %3) #9, !dbg !401
  %11 = load ptr, ptr %3, align 8, !dbg !403, !tbaa !300
  %12 = load double, ptr %11, align 8, !dbg !404, !tbaa !312
  %13 = call fast double @llvm.fabs.f64(double %12), !dbg !405
  %14 = fcmp fast ule double %13, 1.000000e-05, !dbg !406
  %15 = add nsw i64 %7, -1
  tail call void @llvm.dbg.value(metadata i64 %15, metadata !392, metadata !DIExpression()), !dbg !394
  %16 = icmp eq i64 %15, 0, !dbg !407
  %17 = select i1 %14, i1 true, i1 %16, !dbg !407
  br i1 %17, label %18, label %6, !dbg !407, !llvm.loop !408

18:                                               ; preds = %6
  store ptr %11, ptr %1, align 8, !dbg !410, !tbaa !300
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !411
  ret void, !dbg !411
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.fabs.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_if(ptr noundef %0, ptr noundef %1) #3 !dbg !412 {
  %3 = alloca ptr, align 8, !DIAssignID !417
  call void @llvm.dbg.assign(metadata i1 undef, metadata !416, metadata !DIExpression(), metadata !417, metadata ptr %3, metadata !DIExpression()), !dbg !418
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !414, metadata !DIExpression()), !dbg !418
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !415, metadata !DIExpression()), !dbg !418
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !419
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !420
  store ptr %4, ptr %3, align 8, !dbg !421, !tbaa !300, !DIAssignID !422
  call void @llvm.dbg.assign(metadata ptr %4, metadata !416, metadata !DIExpression(), metadata !422, metadata ptr %3, metadata !DIExpression()), !dbg !418
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !423
  %6 = load ptr, ptr %5, align 8, !dbg !423, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !423, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !423, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !423
  %9 = load ptr, ptr %3, align 8, !dbg !424, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !426, !tbaa !312
  %11 = fcmp fast une double %10, 0.000000e+00, !dbg !427
  %12 = load ptr, ptr %5, align 8, !dbg !418, !tbaa !368
  %13 = select i1 %11, i64 1, i64 2, !dbg !418
  %14 = getelementptr inbounds ptr, ptr %12, i64 %13, !dbg !418
  %15 = load ptr, ptr %14, align 8, !dbg !418, !tbaa !300
  %16 = load ptr, ptr %15, align 8, !dbg !418, !tbaa !344
  call void %16(ptr noundef nonnull %15, ptr noundef %1) #9, !dbg !418
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !428
  ret void, !dbg !428
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_exec2(ptr noundef %0, ptr noundef %1) #3 !dbg !429 {
  %3 = alloca ptr, align 8, !DIAssignID !434
  call void @llvm.dbg.assign(metadata i1 undef, metadata !433, metadata !DIExpression(), metadata !434, metadata ptr %3, metadata !DIExpression()), !dbg !435
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !431, metadata !DIExpression()), !dbg !435
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !432, metadata !DIExpression()), !dbg !435
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !436
  store double 0.000000e+00, ptr %4, align 8, !dbg !437, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !438
  store ptr %4, ptr %3, align 8, !dbg !439, !tbaa !300, !DIAssignID !440
  call void @llvm.dbg.assign(metadata ptr %4, metadata !433, metadata !DIExpression(), metadata !440, metadata ptr %3, metadata !DIExpression()), !dbg !435
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !441
  %6 = load ptr, ptr %5, align 8, !dbg !441, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !441, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !441, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !441
  %9 = load ptr, ptr %5, align 8, !dbg !442, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !442
  %11 = load ptr, ptr %10, align 8, !dbg !442, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !442, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef %1) #9, !dbg !442
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !443
  ret void, !dbg !443
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_exec3(ptr noundef %0, ptr noundef %1) #3 !dbg !444 {
  %3 = alloca ptr, align 8, !DIAssignID !449
  call void @llvm.dbg.assign(metadata i1 undef, metadata !448, metadata !DIExpression(), metadata !449, metadata ptr %3, metadata !DIExpression()), !dbg !450
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !446, metadata !DIExpression()), !dbg !450
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !447, metadata !DIExpression()), !dbg !450
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !451
  store double 0.000000e+00, ptr %4, align 8, !dbg !452, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !453
  store ptr %4, ptr %3, align 8, !dbg !454, !tbaa !300, !DIAssignID !455
  call void @llvm.dbg.assign(metadata ptr %4, metadata !448, metadata !DIExpression(), metadata !455, metadata ptr %3, metadata !DIExpression()), !dbg !450
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !456
  %6 = load ptr, ptr %5, align 8, !dbg !456, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !456, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !456, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !456
  %9 = load ptr, ptr %5, align 8, !dbg !457, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !457
  %11 = load ptr, ptr %10, align 8, !dbg !457, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !457, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %3) #9, !dbg !457
  %13 = load ptr, ptr %5, align 8, !dbg !458, !tbaa !368
  %14 = getelementptr inbounds ptr, ptr %13, i64 2, !dbg !458
  %15 = load ptr, ptr %14, align 8, !dbg !458, !tbaa !300
  %16 = load ptr, ptr %15, align 8, !dbg !458, !tbaa !344
  call void %16(ptr noundef nonnull %15, ptr noundef %1) #9, !dbg !458
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !459
  ret void, !dbg !459
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_set(ptr noundef %0, ptr noundef %1) #3 !dbg !460 {
  %3 = alloca ptr, align 8, !DIAssignID !465
  call void @llvm.dbg.assign(metadata i1 undef, metadata !464, metadata !DIExpression(), metadata !465, metadata ptr %3, metadata !DIExpression()), !dbg !466
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !462, metadata !DIExpression()), !dbg !466
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !463, metadata !DIExpression()), !dbg !466
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !467
  store double 0.000000e+00, ptr %4, align 8, !dbg !468, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !469
  store ptr %4, ptr %3, align 8, !dbg !470, !tbaa !300, !DIAssignID !471
  call void @llvm.dbg.assign(metadata ptr %4, metadata !464, metadata !DIExpression(), metadata !471, metadata ptr %3, metadata !DIExpression()), !dbg !466
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !472
  %6 = load ptr, ptr %5, align 8, !dbg !472, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !472, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !472, !tbaa !344
  tail call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !472
  %9 = load ptr, ptr %5, align 8, !dbg !473, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !473
  %11 = load ptr, ptr %10, align 8, !dbg !473, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !473, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %3) #9, !dbg !473
  %13 = load ptr, ptr %3, align 8, !dbg !474, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !474, !tbaa !312
  %15 = load ptr, ptr %1, align 8, !dbg !474, !tbaa !300
  store double %14, ptr %15, align 8, !dbg !474, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !475
  ret void, !dbg !475
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_mem(ptr noundef %0, ptr nocapture noundef %1) #3 !dbg !476 {
  %3 = alloca ptr, align 8, !DIAssignID !482
  call void @llvm.dbg.assign(metadata i1 undef, metadata !480, metadata !DIExpression(), metadata !482, metadata ptr %3, metadata !DIExpression()), !dbg !483
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !478, metadata !DIExpression()), !dbg !483
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !479, metadata !DIExpression()), !dbg !483
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !484
  store double 0.000000e+00, ptr %4, align 8, !dbg !485, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !486
  store ptr %4, ptr %3, align 8, !dbg !487, !tbaa !300, !DIAssignID !488
  call void @llvm.dbg.assign(metadata ptr %4, metadata !480, metadata !DIExpression(), metadata !488, metadata ptr %3, metadata !DIExpression()), !dbg !483
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !489
  %6 = load ptr, ptr %5, align 8, !dbg !489, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !489, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !489, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !489
  %9 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 2, !dbg !490
  %10 = load ptr, ptr %9, align 8, !dbg !490, !tbaa !320
  %11 = load ptr, ptr %3, align 8, !dbg !491, !tbaa !300
  %12 = load double, ptr %11, align 8, !dbg !492, !tbaa !312
  %13 = fadd fast double %12, 1.000000e-04, !dbg !493
  %14 = fptosi double %13 to i32, !dbg !494
  %15 = call ptr @prjm_eval_memory_allocate(ptr noundef %10, i32 noundef %14) #9, !dbg !495
  tail call void @llvm.dbg.value(metadata ptr %15, metadata !481, metadata !DIExpression()), !dbg !483
  %16 = icmp eq ptr %15, null, !dbg !496
  br i1 %16, label %18, label %17, !dbg !498

17:                                               ; preds = %2
  store ptr %15, ptr %1, align 8, !dbg !499, !tbaa !300
  br label %20, !dbg !501

18:                                               ; preds = %2
  %19 = load ptr, ptr %1, align 8, !dbg !502, !tbaa !300
  store double 0.000000e+00, ptr %19, align 8, !dbg !502, !tbaa !312
  br label %20, !dbg !503

20:                                               ; preds = %18, %17
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !503
  ret void, !dbg !503
}

declare !dbg !504 ptr @prjm_eval_memory_allocate(ptr noundef, i32 noundef) local_unnamed_addr #6

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_freembuf(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !508 {
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !510, metadata !DIExpression()), !dbg !512
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !511, metadata !DIExpression()), !dbg !512
  %3 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !513
  %4 = load ptr, ptr %3, align 8, !dbg !513, !tbaa !368
  %5 = load ptr, ptr %4, align 8, !dbg !513, !tbaa !300
  %6 = load ptr, ptr %5, align 8, !dbg !513, !tbaa !344
  tail call void %6(ptr noundef nonnull %5, ptr noundef %1) #9, !dbg !513
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 2, !dbg !514
  %8 = load ptr, ptr %7, align 8, !dbg !514, !tbaa !320
  %9 = load ptr, ptr %1, align 8, !dbg !515, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !516, !tbaa !312
  %11 = fadd fast double %10, 1.000000e-04, !dbg !517
  %12 = fptosi double %11 to i32, !dbg !518
  tail call void @prjm_eval_memory_free_block(ptr noundef %8, i32 noundef %12) #9, !dbg !519
  ret void, !dbg !520
}

declare !dbg !521 void @prjm_eval_memory_free_block(ptr noundef, i32 noundef) local_unnamed_addr #6

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_memcpy(ptr noundef %0, ptr nocapture noundef writeonly %1) #3 !dbg !524 {
  %3 = alloca double, align 8, !DIAssignID !533
  call void @llvm.dbg.assign(metadata i1 undef, metadata !528, metadata !DIExpression(), metadata !533, metadata ptr %3, metadata !DIExpression()), !dbg !534
  %4 = alloca double, align 8, !DIAssignID !535
  call void @llvm.dbg.assign(metadata i1 undef, metadata !529, metadata !DIExpression(), metadata !535, metadata ptr %4, metadata !DIExpression()), !dbg !534
  %5 = alloca ptr, align 8, !DIAssignID !536
  call void @llvm.dbg.assign(metadata i1 undef, metadata !530, metadata !DIExpression(), metadata !536, metadata ptr %5, metadata !DIExpression()), !dbg !534
  %6 = alloca ptr, align 8, !DIAssignID !537
  call void @llvm.dbg.assign(metadata i1 undef, metadata !531, metadata !DIExpression(), metadata !537, metadata ptr %6, metadata !DIExpression()), !dbg !534
  %7 = alloca ptr, align 8, !DIAssignID !538
  call void @llvm.dbg.assign(metadata i1 undef, metadata !532, metadata !DIExpression(), metadata !538, metadata ptr %7, metadata !DIExpression()), !dbg !534
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !526, metadata !DIExpression()), !dbg !534
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !527, metadata !DIExpression()), !dbg !534
  %8 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !539
  store double 0.000000e+00, ptr %8, align 8, !dbg !540, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !541
  store double 0.000000e+00, ptr %3, align 8, !dbg !542, !tbaa !312, !DIAssignID !543
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !528, metadata !DIExpression(), metadata !543, metadata ptr %3, metadata !DIExpression()), !dbg !534
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !544
  store double 0.000000e+00, ptr %4, align 8, !dbg !545, !tbaa !312, !DIAssignID !546
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !529, metadata !DIExpression(), metadata !546, metadata ptr %4, metadata !DIExpression()), !dbg !534
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !547
  store ptr %8, ptr %5, align 8, !dbg !548, !tbaa !300, !DIAssignID !549
  call void @llvm.dbg.assign(metadata ptr %8, metadata !530, metadata !DIExpression(), metadata !549, metadata ptr %5, metadata !DIExpression()), !dbg !534
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !550
  store ptr %3, ptr %6, align 8, !dbg !551, !tbaa !300, !DIAssignID !552
  call void @llvm.dbg.assign(metadata ptr %3, metadata !531, metadata !DIExpression(), metadata !552, metadata ptr %6, metadata !DIExpression()), !dbg !534
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %7) #9, !dbg !553
  store ptr %4, ptr %7, align 8, !dbg !554, !tbaa !300, !DIAssignID !555
  call void @llvm.dbg.assign(metadata ptr %4, metadata !532, metadata !DIExpression(), metadata !555, metadata ptr %7, metadata !DIExpression()), !dbg !534
  %9 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !556
  %10 = load ptr, ptr %9, align 8, !dbg !556, !tbaa !368
  %11 = load ptr, ptr %10, align 8, !dbg !556, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !556, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %5) #9, !dbg !556
  %13 = load ptr, ptr %9, align 8, !dbg !557, !tbaa !368
  %14 = getelementptr inbounds ptr, ptr %13, i64 1, !dbg !557
  %15 = load ptr, ptr %14, align 8, !dbg !557, !tbaa !300
  %16 = load ptr, ptr %15, align 8, !dbg !557, !tbaa !344
  call void %16(ptr noundef nonnull %15, ptr noundef nonnull %6) #9, !dbg !557
  %17 = load ptr, ptr %9, align 8, !dbg !558, !tbaa !368
  %18 = getelementptr inbounds ptr, ptr %17, i64 2, !dbg !558
  %19 = load ptr, ptr %18, align 8, !dbg !558, !tbaa !300
  %20 = load ptr, ptr %19, align 8, !dbg !558, !tbaa !344
  call void %20(ptr noundef nonnull %19, ptr noundef nonnull %7) #9, !dbg !558
  %21 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 2, !dbg !559
  %22 = load ptr, ptr %21, align 8, !dbg !559, !tbaa !320
  %23 = load ptr, ptr %5, align 8, !dbg !559, !tbaa !300
  %24 = load ptr, ptr %6, align 8, !dbg !559, !tbaa !300
  %25 = load ptr, ptr %7, align 8, !dbg !559, !tbaa !300
  %26 = call ptr @prjm_eval_memory_copy(ptr noundef %22, ptr noundef %23, ptr noundef %24, ptr noundef %25) #9, !dbg !559
  store ptr %26, ptr %1, align 8, !dbg !559, !tbaa !300
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %7) #9, !dbg !560
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !560
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !560
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !560
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !560
  ret void, !dbg !560
}

declare !dbg !561 ptr @prjm_eval_memory_copy(ptr noundef, ptr noundef, ptr noundef, ptr noundef) local_unnamed_addr #6

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_memset(ptr noundef %0, ptr nocapture noundef writeonly %1) #3 !dbg !564 {
  %3 = alloca double, align 8, !DIAssignID !573
  call void @llvm.dbg.assign(metadata i1 undef, metadata !568, metadata !DIExpression(), metadata !573, metadata ptr %3, metadata !DIExpression()), !dbg !574
  %4 = alloca double, align 8, !DIAssignID !575
  call void @llvm.dbg.assign(metadata i1 undef, metadata !569, metadata !DIExpression(), metadata !575, metadata ptr %4, metadata !DIExpression()), !dbg !574
  %5 = alloca ptr, align 8, !DIAssignID !576
  call void @llvm.dbg.assign(metadata i1 undef, metadata !570, metadata !DIExpression(), metadata !576, metadata ptr %5, metadata !DIExpression()), !dbg !574
  %6 = alloca ptr, align 8, !DIAssignID !577
  call void @llvm.dbg.assign(metadata i1 undef, metadata !571, metadata !DIExpression(), metadata !577, metadata ptr %6, metadata !DIExpression()), !dbg !574
  %7 = alloca ptr, align 8, !DIAssignID !578
  call void @llvm.dbg.assign(metadata i1 undef, metadata !572, metadata !DIExpression(), metadata !578, metadata ptr %7, metadata !DIExpression()), !dbg !574
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !566, metadata !DIExpression()), !dbg !574
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !567, metadata !DIExpression()), !dbg !574
  %8 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !579
  store double 0.000000e+00, ptr %8, align 8, !dbg !580, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !581
  store double 0.000000e+00, ptr %3, align 8, !dbg !582, !tbaa !312, !DIAssignID !583
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !568, metadata !DIExpression(), metadata !583, metadata ptr %3, metadata !DIExpression()), !dbg !574
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !584
  store double 0.000000e+00, ptr %4, align 8, !dbg !585, !tbaa !312, !DIAssignID !586
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !569, metadata !DIExpression(), metadata !586, metadata ptr %4, metadata !DIExpression()), !dbg !574
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !587
  store ptr %8, ptr %5, align 8, !dbg !588, !tbaa !300, !DIAssignID !589
  call void @llvm.dbg.assign(metadata ptr %8, metadata !570, metadata !DIExpression(), metadata !589, metadata ptr %5, metadata !DIExpression()), !dbg !574
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !590
  store ptr %3, ptr %6, align 8, !dbg !591, !tbaa !300, !DIAssignID !592
  call void @llvm.dbg.assign(metadata ptr %3, metadata !571, metadata !DIExpression(), metadata !592, metadata ptr %6, metadata !DIExpression()), !dbg !574
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %7) #9, !dbg !593
  store ptr %4, ptr %7, align 8, !dbg !594, !tbaa !300, !DIAssignID !595
  call void @llvm.dbg.assign(metadata ptr %4, metadata !572, metadata !DIExpression(), metadata !595, metadata ptr %7, metadata !DIExpression()), !dbg !574
  %9 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !596
  %10 = load ptr, ptr %9, align 8, !dbg !596, !tbaa !368
  %11 = load ptr, ptr %10, align 8, !dbg !596, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !596, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %5) #9, !dbg !596
  %13 = load ptr, ptr %9, align 8, !dbg !597, !tbaa !368
  %14 = getelementptr inbounds ptr, ptr %13, i64 1, !dbg !597
  %15 = load ptr, ptr %14, align 8, !dbg !597, !tbaa !300
  %16 = load ptr, ptr %15, align 8, !dbg !597, !tbaa !344
  call void %16(ptr noundef nonnull %15, ptr noundef nonnull %6) #9, !dbg !597
  %17 = load ptr, ptr %9, align 8, !dbg !598, !tbaa !368
  %18 = getelementptr inbounds ptr, ptr %17, i64 2, !dbg !598
  %19 = load ptr, ptr %18, align 8, !dbg !598, !tbaa !300
  %20 = load ptr, ptr %19, align 8, !dbg !598, !tbaa !344
  call void %20(ptr noundef nonnull %19, ptr noundef nonnull %7) #9, !dbg !598
  %21 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 2, !dbg !599
  %22 = load ptr, ptr %21, align 8, !dbg !599, !tbaa !320
  %23 = load ptr, ptr %5, align 8, !dbg !599, !tbaa !300
  %24 = load ptr, ptr %6, align 8, !dbg !599, !tbaa !300
  %25 = load ptr, ptr %7, align 8, !dbg !599, !tbaa !300
  %26 = call ptr @prjm_eval_memory_set(ptr noundef %22, ptr noundef %23, ptr noundef %24, ptr noundef %25) #9, !dbg !599
  store ptr %26, ptr %1, align 8, !dbg !599, !tbaa !300
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %7) #9, !dbg !600
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !600
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !600
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !600
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !600
  ret void, !dbg !600
}

declare !dbg !601 ptr @prjm_eval_memory_set(ptr noundef, ptr noundef, ptr noundef, ptr noundef) local_unnamed_addr #6

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_bnot(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !602 {
  %3 = alloca ptr, align 8, !DIAssignID !607
  call void @llvm.dbg.assign(metadata i1 undef, metadata !606, metadata !DIExpression(), metadata !607, metadata ptr %3, metadata !DIExpression()), !dbg !608
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !604, metadata !DIExpression()), !dbg !608
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !605, metadata !DIExpression()), !dbg !608
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !609
  store double 0.000000e+00, ptr %4, align 8, !dbg !610, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !611
  store ptr %4, ptr %3, align 8, !dbg !612, !tbaa !300, !DIAssignID !613
  call void @llvm.dbg.assign(metadata ptr %4, metadata !606, metadata !DIExpression(), metadata !613, metadata ptr %3, metadata !DIExpression()), !dbg !608
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !614
  %6 = load ptr, ptr %5, align 8, !dbg !614, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !614, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !614, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !614
  %9 = load ptr, ptr %3, align 8, !dbg !615, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !615, !tbaa !312
  %11 = call fast double @llvm.fabs.f64(double %10), !dbg !615
  %12 = fcmp fast olt double %11, 1.000000e-05, !dbg !615
  %13 = select fast i1 %12, double 1.000000e+00, double 0.000000e+00, !dbg !615
  %14 = load ptr, ptr %1, align 8, !dbg !615, !tbaa !300
  store double %13, ptr %14, align 8, !dbg !615, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !616
  ret void, !dbg !616
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_equal(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !617 {
  %3 = alloca double, align 8, !DIAssignID !625
  call void @llvm.dbg.assign(metadata i1 undef, metadata !621, metadata !DIExpression(), metadata !625, metadata ptr %3, metadata !DIExpression()), !dbg !626
  %4 = alloca double, align 8, !DIAssignID !627
  call void @llvm.dbg.assign(metadata i1 undef, metadata !622, metadata !DIExpression(), metadata !627, metadata ptr %4, metadata !DIExpression()), !dbg !626
  %5 = alloca ptr, align 8, !DIAssignID !628
  call void @llvm.dbg.assign(metadata i1 undef, metadata !623, metadata !DIExpression(), metadata !628, metadata ptr %5, metadata !DIExpression()), !dbg !626
  %6 = alloca ptr, align 8, !DIAssignID !629
  call void @llvm.dbg.assign(metadata i1 undef, metadata !624, metadata !DIExpression(), metadata !629, metadata ptr %6, metadata !DIExpression()), !dbg !626
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !619, metadata !DIExpression()), !dbg !626
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !620, metadata !DIExpression()), !dbg !626
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !630
  store double 0.000000e+00, ptr %3, align 8, !dbg !631, !tbaa !312, !DIAssignID !632
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !621, metadata !DIExpression(), metadata !632, metadata ptr %3, metadata !DIExpression()), !dbg !626
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !633
  store double 0.000000e+00, ptr %4, align 8, !dbg !634, !tbaa !312, !DIAssignID !635
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !622, metadata !DIExpression(), metadata !635, metadata ptr %4, metadata !DIExpression()), !dbg !626
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !636
  store ptr %3, ptr %5, align 8, !dbg !637, !tbaa !300, !DIAssignID !638
  call void @llvm.dbg.assign(metadata ptr %3, metadata !623, metadata !DIExpression(), metadata !638, metadata ptr %5, metadata !DIExpression()), !dbg !626
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !639
  store ptr %4, ptr %6, align 8, !dbg !640, !tbaa !300, !DIAssignID !641
  call void @llvm.dbg.assign(metadata ptr %4, metadata !624, metadata !DIExpression(), metadata !641, metadata ptr %6, metadata !DIExpression()), !dbg !626
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !642
  %8 = load ptr, ptr %7, align 8, !dbg !642, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !642, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !642, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !642
  %11 = load ptr, ptr %7, align 8, !dbg !643, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !643
  %13 = load ptr, ptr %12, align 8, !dbg !643, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !643, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !643
  %15 = load ptr, ptr %5, align 8, !dbg !644, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !644, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !644, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !644, !tbaa !312
  %19 = fsub fast double %16, %18, !dbg !644
  %20 = call fast double @llvm.fabs.f64(double %19), !dbg !644
  %21 = fcmp fast olt double %20, 1.000000e-05, !dbg !644
  %22 = select fast i1 %21, double 1.000000e+00, double 0.000000e+00, !dbg !644
  %23 = load ptr, ptr %1, align 8, !dbg !644, !tbaa !300
  store double %22, ptr %23, align 8, !dbg !644, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !645
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !645
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !645
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !645
  ret void, !dbg !645
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_notequal(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !646 {
  %3 = alloca double, align 8, !DIAssignID !654
  call void @llvm.dbg.assign(metadata i1 undef, metadata !650, metadata !DIExpression(), metadata !654, metadata ptr %3, metadata !DIExpression()), !dbg !655
  %4 = alloca double, align 8, !DIAssignID !656
  call void @llvm.dbg.assign(metadata i1 undef, metadata !651, metadata !DIExpression(), metadata !656, metadata ptr %4, metadata !DIExpression()), !dbg !655
  %5 = alloca ptr, align 8, !DIAssignID !657
  call void @llvm.dbg.assign(metadata i1 undef, metadata !652, metadata !DIExpression(), metadata !657, metadata ptr %5, metadata !DIExpression()), !dbg !655
  %6 = alloca ptr, align 8, !DIAssignID !658
  call void @llvm.dbg.assign(metadata i1 undef, metadata !653, metadata !DIExpression(), metadata !658, metadata ptr %6, metadata !DIExpression()), !dbg !655
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !648, metadata !DIExpression()), !dbg !655
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !649, metadata !DIExpression()), !dbg !655
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !659
  store double 0.000000e+00, ptr %3, align 8, !dbg !660, !tbaa !312, !DIAssignID !661
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !650, metadata !DIExpression(), metadata !661, metadata ptr %3, metadata !DIExpression()), !dbg !655
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !662
  store double 0.000000e+00, ptr %4, align 8, !dbg !663, !tbaa !312, !DIAssignID !664
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !651, metadata !DIExpression(), metadata !664, metadata ptr %4, metadata !DIExpression()), !dbg !655
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !665
  store ptr %3, ptr %5, align 8, !dbg !666, !tbaa !300, !DIAssignID !667
  call void @llvm.dbg.assign(metadata ptr %3, metadata !652, metadata !DIExpression(), metadata !667, metadata ptr %5, metadata !DIExpression()), !dbg !655
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !668
  store ptr %4, ptr %6, align 8, !dbg !669, !tbaa !300, !DIAssignID !670
  call void @llvm.dbg.assign(metadata ptr %4, metadata !653, metadata !DIExpression(), metadata !670, metadata ptr %6, metadata !DIExpression()), !dbg !655
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !671
  %8 = load ptr, ptr %7, align 8, !dbg !671, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !671, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !671, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !671
  %11 = load ptr, ptr %7, align 8, !dbg !672, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !672
  %13 = load ptr, ptr %12, align 8, !dbg !672, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !672, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !672
  %15 = load ptr, ptr %5, align 8, !dbg !673, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !673, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !673, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !673, !tbaa !312
  %19 = fsub fast double %16, %18, !dbg !673
  %20 = call fast double @llvm.fabs.f64(double %19), !dbg !673
  %21 = fcmp fast ogt double %20, 1.000000e-05, !dbg !673
  %22 = select fast i1 %21, double 1.000000e+00, double 0.000000e+00, !dbg !673
  %23 = load ptr, ptr %1, align 8, !dbg !673, !tbaa !300
  store double %22, ptr %23, align 8, !dbg !673, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !674
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !674
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !674
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !674
  ret void, !dbg !674
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_below(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !675 {
  %3 = alloca double, align 8, !DIAssignID !683
  call void @llvm.dbg.assign(metadata i1 undef, metadata !679, metadata !DIExpression(), metadata !683, metadata ptr %3, metadata !DIExpression()), !dbg !684
  %4 = alloca double, align 8, !DIAssignID !685
  call void @llvm.dbg.assign(metadata i1 undef, metadata !680, metadata !DIExpression(), metadata !685, metadata ptr %4, metadata !DIExpression()), !dbg !684
  %5 = alloca ptr, align 8, !DIAssignID !686
  call void @llvm.dbg.assign(metadata i1 undef, metadata !681, metadata !DIExpression(), metadata !686, metadata ptr %5, metadata !DIExpression()), !dbg !684
  %6 = alloca ptr, align 8, !DIAssignID !687
  call void @llvm.dbg.assign(metadata i1 undef, metadata !682, metadata !DIExpression(), metadata !687, metadata ptr %6, metadata !DIExpression()), !dbg !684
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !677, metadata !DIExpression()), !dbg !684
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !678, metadata !DIExpression()), !dbg !684
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !688
  store double 0.000000e+00, ptr %3, align 8, !dbg !689, !tbaa !312, !DIAssignID !690
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !679, metadata !DIExpression(), metadata !690, metadata ptr %3, metadata !DIExpression()), !dbg !684
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !691
  store double 0.000000e+00, ptr %4, align 8, !dbg !692, !tbaa !312, !DIAssignID !693
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !680, metadata !DIExpression(), metadata !693, metadata ptr %4, metadata !DIExpression()), !dbg !684
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !694
  store ptr %3, ptr %5, align 8, !dbg !695, !tbaa !300, !DIAssignID !696
  call void @llvm.dbg.assign(metadata ptr %3, metadata !681, metadata !DIExpression(), metadata !696, metadata ptr %5, metadata !DIExpression()), !dbg !684
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !697
  store ptr %4, ptr %6, align 8, !dbg !698, !tbaa !300, !DIAssignID !699
  call void @llvm.dbg.assign(metadata ptr %4, metadata !682, metadata !DIExpression(), metadata !699, metadata ptr %6, metadata !DIExpression()), !dbg !684
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !700
  %8 = load ptr, ptr %7, align 8, !dbg !700, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !700, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !700, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !700
  %11 = load ptr, ptr %7, align 8, !dbg !701, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !701
  %13 = load ptr, ptr %12, align 8, !dbg !701, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !701, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !701
  %15 = load ptr, ptr %5, align 8, !dbg !702, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !702, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !702, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !702, !tbaa !312
  %19 = fcmp fast olt double %16, %18, !dbg !702
  %20 = select fast i1 %19, double 1.000000e+00, double 0.000000e+00, !dbg !702
  %21 = load ptr, ptr %1, align 8, !dbg !702, !tbaa !300
  store double %20, ptr %21, align 8, !dbg !702, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !703
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !703
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !703
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !703
  ret void, !dbg !703
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_above(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !704 {
  %3 = alloca double, align 8, !DIAssignID !712
  call void @llvm.dbg.assign(metadata i1 undef, metadata !708, metadata !DIExpression(), metadata !712, metadata ptr %3, metadata !DIExpression()), !dbg !713
  %4 = alloca double, align 8, !DIAssignID !714
  call void @llvm.dbg.assign(metadata i1 undef, metadata !709, metadata !DIExpression(), metadata !714, metadata ptr %4, metadata !DIExpression()), !dbg !713
  %5 = alloca ptr, align 8, !DIAssignID !715
  call void @llvm.dbg.assign(metadata i1 undef, metadata !710, metadata !DIExpression(), metadata !715, metadata ptr %5, metadata !DIExpression()), !dbg !713
  %6 = alloca ptr, align 8, !DIAssignID !716
  call void @llvm.dbg.assign(metadata i1 undef, metadata !711, metadata !DIExpression(), metadata !716, metadata ptr %6, metadata !DIExpression()), !dbg !713
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !706, metadata !DIExpression()), !dbg !713
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !707, metadata !DIExpression()), !dbg !713
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !717
  store double 0.000000e+00, ptr %3, align 8, !dbg !718, !tbaa !312, !DIAssignID !719
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !708, metadata !DIExpression(), metadata !719, metadata ptr %3, metadata !DIExpression()), !dbg !713
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !720
  store double 0.000000e+00, ptr %4, align 8, !dbg !721, !tbaa !312, !DIAssignID !722
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !709, metadata !DIExpression(), metadata !722, metadata ptr %4, metadata !DIExpression()), !dbg !713
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !723
  store ptr %3, ptr %5, align 8, !dbg !724, !tbaa !300, !DIAssignID !725
  call void @llvm.dbg.assign(metadata ptr %3, metadata !710, metadata !DIExpression(), metadata !725, metadata ptr %5, metadata !DIExpression()), !dbg !713
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !726
  store ptr %4, ptr %6, align 8, !dbg !727, !tbaa !300, !DIAssignID !728
  call void @llvm.dbg.assign(metadata ptr %4, metadata !711, metadata !DIExpression(), metadata !728, metadata ptr %6, metadata !DIExpression()), !dbg !713
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !729
  %8 = load ptr, ptr %7, align 8, !dbg !729, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !729, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !729, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !729
  %11 = load ptr, ptr %7, align 8, !dbg !730, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !730
  %13 = load ptr, ptr %12, align 8, !dbg !730, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !730, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !730
  %15 = load ptr, ptr %5, align 8, !dbg !731, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !731, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !731, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !731, !tbaa !312
  %19 = fcmp fast ogt double %16, %18, !dbg !731
  %20 = select fast i1 %19, double 1.000000e+00, double 0.000000e+00, !dbg !731
  %21 = load ptr, ptr %1, align 8, !dbg !731, !tbaa !300
  store double %20, ptr %21, align 8, !dbg !731, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !732
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !732
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !732
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !732
  ret void, !dbg !732
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_beloweq(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !733 {
  %3 = alloca double, align 8, !DIAssignID !741
  call void @llvm.dbg.assign(metadata i1 undef, metadata !737, metadata !DIExpression(), metadata !741, metadata ptr %3, metadata !DIExpression()), !dbg !742
  %4 = alloca double, align 8, !DIAssignID !743
  call void @llvm.dbg.assign(metadata i1 undef, metadata !738, metadata !DIExpression(), metadata !743, metadata ptr %4, metadata !DIExpression()), !dbg !742
  %5 = alloca ptr, align 8, !DIAssignID !744
  call void @llvm.dbg.assign(metadata i1 undef, metadata !739, metadata !DIExpression(), metadata !744, metadata ptr %5, metadata !DIExpression()), !dbg !742
  %6 = alloca ptr, align 8, !DIAssignID !745
  call void @llvm.dbg.assign(metadata i1 undef, metadata !740, metadata !DIExpression(), metadata !745, metadata ptr %6, metadata !DIExpression()), !dbg !742
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !735, metadata !DIExpression()), !dbg !742
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !736, metadata !DIExpression()), !dbg !742
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !746
  store double 0.000000e+00, ptr %3, align 8, !dbg !747, !tbaa !312, !DIAssignID !748
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !737, metadata !DIExpression(), metadata !748, metadata ptr %3, metadata !DIExpression()), !dbg !742
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !749
  store double 0.000000e+00, ptr %4, align 8, !dbg !750, !tbaa !312, !DIAssignID !751
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !738, metadata !DIExpression(), metadata !751, metadata ptr %4, metadata !DIExpression()), !dbg !742
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !752
  store ptr %3, ptr %5, align 8, !dbg !753, !tbaa !300, !DIAssignID !754
  call void @llvm.dbg.assign(metadata ptr %3, metadata !739, metadata !DIExpression(), metadata !754, metadata ptr %5, metadata !DIExpression()), !dbg !742
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !755
  store ptr %4, ptr %6, align 8, !dbg !756, !tbaa !300, !DIAssignID !757
  call void @llvm.dbg.assign(metadata ptr %4, metadata !740, metadata !DIExpression(), metadata !757, metadata ptr %6, metadata !DIExpression()), !dbg !742
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !758
  %8 = load ptr, ptr %7, align 8, !dbg !758, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !758, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !758, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !758
  %11 = load ptr, ptr %7, align 8, !dbg !759, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !759
  %13 = load ptr, ptr %12, align 8, !dbg !759, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !759, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !759
  %15 = load ptr, ptr %5, align 8, !dbg !760, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !760, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !760, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !760, !tbaa !312
  %19 = fcmp fast ole double %16, %18, !dbg !760
  %20 = select fast i1 %19, double 1.000000e+00, double 0.000000e+00, !dbg !760
  %21 = load ptr, ptr %1, align 8, !dbg !760, !tbaa !300
  store double %20, ptr %21, align 8, !dbg !760, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !761
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !761
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !761
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !761
  ret void, !dbg !761
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_aboveeq(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !762 {
  %3 = alloca double, align 8, !DIAssignID !770
  call void @llvm.dbg.assign(metadata i1 undef, metadata !766, metadata !DIExpression(), metadata !770, metadata ptr %3, metadata !DIExpression()), !dbg !771
  %4 = alloca double, align 8, !DIAssignID !772
  call void @llvm.dbg.assign(metadata i1 undef, metadata !767, metadata !DIExpression(), metadata !772, metadata ptr %4, metadata !DIExpression()), !dbg !771
  %5 = alloca ptr, align 8, !DIAssignID !773
  call void @llvm.dbg.assign(metadata i1 undef, metadata !768, metadata !DIExpression(), metadata !773, metadata ptr %5, metadata !DIExpression()), !dbg !771
  %6 = alloca ptr, align 8, !DIAssignID !774
  call void @llvm.dbg.assign(metadata i1 undef, metadata !769, metadata !DIExpression(), metadata !774, metadata ptr %6, metadata !DIExpression()), !dbg !771
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !764, metadata !DIExpression()), !dbg !771
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !765, metadata !DIExpression()), !dbg !771
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !775
  store double 0.000000e+00, ptr %3, align 8, !dbg !776, !tbaa !312, !DIAssignID !777
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !766, metadata !DIExpression(), metadata !777, metadata ptr %3, metadata !DIExpression()), !dbg !771
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !778
  store double 0.000000e+00, ptr %4, align 8, !dbg !779, !tbaa !312, !DIAssignID !780
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !767, metadata !DIExpression(), metadata !780, metadata ptr %4, metadata !DIExpression()), !dbg !771
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !781
  store ptr %3, ptr %5, align 8, !dbg !782, !tbaa !300, !DIAssignID !783
  call void @llvm.dbg.assign(metadata ptr %3, metadata !768, metadata !DIExpression(), metadata !783, metadata ptr %5, metadata !DIExpression()), !dbg !771
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !784
  store ptr %4, ptr %6, align 8, !dbg !785, !tbaa !300, !DIAssignID !786
  call void @llvm.dbg.assign(metadata ptr %4, metadata !769, metadata !DIExpression(), metadata !786, metadata ptr %6, metadata !DIExpression()), !dbg !771
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !787
  %8 = load ptr, ptr %7, align 8, !dbg !787, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !787, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !787, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !787
  %11 = load ptr, ptr %7, align 8, !dbg !788, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !788
  %13 = load ptr, ptr %12, align 8, !dbg !788, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !788, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !788
  %15 = load ptr, ptr %5, align 8, !dbg !789, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !789, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !789, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !789, !tbaa !312
  %19 = fcmp fast oge double %16, %18, !dbg !789
  %20 = select fast i1 %19, double 1.000000e+00, double 0.000000e+00, !dbg !789
  %21 = load ptr, ptr %1, align 8, !dbg !789, !tbaa !300
  store double %20, ptr %21, align 8, !dbg !789, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !790
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !790
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !790
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !790
  ret void, !dbg !790
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_add(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !791 {
  %3 = alloca double, align 8, !DIAssignID !799
  call void @llvm.dbg.assign(metadata i1 undef, metadata !795, metadata !DIExpression(), metadata !799, metadata ptr %3, metadata !DIExpression()), !dbg !800
  %4 = alloca double, align 8, !DIAssignID !801
  call void @llvm.dbg.assign(metadata i1 undef, metadata !796, metadata !DIExpression(), metadata !801, metadata ptr %4, metadata !DIExpression()), !dbg !800
  %5 = alloca ptr, align 8, !DIAssignID !802
  call void @llvm.dbg.assign(metadata i1 undef, metadata !797, metadata !DIExpression(), metadata !802, metadata ptr %5, metadata !DIExpression()), !dbg !800
  %6 = alloca ptr, align 8, !DIAssignID !803
  call void @llvm.dbg.assign(metadata i1 undef, metadata !798, metadata !DIExpression(), metadata !803, metadata ptr %6, metadata !DIExpression()), !dbg !800
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !793, metadata !DIExpression()), !dbg !800
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !794, metadata !DIExpression()), !dbg !800
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !804
  store double 0.000000e+00, ptr %3, align 8, !dbg !805, !tbaa !312, !DIAssignID !806
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !795, metadata !DIExpression(), metadata !806, metadata ptr %3, metadata !DIExpression()), !dbg !800
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !807
  store double 0.000000e+00, ptr %4, align 8, !dbg !808, !tbaa !312, !DIAssignID !809
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !796, metadata !DIExpression(), metadata !809, metadata ptr %4, metadata !DIExpression()), !dbg !800
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !810
  store ptr %3, ptr %5, align 8, !dbg !811, !tbaa !300, !DIAssignID !812
  call void @llvm.dbg.assign(metadata ptr %3, metadata !797, metadata !DIExpression(), metadata !812, metadata ptr %5, metadata !DIExpression()), !dbg !800
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !813
  store ptr %4, ptr %6, align 8, !dbg !814, !tbaa !300, !DIAssignID !815
  call void @llvm.dbg.assign(metadata ptr %4, metadata !798, metadata !DIExpression(), metadata !815, metadata ptr %6, metadata !DIExpression()), !dbg !800
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !816
  %8 = load ptr, ptr %7, align 8, !dbg !816, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !816, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !816, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !816
  %11 = load ptr, ptr %7, align 8, !dbg !817, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !817
  %13 = load ptr, ptr %12, align 8, !dbg !817, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !817, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !817
  %15 = load ptr, ptr %5, align 8, !dbg !818, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !818, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !818, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !818, !tbaa !312
  %19 = fadd fast double %18, %16, !dbg !818
  %20 = load ptr, ptr %1, align 8, !dbg !818, !tbaa !300
  store double %19, ptr %20, align 8, !dbg !818, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !819
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !819
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !819
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !819
  ret void, !dbg !819
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sub(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !820 {
  %3 = alloca double, align 8, !DIAssignID !828
  call void @llvm.dbg.assign(metadata i1 undef, metadata !824, metadata !DIExpression(), metadata !828, metadata ptr %3, metadata !DIExpression()), !dbg !829
  %4 = alloca double, align 8, !DIAssignID !830
  call void @llvm.dbg.assign(metadata i1 undef, metadata !825, metadata !DIExpression(), metadata !830, metadata ptr %4, metadata !DIExpression()), !dbg !829
  %5 = alloca ptr, align 8, !DIAssignID !831
  call void @llvm.dbg.assign(metadata i1 undef, metadata !826, metadata !DIExpression(), metadata !831, metadata ptr %5, metadata !DIExpression()), !dbg !829
  %6 = alloca ptr, align 8, !DIAssignID !832
  call void @llvm.dbg.assign(metadata i1 undef, metadata !827, metadata !DIExpression(), metadata !832, metadata ptr %6, metadata !DIExpression()), !dbg !829
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !822, metadata !DIExpression()), !dbg !829
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !823, metadata !DIExpression()), !dbg !829
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !833
  store double 0.000000e+00, ptr %3, align 8, !dbg !834, !tbaa !312, !DIAssignID !835
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !824, metadata !DIExpression(), metadata !835, metadata ptr %3, metadata !DIExpression()), !dbg !829
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !836
  store double 0.000000e+00, ptr %4, align 8, !dbg !837, !tbaa !312, !DIAssignID !838
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !825, metadata !DIExpression(), metadata !838, metadata ptr %4, metadata !DIExpression()), !dbg !829
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !839
  store ptr %3, ptr %5, align 8, !dbg !840, !tbaa !300, !DIAssignID !841
  call void @llvm.dbg.assign(metadata ptr %3, metadata !826, metadata !DIExpression(), metadata !841, metadata ptr %5, metadata !DIExpression()), !dbg !829
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !842
  store ptr %4, ptr %6, align 8, !dbg !843, !tbaa !300, !DIAssignID !844
  call void @llvm.dbg.assign(metadata ptr %4, metadata !827, metadata !DIExpression(), metadata !844, metadata ptr %6, metadata !DIExpression()), !dbg !829
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !845
  %8 = load ptr, ptr %7, align 8, !dbg !845, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !845, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !845, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !845
  %11 = load ptr, ptr %7, align 8, !dbg !846, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !846
  %13 = load ptr, ptr %12, align 8, !dbg !846, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !846, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !846
  %15 = load ptr, ptr %5, align 8, !dbg !847, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !847, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !847, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !847, !tbaa !312
  %19 = fsub fast double %16, %18, !dbg !847
  %20 = load ptr, ptr %1, align 8, !dbg !847, !tbaa !300
  store double %19, ptr %20, align 8, !dbg !847, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !848
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !848
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !848
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !848
  ret void, !dbg !848
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_mul(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !849 {
  %3 = alloca double, align 8, !DIAssignID !857
  call void @llvm.dbg.assign(metadata i1 undef, metadata !853, metadata !DIExpression(), metadata !857, metadata ptr %3, metadata !DIExpression()), !dbg !858
  %4 = alloca double, align 8, !DIAssignID !859
  call void @llvm.dbg.assign(metadata i1 undef, metadata !854, metadata !DIExpression(), metadata !859, metadata ptr %4, metadata !DIExpression()), !dbg !858
  %5 = alloca ptr, align 8, !DIAssignID !860
  call void @llvm.dbg.assign(metadata i1 undef, metadata !855, metadata !DIExpression(), metadata !860, metadata ptr %5, metadata !DIExpression()), !dbg !858
  %6 = alloca ptr, align 8, !DIAssignID !861
  call void @llvm.dbg.assign(metadata i1 undef, metadata !856, metadata !DIExpression(), metadata !861, metadata ptr %6, metadata !DIExpression()), !dbg !858
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !851, metadata !DIExpression()), !dbg !858
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !852, metadata !DIExpression()), !dbg !858
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !862
  store double 0.000000e+00, ptr %3, align 8, !dbg !863, !tbaa !312, !DIAssignID !864
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !853, metadata !DIExpression(), metadata !864, metadata ptr %3, metadata !DIExpression()), !dbg !858
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !865
  store double 0.000000e+00, ptr %4, align 8, !dbg !866, !tbaa !312, !DIAssignID !867
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !854, metadata !DIExpression(), metadata !867, metadata ptr %4, metadata !DIExpression()), !dbg !858
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !868
  store ptr %3, ptr %5, align 8, !dbg !869, !tbaa !300, !DIAssignID !870
  call void @llvm.dbg.assign(metadata ptr %3, metadata !855, metadata !DIExpression(), metadata !870, metadata ptr %5, metadata !DIExpression()), !dbg !858
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !871
  store ptr %4, ptr %6, align 8, !dbg !872, !tbaa !300, !DIAssignID !873
  call void @llvm.dbg.assign(metadata ptr %4, metadata !856, metadata !DIExpression(), metadata !873, metadata ptr %6, metadata !DIExpression()), !dbg !858
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !874
  %8 = load ptr, ptr %7, align 8, !dbg !874, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !874, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !874, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !874
  %11 = load ptr, ptr %7, align 8, !dbg !875, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !875
  %13 = load ptr, ptr %12, align 8, !dbg !875, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !875, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !875
  %15 = load ptr, ptr %5, align 8, !dbg !876, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !876, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !876, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !876, !tbaa !312
  %19 = fmul fast double %18, %16, !dbg !876
  %20 = load ptr, ptr %1, align 8, !dbg !876, !tbaa !300
  store double %19, ptr %20, align 8, !dbg !876, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !877
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !877
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !877
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !877
  ret void, !dbg !877
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_div(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !878 {
  %3 = alloca double, align 8, !DIAssignID !886
  call void @llvm.dbg.assign(metadata i1 undef, metadata !882, metadata !DIExpression(), metadata !886, metadata ptr %3, metadata !DIExpression()), !dbg !887
  %4 = alloca double, align 8, !DIAssignID !888
  call void @llvm.dbg.assign(metadata i1 undef, metadata !883, metadata !DIExpression(), metadata !888, metadata ptr %4, metadata !DIExpression()), !dbg !887
  %5 = alloca ptr, align 8, !DIAssignID !889
  call void @llvm.dbg.assign(metadata i1 undef, metadata !884, metadata !DIExpression(), metadata !889, metadata ptr %5, metadata !DIExpression()), !dbg !887
  %6 = alloca ptr, align 8, !DIAssignID !890
  call void @llvm.dbg.assign(metadata i1 undef, metadata !885, metadata !DIExpression(), metadata !890, metadata ptr %6, metadata !DIExpression()), !dbg !887
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !880, metadata !DIExpression()), !dbg !887
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !881, metadata !DIExpression()), !dbg !887
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !891
  store double 0.000000e+00, ptr %3, align 8, !dbg !892, !tbaa !312, !DIAssignID !893
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !882, metadata !DIExpression(), metadata !893, metadata ptr %3, metadata !DIExpression()), !dbg !887
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !894
  store double 0.000000e+00, ptr %4, align 8, !dbg !895, !tbaa !312, !DIAssignID !896
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !883, metadata !DIExpression(), metadata !896, metadata ptr %4, metadata !DIExpression()), !dbg !887
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !897
  store ptr %3, ptr %5, align 8, !dbg !898, !tbaa !300, !DIAssignID !899
  call void @llvm.dbg.assign(metadata ptr %3, metadata !884, metadata !DIExpression(), metadata !899, metadata ptr %5, metadata !DIExpression()), !dbg !887
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !900
  store ptr %4, ptr %6, align 8, !dbg !901, !tbaa !300, !DIAssignID !902
  call void @llvm.dbg.assign(metadata ptr %4, metadata !885, metadata !DIExpression(), metadata !902, metadata ptr %6, metadata !DIExpression()), !dbg !887
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !903
  %8 = load ptr, ptr %7, align 8, !dbg !903, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !903, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !903, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !903
  %11 = load ptr, ptr %7, align 8, !dbg !904, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !904
  %13 = load ptr, ptr %12, align 8, !dbg !904, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !904, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !904
  %15 = load ptr, ptr %6, align 8, !dbg !905, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !907, !tbaa !312
  %17 = call fast double @llvm.fabs.f64(double %16), !dbg !908
  %18 = fcmp fast olt double %17, 1.000000e-05, !dbg !909
  br i1 %18, label %23, label %19, !dbg !910

19:                                               ; preds = %2
  %20 = load ptr, ptr %5, align 8, !dbg !911, !tbaa !300
  %21 = load double, ptr %20, align 8, !dbg !911, !tbaa !312
  %22 = fdiv fast double %21, %16, !dbg !911
  br label %23, !dbg !912

23:                                               ; preds = %2, %19
  %24 = phi double [ %22, %19 ], [ 0.000000e+00, %2 ]
  %25 = load ptr, ptr %1, align 8, !dbg !887, !tbaa !300
  store double %24, ptr %25, align 8, !dbg !887, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !912
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !912
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !912
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !912
  ret void, !dbg !912
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_mod(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !913 {
  %3 = alloca double, align 8, !DIAssignID !921
  call void @llvm.dbg.assign(metadata i1 undef, metadata !917, metadata !DIExpression(), metadata !921, metadata ptr %3, metadata !DIExpression()), !dbg !922
  %4 = alloca double, align 8, !DIAssignID !923
  call void @llvm.dbg.assign(metadata i1 undef, metadata !918, metadata !DIExpression(), metadata !923, metadata ptr %4, metadata !DIExpression()), !dbg !922
  %5 = alloca ptr, align 8, !DIAssignID !924
  call void @llvm.dbg.assign(metadata i1 undef, metadata !919, metadata !DIExpression(), metadata !924, metadata ptr %5, metadata !DIExpression()), !dbg !922
  %6 = alloca ptr, align 8, !DIAssignID !925
  call void @llvm.dbg.assign(metadata i1 undef, metadata !920, metadata !DIExpression(), metadata !925, metadata ptr %6, metadata !DIExpression()), !dbg !922
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !915, metadata !DIExpression()), !dbg !922
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !916, metadata !DIExpression()), !dbg !922
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !926
  store double 0.000000e+00, ptr %3, align 8, !dbg !927, !tbaa !312, !DIAssignID !928
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !917, metadata !DIExpression(), metadata !928, metadata ptr %3, metadata !DIExpression()), !dbg !922
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !929
  store double 0.000000e+00, ptr %4, align 8, !dbg !930, !tbaa !312, !DIAssignID !931
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !918, metadata !DIExpression(), metadata !931, metadata ptr %4, metadata !DIExpression()), !dbg !922
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !932
  store ptr %3, ptr %5, align 8, !dbg !933, !tbaa !300, !DIAssignID !934
  call void @llvm.dbg.assign(metadata ptr %3, metadata !919, metadata !DIExpression(), metadata !934, metadata ptr %5, metadata !DIExpression()), !dbg !922
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !935
  store ptr %4, ptr %6, align 8, !dbg !936, !tbaa !300, !DIAssignID !937
  call void @llvm.dbg.assign(metadata ptr %4, metadata !920, metadata !DIExpression(), metadata !937, metadata ptr %6, metadata !DIExpression()), !dbg !922
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !938
  %8 = load ptr, ptr %7, align 8, !dbg !938, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !938, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !938, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !938
  %11 = load ptr, ptr %7, align 8, !dbg !939, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !939
  %13 = load ptr, ptr %12, align 8, !dbg !939, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !939, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !939
  %15 = load ptr, ptr %5, align 8, !dbg !940, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !940, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !940, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !940, !tbaa !312
  call void @llvm.dbg.value(metadata double %16, metadata !941, metadata !DIExpression()), !dbg !958
  call void @llvm.dbg.value(metadata double %18, metadata !946, metadata !DIExpression()), !dbg !958
  call void @llvm.dbg.value(metadata double %16, metadata !960, metadata !DIExpression()), !dbg !966
  call void @llvm.dbg.value(metadata ptr undef, metadata !968, metadata !DIExpression()), !dbg !983
  call void @llvm.dbg.value(metadata i64 8, metadata !980, metadata !DIExpression()), !dbg !983
  call void @llvm.dbg.value(metadata ptr undef, metadata !981, metadata !DIExpression()), !dbg !983
  call void @llvm.dbg.value(metadata i64 8, metadata !982, metadata !DIExpression()), !dbg !983
  %19 = bitcast double %16 to i64, !dbg !985
  call void @llvm.dbg.value(metadata i64 %19, metadata !965, metadata !DIExpression()), !dbg !966
  call void @llvm.dbg.value(metadata i64 %19, metadata !947, metadata !DIExpression()), !dbg !958
  call void @llvm.dbg.value(metadata double %18, metadata !960, metadata !DIExpression()), !dbg !986
  call void @llvm.dbg.value(metadata ptr undef, metadata !968, metadata !DIExpression()), !dbg !988
  call void @llvm.dbg.value(metadata i64 8, metadata !980, metadata !DIExpression()), !dbg !988
  call void @llvm.dbg.value(metadata ptr undef, metadata !981, metadata !DIExpression()), !dbg !988
  call void @llvm.dbg.value(metadata i64 8, metadata !982, metadata !DIExpression()), !dbg !988
  %20 = bitcast double %18 to i64, !dbg !990
  call void @llvm.dbg.value(metadata i64 %20, metadata !965, metadata !DIExpression()), !dbg !986
  call void @llvm.dbg.value(metadata i64 %20, metadata !950, metadata !DIExpression()), !dbg !958
  %21 = call double @llvm.fabs.f64(double %16), !dbg !991
  %22 = bitcast double %21 to i64, !dbg !991
  call void @llvm.dbg.value(metadata i64 %22, metadata !951, metadata !DIExpression()), !dbg !958
  %23 = call double @llvm.fabs.f64(double %18), !dbg !992
  %24 = bitcast double %23 to i64, !dbg !992
  call void @llvm.dbg.value(metadata i64 %24, metadata !952, metadata !DIExpression()), !dbg !958
  %25 = icmp ugt i64 %24, 9218868437227405311
  %26 = icmp ugt i64 %22, 4890909195324358656
  %27 = or i1 %26, %25, !dbg !993
  br i1 %27, label %56, label %28, !dbg !993

28:                                               ; preds = %2
  %29 = icmp eq i64 %22, 4890909195324358656, !dbg !995
  br i1 %29, label %30, label %34, !dbg !997

30:                                               ; preds = %28
  %31 = icmp sgt i64 %19, -1, !dbg !998
  %32 = icmp ugt i64 %24, 4890909195324358656
  %33 = or i1 %31, %32, !dbg !999
  br i1 %33, label %56, label %36, !dbg !999

34:                                               ; preds = %28
  %35 = icmp ugt i64 %24, 4890909195324358656, !dbg !1000
  br i1 %35, label %56, label %36, !dbg !1001

36:                                               ; preds = %34, %30
  %37 = icmp eq i64 %24, 4890909195324358656, !dbg !1002
  %38 = icmp sgt i64 %20, -1
  %39 = and i1 %38, %37, !dbg !1003
  br i1 %39, label %56, label %40, !dbg !1003

40:                                               ; preds = %36
  %41 = fptosi double %16 to i64, !dbg !1004
  call void @llvm.dbg.value(metadata i64 %41, metadata !953, metadata !DIExpression()), !dbg !958
  %42 = fptosi double %18 to i64, !dbg !1005
  call void @llvm.dbg.value(metadata i64 %42, metadata !955, metadata !DIExpression()), !dbg !958
  call void @llvm.dbg.value(metadata i64 -9223372036854775808, metadata !956, metadata !DIExpression()), !dbg !958
  %43 = icmp eq i64 %42, 0, !dbg !1006
  br i1 %43, label %56, label %44, !dbg !1008

44:                                               ; preds = %40
  %45 = icmp eq i64 %41, -9223372036854775808, !dbg !1009
  %46 = icmp eq i64 %42, -1
  %47 = and i1 %45, %46, !dbg !1010
  br i1 %47, label %56, label %48, !dbg !1010

48:                                               ; preds = %44
  %49 = srem i64 %41, %42, !dbg !1011
  %50 = sitofp i64 %49 to double, !dbg !1012
  call void @llvm.dbg.value(metadata double %50, metadata !957, metadata !DIExpression()), !dbg !958
  %51 = icmp ult i64 %22, 4746794007248502784, !dbg !1013
  %52 = icmp ult i64 %24, 4746794007248502784
  %53 = and i1 %51, %52, !dbg !1014
  %54 = call fast double @llvm.fabs.f64(double %50), !dbg !1014
  %55 = select fast i1 %53, double %54, double %50, !dbg !1014
  br label %56

56:                                               ; preds = %2, %30, %34, %36, %40, %44, %48
  %57 = phi double [ 0.000000e+00, %2 ], [ 0.000000e+00, %36 ], [ 0.000000e+00, %34 ], [ 0.000000e+00, %30 ], [ %55, %48 ], [ 0.000000e+00, %44 ], [ 0.000000e+00, %40 ], !dbg !958
  %58 = load ptr, ptr %1, align 8, !dbg !940, !tbaa !300
  store double %57, ptr %58, align 8, !dbg !940, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1015
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1015
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1015
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1015
  ret void, !dbg !1015
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_boolean_and_op(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1016 {
  %3 = alloca double, align 8, !DIAssignID !1024
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1020, metadata !DIExpression(), metadata !1024, metadata ptr %3, metadata !DIExpression()), !dbg !1025
  %4 = alloca ptr, align 8, !DIAssignID !1026
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1021, metadata !DIExpression(), metadata !1026, metadata ptr %4, metadata !DIExpression()), !dbg !1025
  %5 = alloca double, align 8, !DIAssignID !1027
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1022, metadata !DIExpression(), metadata !1027, metadata ptr %5, metadata !DIExpression()), !dbg !1025
  %6 = alloca ptr, align 8, !DIAssignID !1028
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1023, metadata !DIExpression(), metadata !1028, metadata ptr %6, metadata !DIExpression()), !dbg !1025
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1018, metadata !DIExpression()), !dbg !1025
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1019, metadata !DIExpression()), !dbg !1025
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1029
  store double 0.000000e+00, ptr %3, align 8, !dbg !1030, !tbaa !312, !DIAssignID !1031
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1020, metadata !DIExpression(), metadata !1031, metadata ptr %3, metadata !DIExpression()), !dbg !1025
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1032
  store ptr %3, ptr %4, align 8, !dbg !1033, !tbaa !300, !DIAssignID !1034
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1021, metadata !DIExpression(), metadata !1034, metadata ptr %4, metadata !DIExpression()), !dbg !1025
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1035
  store double 0.000000e+00, ptr %5, align 8, !dbg !1036, !tbaa !312, !DIAssignID !1037
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1022, metadata !DIExpression(), metadata !1037, metadata ptr %5, metadata !DIExpression()), !dbg !1025
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1038
  store ptr %5, ptr %6, align 8, !dbg !1039, !tbaa !300, !DIAssignID !1040
  call void @llvm.dbg.assign(metadata ptr %5, metadata !1023, metadata !DIExpression(), metadata !1040, metadata ptr %6, metadata !DIExpression()), !dbg !1025
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1041
  %8 = load ptr, ptr %7, align 8, !dbg !1041, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1041, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1041, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %4) #9, !dbg !1041
  %11 = load ptr, ptr %4, align 8, !dbg !1042, !tbaa !300
  %12 = load double, ptr %11, align 8, !dbg !1044, !tbaa !312
  %13 = call fast double @llvm.fabs.f64(double %12), !dbg !1045
  %14 = fcmp fast ogt double %13, 1.000000e-05, !dbg !1046
  br i1 %14, label %15, label %25, !dbg !1047

15:                                               ; preds = %2
  %16 = load ptr, ptr %7, align 8, !dbg !1048, !tbaa !368
  %17 = getelementptr inbounds ptr, ptr %16, i64 1, !dbg !1048
  %18 = load ptr, ptr %17, align 8, !dbg !1048, !tbaa !300
  %19 = load ptr, ptr %18, align 8, !dbg !1048, !tbaa !344
  call void %19(ptr noundef nonnull %18, ptr noundef nonnull %6) #9, !dbg !1048
  %20 = load ptr, ptr %6, align 8, !dbg !1050, !tbaa !300
  %21 = load double, ptr %20, align 8, !dbg !1050, !tbaa !312
  %22 = call fast double @llvm.fabs.f64(double %21), !dbg !1050
  %23 = fcmp fast ogt double %22, 1.000000e-05, !dbg !1050
  %24 = select fast i1 %23, double 1.000000e+00, double 0.000000e+00, !dbg !1050
  br label %25, !dbg !1051

25:                                               ; preds = %2, %15
  %26 = phi double [ %24, %15 ], [ 0.000000e+00, %2 ]
  %27 = load ptr, ptr %1, align 8, !dbg !1052, !tbaa !300
  store double %26, ptr %27, align 8, !dbg !1052, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1053
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1053
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1053
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1053
  ret void, !dbg !1053
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_boolean_or_op(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1054 {
  %3 = alloca double, align 8, !DIAssignID !1062
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1058, metadata !DIExpression(), metadata !1062, metadata ptr %3, metadata !DIExpression()), !dbg !1063
  %4 = alloca ptr, align 8, !DIAssignID !1064
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1059, metadata !DIExpression(), metadata !1064, metadata ptr %4, metadata !DIExpression()), !dbg !1063
  %5 = alloca double, align 8, !DIAssignID !1065
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1060, metadata !DIExpression(), metadata !1065, metadata ptr %5, metadata !DIExpression()), !dbg !1063
  %6 = alloca ptr, align 8, !DIAssignID !1066
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1061, metadata !DIExpression(), metadata !1066, metadata ptr %6, metadata !DIExpression()), !dbg !1063
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1056, metadata !DIExpression()), !dbg !1063
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1057, metadata !DIExpression()), !dbg !1063
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1067
  store double 0.000000e+00, ptr %3, align 8, !dbg !1068, !tbaa !312, !DIAssignID !1069
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1058, metadata !DIExpression(), metadata !1069, metadata ptr %3, metadata !DIExpression()), !dbg !1063
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1070
  store ptr %3, ptr %4, align 8, !dbg !1071, !tbaa !300, !DIAssignID !1072
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1059, metadata !DIExpression(), metadata !1072, metadata ptr %4, metadata !DIExpression()), !dbg !1063
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1073
  store double 0.000000e+00, ptr %5, align 8, !dbg !1074, !tbaa !312, !DIAssignID !1075
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1060, metadata !DIExpression(), metadata !1075, metadata ptr %5, metadata !DIExpression()), !dbg !1063
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1076
  store ptr %5, ptr %6, align 8, !dbg !1077, !tbaa !300, !DIAssignID !1078
  call void @llvm.dbg.assign(metadata ptr %5, metadata !1061, metadata !DIExpression(), metadata !1078, metadata ptr %6, metadata !DIExpression()), !dbg !1063
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1079
  %8 = load ptr, ptr %7, align 8, !dbg !1079, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1079, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1079, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %4) #9, !dbg !1079
  %11 = load ptr, ptr %4, align 8, !dbg !1080, !tbaa !300
  %12 = load double, ptr %11, align 8, !dbg !1082, !tbaa !312
  %13 = call fast double @llvm.fabs.f64(double %12), !dbg !1083
  %14 = fcmp fast olt double %13, 1.000000e-05, !dbg !1084
  br i1 %14, label %15, label %25, !dbg !1085

15:                                               ; preds = %2
  %16 = load ptr, ptr %7, align 8, !dbg !1086, !tbaa !368
  %17 = getelementptr inbounds ptr, ptr %16, i64 1, !dbg !1086
  %18 = load ptr, ptr %17, align 8, !dbg !1086, !tbaa !300
  %19 = load ptr, ptr %18, align 8, !dbg !1086, !tbaa !344
  call void %19(ptr noundef nonnull %18, ptr noundef nonnull %6) #9, !dbg !1086
  %20 = load ptr, ptr %6, align 8, !dbg !1088, !tbaa !300
  %21 = load double, ptr %20, align 8, !dbg !1088, !tbaa !312
  %22 = call fast double @llvm.fabs.f64(double %21), !dbg !1088
  %23 = fcmp fast ogt double %22, 1.000000e-05, !dbg !1088
  %24 = select fast i1 %23, double 1.000000e+00, double 0.000000e+00, !dbg !1088
  br label %25, !dbg !1089

25:                                               ; preds = %2, %15
  %26 = phi double [ %24, %15 ], [ 1.000000e+00, %2 ]
  %27 = load ptr, ptr %1, align 8, !dbg !1090, !tbaa !300
  store double %26, ptr %27, align 8, !dbg !1090, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1091
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1091
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1091
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1091
  ret void, !dbg !1091
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_boolean_and_func(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1092 {
  %3 = alloca double, align 8, !DIAssignID !1100
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1096, metadata !DIExpression(), metadata !1100, metadata ptr %3, metadata !DIExpression()), !dbg !1101
  %4 = alloca double, align 8, !DIAssignID !1102
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1097, metadata !DIExpression(), metadata !1102, metadata ptr %4, metadata !DIExpression()), !dbg !1101
  %5 = alloca ptr, align 8, !DIAssignID !1103
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1098, metadata !DIExpression(), metadata !1103, metadata ptr %5, metadata !DIExpression()), !dbg !1101
  %6 = alloca ptr, align 8, !DIAssignID !1104
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1099, metadata !DIExpression(), metadata !1104, metadata ptr %6, metadata !DIExpression()), !dbg !1101
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1094, metadata !DIExpression()), !dbg !1101
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1095, metadata !DIExpression()), !dbg !1101
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1105
  store double 0.000000e+00, ptr %3, align 8, !dbg !1106, !tbaa !312, !DIAssignID !1107
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1096, metadata !DIExpression(), metadata !1107, metadata ptr %3, metadata !DIExpression()), !dbg !1101
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1108
  store double 0.000000e+00, ptr %4, align 8, !dbg !1109, !tbaa !312, !DIAssignID !1110
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1097, metadata !DIExpression(), metadata !1110, metadata ptr %4, metadata !DIExpression()), !dbg !1101
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1111
  store ptr %3, ptr %5, align 8, !dbg !1112, !tbaa !300, !DIAssignID !1113
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1098, metadata !DIExpression(), metadata !1113, metadata ptr %5, metadata !DIExpression()), !dbg !1101
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1114
  store ptr %4, ptr %6, align 8, !dbg !1115, !tbaa !300, !DIAssignID !1116
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1099, metadata !DIExpression(), metadata !1116, metadata ptr %6, metadata !DIExpression()), !dbg !1101
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1117
  %8 = load ptr, ptr %7, align 8, !dbg !1117, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1117, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1117, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1117
  %11 = load ptr, ptr %7, align 8, !dbg !1118, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1118
  %13 = load ptr, ptr %12, align 8, !dbg !1118, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1118, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1118
  %15 = load ptr, ptr %5, align 8, !dbg !1119, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1119, !tbaa !312
  %17 = call fast double @llvm.fabs.f64(double %16), !dbg !1119
  %18 = fcmp fast ogt double %17, 1.000000e-05, !dbg !1119
  br i1 %18, label %19, label %25, !dbg !1119

19:                                               ; preds = %2
  %20 = load ptr, ptr %6, align 8, !dbg !1119, !tbaa !300
  %21 = load double, ptr %20, align 8, !dbg !1119, !tbaa !312
  %22 = call fast double @llvm.fabs.f64(double %21), !dbg !1119
  %23 = fcmp fast ogt double %22, 1.000000e-05, !dbg !1119
  %24 = select fast i1 %23, double 1.000000e+00, double 0.000000e+00, !dbg !1119
  br label %25

25:                                               ; preds = %19, %2
  %26 = phi double [ 0.000000e+00, %2 ], [ %24, %19 ], !dbg !1101
  %27 = load ptr, ptr %1, align 8, !dbg !1119, !tbaa !300
  store double %26, ptr %27, align 8, !dbg !1119, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1120
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1120
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1120
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1120
  ret void, !dbg !1120
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_boolean_or_func(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1121 {
  %3 = alloca double, align 8, !DIAssignID !1129
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1125, metadata !DIExpression(), metadata !1129, metadata ptr %3, metadata !DIExpression()), !dbg !1130
  %4 = alloca double, align 8, !DIAssignID !1131
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1126, metadata !DIExpression(), metadata !1131, metadata ptr %4, metadata !DIExpression()), !dbg !1130
  %5 = alloca ptr, align 8, !DIAssignID !1132
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1127, metadata !DIExpression(), metadata !1132, metadata ptr %5, metadata !DIExpression()), !dbg !1130
  %6 = alloca ptr, align 8, !DIAssignID !1133
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1128, metadata !DIExpression(), metadata !1133, metadata ptr %6, metadata !DIExpression()), !dbg !1130
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1123, metadata !DIExpression()), !dbg !1130
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1124, metadata !DIExpression()), !dbg !1130
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1134
  store double 0.000000e+00, ptr %3, align 8, !dbg !1135, !tbaa !312, !DIAssignID !1136
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1125, metadata !DIExpression(), metadata !1136, metadata ptr %3, metadata !DIExpression()), !dbg !1130
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1137
  store double 0.000000e+00, ptr %4, align 8, !dbg !1138, !tbaa !312, !DIAssignID !1139
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1126, metadata !DIExpression(), metadata !1139, metadata ptr %4, metadata !DIExpression()), !dbg !1130
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1140
  store ptr %3, ptr %5, align 8, !dbg !1141, !tbaa !300, !DIAssignID !1142
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1127, metadata !DIExpression(), metadata !1142, metadata ptr %5, metadata !DIExpression()), !dbg !1130
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1143
  store ptr %4, ptr %6, align 8, !dbg !1144, !tbaa !300, !DIAssignID !1145
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1128, metadata !DIExpression(), metadata !1145, metadata ptr %6, metadata !DIExpression()), !dbg !1130
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1146
  %8 = load ptr, ptr %7, align 8, !dbg !1146, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1146, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1146, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1146
  %11 = load ptr, ptr %7, align 8, !dbg !1147, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1147
  %13 = load ptr, ptr %12, align 8, !dbg !1147, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1147, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1147
  %15 = load ptr, ptr %5, align 8, !dbg !1148, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1148, !tbaa !312
  %17 = call fast double @llvm.fabs.f64(double %16), !dbg !1148
  %18 = fcmp fast ogt double %17, 1.000000e-05, !dbg !1148
  br i1 %18, label %25, label %19, !dbg !1148

19:                                               ; preds = %2
  %20 = load ptr, ptr %6, align 8, !dbg !1148, !tbaa !300
  %21 = load double, ptr %20, align 8, !dbg !1148, !tbaa !312
  %22 = call fast double @llvm.fabs.f64(double %21), !dbg !1148
  %23 = fcmp fast ogt double %22, 1.000000e-05, !dbg !1148
  %24 = select fast i1 %23, double 1.000000e+00, double 0.000000e+00, !dbg !1148
  br label %25, !dbg !1148

25:                                               ; preds = %19, %2
  %26 = phi double [ 1.000000e+00, %2 ], [ %24, %19 ]
  %27 = load ptr, ptr %1, align 8, !dbg !1148, !tbaa !300
  store double %26, ptr %27, align 8, !dbg !1148, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1149
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1149
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1149
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1149
  ret void, !dbg !1149
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_neg(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1150 {
  %3 = alloca double, align 8, !DIAssignID !1156
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1154, metadata !DIExpression(), metadata !1156, metadata ptr %3, metadata !DIExpression()), !dbg !1157
  %4 = alloca ptr, align 8, !DIAssignID !1158
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1155, metadata !DIExpression(), metadata !1158, metadata ptr %4, metadata !DIExpression()), !dbg !1157
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1152, metadata !DIExpression()), !dbg !1157
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1153, metadata !DIExpression()), !dbg !1157
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1159
  store double 0.000000e+00, ptr %3, align 8, !dbg !1160, !tbaa !312, !DIAssignID !1161
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1154, metadata !DIExpression(), metadata !1161, metadata ptr %3, metadata !DIExpression()), !dbg !1157
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1162
  store ptr %3, ptr %4, align 8, !dbg !1163, !tbaa !300, !DIAssignID !1164
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1155, metadata !DIExpression(), metadata !1164, metadata ptr %4, metadata !DIExpression()), !dbg !1157
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1165
  %6 = load ptr, ptr %5, align 8, !dbg !1165, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1165, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1165, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %4) #9, !dbg !1165
  %9 = load ptr, ptr %4, align 8, !dbg !1166, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1166, !tbaa !312
  %11 = fneg fast double %10, !dbg !1166
  %12 = load ptr, ptr %1, align 8, !dbg !1166, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1166, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1167
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1167
  ret void, !dbg !1167
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_add_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1168 {
  %3 = alloca double, align 8, !DIAssignID !1174
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1172, metadata !DIExpression(), metadata !1174, metadata ptr %3, metadata !DIExpression()), !dbg !1175
  %4 = alloca ptr, align 8, !DIAssignID !1176
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1173, metadata !DIExpression(), metadata !1176, metadata ptr %4, metadata !DIExpression()), !dbg !1175
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1170, metadata !DIExpression()), !dbg !1175
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1171, metadata !DIExpression()), !dbg !1175
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1177
  store double 0.000000e+00, ptr %3, align 8, !dbg !1178, !tbaa !312, !DIAssignID !1179
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1172, metadata !DIExpression(), metadata !1179, metadata ptr %3, metadata !DIExpression()), !dbg !1175
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1180
  store ptr %3, ptr %4, align 8, !dbg !1181, !tbaa !300, !DIAssignID !1182
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1173, metadata !DIExpression(), metadata !1182, metadata ptr %4, metadata !DIExpression()), !dbg !1175
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1183
  %6 = load ptr, ptr %5, align 8, !dbg !1183, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1183, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1183, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1183
  %9 = load ptr, ptr %5, align 8, !dbg !1184, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1184
  %11 = load ptr, ptr %10, align 8, !dbg !1184, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1184, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1184
  %13 = load ptr, ptr %1, align 8, !dbg !1185, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1185, !tbaa !312
  %15 = load ptr, ptr %4, align 8, !dbg !1185, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1185, !tbaa !312
  %17 = fadd fast double %16, %14, !dbg !1185
  store double %17, ptr %13, align 8, !dbg !1185, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1186
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1186
  ret void, !dbg !1186
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sub_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1187 {
  %3 = alloca double, align 8, !DIAssignID !1193
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1191, metadata !DIExpression(), metadata !1193, metadata ptr %3, metadata !DIExpression()), !dbg !1194
  %4 = alloca ptr, align 8, !DIAssignID !1195
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1192, metadata !DIExpression(), metadata !1195, metadata ptr %4, metadata !DIExpression()), !dbg !1194
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1189, metadata !DIExpression()), !dbg !1194
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1190, metadata !DIExpression()), !dbg !1194
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1196
  store double 0.000000e+00, ptr %3, align 8, !dbg !1197, !tbaa !312, !DIAssignID !1198
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1191, metadata !DIExpression(), metadata !1198, metadata ptr %3, metadata !DIExpression()), !dbg !1194
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1199
  store ptr %3, ptr %4, align 8, !dbg !1200, !tbaa !300, !DIAssignID !1201
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1192, metadata !DIExpression(), metadata !1201, metadata ptr %4, metadata !DIExpression()), !dbg !1194
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1202
  %6 = load ptr, ptr %5, align 8, !dbg !1202, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1202, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1202, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1202
  %9 = load ptr, ptr %5, align 8, !dbg !1203, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1203
  %11 = load ptr, ptr %10, align 8, !dbg !1203, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1203, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1203
  %13 = load ptr, ptr %1, align 8, !dbg !1204, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1204, !tbaa !312
  %15 = load ptr, ptr %4, align 8, !dbg !1204, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1204, !tbaa !312
  %17 = fsub fast double %14, %16, !dbg !1204
  store double %17, ptr %13, align 8, !dbg !1204, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1205
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1205
  ret void, !dbg !1205
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_mul_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1206 {
  %3 = alloca double, align 8, !DIAssignID !1212
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1210, metadata !DIExpression(), metadata !1212, metadata ptr %3, metadata !DIExpression()), !dbg !1213
  %4 = alloca ptr, align 8, !DIAssignID !1214
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1211, metadata !DIExpression(), metadata !1214, metadata ptr %4, metadata !DIExpression()), !dbg !1213
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1208, metadata !DIExpression()), !dbg !1213
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1209, metadata !DIExpression()), !dbg !1213
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1215
  store double 0.000000e+00, ptr %3, align 8, !dbg !1216, !tbaa !312, !DIAssignID !1217
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1210, metadata !DIExpression(), metadata !1217, metadata ptr %3, metadata !DIExpression()), !dbg !1213
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1218
  store ptr %3, ptr %4, align 8, !dbg !1219, !tbaa !300, !DIAssignID !1220
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1211, metadata !DIExpression(), metadata !1220, metadata ptr %4, metadata !DIExpression()), !dbg !1213
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1221
  %6 = load ptr, ptr %5, align 8, !dbg !1221, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1221, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1221, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1221
  %9 = load ptr, ptr %5, align 8, !dbg !1222, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1222
  %11 = load ptr, ptr %10, align 8, !dbg !1222, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1222, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1222
  %13 = load ptr, ptr %1, align 8, !dbg !1223, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1223, !tbaa !312
  %15 = load ptr, ptr %4, align 8, !dbg !1223, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1223, !tbaa !312
  %17 = fmul fast double %16, %14, !dbg !1223
  store double %17, ptr %13, align 8, !dbg !1223, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1224
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1224
  ret void, !dbg !1224
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_div_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1225 {
  %3 = alloca double, align 8, !DIAssignID !1231
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1229, metadata !DIExpression(), metadata !1231, metadata ptr %3, metadata !DIExpression()), !dbg !1232
  %4 = alloca ptr, align 8, !DIAssignID !1233
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1230, metadata !DIExpression(), metadata !1233, metadata ptr %4, metadata !DIExpression()), !dbg !1232
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1227, metadata !DIExpression()), !dbg !1232
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1228, metadata !DIExpression()), !dbg !1232
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1234
  store double 0.000000e+00, ptr %3, align 8, !dbg !1235, !tbaa !312, !DIAssignID !1236
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1229, metadata !DIExpression(), metadata !1236, metadata ptr %3, metadata !DIExpression()), !dbg !1232
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1237
  store ptr %3, ptr %4, align 8, !dbg !1238, !tbaa !300, !DIAssignID !1239
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1230, metadata !DIExpression(), metadata !1239, metadata ptr %4, metadata !DIExpression()), !dbg !1232
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1240
  %6 = load ptr, ptr %5, align 8, !dbg !1240, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1240, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1240, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1240
  %9 = load ptr, ptr %5, align 8, !dbg !1241, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1241
  %11 = load ptr, ptr %10, align 8, !dbg !1241, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1241, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1241
  %13 = load ptr, ptr %4, align 8, !dbg !1242, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1244, !tbaa !312
  %15 = call fast double @llvm.fabs.f64(double %14), !dbg !1245
  %16 = fcmp fast olt double %15, 1.000000e-05, !dbg !1246
  %17 = load ptr, ptr %1, align 8, !dbg !1232, !tbaa !300
  br i1 %16, label %21, label %18, !dbg !1247

18:                                               ; preds = %2
  %19 = load double, ptr %17, align 8, !dbg !1248, !tbaa !312
  %20 = fdiv fast double %19, %14, !dbg !1248
  br label %21, !dbg !1249

21:                                               ; preds = %2, %18
  %22 = phi double [ %20, %18 ], [ 0.000000e+00, %2 ]
  store double %22, ptr %17, align 8, !dbg !1232, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1249
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1249
  ret void, !dbg !1249
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_bitwise_or_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1250 {
  %3 = alloca double, align 8, !DIAssignID !1256
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1254, metadata !DIExpression(), metadata !1256, metadata ptr %3, metadata !DIExpression()), !dbg !1257
  %4 = alloca ptr, align 8, !DIAssignID !1258
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1255, metadata !DIExpression(), metadata !1258, metadata ptr %4, metadata !DIExpression()), !dbg !1257
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1252, metadata !DIExpression()), !dbg !1257
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1253, metadata !DIExpression()), !dbg !1257
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1259
  store double 0.000000e+00, ptr %3, align 8, !dbg !1260, !tbaa !312, !DIAssignID !1261
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1254, metadata !DIExpression(), metadata !1261, metadata ptr %3, metadata !DIExpression()), !dbg !1257
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1262
  store ptr %3, ptr %4, align 8, !dbg !1263, !tbaa !300, !DIAssignID !1264
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1255, metadata !DIExpression(), metadata !1264, metadata ptr %4, metadata !DIExpression()), !dbg !1257
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1265
  %6 = load ptr, ptr %5, align 8, !dbg !1265, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1265, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1265, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1265
  %9 = load ptr, ptr %5, align 8, !dbg !1266, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1266
  %11 = load ptr, ptr %10, align 8, !dbg !1266, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1266, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1266
  %13 = load ptr, ptr %1, align 8, !dbg !1267, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1267, !tbaa !312
  %15 = fptosi double %14 to i64, !dbg !1267
  %16 = load ptr, ptr %4, align 8, !dbg !1267, !tbaa !300
  %17 = load double, ptr %16, align 8, !dbg !1267, !tbaa !312
  %18 = fptosi double %17 to i64, !dbg !1267
  %19 = or i64 %18, %15, !dbg !1267
  %20 = sitofp i64 %19 to double, !dbg !1267
  store double %20, ptr %13, align 8, !dbg !1267, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1268
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1268
  ret void, !dbg !1268
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_bitwise_or(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1269 {
  %3 = alloca double, align 8, !DIAssignID !1277
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1273, metadata !DIExpression(), metadata !1277, metadata ptr %3, metadata !DIExpression()), !dbg !1278
  %4 = alloca ptr, align 8, !DIAssignID !1279
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1274, metadata !DIExpression(), metadata !1279, metadata ptr %4, metadata !DIExpression()), !dbg !1278
  %5 = alloca double, align 8, !DIAssignID !1280
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1275, metadata !DIExpression(), metadata !1280, metadata ptr %5, metadata !DIExpression()), !dbg !1278
  %6 = alloca ptr, align 8, !DIAssignID !1281
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1276, metadata !DIExpression(), metadata !1281, metadata ptr %6, metadata !DIExpression()), !dbg !1278
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1271, metadata !DIExpression()), !dbg !1278
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1272, metadata !DIExpression()), !dbg !1278
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1282
  store double 0.000000e+00, ptr %3, align 8, !dbg !1283, !tbaa !312, !DIAssignID !1284
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1273, metadata !DIExpression(), metadata !1284, metadata ptr %3, metadata !DIExpression()), !dbg !1278
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1285
  store ptr %3, ptr %4, align 8, !dbg !1286, !tbaa !300, !DIAssignID !1287
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1274, metadata !DIExpression(), metadata !1287, metadata ptr %4, metadata !DIExpression()), !dbg !1278
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1288
  store double 0.000000e+00, ptr %5, align 8, !dbg !1289, !tbaa !312, !DIAssignID !1290
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1275, metadata !DIExpression(), metadata !1290, metadata ptr %5, metadata !DIExpression()), !dbg !1278
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1291
  store ptr %5, ptr %6, align 8, !dbg !1292, !tbaa !300, !DIAssignID !1293
  call void @llvm.dbg.assign(metadata ptr %5, metadata !1276, metadata !DIExpression(), metadata !1293, metadata ptr %6, metadata !DIExpression()), !dbg !1278
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1294
  %8 = load ptr, ptr %7, align 8, !dbg !1294, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1294, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1294, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %4) #9, !dbg !1294
  %11 = load ptr, ptr %7, align 8, !dbg !1295, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1295
  %13 = load ptr, ptr %12, align 8, !dbg !1295, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1295, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1295
  %15 = load ptr, ptr %4, align 8, !dbg !1296, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1296, !tbaa !312
  %17 = fptosi double %16 to i64, !dbg !1296
  %18 = load ptr, ptr %6, align 8, !dbg !1296, !tbaa !300
  %19 = load double, ptr %18, align 8, !dbg !1296, !tbaa !312
  %20 = fptosi double %19 to i64, !dbg !1296
  %21 = or i64 %20, %17, !dbg !1296
  %22 = sitofp i64 %21 to double, !dbg !1296
  %23 = load ptr, ptr %1, align 8, !dbg !1296, !tbaa !300
  store double %22, ptr %23, align 8, !dbg !1296, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1297
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1297
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1297
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1297
  ret void, !dbg !1297
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_bitwise_and_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1298 {
  %3 = alloca double, align 8, !DIAssignID !1304
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1302, metadata !DIExpression(), metadata !1304, metadata ptr %3, metadata !DIExpression()), !dbg !1305
  %4 = alloca ptr, align 8, !DIAssignID !1306
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1303, metadata !DIExpression(), metadata !1306, metadata ptr %4, metadata !DIExpression()), !dbg !1305
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1300, metadata !DIExpression()), !dbg !1305
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1301, metadata !DIExpression()), !dbg !1305
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1307
  store double 0.000000e+00, ptr %3, align 8, !dbg !1308, !tbaa !312, !DIAssignID !1309
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1302, metadata !DIExpression(), metadata !1309, metadata ptr %3, metadata !DIExpression()), !dbg !1305
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1310
  store ptr %3, ptr %4, align 8, !dbg !1311, !tbaa !300, !DIAssignID !1312
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1303, metadata !DIExpression(), metadata !1312, metadata ptr %4, metadata !DIExpression()), !dbg !1305
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1313
  %6 = load ptr, ptr %5, align 8, !dbg !1313, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1313, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1313, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1313
  %9 = load ptr, ptr %5, align 8, !dbg !1314, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1314
  %11 = load ptr, ptr %10, align 8, !dbg !1314, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1314, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1314
  %13 = load ptr, ptr %1, align 8, !dbg !1315, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1315, !tbaa !312
  %15 = fptosi double %14 to i64, !dbg !1315
  %16 = load ptr, ptr %4, align 8, !dbg !1315, !tbaa !300
  %17 = load double, ptr %16, align 8, !dbg !1315, !tbaa !312
  %18 = fptosi double %17 to i64, !dbg !1315
  %19 = and i64 %18, %15, !dbg !1315
  %20 = sitofp i64 %19 to double, !dbg !1315
  store double %20, ptr %13, align 8, !dbg !1315, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1316
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1316
  ret void, !dbg !1316
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_bitwise_and(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1317 {
  %3 = alloca double, align 8, !DIAssignID !1325
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1321, metadata !DIExpression(), metadata !1325, metadata ptr %3, metadata !DIExpression()), !dbg !1326
  %4 = alloca ptr, align 8, !DIAssignID !1327
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1322, metadata !DIExpression(), metadata !1327, metadata ptr %4, metadata !DIExpression()), !dbg !1326
  %5 = alloca double, align 8, !DIAssignID !1328
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1323, metadata !DIExpression(), metadata !1328, metadata ptr %5, metadata !DIExpression()), !dbg !1326
  %6 = alloca ptr, align 8, !DIAssignID !1329
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1324, metadata !DIExpression(), metadata !1329, metadata ptr %6, metadata !DIExpression()), !dbg !1326
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1319, metadata !DIExpression()), !dbg !1326
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1320, metadata !DIExpression()), !dbg !1326
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1330
  store double 0.000000e+00, ptr %3, align 8, !dbg !1331, !tbaa !312, !DIAssignID !1332
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1321, metadata !DIExpression(), metadata !1332, metadata ptr %3, metadata !DIExpression()), !dbg !1326
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1333
  store ptr %3, ptr %4, align 8, !dbg !1334, !tbaa !300, !DIAssignID !1335
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1322, metadata !DIExpression(), metadata !1335, metadata ptr %4, metadata !DIExpression()), !dbg !1326
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1336
  store double 0.000000e+00, ptr %5, align 8, !dbg !1337, !tbaa !312, !DIAssignID !1338
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1323, metadata !DIExpression(), metadata !1338, metadata ptr %5, metadata !DIExpression()), !dbg !1326
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1339
  store ptr %5, ptr %6, align 8, !dbg !1340, !tbaa !300, !DIAssignID !1341
  call void @llvm.dbg.assign(metadata ptr %5, metadata !1324, metadata !DIExpression(), metadata !1341, metadata ptr %6, metadata !DIExpression()), !dbg !1326
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1342
  %8 = load ptr, ptr %7, align 8, !dbg !1342, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1342, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1342, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %4) #9, !dbg !1342
  %11 = load ptr, ptr %7, align 8, !dbg !1343, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1343
  %13 = load ptr, ptr %12, align 8, !dbg !1343, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1343, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1343
  %15 = load ptr, ptr %4, align 8, !dbg !1344, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1344, !tbaa !312
  %17 = fptosi double %16 to i64, !dbg !1344
  %18 = load ptr, ptr %6, align 8, !dbg !1344, !tbaa !300
  %19 = load double, ptr %18, align 8, !dbg !1344, !tbaa !312
  %20 = fptosi double %19 to i64, !dbg !1344
  %21 = and i64 %20, %17, !dbg !1344
  %22 = sitofp i64 %21 to double, !dbg !1344
  %23 = load ptr, ptr %1, align 8, !dbg !1344, !tbaa !300
  store double %22, ptr %23, align 8, !dbg !1344, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1345
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1345
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1345
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1345
  ret void, !dbg !1345
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_mod_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1346 {
  %3 = alloca double, align 8, !DIAssignID !1352
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1350, metadata !DIExpression(), metadata !1352, metadata ptr %3, metadata !DIExpression()), !dbg !1353
  %4 = alloca ptr, align 8, !DIAssignID !1354
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1351, metadata !DIExpression(), metadata !1354, metadata ptr %4, metadata !DIExpression()), !dbg !1353
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1348, metadata !DIExpression()), !dbg !1353
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1349, metadata !DIExpression()), !dbg !1353
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1355
  store double 0.000000e+00, ptr %3, align 8, !dbg !1356, !tbaa !312, !DIAssignID !1357
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1350, metadata !DIExpression(), metadata !1357, metadata ptr %3, metadata !DIExpression()), !dbg !1353
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1358
  store ptr %3, ptr %4, align 8, !dbg !1359, !tbaa !300, !DIAssignID !1360
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1351, metadata !DIExpression(), metadata !1360, metadata ptr %4, metadata !DIExpression()), !dbg !1353
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1361
  %6 = load ptr, ptr %5, align 8, !dbg !1361, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1361, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1361, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1361
  %9 = load ptr, ptr %5, align 8, !dbg !1362, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1362
  %11 = load ptr, ptr %10, align 8, !dbg !1362, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1362, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1362
  %13 = load ptr, ptr %1, align 8, !dbg !1363, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1363, !tbaa !312
  %15 = load ptr, ptr %4, align 8, !dbg !1363, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1363, !tbaa !312
  call void @llvm.dbg.value(metadata double %14, metadata !941, metadata !DIExpression()), !dbg !1364
  call void @llvm.dbg.value(metadata double %16, metadata !946, metadata !DIExpression()), !dbg !1364
  call void @llvm.dbg.value(metadata double %14, metadata !960, metadata !DIExpression()), !dbg !1366
  call void @llvm.dbg.value(metadata ptr undef, metadata !968, metadata !DIExpression()), !dbg !1368
  call void @llvm.dbg.value(metadata i64 8, metadata !980, metadata !DIExpression()), !dbg !1368
  call void @llvm.dbg.value(metadata ptr undef, metadata !981, metadata !DIExpression()), !dbg !1368
  call void @llvm.dbg.value(metadata i64 8, metadata !982, metadata !DIExpression()), !dbg !1368
  %17 = bitcast double %14 to i64, !dbg !1370
  call void @llvm.dbg.value(metadata i64 %17, metadata !965, metadata !DIExpression()), !dbg !1366
  call void @llvm.dbg.value(metadata i64 %17, metadata !947, metadata !DIExpression()), !dbg !1364
  call void @llvm.dbg.value(metadata double %16, metadata !960, metadata !DIExpression()), !dbg !1371
  call void @llvm.dbg.value(metadata ptr undef, metadata !968, metadata !DIExpression()), !dbg !1373
  call void @llvm.dbg.value(metadata i64 8, metadata !980, metadata !DIExpression()), !dbg !1373
  call void @llvm.dbg.value(metadata ptr undef, metadata !981, metadata !DIExpression()), !dbg !1373
  call void @llvm.dbg.value(metadata i64 8, metadata !982, metadata !DIExpression()), !dbg !1373
  %18 = bitcast double %16 to i64, !dbg !1375
  call void @llvm.dbg.value(metadata i64 %18, metadata !965, metadata !DIExpression()), !dbg !1371
  call void @llvm.dbg.value(metadata i64 %18, metadata !950, metadata !DIExpression()), !dbg !1364
  %19 = call double @llvm.fabs.f64(double %14), !dbg !1376
  %20 = bitcast double %19 to i64, !dbg !1376
  call void @llvm.dbg.value(metadata i64 %20, metadata !951, metadata !DIExpression()), !dbg !1364
  %21 = call double @llvm.fabs.f64(double %16), !dbg !1377
  %22 = bitcast double %21 to i64, !dbg !1377
  call void @llvm.dbg.value(metadata i64 %22, metadata !952, metadata !DIExpression()), !dbg !1364
  %23 = icmp ugt i64 %22, 9218868437227405311
  %24 = icmp ugt i64 %20, 4890909195324358656
  %25 = or i1 %24, %23, !dbg !1378
  br i1 %25, label %54, label %26, !dbg !1378

26:                                               ; preds = %2
  %27 = icmp eq i64 %20, 4890909195324358656, !dbg !1379
  br i1 %27, label %28, label %32, !dbg !1380

28:                                               ; preds = %26
  %29 = icmp sgt i64 %17, -1, !dbg !1381
  %30 = icmp ugt i64 %22, 4890909195324358656
  %31 = or i1 %29, %30, !dbg !1382
  br i1 %31, label %54, label %34, !dbg !1382

32:                                               ; preds = %26
  %33 = icmp ugt i64 %22, 4890909195324358656, !dbg !1383
  br i1 %33, label %54, label %34, !dbg !1384

34:                                               ; preds = %32, %28
  %35 = icmp eq i64 %22, 4890909195324358656, !dbg !1385
  %36 = icmp sgt i64 %18, -1
  %37 = and i1 %36, %35, !dbg !1386
  br i1 %37, label %54, label %38, !dbg !1386

38:                                               ; preds = %34
  %39 = fptosi double %14 to i64, !dbg !1387
  call void @llvm.dbg.value(metadata i64 %39, metadata !953, metadata !DIExpression()), !dbg !1364
  %40 = fptosi double %16 to i64, !dbg !1388
  call void @llvm.dbg.value(metadata i64 %40, metadata !955, metadata !DIExpression()), !dbg !1364
  call void @llvm.dbg.value(metadata i64 -9223372036854775808, metadata !956, metadata !DIExpression()), !dbg !1364
  %41 = icmp eq i64 %40, 0, !dbg !1389
  br i1 %41, label %54, label %42, !dbg !1390

42:                                               ; preds = %38
  %43 = icmp eq i64 %39, -9223372036854775808, !dbg !1391
  %44 = icmp eq i64 %40, -1
  %45 = and i1 %43, %44, !dbg !1392
  br i1 %45, label %54, label %46, !dbg !1392

46:                                               ; preds = %42
  %47 = srem i64 %39, %40, !dbg !1393
  %48 = sitofp i64 %47 to double, !dbg !1394
  call void @llvm.dbg.value(metadata double %48, metadata !957, metadata !DIExpression()), !dbg !1364
  %49 = icmp ult i64 %20, 4746794007248502784, !dbg !1395
  %50 = icmp ult i64 %22, 4746794007248502784
  %51 = and i1 %49, %50, !dbg !1396
  %52 = call fast double @llvm.fabs.f64(double %48), !dbg !1396
  %53 = select fast i1 %51, double %52, double %48, !dbg !1396
  br label %54

54:                                               ; preds = %2, %28, %32, %34, %38, %42, %46
  %55 = phi double [ 0.000000e+00, %2 ], [ 0.000000e+00, %34 ], [ 0.000000e+00, %32 ], [ 0.000000e+00, %28 ], [ %53, %46 ], [ 0.000000e+00, %42 ], [ 0.000000e+00, %38 ], !dbg !1364
  store double %55, ptr %13, align 8, !dbg !1363, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1397
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1397
  ret void, !dbg !1397
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_pow_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1398 {
  %3 = alloca double, align 8, !DIAssignID !1405
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1402, metadata !DIExpression(), metadata !1405, metadata ptr %3, metadata !DIExpression()), !dbg !1406
  %4 = alloca ptr, align 8, !DIAssignID !1407
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1403, metadata !DIExpression(), metadata !1407, metadata ptr %4, metadata !DIExpression()), !dbg !1406
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1400, metadata !DIExpression()), !dbg !1406
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1401, metadata !DIExpression()), !dbg !1406
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1408
  store double 0.000000e+00, ptr %3, align 8, !dbg !1409, !tbaa !312, !DIAssignID !1410
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1402, metadata !DIExpression(), metadata !1410, metadata ptr %3, metadata !DIExpression()), !dbg !1406
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1411
  store ptr %3, ptr %4, align 8, !dbg !1412, !tbaa !300, !DIAssignID !1413
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1403, metadata !DIExpression(), metadata !1413, metadata ptr %4, metadata !DIExpression()), !dbg !1406
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1414
  %6 = load ptr, ptr %5, align 8, !dbg !1414, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1414, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1414, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1414
  %9 = load ptr, ptr %5, align 8, !dbg !1415, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1415
  %11 = load ptr, ptr %10, align 8, !dbg !1415, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1415, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1415
  %13 = load ptr, ptr %1, align 8, !dbg !1416, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1418, !tbaa !312
  %15 = call fast double @llvm.fabs.f64(double %14), !dbg !1419
  %16 = fcmp fast olt double %15, 1.000000e-05, !dbg !1420
  %17 = load ptr, ptr %4, align 8, !dbg !1421, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !1422, !tbaa !312
  %19 = fcmp fast olt double %18, 0.000000e+00
  %20 = select i1 %16, i1 %19, i1 false, !dbg !1423
  %21 = call fast double @llvm.pow.f64(double %14, double %18), !dbg !1423
  %22 = select i1 %20, double 0.000000e+00, double %21, !dbg !1423
  store double %22, ptr %13, align 8, !dbg !1406, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1424
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1424
  ret void, !dbg !1424
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.pow.f64(double, double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sin(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1425 {
  %3 = alloca ptr, align 8, !DIAssignID !1430
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1429, metadata !DIExpression(), metadata !1430, metadata ptr %3, metadata !DIExpression()), !dbg !1431
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1427, metadata !DIExpression()), !dbg !1431
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1428, metadata !DIExpression()), !dbg !1431
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1432
  store double 0.000000e+00, ptr %4, align 8, !dbg !1433, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1434
  store ptr %4, ptr %3, align 8, !dbg !1435, !tbaa !300, !DIAssignID !1436
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1429, metadata !DIExpression(), metadata !1436, metadata ptr %3, metadata !DIExpression()), !dbg !1431
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1437
  %6 = load ptr, ptr %5, align 8, !dbg !1437, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1437, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1437, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1437
  %9 = load ptr, ptr %3, align 8, !dbg !1438, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1438, !tbaa !312
  %11 = call fast double @llvm.sin.f64(double %10), !dbg !1438
  %12 = load ptr, ptr %1, align 8, !dbg !1438, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1438, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1439
  ret void, !dbg !1439
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.sin.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_cos(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1440 {
  %3 = alloca ptr, align 8, !DIAssignID !1445
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1444, metadata !DIExpression(), metadata !1445, metadata ptr %3, metadata !DIExpression()), !dbg !1446
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1442, metadata !DIExpression()), !dbg !1446
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1443, metadata !DIExpression()), !dbg !1446
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1447
  store double 0.000000e+00, ptr %4, align 8, !dbg !1448, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1449
  store ptr %4, ptr %3, align 8, !dbg !1450, !tbaa !300, !DIAssignID !1451
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1444, metadata !DIExpression(), metadata !1451, metadata ptr %3, metadata !DIExpression()), !dbg !1446
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1452
  %6 = load ptr, ptr %5, align 8, !dbg !1452, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1452, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1452, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1452
  %9 = load ptr, ptr %3, align 8, !dbg !1453, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1453, !tbaa !312
  %11 = call fast double @llvm.cos.f64(double %10), !dbg !1453
  %12 = load ptr, ptr %1, align 8, !dbg !1453, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1453, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1454
  ret void, !dbg !1454
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.cos.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_tan(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1455 {
  %3 = alloca ptr, align 8, !DIAssignID !1460
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1459, metadata !DIExpression(), metadata !1460, metadata ptr %3, metadata !DIExpression()), !dbg !1461
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1457, metadata !DIExpression()), !dbg !1461
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1458, metadata !DIExpression()), !dbg !1461
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1462
  store double 0.000000e+00, ptr %4, align 8, !dbg !1463, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1464
  store ptr %4, ptr %3, align 8, !dbg !1465, !tbaa !300, !DIAssignID !1466
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1459, metadata !DIExpression(), metadata !1466, metadata ptr %3, metadata !DIExpression()), !dbg !1461
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1467
  %6 = load ptr, ptr %5, align 8, !dbg !1467, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1467, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1467, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1467
  %9 = load ptr, ptr %3, align 8, !dbg !1468, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1468, !tbaa !312
  %11 = call fast nofpclass(nan inf) double @tan(double noundef nofpclass(nan inf) %10) #10, !dbg !1468
  %12 = load ptr, ptr %1, align 8, !dbg !1468, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1468, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1469
  ret void, !dbg !1469
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare !dbg !1470 nofpclass(nan inf) double @tan(double noundef nofpclass(nan inf)) local_unnamed_addr #7

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_asin(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1474 {
  %3 = alloca ptr, align 8, !DIAssignID !1479
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1478, metadata !DIExpression(), metadata !1479, metadata ptr %3, metadata !DIExpression()), !dbg !1480
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1476, metadata !DIExpression()), !dbg !1480
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1477, metadata !DIExpression()), !dbg !1480
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1481
  store double 0.000000e+00, ptr %4, align 8, !dbg !1482, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1483
  store ptr %4, ptr %3, align 8, !dbg !1484, !tbaa !300, !DIAssignID !1485
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1478, metadata !DIExpression(), metadata !1485, metadata ptr %3, metadata !DIExpression()), !dbg !1480
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1486
  %6 = load ptr, ptr %5, align 8, !dbg !1486, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1486, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1486, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1486
  %9 = load ptr, ptr %3, align 8, !dbg !1487, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1489, !tbaa !312
  %11 = fcmp fast olt double %10, -1.000000e+00, !dbg !1490
  %12 = fcmp fast ogt double %10, 1.000000e+00
  %13 = select i1 %11, i1 true, i1 %12, !dbg !1491
  br i1 %13, label %16, label %14, !dbg !1491

14:                                               ; preds = %2
  %15 = call fast nofpclass(nan inf) double @asin(double noundef nofpclass(nan inf) %10) #10, !dbg !1492
  br label %16, !dbg !1493

16:                                               ; preds = %2, %14
  %17 = phi double [ %15, %14 ], [ 0.000000e+00, %2 ]
  %18 = load ptr, ptr %1, align 8, !dbg !1480, !tbaa !300
  store double %17, ptr %18, align 8, !dbg !1480, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1493
  ret void, !dbg !1493
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare !dbg !1494 nofpclass(nan inf) double @asin(double noundef nofpclass(nan inf)) local_unnamed_addr #7

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_acos(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1495 {
  %3 = alloca ptr, align 8, !DIAssignID !1500
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1499, metadata !DIExpression(), metadata !1500, metadata ptr %3, metadata !DIExpression()), !dbg !1501
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1497, metadata !DIExpression()), !dbg !1501
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1498, metadata !DIExpression()), !dbg !1501
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1502
  store double 0.000000e+00, ptr %4, align 8, !dbg !1503, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1504
  store ptr %4, ptr %3, align 8, !dbg !1505, !tbaa !300, !DIAssignID !1506
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1499, metadata !DIExpression(), metadata !1506, metadata ptr %3, metadata !DIExpression()), !dbg !1501
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1507
  %6 = load ptr, ptr %5, align 8, !dbg !1507, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1507, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1507, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1507
  %9 = load ptr, ptr %3, align 8, !dbg !1508, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1510, !tbaa !312
  %11 = fcmp fast olt double %10, -1.000000e+00, !dbg !1511
  %12 = fcmp fast ogt double %10, 1.000000e+00
  %13 = select i1 %11, i1 true, i1 %12, !dbg !1512
  br i1 %13, label %16, label %14, !dbg !1512

14:                                               ; preds = %2
  %15 = call fast nofpclass(nan inf) double @acos(double noundef nofpclass(nan inf) %10) #10, !dbg !1513
  br label %16, !dbg !1514

16:                                               ; preds = %2, %14
  %17 = phi double [ %15, %14 ], [ 0.000000e+00, %2 ]
  %18 = load ptr, ptr %1, align 8, !dbg !1501, !tbaa !300
  store double %17, ptr %18, align 8, !dbg !1501, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1514
  ret void, !dbg !1514
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare !dbg !1515 nofpclass(nan inf) double @acos(double noundef nofpclass(nan inf)) local_unnamed_addr #7

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_atan(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1516 {
  %3 = alloca ptr, align 8, !DIAssignID !1521
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1520, metadata !DIExpression(), metadata !1521, metadata ptr %3, metadata !DIExpression()), !dbg !1522
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1518, metadata !DIExpression()), !dbg !1522
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1519, metadata !DIExpression()), !dbg !1522
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1523
  store double 0.000000e+00, ptr %4, align 8, !dbg !1524, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1525
  store ptr %4, ptr %3, align 8, !dbg !1526, !tbaa !300, !DIAssignID !1527
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1520, metadata !DIExpression(), metadata !1527, metadata ptr %3, metadata !DIExpression()), !dbg !1522
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1528
  %6 = load ptr, ptr %5, align 8, !dbg !1528, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1528, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1528, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1528
  %9 = load ptr, ptr %3, align 8, !dbg !1529, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1529, !tbaa !312
  %11 = call fast nofpclass(nan inf) double @atan(double noundef nofpclass(nan inf) %10) #10, !dbg !1529
  %12 = load ptr, ptr %1, align 8, !dbg !1529, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1529, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1530
  ret void, !dbg !1530
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare !dbg !1531 nofpclass(nan inf) double @atan(double noundef nofpclass(nan inf)) local_unnamed_addr #7

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_atan2(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1532 {
  %3 = alloca double, align 8, !DIAssignID !1540
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1536, metadata !DIExpression(), metadata !1540, metadata ptr %3, metadata !DIExpression()), !dbg !1541
  %4 = alloca double, align 8, !DIAssignID !1542
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1537, metadata !DIExpression(), metadata !1542, metadata ptr %4, metadata !DIExpression()), !dbg !1541
  %5 = alloca ptr, align 8, !DIAssignID !1543
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1538, metadata !DIExpression(), metadata !1543, metadata ptr %5, metadata !DIExpression()), !dbg !1541
  %6 = alloca ptr, align 8, !DIAssignID !1544
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1539, metadata !DIExpression(), metadata !1544, metadata ptr %6, metadata !DIExpression()), !dbg !1541
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1534, metadata !DIExpression()), !dbg !1541
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1535, metadata !DIExpression()), !dbg !1541
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1545
  store double 0.000000e+00, ptr %3, align 8, !dbg !1546, !tbaa !312, !DIAssignID !1547
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1536, metadata !DIExpression(), metadata !1547, metadata ptr %3, metadata !DIExpression()), !dbg !1541
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1548
  store double 0.000000e+00, ptr %4, align 8, !dbg !1549, !tbaa !312, !DIAssignID !1550
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1537, metadata !DIExpression(), metadata !1550, metadata ptr %4, metadata !DIExpression()), !dbg !1541
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1551
  store ptr %3, ptr %5, align 8, !dbg !1552, !tbaa !300, !DIAssignID !1553
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1538, metadata !DIExpression(), metadata !1553, metadata ptr %5, metadata !DIExpression()), !dbg !1541
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1554
  store ptr %4, ptr %6, align 8, !dbg !1555, !tbaa !300, !DIAssignID !1556
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1539, metadata !DIExpression(), metadata !1556, metadata ptr %6, metadata !DIExpression()), !dbg !1541
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1557
  %8 = load ptr, ptr %7, align 8, !dbg !1557, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1557, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1557, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1557
  %11 = load ptr, ptr %7, align 8, !dbg !1558, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1558
  %13 = load ptr, ptr %12, align 8, !dbg !1558, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1558, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1558
  %15 = load ptr, ptr %5, align 8, !dbg !1559, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1559, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !1559, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !1559, !tbaa !312
  %19 = call fast nofpclass(nan inf) double @atan2(double noundef nofpclass(nan inf) %16, double noundef nofpclass(nan inf) %18) #10, !dbg !1559
  %20 = load ptr, ptr %1, align 8, !dbg !1559, !tbaa !300
  store double %19, ptr %20, align 8, !dbg !1559, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1560
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1560
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1560
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1560
  ret void, !dbg !1560
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare !dbg !1561 nofpclass(nan inf) double @atan2(double noundef nofpclass(nan inf), double noundef nofpclass(nan inf)) local_unnamed_addr #7

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sqrt(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1564 {
  %3 = alloca ptr, align 8, !DIAssignID !1569
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1568, metadata !DIExpression(), metadata !1569, metadata ptr %3, metadata !DIExpression()), !dbg !1570
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1566, metadata !DIExpression()), !dbg !1570
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1567, metadata !DIExpression()), !dbg !1570
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1571
  store double 0.000000e+00, ptr %4, align 8, !dbg !1572, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1573
  store ptr %4, ptr %3, align 8, !dbg !1574, !tbaa !300, !DIAssignID !1575
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1568, metadata !DIExpression(), metadata !1575, metadata ptr %3, metadata !DIExpression()), !dbg !1570
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1576
  %6 = load ptr, ptr %5, align 8, !dbg !1576, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1576, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1576, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1576
  %9 = load ptr, ptr %3, align 8, !dbg !1577, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1577, !tbaa !312
  %11 = call fast double @llvm.fabs.f64(double %10), !dbg !1577
  %12 = call fast double @llvm.sqrt.f64(double %11), !dbg !1577
  %13 = load ptr, ptr %1, align 8, !dbg !1577, !tbaa !300
  store double %12, ptr %13, align 8, !dbg !1577, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1578
  ret void, !dbg !1578
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.sqrt.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_pow(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1579 {
  %3 = alloca double, align 8, !DIAssignID !1588
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1583, metadata !DIExpression(), metadata !1588, metadata ptr %3, metadata !DIExpression()), !dbg !1589
  %4 = alloca double, align 8, !DIAssignID !1590
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1584, metadata !DIExpression(), metadata !1590, metadata ptr %4, metadata !DIExpression()), !dbg !1589
  %5 = alloca ptr, align 8, !DIAssignID !1591
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1585, metadata !DIExpression(), metadata !1591, metadata ptr %5, metadata !DIExpression()), !dbg !1589
  %6 = alloca ptr, align 8, !DIAssignID !1592
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1586, metadata !DIExpression(), metadata !1592, metadata ptr %6, metadata !DIExpression()), !dbg !1589
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1581, metadata !DIExpression()), !dbg !1589
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1582, metadata !DIExpression()), !dbg !1589
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1593
  store double 0.000000e+00, ptr %3, align 8, !dbg !1594, !tbaa !312, !DIAssignID !1595
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1583, metadata !DIExpression(), metadata !1595, metadata ptr %3, metadata !DIExpression()), !dbg !1589
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1596
  store double 0.000000e+00, ptr %4, align 8, !dbg !1597, !tbaa !312, !DIAssignID !1598
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1584, metadata !DIExpression(), metadata !1598, metadata ptr %4, metadata !DIExpression()), !dbg !1589
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1599
  store ptr %3, ptr %5, align 8, !dbg !1600, !tbaa !300, !DIAssignID !1601
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1585, metadata !DIExpression(), metadata !1601, metadata ptr %5, metadata !DIExpression()), !dbg !1589
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1602
  store ptr %4, ptr %6, align 8, !dbg !1603, !tbaa !300, !DIAssignID !1604
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1586, metadata !DIExpression(), metadata !1604, metadata ptr %6, metadata !DIExpression()), !dbg !1589
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1605
  %8 = load ptr, ptr %7, align 8, !dbg !1605, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1605, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1605, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1605
  %11 = load ptr, ptr %7, align 8, !dbg !1606, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1606
  %13 = load ptr, ptr %12, align 8, !dbg !1606, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1606, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1606
  %15 = load ptr, ptr %5, align 8, !dbg !1607, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1609, !tbaa !312
  %17 = call fast double @llvm.fabs.f64(double %16), !dbg !1610
  %18 = fcmp fast olt double %17, 1.000000e-05, !dbg !1611
  %19 = load ptr, ptr %6, align 8, !dbg !1612, !tbaa !300
  %20 = load double, ptr %19, align 8, !dbg !1613, !tbaa !312
  %21 = fcmp fast olt double %20, 0.000000e+00
  %22 = select i1 %18, i1 %21, i1 false, !dbg !1614
  %23 = call fast double @llvm.pow.f64(double %16, double %20), !dbg !1614
  %24 = select i1 %22, double 0.000000e+00, double %23, !dbg !1614
  %25 = load ptr, ptr %1, align 8, !dbg !1589, !tbaa !300
  store double %24, ptr %25, align 8, !dbg !1589, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1615
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1615
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1615
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1615
  ret void, !dbg !1615
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_exp(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1616 {
  %3 = alloca ptr, align 8, !DIAssignID !1621
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1620, metadata !DIExpression(), metadata !1621, metadata ptr %3, metadata !DIExpression()), !dbg !1622
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1618, metadata !DIExpression()), !dbg !1622
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1619, metadata !DIExpression()), !dbg !1622
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1623
  store double 0.000000e+00, ptr %4, align 8, !dbg !1624, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1625
  store ptr %4, ptr %3, align 8, !dbg !1626, !tbaa !300, !DIAssignID !1627
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1620, metadata !DIExpression(), metadata !1627, metadata ptr %3, metadata !DIExpression()), !dbg !1622
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1628
  %6 = load ptr, ptr %5, align 8, !dbg !1628, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1628, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1628, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1628
  %9 = load ptr, ptr %3, align 8, !dbg !1629, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1629, !tbaa !312
  %11 = call fast double @llvm.exp.f64(double %10), !dbg !1629
  %12 = load ptr, ptr %1, align 8, !dbg !1629, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1629, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1630
  ret void, !dbg !1630
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.exp.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_log(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1631 {
  %3 = alloca ptr, align 8, !DIAssignID !1636
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1635, metadata !DIExpression(), metadata !1636, metadata ptr %3, metadata !DIExpression()), !dbg !1637
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1633, metadata !DIExpression()), !dbg !1637
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1634, metadata !DIExpression()), !dbg !1637
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1638
  store double 0.000000e+00, ptr %4, align 8, !dbg !1639, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1640
  store ptr %4, ptr %3, align 8, !dbg !1641, !tbaa !300, !DIAssignID !1642
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1635, metadata !DIExpression(), metadata !1642, metadata ptr %3, metadata !DIExpression()), !dbg !1637
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1643
  %6 = load ptr, ptr %5, align 8, !dbg !1643, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1643, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1643, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1643
  %9 = load ptr, ptr %3, align 8, !dbg !1644, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1646, !tbaa !312
  %11 = fcmp fast ugt double %10, 0.000000e+00, !dbg !1647
  %12 = call fast double @llvm.log.f64(double %10), !dbg !1648
  %13 = select i1 %11, double %12, double 0.000000e+00, !dbg !1648
  %14 = load ptr, ptr %1, align 8, !dbg !1637, !tbaa !300
  store double %13, ptr %14, align 8, !dbg !1637, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1649
  ret void, !dbg !1649
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.log.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_log10(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1650 {
  %3 = alloca ptr, align 8, !DIAssignID !1655
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1654, metadata !DIExpression(), metadata !1655, metadata ptr %3, metadata !DIExpression()), !dbg !1656
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1652, metadata !DIExpression()), !dbg !1656
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1653, metadata !DIExpression()), !dbg !1656
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1657
  store double 0.000000e+00, ptr %4, align 8, !dbg !1658, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1659
  store ptr %4, ptr %3, align 8, !dbg !1660, !tbaa !300, !DIAssignID !1661
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1654, metadata !DIExpression(), metadata !1661, metadata ptr %3, metadata !DIExpression()), !dbg !1656
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1662
  %6 = load ptr, ptr %5, align 8, !dbg !1662, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1662, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1662, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1662
  %9 = load ptr, ptr %3, align 8, !dbg !1663, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1665, !tbaa !312
  %11 = fcmp fast ugt double %10, 0.000000e+00, !dbg !1666
  %12 = call fast double @llvm.log10.f64(double %10), !dbg !1667
  %13 = select i1 %11, double %12, double 0.000000e+00, !dbg !1667
  %14 = load ptr, ptr %1, align 8, !dbg !1656, !tbaa !300
  store double %13, ptr %14, align 8, !dbg !1656, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1668
  ret void, !dbg !1668
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.log10.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_floor(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1669 {
  %3 = alloca ptr, align 8, !DIAssignID !1674
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1673, metadata !DIExpression(), metadata !1674, metadata ptr %3, metadata !DIExpression()), !dbg !1675
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1671, metadata !DIExpression()), !dbg !1675
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1672, metadata !DIExpression()), !dbg !1675
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1676
  store double 0.000000e+00, ptr %4, align 8, !dbg !1677, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1678
  store ptr %4, ptr %3, align 8, !dbg !1679, !tbaa !300, !DIAssignID !1680
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1673, metadata !DIExpression(), metadata !1680, metadata ptr %3, metadata !DIExpression()), !dbg !1675
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1681
  %6 = load ptr, ptr %5, align 8, !dbg !1681, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1681, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1681, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1681
  %9 = load ptr, ptr %3, align 8, !dbg !1682, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1682, !tbaa !312
  %11 = call fast double @llvm.floor.f64(double %10), !dbg !1682
  %12 = load ptr, ptr %1, align 8, !dbg !1682, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1682, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1683
  ret void, !dbg !1683
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.floor.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_ceil(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1684 {
  %3 = alloca ptr, align 8, !DIAssignID !1689
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1688, metadata !DIExpression(), metadata !1689, metadata ptr %3, metadata !DIExpression()), !dbg !1690
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1686, metadata !DIExpression()), !dbg !1690
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1687, metadata !DIExpression()), !dbg !1690
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1691
  store double 0.000000e+00, ptr %4, align 8, !dbg !1692, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1693
  store ptr %4, ptr %3, align 8, !dbg !1694, !tbaa !300, !DIAssignID !1695
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1688, metadata !DIExpression(), metadata !1695, metadata ptr %3, metadata !DIExpression()), !dbg !1690
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1696
  %6 = load ptr, ptr %5, align 8, !dbg !1696, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1696, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1696, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1696
  %9 = load ptr, ptr %3, align 8, !dbg !1697, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1697, !tbaa !312
  %11 = call fast double @llvm.ceil.f64(double %10), !dbg !1697
  %12 = load ptr, ptr %1, align 8, !dbg !1697, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1697, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1698
  ret void, !dbg !1698
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.ceil.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sigmoid(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1699 {
  %3 = alloca double, align 8, !DIAssignID !1708
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1703, metadata !DIExpression(), metadata !1708, metadata ptr %3, metadata !DIExpression()), !dbg !1709
  %4 = alloca double, align 8, !DIAssignID !1710
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1704, metadata !DIExpression(), metadata !1710, metadata ptr %4, metadata !DIExpression()), !dbg !1709
  %5 = alloca ptr, align 8, !DIAssignID !1711
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1705, metadata !DIExpression(), metadata !1711, metadata ptr %5, metadata !DIExpression()), !dbg !1709
  %6 = alloca ptr, align 8, !DIAssignID !1712
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1706, metadata !DIExpression(), metadata !1712, metadata ptr %6, metadata !DIExpression()), !dbg !1709
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1701, metadata !DIExpression()), !dbg !1709
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1702, metadata !DIExpression()), !dbg !1709
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1713
  store double 0.000000e+00, ptr %3, align 8, !dbg !1714, !tbaa !312, !DIAssignID !1715
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1703, metadata !DIExpression(), metadata !1715, metadata ptr %3, metadata !DIExpression()), !dbg !1709
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1716
  store double 0.000000e+00, ptr %4, align 8, !dbg !1717, !tbaa !312, !DIAssignID !1718
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1704, metadata !DIExpression(), metadata !1718, metadata ptr %4, metadata !DIExpression()), !dbg !1709
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1719
  store ptr %3, ptr %5, align 8, !dbg !1720, !tbaa !300, !DIAssignID !1721
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1705, metadata !DIExpression(), metadata !1721, metadata ptr %5, metadata !DIExpression()), !dbg !1709
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1722
  store ptr %4, ptr %6, align 8, !dbg !1723, !tbaa !300, !DIAssignID !1724
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1706, metadata !DIExpression(), metadata !1724, metadata ptr %6, metadata !DIExpression()), !dbg !1709
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1725
  %8 = load ptr, ptr %7, align 8, !dbg !1725, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1725, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1725, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1725
  %11 = load ptr, ptr %7, align 8, !dbg !1726, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1726
  %13 = load ptr, ptr %12, align 8, !dbg !1726, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1726, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1726
  %15 = load ptr, ptr %5, align 8, !dbg !1727, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1728, !tbaa !312
  %17 = fneg fast double %16, !dbg !1729
  %18 = load ptr, ptr %6, align 8, !dbg !1730, !tbaa !300
  %19 = load double, ptr %18, align 8, !dbg !1731, !tbaa !312
  %20 = fmul fast double %19, %17, !dbg !1732
  %21 = call fast double @llvm.exp.f64(double %20), !dbg !1733
  %22 = fadd fast double %21, 1.000000e+00, !dbg !1734
  tail call void @llvm.dbg.value(metadata double %22, metadata !1707, metadata !DIExpression()), !dbg !1709
  %23 = fcmp fast ogt double %22, 1.000000e-05, !dbg !1735
  %24 = fdiv fast double 1.000000e+00, %22, !dbg !1735
  %25 = select fast i1 %23, double %24, double 0.000000e+00, !dbg !1735
  %26 = load ptr, ptr %1, align 8, !dbg !1735, !tbaa !300
  store double %25, ptr %26, align 8, !dbg !1735, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1736
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1736
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1736
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1736
  ret void, !dbg !1736
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sqr(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1737 {
  %3 = alloca ptr, align 8, !DIAssignID !1742
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1741, metadata !DIExpression(), metadata !1742, metadata ptr %3, metadata !DIExpression()), !dbg !1743
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1739, metadata !DIExpression()), !dbg !1743
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1740, metadata !DIExpression()), !dbg !1743
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1744
  store double 0.000000e+00, ptr %4, align 8, !dbg !1745, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1746
  store ptr %4, ptr %3, align 8, !dbg !1747, !tbaa !300, !DIAssignID !1748
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1741, metadata !DIExpression(), metadata !1748, metadata ptr %3, metadata !DIExpression()), !dbg !1743
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1749
  %6 = load ptr, ptr %5, align 8, !dbg !1749, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1749, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1749, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1749
  %9 = load ptr, ptr %3, align 8, !dbg !1750, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1750, !tbaa !312
  %11 = fmul fast double %10, %10, !dbg !1750
  %12 = load ptr, ptr %1, align 8, !dbg !1750, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1750, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1751
  ret void, !dbg !1751
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_abs(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1752 {
  %3 = alloca ptr, align 8, !DIAssignID !1757
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1756, metadata !DIExpression(), metadata !1757, metadata ptr %3, metadata !DIExpression()), !dbg !1758
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1754, metadata !DIExpression()), !dbg !1758
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1755, metadata !DIExpression()), !dbg !1758
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1759
  store double 0.000000e+00, ptr %4, align 8, !dbg !1760, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1761
  store ptr %4, ptr %3, align 8, !dbg !1762, !tbaa !300, !DIAssignID !1763
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1756, metadata !DIExpression(), metadata !1763, metadata ptr %3, metadata !DIExpression()), !dbg !1758
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1764
  %6 = load ptr, ptr %5, align 8, !dbg !1764, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1764, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1764, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1764
  %9 = load ptr, ptr %3, align 8, !dbg !1765, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1765, !tbaa !312
  %11 = call fast double @llvm.fabs.f64(double %10), !dbg !1765
  %12 = load ptr, ptr %1, align 8, !dbg !1765, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1765, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1766
  ret void, !dbg !1766
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_min(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1767 {
  %3 = alloca double, align 8, !DIAssignID !1775
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1771, metadata !DIExpression(), metadata !1775, metadata ptr %3, metadata !DIExpression()), !dbg !1776
  %4 = alloca double, align 8, !DIAssignID !1777
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1772, metadata !DIExpression(), metadata !1777, metadata ptr %4, metadata !DIExpression()), !dbg !1776
  %5 = alloca ptr, align 8, !DIAssignID !1778
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1773, metadata !DIExpression(), metadata !1778, metadata ptr %5, metadata !DIExpression()), !dbg !1776
  %6 = alloca ptr, align 8, !DIAssignID !1779
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1774, metadata !DIExpression(), metadata !1779, metadata ptr %6, metadata !DIExpression()), !dbg !1776
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1769, metadata !DIExpression()), !dbg !1776
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1770, metadata !DIExpression()), !dbg !1776
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1780
  store double 0.000000e+00, ptr %3, align 8, !dbg !1781, !tbaa !312, !DIAssignID !1782
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1771, metadata !DIExpression(), metadata !1782, metadata ptr %3, metadata !DIExpression()), !dbg !1776
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1783
  store double 0.000000e+00, ptr %4, align 8, !dbg !1784, !tbaa !312, !DIAssignID !1785
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1772, metadata !DIExpression(), metadata !1785, metadata ptr %4, metadata !DIExpression()), !dbg !1776
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1786
  store ptr %3, ptr %5, align 8, !dbg !1787, !tbaa !300, !DIAssignID !1788
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1773, metadata !DIExpression(), metadata !1788, metadata ptr %5, metadata !DIExpression()), !dbg !1776
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1789
  store ptr %4, ptr %6, align 8, !dbg !1790, !tbaa !300, !DIAssignID !1791
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1774, metadata !DIExpression(), metadata !1791, metadata ptr %6, metadata !DIExpression()), !dbg !1776
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1792
  %8 = load ptr, ptr %7, align 8, !dbg !1792, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1792, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1792, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1792
  %11 = load ptr, ptr %7, align 8, !dbg !1793, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1793
  %13 = load ptr, ptr %12, align 8, !dbg !1793, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1793, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1793
  %15 = load ptr, ptr %5, align 8, !dbg !1794, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1794, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !1794, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !1794, !tbaa !312
  %19 = call fast double @llvm.minnum.f64(double %16, double %18), !dbg !1794
  %20 = load ptr, ptr %1, align 8, !dbg !1794, !tbaa !300
  store double %19, ptr %20, align 8, !dbg !1794, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1795
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1795
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1795
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1795
  ret void, !dbg !1795
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_max(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1796 {
  %3 = alloca double, align 8, !DIAssignID !1804
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1800, metadata !DIExpression(), metadata !1804, metadata ptr %3, metadata !DIExpression()), !dbg !1805
  %4 = alloca double, align 8, !DIAssignID !1806
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1801, metadata !DIExpression(), metadata !1806, metadata ptr %4, metadata !DIExpression()), !dbg !1805
  %5 = alloca ptr, align 8, !DIAssignID !1807
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1802, metadata !DIExpression(), metadata !1807, metadata ptr %5, metadata !DIExpression()), !dbg !1805
  %6 = alloca ptr, align 8, !DIAssignID !1808
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1803, metadata !DIExpression(), metadata !1808, metadata ptr %6, metadata !DIExpression()), !dbg !1805
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1798, metadata !DIExpression()), !dbg !1805
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1799, metadata !DIExpression()), !dbg !1805
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1809
  store double 0.000000e+00, ptr %3, align 8, !dbg !1810, !tbaa !312, !DIAssignID !1811
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1800, metadata !DIExpression(), metadata !1811, metadata ptr %3, metadata !DIExpression()), !dbg !1805
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1812
  store double 0.000000e+00, ptr %4, align 8, !dbg !1813, !tbaa !312, !DIAssignID !1814
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1801, metadata !DIExpression(), metadata !1814, metadata ptr %4, metadata !DIExpression()), !dbg !1805
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1815
  store ptr %3, ptr %5, align 8, !dbg !1816, !tbaa !300, !DIAssignID !1817
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1802, metadata !DIExpression(), metadata !1817, metadata ptr %5, metadata !DIExpression()), !dbg !1805
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1818
  store ptr %4, ptr %6, align 8, !dbg !1819, !tbaa !300, !DIAssignID !1820
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1803, metadata !DIExpression(), metadata !1820, metadata ptr %6, metadata !DIExpression()), !dbg !1805
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1821
  %8 = load ptr, ptr %7, align 8, !dbg !1821, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1821, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1821, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1821
  %11 = load ptr, ptr %7, align 8, !dbg !1822, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1822
  %13 = load ptr, ptr %12, align 8, !dbg !1822, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1822, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1822
  %15 = load ptr, ptr %5, align 8, !dbg !1823, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1823, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !1823, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !1823, !tbaa !312
  %19 = call fast double @llvm.maxnum.f64(double %16, double %18), !dbg !1823
  %20 = load ptr, ptr %1, align 8, !dbg !1823, !tbaa !300
  store double %19, ptr %20, align 8, !dbg !1823, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1824
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1824
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1824
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1824
  ret void, !dbg !1824
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sign(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1825 {
  %3 = alloca ptr, align 8, !DIAssignID !1830
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1829, metadata !DIExpression(), metadata !1830, metadata ptr %3, metadata !DIExpression()), !dbg !1831
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1827, metadata !DIExpression()), !dbg !1831
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1828, metadata !DIExpression()), !dbg !1831
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1832
  store double 0.000000e+00, ptr %4, align 8, !dbg !1833, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1834
  store ptr %4, ptr %3, align 8, !dbg !1835, !tbaa !300, !DIAssignID !1836
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1829, metadata !DIExpression(), metadata !1836, metadata ptr %3, metadata !DIExpression()), !dbg !1831
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1837
  %6 = load ptr, ptr %5, align 8, !dbg !1837, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1837, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1837, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1837
  %9 = load ptr, ptr %3, align 8, !dbg !1838, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1840, !tbaa !312
  %11 = fcmp fast oeq double %10, 0.000000e+00, !dbg !1841
  %12 = fcmp fast olt double %10, 0.000000e+00, !dbg !1842
  %13 = select fast i1 %12, double -1.000000e+00, double 1.000000e+00, !dbg !1842
  %14 = select i1 %11, double 0.000000e+00, double %13, !dbg !1842
  %15 = load ptr, ptr %1, align 8, !dbg !1831, !tbaa !300
  store double %14, ptr %15, align 8, !dbg !1831, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1843
  ret void, !dbg !1843
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_rand(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1844 {
  %3 = alloca ptr, align 8, !DIAssignID !1850
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1848, metadata !DIExpression(), metadata !1850, metadata ptr %3, metadata !DIExpression()), !dbg !1851
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1846, metadata !DIExpression()), !dbg !1851
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1847, metadata !DIExpression()), !dbg !1851
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1852
  store double 0.000000e+00, ptr %4, align 8, !dbg !1853, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1854
  store ptr %4, ptr %3, align 8, !dbg !1855, !tbaa !300, !DIAssignID !1856
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1848, metadata !DIExpression(), metadata !1856, metadata ptr %3, metadata !DIExpression()), !dbg !1851
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1857
  %6 = load ptr, ptr %5, align 8, !dbg !1857, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1857, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1857, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1857
  %9 = load ptr, ptr %3, align 8, !dbg !1858, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1859, !tbaa !312
  tail call void @llvm.dbg.value(metadata double poison, metadata !1849, metadata !DIExpression()), !dbg !1851
  %11 = call align 4 ptr @llvm.threadlocal.address.p0(ptr align 4 @prjm_eval_genrand_int32.mti), !dbg !1860
  %12 = load i32, ptr %11, align 4, !dbg !1860, !tbaa !295
  %13 = icmp eq i32 %12, 0, !dbg !1860
  br i1 %13, label %14, label %31, !dbg !1862

14:                                               ; preds = %2
  call void @llvm.dbg.value(metadata i32 1094840333, metadata !244, metadata !DIExpression()), !dbg !1863
  %15 = call align 4 ptr @llvm.threadlocal.address.p0(ptr align 4 @prjm_eval_genrand_int32.mt), !dbg !1864
  store i32 1094840333, ptr %15, align 4, !dbg !1865, !tbaa !295
  store i32 1, ptr %11, align 4, !dbg !1866, !tbaa !295
  br label %16, !dbg !1868

16:                                               ; preds = %16, %14
  %17 = phi i32 [ 1, %14 ], [ %29, %16 ]
  %18 = add nsw i32 %17, -1, !dbg !1869
  %19 = sext i32 %18 to i64, !dbg !1872
  %20 = getelementptr inbounds [624 x i32], ptr %15, i64 0, i64 %19, !dbg !1872
  %21 = load i32, ptr %20, align 4, !dbg !1872, !tbaa !295
  %22 = lshr i32 %21, 30, !dbg !1873
  %23 = xor i32 %22, %21, !dbg !1874
  %24 = mul i32 %23, 1812433253, !dbg !1875
  %25 = sext i32 %17 to i64, !dbg !1876
  %26 = add i32 %24, %17, !dbg !1877
  %27 = getelementptr inbounds [624 x i32], ptr %15, i64 0, i64 %25, !dbg !1878
  store i32 %26, ptr %27, align 4, !dbg !1879, !tbaa !295
  %28 = load i32, ptr %11, align 4, !dbg !1880, !tbaa !295
  %29 = add nsw i32 %28, 1, !dbg !1880
  store i32 %29, ptr %11, align 4, !dbg !1866, !tbaa !295
  %30 = icmp slt i32 %28, 623, !dbg !1881
  br i1 %30, label %16, label %34, !dbg !1868, !llvm.loop !1882

31:                                               ; preds = %2
  %32 = icmp sgt i32 %12, 623, !dbg !1884
  %33 = call align 4 ptr @llvm.threadlocal.address.p0(ptr align 4 @prjm_eval_genrand_int32.mt)
  br i1 %32, label %34, label %132, !dbg !1885

34:                                               ; preds = %16, %31
  %35 = phi ptr [ %33, %31 ], [ %15, %16 ]
  call void @llvm.dbg.value(metadata i32 0, metadata !247, metadata !DIExpression()), !dbg !1886
  %36 = load i32, ptr %35, align 4, !dbg !1887, !tbaa !295
  br label %37, !dbg !1891

37:                                               ; preds = %37, %34
  %38 = phi i64 [ 0, %34 ], [ %75, %37 ], !dbg !1892
  %39 = phi i32 [ %36, %34 ], [ %48, %37 ]
  %40 = or disjoint i64 %38, 1, !dbg !1891
  %41 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %38, !dbg !1887
  %42 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %40, !dbg !1887
  %43 = or disjoint i64 %38, 1, !dbg !1892
  %44 = add i64 %38, 2, !dbg !1892
  %45 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %43, !dbg !1893
  %46 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %44, !dbg !1893
  %47 = load i32, ptr %45, align 4, !dbg !1893, !tbaa !295
  %48 = load i32, ptr %46, align 4, !dbg !1893, !tbaa !295
  %49 = and i32 %39, -2147483648, !dbg !1894
  %50 = and i32 %47, -2147483648, !dbg !1894
  %51 = and i32 %47, 2147483646, !dbg !1895
  %52 = and i32 %48, 2147483646, !dbg !1895
  %53 = or disjoint i32 %51, %49, !dbg !1896
  %54 = or disjoint i32 %52, %50, !dbg !1896
  %55 = add nuw nsw i64 %38, 397, !dbg !1897
  %56 = add i64 %38, 398, !dbg !1897
  %57 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %55, !dbg !1898
  %58 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %56, !dbg !1898
  %59 = load i32, ptr %57, align 4, !dbg !1898, !tbaa !295
  %60 = load i32, ptr %58, align 4, !dbg !1898, !tbaa !295
  %61 = lshr exact i32 %53, 1, !dbg !1899
  %62 = lshr exact i32 %54, 1, !dbg !1899
  %63 = and i32 %47, 1, !dbg !1900
  %64 = and i32 %48, 1, !dbg !1900
  %65 = zext nneg i32 %63 to i64, !dbg !1900
  %66 = zext nneg i32 %64 to i64, !dbg !1900
  %67 = getelementptr inbounds [2 x i32], ptr @prjm_eval_genrand_int32.mag01, i64 0, i64 %65, !dbg !1901
  %68 = getelementptr inbounds [2 x i32], ptr @prjm_eval_genrand_int32.mag01, i64 0, i64 %66, !dbg !1901
  %69 = load i32, ptr %67, align 4, !dbg !1901, !tbaa !295
  %70 = load i32, ptr %68, align 4, !dbg !1901, !tbaa !295
  %71 = xor i32 %69, %59, !dbg !1902
  %72 = xor i32 %70, %60, !dbg !1902
  %73 = xor i32 %71, %61, !dbg !1903
  %74 = xor i32 %72, %62, !dbg !1903
  store i32 %73, ptr %41, align 4, !dbg !1904, !tbaa !295
  store i32 %74, ptr %42, align 4, !dbg !1904, !tbaa !295
  %75 = add nuw i64 %38, 2, !dbg !1892
  %76 = icmp eq i64 %75, 226, !dbg !1892
  br i1 %76, label %77, label %37, !dbg !1892, !llvm.loop !1905

77:                                               ; preds = %37
  call void @llvm.dbg.value(metadata i64 226, metadata !247, metadata !DIExpression()), !dbg !1886
  %78 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 226, !dbg !1887
  %79 = and i32 %48, -2147483648, !dbg !1894
  %80 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 227, !dbg !1893
  %81 = load i32, ptr %80, align 4, !dbg !1893, !tbaa !295
  %82 = and i32 %81, 2147483646, !dbg !1895
  %83 = or disjoint i32 %82, %79, !dbg !1896
  call void @llvm.dbg.value(metadata !DIArgList(i32 %79, i32 %81), metadata !243, metadata !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 2147483647, DW_OP_and, DW_OP_or, DW_OP_stack_value)), !dbg !1909
  %84 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 623, !dbg !1898
  %85 = load i32, ptr %84, align 4, !dbg !1898, !tbaa !295
  %86 = lshr exact i32 %83, 1, !dbg !1899
  %87 = and i32 %81, 1, !dbg !1900
  %88 = zext nneg i32 %87 to i64, !dbg !1900
  %89 = getelementptr inbounds [2 x i32], ptr @prjm_eval_genrand_int32.mag01, i64 0, i64 %88, !dbg !1901
  %90 = load i32, ptr %89, align 4, !dbg !1901, !tbaa !295
  %91 = xor i32 %90, %85, !dbg !1902
  %92 = xor i32 %91, %86, !dbg !1903
  store i32 %92, ptr %78, align 4, !dbg !1904, !tbaa !295
  call void @llvm.dbg.value(metadata i64 227, metadata !247, metadata !DIExpression()), !dbg !1886
  call void @llvm.dbg.value(metadata i64 227, metadata !247, metadata !DIExpression(DW_OP_LLVM_convert, 64, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_stack_value)), !dbg !1886
  %93 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 227
  %94 = load i32, ptr %93, align 4, !dbg !1910, !tbaa !295
  br label %95, !dbg !1914

95:                                               ; preds = %95, %77
  %96 = phi i32 [ %94, %77 ], [ %102, %95 ], !dbg !1910
  %97 = phi i64 [ 227, %77 ], [ %100, %95 ]
  call void @llvm.dbg.value(metadata i64 %97, metadata !247, metadata !DIExpression()), !dbg !1886
  %98 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %97, !dbg !1910
  %99 = and i32 %96, -2147483648, !dbg !1915
  %100 = add nuw nsw i64 %97, 1, !dbg !1916
  %101 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %100, !dbg !1917
  %102 = load i32, ptr %101, align 4, !dbg !1917, !tbaa !295
  %103 = and i32 %102, 2147483646, !dbg !1918
  %104 = or disjoint i32 %103, %99, !dbg !1919
  call void @llvm.dbg.value(metadata !DIArgList(i32 %99, i32 %102), metadata !243, metadata !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 2147483647, DW_OP_and, DW_OP_or, DW_OP_stack_value)), !dbg !1909
  %105 = add nsw i64 %97, -227, !dbg !1920
  %106 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %105, !dbg !1921
  %107 = load i32, ptr %106, align 4, !dbg !1921, !tbaa !295
  %108 = lshr exact i32 %104, 1, !dbg !1922
  %109 = and i32 %102, 1, !dbg !1923
  %110 = zext nneg i32 %109 to i64, !dbg !1923
  %111 = getelementptr inbounds [2 x i32], ptr @prjm_eval_genrand_int32.mag01, i64 0, i64 %110, !dbg !1924
  %112 = load i32, ptr %111, align 4, !dbg !1924, !tbaa !295
  %113 = xor i32 %112, %107, !dbg !1925
  %114 = xor i32 %113, %108, !dbg !1926
  store i32 %114, ptr %98, align 4, !dbg !1927, !tbaa !295
  call void @llvm.dbg.value(metadata i64 %100, metadata !247, metadata !DIExpression()), !dbg !1886
  %115 = icmp eq i64 %100, 623, !dbg !1928
  br i1 %115, label %116, label %95, !dbg !1914, !llvm.loop !1929

116:                                              ; preds = %95
  %117 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 623, !dbg !1931
  %118 = load i32, ptr %117, align 4, !dbg !1931, !tbaa !295
  %119 = and i32 %118, -2147483648, !dbg !1932
  %120 = load i32, ptr %35, align 4, !dbg !1933, !tbaa !295
  %121 = and i32 %120, 2147483646, !dbg !1934
  %122 = or disjoint i32 %121, %119, !dbg !1935
  call void @llvm.dbg.value(metadata !DIArgList(i32 %119, i32 %120), metadata !243, metadata !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 2147483647, DW_OP_and, DW_OP_or, DW_OP_stack_value)), !dbg !1909
  %123 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 396, !dbg !1936
  %124 = load i32, ptr %123, align 4, !dbg !1936, !tbaa !295
  %125 = lshr exact i32 %122, 1, !dbg !1937
  %126 = and i32 %120, 1, !dbg !1938
  %127 = zext nneg i32 %126 to i64, !dbg !1938
  %128 = getelementptr inbounds [2 x i32], ptr @prjm_eval_genrand_int32.mag01, i64 0, i64 %127, !dbg !1939
  %129 = load i32, ptr %128, align 4, !dbg !1939, !tbaa !295
  %130 = xor i32 %129, %124, !dbg !1940
  %131 = xor i32 %130, %125, !dbg !1941
  store i32 %131, ptr %117, align 4, !dbg !1942, !tbaa !295
  br label %132, !dbg !1943

132:                                              ; preds = %31, %116
  %133 = phi ptr [ %35, %116 ], [ %33, %31 ], !dbg !1944
  %134 = phi i32 [ 0, %116 ], [ %12, %31 ], !dbg !1945
  %135 = call fast double @llvm.floor.f64(double %10), !dbg !1946
  tail call void @llvm.dbg.value(metadata double %135, metadata !1849, metadata !DIExpression()), !dbg !1851
  %136 = fcmp fast olt double %135, 1.000000e+00, !dbg !1947
  %137 = select i1 %136, double 1.000000e+00, double %135, !dbg !1949
  tail call void @llvm.dbg.value(metadata double %137, metadata !1849, metadata !DIExpression()), !dbg !1851
  %138 = add nsw i32 %134, 1, !dbg !1945
  store i32 %138, ptr %11, align 4, !dbg !1945, !tbaa !295
  %139 = sext i32 %134 to i64, !dbg !1944
  %140 = getelementptr inbounds [624 x i32], ptr %133, i64 0, i64 %139, !dbg !1944
  %141 = load i32, ptr %140, align 4, !dbg !1944, !tbaa !295
  call void @llvm.dbg.value(metadata i32 %141, metadata !243, metadata !DIExpression()), !dbg !1909
  %142 = lshr i32 %141, 11, !dbg !1950
  %143 = xor i32 %142, %141, !dbg !1951
  call void @llvm.dbg.value(metadata i32 %143, metadata !243, metadata !DIExpression()), !dbg !1909
  %144 = shl i32 %143, 7, !dbg !1952
  %145 = and i32 %144, -1658038656, !dbg !1953
  %146 = xor i32 %145, %143, !dbg !1954
  call void @llvm.dbg.value(metadata i32 %146, metadata !243, metadata !DIExpression()), !dbg !1909
  %147 = shl i32 %146, 15, !dbg !1955
  %148 = and i32 %147, -272236544, !dbg !1956
  %149 = xor i32 %148, %146, !dbg !1957
  call void @llvm.dbg.value(metadata i32 %149, metadata !243, metadata !DIExpression()), !dbg !1909
  %150 = lshr i32 %149, 18, !dbg !1958
  %151 = xor i32 %150, %149, !dbg !1959
  call void @llvm.dbg.value(metadata i32 %151, metadata !243, metadata !DIExpression()), !dbg !1909
  %152 = uitofp i32 %151 to double, !dbg !1960
  %153 = fmul fast double %137, 0x3DF0000000100000, !dbg !1960
  %154 = fmul fast double %153, %152, !dbg !1960
  %155 = load ptr, ptr %1, align 8, !dbg !1960, !tbaa !300
  store double %154, ptr %155, align 8, !dbg !1960, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1961
  ret void, !dbg !1961
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_invsqrt(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !20 {
  %3 = alloca ptr, align 8, !DIAssignID !1962
  call void @llvm.dbg.assign(metadata i1 undef, metadata !60, metadata !DIExpression(), metadata !1962, metadata ptr %3, metadata !DIExpression()), !dbg !1963
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !50, metadata !DIExpression()), !dbg !1963
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !51, metadata !DIExpression()), !dbg !1963
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1964
  store double 0.000000e+00, ptr %4, align 8, !dbg !1965, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1966
  store ptr %4, ptr %3, align 8, !dbg !1967, !tbaa !300, !DIAssignID !1968
  call void @llvm.dbg.assign(metadata ptr %4, metadata !60, metadata !DIExpression(), metadata !1968, metadata ptr %3, metadata !DIExpression()), !dbg !1963
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1969
  %6 = load ptr, ptr %5, align 8, !dbg !1969, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1969, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1969, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1969
  %9 = load ptr, ptr %3, align 8, !dbg !1970, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1971, !tbaa !312
  tail call void @llvm.dbg.value(metadata double poison, metadata !61, metadata !DIExpression()), !dbg !1963
  tail call void @llvm.dbg.value(metadata double %10, metadata !52, metadata !DIExpression()), !dbg !1963
  %11 = bitcast double %10 to i64, !dbg !1972
  %12 = lshr i64 %11, 1, !dbg !1973
  %13 = sub nsw i64 6910469410427058089, %12, !dbg !1974
  %14 = bitcast i64 %13 to double, !dbg !1975
  tail call void @llvm.dbg.value(metadata double %14, metadata !52, metadata !DIExpression()), !dbg !1963
  %15 = fmul fast double %10, 5.000000e-01, !dbg !1976
  %16 = fmul fast double %14, %14, !dbg !1976
  %17 = fmul fast double %16, %15, !dbg !1976
  %18 = fsub fast double 1.500000e+00, %17, !dbg !1977
  %19 = fmul fast double %18, %14, !dbg !1978
  tail call void @llvm.dbg.value(metadata double %19, metadata !52, metadata !DIExpression()), !dbg !1963
  %20 = load ptr, ptr %1, align 8, !dbg !1979, !tbaa !300
  store double %19, ptr %20, align 8, !dbg !1979, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1980
  ret void, !dbg !1980
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare nonnull ptr @llvm.threadlocal.address.p0(ptr nonnull) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare void @llvm.dbg.assign(metadata, metadata, metadata, metadata, metadata, metadata) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare void @llvm.dbg.value(metadata, metadata, metadata) #8

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.smin.i64(i64, i64) #8

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.maxnum.f64(double, double) #8

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.minnum.f64(double, double) #8

attributes #0 = { mustprogress nofree norecurse nosync nounwind sspstrong willreturn memory(argmem: write) uwtable "approx-func-fp-math"="true" "frame-pointer"="non-leaf" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+fix-cortex-a53-835769,+fp-armv8,+neon,+outline-atomics,+v8a,-fmv" "unsafe-fp-math"="true" }
attributes #1 = { mustprogress nofree norecurse nosync nounwind sspstrong willreturn memory(write, argmem: readwrite, inaccessiblemem: none) uwtable "approx-func-fp-math"="true" "frame-pointer"="non-leaf" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+fix-cortex-a53-835769,+fp-armv8,+neon,+outline-atomics,+v8a,-fmv" "unsafe-fp-math"="true" }
attributes #2 = { mustprogress nofree norecurse nosync nounwind sspstrong willreturn memory(argmem: readwrite) uwtable "approx-func-fp-math"="true" "frame-pointer"="non-leaf" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+fix-cortex-a53-835769,+fp-armv8,+neon,+outline-atomics,+v8a,-fmv" "unsafe-fp-math"="true" }
attributes #3 = { nounwind sspstrong uwtable "approx-func-fp-math"="true" "frame-pointer"="non-leaf" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+fix-cortex-a53-835769,+fp-armv8,+neon,+outline-atomics,+v8a,-fmv" "unsafe-fp-math"="true" }
attributes #4 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { "approx-func-fp-math"="true" "frame-pointer"="non-leaf" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+fix-cortex-a53-835769,+fp-armv8,+neon,+outline-atomics,+v8a,-fmv" "unsafe-fp-math"="true" }
attributes #7 = { mustprogress nofree nosync nounwind willreturn memory(none) "approx-func-fp-math"="true" "frame-pointer"="non-leaf" "no-infs-fp-math"="true" "no-nans-fp-math"="true" "no-signed-zeros-fp-math"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+fix-cortex-a53-835769,+fp-armv8,+neon,+outline-atomics,+v8a,-fmv" "unsafe-fp-math"="true" }
attributes #8 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #9 = { nounwind }
attributes #10 = { nounwind willreturn memory(none) }

!llvm.dbg.cu = !{!2}
!llvm.module.flags = !{!273, !274, !275, !276, !277, !278, !279}
!llvm.ident = !{!280}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "intrinsic_function_table", scope: !2, file: !6, line: 26, type: !260, isLocal: true, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C11, file: !3, producer: "Android (13691557, +pgo, -bolt, +lto, -mlgo, based on r522817d) clang version 18.0.4 (https://android.googlesource.com/toolchain/llvm-project d8003a456d14a3deb8054cdaa529ffbf02d9b262)", isOptimized: true, runtimeVersion: 0, emissionKind: FullDebug, retainedTypes: !4, globals: !17, splitDebugInlining: false, nameTableKind: None)
!3 = !DIFile(filename: "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit/i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c", directory: "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit/arithmetic-proposal/i04-only/bits-v2/arm64")
!4 = !{!5, !11, !14, !13}
!5 = !DIDerivedType(tag: DW_TAG_typedef, name: "PRJM_EVAL_I", file: !6, line: 18, baseType: !7)
!6 = !DIFile(filename: "i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c", directory: "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit")
!7 = !DIDerivedType(tag: DW_TAG_typedef, name: "int64_t", file: !8, line: 67, baseType: !9)
!8 = !DIFile(filename: "Library/Android/sdk/ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/sysroot/usr/include/stdint.h", directory: "/Users/jneerdael")
!9 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int64_t", file: !8, line: 43, baseType: !10)
!10 = !DIBasicType(name: "long", size: 64, encoding: DW_ATE_signed)
!11 = !DIDerivedType(tag: DW_TAG_typedef, name: "PRJM_EVAL_F", file: !12, line: 22, baseType: !13)
!12 = !DIFile(filename: "i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/api/projectm-eval.h", directory: "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit")
!13 = !DIBasicType(name: "double", size: 64, encoding: DW_ATE_float)
!14 = !DIDerivedType(tag: DW_TAG_typedef, name: "int32_t", file: !8, line: 64, baseType: !15)
!15 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int32_t", file: !8, line: 40, baseType: !16)
!16 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!17 = !{!18, !63, !65, !71, !76, !81, !86, !88, !93, !98, !103, !105, !107, !112, !114, !116, !118, !120, !122, !124, !126, !128, !130, !132, !134, !136, !138, !140, !142, !144, !146, !148, !150, !152, !154, !156, !158, !160, !162, !164, !166, !168, !170, !172, !174, !176, !178, !180, !182, !184, !186, !188, !190, !192, !194, !196, !198, !200, !202, !204, !206, !208, !210, !212, !214, !216, !218, !220, !222, !224, !226, !228, !230, !232, !0, !234, !253, !258}
!18 = !DIGlobalVariableExpression(var: !19, expr: !DIExpression())
!19 = distinct !DIGlobalVariable(name: "three_halfs", scope: !20, file: !6, line: 1243, type: !62, isLocal: true, isDefinition: true)
!20 = distinct !DISubprogram(name: "prjm_eval_func_invsqrt", scope: !6, file: !6, line: 1221, type: !21, scopeLine: 1222, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !49)
!21 = !DISubroutineType(types: !22)
!22 = !{null, !23, !38}
!23 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !24, size: 64)
!24 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "prjm_eval_exptreenode", file: !25, line: 72, size: 320, elements: !26)
!25 = !DIFile(filename: "i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/CompilerTypes.h", directory: "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit")
!26 = !{!27, !30, !31, !39, !41}
!27 = !DIDerivedType(tag: DW_TAG_member, name: "func", scope: !24, file: !25, line: 74, baseType: !28, size: 64)
!28 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !29, size: 64)
!29 = !DIDerivedType(tag: DW_TAG_typedef, name: "prjm_eval_expr_func_t", file: !25, line: 12, baseType: !21)
!30 = !DIDerivedType(tag: DW_TAG_member, name: "value", scope: !24, file: !25, line: 75, baseType: !11, size: 64, offset: 64)
!31 = !DIDerivedType(tag: DW_TAG_member, scope: !24, file: !25, line: 76, baseType: !32, size: 64, offset: 128)
!32 = distinct !DICompositeType(tag: DW_TAG_union_type, scope: !24, file: !25, line: 76, size: 64, elements: !33)
!33 = !{!34, !36}
!34 = !DIDerivedType(tag: DW_TAG_member, name: "var", scope: !32, file: !25, line: 78, baseType: !35, size: 64)
!35 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !11, size: 64)
!36 = !DIDerivedType(tag: DW_TAG_member, name: "memory_buffer", scope: !32, file: !25, line: 79, baseType: !37, size: 64)
!37 = !DIDerivedType(tag: DW_TAG_typedef, name: "projectm_eval_mem_buffer", file: !12, line: 43, baseType: !38)
!38 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !35, size: 64)
!39 = !DIDerivedType(tag: DW_TAG_member, name: "args", scope: !24, file: !25, line: 81, baseType: !40, size: 64, offset: 192)
!40 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !23, size: 64)
!41 = !DIDerivedType(tag: DW_TAG_member, name: "list", scope: !24, file: !25, line: 82, baseType: !42, size: 64, offset: 256)
!42 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !43, size: 64)
!43 = !DIDerivedType(tag: DW_TAG_typedef, name: "prjm_eval_exptreenode_list_item_t", file: !25, line: 66, baseType: !44)
!44 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "prjm_eval_exptreenode_list_item", file: !25, line: 62, size: 128, elements: !45)
!45 = !{!46, !47}
!46 = !DIDerivedType(tag: DW_TAG_member, name: "expr", scope: !44, file: !25, line: 64, baseType: !23, size: 64)
!47 = !DIDerivedType(tag: DW_TAG_member, name: "next", scope: !44, file: !25, line: 65, baseType: !48, size: 64, offset: 64)
!48 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !44, size: 64)
!49 = !{!50, !51, !52, !60, !61}
!50 = !DILocalVariable(name: "ctx", arg: 1, scope: !20, file: !6, line: 1221, type: !23)
!51 = !DILocalVariable(name: "ret_val", arg: 2, scope: !20, file: !6, line: 1221, type: !38)
!52 = !DILocalVariable(name: "type_conv", scope: !20, file: !6, line: 1241, type: !53)
!53 = distinct !DICompositeType(tag: DW_TAG_union_type, scope: !20, file: !6, line: 1237, size: 64, elements: !54)
!54 = !{!55, !56}
!55 = !DIDerivedType(tag: DW_TAG_member, name: "PRJM_F_val", scope: !53, file: !6, line: 1239, baseType: !11, size: 64)
!56 = !DIDerivedType(tag: DW_TAG_member, name: "int_val", scope: !53, file: !6, line: 1240, baseType: !57, size: 64)
!57 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint64_t", file: !8, line: 68, baseType: !58)
!58 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint64_t", file: !8, line: 44, baseType: !59)
!59 = !DIBasicType(name: "unsigned long", size: 64, encoding: DW_ATE_unsigned)
!60 = !DILocalVariable(name: "value_ptr", scope: !20, file: !6, line: 1248, type: !35)
!61 = !DILocalVariable(name: "num2", scope: !20, file: !6, line: 1252, type: !11)
!62 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !11)
!63 = !DIGlobalVariableExpression(var: !64, expr: !DIExpression())
!64 = distinct !DIGlobalVariable(name: "one_half", scope: !20, file: !6, line: 1244, type: !62, isLocal: true, isDefinition: true)
!65 = !DIGlobalVariableExpression(var: !66, expr: !DIExpression())
!66 = distinct !DIGlobalVariable(scope: null, file: !6, line: 28, type: !67, isLocal: true, isDefinition: true)
!67 = !DICompositeType(tag: DW_TAG_array_type, baseType: !68, size: 80, elements: !69)
!68 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_unsigned_char)
!69 = !{!70}
!70 = !DISubrange(count: 10)
!71 = !DIGlobalVariableExpression(var: !72, expr: !DIExpression())
!72 = distinct !DIGlobalVariable(scope: null, file: !6, line: 29, type: !73, isLocal: true, isDefinition: true)
!73 = !DICompositeType(tag: DW_TAG_array_type, baseType: !68, size: 64, elements: !74)
!74 = !{!75}
!75 = !DISubrange(count: 8)
!76 = !DIGlobalVariableExpression(var: !77, expr: !DIExpression())
!77 = distinct !DIGlobalVariable(scope: null, file: !6, line: 30, type: !78, isLocal: true, isDefinition: true)
!78 = !DICompositeType(tag: DW_TAG_array_type, baseType: !68, size: 72, elements: !79)
!79 = !{!80}
!80 = !DISubrange(count: 9)
!81 = !DIGlobalVariableExpression(var: !82, expr: !DIExpression())
!82 = distinct !DIGlobalVariable(scope: null, file: !6, line: 31, type: !83, isLocal: true, isDefinition: true)
!83 = !DICompositeType(tag: DW_TAG_array_type, baseType: !68, size: 56, elements: !84)
!84 = !{!85}
!85 = !DISubrange(count: 7)
!86 = !DIGlobalVariableExpression(var: !87, expr: !DIExpression())
!87 = distinct !DIGlobalVariable(scope: null, file: !6, line: 32, type: !73, isLocal: true, isDefinition: true)
!88 = !DIGlobalVariableExpression(var: !89, expr: !DIExpression())
!89 = distinct !DIGlobalVariable(scope: null, file: !6, line: 34, type: !90, isLocal: true, isDefinition: true)
!90 = !DICompositeType(tag: DW_TAG_array_type, baseType: !68, size: 24, elements: !91)
!91 = !{!92}
!92 = !DISubrange(count: 3)
!93 = !DIGlobalVariableExpression(var: !94, expr: !DIExpression())
!94 = distinct !DIGlobalVariable(scope: null, file: !6, line: 35, type: !95, isLocal: true, isDefinition: true)
!95 = !DICompositeType(tag: DW_TAG_array_type, baseType: !68, size: 32, elements: !96)
!96 = !{!97}
!97 = !DISubrange(count: 4)
!98 = !DIGlobalVariableExpression(var: !99, expr: !DIExpression())
!99 = distinct !DIGlobalVariable(scope: null, file: !6, line: 36, type: !100, isLocal: true, isDefinition: true)
!100 = !DICompositeType(tag: DW_TAG_array_type, baseType: !68, size: 40, elements: !101)
!101 = !{!102}
!102 = !DISubrange(count: 5)
!103 = !DIGlobalVariableExpression(var: !104, expr: !DIExpression())
!104 = distinct !DIGlobalVariable(scope: null, file: !6, line: 37, type: !95, isLocal: true, isDefinition: true)
!105 = !DIGlobalVariableExpression(var: !106, expr: !DIExpression())
!106 = distinct !DIGlobalVariable(scope: null, file: !6, line: 38, type: !100, isLocal: true, isDefinition: true)
!107 = !DIGlobalVariableExpression(var: !108, expr: !DIExpression())
!108 = distinct !DIGlobalVariable(scope: null, file: !6, line: 39, type: !109, isLocal: true, isDefinition: true)
!109 = !DICompositeType(tag: DW_TAG_array_type, baseType: !68, size: 48, elements: !110)
!110 = !{!111}
!111 = !DISubrange(count: 6)
!112 = !DIGlobalVariableExpression(var: !113, expr: !DIExpression())
!113 = distinct !DIGlobalVariable(scope: null, file: !6, line: 41, type: !100, isLocal: true, isDefinition: true)
!114 = !DIGlobalVariableExpression(var: !115, expr: !DIExpression())
!115 = distinct !DIGlobalVariable(scope: null, file: !6, line: 42, type: !100, isLocal: true, isDefinition: true)
!116 = !DIGlobalVariableExpression(var: !117, expr: !DIExpression())
!117 = distinct !DIGlobalVariable(scope: null, file: !6, line: 43, type: !83, isLocal: true, isDefinition: true)
!118 = !DIGlobalVariableExpression(var: !119, expr: !DIExpression())
!119 = distinct !DIGlobalVariable(scope: null, file: !6, line: 44, type: !109, isLocal: true, isDefinition: true)
!120 = !DIGlobalVariableExpression(var: !121, expr: !DIExpression())
!121 = distinct !DIGlobalVariable(scope: null, file: !6, line: 45, type: !83, isLocal: true, isDefinition: true)
!122 = !DIGlobalVariableExpression(var: !123, expr: !DIExpression())
!123 = distinct !DIGlobalVariable(scope: null, file: !6, line: 46, type: !83, isLocal: true, isDefinition: true)
!124 = !DIGlobalVariableExpression(var: !125, expr: !DIExpression())
!125 = distinct !DIGlobalVariable(scope: null, file: !6, line: 47, type: !109, isLocal: true, isDefinition: true)
!126 = !DIGlobalVariableExpression(var: !127, expr: !DIExpression())
!127 = distinct !DIGlobalVariable(scope: null, file: !6, line: 48, type: !83, isLocal: true, isDefinition: true)
!128 = !DIGlobalVariableExpression(var: !129, expr: !DIExpression())
!129 = distinct !DIGlobalVariable(scope: null, file: !6, line: 49, type: !109, isLocal: true, isDefinition: true)
!130 = !DIGlobalVariableExpression(var: !131, expr: !DIExpression())
!131 = distinct !DIGlobalVariable(scope: null, file: !6, line: 50, type: !83, isLocal: true, isDefinition: true)
!132 = !DIGlobalVariableExpression(var: !133, expr: !DIExpression())
!133 = distinct !DIGlobalVariable(scope: null, file: !6, line: 51, type: !83, isLocal: true, isDefinition: true)
!134 = !DIGlobalVariableExpression(var: !135, expr: !DIExpression())
!135 = distinct !DIGlobalVariable(scope: null, file: !6, line: 53, type: !100, isLocal: true, isDefinition: true)
!136 = !DIGlobalVariableExpression(var: !137, expr: !DIExpression())
!137 = distinct !DIGlobalVariable(scope: null, file: !6, line: 54, type: !83, isLocal: true, isDefinition: true)
!138 = !DIGlobalVariableExpression(var: !139, expr: !DIExpression())
!139 = distinct !DIGlobalVariable(scope: null, file: !6, line: 55, type: !100, isLocal: true, isDefinition: true)
!140 = !DIGlobalVariableExpression(var: !141, expr: !DIExpression())
!141 = distinct !DIGlobalVariable(scope: null, file: !6, line: 56, type: !100, isLocal: true, isDefinition: true)
!142 = !DIGlobalVariableExpression(var: !143, expr: !DIExpression())
!143 = distinct !DIGlobalVariable(scope: null, file: !6, line: 57, type: !100, isLocal: true, isDefinition: true)
!144 = !DIGlobalVariableExpression(var: !145, expr: !DIExpression())
!145 = distinct !DIGlobalVariable(scope: null, file: !6, line: 58, type: !100, isLocal: true, isDefinition: true)
!146 = !DIGlobalVariableExpression(var: !147, expr: !DIExpression())
!147 = distinct !DIGlobalVariable(scope: null, file: !6, line: 59, type: !100, isLocal: true, isDefinition: true)
!148 = !DIGlobalVariableExpression(var: !149, expr: !DIExpression())
!149 = distinct !DIGlobalVariable(scope: null, file: !6, line: 60, type: !83, isLocal: true, isDefinition: true)
!150 = !DIGlobalVariableExpression(var: !151, expr: !DIExpression())
!151 = distinct !DIGlobalVariable(scope: null, file: !6, line: 61, type: !83, isLocal: true, isDefinition: true)
!152 = !DIGlobalVariableExpression(var: !153, expr: !DIExpression())
!153 = distinct !DIGlobalVariable(scope: null, file: !6, line: 62, type: !109, isLocal: true, isDefinition: true)
!154 = !DIGlobalVariableExpression(var: !155, expr: !DIExpression())
!155 = distinct !DIGlobalVariable(scope: null, file: !6, line: 63, type: !83, isLocal: true, isDefinition: true)
!156 = !DIGlobalVariableExpression(var: !157, expr: !DIExpression())
!157 = distinct !DIGlobalVariable(scope: null, file: !6, line: 64, type: !83, isLocal: true, isDefinition: true)
!158 = !DIGlobalVariableExpression(var: !159, expr: !DIExpression())
!159 = distinct !DIGlobalVariable(scope: null, file: !6, line: 65, type: !83, isLocal: true, isDefinition: true)
!160 = !DIGlobalVariableExpression(var: !161, expr: !DIExpression())
!161 = distinct !DIGlobalVariable(scope: null, file: !6, line: 66, type: !83, isLocal: true, isDefinition: true)
!162 = !DIGlobalVariableExpression(var: !163, expr: !DIExpression())
!163 = distinct !DIGlobalVariable(scope: null, file: !6, line: 68, type: !95, isLocal: true, isDefinition: true)
!164 = !DIGlobalVariableExpression(var: !165, expr: !DIExpression())
!165 = distinct !DIGlobalVariable(scope: null, file: !6, line: 69, type: !95, isLocal: true, isDefinition: true)
!166 = !DIGlobalVariableExpression(var: !167, expr: !DIExpression())
!167 = distinct !DIGlobalVariable(scope: null, file: !6, line: 70, type: !95, isLocal: true, isDefinition: true)
!168 = !DIGlobalVariableExpression(var: !169, expr: !DIExpression())
!169 = distinct !DIGlobalVariable(scope: null, file: !6, line: 71, type: !100, isLocal: true, isDefinition: true)
!170 = !DIGlobalVariableExpression(var: !171, expr: !DIExpression())
!171 = distinct !DIGlobalVariable(scope: null, file: !6, line: 72, type: !100, isLocal: true, isDefinition: true)
!172 = !DIGlobalVariableExpression(var: !173, expr: !DIExpression())
!173 = distinct !DIGlobalVariable(scope: null, file: !6, line: 73, type: !100, isLocal: true, isDefinition: true)
!174 = !DIGlobalVariableExpression(var: !175, expr: !DIExpression())
!175 = distinct !DIGlobalVariable(scope: null, file: !6, line: 74, type: !109, isLocal: true, isDefinition: true)
!176 = !DIGlobalVariableExpression(var: !177, expr: !DIExpression())
!177 = distinct !DIGlobalVariable(scope: null, file: !6, line: 75, type: !95, isLocal: true, isDefinition: true)
!178 = !DIGlobalVariableExpression(var: !179, expr: !DIExpression())
!179 = distinct !DIGlobalVariable(scope: null, file: !6, line: 76, type: !100, isLocal: true, isDefinition: true)
!180 = !DIGlobalVariableExpression(var: !181, expr: !DIExpression())
!181 = distinct !DIGlobalVariable(scope: null, file: !6, line: 77, type: !95, isLocal: true, isDefinition: true)
!182 = !DIGlobalVariableExpression(var: !183, expr: !DIExpression())
!183 = distinct !DIGlobalVariable(scope: null, file: !6, line: 78, type: !83, isLocal: true, isDefinition: true)
!184 = !DIGlobalVariableExpression(var: !185, expr: !DIExpression())
!185 = distinct !DIGlobalVariable(scope: null, file: !6, line: 79, type: !95, isLocal: true, isDefinition: true)
!186 = !DIGlobalVariableExpression(var: !187, expr: !DIExpression())
!187 = distinct !DIGlobalVariable(scope: null, file: !6, line: 80, type: !100, isLocal: true, isDefinition: true)
!188 = !DIGlobalVariableExpression(var: !189, expr: !DIExpression())
!189 = distinct !DIGlobalVariable(scope: null, file: !6, line: 82, type: !95, isLocal: true, isDefinition: true)
!190 = !DIGlobalVariableExpression(var: !191, expr: !DIExpression())
!191 = distinct !DIGlobalVariable(scope: null, file: !6, line: 83, type: !109, isLocal: true, isDefinition: true)
!192 = !DIGlobalVariableExpression(var: !193, expr: !DIExpression())
!193 = distinct !DIGlobalVariable(scope: null, file: !6, line: 84, type: !95, isLocal: true, isDefinition: true)
!194 = !DIGlobalVariableExpression(var: !195, expr: !DIExpression())
!195 = distinct !DIGlobalVariable(scope: null, file: !6, line: 85, type: !95, isLocal: true, isDefinition: true)
!196 = !DIGlobalVariableExpression(var: !197, expr: !DIExpression())
!197 = distinct !DIGlobalVariable(scope: null, file: !6, line: 86, type: !95, isLocal: true, isDefinition: true)
!198 = !DIGlobalVariableExpression(var: !199, expr: !DIExpression())
!199 = distinct !DIGlobalVariable(scope: null, file: !6, line: 87, type: !100, isLocal: true, isDefinition: true)
!200 = !DIGlobalVariableExpression(var: !201, expr: !DIExpression())
!201 = distinct !DIGlobalVariable(scope: null, file: !6, line: 88, type: !100, isLocal: true, isDefinition: true)
!202 = !DIGlobalVariableExpression(var: !203, expr: !DIExpression())
!203 = distinct !DIGlobalVariable(scope: null, file: !6, line: 89, type: !109, isLocal: true, isDefinition: true)
!204 = !DIGlobalVariableExpression(var: !205, expr: !DIExpression())
!205 = distinct !DIGlobalVariable(scope: null, file: !6, line: 90, type: !95, isLocal: true, isDefinition: true)
!206 = !DIGlobalVariableExpression(var: !207, expr: !DIExpression())
!207 = distinct !DIGlobalVariable(scope: null, file: !6, line: 91, type: !100, isLocal: true, isDefinition: true)
!208 = !DIGlobalVariableExpression(var: !209, expr: !DIExpression())
!209 = distinct !DIGlobalVariable(scope: null, file: !6, line: 92, type: !73, isLocal: true, isDefinition: true)
!210 = !DIGlobalVariableExpression(var: !211, expr: !DIExpression())
!211 = distinct !DIGlobalVariable(scope: null, file: !6, line: 93, type: !73, isLocal: true, isDefinition: true)
!212 = !DIGlobalVariableExpression(var: !213, expr: !DIExpression())
!213 = distinct !DIGlobalVariable(scope: null, file: !6, line: 95, type: !100, isLocal: true, isDefinition: true)
!214 = !DIGlobalVariableExpression(var: !215, expr: !DIExpression())
!215 = distinct !DIGlobalVariable(scope: null, file: !6, line: 96, type: !95, isLocal: true, isDefinition: true)
!216 = !DIGlobalVariableExpression(var: !217, expr: !DIExpression())
!217 = distinct !DIGlobalVariable(scope: null, file: !6, line: 98, type: !109, isLocal: true, isDefinition: true)
!218 = !DIGlobalVariableExpression(var: !219, expr: !DIExpression())
!219 = distinct !DIGlobalVariable(scope: null, file: !6, line: 99, type: !109, isLocal: true, isDefinition: true)
!220 = !DIGlobalVariableExpression(var: !221, expr: !DIExpression())
!221 = distinct !DIGlobalVariable(scope: null, file: !6, line: 100, type: !100, isLocal: true, isDefinition: true)
!222 = !DIGlobalVariableExpression(var: !223, expr: !DIExpression())
!223 = distinct !DIGlobalVariable(scope: null, file: !6, line: 101, type: !73, isLocal: true, isDefinition: true)
!224 = !DIGlobalVariableExpression(var: !225, expr: !DIExpression())
!225 = distinct !DIGlobalVariable(scope: null, file: !6, line: 102, type: !109, isLocal: true, isDefinition: true)
!226 = !DIGlobalVariableExpression(var: !227, expr: !DIExpression())
!227 = distinct !DIGlobalVariable(scope: null, file: !6, line: 103, type: !78, isLocal: true, isDefinition: true)
!228 = !DIGlobalVariableExpression(var: !229, expr: !DIExpression())
!229 = distinct !DIGlobalVariable(scope: null, file: !6, line: 104, type: !78, isLocal: true, isDefinition: true)
!230 = !DIGlobalVariableExpression(var: !231, expr: !DIExpression())
!231 = distinct !DIGlobalVariable(scope: null, file: !6, line: 105, type: !83, isLocal: true, isDefinition: true)
!232 = !DIGlobalVariableExpression(var: !233, expr: !DIExpression())
!233 = distinct !DIGlobalVariable(scope: null, file: !6, line: 106, type: !83, isLocal: true, isDefinition: true)
!234 = !DIGlobalVariableExpression(var: !235, expr: !DIExpression())
!235 = distinct !DIGlobalVariable(name: "mag01", scope: !236, file: !6, line: 161, type: !250, isLocal: true, isDefinition: true)
!236 = distinct !DISubprogram(name: "prjm_eval_genrand_int32", scope: !6, file: !6, line: 158, type: !237, scopeLine: 159, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !242)
!237 = !DISubroutineType(types: !238)
!238 = !{!239}
!239 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint32_t", file: !8, line: 65, baseType: !240)
!240 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint32_t", file: !8, line: 41, baseType: !241)
!241 = !DIBasicType(name: "unsigned int", size: 32, encoding: DW_ATE_unsigned)
!242 = !{!243, !244, !247}
!243 = !DILocalVariable(name: "y", scope: !236, file: !6, line: 160, type: !239)
!244 = !DILocalVariable(name: "s", scope: !245, file: !6, line: 171, type: !239)
!245 = distinct !DILexicalBlock(scope: !246, file: !6, line: 170, column: 5)
!246 = distinct !DILexicalBlock(scope: !236, file: !6, line: 169, column: 9)
!247 = !DILocalVariable(name: "kk", scope: !248, file: !6, line: 189, type: !14)
!248 = distinct !DILexicalBlock(scope: !249, file: !6, line: 188, column: 5)
!249 = distinct !DILexicalBlock(scope: !236, file: !6, line: 187, column: 9)
!250 = !DICompositeType(tag: DW_TAG_array_type, baseType: !239, size: 64, elements: !251)
!251 = !{!252}
!252 = !DISubrange(count: 2)
!253 = !DIGlobalVariableExpression(var: !254, expr: !DIExpression())
!254 = distinct !DIGlobalVariable(name: "mt", scope: !236, file: !6, line: 165, type: !255, isLocal: true, isDefinition: true)
!255 = !DICompositeType(tag: DW_TAG_array_type, baseType: !239, size: 19968, elements: !256)
!256 = !{!257}
!257 = !DISubrange(count: 624)
!258 = !DIGlobalVariableExpression(var: !259, expr: !DIExpression())
!259 = distinct !DIGlobalVariable(name: "mti", scope: !236, file: !6, line: 166, type: !14, isLocal: true, isDefinition: true)
!260 = !DICompositeType(tag: DW_TAG_array_type, baseType: !261, size: 13824, elements: !271)
!261 = !DIDerivedType(tag: DW_TAG_typedef, name: "prjm_eval_function_def_t", file: !25, line: 26, baseType: !262)
!262 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "prjm_eval_function_def", file: !25, line: 19, size: 192, elements: !263)
!263 = !{!264, !266, !267, !268, !270}
!264 = !DIDerivedType(tag: DW_TAG_member, name: "name", scope: !262, file: !25, line: 21, baseType: !265, size: 64)
!265 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !68, size: 64)
!266 = !DIDerivedType(tag: DW_TAG_member, name: "func", scope: !262, file: !25, line: 22, baseType: !28, size: 64, offset: 64)
!267 = !DIDerivedType(tag: DW_TAG_member, name: "arg_count", scope: !262, file: !25, line: 23, baseType: !16, size: 32, offset: 128)
!268 = !DIDerivedType(tag: DW_TAG_member, name: "is_const_eval", scope: !262, file: !25, line: 24, baseType: !269, size: 8, offset: 160)
!269 = !DIBasicType(name: "_Bool", size: 8, encoding: DW_ATE_boolean)
!270 = !DIDerivedType(tag: DW_TAG_member, name: "is_state_changing", scope: !262, file: !25, line: 25, baseType: !269, size: 8, offset: 168)
!271 = !{!272}
!272 = !DISubrange(count: 72)
!273 = !{i32 7, !"Dwarf Version", i32 4}
!274 = !{i32 2, !"Debug Info Version", i32 3}
!275 = !{i32 1, !"wchar_size", i32 4}
!276 = !{i32 8, !"PIC Level", i32 2}
!277 = !{i32 7, !"uwtable", i32 2}
!278 = !{i32 7, !"frame-pointer", i32 1}
!279 = !{i32 7, !"debug-info-assignment-tracking", i1 true}
!280 = !{!"Android (13691557, +pgo, -bolt, +lto, -mlgo, based on r522817d) clang version 18.0.4 (https://android.googlesource.com/toolchain/llvm-project d8003a456d14a3deb8054cdaa529ffbf02d9b262)"}
!281 = distinct !DISubprogram(name: "prjm_eval_intrinsic_functions", scope: !6, file: !6, line: 151, type: !282, scopeLine: 152, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !290)
!282 = !DISubroutineType(types: !283)
!283 = !{null, !284, !289}
!284 = !DIDerivedType(tag: DW_TAG_typedef, name: "prjm_eval_intrinsic_function_list_ptr", file: !25, line: 40, baseType: !285)
!285 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !286, size: 64)
!286 = !DIDerivedType(tag: DW_TAG_typedef, name: "prjm_eval_intrinsic_function_list", file: !25, line: 39, baseType: !287)
!287 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !288, size: 64)
!288 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !261)
!289 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !239, size: 64)
!290 = !{!291, !292}
!291 = !DILocalVariable(name: "list", arg: 1, scope: !281, file: !6, line: 151, type: !284)
!292 = !DILocalVariable(name: "count", arg: 2, scope: !281, file: !6, line: 151, type: !289)
!293 = !DILocation(line: 0, scope: !281)
!294 = !DILocation(line: 153, column: 12, scope: !281)
!295 = !{!296, !296, i64 0}
!296 = !{!"int", !297, i64 0}
!297 = !{!"omnipotent char", !298, i64 0}
!298 = !{!"Simple C/C++ TBAA"}
!299 = !DILocation(line: 154, column: 11, scope: !281)
!300 = !{!301, !301, i64 0}
!301 = !{!"any pointer", !297, i64 0}
!302 = !DILocation(line: 155, column: 1, scope: !281)
!303 = distinct !DISubprogram(name: "prjm_eval_func_const", scope: !6, file: !6, line: 219, type: !21, scopeLine: 220, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !304)
!304 = !{!305, !306}
!305 = !DILocalVariable(name: "ctx", arg: 1, scope: !303, file: !6, line: 219, type: !23)
!306 = !DILocalVariable(name: "ret_val", arg: 2, scope: !303, file: !6, line: 219, type: !38)
!307 = !DILocation(line: 0, scope: !303)
!308 = !DILocation(line: 223, column: 5, scope: !303)
!309 = !{!310, !311, i64 8}
!310 = !{!"prjm_eval_exptreenode", !301, i64 0, !311, i64 8, !297, i64 16, !301, i64 24, !301, i64 32}
!311 = !{!"double", !297, i64 0}
!312 = !{!311, !311, i64 0}
!313 = !DILocation(line: 224, column: 1, scope: !303)
!314 = distinct !DISubprogram(name: "prjm_eval_func_var", scope: !6, file: !6, line: 226, type: !21, scopeLine: 227, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !315)
!315 = !{!316, !317}
!316 = !DILocalVariable(name: "ctx", arg: 1, scope: !314, file: !6, line: 226, type: !23)
!317 = !DILocalVariable(name: "ret_val", arg: 2, scope: !314, file: !6, line: 226, type: !38)
!318 = !DILocation(line: 0, scope: !314)
!319 = !DILocation(line: 231, column: 5, scope: !314)
!320 = !{!297, !297, i64 0}
!321 = !DILocation(line: 232, column: 1, scope: !314)
!322 = distinct !DISubprogram(name: "prjm_eval_func_execute_list", scope: !6, file: !6, line: 236, type: !21, scopeLine: 237, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !323)
!323 = !{!324, !325, !326, !327}
!324 = !DILocalVariable(name: "ctx", arg: 1, scope: !322, file: !6, line: 236, type: !23)
!325 = !DILocalVariable(name: "ret_val", arg: 2, scope: !322, file: !6, line: 236, type: !38)
!326 = !DILocalVariable(name: "value_ptr", scope: !322, file: !6, line: 242, type: !35)
!327 = !DILocalVariable(name: "item", scope: !322, file: !6, line: 243, type: !42)
!328 = distinct !DIAssignID()
!329 = !DILocation(line: 0, scope: !322)
!330 = !DILocation(line: 241, column: 10, scope: !322)
!331 = !DILocation(line: 241, column: 16, scope: !322)
!332 = !DILocation(line: 242, column: 5, scope: !322)
!333 = distinct !DIAssignID()
!334 = !DILocation(line: 243, column: 52, scope: !322)
!335 = !DILocation(line: 244, column: 5, scope: !322)
!336 = !DILocation(line: 249, column: 20, scope: !337)
!337 = distinct !DILexicalBlock(scope: !322, file: !6, line: 245, column: 5)
!338 = !DILocation(line: 250, column: 19, scope: !337)
!339 = distinct !DIAssignID()
!340 = !DILocation(line: 251, column: 15, scope: !337)
!341 = !{!342, !301, i64 0}
!342 = !{!"prjm_eval_exptreenode_list_item", !301, i64 0, !301, i64 8}
!343 = !DILocation(line: 251, column: 21, scope: !337)
!344 = !{!310, !301, i64 0}
!345 = !DILocation(line: 251, column: 9, scope: !337)
!346 = !DILocation(line: 252, column: 22, scope: !337)
!347 = distinct !{!347, !335, !348, !349}
!348 = !DILocation(line: 253, column: 5, scope: !322)
!349 = !{!"llvm.loop.mustprogress"}
!350 = !DILocation(line: 255, column: 5, scope: !322)
!351 = !DILocation(line: 256, column: 1, scope: !322)
!352 = distinct !DISubprogram(name: "prjm_eval_func_execute_loop", scope: !6, file: !6, line: 258, type: !21, scopeLine: 259, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !353)
!353 = !{!354, !355, !356, !357, !358}
!354 = !DILocalVariable(name: "ctx", arg: 1, scope: !352, file: !6, line: 258, type: !23)
!355 = !DILocalVariable(name: "ret_val", arg: 2, scope: !352, file: !6, line: 258, type: !38)
!356 = !DILocalVariable(name: "value_ptr", scope: !352, file: !6, line: 263, type: !35)
!357 = !DILocalVariable(name: "loop_count_int", scope: !352, file: !6, line: 266, type: !5)
!358 = !DILocalVariable(name: "i", scope: !359, file: !6, line: 273, type: !5)
!359 = distinct !DILexicalBlock(scope: !352, file: !6, line: 273, column: 5)
!360 = distinct !DIAssignID()
!361 = !DILocation(line: 0, scope: !352)
!362 = !DILocation(line: 262, column: 10, scope: !352)
!363 = !DILocation(line: 262, column: 16, scope: !352)
!364 = !DILocation(line: 263, column: 5, scope: !352)
!365 = !DILocation(line: 263, column: 18, scope: !352)
!366 = distinct !DIAssignID()
!367 = !DILocation(line: 264, column: 5, scope: !352)
!368 = !{!310, !301, i64 24}
!369 = !DILocation(line: 266, column: 50, scope: !352)
!370 = !DILocation(line: 266, column: 49, scope: !352)
!371 = !DILocation(line: 266, column: 34, scope: !352)
!372 = !DILocation(line: 268, column: 9, scope: !352)
!373 = !DILocation(line: 0, scope: !359)
!374 = !DILocation(line: 273, column: 31, scope: !375)
!375 = distinct !DILexicalBlock(scope: !359, file: !6, line: 273, column: 5)
!376 = !DILocation(line: 273, column: 5, scope: !359)
!377 = !DILocation(line: 280, column: 5, scope: !352)
!378 = !DILocation(line: 281, column: 1, scope: !352)
!379 = !DILocation(line: 275, column: 20, scope: !380)
!380 = distinct !DILexicalBlock(scope: !375, file: !6, line: 274, column: 5)
!381 = !DILocation(line: 276, column: 19, scope: !380)
!382 = distinct !DIAssignID()
!383 = !DILocation(line: 277, column: 9, scope: !380)
!384 = !DILocation(line: 273, column: 50, scope: !375)
!385 = distinct !{!385, !376, !386, !349}
!386 = !DILocation(line: 278, column: 5, scope: !359)
!387 = distinct !DISubprogram(name: "prjm_eval_func_execute_while", scope: !6, file: !6, line: 283, type: !21, scopeLine: 284, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !388)
!388 = !{!389, !390, !391, !392}
!389 = !DILocalVariable(name: "ctx", arg: 1, scope: !387, file: !6, line: 283, type: !23)
!390 = !DILocalVariable(name: "ret_val", arg: 2, scope: !387, file: !6, line: 283, type: !38)
!391 = !DILocalVariable(name: "value_ptr", scope: !387, file: !6, line: 288, type: !35)
!392 = !DILocalVariable(name: "loop_count_int", scope: !387, file: !6, line: 289, type: !5)
!393 = distinct !DIAssignID()
!394 = !DILocation(line: 0, scope: !387)
!395 = !DILocation(line: 287, column: 10, scope: !387)
!396 = !DILocation(line: 287, column: 16, scope: !387)
!397 = !DILocation(line: 288, column: 5, scope: !387)
!398 = !DILocation(line: 288, column: 18, scope: !387)
!399 = distinct !DIAssignID()
!400 = !DILocation(line: 290, column: 5, scope: !387)
!401 = !DILocation(line: 292, column: 9, scope: !402)
!402 = distinct !DILexicalBlock(scope: !387, file: !6, line: 291, column: 5)
!403 = !DILocation(line: 293, column: 20, scope: !387)
!404 = !DILocation(line: 293, column: 19, scope: !387)
!405 = !DILocation(line: 293, column: 14, scope: !387)
!406 = !DILocation(line: 293, column: 31, scope: !387)
!407 = !DILocation(line: 293, column: 53, scope: !387)
!408 = distinct !{!408, !400, !409, !349}
!409 = !DILocation(line: 293, column: 72, scope: !387)
!410 = !DILocation(line: 295, column: 5, scope: !387)
!411 = !DILocation(line: 296, column: 1, scope: !387)
!412 = distinct !DISubprogram(name: "prjm_eval_func_if", scope: !6, file: !6, line: 298, type: !21, scopeLine: 299, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !413)
!413 = !{!414, !415, !416}
!414 = !DILocalVariable(name: "ctx", arg: 1, scope: !412, file: !6, line: 298, type: !23)
!415 = !DILocalVariable(name: "ret_val", arg: 2, scope: !412, file: !6, line: 298, type: !38)
!416 = !DILocalVariable(name: "if_arg", scope: !412, file: !6, line: 302, type: !35)
!417 = distinct !DIAssignID()
!418 = !DILocation(line: 0, scope: !412)
!419 = !DILocation(line: 302, column: 5, scope: !412)
!420 = !DILocation(line: 302, column: 33, scope: !412)
!421 = !DILocation(line: 302, column: 18, scope: !412)
!422 = distinct !DIAssignID()
!423 = !DILocation(line: 304, column: 5, scope: !412)
!424 = !DILocation(line: 306, column: 11, scope: !425)
!425 = distinct !DILexicalBlock(scope: !412, file: !6, line: 306, column: 9)
!426 = !DILocation(line: 306, column: 10, scope: !425)
!427 = !DILocation(line: 306, column: 19, scope: !425)
!428 = !DILocation(line: 312, column: 1, scope: !412)
!429 = distinct !DISubprogram(name: "prjm_eval_func_exec2", scope: !6, file: !6, line: 314, type: !21, scopeLine: 315, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !430)
!430 = !{!431, !432, !433}
!431 = !DILocalVariable(name: "ctx", arg: 1, scope: !429, file: !6, line: 314, type: !23)
!432 = !DILocalVariable(name: "ret_val", arg: 2, scope: !429, file: !6, line: 314, type: !38)
!433 = !DILocalVariable(name: "value_ptr", scope: !429, file: !6, line: 319, type: !35)
!434 = distinct !DIAssignID()
!435 = !DILocation(line: 0, scope: !429)
!436 = !DILocation(line: 318, column: 10, scope: !429)
!437 = !DILocation(line: 318, column: 16, scope: !429)
!438 = !DILocation(line: 319, column: 5, scope: !429)
!439 = !DILocation(line: 319, column: 18, scope: !429)
!440 = distinct !DIAssignID()
!441 = !DILocation(line: 321, column: 5, scope: !429)
!442 = !DILocation(line: 322, column: 5, scope: !429)
!443 = !DILocation(line: 323, column: 1, scope: !429)
!444 = distinct !DISubprogram(name: "prjm_eval_func_exec3", scope: !6, file: !6, line: 325, type: !21, scopeLine: 326, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !445)
!445 = !{!446, !447, !448}
!446 = !DILocalVariable(name: "ctx", arg: 1, scope: !444, file: !6, line: 325, type: !23)
!447 = !DILocalVariable(name: "ret_val", arg: 2, scope: !444, file: !6, line: 325, type: !38)
!448 = !DILocalVariable(name: "value_ptr", scope: !444, file: !6, line: 330, type: !35)
!449 = distinct !DIAssignID()
!450 = !DILocation(line: 0, scope: !444)
!451 = !DILocation(line: 329, column: 10, scope: !444)
!452 = !DILocation(line: 329, column: 16, scope: !444)
!453 = !DILocation(line: 330, column: 5, scope: !444)
!454 = !DILocation(line: 330, column: 18, scope: !444)
!455 = distinct !DIAssignID()
!456 = !DILocation(line: 332, column: 5, scope: !444)
!457 = !DILocation(line: 333, column: 5, scope: !444)
!458 = !DILocation(line: 334, column: 5, scope: !444)
!459 = !DILocation(line: 335, column: 1, scope: !444)
!460 = distinct !DISubprogram(name: "prjm_eval_func_set", scope: !6, file: !6, line: 337, type: !21, scopeLine: 338, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !461)
!461 = !{!462, !463, !464}
!462 = !DILocalVariable(name: "ctx", arg: 1, scope: !460, file: !6, line: 337, type: !23)
!463 = !DILocalVariable(name: "ret_val", arg: 2, scope: !460, file: !6, line: 337, type: !38)
!464 = !DILocalVariable(name: "value_ptr", scope: !460, file: !6, line: 342, type: !35)
!465 = distinct !DIAssignID()
!466 = !DILocation(line: 0, scope: !460)
!467 = !DILocation(line: 341, column: 10, scope: !460)
!468 = !DILocation(line: 341, column: 16, scope: !460)
!469 = !DILocation(line: 342, column: 5, scope: !460)
!470 = !DILocation(line: 342, column: 18, scope: !460)
!471 = distinct !DIAssignID()
!472 = !DILocation(line: 344, column: 5, scope: !460)
!473 = !DILocation(line: 345, column: 5, scope: !460)
!474 = !DILocation(line: 347, column: 5, scope: !460)
!475 = !DILocation(line: 348, column: 1, scope: !460)
!476 = distinct !DISubprogram(name: "prjm_eval_func_mem", scope: !6, file: !6, line: 352, type: !21, scopeLine: 353, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !477)
!477 = !{!478, !479, !480, !481}
!478 = !DILocalVariable(name: "ctx", arg: 1, scope: !476, file: !6, line: 352, type: !23)
!479 = !DILocalVariable(name: "ret_val", arg: 2, scope: !476, file: !6, line: 352, type: !38)
!480 = !DILocalVariable(name: "index_ptr", scope: !476, file: !6, line: 358, type: !35)
!481 = !DILocalVariable(name: "mem_addr", scope: !476, file: !6, line: 362, type: !35)
!482 = distinct !DIAssignID()
!483 = !DILocation(line: 0, scope: !476)
!484 = !DILocation(line: 357, column: 10, scope: !476)
!485 = !DILocation(line: 357, column: 16, scope: !476)
!486 = !DILocation(line: 358, column: 5, scope: !476)
!487 = !DILocation(line: 358, column: 18, scope: !476)
!488 = distinct !DIAssignID()
!489 = !DILocation(line: 359, column: 5, scope: !476)
!490 = !DILocation(line: 362, column: 60, scope: !476)
!491 = !DILocation(line: 362, column: 87, scope: !476)
!492 = !DILocation(line: 362, column: 86, scope: !476)
!493 = !DILocation(line: 362, column: 97, scope: !476)
!494 = !DILocation(line: 362, column: 75, scope: !476)
!495 = !DILocation(line: 362, column: 29, scope: !476)
!496 = !DILocation(line: 363, column: 9, scope: !497)
!497 = distinct !DILexicalBlock(scope: !476, file: !6, line: 363, column: 9)
!498 = !DILocation(line: 363, column: 9, scope: !476)
!499 = !DILocation(line: 365, column: 9, scope: !500)
!500 = distinct !DILexicalBlock(scope: !497, file: !6, line: 364, column: 5)
!501 = !DILocation(line: 366, column: 9, scope: !500)
!502 = !DILocation(line: 369, column: 5, scope: !476)
!503 = !DILocation(line: 370, column: 1, scope: !476)
!504 = !DISubprogram(name: "prjm_eval_memory_allocate", scope: !505, file: !505, line: 56, type: !506, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!505 = !DIFile(filename: "i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/MemoryBuffer.h", directory: "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit")
!506 = !DISubroutineType(types: !507)
!507 = !{!35, !37, !16}
!508 = distinct !DISubprogram(name: "prjm_eval_func_freembuf", scope: !6, file: !6, line: 372, type: !21, scopeLine: 373, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !509)
!509 = !{!510, !511}
!510 = !DILocalVariable(name: "ctx", arg: 1, scope: !508, file: !6, line: 372, type: !23)
!511 = !DILocalVariable(name: "ret_val", arg: 2, scope: !508, file: !6, line: 372, type: !38)
!512 = !DILocation(line: 0, scope: !508)
!513 = !DILocation(line: 377, column: 5, scope: !508)
!514 = !DILocation(line: 380, column: 38, scope: !508)
!515 = !DILocation(line: 380, column: 65, scope: !508)
!516 = !DILocation(line: 380, column: 64, scope: !508)
!517 = !DILocation(line: 380, column: 74, scope: !508)
!518 = !DILocation(line: 380, column: 53, scope: !508)
!519 = !DILocation(line: 380, column: 5, scope: !508)
!520 = !DILocation(line: 381, column: 1, scope: !508)
!521 = !DISubprogram(name: "prjm_eval_memory_free_block", scope: !505, file: !505, line: 48, type: !522, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!522 = !DISubroutineType(types: !523)
!523 = !{null, !37, !16}
!524 = distinct !DISubprogram(name: "prjm_eval_func_memcpy", scope: !6, file: !6, line: 383, type: !21, scopeLine: 384, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !525)
!525 = !{!526, !527, !528, !529, !530, !531, !532}
!526 = !DILocalVariable(name: "ctx", arg: 1, scope: !524, file: !6, line: 383, type: !23)
!527 = !DILocalVariable(name: "ret_val", arg: 2, scope: !524, file: !6, line: 383, type: !38)
!528 = !DILocalVariable(name: "src_index", scope: !524, file: !6, line: 388, type: !11)
!529 = !DILocalVariable(name: "count", scope: !524, file: !6, line: 389, type: !11)
!530 = !DILocalVariable(name: "dest_index_ptr", scope: !524, file: !6, line: 390, type: !35)
!531 = !DILocalVariable(name: "src_index_ptr", scope: !524, file: !6, line: 391, type: !35)
!532 = !DILocalVariable(name: "count_ptr", scope: !524, file: !6, line: 392, type: !35)
!533 = distinct !DIAssignID()
!534 = !DILocation(line: 0, scope: !524)
!535 = distinct !DIAssignID()
!536 = distinct !DIAssignID()
!537 = distinct !DIAssignID()
!538 = distinct !DIAssignID()
!539 = !DILocation(line: 387, column: 10, scope: !524)
!540 = !DILocation(line: 387, column: 16, scope: !524)
!541 = !DILocation(line: 388, column: 5, scope: !524)
!542 = !DILocation(line: 388, column: 17, scope: !524)
!543 = distinct !DIAssignID()
!544 = !DILocation(line: 389, column: 5, scope: !524)
!545 = !DILocation(line: 389, column: 17, scope: !524)
!546 = distinct !DIAssignID()
!547 = !DILocation(line: 390, column: 5, scope: !524)
!548 = !DILocation(line: 390, column: 18, scope: !524)
!549 = distinct !DIAssignID()
!550 = !DILocation(line: 391, column: 5, scope: !524)
!551 = !DILocation(line: 391, column: 18, scope: !524)
!552 = distinct !DIAssignID()
!553 = !DILocation(line: 392, column: 5, scope: !524)
!554 = !DILocation(line: 392, column: 18, scope: !524)
!555 = distinct !DIAssignID()
!556 = !DILocation(line: 394, column: 5, scope: !524)
!557 = !DILocation(line: 395, column: 5, scope: !524)
!558 = !DILocation(line: 396, column: 5, scope: !524)
!559 = !DILocation(line: 398, column: 5, scope: !524)
!560 = !DILocation(line: 399, column: 1, scope: !524)
!561 = !DISubprogram(name: "prjm_eval_memory_copy", scope: !505, file: !505, line: 66, type: !562, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!562 = !DISubroutineType(types: !563)
!563 = !{!35, !37, !35, !35, !35}
!564 = distinct !DISubprogram(name: "prjm_eval_func_memset", scope: !6, file: !6, line: 401, type: !21, scopeLine: 402, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !565)
!565 = !{!566, !567, !568, !569, !570, !571, !572}
!566 = !DILocalVariable(name: "ctx", arg: 1, scope: !564, file: !6, line: 401, type: !23)
!567 = !DILocalVariable(name: "ret_val", arg: 2, scope: !564, file: !6, line: 401, type: !38)
!568 = !DILocalVariable(name: "value", scope: !564, file: !6, line: 406, type: !11)
!569 = !DILocalVariable(name: "count", scope: !564, file: !6, line: 407, type: !11)
!570 = !DILocalVariable(name: "dest_index_ptr", scope: !564, file: !6, line: 408, type: !35)
!571 = !DILocalVariable(name: "value_ptr", scope: !564, file: !6, line: 409, type: !35)
!572 = !DILocalVariable(name: "count_ptr", scope: !564, file: !6, line: 410, type: !35)
!573 = distinct !DIAssignID()
!574 = !DILocation(line: 0, scope: !564)
!575 = distinct !DIAssignID()
!576 = distinct !DIAssignID()
!577 = distinct !DIAssignID()
!578 = distinct !DIAssignID()
!579 = !DILocation(line: 405, column: 10, scope: !564)
!580 = !DILocation(line: 405, column: 16, scope: !564)
!581 = !DILocation(line: 406, column: 5, scope: !564)
!582 = !DILocation(line: 406, column: 17, scope: !564)
!583 = distinct !DIAssignID()
!584 = !DILocation(line: 407, column: 5, scope: !564)
!585 = !DILocation(line: 407, column: 17, scope: !564)
!586 = distinct !DIAssignID()
!587 = !DILocation(line: 408, column: 5, scope: !564)
!588 = !DILocation(line: 408, column: 18, scope: !564)
!589 = distinct !DIAssignID()
!590 = !DILocation(line: 409, column: 5, scope: !564)
!591 = !DILocation(line: 409, column: 18, scope: !564)
!592 = distinct !DIAssignID()
!593 = !DILocation(line: 410, column: 5, scope: !564)
!594 = !DILocation(line: 410, column: 18, scope: !564)
!595 = distinct !DIAssignID()
!596 = !DILocation(line: 412, column: 5, scope: !564)
!597 = !DILocation(line: 413, column: 5, scope: !564)
!598 = !DILocation(line: 414, column: 5, scope: !564)
!599 = !DILocation(line: 416, column: 5, scope: !564)
!600 = !DILocation(line: 417, column: 1, scope: !564)
!601 = !DISubprogram(name: "prjm_eval_memory_set", scope: !505, file: !505, line: 79, type: !562, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!602 = distinct !DISubprogram(name: "prjm_eval_func_bnot", scope: !6, file: !6, line: 423, type: !21, scopeLine: 424, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !603)
!603 = !{!604, !605, !606}
!604 = !DILocalVariable(name: "ctx", arg: 1, scope: !602, file: !6, line: 423, type: !23)
!605 = !DILocalVariable(name: "ret_val", arg: 2, scope: !602, file: !6, line: 423, type: !38)
!606 = !DILocalVariable(name: "value_ptr", scope: !602, file: !6, line: 428, type: !35)
!607 = distinct !DIAssignID()
!608 = !DILocation(line: 0, scope: !602)
!609 = !DILocation(line: 427, column: 10, scope: !602)
!610 = !DILocation(line: 427, column: 16, scope: !602)
!611 = !DILocation(line: 428, column: 5, scope: !602)
!612 = !DILocation(line: 428, column: 18, scope: !602)
!613 = distinct !DIAssignID()
!614 = !DILocation(line: 430, column: 5, scope: !602)
!615 = !DILocation(line: 432, column: 5, scope: !602)
!616 = !DILocation(line: 433, column: 1, scope: !602)
!617 = distinct !DISubprogram(name: "prjm_eval_func_equal", scope: !6, file: !6, line: 435, type: !21, scopeLine: 436, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !618)
!618 = !{!619, !620, !621, !622, !623, !624}
!619 = !DILocalVariable(name: "ctx", arg: 1, scope: !617, file: !6, line: 435, type: !23)
!620 = !DILocalVariable(name: "ret_val", arg: 2, scope: !617, file: !6, line: 435, type: !38)
!621 = !DILocalVariable(name: "val1", scope: !617, file: !6, line: 439, type: !11)
!622 = !DILocalVariable(name: "val2", scope: !617, file: !6, line: 440, type: !11)
!623 = !DILocalVariable(name: "val1_ptr", scope: !617, file: !6, line: 441, type: !35)
!624 = !DILocalVariable(name: "val2_ptr", scope: !617, file: !6, line: 442, type: !35)
!625 = distinct !DIAssignID()
!626 = !DILocation(line: 0, scope: !617)
!627 = distinct !DIAssignID()
!628 = distinct !DIAssignID()
!629 = distinct !DIAssignID()
!630 = !DILocation(line: 439, column: 5, scope: !617)
!631 = !DILocation(line: 439, column: 17, scope: !617)
!632 = distinct !DIAssignID()
!633 = !DILocation(line: 440, column: 5, scope: !617)
!634 = !DILocation(line: 440, column: 17, scope: !617)
!635 = distinct !DIAssignID()
!636 = !DILocation(line: 441, column: 5, scope: !617)
!637 = !DILocation(line: 441, column: 18, scope: !617)
!638 = distinct !DIAssignID()
!639 = !DILocation(line: 442, column: 5, scope: !617)
!640 = !DILocation(line: 442, column: 18, scope: !617)
!641 = distinct !DIAssignID()
!642 = !DILocation(line: 444, column: 5, scope: !617)
!643 = !DILocation(line: 445, column: 5, scope: !617)
!644 = !DILocation(line: 447, column: 5, scope: !617)
!645 = !DILocation(line: 448, column: 1, scope: !617)
!646 = distinct !DISubprogram(name: "prjm_eval_func_notequal", scope: !6, file: !6, line: 450, type: !21, scopeLine: 451, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !647)
!647 = !{!648, !649, !650, !651, !652, !653}
!648 = !DILocalVariable(name: "ctx", arg: 1, scope: !646, file: !6, line: 450, type: !23)
!649 = !DILocalVariable(name: "ret_val", arg: 2, scope: !646, file: !6, line: 450, type: !38)
!650 = !DILocalVariable(name: "val1", scope: !646, file: !6, line: 454, type: !11)
!651 = !DILocalVariable(name: "val2", scope: !646, file: !6, line: 455, type: !11)
!652 = !DILocalVariable(name: "val1_ptr", scope: !646, file: !6, line: 456, type: !35)
!653 = !DILocalVariable(name: "val2_ptr", scope: !646, file: !6, line: 457, type: !35)
!654 = distinct !DIAssignID()
!655 = !DILocation(line: 0, scope: !646)
!656 = distinct !DIAssignID()
!657 = distinct !DIAssignID()
!658 = distinct !DIAssignID()
!659 = !DILocation(line: 454, column: 5, scope: !646)
!660 = !DILocation(line: 454, column: 17, scope: !646)
!661 = distinct !DIAssignID()
!662 = !DILocation(line: 455, column: 5, scope: !646)
!663 = !DILocation(line: 455, column: 17, scope: !646)
!664 = distinct !DIAssignID()
!665 = !DILocation(line: 456, column: 5, scope: !646)
!666 = !DILocation(line: 456, column: 18, scope: !646)
!667 = distinct !DIAssignID()
!668 = !DILocation(line: 457, column: 5, scope: !646)
!669 = !DILocation(line: 457, column: 18, scope: !646)
!670 = distinct !DIAssignID()
!671 = !DILocation(line: 458, column: 5, scope: !646)
!672 = !DILocation(line: 459, column: 5, scope: !646)
!673 = !DILocation(line: 461, column: 5, scope: !646)
!674 = !DILocation(line: 462, column: 1, scope: !646)
!675 = distinct !DISubprogram(name: "prjm_eval_func_below", scope: !6, file: !6, line: 464, type: !21, scopeLine: 465, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !676)
!676 = !{!677, !678, !679, !680, !681, !682}
!677 = !DILocalVariable(name: "ctx", arg: 1, scope: !675, file: !6, line: 464, type: !23)
!678 = !DILocalVariable(name: "ret_val", arg: 2, scope: !675, file: !6, line: 464, type: !38)
!679 = !DILocalVariable(name: "val1", scope: !675, file: !6, line: 468, type: !11)
!680 = !DILocalVariable(name: "val2", scope: !675, file: !6, line: 469, type: !11)
!681 = !DILocalVariable(name: "val1_ptr", scope: !675, file: !6, line: 470, type: !35)
!682 = !DILocalVariable(name: "val2_ptr", scope: !675, file: !6, line: 471, type: !35)
!683 = distinct !DIAssignID()
!684 = !DILocation(line: 0, scope: !675)
!685 = distinct !DIAssignID()
!686 = distinct !DIAssignID()
!687 = distinct !DIAssignID()
!688 = !DILocation(line: 468, column: 5, scope: !675)
!689 = !DILocation(line: 468, column: 17, scope: !675)
!690 = distinct !DIAssignID()
!691 = !DILocation(line: 469, column: 5, scope: !675)
!692 = !DILocation(line: 469, column: 17, scope: !675)
!693 = distinct !DIAssignID()
!694 = !DILocation(line: 470, column: 5, scope: !675)
!695 = !DILocation(line: 470, column: 18, scope: !675)
!696 = distinct !DIAssignID()
!697 = !DILocation(line: 471, column: 5, scope: !675)
!698 = !DILocation(line: 471, column: 18, scope: !675)
!699 = distinct !DIAssignID()
!700 = !DILocation(line: 473, column: 5, scope: !675)
!701 = !DILocation(line: 474, column: 5, scope: !675)
!702 = !DILocation(line: 476, column: 5, scope: !675)
!703 = !DILocation(line: 477, column: 1, scope: !675)
!704 = distinct !DISubprogram(name: "prjm_eval_func_above", scope: !6, file: !6, line: 479, type: !21, scopeLine: 480, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !705)
!705 = !{!706, !707, !708, !709, !710, !711}
!706 = !DILocalVariable(name: "ctx", arg: 1, scope: !704, file: !6, line: 479, type: !23)
!707 = !DILocalVariable(name: "ret_val", arg: 2, scope: !704, file: !6, line: 479, type: !38)
!708 = !DILocalVariable(name: "val1", scope: !704, file: !6, line: 483, type: !11)
!709 = !DILocalVariable(name: "val2", scope: !704, file: !6, line: 484, type: !11)
!710 = !DILocalVariable(name: "val1_ptr", scope: !704, file: !6, line: 485, type: !35)
!711 = !DILocalVariable(name: "val2_ptr", scope: !704, file: !6, line: 486, type: !35)
!712 = distinct !DIAssignID()
!713 = !DILocation(line: 0, scope: !704)
!714 = distinct !DIAssignID()
!715 = distinct !DIAssignID()
!716 = distinct !DIAssignID()
!717 = !DILocation(line: 483, column: 5, scope: !704)
!718 = !DILocation(line: 483, column: 17, scope: !704)
!719 = distinct !DIAssignID()
!720 = !DILocation(line: 484, column: 5, scope: !704)
!721 = !DILocation(line: 484, column: 17, scope: !704)
!722 = distinct !DIAssignID()
!723 = !DILocation(line: 485, column: 5, scope: !704)
!724 = !DILocation(line: 485, column: 18, scope: !704)
!725 = distinct !DIAssignID()
!726 = !DILocation(line: 486, column: 5, scope: !704)
!727 = !DILocation(line: 486, column: 18, scope: !704)
!728 = distinct !DIAssignID()
!729 = !DILocation(line: 488, column: 5, scope: !704)
!730 = !DILocation(line: 489, column: 5, scope: !704)
!731 = !DILocation(line: 491, column: 5, scope: !704)
!732 = !DILocation(line: 492, column: 1, scope: !704)
!733 = distinct !DISubprogram(name: "prjm_eval_func_beloweq", scope: !6, file: !6, line: 494, type: !21, scopeLine: 495, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !734)
!734 = !{!735, !736, !737, !738, !739, !740}
!735 = !DILocalVariable(name: "ctx", arg: 1, scope: !733, file: !6, line: 494, type: !23)
!736 = !DILocalVariable(name: "ret_val", arg: 2, scope: !733, file: !6, line: 494, type: !38)
!737 = !DILocalVariable(name: "val1", scope: !733, file: !6, line: 498, type: !11)
!738 = !DILocalVariable(name: "val2", scope: !733, file: !6, line: 499, type: !11)
!739 = !DILocalVariable(name: "val1_ptr", scope: !733, file: !6, line: 500, type: !35)
!740 = !DILocalVariable(name: "val2_ptr", scope: !733, file: !6, line: 501, type: !35)
!741 = distinct !DIAssignID()
!742 = !DILocation(line: 0, scope: !733)
!743 = distinct !DIAssignID()
!744 = distinct !DIAssignID()
!745 = distinct !DIAssignID()
!746 = !DILocation(line: 498, column: 5, scope: !733)
!747 = !DILocation(line: 498, column: 17, scope: !733)
!748 = distinct !DIAssignID()
!749 = !DILocation(line: 499, column: 5, scope: !733)
!750 = !DILocation(line: 499, column: 17, scope: !733)
!751 = distinct !DIAssignID()
!752 = !DILocation(line: 500, column: 5, scope: !733)
!753 = !DILocation(line: 500, column: 18, scope: !733)
!754 = distinct !DIAssignID()
!755 = !DILocation(line: 501, column: 5, scope: !733)
!756 = !DILocation(line: 501, column: 18, scope: !733)
!757 = distinct !DIAssignID()
!758 = !DILocation(line: 503, column: 5, scope: !733)
!759 = !DILocation(line: 504, column: 5, scope: !733)
!760 = !DILocation(line: 506, column: 5, scope: !733)
!761 = !DILocation(line: 507, column: 1, scope: !733)
!762 = distinct !DISubprogram(name: "prjm_eval_func_aboveeq", scope: !6, file: !6, line: 509, type: !21, scopeLine: 510, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !763)
!763 = !{!764, !765, !766, !767, !768, !769}
!764 = !DILocalVariable(name: "ctx", arg: 1, scope: !762, file: !6, line: 509, type: !23)
!765 = !DILocalVariable(name: "ret_val", arg: 2, scope: !762, file: !6, line: 509, type: !38)
!766 = !DILocalVariable(name: "val1", scope: !762, file: !6, line: 513, type: !11)
!767 = !DILocalVariable(name: "val2", scope: !762, file: !6, line: 514, type: !11)
!768 = !DILocalVariable(name: "val1_ptr", scope: !762, file: !6, line: 515, type: !35)
!769 = !DILocalVariable(name: "val2_ptr", scope: !762, file: !6, line: 516, type: !35)
!770 = distinct !DIAssignID()
!771 = !DILocation(line: 0, scope: !762)
!772 = distinct !DIAssignID()
!773 = distinct !DIAssignID()
!774 = distinct !DIAssignID()
!775 = !DILocation(line: 513, column: 5, scope: !762)
!776 = !DILocation(line: 513, column: 17, scope: !762)
!777 = distinct !DIAssignID()
!778 = !DILocation(line: 514, column: 5, scope: !762)
!779 = !DILocation(line: 514, column: 17, scope: !762)
!780 = distinct !DIAssignID()
!781 = !DILocation(line: 515, column: 5, scope: !762)
!782 = !DILocation(line: 515, column: 18, scope: !762)
!783 = distinct !DIAssignID()
!784 = !DILocation(line: 516, column: 5, scope: !762)
!785 = !DILocation(line: 516, column: 18, scope: !762)
!786 = distinct !DIAssignID()
!787 = !DILocation(line: 518, column: 5, scope: !762)
!788 = !DILocation(line: 519, column: 5, scope: !762)
!789 = !DILocation(line: 521, column: 5, scope: !762)
!790 = !DILocation(line: 522, column: 1, scope: !762)
!791 = distinct !DISubprogram(name: "prjm_eval_func_add", scope: !6, file: !6, line: 524, type: !21, scopeLine: 525, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !792)
!792 = !{!793, !794, !795, !796, !797, !798}
!793 = !DILocalVariable(name: "ctx", arg: 1, scope: !791, file: !6, line: 524, type: !23)
!794 = !DILocalVariable(name: "ret_val", arg: 2, scope: !791, file: !6, line: 524, type: !38)
!795 = !DILocalVariable(name: "val1", scope: !791, file: !6, line: 528, type: !11)
!796 = !DILocalVariable(name: "val2", scope: !791, file: !6, line: 529, type: !11)
!797 = !DILocalVariable(name: "val1_ptr", scope: !791, file: !6, line: 530, type: !35)
!798 = !DILocalVariable(name: "val2_ptr", scope: !791, file: !6, line: 531, type: !35)
!799 = distinct !DIAssignID()
!800 = !DILocation(line: 0, scope: !791)
!801 = distinct !DIAssignID()
!802 = distinct !DIAssignID()
!803 = distinct !DIAssignID()
!804 = !DILocation(line: 528, column: 5, scope: !791)
!805 = !DILocation(line: 528, column: 17, scope: !791)
!806 = distinct !DIAssignID()
!807 = !DILocation(line: 529, column: 5, scope: !791)
!808 = !DILocation(line: 529, column: 17, scope: !791)
!809 = distinct !DIAssignID()
!810 = !DILocation(line: 530, column: 5, scope: !791)
!811 = !DILocation(line: 530, column: 18, scope: !791)
!812 = distinct !DIAssignID()
!813 = !DILocation(line: 531, column: 5, scope: !791)
!814 = !DILocation(line: 531, column: 18, scope: !791)
!815 = distinct !DIAssignID()
!816 = !DILocation(line: 533, column: 5, scope: !791)
!817 = !DILocation(line: 534, column: 5, scope: !791)
!818 = !DILocation(line: 536, column: 5, scope: !791)
!819 = !DILocation(line: 537, column: 1, scope: !791)
!820 = distinct !DISubprogram(name: "prjm_eval_func_sub", scope: !6, file: !6, line: 539, type: !21, scopeLine: 540, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !821)
!821 = !{!822, !823, !824, !825, !826, !827}
!822 = !DILocalVariable(name: "ctx", arg: 1, scope: !820, file: !6, line: 539, type: !23)
!823 = !DILocalVariable(name: "ret_val", arg: 2, scope: !820, file: !6, line: 539, type: !38)
!824 = !DILocalVariable(name: "val1", scope: !820, file: !6, line: 543, type: !11)
!825 = !DILocalVariable(name: "val2", scope: !820, file: !6, line: 544, type: !11)
!826 = !DILocalVariable(name: "val1_ptr", scope: !820, file: !6, line: 545, type: !35)
!827 = !DILocalVariable(name: "val2_ptr", scope: !820, file: !6, line: 546, type: !35)
!828 = distinct !DIAssignID()
!829 = !DILocation(line: 0, scope: !820)
!830 = distinct !DIAssignID()
!831 = distinct !DIAssignID()
!832 = distinct !DIAssignID()
!833 = !DILocation(line: 543, column: 5, scope: !820)
!834 = !DILocation(line: 543, column: 17, scope: !820)
!835 = distinct !DIAssignID()
!836 = !DILocation(line: 544, column: 5, scope: !820)
!837 = !DILocation(line: 544, column: 17, scope: !820)
!838 = distinct !DIAssignID()
!839 = !DILocation(line: 545, column: 5, scope: !820)
!840 = !DILocation(line: 545, column: 18, scope: !820)
!841 = distinct !DIAssignID()
!842 = !DILocation(line: 546, column: 5, scope: !820)
!843 = !DILocation(line: 546, column: 18, scope: !820)
!844 = distinct !DIAssignID()
!845 = !DILocation(line: 548, column: 5, scope: !820)
!846 = !DILocation(line: 549, column: 5, scope: !820)
!847 = !DILocation(line: 551, column: 5, scope: !820)
!848 = !DILocation(line: 552, column: 1, scope: !820)
!849 = distinct !DISubprogram(name: "prjm_eval_func_mul", scope: !6, file: !6, line: 554, type: !21, scopeLine: 555, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !850)
!850 = !{!851, !852, !853, !854, !855, !856}
!851 = !DILocalVariable(name: "ctx", arg: 1, scope: !849, file: !6, line: 554, type: !23)
!852 = !DILocalVariable(name: "ret_val", arg: 2, scope: !849, file: !6, line: 554, type: !38)
!853 = !DILocalVariable(name: "val1", scope: !849, file: !6, line: 558, type: !11)
!854 = !DILocalVariable(name: "val2", scope: !849, file: !6, line: 559, type: !11)
!855 = !DILocalVariable(name: "val1_ptr", scope: !849, file: !6, line: 560, type: !35)
!856 = !DILocalVariable(name: "val2_ptr", scope: !849, file: !6, line: 561, type: !35)
!857 = distinct !DIAssignID()
!858 = !DILocation(line: 0, scope: !849)
!859 = distinct !DIAssignID()
!860 = distinct !DIAssignID()
!861 = distinct !DIAssignID()
!862 = !DILocation(line: 558, column: 5, scope: !849)
!863 = !DILocation(line: 558, column: 17, scope: !849)
!864 = distinct !DIAssignID()
!865 = !DILocation(line: 559, column: 5, scope: !849)
!866 = !DILocation(line: 559, column: 17, scope: !849)
!867 = distinct !DIAssignID()
!868 = !DILocation(line: 560, column: 5, scope: !849)
!869 = !DILocation(line: 560, column: 18, scope: !849)
!870 = distinct !DIAssignID()
!871 = !DILocation(line: 561, column: 5, scope: !849)
!872 = !DILocation(line: 561, column: 18, scope: !849)
!873 = distinct !DIAssignID()
!874 = !DILocation(line: 563, column: 5, scope: !849)
!875 = !DILocation(line: 564, column: 5, scope: !849)
!876 = !DILocation(line: 566, column: 5, scope: !849)
!877 = !DILocation(line: 567, column: 1, scope: !849)
!878 = distinct !DISubprogram(name: "prjm_eval_func_div", scope: !6, file: !6, line: 569, type: !21, scopeLine: 570, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !879)
!879 = !{!880, !881, !882, !883, !884, !885}
!880 = !DILocalVariable(name: "ctx", arg: 1, scope: !878, file: !6, line: 569, type: !23)
!881 = !DILocalVariable(name: "ret_val", arg: 2, scope: !878, file: !6, line: 569, type: !38)
!882 = !DILocalVariable(name: "val1", scope: !878, file: !6, line: 573, type: !11)
!883 = !DILocalVariable(name: "val2", scope: !878, file: !6, line: 574, type: !11)
!884 = !DILocalVariable(name: "val1_ptr", scope: !878, file: !6, line: 575, type: !35)
!885 = !DILocalVariable(name: "val2_ptr", scope: !878, file: !6, line: 576, type: !35)
!886 = distinct !DIAssignID()
!887 = !DILocation(line: 0, scope: !878)
!888 = distinct !DIAssignID()
!889 = distinct !DIAssignID()
!890 = distinct !DIAssignID()
!891 = !DILocation(line: 573, column: 5, scope: !878)
!892 = !DILocation(line: 573, column: 17, scope: !878)
!893 = distinct !DIAssignID()
!894 = !DILocation(line: 574, column: 5, scope: !878)
!895 = !DILocation(line: 574, column: 17, scope: !878)
!896 = distinct !DIAssignID()
!897 = !DILocation(line: 575, column: 5, scope: !878)
!898 = !DILocation(line: 575, column: 18, scope: !878)
!899 = distinct !DIAssignID()
!900 = !DILocation(line: 576, column: 5, scope: !878)
!901 = !DILocation(line: 576, column: 18, scope: !878)
!902 = distinct !DIAssignID()
!903 = !DILocation(line: 578, column: 5, scope: !878)
!904 = !DILocation(line: 579, column: 5, scope: !878)
!905 = !DILocation(line: 581, column: 14, scope: !906)
!906 = distinct !DILexicalBlock(scope: !878, file: !6, line: 581, column: 8)
!907 = !DILocation(line: 581, column: 13, scope: !906)
!908 = !DILocation(line: 581, column: 8, scope: !906)
!909 = !DILocation(line: 581, column: 24, scope: !906)
!910 = !DILocation(line: 581, column: 8, scope: !878)
!911 = !DILocation(line: 587, column: 5, scope: !878)
!912 = !DILocation(line: 588, column: 1, scope: !878)
!913 = distinct !DISubprogram(name: "prjm_eval_func_mod", scope: !6, file: !6, line: 647, type: !21, scopeLine: 648, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !914)
!914 = !{!915, !916, !917, !918, !919, !920}
!915 = !DILocalVariable(name: "ctx", arg: 1, scope: !913, file: !6, line: 647, type: !23)
!916 = !DILocalVariable(name: "ret_val", arg: 2, scope: !913, file: !6, line: 647, type: !38)
!917 = !DILocalVariable(name: "val1", scope: !913, file: !6, line: 651, type: !11)
!918 = !DILocalVariable(name: "val2", scope: !913, file: !6, line: 652, type: !11)
!919 = !DILocalVariable(name: "val1_ptr", scope: !913, file: !6, line: 653, type: !35)
!920 = !DILocalVariable(name: "val2_ptr", scope: !913, file: !6, line: 654, type: !35)
!921 = distinct !DIAssignID()
!922 = !DILocation(line: 0, scope: !913)
!923 = distinct !DIAssignID()
!924 = distinct !DIAssignID()
!925 = distinct !DIAssignID()
!926 = !DILocation(line: 651, column: 5, scope: !913)
!927 = !DILocation(line: 651, column: 17, scope: !913)
!928 = distinct !DIAssignID()
!929 = !DILocation(line: 652, column: 5, scope: !913)
!930 = !DILocation(line: 652, column: 17, scope: !913)
!931 = distinct !DIAssignID()
!932 = !DILocation(line: 653, column: 5, scope: !913)
!933 = !DILocation(line: 653, column: 18, scope: !913)
!934 = distinct !DIAssignID()
!935 = !DILocation(line: 654, column: 5, scope: !913)
!936 = !DILocation(line: 654, column: 18, scope: !913)
!937 = distinct !DIAssignID()
!938 = !DILocation(line: 656, column: 5, scope: !913)
!939 = !DILocation(line: 657, column: 5, scope: !913)
!940 = !DILocation(line: 659, column: 5, scope: !913)
!941 = !DILocalVariable(name: "numerator", arg: 1, scope: !942, file: !6, line: 618, type: !11)
!942 = distinct !DISubprogram(name: "bounded_milkdrop_remainder", scope: !6, file: !6, line: 618, type: !943, scopeLine: 619, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !945)
!943 = !DISubroutineType(types: !944)
!944 = !{!11, !11, !11}
!945 = !{!941, !946, !947, !950, !951, !952, !953, !955, !956, !957}
!946 = !DILocalVariable(name: "denominator", arg: 2, scope: !942, file: !6, line: 618, type: !11)
!947 = !DILocalVariable(name: "numeratorBits", scope: !942, file: !6, line: 620, type: !948)
!948 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !949)
!949 = !DIDerivedType(tag: DW_TAG_typedef, name: "remainder_bits_t", file: !6, line: 603, baseType: !57)
!950 = !DILocalVariable(name: "denominatorBits", scope: !942, file: !6, line: 621, type: !948)
!951 = !DILocalVariable(name: "numeratorMagnitude", scope: !942, file: !6, line: 622, type: !948)
!952 = !DILocalVariable(name: "denominatorMagnitude", scope: !942, file: !6, line: 623, type: !948)
!953 = !DILocalVariable(name: "dividend", scope: !942, file: !6, line: 633, type: !954)
!954 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !5)
!955 = !DILocalVariable(name: "divisor", scope: !942, file: !6, line: 634, type: !954)
!956 = !DILocalVariable(name: "minimum", scope: !942, file: !6, line: 638, type: !954)
!957 = !DILocalVariable(name: "remainder", scope: !942, file: !6, line: 642, type: !62)
!958 = !DILocation(line: 0, scope: !942, inlinedAt: !959)
!959 = distinct !DILocation(line: 659, column: 5, scope: !913)
!960 = !DILocalVariable(name: "value", arg: 1, scope: !961, file: !6, line: 609, type: !11)
!961 = distinct !DISubprogram(name: "remainder_value_bits", scope: !6, file: !6, line: 609, type: !962, scopeLine: 610, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !964)
!962 = !DISubroutineType(types: !963)
!963 = !{!949, !11}
!964 = !{!960, !965}
!965 = !DILocalVariable(name: "bits", scope: !961, file: !6, line: 611, type: !949)
!966 = !DILocation(line: 0, scope: !961, inlinedAt: !967)
!967 = distinct !DILocation(line: 620, column: 44, scope: !942, inlinedAt: !959)
!968 = !DILocalVariable(name: "dst", arg: 1, scope: !969, file: !970, line: 50, type: !974)
!969 = distinct !DISubprogram(name: "memcpy", linkageName: "_ZL6memcpyPvU17pass_object_size0PKvm", scope: !970, file: !970, line: 50, type: !971, scopeLine: 52, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !979)
!970 = !DIFile(filename: "Library/Android/sdk/ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/sysroot/usr/include/bits/fortify/string.h", directory: "/Users/jneerdael")
!971 = !DISubroutineType(types: !972)
!972 = !{!973, !974, !59, !975, !977}
!973 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!974 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !973)
!975 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !976, size: 64)
!976 = !DIDerivedType(tag: DW_TAG_const_type, baseType: null)
!977 = !DIDerivedType(tag: DW_TAG_typedef, name: "size_t", file: !978, line: 13, baseType: !59)
!978 = !DIFile(filename: "Library/Android/sdk/ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/lib/clang/18/include/__stddef_size_t.h", directory: "/Users/jneerdael")
!979 = !{!968, !980, !981, !982}
!980 = !DILocalVariable(arg: 2, scope: !969, type: !59, flags: DIFlagArtificial)
!981 = !DILocalVariable(name: "src", arg: 3, scope: !969, file: !970, line: 50, type: !975)
!982 = !DILocalVariable(name: "copy_amount", arg: 4, scope: !969, file: !970, line: 50, type: !977)
!983 = !DILocation(line: 0, scope: !969, inlinedAt: !984)
!984 = distinct !DILocation(line: 612, column: 5, scope: !961, inlinedAt: !967)
!985 = !DILocation(line: 53, column: 12, scope: !969, inlinedAt: !984)
!986 = !DILocation(line: 0, scope: !961, inlinedAt: !987)
!987 = distinct !DILocation(line: 621, column: 46, scope: !942, inlinedAt: !959)
!988 = !DILocation(line: 0, scope: !969, inlinedAt: !989)
!989 = distinct !DILocation(line: 612, column: 5, scope: !961, inlinedAt: !987)
!990 = !DILocation(line: 53, column: 12, scope: !969, inlinedAt: !989)
!991 = !DILocation(line: 622, column: 63, scope: !942, inlinedAt: !959)
!992 = !DILocation(line: 623, column: 67, scope: !942, inlinedAt: !959)
!993 = !DILocation(line: 624, column: 55, scope: !994, inlinedAt: !959)
!994 = distinct !DILexicalBlock(scope: !942, file: !6, line: 624, column: 9)
!995 = !DILocation(line: 629, column: 29, scope: !996, inlinedAt: !959)
!996 = distinct !DILexicalBlock(scope: !942, file: !6, line: 628, column: 9)
!997 = !DILocation(line: 629, column: 58, scope: !996, inlinedAt: !959)
!998 = !DILocation(line: 629, column: 77, scope: !996, inlinedAt: !959)
!999 = !DILocation(line: 629, column: 100, scope: !996, inlinedAt: !959)
!1000 = !DILocation(line: 630, column: 30, scope: !996, inlinedAt: !959)
!1001 = !DILocation(line: 630, column: 58, scope: !996, inlinedAt: !959)
!1002 = !DILocation(line: 631, column: 31, scope: !996, inlinedAt: !959)
!1003 = !DILocation(line: 631, column: 60, scope: !996, inlinedAt: !959)
!1004 = !DILocation(line: 633, column: 34, scope: !942, inlinedAt: !959)
!1005 = !DILocation(line: 634, column: 33, scope: !942, inlinedAt: !959)
!1006 = !DILocation(line: 640, column: 17, scope: !1007, inlinedAt: !959)
!1007 = distinct !DILexicalBlock(scope: !942, file: !6, line: 640, column: 9)
!1008 = !DILocation(line: 640, column: 22, scope: !1007, inlinedAt: !959)
!1009 = !DILocation(line: 640, column: 35, scope: !1007, inlinedAt: !959)
!1010 = !DILocation(line: 640, column: 46, scope: !1007, inlinedAt: !959)
!1011 = !DILocation(line: 642, column: 59, scope: !942, inlinedAt: !959)
!1012 = !DILocation(line: 642, column: 35, scope: !942, inlinedAt: !959)
!1013 = !DILocation(line: 643, column: 31, scope: !942, inlinedAt: !959)
!1014 = !DILocation(line: 643, column: 63, scope: !942, inlinedAt: !959)
!1015 = !DILocation(line: 660, column: 1, scope: !913)
!1016 = distinct !DISubprogram(name: "prjm_eval_func_boolean_and_op", scope: !6, file: !6, line: 662, type: !21, scopeLine: 663, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1017)
!1017 = !{!1018, !1019, !1020, !1021, !1022, !1023}
!1018 = !DILocalVariable(name: "ctx", arg: 1, scope: !1016, file: !6, line: 662, type: !23)
!1019 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1016, file: !6, line: 662, type: !38)
!1020 = !DILocalVariable(name: "val1", scope: !1016, file: !6, line: 666, type: !11)
!1021 = !DILocalVariable(name: "val1_ptr", scope: !1016, file: !6, line: 667, type: !35)
!1022 = !DILocalVariable(name: "val2", scope: !1016, file: !6, line: 668, type: !11)
!1023 = !DILocalVariable(name: "val2_ptr", scope: !1016, file: !6, line: 669, type: !35)
!1024 = distinct !DIAssignID()
!1025 = !DILocation(line: 0, scope: !1016)
!1026 = distinct !DIAssignID()
!1027 = distinct !DIAssignID()
!1028 = distinct !DIAssignID()
!1029 = !DILocation(line: 666, column: 5, scope: !1016)
!1030 = !DILocation(line: 666, column: 17, scope: !1016)
!1031 = distinct !DIAssignID()
!1032 = !DILocation(line: 667, column: 5, scope: !1016)
!1033 = !DILocation(line: 667, column: 18, scope: !1016)
!1034 = distinct !DIAssignID()
!1035 = !DILocation(line: 668, column: 5, scope: !1016)
!1036 = !DILocation(line: 668, column: 17, scope: !1016)
!1037 = distinct !DIAssignID()
!1038 = !DILocation(line: 669, column: 5, scope: !1016)
!1039 = !DILocation(line: 669, column: 18, scope: !1016)
!1040 = distinct !DIAssignID()
!1041 = !DILocation(line: 675, column: 5, scope: !1016)
!1042 = !DILocation(line: 677, column: 15, scope: !1043)
!1043 = distinct !DILexicalBlock(scope: !1016, file: !6, line: 677, column: 9)
!1044 = !DILocation(line: 677, column: 14, scope: !1043)
!1045 = !DILocation(line: 677, column: 9, scope: !1043)
!1046 = !DILocation(line: 677, column: 25, scope: !1043)
!1047 = !DILocation(line: 677, column: 9, scope: !1016)
!1048 = !DILocation(line: 679, column: 9, scope: !1049)
!1049 = distinct !DILexicalBlock(scope: !1043, file: !6, line: 678, column: 5)
!1050 = !DILocation(line: 681, column: 9, scope: !1049)
!1051 = !DILocation(line: 682, column: 5, scope: !1049)
!1052 = !DILocation(line: 0, scope: !1043)
!1053 = !DILocation(line: 687, column: 1, scope: !1016)
!1054 = distinct !DISubprogram(name: "prjm_eval_func_boolean_or_op", scope: !6, file: !6, line: 689, type: !21, scopeLine: 690, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1055)
!1055 = !{!1056, !1057, !1058, !1059, !1060, !1061}
!1056 = !DILocalVariable(name: "ctx", arg: 1, scope: !1054, file: !6, line: 689, type: !23)
!1057 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1054, file: !6, line: 689, type: !38)
!1058 = !DILocalVariable(name: "val1", scope: !1054, file: !6, line: 693, type: !11)
!1059 = !DILocalVariable(name: "val1_ptr", scope: !1054, file: !6, line: 694, type: !35)
!1060 = !DILocalVariable(name: "val2", scope: !1054, file: !6, line: 695, type: !11)
!1061 = !DILocalVariable(name: "val2_ptr", scope: !1054, file: !6, line: 696, type: !35)
!1062 = distinct !DIAssignID()
!1063 = !DILocation(line: 0, scope: !1054)
!1064 = distinct !DIAssignID()
!1065 = distinct !DIAssignID()
!1066 = distinct !DIAssignID()
!1067 = !DILocation(line: 693, column: 5, scope: !1054)
!1068 = !DILocation(line: 693, column: 17, scope: !1054)
!1069 = distinct !DIAssignID()
!1070 = !DILocation(line: 694, column: 5, scope: !1054)
!1071 = !DILocation(line: 694, column: 18, scope: !1054)
!1072 = distinct !DIAssignID()
!1073 = !DILocation(line: 695, column: 5, scope: !1054)
!1074 = !DILocation(line: 695, column: 17, scope: !1054)
!1075 = distinct !DIAssignID()
!1076 = !DILocation(line: 696, column: 5, scope: !1054)
!1077 = !DILocation(line: 696, column: 18, scope: !1054)
!1078 = distinct !DIAssignID()
!1079 = !DILocation(line: 702, column: 5, scope: !1054)
!1080 = !DILocation(line: 704, column: 15, scope: !1081)
!1081 = distinct !DILexicalBlock(scope: !1054, file: !6, line: 704, column: 9)
!1082 = !DILocation(line: 704, column: 14, scope: !1081)
!1083 = !DILocation(line: 704, column: 9, scope: !1081)
!1084 = !DILocation(line: 704, column: 25, scope: !1081)
!1085 = !DILocation(line: 704, column: 9, scope: !1054)
!1086 = !DILocation(line: 706, column: 9, scope: !1087)
!1087 = distinct !DILexicalBlock(scope: !1081, file: !6, line: 705, column: 5)
!1088 = !DILocation(line: 708, column: 9, scope: !1087)
!1089 = !DILocation(line: 709, column: 5, scope: !1087)
!1090 = !DILocation(line: 0, scope: !1081)
!1091 = !DILocation(line: 714, column: 1, scope: !1054)
!1092 = distinct !DISubprogram(name: "prjm_eval_func_boolean_and_func", scope: !6, file: !6, line: 716, type: !21, scopeLine: 717, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1093)
!1093 = !{!1094, !1095, !1096, !1097, !1098, !1099}
!1094 = !DILocalVariable(name: "ctx", arg: 1, scope: !1092, file: !6, line: 716, type: !23)
!1095 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1092, file: !6, line: 716, type: !38)
!1096 = !DILocalVariable(name: "val1", scope: !1092, file: !6, line: 720, type: !11)
!1097 = !DILocalVariable(name: "val2", scope: !1092, file: !6, line: 721, type: !11)
!1098 = !DILocalVariable(name: "val1_ptr", scope: !1092, file: !6, line: 722, type: !35)
!1099 = !DILocalVariable(name: "val2_ptr", scope: !1092, file: !6, line: 723, type: !35)
!1100 = distinct !DIAssignID()
!1101 = !DILocation(line: 0, scope: !1092)
!1102 = distinct !DIAssignID()
!1103 = distinct !DIAssignID()
!1104 = distinct !DIAssignID()
!1105 = !DILocation(line: 720, column: 5, scope: !1092)
!1106 = !DILocation(line: 720, column: 17, scope: !1092)
!1107 = distinct !DIAssignID()
!1108 = !DILocation(line: 721, column: 5, scope: !1092)
!1109 = !DILocation(line: 721, column: 17, scope: !1092)
!1110 = distinct !DIAssignID()
!1111 = !DILocation(line: 722, column: 5, scope: !1092)
!1112 = !DILocation(line: 722, column: 18, scope: !1092)
!1113 = distinct !DIAssignID()
!1114 = !DILocation(line: 723, column: 5, scope: !1092)
!1115 = !DILocation(line: 723, column: 18, scope: !1092)
!1116 = distinct !DIAssignID()
!1117 = !DILocation(line: 725, column: 5, scope: !1092)
!1118 = !DILocation(line: 726, column: 5, scope: !1092)
!1119 = !DILocation(line: 729, column: 5, scope: !1092)
!1120 = !DILocation(line: 730, column: 1, scope: !1092)
!1121 = distinct !DISubprogram(name: "prjm_eval_func_boolean_or_func", scope: !6, file: !6, line: 732, type: !21, scopeLine: 733, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1122)
!1122 = !{!1123, !1124, !1125, !1126, !1127, !1128}
!1123 = !DILocalVariable(name: "ctx", arg: 1, scope: !1121, file: !6, line: 732, type: !23)
!1124 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1121, file: !6, line: 732, type: !38)
!1125 = !DILocalVariable(name: "val1", scope: !1121, file: !6, line: 736, type: !11)
!1126 = !DILocalVariable(name: "val2", scope: !1121, file: !6, line: 737, type: !11)
!1127 = !DILocalVariable(name: "val1_ptr", scope: !1121, file: !6, line: 738, type: !35)
!1128 = !DILocalVariable(name: "val2_ptr", scope: !1121, file: !6, line: 739, type: !35)
!1129 = distinct !DIAssignID()
!1130 = !DILocation(line: 0, scope: !1121)
!1131 = distinct !DIAssignID()
!1132 = distinct !DIAssignID()
!1133 = distinct !DIAssignID()
!1134 = !DILocation(line: 736, column: 5, scope: !1121)
!1135 = !DILocation(line: 736, column: 17, scope: !1121)
!1136 = distinct !DIAssignID()
!1137 = !DILocation(line: 737, column: 5, scope: !1121)
!1138 = !DILocation(line: 737, column: 17, scope: !1121)
!1139 = distinct !DIAssignID()
!1140 = !DILocation(line: 738, column: 5, scope: !1121)
!1141 = !DILocation(line: 738, column: 18, scope: !1121)
!1142 = distinct !DIAssignID()
!1143 = !DILocation(line: 739, column: 5, scope: !1121)
!1144 = !DILocation(line: 739, column: 18, scope: !1121)
!1145 = distinct !DIAssignID()
!1146 = !DILocation(line: 741, column: 5, scope: !1121)
!1147 = !DILocation(line: 742, column: 5, scope: !1121)
!1148 = !DILocation(line: 745, column: 5, scope: !1121)
!1149 = !DILocation(line: 746, column: 1, scope: !1121)
!1150 = distinct !DISubprogram(name: "prjm_eval_func_neg", scope: !6, file: !6, line: 748, type: !21, scopeLine: 749, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1151)
!1151 = !{!1152, !1153, !1154, !1155}
!1152 = !DILocalVariable(name: "ctx", arg: 1, scope: !1150, file: !6, line: 748, type: !23)
!1153 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1150, file: !6, line: 748, type: !38)
!1154 = !DILocalVariable(name: "val1", scope: !1150, file: !6, line: 752, type: !11)
!1155 = !DILocalVariable(name: "val1_ptr", scope: !1150, file: !6, line: 753, type: !35)
!1156 = distinct !DIAssignID()
!1157 = !DILocation(line: 0, scope: !1150)
!1158 = distinct !DIAssignID()
!1159 = !DILocation(line: 752, column: 5, scope: !1150)
!1160 = !DILocation(line: 752, column: 17, scope: !1150)
!1161 = distinct !DIAssignID()
!1162 = !DILocation(line: 753, column: 5, scope: !1150)
!1163 = !DILocation(line: 753, column: 18, scope: !1150)
!1164 = distinct !DIAssignID()
!1165 = !DILocation(line: 755, column: 5, scope: !1150)
!1166 = !DILocation(line: 757, column: 5, scope: !1150)
!1167 = !DILocation(line: 758, column: 1, scope: !1150)
!1168 = distinct !DISubprogram(name: "prjm_eval_func_add_op", scope: !6, file: !6, line: 760, type: !21, scopeLine: 761, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1169)
!1169 = !{!1170, !1171, !1172, !1173}
!1170 = !DILocalVariable(name: "ctx", arg: 1, scope: !1168, file: !6, line: 760, type: !23)
!1171 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1168, file: !6, line: 760, type: !38)
!1172 = !DILocalVariable(name: "val2", scope: !1168, file: !6, line: 764, type: !11)
!1173 = !DILocalVariable(name: "val2_ptr", scope: !1168, file: !6, line: 765, type: !35)
!1174 = distinct !DIAssignID()
!1175 = !DILocation(line: 0, scope: !1168)
!1176 = distinct !DIAssignID()
!1177 = !DILocation(line: 764, column: 5, scope: !1168)
!1178 = !DILocation(line: 764, column: 17, scope: !1168)
!1179 = distinct !DIAssignID()
!1180 = !DILocation(line: 765, column: 5, scope: !1168)
!1181 = !DILocation(line: 765, column: 18, scope: !1168)
!1182 = distinct !DIAssignID()
!1183 = !DILocation(line: 767, column: 5, scope: !1168)
!1184 = !DILocation(line: 768, column: 5, scope: !1168)
!1185 = !DILocation(line: 770, column: 5, scope: !1168)
!1186 = !DILocation(line: 771, column: 1, scope: !1168)
!1187 = distinct !DISubprogram(name: "prjm_eval_func_sub_op", scope: !6, file: !6, line: 773, type: !21, scopeLine: 774, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1188)
!1188 = !{!1189, !1190, !1191, !1192}
!1189 = !DILocalVariable(name: "ctx", arg: 1, scope: !1187, file: !6, line: 773, type: !23)
!1190 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1187, file: !6, line: 773, type: !38)
!1191 = !DILocalVariable(name: "val2", scope: !1187, file: !6, line: 777, type: !11)
!1192 = !DILocalVariable(name: "val2_ptr", scope: !1187, file: !6, line: 778, type: !35)
!1193 = distinct !DIAssignID()
!1194 = !DILocation(line: 0, scope: !1187)
!1195 = distinct !DIAssignID()
!1196 = !DILocation(line: 777, column: 5, scope: !1187)
!1197 = !DILocation(line: 777, column: 17, scope: !1187)
!1198 = distinct !DIAssignID()
!1199 = !DILocation(line: 778, column: 5, scope: !1187)
!1200 = !DILocation(line: 778, column: 18, scope: !1187)
!1201 = distinct !DIAssignID()
!1202 = !DILocation(line: 780, column: 5, scope: !1187)
!1203 = !DILocation(line: 781, column: 5, scope: !1187)
!1204 = !DILocation(line: 783, column: 5, scope: !1187)
!1205 = !DILocation(line: 784, column: 1, scope: !1187)
!1206 = distinct !DISubprogram(name: "prjm_eval_func_mul_op", scope: !6, file: !6, line: 786, type: !21, scopeLine: 787, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1207)
!1207 = !{!1208, !1209, !1210, !1211}
!1208 = !DILocalVariable(name: "ctx", arg: 1, scope: !1206, file: !6, line: 786, type: !23)
!1209 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1206, file: !6, line: 786, type: !38)
!1210 = !DILocalVariable(name: "val2", scope: !1206, file: !6, line: 790, type: !11)
!1211 = !DILocalVariable(name: "val2_ptr", scope: !1206, file: !6, line: 791, type: !35)
!1212 = distinct !DIAssignID()
!1213 = !DILocation(line: 0, scope: !1206)
!1214 = distinct !DIAssignID()
!1215 = !DILocation(line: 790, column: 5, scope: !1206)
!1216 = !DILocation(line: 790, column: 17, scope: !1206)
!1217 = distinct !DIAssignID()
!1218 = !DILocation(line: 791, column: 5, scope: !1206)
!1219 = !DILocation(line: 791, column: 18, scope: !1206)
!1220 = distinct !DIAssignID()
!1221 = !DILocation(line: 793, column: 5, scope: !1206)
!1222 = !DILocation(line: 794, column: 5, scope: !1206)
!1223 = !DILocation(line: 796, column: 5, scope: !1206)
!1224 = !DILocation(line: 797, column: 1, scope: !1206)
!1225 = distinct !DISubprogram(name: "prjm_eval_func_div_op", scope: !6, file: !6, line: 799, type: !21, scopeLine: 800, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1226)
!1226 = !{!1227, !1228, !1229, !1230}
!1227 = !DILocalVariable(name: "ctx", arg: 1, scope: !1225, file: !6, line: 799, type: !23)
!1228 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1225, file: !6, line: 799, type: !38)
!1229 = !DILocalVariable(name: "val2", scope: !1225, file: !6, line: 803, type: !11)
!1230 = !DILocalVariable(name: "val2_ptr", scope: !1225, file: !6, line: 804, type: !35)
!1231 = distinct !DIAssignID()
!1232 = !DILocation(line: 0, scope: !1225)
!1233 = distinct !DIAssignID()
!1234 = !DILocation(line: 803, column: 5, scope: !1225)
!1235 = !DILocation(line: 803, column: 17, scope: !1225)
!1236 = distinct !DIAssignID()
!1237 = !DILocation(line: 804, column: 5, scope: !1225)
!1238 = !DILocation(line: 804, column: 18, scope: !1225)
!1239 = distinct !DIAssignID()
!1240 = !DILocation(line: 806, column: 5, scope: !1225)
!1241 = !DILocation(line: 807, column: 5, scope: !1225)
!1242 = !DILocation(line: 809, column: 14, scope: !1243)
!1243 = distinct !DILexicalBlock(scope: !1225, file: !6, line: 809, column: 8)
!1244 = !DILocation(line: 809, column: 13, scope: !1243)
!1245 = !DILocation(line: 809, column: 8, scope: !1243)
!1246 = !DILocation(line: 809, column: 24, scope: !1243)
!1247 = !DILocation(line: 809, column: 8, scope: !1225)
!1248 = !DILocation(line: 815, column: 5, scope: !1225)
!1249 = !DILocation(line: 816, column: 1, scope: !1225)
!1250 = distinct !DISubprogram(name: "prjm_eval_func_bitwise_or_op", scope: !6, file: !6, line: 818, type: !21, scopeLine: 819, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1251)
!1251 = !{!1252, !1253, !1254, !1255}
!1252 = !DILocalVariable(name: "ctx", arg: 1, scope: !1250, file: !6, line: 818, type: !23)
!1253 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1250, file: !6, line: 818, type: !38)
!1254 = !DILocalVariable(name: "val2", scope: !1250, file: !6, line: 822, type: !11)
!1255 = !DILocalVariable(name: "val2_ptr", scope: !1250, file: !6, line: 823, type: !35)
!1256 = distinct !DIAssignID()
!1257 = !DILocation(line: 0, scope: !1250)
!1258 = distinct !DIAssignID()
!1259 = !DILocation(line: 822, column: 5, scope: !1250)
!1260 = !DILocation(line: 822, column: 17, scope: !1250)
!1261 = distinct !DIAssignID()
!1262 = !DILocation(line: 823, column: 5, scope: !1250)
!1263 = !DILocation(line: 823, column: 18, scope: !1250)
!1264 = distinct !DIAssignID()
!1265 = !DILocation(line: 825, column: 5, scope: !1250)
!1266 = !DILocation(line: 826, column: 5, scope: !1250)
!1267 = !DILocation(line: 828, column: 5, scope: !1250)
!1268 = !DILocation(line: 829, column: 1, scope: !1250)
!1269 = distinct !DISubprogram(name: "prjm_eval_func_bitwise_or", scope: !6, file: !6, line: 831, type: !21, scopeLine: 832, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1270)
!1270 = !{!1271, !1272, !1273, !1274, !1275, !1276}
!1271 = !DILocalVariable(name: "ctx", arg: 1, scope: !1269, file: !6, line: 831, type: !23)
!1272 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1269, file: !6, line: 831, type: !38)
!1273 = !DILocalVariable(name: "val1", scope: !1269, file: !6, line: 835, type: !11)
!1274 = !DILocalVariable(name: "val1_ptr", scope: !1269, file: !6, line: 836, type: !35)
!1275 = !DILocalVariable(name: "val2", scope: !1269, file: !6, line: 837, type: !11)
!1276 = !DILocalVariable(name: "val2_ptr", scope: !1269, file: !6, line: 838, type: !35)
!1277 = distinct !DIAssignID()
!1278 = !DILocation(line: 0, scope: !1269)
!1279 = distinct !DIAssignID()
!1280 = distinct !DIAssignID()
!1281 = distinct !DIAssignID()
!1282 = !DILocation(line: 835, column: 5, scope: !1269)
!1283 = !DILocation(line: 835, column: 17, scope: !1269)
!1284 = distinct !DIAssignID()
!1285 = !DILocation(line: 836, column: 5, scope: !1269)
!1286 = !DILocation(line: 836, column: 18, scope: !1269)
!1287 = distinct !DIAssignID()
!1288 = !DILocation(line: 837, column: 5, scope: !1269)
!1289 = !DILocation(line: 837, column: 17, scope: !1269)
!1290 = distinct !DIAssignID()
!1291 = !DILocation(line: 838, column: 5, scope: !1269)
!1292 = !DILocation(line: 838, column: 18, scope: !1269)
!1293 = distinct !DIAssignID()
!1294 = !DILocation(line: 840, column: 5, scope: !1269)
!1295 = !DILocation(line: 841, column: 5, scope: !1269)
!1296 = !DILocation(line: 843, column: 5, scope: !1269)
!1297 = !DILocation(line: 844, column: 1, scope: !1269)
!1298 = distinct !DISubprogram(name: "prjm_eval_func_bitwise_and_op", scope: !6, file: !6, line: 846, type: !21, scopeLine: 847, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1299)
!1299 = !{!1300, !1301, !1302, !1303}
!1300 = !DILocalVariable(name: "ctx", arg: 1, scope: !1298, file: !6, line: 846, type: !23)
!1301 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1298, file: !6, line: 846, type: !38)
!1302 = !DILocalVariable(name: "val2", scope: !1298, file: !6, line: 850, type: !11)
!1303 = !DILocalVariable(name: "val2_ptr", scope: !1298, file: !6, line: 851, type: !35)
!1304 = distinct !DIAssignID()
!1305 = !DILocation(line: 0, scope: !1298)
!1306 = distinct !DIAssignID()
!1307 = !DILocation(line: 850, column: 5, scope: !1298)
!1308 = !DILocation(line: 850, column: 17, scope: !1298)
!1309 = distinct !DIAssignID()
!1310 = !DILocation(line: 851, column: 5, scope: !1298)
!1311 = !DILocation(line: 851, column: 18, scope: !1298)
!1312 = distinct !DIAssignID()
!1313 = !DILocation(line: 853, column: 5, scope: !1298)
!1314 = !DILocation(line: 854, column: 5, scope: !1298)
!1315 = !DILocation(line: 856, column: 5, scope: !1298)
!1316 = !DILocation(line: 857, column: 1, scope: !1298)
!1317 = distinct !DISubprogram(name: "prjm_eval_func_bitwise_and", scope: !6, file: !6, line: 859, type: !21, scopeLine: 860, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1318)
!1318 = !{!1319, !1320, !1321, !1322, !1323, !1324}
!1319 = !DILocalVariable(name: "ctx", arg: 1, scope: !1317, file: !6, line: 859, type: !23)
!1320 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1317, file: !6, line: 859, type: !38)
!1321 = !DILocalVariable(name: "val1", scope: !1317, file: !6, line: 863, type: !11)
!1322 = !DILocalVariable(name: "val1_ptr", scope: !1317, file: !6, line: 864, type: !35)
!1323 = !DILocalVariable(name: "val2", scope: !1317, file: !6, line: 865, type: !11)
!1324 = !DILocalVariable(name: "val2_ptr", scope: !1317, file: !6, line: 866, type: !35)
!1325 = distinct !DIAssignID()
!1326 = !DILocation(line: 0, scope: !1317)
!1327 = distinct !DIAssignID()
!1328 = distinct !DIAssignID()
!1329 = distinct !DIAssignID()
!1330 = !DILocation(line: 863, column: 5, scope: !1317)
!1331 = !DILocation(line: 863, column: 17, scope: !1317)
!1332 = distinct !DIAssignID()
!1333 = !DILocation(line: 864, column: 5, scope: !1317)
!1334 = !DILocation(line: 864, column: 18, scope: !1317)
!1335 = distinct !DIAssignID()
!1336 = !DILocation(line: 865, column: 5, scope: !1317)
!1337 = !DILocation(line: 865, column: 17, scope: !1317)
!1338 = distinct !DIAssignID()
!1339 = !DILocation(line: 866, column: 5, scope: !1317)
!1340 = !DILocation(line: 866, column: 18, scope: !1317)
!1341 = distinct !DIAssignID()
!1342 = !DILocation(line: 868, column: 5, scope: !1317)
!1343 = !DILocation(line: 869, column: 5, scope: !1317)
!1344 = !DILocation(line: 871, column: 5, scope: !1317)
!1345 = !DILocation(line: 872, column: 1, scope: !1317)
!1346 = distinct !DISubprogram(name: "prjm_eval_func_mod_op", scope: !6, file: !6, line: 874, type: !21, scopeLine: 875, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1347)
!1347 = !{!1348, !1349, !1350, !1351}
!1348 = !DILocalVariable(name: "ctx", arg: 1, scope: !1346, file: !6, line: 874, type: !23)
!1349 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1346, file: !6, line: 874, type: !38)
!1350 = !DILocalVariable(name: "val2", scope: !1346, file: !6, line: 878, type: !11)
!1351 = !DILocalVariable(name: "val2_ptr", scope: !1346, file: !6, line: 879, type: !35)
!1352 = distinct !DIAssignID()
!1353 = !DILocation(line: 0, scope: !1346)
!1354 = distinct !DIAssignID()
!1355 = !DILocation(line: 878, column: 5, scope: !1346)
!1356 = !DILocation(line: 878, column: 17, scope: !1346)
!1357 = distinct !DIAssignID()
!1358 = !DILocation(line: 879, column: 5, scope: !1346)
!1359 = !DILocation(line: 879, column: 18, scope: !1346)
!1360 = distinct !DIAssignID()
!1361 = !DILocation(line: 881, column: 5, scope: !1346)
!1362 = !DILocation(line: 882, column: 5, scope: !1346)
!1363 = !DILocation(line: 884, column: 5, scope: !1346)
!1364 = !DILocation(line: 0, scope: !942, inlinedAt: !1365)
!1365 = distinct !DILocation(line: 884, column: 5, scope: !1346)
!1366 = !DILocation(line: 0, scope: !961, inlinedAt: !1367)
!1367 = distinct !DILocation(line: 620, column: 44, scope: !942, inlinedAt: !1365)
!1368 = !DILocation(line: 0, scope: !969, inlinedAt: !1369)
!1369 = distinct !DILocation(line: 612, column: 5, scope: !961, inlinedAt: !1367)
!1370 = !DILocation(line: 53, column: 12, scope: !969, inlinedAt: !1369)
!1371 = !DILocation(line: 0, scope: !961, inlinedAt: !1372)
!1372 = distinct !DILocation(line: 621, column: 46, scope: !942, inlinedAt: !1365)
!1373 = !DILocation(line: 0, scope: !969, inlinedAt: !1374)
!1374 = distinct !DILocation(line: 612, column: 5, scope: !961, inlinedAt: !1372)
!1375 = !DILocation(line: 53, column: 12, scope: !969, inlinedAt: !1374)
!1376 = !DILocation(line: 622, column: 63, scope: !942, inlinedAt: !1365)
!1377 = !DILocation(line: 623, column: 67, scope: !942, inlinedAt: !1365)
!1378 = !DILocation(line: 624, column: 55, scope: !994, inlinedAt: !1365)
!1379 = !DILocation(line: 629, column: 29, scope: !996, inlinedAt: !1365)
!1380 = !DILocation(line: 629, column: 58, scope: !996, inlinedAt: !1365)
!1381 = !DILocation(line: 629, column: 77, scope: !996, inlinedAt: !1365)
!1382 = !DILocation(line: 629, column: 100, scope: !996, inlinedAt: !1365)
!1383 = !DILocation(line: 630, column: 30, scope: !996, inlinedAt: !1365)
!1384 = !DILocation(line: 630, column: 58, scope: !996, inlinedAt: !1365)
!1385 = !DILocation(line: 631, column: 31, scope: !996, inlinedAt: !1365)
!1386 = !DILocation(line: 631, column: 60, scope: !996, inlinedAt: !1365)
!1387 = !DILocation(line: 633, column: 34, scope: !942, inlinedAt: !1365)
!1388 = !DILocation(line: 634, column: 33, scope: !942, inlinedAt: !1365)
!1389 = !DILocation(line: 640, column: 17, scope: !1007, inlinedAt: !1365)
!1390 = !DILocation(line: 640, column: 22, scope: !1007, inlinedAt: !1365)
!1391 = !DILocation(line: 640, column: 35, scope: !1007, inlinedAt: !1365)
!1392 = !DILocation(line: 640, column: 46, scope: !1007, inlinedAt: !1365)
!1393 = !DILocation(line: 642, column: 59, scope: !942, inlinedAt: !1365)
!1394 = !DILocation(line: 642, column: 35, scope: !942, inlinedAt: !1365)
!1395 = !DILocation(line: 643, column: 31, scope: !942, inlinedAt: !1365)
!1396 = !DILocation(line: 643, column: 63, scope: !942, inlinedAt: !1365)
!1397 = !DILocation(line: 885, column: 1, scope: !1346)
!1398 = distinct !DISubprogram(name: "prjm_eval_func_pow_op", scope: !6, file: !6, line: 887, type: !21, scopeLine: 888, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1399)
!1399 = !{!1400, !1401, !1402, !1403, !1404}
!1400 = !DILocalVariable(name: "ctx", arg: 1, scope: !1398, file: !6, line: 887, type: !23)
!1401 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1398, file: !6, line: 887, type: !38)
!1402 = !DILocalVariable(name: "val2", scope: !1398, file: !6, line: 891, type: !11)
!1403 = !DILocalVariable(name: "val2_ptr", scope: !1398, file: !6, line: 892, type: !35)
!1404 = !DILocalVariable(name: "result", scope: !1398, file: !6, line: 903, type: !11)
!1405 = distinct !DIAssignID()
!1406 = !DILocation(line: 0, scope: !1398)
!1407 = distinct !DIAssignID()
!1408 = !DILocation(line: 891, column: 5, scope: !1398)
!1409 = !DILocation(line: 891, column: 17, scope: !1398)
!1410 = distinct !DIAssignID()
!1411 = !DILocation(line: 892, column: 5, scope: !1398)
!1412 = !DILocation(line: 892, column: 18, scope: !1398)
!1413 = distinct !DIAssignID()
!1414 = !DILocation(line: 894, column: 5, scope: !1398)
!1415 = !DILocation(line: 895, column: 5, scope: !1398)
!1416 = !DILocation(line: 897, column: 14, scope: !1417)
!1417 = distinct !DILexicalBlock(scope: !1398, file: !6, line: 897, column: 8)
!1418 = !DILocation(line: 897, column: 13, scope: !1417)
!1419 = !DILocation(line: 897, column: 8, scope: !1417)
!1420 = !DILocation(line: 897, column: 24, scope: !1417)
!1421 = !DILocation(line: 903, column: 42, scope: !1398)
!1422 = !DILocation(line: 903, column: 41, scope: !1398)
!1423 = !DILocation(line: 897, column: 46, scope: !1417)
!1424 = !DILocation(line: 906, column: 1, scope: !1398)
!1425 = distinct !DISubprogram(name: "prjm_eval_func_sin", scope: !6, file: !6, line: 910, type: !21, scopeLine: 911, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1426)
!1426 = !{!1427, !1428, !1429}
!1427 = !DILocalVariable(name: "ctx", arg: 1, scope: !1425, file: !6, line: 910, type: !23)
!1428 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1425, file: !6, line: 910, type: !38)
!1429 = !DILocalVariable(name: "math_arg_ptr", scope: !1425, file: !6, line: 915, type: !35)
!1430 = distinct !DIAssignID()
!1431 = !DILocation(line: 0, scope: !1425)
!1432 = !DILocation(line: 914, column: 10, scope: !1425)
!1433 = !DILocation(line: 914, column: 16, scope: !1425)
!1434 = !DILocation(line: 915, column: 5, scope: !1425)
!1435 = !DILocation(line: 915, column: 18, scope: !1425)
!1436 = distinct !DIAssignID()
!1437 = !DILocation(line: 917, column: 5, scope: !1425)
!1438 = !DILocation(line: 919, column: 5, scope: !1425)
!1439 = !DILocation(line: 920, column: 1, scope: !1425)
!1440 = distinct !DISubprogram(name: "prjm_eval_func_cos", scope: !6, file: !6, line: 922, type: !21, scopeLine: 923, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1441)
!1441 = !{!1442, !1443, !1444}
!1442 = !DILocalVariable(name: "ctx", arg: 1, scope: !1440, file: !6, line: 922, type: !23)
!1443 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1440, file: !6, line: 922, type: !38)
!1444 = !DILocalVariable(name: "math_arg_ptr", scope: !1440, file: !6, line: 927, type: !35)
!1445 = distinct !DIAssignID()
!1446 = !DILocation(line: 0, scope: !1440)
!1447 = !DILocation(line: 926, column: 10, scope: !1440)
!1448 = !DILocation(line: 926, column: 16, scope: !1440)
!1449 = !DILocation(line: 927, column: 5, scope: !1440)
!1450 = !DILocation(line: 927, column: 18, scope: !1440)
!1451 = distinct !DIAssignID()
!1452 = !DILocation(line: 929, column: 5, scope: !1440)
!1453 = !DILocation(line: 931, column: 5, scope: !1440)
!1454 = !DILocation(line: 932, column: 1, scope: !1440)
!1455 = distinct !DISubprogram(name: "prjm_eval_func_tan", scope: !6, file: !6, line: 934, type: !21, scopeLine: 935, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1456)
!1456 = !{!1457, !1458, !1459}
!1457 = !DILocalVariable(name: "ctx", arg: 1, scope: !1455, file: !6, line: 934, type: !23)
!1458 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1455, file: !6, line: 934, type: !38)
!1459 = !DILocalVariable(name: "math_arg_ptr", scope: !1455, file: !6, line: 939, type: !35)
!1460 = distinct !DIAssignID()
!1461 = !DILocation(line: 0, scope: !1455)
!1462 = !DILocation(line: 938, column: 10, scope: !1455)
!1463 = !DILocation(line: 938, column: 16, scope: !1455)
!1464 = !DILocation(line: 939, column: 5, scope: !1455)
!1465 = !DILocation(line: 939, column: 18, scope: !1455)
!1466 = distinct !DIAssignID()
!1467 = !DILocation(line: 941, column: 5, scope: !1455)
!1468 = !DILocation(line: 943, column: 5, scope: !1455)
!1469 = !DILocation(line: 944, column: 1, scope: !1455)
!1470 = !DISubprogram(name: "tan", scope: !1471, file: !1471, line: 100, type: !1472, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1471 = !DIFile(filename: "Library/Android/sdk/ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/sysroot/usr/include/math.h", directory: "/Users/jneerdael")
!1472 = !DISubroutineType(types: !1473)
!1473 = !{!13, !13}
!1474 = distinct !DISubprogram(name: "prjm_eval_func_asin", scope: !6, file: !6, line: 946, type: !21, scopeLine: 947, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1475)
!1475 = !{!1476, !1477, !1478}
!1476 = !DILocalVariable(name: "ctx", arg: 1, scope: !1474, file: !6, line: 946, type: !23)
!1477 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1474, file: !6, line: 946, type: !38)
!1478 = !DILocalVariable(name: "math_arg_ptr", scope: !1474, file: !6, line: 951, type: !35)
!1479 = distinct !DIAssignID()
!1480 = !DILocation(line: 0, scope: !1474)
!1481 = !DILocation(line: 950, column: 10, scope: !1474)
!1482 = !DILocation(line: 950, column: 16, scope: !1474)
!1483 = !DILocation(line: 951, column: 5, scope: !1474)
!1484 = !DILocation(line: 951, column: 18, scope: !1474)
!1485 = distinct !DIAssignID()
!1486 = !DILocation(line: 953, column: 5, scope: !1474)
!1487 = !DILocation(line: 955, column: 10, scope: !1488)
!1488 = distinct !DILexicalBlock(scope: !1474, file: !6, line: 955, column: 9)
!1489 = !DILocation(line: 955, column: 9, scope: !1488)
!1490 = !DILocation(line: 955, column: 23, scope: !1488)
!1491 = !DILocation(line: 955, column: 30, scope: !1488)
!1492 = !DILocation(line: 961, column: 5, scope: !1474)
!1493 = !DILocation(line: 962, column: 1, scope: !1474)
!1494 = !DISubprogram(name: "asin", scope: !1471, file: !1471, line: 80, type: !1472, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1495 = distinct !DISubprogram(name: "prjm_eval_func_acos", scope: !6, file: !6, line: 964, type: !21, scopeLine: 965, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1496)
!1496 = !{!1497, !1498, !1499}
!1497 = !DILocalVariable(name: "ctx", arg: 1, scope: !1495, file: !6, line: 964, type: !23)
!1498 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1495, file: !6, line: 964, type: !38)
!1499 = !DILocalVariable(name: "math_arg_ptr", scope: !1495, file: !6, line: 969, type: !35)
!1500 = distinct !DIAssignID()
!1501 = !DILocation(line: 0, scope: !1495)
!1502 = !DILocation(line: 968, column: 10, scope: !1495)
!1503 = !DILocation(line: 968, column: 16, scope: !1495)
!1504 = !DILocation(line: 969, column: 5, scope: !1495)
!1505 = !DILocation(line: 969, column: 18, scope: !1495)
!1506 = distinct !DIAssignID()
!1507 = !DILocation(line: 971, column: 5, scope: !1495)
!1508 = !DILocation(line: 973, column: 10, scope: !1509)
!1509 = distinct !DILexicalBlock(scope: !1495, file: !6, line: 973, column: 9)
!1510 = !DILocation(line: 973, column: 9, scope: !1509)
!1511 = !DILocation(line: 973, column: 23, scope: !1509)
!1512 = !DILocation(line: 973, column: 30, scope: !1509)
!1513 = !DILocation(line: 979, column: 5, scope: !1495)
!1514 = !DILocation(line: 980, column: 1, scope: !1495)
!1515 = !DISubprogram(name: "acos", scope: !1471, file: !1471, line: 76, type: !1472, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1516 = distinct !DISubprogram(name: "prjm_eval_func_atan", scope: !6, file: !6, line: 982, type: !21, scopeLine: 983, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1517)
!1517 = !{!1518, !1519, !1520}
!1518 = !DILocalVariable(name: "ctx", arg: 1, scope: !1516, file: !6, line: 982, type: !23)
!1519 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1516, file: !6, line: 982, type: !38)
!1520 = !DILocalVariable(name: "math_arg_ptr", scope: !1516, file: !6, line: 987, type: !35)
!1521 = distinct !DIAssignID()
!1522 = !DILocation(line: 0, scope: !1516)
!1523 = !DILocation(line: 986, column: 10, scope: !1516)
!1524 = !DILocation(line: 986, column: 16, scope: !1516)
!1525 = !DILocation(line: 987, column: 5, scope: !1516)
!1526 = !DILocation(line: 987, column: 18, scope: !1516)
!1527 = distinct !DIAssignID()
!1528 = !DILocation(line: 989, column: 5, scope: !1516)
!1529 = !DILocation(line: 991, column: 5, scope: !1516)
!1530 = !DILocation(line: 992, column: 1, scope: !1516)
!1531 = !DISubprogram(name: "atan", scope: !1471, file: !1471, line: 84, type: !1472, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1532 = distinct !DISubprogram(name: "prjm_eval_func_atan2", scope: !6, file: !6, line: 994, type: !21, scopeLine: 995, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1533)
!1533 = !{!1534, !1535, !1536, !1537, !1538, !1539}
!1534 = !DILocalVariable(name: "ctx", arg: 1, scope: !1532, file: !6, line: 994, type: !23)
!1535 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1532, file: !6, line: 994, type: !38)
!1536 = !DILocalVariable(name: "math_arg1", scope: !1532, file: !6, line: 998, type: !11)
!1537 = !DILocalVariable(name: "math_arg2", scope: !1532, file: !6, line: 999, type: !11)
!1538 = !DILocalVariable(name: "math_arg1_ptr", scope: !1532, file: !6, line: 1000, type: !35)
!1539 = !DILocalVariable(name: "math_arg2_ptr", scope: !1532, file: !6, line: 1001, type: !35)
!1540 = distinct !DIAssignID()
!1541 = !DILocation(line: 0, scope: !1532)
!1542 = distinct !DIAssignID()
!1543 = distinct !DIAssignID()
!1544 = distinct !DIAssignID()
!1545 = !DILocation(line: 998, column: 5, scope: !1532)
!1546 = !DILocation(line: 998, column: 17, scope: !1532)
!1547 = distinct !DIAssignID()
!1548 = !DILocation(line: 999, column: 5, scope: !1532)
!1549 = !DILocation(line: 999, column: 17, scope: !1532)
!1550 = distinct !DIAssignID()
!1551 = !DILocation(line: 1000, column: 5, scope: !1532)
!1552 = !DILocation(line: 1000, column: 18, scope: !1532)
!1553 = distinct !DIAssignID()
!1554 = !DILocation(line: 1001, column: 5, scope: !1532)
!1555 = !DILocation(line: 1001, column: 18, scope: !1532)
!1556 = distinct !DIAssignID()
!1557 = !DILocation(line: 1003, column: 5, scope: !1532)
!1558 = !DILocation(line: 1004, column: 5, scope: !1532)
!1559 = !DILocation(line: 1006, column: 5, scope: !1532)
!1560 = !DILocation(line: 1007, column: 1, scope: !1532)
!1561 = !DISubprogram(name: "atan2", scope: !1471, file: !1471, line: 88, type: !1562, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1562 = !DISubroutineType(types: !1563)
!1563 = !{!13, !13, !13}
!1564 = distinct !DISubprogram(name: "prjm_eval_func_sqrt", scope: !6, file: !6, line: 1009, type: !21, scopeLine: 1010, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1565)
!1565 = !{!1566, !1567, !1568}
!1566 = !DILocalVariable(name: "ctx", arg: 1, scope: !1564, file: !6, line: 1009, type: !23)
!1567 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1564, file: !6, line: 1009, type: !38)
!1568 = !DILocalVariable(name: "math_arg_ptr", scope: !1564, file: !6, line: 1014, type: !35)
!1569 = distinct !DIAssignID()
!1570 = !DILocation(line: 0, scope: !1564)
!1571 = !DILocation(line: 1013, column: 10, scope: !1564)
!1572 = !DILocation(line: 1013, column: 16, scope: !1564)
!1573 = !DILocation(line: 1014, column: 5, scope: !1564)
!1574 = !DILocation(line: 1014, column: 18, scope: !1564)
!1575 = distinct !DIAssignID()
!1576 = !DILocation(line: 1016, column: 5, scope: !1564)
!1577 = !DILocation(line: 1018, column: 5, scope: !1564)
!1578 = !DILocation(line: 1019, column: 1, scope: !1564)
!1579 = distinct !DISubprogram(name: "prjm_eval_func_pow", scope: !6, file: !6, line: 1021, type: !21, scopeLine: 1022, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1580)
!1580 = !{!1581, !1582, !1583, !1584, !1585, !1586, !1587}
!1581 = !DILocalVariable(name: "ctx", arg: 1, scope: !1579, file: !6, line: 1021, type: !23)
!1582 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1579, file: !6, line: 1021, type: !38)
!1583 = !DILocalVariable(name: "math_arg1", scope: !1579, file: !6, line: 1025, type: !11)
!1584 = !DILocalVariable(name: "math_arg2", scope: !1579, file: !6, line: 1026, type: !11)
!1585 = !DILocalVariable(name: "math_arg1_ptr", scope: !1579, file: !6, line: 1027, type: !35)
!1586 = !DILocalVariable(name: "math_arg2_ptr", scope: !1579, file: !6, line: 1028, type: !35)
!1587 = !DILocalVariable(name: "result", scope: !1579, file: !6, line: 1039, type: !11)
!1588 = distinct !DIAssignID()
!1589 = !DILocation(line: 0, scope: !1579)
!1590 = distinct !DIAssignID()
!1591 = distinct !DIAssignID()
!1592 = distinct !DIAssignID()
!1593 = !DILocation(line: 1025, column: 5, scope: !1579)
!1594 = !DILocation(line: 1025, column: 17, scope: !1579)
!1595 = distinct !DIAssignID()
!1596 = !DILocation(line: 1026, column: 5, scope: !1579)
!1597 = !DILocation(line: 1026, column: 17, scope: !1579)
!1598 = distinct !DIAssignID()
!1599 = !DILocation(line: 1027, column: 5, scope: !1579)
!1600 = !DILocation(line: 1027, column: 18, scope: !1579)
!1601 = distinct !DIAssignID()
!1602 = !DILocation(line: 1028, column: 5, scope: !1579)
!1603 = !DILocation(line: 1028, column: 18, scope: !1579)
!1604 = distinct !DIAssignID()
!1605 = !DILocation(line: 1030, column: 5, scope: !1579)
!1606 = !DILocation(line: 1031, column: 5, scope: !1579)
!1607 = !DILocation(line: 1033, column: 15, scope: !1608)
!1608 = distinct !DILexicalBlock(scope: !1579, file: !6, line: 1033, column: 9)
!1609 = !DILocation(line: 1033, column: 14, scope: !1608)
!1610 = !DILocation(line: 1033, column: 9, scope: !1608)
!1611 = !DILocation(line: 1033, column: 30, scope: !1608)
!1612 = !DILocation(line: 1039, column: 47, scope: !1579)
!1613 = !DILocation(line: 1039, column: 46, scope: !1579)
!1614 = !DILocation(line: 1033, column: 52, scope: !1608)
!1615 = !DILocation(line: 1042, column: 1, scope: !1579)
!1616 = distinct !DISubprogram(name: "prjm_eval_func_exp", scope: !6, file: !6, line: 1044, type: !21, scopeLine: 1045, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1617)
!1617 = !{!1618, !1619, !1620}
!1618 = !DILocalVariable(name: "ctx", arg: 1, scope: !1616, file: !6, line: 1044, type: !23)
!1619 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1616, file: !6, line: 1044, type: !38)
!1620 = !DILocalVariable(name: "math_arg_ptr", scope: !1616, file: !6, line: 1049, type: !35)
!1621 = distinct !DIAssignID()
!1622 = !DILocation(line: 0, scope: !1616)
!1623 = !DILocation(line: 1048, column: 10, scope: !1616)
!1624 = !DILocation(line: 1048, column: 16, scope: !1616)
!1625 = !DILocation(line: 1049, column: 5, scope: !1616)
!1626 = !DILocation(line: 1049, column: 18, scope: !1616)
!1627 = distinct !DIAssignID()
!1628 = !DILocation(line: 1051, column: 5, scope: !1616)
!1629 = !DILocation(line: 1053, column: 5, scope: !1616)
!1630 = !DILocation(line: 1054, column: 1, scope: !1616)
!1631 = distinct !DISubprogram(name: "prjm_eval_func_log", scope: !6, file: !6, line: 1056, type: !21, scopeLine: 1057, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1632)
!1632 = !{!1633, !1634, !1635}
!1633 = !DILocalVariable(name: "ctx", arg: 1, scope: !1631, file: !6, line: 1056, type: !23)
!1634 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1631, file: !6, line: 1056, type: !38)
!1635 = !DILocalVariable(name: "math_arg_ptr", scope: !1631, file: !6, line: 1061, type: !35)
!1636 = distinct !DIAssignID()
!1637 = !DILocation(line: 0, scope: !1631)
!1638 = !DILocation(line: 1060, column: 10, scope: !1631)
!1639 = !DILocation(line: 1060, column: 16, scope: !1631)
!1640 = !DILocation(line: 1061, column: 5, scope: !1631)
!1641 = !DILocation(line: 1061, column: 18, scope: !1631)
!1642 = distinct !DIAssignID()
!1643 = !DILocation(line: 1063, column: 5, scope: !1631)
!1644 = !DILocation(line: 1065, column: 10, scope: !1645)
!1645 = distinct !DILexicalBlock(scope: !1631, file: !6, line: 1065, column: 9)
!1646 = !DILocation(line: 1065, column: 9, scope: !1645)
!1647 = !DILocation(line: 1065, column: 23, scope: !1645)
!1648 = !DILocation(line: 1065, column: 9, scope: !1631)
!1649 = !DILocation(line: 1072, column: 1, scope: !1631)
!1650 = distinct !DISubprogram(name: "prjm_eval_func_log10", scope: !6, file: !6, line: 1074, type: !21, scopeLine: 1075, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1651)
!1651 = !{!1652, !1653, !1654}
!1652 = !DILocalVariable(name: "ctx", arg: 1, scope: !1650, file: !6, line: 1074, type: !23)
!1653 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1650, file: !6, line: 1074, type: !38)
!1654 = !DILocalVariable(name: "math_arg_ptr", scope: !1650, file: !6, line: 1079, type: !35)
!1655 = distinct !DIAssignID()
!1656 = !DILocation(line: 0, scope: !1650)
!1657 = !DILocation(line: 1078, column: 10, scope: !1650)
!1658 = !DILocation(line: 1078, column: 16, scope: !1650)
!1659 = !DILocation(line: 1079, column: 5, scope: !1650)
!1660 = !DILocation(line: 1079, column: 18, scope: !1650)
!1661 = distinct !DIAssignID()
!1662 = !DILocation(line: 1081, column: 5, scope: !1650)
!1663 = !DILocation(line: 1083, column: 10, scope: !1664)
!1664 = distinct !DILexicalBlock(scope: !1650, file: !6, line: 1083, column: 9)
!1665 = !DILocation(line: 1083, column: 9, scope: !1664)
!1666 = !DILocation(line: 1083, column: 23, scope: !1664)
!1667 = !DILocation(line: 1083, column: 9, scope: !1650)
!1668 = !DILocation(line: 1090, column: 1, scope: !1650)
!1669 = distinct !DISubprogram(name: "prjm_eval_func_floor", scope: !6, file: !6, line: 1092, type: !21, scopeLine: 1093, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1670)
!1670 = !{!1671, !1672, !1673}
!1671 = !DILocalVariable(name: "ctx", arg: 1, scope: !1669, file: !6, line: 1092, type: !23)
!1672 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1669, file: !6, line: 1092, type: !38)
!1673 = !DILocalVariable(name: "math_arg_ptr", scope: !1669, file: !6, line: 1097, type: !35)
!1674 = distinct !DIAssignID()
!1675 = !DILocation(line: 0, scope: !1669)
!1676 = !DILocation(line: 1096, column: 10, scope: !1669)
!1677 = !DILocation(line: 1096, column: 16, scope: !1669)
!1678 = !DILocation(line: 1097, column: 5, scope: !1669)
!1679 = !DILocation(line: 1097, column: 18, scope: !1669)
!1680 = distinct !DIAssignID()
!1681 = !DILocation(line: 1099, column: 5, scope: !1669)
!1682 = !DILocation(line: 1101, column: 5, scope: !1669)
!1683 = !DILocation(line: 1102, column: 1, scope: !1669)
!1684 = distinct !DISubprogram(name: "prjm_eval_func_ceil", scope: !6, file: !6, line: 1104, type: !21, scopeLine: 1105, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1685)
!1685 = !{!1686, !1687, !1688}
!1686 = !DILocalVariable(name: "ctx", arg: 1, scope: !1684, file: !6, line: 1104, type: !23)
!1687 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1684, file: !6, line: 1104, type: !38)
!1688 = !DILocalVariable(name: "math_arg_ptr", scope: !1684, file: !6, line: 1109, type: !35)
!1689 = distinct !DIAssignID()
!1690 = !DILocation(line: 0, scope: !1684)
!1691 = !DILocation(line: 1108, column: 10, scope: !1684)
!1692 = !DILocation(line: 1108, column: 16, scope: !1684)
!1693 = !DILocation(line: 1109, column: 5, scope: !1684)
!1694 = !DILocation(line: 1109, column: 18, scope: !1684)
!1695 = distinct !DIAssignID()
!1696 = !DILocation(line: 1111, column: 5, scope: !1684)
!1697 = !DILocation(line: 1113, column: 5, scope: !1684)
!1698 = !DILocation(line: 1114, column: 1, scope: !1684)
!1699 = distinct !DISubprogram(name: "prjm_eval_func_sigmoid", scope: !6, file: !6, line: 1116, type: !21, scopeLine: 1117, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1700)
!1700 = !{!1701, !1702, !1703, !1704, !1705, !1706, !1707}
!1701 = !DILocalVariable(name: "ctx", arg: 1, scope: !1699, file: !6, line: 1116, type: !23)
!1702 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1699, file: !6, line: 1116, type: !38)
!1703 = !DILocalVariable(name: "math_arg1", scope: !1699, file: !6, line: 1120, type: !11)
!1704 = !DILocalVariable(name: "math_arg2", scope: !1699, file: !6, line: 1121, type: !11)
!1705 = !DILocalVariable(name: "math_arg1_ptr", scope: !1699, file: !6, line: 1122, type: !35)
!1706 = !DILocalVariable(name: "math_arg2_ptr", scope: !1699, file: !6, line: 1123, type: !35)
!1707 = !DILocalVariable(name: "t", scope: !1699, file: !6, line: 1128, type: !13)
!1708 = distinct !DIAssignID()
!1709 = !DILocation(line: 0, scope: !1699)
!1710 = distinct !DIAssignID()
!1711 = distinct !DIAssignID()
!1712 = distinct !DIAssignID()
!1713 = !DILocation(line: 1120, column: 5, scope: !1699)
!1714 = !DILocation(line: 1120, column: 17, scope: !1699)
!1715 = distinct !DIAssignID()
!1716 = !DILocation(line: 1121, column: 5, scope: !1699)
!1717 = !DILocation(line: 1121, column: 17, scope: !1699)
!1718 = distinct !DIAssignID()
!1719 = !DILocation(line: 1122, column: 5, scope: !1699)
!1720 = !DILocation(line: 1122, column: 18, scope: !1699)
!1721 = distinct !DIAssignID()
!1722 = !DILocation(line: 1123, column: 5, scope: !1699)
!1723 = !DILocation(line: 1123, column: 18, scope: !1699)
!1724 = distinct !DIAssignID()
!1725 = !DILocation(line: 1125, column: 5, scope: !1699)
!1726 = !DILocation(line: 1126, column: 5, scope: !1699)
!1727 = !DILocation(line: 1128, column: 37, scope: !1699)
!1728 = !DILocation(line: 1128, column: 36, scope: !1699)
!1729 = !DILocation(line: 1128, column: 34, scope: !1699)
!1730 = !DILocation(line: 1128, column: 56, scope: !1699)
!1731 = !DILocation(line: 1128, column: 55, scope: !1699)
!1732 = !DILocation(line: 1128, column: 52, scope: !1699)
!1733 = !DILocation(line: 1128, column: 21, scope: !1699)
!1734 = !DILocation(line: 1128, column: 19, scope: !1699)
!1735 = !DILocation(line: 1129, column: 5, scope: !1699)
!1736 = !DILocation(line: 1130, column: 1, scope: !1699)
!1737 = distinct !DISubprogram(name: "prjm_eval_func_sqr", scope: !6, file: !6, line: 1132, type: !21, scopeLine: 1133, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1738)
!1738 = !{!1739, !1740, !1741}
!1739 = !DILocalVariable(name: "ctx", arg: 1, scope: !1737, file: !6, line: 1132, type: !23)
!1740 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1737, file: !6, line: 1132, type: !38)
!1741 = !DILocalVariable(name: "value_ptr", scope: !1737, file: !6, line: 1137, type: !35)
!1742 = distinct !DIAssignID()
!1743 = !DILocation(line: 0, scope: !1737)
!1744 = !DILocation(line: 1136, column: 10, scope: !1737)
!1745 = !DILocation(line: 1136, column: 16, scope: !1737)
!1746 = !DILocation(line: 1137, column: 5, scope: !1737)
!1747 = !DILocation(line: 1137, column: 18, scope: !1737)
!1748 = distinct !DIAssignID()
!1749 = !DILocation(line: 1139, column: 5, scope: !1737)
!1750 = !DILocation(line: 1141, column: 5, scope: !1737)
!1751 = !DILocation(line: 1142, column: 1, scope: !1737)
!1752 = distinct !DISubprogram(name: "prjm_eval_func_abs", scope: !6, file: !6, line: 1144, type: !21, scopeLine: 1145, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1753)
!1753 = !{!1754, !1755, !1756}
!1754 = !DILocalVariable(name: "ctx", arg: 1, scope: !1752, file: !6, line: 1144, type: !23)
!1755 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1752, file: !6, line: 1144, type: !38)
!1756 = !DILocalVariable(name: "value_ptr", scope: !1752, file: !6, line: 1149, type: !35)
!1757 = distinct !DIAssignID()
!1758 = !DILocation(line: 0, scope: !1752)
!1759 = !DILocation(line: 1148, column: 10, scope: !1752)
!1760 = !DILocation(line: 1148, column: 16, scope: !1752)
!1761 = !DILocation(line: 1149, column: 5, scope: !1752)
!1762 = !DILocation(line: 1149, column: 18, scope: !1752)
!1763 = distinct !DIAssignID()
!1764 = !DILocation(line: 1151, column: 5, scope: !1752)
!1765 = !DILocation(line: 1153, column: 5, scope: !1752)
!1766 = !DILocation(line: 1154, column: 1, scope: !1752)
!1767 = distinct !DISubprogram(name: "prjm_eval_func_min", scope: !6, file: !6, line: 1156, type: !21, scopeLine: 1157, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1768)
!1768 = !{!1769, !1770, !1771, !1772, !1773, !1774}
!1769 = !DILocalVariable(name: "ctx", arg: 1, scope: !1767, file: !6, line: 1156, type: !23)
!1770 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1767, file: !6, line: 1156, type: !38)
!1771 = !DILocalVariable(name: "math_arg1", scope: !1767, file: !6, line: 1160, type: !11)
!1772 = !DILocalVariable(name: "math_arg2", scope: !1767, file: !6, line: 1161, type: !11)
!1773 = !DILocalVariable(name: "math_arg1_ptr", scope: !1767, file: !6, line: 1162, type: !35)
!1774 = !DILocalVariable(name: "math_arg2_ptr", scope: !1767, file: !6, line: 1163, type: !35)
!1775 = distinct !DIAssignID()
!1776 = !DILocation(line: 0, scope: !1767)
!1777 = distinct !DIAssignID()
!1778 = distinct !DIAssignID()
!1779 = distinct !DIAssignID()
!1780 = !DILocation(line: 1160, column: 5, scope: !1767)
!1781 = !DILocation(line: 1160, column: 17, scope: !1767)
!1782 = distinct !DIAssignID()
!1783 = !DILocation(line: 1161, column: 5, scope: !1767)
!1784 = !DILocation(line: 1161, column: 17, scope: !1767)
!1785 = distinct !DIAssignID()
!1786 = !DILocation(line: 1162, column: 5, scope: !1767)
!1787 = !DILocation(line: 1162, column: 18, scope: !1767)
!1788 = distinct !DIAssignID()
!1789 = !DILocation(line: 1163, column: 5, scope: !1767)
!1790 = !DILocation(line: 1163, column: 18, scope: !1767)
!1791 = distinct !DIAssignID()
!1792 = !DILocation(line: 1165, column: 5, scope: !1767)
!1793 = !DILocation(line: 1166, column: 5, scope: !1767)
!1794 = !DILocation(line: 1168, column: 5, scope: !1767)
!1795 = !DILocation(line: 1169, column: 1, scope: !1767)
!1796 = distinct !DISubprogram(name: "prjm_eval_func_max", scope: !6, file: !6, line: 1171, type: !21, scopeLine: 1172, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1797)
!1797 = !{!1798, !1799, !1800, !1801, !1802, !1803}
!1798 = !DILocalVariable(name: "ctx", arg: 1, scope: !1796, file: !6, line: 1171, type: !23)
!1799 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1796, file: !6, line: 1171, type: !38)
!1800 = !DILocalVariable(name: "math_arg1", scope: !1796, file: !6, line: 1175, type: !11)
!1801 = !DILocalVariable(name: "math_arg2", scope: !1796, file: !6, line: 1176, type: !11)
!1802 = !DILocalVariable(name: "math_arg1_ptr", scope: !1796, file: !6, line: 1177, type: !35)
!1803 = !DILocalVariable(name: "math_arg2_ptr", scope: !1796, file: !6, line: 1178, type: !35)
!1804 = distinct !DIAssignID()
!1805 = !DILocation(line: 0, scope: !1796)
!1806 = distinct !DIAssignID()
!1807 = distinct !DIAssignID()
!1808 = distinct !DIAssignID()
!1809 = !DILocation(line: 1175, column: 5, scope: !1796)
!1810 = !DILocation(line: 1175, column: 17, scope: !1796)
!1811 = distinct !DIAssignID()
!1812 = !DILocation(line: 1176, column: 5, scope: !1796)
!1813 = !DILocation(line: 1176, column: 17, scope: !1796)
!1814 = distinct !DIAssignID()
!1815 = !DILocation(line: 1177, column: 5, scope: !1796)
!1816 = !DILocation(line: 1177, column: 18, scope: !1796)
!1817 = distinct !DIAssignID()
!1818 = !DILocation(line: 1178, column: 5, scope: !1796)
!1819 = !DILocation(line: 1178, column: 18, scope: !1796)
!1820 = distinct !DIAssignID()
!1821 = !DILocation(line: 1180, column: 5, scope: !1796)
!1822 = !DILocation(line: 1181, column: 5, scope: !1796)
!1823 = !DILocation(line: 1183, column: 5, scope: !1796)
!1824 = !DILocation(line: 1184, column: 1, scope: !1796)
!1825 = distinct !DISubprogram(name: "prjm_eval_func_sign", scope: !6, file: !6, line: 1186, type: !21, scopeLine: 1187, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1826)
!1826 = !{!1827, !1828, !1829}
!1827 = !DILocalVariable(name: "ctx", arg: 1, scope: !1825, file: !6, line: 1186, type: !23)
!1828 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1825, file: !6, line: 1186, type: !38)
!1829 = !DILocalVariable(name: "value_ptr", scope: !1825, file: !6, line: 1191, type: !35)
!1830 = distinct !DIAssignID()
!1831 = !DILocation(line: 0, scope: !1825)
!1832 = !DILocation(line: 1190, column: 10, scope: !1825)
!1833 = !DILocation(line: 1190, column: 16, scope: !1825)
!1834 = !DILocation(line: 1191, column: 5, scope: !1825)
!1835 = !DILocation(line: 1191, column: 18, scope: !1825)
!1836 = distinct !DIAssignID()
!1837 = !DILocation(line: 1193, column: 5, scope: !1825)
!1838 = !DILocation(line: 1195, column: 10, scope: !1839)
!1839 = distinct !DILexicalBlock(scope: !1825, file: !6, line: 1195, column: 9)
!1840 = !DILocation(line: 1195, column: 9, scope: !1839)
!1841 = !DILocation(line: 1195, column: 20, scope: !1839)
!1842 = !DILocation(line: 1195, column: 9, scope: !1825)
!1843 = !DILocation(line: 1201, column: 1, scope: !1825)
!1844 = distinct !DISubprogram(name: "prjm_eval_func_rand", scope: !6, file: !6, line: 1203, type: !21, scopeLine: 1204, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1845)
!1845 = !{!1846, !1847, !1848, !1849}
!1846 = !DILocalVariable(name: "ctx", arg: 1, scope: !1844, file: !6, line: 1203, type: !23)
!1847 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1844, file: !6, line: 1203, type: !38)
!1848 = !DILocalVariable(name: "value_ptr", scope: !1844, file: !6, line: 1208, type: !35)
!1849 = !DILocalVariable(name: "rand_max", scope: !1844, file: !6, line: 1212, type: !11)
!1850 = distinct !DIAssignID()
!1851 = !DILocation(line: 0, scope: !1844)
!1852 = !DILocation(line: 1207, column: 10, scope: !1844)
!1853 = !DILocation(line: 1207, column: 16, scope: !1844)
!1854 = !DILocation(line: 1208, column: 5, scope: !1844)
!1855 = !DILocation(line: 1208, column: 18, scope: !1844)
!1856 = distinct !DIAssignID()
!1857 = !DILocation(line: 1210, column: 5, scope: !1844)
!1858 = !DILocation(line: 1212, column: 35, scope: !1844)
!1859 = !DILocation(line: 1212, column: 34, scope: !1844)
!1860 = !DILocation(line: 169, column: 10, scope: !246, inlinedAt: !1861)
!1861 = distinct !DILocation(line: 1218, column: 5, scope: !1844)
!1862 = !DILocation(line: 169, column: 9, scope: !236, inlinedAt: !1861)
!1863 = !DILocation(line: 0, scope: !245, inlinedAt: !1861)
!1864 = !DILocation(line: 172, column: 9, scope: !245, inlinedAt: !1861)
!1865 = !DILocation(line: 172, column: 15, scope: !245, inlinedAt: !1861)
!1866 = !DILocation(line: 173, scope: !1867, inlinedAt: !1861)
!1867 = distinct !DILexicalBlock(scope: !245, file: !6, line: 173, column: 9)
!1868 = !DILocation(line: 173, column: 9, scope: !1867, inlinedAt: !1861)
!1869 = !DILocation(line: 176, column: 41, scope: !1870, inlinedAt: !1861)
!1870 = distinct !DILexicalBlock(scope: !1871, file: !6, line: 174, column: 9)
!1871 = distinct !DILexicalBlock(scope: !1867, file: !6, line: 173, column: 9)
!1872 = !DILocation(line: 176, column: 34, scope: !1870, inlinedAt: !1861)
!1873 = !DILocation(line: 176, column: 61, scope: !1870, inlinedAt: !1861)
!1874 = !DILocation(line: 176, column: 46, scope: !1870, inlinedAt: !1861)
!1875 = !DILocation(line: 176, column: 31, scope: !1870, inlinedAt: !1861)
!1876 = !DILocation(line: 176, column: 71, scope: !1870, inlinedAt: !1861)
!1877 = !DILocation(line: 176, column: 69, scope: !1870, inlinedAt: !1861)
!1878 = !DILocation(line: 175, column: 13, scope: !1870, inlinedAt: !1861)
!1879 = !DILocation(line: 175, column: 21, scope: !1870, inlinedAt: !1861)
!1880 = !DILocation(line: 173, column: 35, scope: !1871, inlinedAt: !1861)
!1881 = !DILocation(line: 173, column: 27, scope: !1871, inlinedAt: !1861)
!1882 = distinct !{!1882, !1868, !1883, !349}
!1883 = !DILocation(line: 184, column: 9, scope: !1867, inlinedAt: !1861)
!1884 = !DILocation(line: 187, column: 13, scope: !249, inlinedAt: !1861)
!1885 = !DILocation(line: 187, column: 9, scope: !236, inlinedAt: !1861)
!1886 = !DILocation(line: 0, scope: !248, inlinedAt: !1861)
!1887 = !DILocation(line: 193, column: 18, scope: !1888, inlinedAt: !1861)
!1888 = distinct !DILexicalBlock(scope: !1889, file: !6, line: 192, column: 9)
!1889 = distinct !DILexicalBlock(scope: !1890, file: !6, line: 191, column: 9)
!1890 = distinct !DILexicalBlock(scope: !248, file: !6, line: 191, column: 9)
!1891 = !DILocation(line: 191, column: 9, scope: !1890, inlinedAt: !1861)
!1892 = !DILocation(line: 193, column: 48, scope: !1888, inlinedAt: !1861)
!1893 = !DILocation(line: 193, column: 42, scope: !1888, inlinedAt: !1861)
!1894 = !DILocation(line: 193, column: 25, scope: !1888, inlinedAt: !1861)
!1895 = !DILocation(line: 193, column: 53, scope: !1888, inlinedAt: !1861)
!1896 = !DILocation(line: 193, column: 39, scope: !1888, inlinedAt: !1861)
!1897 = !DILocation(line: 194, column: 28, scope: !1888, inlinedAt: !1861)
!1898 = !DILocation(line: 194, column: 22, scope: !1888, inlinedAt: !1861)
!1899 = !DILocation(line: 194, column: 38, scope: !1888, inlinedAt: !1861)
!1900 = !DILocation(line: 194, column: 54, scope: !1888, inlinedAt: !1861)
!1901 = !DILocation(line: 194, column: 46, scope: !1888, inlinedAt: !1861)
!1902 = !DILocation(line: 194, column: 33, scope: !1888, inlinedAt: !1861)
!1903 = !DILocation(line: 194, column: 44, scope: !1888, inlinedAt: !1861)
!1904 = !DILocation(line: 194, column: 20, scope: !1888, inlinedAt: !1861)
!1905 = distinct !{!1905, !1891, !1906, !349, !1907, !1908}
!1906 = !DILocation(line: 195, column: 9, scope: !1890, inlinedAt: !1861)
!1907 = !{!"llvm.loop.isvectorized", i32 1}
!1908 = !{!"llvm.loop.unroll.runtime.disable"}
!1909 = !DILocation(line: 0, scope: !236, inlinedAt: !1861)
!1910 = !DILocation(line: 198, column: 18, scope: !1911, inlinedAt: !1861)
!1911 = distinct !DILexicalBlock(scope: !1912, file: !6, line: 197, column: 9)
!1912 = distinct !DILexicalBlock(scope: !1913, file: !6, line: 196, column: 9)
!1913 = distinct !DILexicalBlock(scope: !248, file: !6, line: 196, column: 9)
!1914 = !DILocation(line: 196, column: 9, scope: !1913, inlinedAt: !1861)
!1915 = !DILocation(line: 198, column: 25, scope: !1911, inlinedAt: !1861)
!1916 = !DILocation(line: 198, column: 48, scope: !1911, inlinedAt: !1861)
!1917 = !DILocation(line: 198, column: 42, scope: !1911, inlinedAt: !1861)
!1918 = !DILocation(line: 198, column: 53, scope: !1911, inlinedAt: !1861)
!1919 = !DILocation(line: 198, column: 39, scope: !1911, inlinedAt: !1861)
!1920 = !DILocation(line: 199, column: 28, scope: !1911, inlinedAt: !1861)
!1921 = !DILocation(line: 199, column: 22, scope: !1911, inlinedAt: !1861)
!1922 = !DILocation(line: 199, column: 44, scope: !1911, inlinedAt: !1861)
!1923 = !DILocation(line: 199, column: 60, scope: !1911, inlinedAt: !1861)
!1924 = !DILocation(line: 199, column: 52, scope: !1911, inlinedAt: !1861)
!1925 = !DILocation(line: 199, column: 39, scope: !1911, inlinedAt: !1861)
!1926 = !DILocation(line: 199, column: 50, scope: !1911, inlinedAt: !1861)
!1927 = !DILocation(line: 199, column: 20, scope: !1911, inlinedAt: !1861)
!1928 = !DILocation(line: 196, column: 19, scope: !1912, inlinedAt: !1861)
!1929 = distinct !{!1929, !1914, !1930, !349}
!1930 = !DILocation(line: 200, column: 9, scope: !1913, inlinedAt: !1861)
!1931 = !DILocation(line: 201, column: 14, scope: !248, inlinedAt: !1861)
!1932 = !DILocation(line: 201, column: 24, scope: !248, inlinedAt: !1861)
!1933 = !DILocation(line: 201, column: 41, scope: !248, inlinedAt: !1861)
!1934 = !DILocation(line: 201, column: 47, scope: !248, inlinedAt: !1861)
!1935 = !DILocation(line: 201, column: 38, scope: !248, inlinedAt: !1861)
!1936 = !DILocation(line: 202, column: 21, scope: !248, inlinedAt: !1861)
!1937 = !DILocation(line: 202, column: 36, scope: !248, inlinedAt: !1861)
!1938 = !DILocation(line: 202, column: 52, scope: !248, inlinedAt: !1861)
!1939 = !DILocation(line: 202, column: 44, scope: !248, inlinedAt: !1861)
!1940 = !DILocation(line: 202, column: 31, scope: !248, inlinedAt: !1861)
!1941 = !DILocation(line: 202, column: 42, scope: !248, inlinedAt: !1861)
!1942 = !DILocation(line: 202, column: 19, scope: !248, inlinedAt: !1861)
!1943 = !DILocation(line: 205, column: 5, scope: !248, inlinedAt: !1861)
!1944 = !DILocation(line: 207, column: 9, scope: !236, inlinedAt: !1861)
!1945 = !DILocation(line: 207, column: 15, scope: !236, inlinedAt: !1861)
!1946 = !DILocation(line: 1212, column: 28, scope: !1844)
!1947 = !DILocation(line: 1213, column: 18, scope: !1948)
!1948 = distinct !DILexicalBlock(scope: !1844, file: !6, line: 1213, column: 9)
!1949 = !DILocation(line: 1213, column: 9, scope: !1844)
!1950 = !DILocation(line: 210, column: 13, scope: !236, inlinedAt: !1861)
!1951 = !DILocation(line: 210, column: 7, scope: !236, inlinedAt: !1861)
!1952 = !DILocation(line: 211, column: 13, scope: !236, inlinedAt: !1861)
!1953 = !DILocation(line: 211, column: 19, scope: !236, inlinedAt: !1861)
!1954 = !DILocation(line: 211, column: 7, scope: !236, inlinedAt: !1861)
!1955 = !DILocation(line: 212, column: 13, scope: !236, inlinedAt: !1861)
!1956 = !DILocation(line: 212, column: 20, scope: !236, inlinedAt: !1861)
!1957 = !DILocation(line: 212, column: 7, scope: !236, inlinedAt: !1861)
!1958 = !DILocation(line: 213, column: 13, scope: !236, inlinedAt: !1861)
!1959 = !DILocation(line: 213, column: 7, scope: !236, inlinedAt: !1861)
!1960 = !DILocation(line: 1218, column: 5, scope: !1844)
!1961 = !DILocation(line: 1219, column: 1, scope: !1844)
!1962 = distinct !DIAssignID()
!1963 = !DILocation(line: 0, scope: !20)
!1964 = !DILocation(line: 1247, column: 10, scope: !20)
!1965 = !DILocation(line: 1247, column: 16, scope: !20)
!1966 = !DILocation(line: 1248, column: 5, scope: !20)
!1967 = !DILocation(line: 1248, column: 18, scope: !20)
!1968 = distinct !DIAssignID()
!1969 = !DILocation(line: 1250, column: 5, scope: !20)
!1970 = !DILocation(line: 1252, column: 26, scope: !20)
!1971 = !DILocation(line: 1252, column: 25, scope: !20)
!1972 = !DILocation(line: 1254, column: 59, scope: !20)
!1973 = !DILocation(line: 1254, column: 67, scope: !20)
!1974 = !DILocation(line: 1254, column: 46, scope: !20)
!1975 = !DILocation(line: 1254, column: 23, scope: !20)
!1976 = !DILocation(line: 1255, column: 95, scope: !20)
!1977 = !DILocation(line: 1255, column: 64, scope: !20)
!1978 = !DILocation(line: 1255, column: 49, scope: !20)
!1979 = !DILocation(line: 1257, column: 5, scope: !20)
!1980 = !DILocation(line: 1258, column: 1, scope: !20)
