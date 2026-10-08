; ModuleID = '/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit/i04-bits-v3-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c'
source_filename = "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit/i04-bits-v3-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c"
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
  call void @llvm.dbg.value(metadata double %16, metadata !941, metadata !DIExpression()), !dbg !964
  call void @llvm.dbg.value(metadata double %18, metadata !946, metadata !DIExpression()), !dbg !964
  call void @llvm.dbg.value(metadata double %16, metadata !966, metadata !DIExpression()), !dbg !972
  call void @llvm.dbg.value(metadata ptr undef, metadata !974, metadata !DIExpression()), !dbg !989
  call void @llvm.dbg.value(metadata i64 8, metadata !986, metadata !DIExpression()), !dbg !989
  call void @llvm.dbg.value(metadata ptr undef, metadata !987, metadata !DIExpression()), !dbg !989
  call void @llvm.dbg.value(metadata i64 8, metadata !988, metadata !DIExpression()), !dbg !989
  %19 = bitcast double %16 to i64, !dbg !991
  call void @llvm.dbg.value(metadata i64 %19, metadata !971, metadata !DIExpression()), !dbg !972
  call void @llvm.dbg.value(metadata i64 %19, metadata !947, metadata !DIExpression()), !dbg !964
  call void @llvm.dbg.value(metadata double %18, metadata !966, metadata !DIExpression()), !dbg !992
  call void @llvm.dbg.value(metadata ptr undef, metadata !974, metadata !DIExpression()), !dbg !994
  call void @llvm.dbg.value(metadata i64 8, metadata !986, metadata !DIExpression()), !dbg !994
  call void @llvm.dbg.value(metadata ptr undef, metadata !987, metadata !DIExpression()), !dbg !994
  call void @llvm.dbg.value(metadata i64 8, metadata !988, metadata !DIExpression()), !dbg !994
  %20 = bitcast double %18 to i64, !dbg !996
  call void @llvm.dbg.value(metadata i64 %20, metadata !971, metadata !DIExpression()), !dbg !992
  call void @llvm.dbg.value(metadata i64 %20, metadata !950, metadata !DIExpression()), !dbg !964
  %21 = call double @llvm.fabs.f64(double %16), !dbg !997
  %22 = bitcast double %21 to i64, !dbg !997
  call void @llvm.dbg.value(metadata i64 %22, metadata !951, metadata !DIExpression()), !dbg !964
  %23 = call double @llvm.fabs.f64(double %18), !dbg !998
  %24 = bitcast double %23 to i64, !dbg !998
  call void @llvm.dbg.value(metadata i64 %24, metadata !952, metadata !DIExpression()), !dbg !964
  %25 = or i64 %24, %22, !dbg !999
  %26 = icmp ult i64 %25, 4746794007248502784, !dbg !1000
  br i1 %26, label %27, label %35, !dbg !1001

27:                                               ; preds = %2
  call void @llvm.dbg.value(metadata i32 poison, metadata !953, metadata !DIExpression()), !dbg !1002
  %28 = fptosi double %18 to i32, !dbg !1003
  call void @llvm.dbg.value(metadata i32 %28, metadata !957, metadata !DIExpression()), !dbg !1002
  %29 = icmp eq i32 %28, 0, !dbg !1004
  br i1 %29, label %67, label %30, !dbg !1006

30:                                               ; preds = %27
  %31 = fptosi double %16 to i32, !dbg !1007
  call void @llvm.dbg.value(metadata i32 %31, metadata !953, metadata !DIExpression()), !dbg !1002
  %32 = srem i32 %31, %28, !dbg !1008
  call void @llvm.dbg.value(metadata i32 %32, metadata !958, metadata !DIExpression()), !dbg !1002
  %33 = call i32 @llvm.abs.i32(i32 %32, i1 true), !dbg !1009
  %34 = sitofp i32 %33 to double, !dbg !1010
  br label %67

35:                                               ; preds = %2
  %36 = icmp ugt i64 %24, 9218868437227405311
  %37 = icmp ugt i64 %22, 4890909195324358656
  %38 = or i1 %37, %36, !dbg !1011
  br i1 %38, label %67, label %39, !dbg !1011

39:                                               ; preds = %35
  %40 = icmp eq i64 %22, 4890909195324358656, !dbg !1013
  br i1 %40, label %41, label %45, !dbg !1015

41:                                               ; preds = %39
  %42 = icmp sgt i64 %19, -1, !dbg !1016
  %43 = icmp ugt i64 %24, 4890909195324358656
  %44 = or i1 %42, %43, !dbg !1017
  br i1 %44, label %67, label %47, !dbg !1017

45:                                               ; preds = %39
  %46 = icmp ugt i64 %24, 4890909195324358656, !dbg !1018
  br i1 %46, label %67, label %47, !dbg !1019

47:                                               ; preds = %45, %41
  %48 = icmp eq i64 %24, 4890909195324358656, !dbg !1020
  %49 = icmp sgt i64 %20, -1
  %50 = and i1 %49, %48, !dbg !1021
  br i1 %50, label %67, label %51, !dbg !1021

51:                                               ; preds = %47
  %52 = fptosi double %16 to i64, !dbg !1022
  call void @llvm.dbg.value(metadata i64 %52, metadata !959, metadata !DIExpression()), !dbg !964
  %53 = fptosi double %18 to i64, !dbg !1023
  call void @llvm.dbg.value(metadata i64 %53, metadata !961, metadata !DIExpression()), !dbg !964
  call void @llvm.dbg.value(metadata i64 -9223372036854775808, metadata !962, metadata !DIExpression()), !dbg !964
  %54 = icmp eq i64 %53, 0, !dbg !1024
  br i1 %54, label %67, label %55, !dbg !1026

55:                                               ; preds = %51
  %56 = icmp eq i64 %52, -9223372036854775808, !dbg !1027
  %57 = icmp eq i64 %53, -1
  %58 = and i1 %56, %57, !dbg !1028
  br i1 %58, label %67, label %59, !dbg !1028

59:                                               ; preds = %55
  %60 = srem i64 %52, %53, !dbg !1029
  %61 = sitofp i64 %60 to double, !dbg !1030
  call void @llvm.dbg.value(metadata double %61, metadata !963, metadata !DIExpression()), !dbg !964
  %62 = icmp ult i64 %22, 4746794007248502784, !dbg !1031
  %63 = icmp ult i64 %24, 4746794007248502784
  %64 = and i1 %62, %63, !dbg !1032
  %65 = call fast double @llvm.fabs.f64(double %61), !dbg !1032
  %66 = select fast i1 %64, double %65, double %61, !dbg !1032
  br label %67

67:                                               ; preds = %27, %30, %35, %41, %45, %47, %51, %55, %59
  %68 = phi double [ %34, %30 ], [ 0.000000e+00, %27 ], [ 0.000000e+00, %35 ], [ 0.000000e+00, %47 ], [ 0.000000e+00, %45 ], [ 0.000000e+00, %41 ], [ %66, %59 ], [ 0.000000e+00, %55 ], [ 0.000000e+00, %51 ], !dbg !964
  %69 = load ptr, ptr %1, align 8, !dbg !940, !tbaa !300
  store double %68, ptr %69, align 8, !dbg !940, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1033
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1033
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1033
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1033
  ret void, !dbg !1033
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_boolean_and_op(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1034 {
  %3 = alloca double, align 8, !DIAssignID !1042
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1038, metadata !DIExpression(), metadata !1042, metadata ptr %3, metadata !DIExpression()), !dbg !1043
  %4 = alloca ptr, align 8, !DIAssignID !1044
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1039, metadata !DIExpression(), metadata !1044, metadata ptr %4, metadata !DIExpression()), !dbg !1043
  %5 = alloca double, align 8, !DIAssignID !1045
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1040, metadata !DIExpression(), metadata !1045, metadata ptr %5, metadata !DIExpression()), !dbg !1043
  %6 = alloca ptr, align 8, !DIAssignID !1046
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1041, metadata !DIExpression(), metadata !1046, metadata ptr %6, metadata !DIExpression()), !dbg !1043
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1036, metadata !DIExpression()), !dbg !1043
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1037, metadata !DIExpression()), !dbg !1043
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1047
  store double 0.000000e+00, ptr %3, align 8, !dbg !1048, !tbaa !312, !DIAssignID !1049
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1038, metadata !DIExpression(), metadata !1049, metadata ptr %3, metadata !DIExpression()), !dbg !1043
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1050
  store ptr %3, ptr %4, align 8, !dbg !1051, !tbaa !300, !DIAssignID !1052
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1039, metadata !DIExpression(), metadata !1052, metadata ptr %4, metadata !DIExpression()), !dbg !1043
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1053
  store double 0.000000e+00, ptr %5, align 8, !dbg !1054, !tbaa !312, !DIAssignID !1055
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1040, metadata !DIExpression(), metadata !1055, metadata ptr %5, metadata !DIExpression()), !dbg !1043
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1056
  store ptr %5, ptr %6, align 8, !dbg !1057, !tbaa !300, !DIAssignID !1058
  call void @llvm.dbg.assign(metadata ptr %5, metadata !1041, metadata !DIExpression(), metadata !1058, metadata ptr %6, metadata !DIExpression()), !dbg !1043
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1059
  %8 = load ptr, ptr %7, align 8, !dbg !1059, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1059, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1059, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %4) #9, !dbg !1059
  %11 = load ptr, ptr %4, align 8, !dbg !1060, !tbaa !300
  %12 = load double, ptr %11, align 8, !dbg !1062, !tbaa !312
  %13 = call fast double @llvm.fabs.f64(double %12), !dbg !1063
  %14 = fcmp fast ogt double %13, 1.000000e-05, !dbg !1064
  br i1 %14, label %15, label %25, !dbg !1065

15:                                               ; preds = %2
  %16 = load ptr, ptr %7, align 8, !dbg !1066, !tbaa !368
  %17 = getelementptr inbounds ptr, ptr %16, i64 1, !dbg !1066
  %18 = load ptr, ptr %17, align 8, !dbg !1066, !tbaa !300
  %19 = load ptr, ptr %18, align 8, !dbg !1066, !tbaa !344
  call void %19(ptr noundef nonnull %18, ptr noundef nonnull %6) #9, !dbg !1066
  %20 = load ptr, ptr %6, align 8, !dbg !1068, !tbaa !300
  %21 = load double, ptr %20, align 8, !dbg !1068, !tbaa !312
  %22 = call fast double @llvm.fabs.f64(double %21), !dbg !1068
  %23 = fcmp fast ogt double %22, 1.000000e-05, !dbg !1068
  %24 = select fast i1 %23, double 1.000000e+00, double 0.000000e+00, !dbg !1068
  br label %25, !dbg !1069

25:                                               ; preds = %2, %15
  %26 = phi double [ %24, %15 ], [ 0.000000e+00, %2 ]
  %27 = load ptr, ptr %1, align 8, !dbg !1070, !tbaa !300
  store double %26, ptr %27, align 8, !dbg !1070, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1071
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1071
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1071
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1071
  ret void, !dbg !1071
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_boolean_or_op(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1072 {
  %3 = alloca double, align 8, !DIAssignID !1080
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1076, metadata !DIExpression(), metadata !1080, metadata ptr %3, metadata !DIExpression()), !dbg !1081
  %4 = alloca ptr, align 8, !DIAssignID !1082
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1077, metadata !DIExpression(), metadata !1082, metadata ptr %4, metadata !DIExpression()), !dbg !1081
  %5 = alloca double, align 8, !DIAssignID !1083
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1078, metadata !DIExpression(), metadata !1083, metadata ptr %5, metadata !DIExpression()), !dbg !1081
  %6 = alloca ptr, align 8, !DIAssignID !1084
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1079, metadata !DIExpression(), metadata !1084, metadata ptr %6, metadata !DIExpression()), !dbg !1081
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1074, metadata !DIExpression()), !dbg !1081
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1075, metadata !DIExpression()), !dbg !1081
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1085
  store double 0.000000e+00, ptr %3, align 8, !dbg !1086, !tbaa !312, !DIAssignID !1087
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1076, metadata !DIExpression(), metadata !1087, metadata ptr %3, metadata !DIExpression()), !dbg !1081
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1088
  store ptr %3, ptr %4, align 8, !dbg !1089, !tbaa !300, !DIAssignID !1090
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1077, metadata !DIExpression(), metadata !1090, metadata ptr %4, metadata !DIExpression()), !dbg !1081
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1091
  store double 0.000000e+00, ptr %5, align 8, !dbg !1092, !tbaa !312, !DIAssignID !1093
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1078, metadata !DIExpression(), metadata !1093, metadata ptr %5, metadata !DIExpression()), !dbg !1081
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1094
  store ptr %5, ptr %6, align 8, !dbg !1095, !tbaa !300, !DIAssignID !1096
  call void @llvm.dbg.assign(metadata ptr %5, metadata !1079, metadata !DIExpression(), metadata !1096, metadata ptr %6, metadata !DIExpression()), !dbg !1081
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1097
  %8 = load ptr, ptr %7, align 8, !dbg !1097, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1097, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1097, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %4) #9, !dbg !1097
  %11 = load ptr, ptr %4, align 8, !dbg !1098, !tbaa !300
  %12 = load double, ptr %11, align 8, !dbg !1100, !tbaa !312
  %13 = call fast double @llvm.fabs.f64(double %12), !dbg !1101
  %14 = fcmp fast olt double %13, 1.000000e-05, !dbg !1102
  br i1 %14, label %15, label %25, !dbg !1103

15:                                               ; preds = %2
  %16 = load ptr, ptr %7, align 8, !dbg !1104, !tbaa !368
  %17 = getelementptr inbounds ptr, ptr %16, i64 1, !dbg !1104
  %18 = load ptr, ptr %17, align 8, !dbg !1104, !tbaa !300
  %19 = load ptr, ptr %18, align 8, !dbg !1104, !tbaa !344
  call void %19(ptr noundef nonnull %18, ptr noundef nonnull %6) #9, !dbg !1104
  %20 = load ptr, ptr %6, align 8, !dbg !1106, !tbaa !300
  %21 = load double, ptr %20, align 8, !dbg !1106, !tbaa !312
  %22 = call fast double @llvm.fabs.f64(double %21), !dbg !1106
  %23 = fcmp fast ogt double %22, 1.000000e-05, !dbg !1106
  %24 = select fast i1 %23, double 1.000000e+00, double 0.000000e+00, !dbg !1106
  br label %25, !dbg !1107

25:                                               ; preds = %2, %15
  %26 = phi double [ %24, %15 ], [ 1.000000e+00, %2 ]
  %27 = load ptr, ptr %1, align 8, !dbg !1108, !tbaa !300
  store double %26, ptr %27, align 8, !dbg !1108, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1109
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1109
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1109
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1109
  ret void, !dbg !1109
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_boolean_and_func(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1110 {
  %3 = alloca double, align 8, !DIAssignID !1118
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1114, metadata !DIExpression(), metadata !1118, metadata ptr %3, metadata !DIExpression()), !dbg !1119
  %4 = alloca double, align 8, !DIAssignID !1120
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1115, metadata !DIExpression(), metadata !1120, metadata ptr %4, metadata !DIExpression()), !dbg !1119
  %5 = alloca ptr, align 8, !DIAssignID !1121
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1116, metadata !DIExpression(), metadata !1121, metadata ptr %5, metadata !DIExpression()), !dbg !1119
  %6 = alloca ptr, align 8, !DIAssignID !1122
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1117, metadata !DIExpression(), metadata !1122, metadata ptr %6, metadata !DIExpression()), !dbg !1119
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1112, metadata !DIExpression()), !dbg !1119
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1113, metadata !DIExpression()), !dbg !1119
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1123
  store double 0.000000e+00, ptr %3, align 8, !dbg !1124, !tbaa !312, !DIAssignID !1125
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1114, metadata !DIExpression(), metadata !1125, metadata ptr %3, metadata !DIExpression()), !dbg !1119
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1126
  store double 0.000000e+00, ptr %4, align 8, !dbg !1127, !tbaa !312, !DIAssignID !1128
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1115, metadata !DIExpression(), metadata !1128, metadata ptr %4, metadata !DIExpression()), !dbg !1119
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1129
  store ptr %3, ptr %5, align 8, !dbg !1130, !tbaa !300, !DIAssignID !1131
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1116, metadata !DIExpression(), metadata !1131, metadata ptr %5, metadata !DIExpression()), !dbg !1119
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1132
  store ptr %4, ptr %6, align 8, !dbg !1133, !tbaa !300, !DIAssignID !1134
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1117, metadata !DIExpression(), metadata !1134, metadata ptr %6, metadata !DIExpression()), !dbg !1119
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1135
  %8 = load ptr, ptr %7, align 8, !dbg !1135, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1135, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1135, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1135
  %11 = load ptr, ptr %7, align 8, !dbg !1136, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1136
  %13 = load ptr, ptr %12, align 8, !dbg !1136, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1136, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1136
  %15 = load ptr, ptr %5, align 8, !dbg !1137, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1137, !tbaa !312
  %17 = call fast double @llvm.fabs.f64(double %16), !dbg !1137
  %18 = fcmp fast ogt double %17, 1.000000e-05, !dbg !1137
  br i1 %18, label %19, label %25, !dbg !1137

19:                                               ; preds = %2
  %20 = load ptr, ptr %6, align 8, !dbg !1137, !tbaa !300
  %21 = load double, ptr %20, align 8, !dbg !1137, !tbaa !312
  %22 = call fast double @llvm.fabs.f64(double %21), !dbg !1137
  %23 = fcmp fast ogt double %22, 1.000000e-05, !dbg !1137
  %24 = select fast i1 %23, double 1.000000e+00, double 0.000000e+00, !dbg !1137
  br label %25

25:                                               ; preds = %19, %2
  %26 = phi double [ 0.000000e+00, %2 ], [ %24, %19 ], !dbg !1119
  %27 = load ptr, ptr %1, align 8, !dbg !1137, !tbaa !300
  store double %26, ptr %27, align 8, !dbg !1137, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1138
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1138
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1138
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1138
  ret void, !dbg !1138
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_boolean_or_func(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1139 {
  %3 = alloca double, align 8, !DIAssignID !1147
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1143, metadata !DIExpression(), metadata !1147, metadata ptr %3, metadata !DIExpression()), !dbg !1148
  %4 = alloca double, align 8, !DIAssignID !1149
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1144, metadata !DIExpression(), metadata !1149, metadata ptr %4, metadata !DIExpression()), !dbg !1148
  %5 = alloca ptr, align 8, !DIAssignID !1150
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1145, metadata !DIExpression(), metadata !1150, metadata ptr %5, metadata !DIExpression()), !dbg !1148
  %6 = alloca ptr, align 8, !DIAssignID !1151
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1146, metadata !DIExpression(), metadata !1151, metadata ptr %6, metadata !DIExpression()), !dbg !1148
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1141, metadata !DIExpression()), !dbg !1148
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1142, metadata !DIExpression()), !dbg !1148
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1152
  store double 0.000000e+00, ptr %3, align 8, !dbg !1153, !tbaa !312, !DIAssignID !1154
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1143, metadata !DIExpression(), metadata !1154, metadata ptr %3, metadata !DIExpression()), !dbg !1148
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1155
  store double 0.000000e+00, ptr %4, align 8, !dbg !1156, !tbaa !312, !DIAssignID !1157
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1144, metadata !DIExpression(), metadata !1157, metadata ptr %4, metadata !DIExpression()), !dbg !1148
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1158
  store ptr %3, ptr %5, align 8, !dbg !1159, !tbaa !300, !DIAssignID !1160
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1145, metadata !DIExpression(), metadata !1160, metadata ptr %5, metadata !DIExpression()), !dbg !1148
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1161
  store ptr %4, ptr %6, align 8, !dbg !1162, !tbaa !300, !DIAssignID !1163
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1146, metadata !DIExpression(), metadata !1163, metadata ptr %6, metadata !DIExpression()), !dbg !1148
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1164
  %8 = load ptr, ptr %7, align 8, !dbg !1164, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1164, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1164, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1164
  %11 = load ptr, ptr %7, align 8, !dbg !1165, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1165
  %13 = load ptr, ptr %12, align 8, !dbg !1165, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1165, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1165
  %15 = load ptr, ptr %5, align 8, !dbg !1166, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1166, !tbaa !312
  %17 = call fast double @llvm.fabs.f64(double %16), !dbg !1166
  %18 = fcmp fast ogt double %17, 1.000000e-05, !dbg !1166
  br i1 %18, label %25, label %19, !dbg !1166

19:                                               ; preds = %2
  %20 = load ptr, ptr %6, align 8, !dbg !1166, !tbaa !300
  %21 = load double, ptr %20, align 8, !dbg !1166, !tbaa !312
  %22 = call fast double @llvm.fabs.f64(double %21), !dbg !1166
  %23 = fcmp fast ogt double %22, 1.000000e-05, !dbg !1166
  %24 = select fast i1 %23, double 1.000000e+00, double 0.000000e+00, !dbg !1166
  br label %25, !dbg !1166

25:                                               ; preds = %19, %2
  %26 = phi double [ 1.000000e+00, %2 ], [ %24, %19 ]
  %27 = load ptr, ptr %1, align 8, !dbg !1166, !tbaa !300
  store double %26, ptr %27, align 8, !dbg !1166, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1167
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1167
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1167
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1167
  ret void, !dbg !1167
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_neg(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1168 {
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
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %4) #9, !dbg !1183
  %9 = load ptr, ptr %4, align 8, !dbg !1184, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1184, !tbaa !312
  %11 = fneg fast double %10, !dbg !1184
  %12 = load ptr, ptr %1, align 8, !dbg !1184, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1184, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1185
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1185
  ret void, !dbg !1185
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_add_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1186 {
  %3 = alloca double, align 8, !DIAssignID !1192
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1190, metadata !DIExpression(), metadata !1192, metadata ptr %3, metadata !DIExpression()), !dbg !1193
  %4 = alloca ptr, align 8, !DIAssignID !1194
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1191, metadata !DIExpression(), metadata !1194, metadata ptr %4, metadata !DIExpression()), !dbg !1193
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1188, metadata !DIExpression()), !dbg !1193
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1189, metadata !DIExpression()), !dbg !1193
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1195
  store double 0.000000e+00, ptr %3, align 8, !dbg !1196, !tbaa !312, !DIAssignID !1197
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1190, metadata !DIExpression(), metadata !1197, metadata ptr %3, metadata !DIExpression()), !dbg !1193
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1198
  store ptr %3, ptr %4, align 8, !dbg !1199, !tbaa !300, !DIAssignID !1200
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1191, metadata !DIExpression(), metadata !1200, metadata ptr %4, metadata !DIExpression()), !dbg !1193
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1201
  %6 = load ptr, ptr %5, align 8, !dbg !1201, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1201, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1201, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1201
  %9 = load ptr, ptr %5, align 8, !dbg !1202, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1202
  %11 = load ptr, ptr %10, align 8, !dbg !1202, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1202, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1202
  %13 = load ptr, ptr %1, align 8, !dbg !1203, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1203, !tbaa !312
  %15 = load ptr, ptr %4, align 8, !dbg !1203, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1203, !tbaa !312
  %17 = fadd fast double %16, %14, !dbg !1203
  store double %17, ptr %13, align 8, !dbg !1203, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1204
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1204
  ret void, !dbg !1204
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sub_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1205 {
  %3 = alloca double, align 8, !DIAssignID !1211
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1209, metadata !DIExpression(), metadata !1211, metadata ptr %3, metadata !DIExpression()), !dbg !1212
  %4 = alloca ptr, align 8, !DIAssignID !1213
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1210, metadata !DIExpression(), metadata !1213, metadata ptr %4, metadata !DIExpression()), !dbg !1212
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1207, metadata !DIExpression()), !dbg !1212
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1208, metadata !DIExpression()), !dbg !1212
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1214
  store double 0.000000e+00, ptr %3, align 8, !dbg !1215, !tbaa !312, !DIAssignID !1216
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1209, metadata !DIExpression(), metadata !1216, metadata ptr %3, metadata !DIExpression()), !dbg !1212
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1217
  store ptr %3, ptr %4, align 8, !dbg !1218, !tbaa !300, !DIAssignID !1219
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1210, metadata !DIExpression(), metadata !1219, metadata ptr %4, metadata !DIExpression()), !dbg !1212
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1220
  %6 = load ptr, ptr %5, align 8, !dbg !1220, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1220, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1220, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1220
  %9 = load ptr, ptr %5, align 8, !dbg !1221, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1221
  %11 = load ptr, ptr %10, align 8, !dbg !1221, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1221, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1221
  %13 = load ptr, ptr %1, align 8, !dbg !1222, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1222, !tbaa !312
  %15 = load ptr, ptr %4, align 8, !dbg !1222, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1222, !tbaa !312
  %17 = fsub fast double %14, %16, !dbg !1222
  store double %17, ptr %13, align 8, !dbg !1222, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1223
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1223
  ret void, !dbg !1223
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_mul_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1224 {
  %3 = alloca double, align 8, !DIAssignID !1230
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1228, metadata !DIExpression(), metadata !1230, metadata ptr %3, metadata !DIExpression()), !dbg !1231
  %4 = alloca ptr, align 8, !DIAssignID !1232
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1229, metadata !DIExpression(), metadata !1232, metadata ptr %4, metadata !DIExpression()), !dbg !1231
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1226, metadata !DIExpression()), !dbg !1231
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1227, metadata !DIExpression()), !dbg !1231
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1233
  store double 0.000000e+00, ptr %3, align 8, !dbg !1234, !tbaa !312, !DIAssignID !1235
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1228, metadata !DIExpression(), metadata !1235, metadata ptr %3, metadata !DIExpression()), !dbg !1231
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1236
  store ptr %3, ptr %4, align 8, !dbg !1237, !tbaa !300, !DIAssignID !1238
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1229, metadata !DIExpression(), metadata !1238, metadata ptr %4, metadata !DIExpression()), !dbg !1231
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1239
  %6 = load ptr, ptr %5, align 8, !dbg !1239, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1239, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1239, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1239
  %9 = load ptr, ptr %5, align 8, !dbg !1240, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1240
  %11 = load ptr, ptr %10, align 8, !dbg !1240, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1240, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1240
  %13 = load ptr, ptr %1, align 8, !dbg !1241, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1241, !tbaa !312
  %15 = load ptr, ptr %4, align 8, !dbg !1241, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1241, !tbaa !312
  %17 = fmul fast double %16, %14, !dbg !1241
  store double %17, ptr %13, align 8, !dbg !1241, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1242
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1242
  ret void, !dbg !1242
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_div_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1243 {
  %3 = alloca double, align 8, !DIAssignID !1249
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1247, metadata !DIExpression(), metadata !1249, metadata ptr %3, metadata !DIExpression()), !dbg !1250
  %4 = alloca ptr, align 8, !DIAssignID !1251
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1248, metadata !DIExpression(), metadata !1251, metadata ptr %4, metadata !DIExpression()), !dbg !1250
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1245, metadata !DIExpression()), !dbg !1250
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1246, metadata !DIExpression()), !dbg !1250
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1252
  store double 0.000000e+00, ptr %3, align 8, !dbg !1253, !tbaa !312, !DIAssignID !1254
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1247, metadata !DIExpression(), metadata !1254, metadata ptr %3, metadata !DIExpression()), !dbg !1250
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1255
  store ptr %3, ptr %4, align 8, !dbg !1256, !tbaa !300, !DIAssignID !1257
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1248, metadata !DIExpression(), metadata !1257, metadata ptr %4, metadata !DIExpression()), !dbg !1250
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1258
  %6 = load ptr, ptr %5, align 8, !dbg !1258, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1258, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1258, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1258
  %9 = load ptr, ptr %5, align 8, !dbg !1259, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1259
  %11 = load ptr, ptr %10, align 8, !dbg !1259, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1259, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1259
  %13 = load ptr, ptr %4, align 8, !dbg !1260, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1262, !tbaa !312
  %15 = call fast double @llvm.fabs.f64(double %14), !dbg !1263
  %16 = fcmp fast olt double %15, 1.000000e-05, !dbg !1264
  %17 = load ptr, ptr %1, align 8, !dbg !1250, !tbaa !300
  br i1 %16, label %21, label %18, !dbg !1265

18:                                               ; preds = %2
  %19 = load double, ptr %17, align 8, !dbg !1266, !tbaa !312
  %20 = fdiv fast double %19, %14, !dbg !1266
  br label %21, !dbg !1267

21:                                               ; preds = %2, %18
  %22 = phi double [ %20, %18 ], [ 0.000000e+00, %2 ]
  store double %22, ptr %17, align 8, !dbg !1250, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1267
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1267
  ret void, !dbg !1267
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_bitwise_or_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1268 {
  %3 = alloca double, align 8, !DIAssignID !1274
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1272, metadata !DIExpression(), metadata !1274, metadata ptr %3, metadata !DIExpression()), !dbg !1275
  %4 = alloca ptr, align 8, !DIAssignID !1276
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1273, metadata !DIExpression(), metadata !1276, metadata ptr %4, metadata !DIExpression()), !dbg !1275
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1270, metadata !DIExpression()), !dbg !1275
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1271, metadata !DIExpression()), !dbg !1275
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1277
  store double 0.000000e+00, ptr %3, align 8, !dbg !1278, !tbaa !312, !DIAssignID !1279
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1272, metadata !DIExpression(), metadata !1279, metadata ptr %3, metadata !DIExpression()), !dbg !1275
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1280
  store ptr %3, ptr %4, align 8, !dbg !1281, !tbaa !300, !DIAssignID !1282
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1273, metadata !DIExpression(), metadata !1282, metadata ptr %4, metadata !DIExpression()), !dbg !1275
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1283
  %6 = load ptr, ptr %5, align 8, !dbg !1283, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1283, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1283, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1283
  %9 = load ptr, ptr %5, align 8, !dbg !1284, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1284
  %11 = load ptr, ptr %10, align 8, !dbg !1284, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1284, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1284
  %13 = load ptr, ptr %1, align 8, !dbg !1285, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1285, !tbaa !312
  %15 = fptosi double %14 to i64, !dbg !1285
  %16 = load ptr, ptr %4, align 8, !dbg !1285, !tbaa !300
  %17 = load double, ptr %16, align 8, !dbg !1285, !tbaa !312
  %18 = fptosi double %17 to i64, !dbg !1285
  %19 = or i64 %18, %15, !dbg !1285
  %20 = sitofp i64 %19 to double, !dbg !1285
  store double %20, ptr %13, align 8, !dbg !1285, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1286
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1286
  ret void, !dbg !1286
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_bitwise_or(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1287 {
  %3 = alloca double, align 8, !DIAssignID !1295
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1291, metadata !DIExpression(), metadata !1295, metadata ptr %3, metadata !DIExpression()), !dbg !1296
  %4 = alloca ptr, align 8, !DIAssignID !1297
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1292, metadata !DIExpression(), metadata !1297, metadata ptr %4, metadata !DIExpression()), !dbg !1296
  %5 = alloca double, align 8, !DIAssignID !1298
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1293, metadata !DIExpression(), metadata !1298, metadata ptr %5, metadata !DIExpression()), !dbg !1296
  %6 = alloca ptr, align 8, !DIAssignID !1299
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1294, metadata !DIExpression(), metadata !1299, metadata ptr %6, metadata !DIExpression()), !dbg !1296
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1289, metadata !DIExpression()), !dbg !1296
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1290, metadata !DIExpression()), !dbg !1296
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1300
  store double 0.000000e+00, ptr %3, align 8, !dbg !1301, !tbaa !312, !DIAssignID !1302
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1291, metadata !DIExpression(), metadata !1302, metadata ptr %3, metadata !DIExpression()), !dbg !1296
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1303
  store ptr %3, ptr %4, align 8, !dbg !1304, !tbaa !300, !DIAssignID !1305
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1292, metadata !DIExpression(), metadata !1305, metadata ptr %4, metadata !DIExpression()), !dbg !1296
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1306
  store double 0.000000e+00, ptr %5, align 8, !dbg !1307, !tbaa !312, !DIAssignID !1308
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1293, metadata !DIExpression(), metadata !1308, metadata ptr %5, metadata !DIExpression()), !dbg !1296
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1309
  store ptr %5, ptr %6, align 8, !dbg !1310, !tbaa !300, !DIAssignID !1311
  call void @llvm.dbg.assign(metadata ptr %5, metadata !1294, metadata !DIExpression(), metadata !1311, metadata ptr %6, metadata !DIExpression()), !dbg !1296
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1312
  %8 = load ptr, ptr %7, align 8, !dbg !1312, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1312, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1312, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %4) #9, !dbg !1312
  %11 = load ptr, ptr %7, align 8, !dbg !1313, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1313
  %13 = load ptr, ptr %12, align 8, !dbg !1313, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1313, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1313
  %15 = load ptr, ptr %4, align 8, !dbg !1314, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1314, !tbaa !312
  %17 = fptosi double %16 to i64, !dbg !1314
  %18 = load ptr, ptr %6, align 8, !dbg !1314, !tbaa !300
  %19 = load double, ptr %18, align 8, !dbg !1314, !tbaa !312
  %20 = fptosi double %19 to i64, !dbg !1314
  %21 = or i64 %20, %17, !dbg !1314
  %22 = sitofp i64 %21 to double, !dbg !1314
  %23 = load ptr, ptr %1, align 8, !dbg !1314, !tbaa !300
  store double %22, ptr %23, align 8, !dbg !1314, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1315
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1315
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1315
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1315
  ret void, !dbg !1315
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_bitwise_and_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1316 {
  %3 = alloca double, align 8, !DIAssignID !1322
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1320, metadata !DIExpression(), metadata !1322, metadata ptr %3, metadata !DIExpression()), !dbg !1323
  %4 = alloca ptr, align 8, !DIAssignID !1324
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1321, metadata !DIExpression(), metadata !1324, metadata ptr %4, metadata !DIExpression()), !dbg !1323
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1318, metadata !DIExpression()), !dbg !1323
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1319, metadata !DIExpression()), !dbg !1323
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1325
  store double 0.000000e+00, ptr %3, align 8, !dbg !1326, !tbaa !312, !DIAssignID !1327
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1320, metadata !DIExpression(), metadata !1327, metadata ptr %3, metadata !DIExpression()), !dbg !1323
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1328
  store ptr %3, ptr %4, align 8, !dbg !1329, !tbaa !300, !DIAssignID !1330
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1321, metadata !DIExpression(), metadata !1330, metadata ptr %4, metadata !DIExpression()), !dbg !1323
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1331
  %6 = load ptr, ptr %5, align 8, !dbg !1331, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1331, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1331, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1331
  %9 = load ptr, ptr %5, align 8, !dbg !1332, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1332
  %11 = load ptr, ptr %10, align 8, !dbg !1332, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1332, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1332
  %13 = load ptr, ptr %1, align 8, !dbg !1333, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1333, !tbaa !312
  %15 = fptosi double %14 to i64, !dbg !1333
  %16 = load ptr, ptr %4, align 8, !dbg !1333, !tbaa !300
  %17 = load double, ptr %16, align 8, !dbg !1333, !tbaa !312
  %18 = fptosi double %17 to i64, !dbg !1333
  %19 = and i64 %18, %15, !dbg !1333
  %20 = sitofp i64 %19 to double, !dbg !1333
  store double %20, ptr %13, align 8, !dbg !1333, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1334
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1334
  ret void, !dbg !1334
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_bitwise_and(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1335 {
  %3 = alloca double, align 8, !DIAssignID !1343
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1339, metadata !DIExpression(), metadata !1343, metadata ptr %3, metadata !DIExpression()), !dbg !1344
  %4 = alloca ptr, align 8, !DIAssignID !1345
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1340, metadata !DIExpression(), metadata !1345, metadata ptr %4, metadata !DIExpression()), !dbg !1344
  %5 = alloca double, align 8, !DIAssignID !1346
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1341, metadata !DIExpression(), metadata !1346, metadata ptr %5, metadata !DIExpression()), !dbg !1344
  %6 = alloca ptr, align 8, !DIAssignID !1347
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1342, metadata !DIExpression(), metadata !1347, metadata ptr %6, metadata !DIExpression()), !dbg !1344
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1337, metadata !DIExpression()), !dbg !1344
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1338, metadata !DIExpression()), !dbg !1344
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1348
  store double 0.000000e+00, ptr %3, align 8, !dbg !1349, !tbaa !312, !DIAssignID !1350
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1339, metadata !DIExpression(), metadata !1350, metadata ptr %3, metadata !DIExpression()), !dbg !1344
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1351
  store ptr %3, ptr %4, align 8, !dbg !1352, !tbaa !300, !DIAssignID !1353
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1340, metadata !DIExpression(), metadata !1353, metadata ptr %4, metadata !DIExpression()), !dbg !1344
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1354
  store double 0.000000e+00, ptr %5, align 8, !dbg !1355, !tbaa !312, !DIAssignID !1356
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1341, metadata !DIExpression(), metadata !1356, metadata ptr %5, metadata !DIExpression()), !dbg !1344
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1357
  store ptr %5, ptr %6, align 8, !dbg !1358, !tbaa !300, !DIAssignID !1359
  call void @llvm.dbg.assign(metadata ptr %5, metadata !1342, metadata !DIExpression(), metadata !1359, metadata ptr %6, metadata !DIExpression()), !dbg !1344
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1360
  %8 = load ptr, ptr %7, align 8, !dbg !1360, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1360, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1360, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %4) #9, !dbg !1360
  %11 = load ptr, ptr %7, align 8, !dbg !1361, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1361
  %13 = load ptr, ptr %12, align 8, !dbg !1361, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1361, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1361
  %15 = load ptr, ptr %4, align 8, !dbg !1362, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1362, !tbaa !312
  %17 = fptosi double %16 to i64, !dbg !1362
  %18 = load ptr, ptr %6, align 8, !dbg !1362, !tbaa !300
  %19 = load double, ptr %18, align 8, !dbg !1362, !tbaa !312
  %20 = fptosi double %19 to i64, !dbg !1362
  %21 = and i64 %20, %17, !dbg !1362
  %22 = sitofp i64 %21 to double, !dbg !1362
  %23 = load ptr, ptr %1, align 8, !dbg !1362, !tbaa !300
  store double %22, ptr %23, align 8, !dbg !1362, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1363
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1363
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1363
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1363
  ret void, !dbg !1363
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_mod_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1364 {
  %3 = alloca double, align 8, !DIAssignID !1370
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1368, metadata !DIExpression(), metadata !1370, metadata ptr %3, metadata !DIExpression()), !dbg !1371
  %4 = alloca ptr, align 8, !DIAssignID !1372
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1369, metadata !DIExpression(), metadata !1372, metadata ptr %4, metadata !DIExpression()), !dbg !1371
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1366, metadata !DIExpression()), !dbg !1371
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1367, metadata !DIExpression()), !dbg !1371
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1373
  store double 0.000000e+00, ptr %3, align 8, !dbg !1374, !tbaa !312, !DIAssignID !1375
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1368, metadata !DIExpression(), metadata !1375, metadata ptr %3, metadata !DIExpression()), !dbg !1371
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1376
  store ptr %3, ptr %4, align 8, !dbg !1377, !tbaa !300, !DIAssignID !1378
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1369, metadata !DIExpression(), metadata !1378, metadata ptr %4, metadata !DIExpression()), !dbg !1371
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1379
  %6 = load ptr, ptr %5, align 8, !dbg !1379, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1379, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1379, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1379
  %9 = load ptr, ptr %5, align 8, !dbg !1380, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1380
  %11 = load ptr, ptr %10, align 8, !dbg !1380, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1380, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1380
  %13 = load ptr, ptr %1, align 8, !dbg !1381, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1381, !tbaa !312
  %15 = load ptr, ptr %4, align 8, !dbg !1381, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1381, !tbaa !312
  call void @llvm.dbg.value(metadata double %14, metadata !941, metadata !DIExpression()), !dbg !1382
  call void @llvm.dbg.value(metadata double %16, metadata !946, metadata !DIExpression()), !dbg !1382
  call void @llvm.dbg.value(metadata double %14, metadata !966, metadata !DIExpression()), !dbg !1384
  call void @llvm.dbg.value(metadata ptr undef, metadata !974, metadata !DIExpression()), !dbg !1386
  call void @llvm.dbg.value(metadata i64 8, metadata !986, metadata !DIExpression()), !dbg !1386
  call void @llvm.dbg.value(metadata ptr undef, metadata !987, metadata !DIExpression()), !dbg !1386
  call void @llvm.dbg.value(metadata i64 8, metadata !988, metadata !DIExpression()), !dbg !1386
  %17 = bitcast double %14 to i64, !dbg !1388
  call void @llvm.dbg.value(metadata i64 %17, metadata !971, metadata !DIExpression()), !dbg !1384
  call void @llvm.dbg.value(metadata i64 %17, metadata !947, metadata !DIExpression()), !dbg !1382
  call void @llvm.dbg.value(metadata double %16, metadata !966, metadata !DIExpression()), !dbg !1389
  call void @llvm.dbg.value(metadata ptr undef, metadata !974, metadata !DIExpression()), !dbg !1391
  call void @llvm.dbg.value(metadata i64 8, metadata !986, metadata !DIExpression()), !dbg !1391
  call void @llvm.dbg.value(metadata ptr undef, metadata !987, metadata !DIExpression()), !dbg !1391
  call void @llvm.dbg.value(metadata i64 8, metadata !988, metadata !DIExpression()), !dbg !1391
  %18 = bitcast double %16 to i64, !dbg !1393
  call void @llvm.dbg.value(metadata i64 %18, metadata !971, metadata !DIExpression()), !dbg !1389
  call void @llvm.dbg.value(metadata i64 %18, metadata !950, metadata !DIExpression()), !dbg !1382
  %19 = call double @llvm.fabs.f64(double %14), !dbg !1394
  %20 = bitcast double %19 to i64, !dbg !1394
  call void @llvm.dbg.value(metadata i64 %20, metadata !951, metadata !DIExpression()), !dbg !1382
  %21 = call double @llvm.fabs.f64(double %16), !dbg !1395
  %22 = bitcast double %21 to i64, !dbg !1395
  call void @llvm.dbg.value(metadata i64 %22, metadata !952, metadata !DIExpression()), !dbg !1382
  %23 = or i64 %22, %20, !dbg !1396
  %24 = icmp ult i64 %23, 4746794007248502784, !dbg !1397
  br i1 %24, label %25, label %33, !dbg !1398

25:                                               ; preds = %2
  call void @llvm.dbg.value(metadata i32 poison, metadata !953, metadata !DIExpression()), !dbg !1399
  %26 = fptosi double %16 to i32, !dbg !1400
  call void @llvm.dbg.value(metadata i32 %26, metadata !957, metadata !DIExpression()), !dbg !1399
  %27 = icmp eq i32 %26, 0, !dbg !1401
  br i1 %27, label %65, label %28, !dbg !1402

28:                                               ; preds = %25
  %29 = fptosi double %14 to i32, !dbg !1403
  call void @llvm.dbg.value(metadata i32 %29, metadata !953, metadata !DIExpression()), !dbg !1399
  %30 = srem i32 %29, %26, !dbg !1404
  call void @llvm.dbg.value(metadata i32 %30, metadata !958, metadata !DIExpression()), !dbg !1399
  %31 = call i32 @llvm.abs.i32(i32 %30, i1 true), !dbg !1405
  %32 = sitofp i32 %31 to double, !dbg !1406
  br label %65

33:                                               ; preds = %2
  %34 = icmp ugt i64 %22, 9218868437227405311
  %35 = icmp ugt i64 %20, 4890909195324358656
  %36 = or i1 %35, %34, !dbg !1407
  br i1 %36, label %65, label %37, !dbg !1407

37:                                               ; preds = %33
  %38 = icmp eq i64 %20, 4890909195324358656, !dbg !1408
  br i1 %38, label %39, label %43, !dbg !1409

39:                                               ; preds = %37
  %40 = icmp sgt i64 %17, -1, !dbg !1410
  %41 = icmp ugt i64 %22, 4890909195324358656
  %42 = or i1 %40, %41, !dbg !1411
  br i1 %42, label %65, label %45, !dbg !1411

43:                                               ; preds = %37
  %44 = icmp ugt i64 %22, 4890909195324358656, !dbg !1412
  br i1 %44, label %65, label %45, !dbg !1413

45:                                               ; preds = %43, %39
  %46 = icmp eq i64 %22, 4890909195324358656, !dbg !1414
  %47 = icmp sgt i64 %18, -1
  %48 = and i1 %47, %46, !dbg !1415
  br i1 %48, label %65, label %49, !dbg !1415

49:                                               ; preds = %45
  %50 = fptosi double %14 to i64, !dbg !1416
  call void @llvm.dbg.value(metadata i64 %50, metadata !959, metadata !DIExpression()), !dbg !1382
  %51 = fptosi double %16 to i64, !dbg !1417
  call void @llvm.dbg.value(metadata i64 %51, metadata !961, metadata !DIExpression()), !dbg !1382
  call void @llvm.dbg.value(metadata i64 -9223372036854775808, metadata !962, metadata !DIExpression()), !dbg !1382
  %52 = icmp eq i64 %51, 0, !dbg !1418
  br i1 %52, label %65, label %53, !dbg !1419

53:                                               ; preds = %49
  %54 = icmp eq i64 %50, -9223372036854775808, !dbg !1420
  %55 = icmp eq i64 %51, -1
  %56 = and i1 %54, %55, !dbg !1421
  br i1 %56, label %65, label %57, !dbg !1421

57:                                               ; preds = %53
  %58 = srem i64 %50, %51, !dbg !1422
  %59 = sitofp i64 %58 to double, !dbg !1423
  call void @llvm.dbg.value(metadata double %59, metadata !963, metadata !DIExpression()), !dbg !1382
  %60 = icmp ult i64 %20, 4746794007248502784, !dbg !1424
  %61 = icmp ult i64 %22, 4746794007248502784
  %62 = and i1 %60, %61, !dbg !1425
  %63 = call fast double @llvm.fabs.f64(double %59), !dbg !1425
  %64 = select fast i1 %62, double %63, double %59, !dbg !1425
  br label %65

65:                                               ; preds = %25, %28, %33, %39, %43, %45, %49, %53, %57
  %66 = phi double [ %32, %28 ], [ 0.000000e+00, %25 ], [ 0.000000e+00, %33 ], [ 0.000000e+00, %45 ], [ 0.000000e+00, %43 ], [ 0.000000e+00, %39 ], [ %64, %57 ], [ 0.000000e+00, %53 ], [ 0.000000e+00, %49 ], !dbg !1382
  store double %66, ptr %13, align 8, !dbg !1381, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1426
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1426
  ret void, !dbg !1426
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_pow_op(ptr nocapture noundef readonly %0, ptr noundef %1) #3 !dbg !1427 {
  %3 = alloca double, align 8, !DIAssignID !1434
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1431, metadata !DIExpression(), metadata !1434, metadata ptr %3, metadata !DIExpression()), !dbg !1435
  %4 = alloca ptr, align 8, !DIAssignID !1436
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1432, metadata !DIExpression(), metadata !1436, metadata ptr %4, metadata !DIExpression()), !dbg !1435
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1429, metadata !DIExpression()), !dbg !1435
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1430, metadata !DIExpression()), !dbg !1435
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1437
  store double 0.000000e+00, ptr %3, align 8, !dbg !1438, !tbaa !312, !DIAssignID !1439
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1431, metadata !DIExpression(), metadata !1439, metadata ptr %3, metadata !DIExpression()), !dbg !1435
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1440
  store ptr %3, ptr %4, align 8, !dbg !1441, !tbaa !300, !DIAssignID !1442
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1432, metadata !DIExpression(), metadata !1442, metadata ptr %4, metadata !DIExpression()), !dbg !1435
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1443
  %6 = load ptr, ptr %5, align 8, !dbg !1443, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1443, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1443, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef %1) #9, !dbg !1443
  %9 = load ptr, ptr %5, align 8, !dbg !1444, !tbaa !368
  %10 = getelementptr inbounds ptr, ptr %9, i64 1, !dbg !1444
  %11 = load ptr, ptr %10, align 8, !dbg !1444, !tbaa !300
  %12 = load ptr, ptr %11, align 8, !dbg !1444, !tbaa !344
  call void %12(ptr noundef nonnull %11, ptr noundef nonnull %4) #9, !dbg !1444
  %13 = load ptr, ptr %1, align 8, !dbg !1445, !tbaa !300
  %14 = load double, ptr %13, align 8, !dbg !1447, !tbaa !312
  %15 = call fast double @llvm.fabs.f64(double %14), !dbg !1448
  %16 = fcmp fast olt double %15, 1.000000e-05, !dbg !1449
  %17 = load ptr, ptr %4, align 8, !dbg !1450, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !1451, !tbaa !312
  %19 = fcmp fast olt double %18, 0.000000e+00
  %20 = select i1 %16, i1 %19, i1 false, !dbg !1452
  %21 = call fast double @llvm.pow.f64(double %14, double %18), !dbg !1452
  %22 = select i1 %20, double 0.000000e+00, double %21, !dbg !1452
  store double %22, ptr %13, align 8, !dbg !1435, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1453
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1453
  ret void, !dbg !1453
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.pow.f64(double, double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sin(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1454 {
  %3 = alloca ptr, align 8, !DIAssignID !1459
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1458, metadata !DIExpression(), metadata !1459, metadata ptr %3, metadata !DIExpression()), !dbg !1460
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1456, metadata !DIExpression()), !dbg !1460
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1457, metadata !DIExpression()), !dbg !1460
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1461
  store double 0.000000e+00, ptr %4, align 8, !dbg !1462, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1463
  store ptr %4, ptr %3, align 8, !dbg !1464, !tbaa !300, !DIAssignID !1465
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1458, metadata !DIExpression(), metadata !1465, metadata ptr %3, metadata !DIExpression()), !dbg !1460
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1466
  %6 = load ptr, ptr %5, align 8, !dbg !1466, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1466, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1466, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1466
  %9 = load ptr, ptr %3, align 8, !dbg !1467, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1467, !tbaa !312
  %11 = call fast double @llvm.sin.f64(double %10), !dbg !1467
  %12 = load ptr, ptr %1, align 8, !dbg !1467, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1467, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1468
  ret void, !dbg !1468
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.sin.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_cos(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1469 {
  %3 = alloca ptr, align 8, !DIAssignID !1474
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1473, metadata !DIExpression(), metadata !1474, metadata ptr %3, metadata !DIExpression()), !dbg !1475
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1471, metadata !DIExpression()), !dbg !1475
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1472, metadata !DIExpression()), !dbg !1475
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1476
  store double 0.000000e+00, ptr %4, align 8, !dbg !1477, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1478
  store ptr %4, ptr %3, align 8, !dbg !1479, !tbaa !300, !DIAssignID !1480
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1473, metadata !DIExpression(), metadata !1480, metadata ptr %3, metadata !DIExpression()), !dbg !1475
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1481
  %6 = load ptr, ptr %5, align 8, !dbg !1481, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1481, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1481, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1481
  %9 = load ptr, ptr %3, align 8, !dbg !1482, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1482, !tbaa !312
  %11 = call fast double @llvm.cos.f64(double %10), !dbg !1482
  %12 = load ptr, ptr %1, align 8, !dbg !1482, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1482, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1483
  ret void, !dbg !1483
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.cos.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_tan(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1484 {
  %3 = alloca ptr, align 8, !DIAssignID !1489
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1488, metadata !DIExpression(), metadata !1489, metadata ptr %3, metadata !DIExpression()), !dbg !1490
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1486, metadata !DIExpression()), !dbg !1490
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1487, metadata !DIExpression()), !dbg !1490
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1491
  store double 0.000000e+00, ptr %4, align 8, !dbg !1492, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1493
  store ptr %4, ptr %3, align 8, !dbg !1494, !tbaa !300, !DIAssignID !1495
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1488, metadata !DIExpression(), metadata !1495, metadata ptr %3, metadata !DIExpression()), !dbg !1490
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1496
  %6 = load ptr, ptr %5, align 8, !dbg !1496, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1496, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1496, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1496
  %9 = load ptr, ptr %3, align 8, !dbg !1497, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1497, !tbaa !312
  %11 = call fast nofpclass(nan inf) double @tan(double noundef nofpclass(nan inf) %10) #10, !dbg !1497
  %12 = load ptr, ptr %1, align 8, !dbg !1497, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1497, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1498
  ret void, !dbg !1498
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare !dbg !1499 nofpclass(nan inf) double @tan(double noundef nofpclass(nan inf)) local_unnamed_addr #7

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_asin(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1503 {
  %3 = alloca ptr, align 8, !DIAssignID !1508
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1507, metadata !DIExpression(), metadata !1508, metadata ptr %3, metadata !DIExpression()), !dbg !1509
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1505, metadata !DIExpression()), !dbg !1509
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1506, metadata !DIExpression()), !dbg !1509
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1510
  store double 0.000000e+00, ptr %4, align 8, !dbg !1511, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1512
  store ptr %4, ptr %3, align 8, !dbg !1513, !tbaa !300, !DIAssignID !1514
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1507, metadata !DIExpression(), metadata !1514, metadata ptr %3, metadata !DIExpression()), !dbg !1509
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1515
  %6 = load ptr, ptr %5, align 8, !dbg !1515, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1515, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1515, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1515
  %9 = load ptr, ptr %3, align 8, !dbg !1516, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1518, !tbaa !312
  %11 = fcmp fast olt double %10, -1.000000e+00, !dbg !1519
  %12 = fcmp fast ogt double %10, 1.000000e+00
  %13 = select i1 %11, i1 true, i1 %12, !dbg !1520
  br i1 %13, label %16, label %14, !dbg !1520

14:                                               ; preds = %2
  %15 = call fast nofpclass(nan inf) double @asin(double noundef nofpclass(nan inf) %10) #10, !dbg !1521
  br label %16, !dbg !1522

16:                                               ; preds = %2, %14
  %17 = phi double [ %15, %14 ], [ 0.000000e+00, %2 ]
  %18 = load ptr, ptr %1, align 8, !dbg !1509, !tbaa !300
  store double %17, ptr %18, align 8, !dbg !1509, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1522
  ret void, !dbg !1522
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare !dbg !1523 nofpclass(nan inf) double @asin(double noundef nofpclass(nan inf)) local_unnamed_addr #7

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_acos(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1524 {
  %3 = alloca ptr, align 8, !DIAssignID !1529
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1528, metadata !DIExpression(), metadata !1529, metadata ptr %3, metadata !DIExpression()), !dbg !1530
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1526, metadata !DIExpression()), !dbg !1530
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1527, metadata !DIExpression()), !dbg !1530
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1531
  store double 0.000000e+00, ptr %4, align 8, !dbg !1532, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1533
  store ptr %4, ptr %3, align 8, !dbg !1534, !tbaa !300, !DIAssignID !1535
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1528, metadata !DIExpression(), metadata !1535, metadata ptr %3, metadata !DIExpression()), !dbg !1530
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1536
  %6 = load ptr, ptr %5, align 8, !dbg !1536, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1536, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1536, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1536
  %9 = load ptr, ptr %3, align 8, !dbg !1537, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1539, !tbaa !312
  %11 = fcmp fast olt double %10, -1.000000e+00, !dbg !1540
  %12 = fcmp fast ogt double %10, 1.000000e+00
  %13 = select i1 %11, i1 true, i1 %12, !dbg !1541
  br i1 %13, label %16, label %14, !dbg !1541

14:                                               ; preds = %2
  %15 = call fast nofpclass(nan inf) double @acos(double noundef nofpclass(nan inf) %10) #10, !dbg !1542
  br label %16, !dbg !1543

16:                                               ; preds = %2, %14
  %17 = phi double [ %15, %14 ], [ 0.000000e+00, %2 ]
  %18 = load ptr, ptr %1, align 8, !dbg !1530, !tbaa !300
  store double %17, ptr %18, align 8, !dbg !1530, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1543
  ret void, !dbg !1543
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare !dbg !1544 nofpclass(nan inf) double @acos(double noundef nofpclass(nan inf)) local_unnamed_addr #7

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_atan(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1545 {
  %3 = alloca ptr, align 8, !DIAssignID !1550
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1549, metadata !DIExpression(), metadata !1550, metadata ptr %3, metadata !DIExpression()), !dbg !1551
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1547, metadata !DIExpression()), !dbg !1551
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1548, metadata !DIExpression()), !dbg !1551
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1552
  store double 0.000000e+00, ptr %4, align 8, !dbg !1553, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1554
  store ptr %4, ptr %3, align 8, !dbg !1555, !tbaa !300, !DIAssignID !1556
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1549, metadata !DIExpression(), metadata !1556, metadata ptr %3, metadata !DIExpression()), !dbg !1551
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1557
  %6 = load ptr, ptr %5, align 8, !dbg !1557, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1557, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1557, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1557
  %9 = load ptr, ptr %3, align 8, !dbg !1558, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1558, !tbaa !312
  %11 = call fast nofpclass(nan inf) double @atan(double noundef nofpclass(nan inf) %10) #10, !dbg !1558
  %12 = load ptr, ptr %1, align 8, !dbg !1558, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1558, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1559
  ret void, !dbg !1559
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare !dbg !1560 nofpclass(nan inf) double @atan(double noundef nofpclass(nan inf)) local_unnamed_addr #7

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_atan2(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1561 {
  %3 = alloca double, align 8, !DIAssignID !1569
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1565, metadata !DIExpression(), metadata !1569, metadata ptr %3, metadata !DIExpression()), !dbg !1570
  %4 = alloca double, align 8, !DIAssignID !1571
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1566, metadata !DIExpression(), metadata !1571, metadata ptr %4, metadata !DIExpression()), !dbg !1570
  %5 = alloca ptr, align 8, !DIAssignID !1572
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1567, metadata !DIExpression(), metadata !1572, metadata ptr %5, metadata !DIExpression()), !dbg !1570
  %6 = alloca ptr, align 8, !DIAssignID !1573
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1568, metadata !DIExpression(), metadata !1573, metadata ptr %6, metadata !DIExpression()), !dbg !1570
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1563, metadata !DIExpression()), !dbg !1570
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1564, metadata !DIExpression()), !dbg !1570
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1574
  store double 0.000000e+00, ptr %3, align 8, !dbg !1575, !tbaa !312, !DIAssignID !1576
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1565, metadata !DIExpression(), metadata !1576, metadata ptr %3, metadata !DIExpression()), !dbg !1570
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1577
  store double 0.000000e+00, ptr %4, align 8, !dbg !1578, !tbaa !312, !DIAssignID !1579
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1566, metadata !DIExpression(), metadata !1579, metadata ptr %4, metadata !DIExpression()), !dbg !1570
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1580
  store ptr %3, ptr %5, align 8, !dbg !1581, !tbaa !300, !DIAssignID !1582
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1567, metadata !DIExpression(), metadata !1582, metadata ptr %5, metadata !DIExpression()), !dbg !1570
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1583
  store ptr %4, ptr %6, align 8, !dbg !1584, !tbaa !300, !DIAssignID !1585
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1568, metadata !DIExpression(), metadata !1585, metadata ptr %6, metadata !DIExpression()), !dbg !1570
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1586
  %8 = load ptr, ptr %7, align 8, !dbg !1586, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1586, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1586, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1586
  %11 = load ptr, ptr %7, align 8, !dbg !1587, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1587
  %13 = load ptr, ptr %12, align 8, !dbg !1587, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1587, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1587
  %15 = load ptr, ptr %5, align 8, !dbg !1588, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1588, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !1588, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !1588, !tbaa !312
  %19 = call fast nofpclass(nan inf) double @atan2(double noundef nofpclass(nan inf) %16, double noundef nofpclass(nan inf) %18) #10, !dbg !1588
  %20 = load ptr, ptr %1, align 8, !dbg !1588, !tbaa !300
  store double %19, ptr %20, align 8, !dbg !1588, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1589
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1589
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1589
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1589
  ret void, !dbg !1589
}

; Function Attrs: mustprogress nofree nosync nounwind willreturn memory(none)
declare !dbg !1590 nofpclass(nan inf) double @atan2(double noundef nofpclass(nan inf), double noundef nofpclass(nan inf)) local_unnamed_addr #7

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sqrt(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1593 {
  %3 = alloca ptr, align 8, !DIAssignID !1598
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1597, metadata !DIExpression(), metadata !1598, metadata ptr %3, metadata !DIExpression()), !dbg !1599
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1595, metadata !DIExpression()), !dbg !1599
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1596, metadata !DIExpression()), !dbg !1599
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1600
  store double 0.000000e+00, ptr %4, align 8, !dbg !1601, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1602
  store ptr %4, ptr %3, align 8, !dbg !1603, !tbaa !300, !DIAssignID !1604
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1597, metadata !DIExpression(), metadata !1604, metadata ptr %3, metadata !DIExpression()), !dbg !1599
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1605
  %6 = load ptr, ptr %5, align 8, !dbg !1605, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1605, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1605, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1605
  %9 = load ptr, ptr %3, align 8, !dbg !1606, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1606, !tbaa !312
  %11 = call fast double @llvm.fabs.f64(double %10), !dbg !1606
  %12 = call fast double @llvm.sqrt.f64(double %11), !dbg !1606
  %13 = load ptr, ptr %1, align 8, !dbg !1606, !tbaa !300
  store double %12, ptr %13, align 8, !dbg !1606, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1607
  ret void, !dbg !1607
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.sqrt.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_pow(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1608 {
  %3 = alloca double, align 8, !DIAssignID !1617
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1612, metadata !DIExpression(), metadata !1617, metadata ptr %3, metadata !DIExpression()), !dbg !1618
  %4 = alloca double, align 8, !DIAssignID !1619
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1613, metadata !DIExpression(), metadata !1619, metadata ptr %4, metadata !DIExpression()), !dbg !1618
  %5 = alloca ptr, align 8, !DIAssignID !1620
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1614, metadata !DIExpression(), metadata !1620, metadata ptr %5, metadata !DIExpression()), !dbg !1618
  %6 = alloca ptr, align 8, !DIAssignID !1621
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1615, metadata !DIExpression(), metadata !1621, metadata ptr %6, metadata !DIExpression()), !dbg !1618
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1610, metadata !DIExpression()), !dbg !1618
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1611, metadata !DIExpression()), !dbg !1618
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1622
  store double 0.000000e+00, ptr %3, align 8, !dbg !1623, !tbaa !312, !DIAssignID !1624
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1612, metadata !DIExpression(), metadata !1624, metadata ptr %3, metadata !DIExpression()), !dbg !1618
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1625
  store double 0.000000e+00, ptr %4, align 8, !dbg !1626, !tbaa !312, !DIAssignID !1627
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1613, metadata !DIExpression(), metadata !1627, metadata ptr %4, metadata !DIExpression()), !dbg !1618
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1628
  store ptr %3, ptr %5, align 8, !dbg !1629, !tbaa !300, !DIAssignID !1630
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1614, metadata !DIExpression(), metadata !1630, metadata ptr %5, metadata !DIExpression()), !dbg !1618
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1631
  store ptr %4, ptr %6, align 8, !dbg !1632, !tbaa !300, !DIAssignID !1633
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1615, metadata !DIExpression(), metadata !1633, metadata ptr %6, metadata !DIExpression()), !dbg !1618
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1634
  %8 = load ptr, ptr %7, align 8, !dbg !1634, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1634, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1634, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1634
  %11 = load ptr, ptr %7, align 8, !dbg !1635, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1635
  %13 = load ptr, ptr %12, align 8, !dbg !1635, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1635, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1635
  %15 = load ptr, ptr %5, align 8, !dbg !1636, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1638, !tbaa !312
  %17 = call fast double @llvm.fabs.f64(double %16), !dbg !1639
  %18 = fcmp fast olt double %17, 1.000000e-05, !dbg !1640
  %19 = load ptr, ptr %6, align 8, !dbg !1641, !tbaa !300
  %20 = load double, ptr %19, align 8, !dbg !1642, !tbaa !312
  %21 = fcmp fast olt double %20, 0.000000e+00
  %22 = select i1 %18, i1 %21, i1 false, !dbg !1643
  %23 = call fast double @llvm.pow.f64(double %16, double %20), !dbg !1643
  %24 = select i1 %22, double 0.000000e+00, double %23, !dbg !1643
  %25 = load ptr, ptr %1, align 8, !dbg !1618, !tbaa !300
  store double %24, ptr %25, align 8, !dbg !1618, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1644
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1644
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1644
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1644
  ret void, !dbg !1644
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_exp(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1645 {
  %3 = alloca ptr, align 8, !DIAssignID !1650
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1649, metadata !DIExpression(), metadata !1650, metadata ptr %3, metadata !DIExpression()), !dbg !1651
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1647, metadata !DIExpression()), !dbg !1651
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1648, metadata !DIExpression()), !dbg !1651
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1652
  store double 0.000000e+00, ptr %4, align 8, !dbg !1653, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1654
  store ptr %4, ptr %3, align 8, !dbg !1655, !tbaa !300, !DIAssignID !1656
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1649, metadata !DIExpression(), metadata !1656, metadata ptr %3, metadata !DIExpression()), !dbg !1651
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1657
  %6 = load ptr, ptr %5, align 8, !dbg !1657, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1657, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1657, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1657
  %9 = load ptr, ptr %3, align 8, !dbg !1658, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1658, !tbaa !312
  %11 = call fast double @llvm.exp.f64(double %10), !dbg !1658
  %12 = load ptr, ptr %1, align 8, !dbg !1658, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1658, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1659
  ret void, !dbg !1659
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.exp.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_log(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1660 {
  %3 = alloca ptr, align 8, !DIAssignID !1665
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1664, metadata !DIExpression(), metadata !1665, metadata ptr %3, metadata !DIExpression()), !dbg !1666
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1662, metadata !DIExpression()), !dbg !1666
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1663, metadata !DIExpression()), !dbg !1666
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1667
  store double 0.000000e+00, ptr %4, align 8, !dbg !1668, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1669
  store ptr %4, ptr %3, align 8, !dbg !1670, !tbaa !300, !DIAssignID !1671
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1664, metadata !DIExpression(), metadata !1671, metadata ptr %3, metadata !DIExpression()), !dbg !1666
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1672
  %6 = load ptr, ptr %5, align 8, !dbg !1672, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1672, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1672, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1672
  %9 = load ptr, ptr %3, align 8, !dbg !1673, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1675, !tbaa !312
  %11 = fcmp fast ugt double %10, 0.000000e+00, !dbg !1676
  %12 = call fast double @llvm.log.f64(double %10), !dbg !1677
  %13 = select i1 %11, double %12, double 0.000000e+00, !dbg !1677
  %14 = load ptr, ptr %1, align 8, !dbg !1666, !tbaa !300
  store double %13, ptr %14, align 8, !dbg !1666, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1678
  ret void, !dbg !1678
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.log.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_log10(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1679 {
  %3 = alloca ptr, align 8, !DIAssignID !1684
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1683, metadata !DIExpression(), metadata !1684, metadata ptr %3, metadata !DIExpression()), !dbg !1685
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1681, metadata !DIExpression()), !dbg !1685
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1682, metadata !DIExpression()), !dbg !1685
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1686
  store double 0.000000e+00, ptr %4, align 8, !dbg !1687, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1688
  store ptr %4, ptr %3, align 8, !dbg !1689, !tbaa !300, !DIAssignID !1690
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1683, metadata !DIExpression(), metadata !1690, metadata ptr %3, metadata !DIExpression()), !dbg !1685
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1691
  %6 = load ptr, ptr %5, align 8, !dbg !1691, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1691, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1691, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1691
  %9 = load ptr, ptr %3, align 8, !dbg !1692, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1694, !tbaa !312
  %11 = fcmp fast ugt double %10, 0.000000e+00, !dbg !1695
  %12 = call fast double @llvm.log10.f64(double %10), !dbg !1696
  %13 = select i1 %11, double %12, double 0.000000e+00, !dbg !1696
  %14 = load ptr, ptr %1, align 8, !dbg !1685, !tbaa !300
  store double %13, ptr %14, align 8, !dbg !1685, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1697
  ret void, !dbg !1697
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.log10.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_floor(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1698 {
  %3 = alloca ptr, align 8, !DIAssignID !1703
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1702, metadata !DIExpression(), metadata !1703, metadata ptr %3, metadata !DIExpression()), !dbg !1704
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1700, metadata !DIExpression()), !dbg !1704
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1701, metadata !DIExpression()), !dbg !1704
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1705
  store double 0.000000e+00, ptr %4, align 8, !dbg !1706, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1707
  store ptr %4, ptr %3, align 8, !dbg !1708, !tbaa !300, !DIAssignID !1709
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1702, metadata !DIExpression(), metadata !1709, metadata ptr %3, metadata !DIExpression()), !dbg !1704
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1710
  %6 = load ptr, ptr %5, align 8, !dbg !1710, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1710, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1710, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1710
  %9 = load ptr, ptr %3, align 8, !dbg !1711, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1711, !tbaa !312
  %11 = call fast double @llvm.floor.f64(double %10), !dbg !1711
  %12 = load ptr, ptr %1, align 8, !dbg !1711, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1711, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1712
  ret void, !dbg !1712
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.floor.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_ceil(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1713 {
  %3 = alloca ptr, align 8, !DIAssignID !1718
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1717, metadata !DIExpression(), metadata !1718, metadata ptr %3, metadata !DIExpression()), !dbg !1719
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1715, metadata !DIExpression()), !dbg !1719
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1716, metadata !DIExpression()), !dbg !1719
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1720
  store double 0.000000e+00, ptr %4, align 8, !dbg !1721, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1722
  store ptr %4, ptr %3, align 8, !dbg !1723, !tbaa !300, !DIAssignID !1724
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1717, metadata !DIExpression(), metadata !1724, metadata ptr %3, metadata !DIExpression()), !dbg !1719
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1725
  %6 = load ptr, ptr %5, align 8, !dbg !1725, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1725, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1725, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1725
  %9 = load ptr, ptr %3, align 8, !dbg !1726, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1726, !tbaa !312
  %11 = call fast double @llvm.ceil.f64(double %10), !dbg !1726
  %12 = load ptr, ptr %1, align 8, !dbg !1726, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1726, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1727
  ret void, !dbg !1727
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.ceil.f64(double) #5

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sigmoid(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1728 {
  %3 = alloca double, align 8, !DIAssignID !1737
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1732, metadata !DIExpression(), metadata !1737, metadata ptr %3, metadata !DIExpression()), !dbg !1738
  %4 = alloca double, align 8, !DIAssignID !1739
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1733, metadata !DIExpression(), metadata !1739, metadata ptr %4, metadata !DIExpression()), !dbg !1738
  %5 = alloca ptr, align 8, !DIAssignID !1740
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1734, metadata !DIExpression(), metadata !1740, metadata ptr %5, metadata !DIExpression()), !dbg !1738
  %6 = alloca ptr, align 8, !DIAssignID !1741
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1735, metadata !DIExpression(), metadata !1741, metadata ptr %6, metadata !DIExpression()), !dbg !1738
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1730, metadata !DIExpression()), !dbg !1738
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1731, metadata !DIExpression()), !dbg !1738
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1742
  store double 0.000000e+00, ptr %3, align 8, !dbg !1743, !tbaa !312, !DIAssignID !1744
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1732, metadata !DIExpression(), metadata !1744, metadata ptr %3, metadata !DIExpression()), !dbg !1738
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1745
  store double 0.000000e+00, ptr %4, align 8, !dbg !1746, !tbaa !312, !DIAssignID !1747
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1733, metadata !DIExpression(), metadata !1747, metadata ptr %4, metadata !DIExpression()), !dbg !1738
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1748
  store ptr %3, ptr %5, align 8, !dbg !1749, !tbaa !300, !DIAssignID !1750
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1734, metadata !DIExpression(), metadata !1750, metadata ptr %5, metadata !DIExpression()), !dbg !1738
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1751
  store ptr %4, ptr %6, align 8, !dbg !1752, !tbaa !300, !DIAssignID !1753
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1735, metadata !DIExpression(), metadata !1753, metadata ptr %6, metadata !DIExpression()), !dbg !1738
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1754
  %8 = load ptr, ptr %7, align 8, !dbg !1754, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1754, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1754, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1754
  %11 = load ptr, ptr %7, align 8, !dbg !1755, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1755
  %13 = load ptr, ptr %12, align 8, !dbg !1755, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1755, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1755
  %15 = load ptr, ptr %5, align 8, !dbg !1756, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1757, !tbaa !312
  %17 = fneg fast double %16, !dbg !1758
  %18 = load ptr, ptr %6, align 8, !dbg !1759, !tbaa !300
  %19 = load double, ptr %18, align 8, !dbg !1760, !tbaa !312
  %20 = fmul fast double %19, %17, !dbg !1761
  %21 = call fast double @llvm.exp.f64(double %20), !dbg !1762
  %22 = fadd fast double %21, 1.000000e+00, !dbg !1763
  tail call void @llvm.dbg.value(metadata double %22, metadata !1736, metadata !DIExpression()), !dbg !1738
  %23 = fcmp fast ogt double %22, 1.000000e-05, !dbg !1764
  %24 = fdiv fast double 1.000000e+00, %22, !dbg !1764
  %25 = select fast i1 %23, double %24, double 0.000000e+00, !dbg !1764
  %26 = load ptr, ptr %1, align 8, !dbg !1764, !tbaa !300
  store double %25, ptr %26, align 8, !dbg !1764, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1765
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1765
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1765
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1765
  ret void, !dbg !1765
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sqr(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1766 {
  %3 = alloca ptr, align 8, !DIAssignID !1771
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1770, metadata !DIExpression(), metadata !1771, metadata ptr %3, metadata !DIExpression()), !dbg !1772
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1768, metadata !DIExpression()), !dbg !1772
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1769, metadata !DIExpression()), !dbg !1772
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1773
  store double 0.000000e+00, ptr %4, align 8, !dbg !1774, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1775
  store ptr %4, ptr %3, align 8, !dbg !1776, !tbaa !300, !DIAssignID !1777
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1770, metadata !DIExpression(), metadata !1777, metadata ptr %3, metadata !DIExpression()), !dbg !1772
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1778
  %6 = load ptr, ptr %5, align 8, !dbg !1778, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1778, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1778, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1778
  %9 = load ptr, ptr %3, align 8, !dbg !1779, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1779, !tbaa !312
  %11 = fmul fast double %10, %10, !dbg !1779
  %12 = load ptr, ptr %1, align 8, !dbg !1779, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1779, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1780
  ret void, !dbg !1780
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_abs(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1781 {
  %3 = alloca ptr, align 8, !DIAssignID !1786
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1785, metadata !DIExpression(), metadata !1786, metadata ptr %3, metadata !DIExpression()), !dbg !1787
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1783, metadata !DIExpression()), !dbg !1787
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1784, metadata !DIExpression()), !dbg !1787
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1788
  store double 0.000000e+00, ptr %4, align 8, !dbg !1789, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1790
  store ptr %4, ptr %3, align 8, !dbg !1791, !tbaa !300, !DIAssignID !1792
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1785, metadata !DIExpression(), metadata !1792, metadata ptr %3, metadata !DIExpression()), !dbg !1787
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1793
  %6 = load ptr, ptr %5, align 8, !dbg !1793, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1793, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1793, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1793
  %9 = load ptr, ptr %3, align 8, !dbg !1794, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1794, !tbaa !312
  %11 = call fast double @llvm.fabs.f64(double %10), !dbg !1794
  %12 = load ptr, ptr %1, align 8, !dbg !1794, !tbaa !300
  store double %11, ptr %12, align 8, !dbg !1794, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1795
  ret void, !dbg !1795
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_min(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1796 {
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
  %19 = call fast double @llvm.minnum.f64(double %16, double %18), !dbg !1823
  %20 = load ptr, ptr %1, align 8, !dbg !1823, !tbaa !300
  store double %19, ptr %20, align 8, !dbg !1823, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1824
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1824
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1824
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1824
  ret void, !dbg !1824
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_max(ptr nocapture noundef readonly %0, ptr nocapture noundef readonly %1) #3 !dbg !1825 {
  %3 = alloca double, align 8, !DIAssignID !1833
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1829, metadata !DIExpression(), metadata !1833, metadata ptr %3, metadata !DIExpression()), !dbg !1834
  %4 = alloca double, align 8, !DIAssignID !1835
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1830, metadata !DIExpression(), metadata !1835, metadata ptr %4, metadata !DIExpression()), !dbg !1834
  %5 = alloca ptr, align 8, !DIAssignID !1836
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1831, metadata !DIExpression(), metadata !1836, metadata ptr %5, metadata !DIExpression()), !dbg !1834
  %6 = alloca ptr, align 8, !DIAssignID !1837
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1832, metadata !DIExpression(), metadata !1837, metadata ptr %6, metadata !DIExpression()), !dbg !1834
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1827, metadata !DIExpression()), !dbg !1834
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1828, metadata !DIExpression()), !dbg !1834
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1838
  store double 0.000000e+00, ptr %3, align 8, !dbg !1839, !tbaa !312, !DIAssignID !1840
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1829, metadata !DIExpression(), metadata !1840, metadata ptr %3, metadata !DIExpression()), !dbg !1834
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %4) #9, !dbg !1841
  store double 0.000000e+00, ptr %4, align 8, !dbg !1842, !tbaa !312, !DIAssignID !1843
  call void @llvm.dbg.assign(metadata double 0.000000e+00, metadata !1830, metadata !DIExpression(), metadata !1843, metadata ptr %4, metadata !DIExpression()), !dbg !1834
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %5) #9, !dbg !1844
  store ptr %3, ptr %5, align 8, !dbg !1845, !tbaa !300, !DIAssignID !1846
  call void @llvm.dbg.assign(metadata ptr %3, metadata !1831, metadata !DIExpression(), metadata !1846, metadata ptr %5, metadata !DIExpression()), !dbg !1834
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %6) #9, !dbg !1847
  store ptr %4, ptr %6, align 8, !dbg !1848, !tbaa !300, !DIAssignID !1849
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1832, metadata !DIExpression(), metadata !1849, metadata ptr %6, metadata !DIExpression()), !dbg !1834
  %7 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1850
  %8 = load ptr, ptr %7, align 8, !dbg !1850, !tbaa !368
  %9 = load ptr, ptr %8, align 8, !dbg !1850, !tbaa !300
  %10 = load ptr, ptr %9, align 8, !dbg !1850, !tbaa !344
  call void %10(ptr noundef nonnull %9, ptr noundef nonnull %5) #9, !dbg !1850
  %11 = load ptr, ptr %7, align 8, !dbg !1851, !tbaa !368
  %12 = getelementptr inbounds ptr, ptr %11, i64 1, !dbg !1851
  %13 = load ptr, ptr %12, align 8, !dbg !1851, !tbaa !300
  %14 = load ptr, ptr %13, align 8, !dbg !1851, !tbaa !344
  call void %14(ptr noundef nonnull %13, ptr noundef nonnull %6) #9, !dbg !1851
  %15 = load ptr, ptr %5, align 8, !dbg !1852, !tbaa !300
  %16 = load double, ptr %15, align 8, !dbg !1852, !tbaa !312
  %17 = load ptr, ptr %6, align 8, !dbg !1852, !tbaa !300
  %18 = load double, ptr %17, align 8, !dbg !1852, !tbaa !312
  %19 = call fast double @llvm.maxnum.f64(double %16, double %18), !dbg !1852
  %20 = load ptr, ptr %1, align 8, !dbg !1852, !tbaa !300
  store double %19, ptr %20, align 8, !dbg !1852, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %6) #9, !dbg !1853
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %5) #9, !dbg !1853
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %4) #9, !dbg !1853
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1853
  ret void, !dbg !1853
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_sign(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1854 {
  %3 = alloca ptr, align 8, !DIAssignID !1859
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1858, metadata !DIExpression(), metadata !1859, metadata ptr %3, metadata !DIExpression()), !dbg !1860
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1856, metadata !DIExpression()), !dbg !1860
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1857, metadata !DIExpression()), !dbg !1860
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1861
  store double 0.000000e+00, ptr %4, align 8, !dbg !1862, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1863
  store ptr %4, ptr %3, align 8, !dbg !1864, !tbaa !300, !DIAssignID !1865
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1858, metadata !DIExpression(), metadata !1865, metadata ptr %3, metadata !DIExpression()), !dbg !1860
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1866
  %6 = load ptr, ptr %5, align 8, !dbg !1866, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1866, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1866, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1866
  %9 = load ptr, ptr %3, align 8, !dbg !1867, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1869, !tbaa !312
  %11 = fcmp fast oeq double %10, 0.000000e+00, !dbg !1870
  %12 = fcmp fast olt double %10, 0.000000e+00, !dbg !1871
  %13 = select fast i1 %12, double -1.000000e+00, double 1.000000e+00, !dbg !1871
  %14 = select i1 %11, double 0.000000e+00, double %13, !dbg !1871
  %15 = load ptr, ptr %1, align 8, !dbg !1860, !tbaa !300
  store double %14, ptr %15, align 8, !dbg !1860, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1872
  ret void, !dbg !1872
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_rand(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !1873 {
  %3 = alloca ptr, align 8, !DIAssignID !1879
  call void @llvm.dbg.assign(metadata i1 undef, metadata !1877, metadata !DIExpression(), metadata !1879, metadata ptr %3, metadata !DIExpression()), !dbg !1880
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !1875, metadata !DIExpression()), !dbg !1880
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !1876, metadata !DIExpression()), !dbg !1880
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1881
  store double 0.000000e+00, ptr %4, align 8, !dbg !1882, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1883
  store ptr %4, ptr %3, align 8, !dbg !1884, !tbaa !300, !DIAssignID !1885
  call void @llvm.dbg.assign(metadata ptr %4, metadata !1877, metadata !DIExpression(), metadata !1885, metadata ptr %3, metadata !DIExpression()), !dbg !1880
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1886
  %6 = load ptr, ptr %5, align 8, !dbg !1886, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1886, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1886, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1886
  %9 = load ptr, ptr %3, align 8, !dbg !1887, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !1888, !tbaa !312
  tail call void @llvm.dbg.value(metadata double poison, metadata !1878, metadata !DIExpression()), !dbg !1880
  %11 = call align 4 ptr @llvm.threadlocal.address.p0(ptr align 4 @prjm_eval_genrand_int32.mti), !dbg !1889
  %12 = load i32, ptr %11, align 4, !dbg !1889, !tbaa !295
  %13 = icmp eq i32 %12, 0, !dbg !1889
  br i1 %13, label %14, label %31, !dbg !1891

14:                                               ; preds = %2
  call void @llvm.dbg.value(metadata i32 1094840333, metadata !244, metadata !DIExpression()), !dbg !1892
  %15 = call align 4 ptr @llvm.threadlocal.address.p0(ptr align 4 @prjm_eval_genrand_int32.mt), !dbg !1893
  store i32 1094840333, ptr %15, align 4, !dbg !1894, !tbaa !295
  store i32 1, ptr %11, align 4, !dbg !1895, !tbaa !295
  br label %16, !dbg !1897

16:                                               ; preds = %16, %14
  %17 = phi i32 [ 1, %14 ], [ %29, %16 ]
  %18 = add nsw i32 %17, -1, !dbg !1898
  %19 = sext i32 %18 to i64, !dbg !1901
  %20 = getelementptr inbounds [624 x i32], ptr %15, i64 0, i64 %19, !dbg !1901
  %21 = load i32, ptr %20, align 4, !dbg !1901, !tbaa !295
  %22 = lshr i32 %21, 30, !dbg !1902
  %23 = xor i32 %22, %21, !dbg !1903
  %24 = mul i32 %23, 1812433253, !dbg !1904
  %25 = sext i32 %17 to i64, !dbg !1905
  %26 = add i32 %24, %17, !dbg !1906
  %27 = getelementptr inbounds [624 x i32], ptr %15, i64 0, i64 %25, !dbg !1907
  store i32 %26, ptr %27, align 4, !dbg !1908, !tbaa !295
  %28 = load i32, ptr %11, align 4, !dbg !1909, !tbaa !295
  %29 = add nsw i32 %28, 1, !dbg !1909
  store i32 %29, ptr %11, align 4, !dbg !1895, !tbaa !295
  %30 = icmp slt i32 %28, 623, !dbg !1910
  br i1 %30, label %16, label %34, !dbg !1897, !llvm.loop !1911

31:                                               ; preds = %2
  %32 = icmp sgt i32 %12, 623, !dbg !1913
  %33 = call align 4 ptr @llvm.threadlocal.address.p0(ptr align 4 @prjm_eval_genrand_int32.mt)
  br i1 %32, label %34, label %132, !dbg !1914

34:                                               ; preds = %16, %31
  %35 = phi ptr [ %33, %31 ], [ %15, %16 ]
  call void @llvm.dbg.value(metadata i32 0, metadata !247, metadata !DIExpression()), !dbg !1915
  %36 = load i32, ptr %35, align 4, !dbg !1916, !tbaa !295
  br label %37, !dbg !1920

37:                                               ; preds = %37, %34
  %38 = phi i64 [ 0, %34 ], [ %75, %37 ], !dbg !1921
  %39 = phi i32 [ %36, %34 ], [ %48, %37 ]
  %40 = or disjoint i64 %38, 1, !dbg !1920
  %41 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %38, !dbg !1916
  %42 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %40, !dbg !1916
  %43 = or disjoint i64 %38, 1, !dbg !1921
  %44 = add i64 %38, 2, !dbg !1921
  %45 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %43, !dbg !1922
  %46 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %44, !dbg !1922
  %47 = load i32, ptr %45, align 4, !dbg !1922, !tbaa !295
  %48 = load i32, ptr %46, align 4, !dbg !1922, !tbaa !295
  %49 = and i32 %39, -2147483648, !dbg !1923
  %50 = and i32 %47, -2147483648, !dbg !1923
  %51 = and i32 %47, 2147483646, !dbg !1924
  %52 = and i32 %48, 2147483646, !dbg !1924
  %53 = or disjoint i32 %51, %49, !dbg !1925
  %54 = or disjoint i32 %52, %50, !dbg !1925
  %55 = add nuw nsw i64 %38, 397, !dbg !1926
  %56 = add i64 %38, 398, !dbg !1926
  %57 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %55, !dbg !1927
  %58 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %56, !dbg !1927
  %59 = load i32, ptr %57, align 4, !dbg !1927, !tbaa !295
  %60 = load i32, ptr %58, align 4, !dbg !1927, !tbaa !295
  %61 = lshr exact i32 %53, 1, !dbg !1928
  %62 = lshr exact i32 %54, 1, !dbg !1928
  %63 = and i32 %47, 1, !dbg !1929
  %64 = and i32 %48, 1, !dbg !1929
  %65 = zext nneg i32 %63 to i64, !dbg !1929
  %66 = zext nneg i32 %64 to i64, !dbg !1929
  %67 = getelementptr inbounds [2 x i32], ptr @prjm_eval_genrand_int32.mag01, i64 0, i64 %65, !dbg !1930
  %68 = getelementptr inbounds [2 x i32], ptr @prjm_eval_genrand_int32.mag01, i64 0, i64 %66, !dbg !1930
  %69 = load i32, ptr %67, align 4, !dbg !1930, !tbaa !295
  %70 = load i32, ptr %68, align 4, !dbg !1930, !tbaa !295
  %71 = xor i32 %69, %59, !dbg !1931
  %72 = xor i32 %70, %60, !dbg !1931
  %73 = xor i32 %71, %61, !dbg !1932
  %74 = xor i32 %72, %62, !dbg !1932
  store i32 %73, ptr %41, align 4, !dbg !1933, !tbaa !295
  store i32 %74, ptr %42, align 4, !dbg !1933, !tbaa !295
  %75 = add nuw i64 %38, 2, !dbg !1921
  %76 = icmp eq i64 %75, 226, !dbg !1921
  br i1 %76, label %77, label %37, !dbg !1921, !llvm.loop !1934

77:                                               ; preds = %37
  call void @llvm.dbg.value(metadata i64 226, metadata !247, metadata !DIExpression()), !dbg !1915
  %78 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 226, !dbg !1916
  %79 = and i32 %48, -2147483648, !dbg !1923
  %80 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 227, !dbg !1922
  %81 = load i32, ptr %80, align 4, !dbg !1922, !tbaa !295
  %82 = and i32 %81, 2147483646, !dbg !1924
  %83 = or disjoint i32 %82, %79, !dbg !1925
  call void @llvm.dbg.value(metadata !DIArgList(i32 %79, i32 %81), metadata !243, metadata !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 2147483647, DW_OP_and, DW_OP_or, DW_OP_stack_value)), !dbg !1938
  %84 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 623, !dbg !1927
  %85 = load i32, ptr %84, align 4, !dbg !1927, !tbaa !295
  %86 = lshr exact i32 %83, 1, !dbg !1928
  %87 = and i32 %81, 1, !dbg !1929
  %88 = zext nneg i32 %87 to i64, !dbg !1929
  %89 = getelementptr inbounds [2 x i32], ptr @prjm_eval_genrand_int32.mag01, i64 0, i64 %88, !dbg !1930
  %90 = load i32, ptr %89, align 4, !dbg !1930, !tbaa !295
  %91 = xor i32 %90, %85, !dbg !1931
  %92 = xor i32 %91, %86, !dbg !1932
  store i32 %92, ptr %78, align 4, !dbg !1933, !tbaa !295
  call void @llvm.dbg.value(metadata i64 227, metadata !247, metadata !DIExpression()), !dbg !1915
  call void @llvm.dbg.value(metadata i64 227, metadata !247, metadata !DIExpression(DW_OP_LLVM_convert, 64, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_stack_value)), !dbg !1915
  %93 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 227
  %94 = load i32, ptr %93, align 4, !dbg !1939, !tbaa !295
  br label %95, !dbg !1943

95:                                               ; preds = %95, %77
  %96 = phi i32 [ %94, %77 ], [ %102, %95 ], !dbg !1939
  %97 = phi i64 [ 227, %77 ], [ %100, %95 ]
  call void @llvm.dbg.value(metadata i64 %97, metadata !247, metadata !DIExpression()), !dbg !1915
  %98 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %97, !dbg !1939
  %99 = and i32 %96, -2147483648, !dbg !1944
  %100 = add nuw nsw i64 %97, 1, !dbg !1945
  %101 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %100, !dbg !1946
  %102 = load i32, ptr %101, align 4, !dbg !1946, !tbaa !295
  %103 = and i32 %102, 2147483646, !dbg !1947
  %104 = or disjoint i32 %103, %99, !dbg !1948
  call void @llvm.dbg.value(metadata !DIArgList(i32 %99, i32 %102), metadata !243, metadata !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 2147483647, DW_OP_and, DW_OP_or, DW_OP_stack_value)), !dbg !1938
  %105 = add nsw i64 %97, -227, !dbg !1949
  %106 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 %105, !dbg !1950
  %107 = load i32, ptr %106, align 4, !dbg !1950, !tbaa !295
  %108 = lshr exact i32 %104, 1, !dbg !1951
  %109 = and i32 %102, 1, !dbg !1952
  %110 = zext nneg i32 %109 to i64, !dbg !1952
  %111 = getelementptr inbounds [2 x i32], ptr @prjm_eval_genrand_int32.mag01, i64 0, i64 %110, !dbg !1953
  %112 = load i32, ptr %111, align 4, !dbg !1953, !tbaa !295
  %113 = xor i32 %112, %107, !dbg !1954
  %114 = xor i32 %113, %108, !dbg !1955
  store i32 %114, ptr %98, align 4, !dbg !1956, !tbaa !295
  call void @llvm.dbg.value(metadata i64 %100, metadata !247, metadata !DIExpression()), !dbg !1915
  %115 = icmp eq i64 %100, 623, !dbg !1957
  br i1 %115, label %116, label %95, !dbg !1943, !llvm.loop !1958

116:                                              ; preds = %95
  %117 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 623, !dbg !1960
  %118 = load i32, ptr %117, align 4, !dbg !1960, !tbaa !295
  %119 = and i32 %118, -2147483648, !dbg !1961
  %120 = load i32, ptr %35, align 4, !dbg !1962, !tbaa !295
  %121 = and i32 %120, 2147483646, !dbg !1963
  %122 = or disjoint i32 %121, %119, !dbg !1964
  call void @llvm.dbg.value(metadata !DIArgList(i32 %119, i32 %120), metadata !243, metadata !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 2147483647, DW_OP_and, DW_OP_or, DW_OP_stack_value)), !dbg !1938
  %123 = getelementptr inbounds [624 x i32], ptr %35, i64 0, i64 396, !dbg !1965
  %124 = load i32, ptr %123, align 4, !dbg !1965, !tbaa !295
  %125 = lshr exact i32 %122, 1, !dbg !1966
  %126 = and i32 %120, 1, !dbg !1967
  %127 = zext nneg i32 %126 to i64, !dbg !1967
  %128 = getelementptr inbounds [2 x i32], ptr @prjm_eval_genrand_int32.mag01, i64 0, i64 %127, !dbg !1968
  %129 = load i32, ptr %128, align 4, !dbg !1968, !tbaa !295
  %130 = xor i32 %129, %124, !dbg !1969
  %131 = xor i32 %130, %125, !dbg !1970
  store i32 %131, ptr %117, align 4, !dbg !1971, !tbaa !295
  br label %132, !dbg !1972

132:                                              ; preds = %31, %116
  %133 = phi ptr [ %35, %116 ], [ %33, %31 ], !dbg !1973
  %134 = phi i32 [ 0, %116 ], [ %12, %31 ], !dbg !1974
  %135 = call fast double @llvm.floor.f64(double %10), !dbg !1975
  tail call void @llvm.dbg.value(metadata double %135, metadata !1878, metadata !DIExpression()), !dbg !1880
  %136 = fcmp fast olt double %135, 1.000000e+00, !dbg !1976
  %137 = select i1 %136, double 1.000000e+00, double %135, !dbg !1978
  tail call void @llvm.dbg.value(metadata double %137, metadata !1878, metadata !DIExpression()), !dbg !1880
  %138 = add nsw i32 %134, 1, !dbg !1974
  store i32 %138, ptr %11, align 4, !dbg !1974, !tbaa !295
  %139 = sext i32 %134 to i64, !dbg !1973
  %140 = getelementptr inbounds [624 x i32], ptr %133, i64 0, i64 %139, !dbg !1973
  %141 = load i32, ptr %140, align 4, !dbg !1973, !tbaa !295
  call void @llvm.dbg.value(metadata i32 %141, metadata !243, metadata !DIExpression()), !dbg !1938
  %142 = lshr i32 %141, 11, !dbg !1979
  %143 = xor i32 %142, %141, !dbg !1980
  call void @llvm.dbg.value(metadata i32 %143, metadata !243, metadata !DIExpression()), !dbg !1938
  %144 = shl i32 %143, 7, !dbg !1981
  %145 = and i32 %144, -1658038656, !dbg !1982
  %146 = xor i32 %145, %143, !dbg !1983
  call void @llvm.dbg.value(metadata i32 %146, metadata !243, metadata !DIExpression()), !dbg !1938
  %147 = shl i32 %146, 15, !dbg !1984
  %148 = and i32 %147, -272236544, !dbg !1985
  %149 = xor i32 %148, %146, !dbg !1986
  call void @llvm.dbg.value(metadata i32 %149, metadata !243, metadata !DIExpression()), !dbg !1938
  %150 = lshr i32 %149, 18, !dbg !1987
  %151 = xor i32 %150, %149, !dbg !1988
  call void @llvm.dbg.value(metadata i32 %151, metadata !243, metadata !DIExpression()), !dbg !1938
  %152 = uitofp i32 %151 to double, !dbg !1989
  %153 = fmul fast double %137, 0x3DF0000000100000, !dbg !1989
  %154 = fmul fast double %153, %152, !dbg !1989
  %155 = load ptr, ptr %1, align 8, !dbg !1989, !tbaa !300
  store double %154, ptr %155, align 8, !dbg !1989, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !1990
  ret void, !dbg !1990
}

; Function Attrs: nounwind sspstrong uwtable
define hidden void @prjm_eval_func_invsqrt(ptr noundef %0, ptr nocapture noundef readonly %1) #3 !dbg !20 {
  %3 = alloca ptr, align 8, !DIAssignID !1991
  call void @llvm.dbg.assign(metadata i1 undef, metadata !60, metadata !DIExpression(), metadata !1991, metadata ptr %3, metadata !DIExpression()), !dbg !1992
  tail call void @llvm.dbg.value(metadata ptr %0, metadata !50, metadata !DIExpression()), !dbg !1992
  tail call void @llvm.dbg.value(metadata ptr %1, metadata !51, metadata !DIExpression()), !dbg !1992
  %4 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 1, !dbg !1993
  store double 0.000000e+00, ptr %4, align 8, !dbg !1994, !tbaa !309
  call void @llvm.lifetime.start.p0(i64 8, ptr nonnull %3) #9, !dbg !1995
  store ptr %4, ptr %3, align 8, !dbg !1996, !tbaa !300, !DIAssignID !1997
  call void @llvm.dbg.assign(metadata ptr %4, metadata !60, metadata !DIExpression(), metadata !1997, metadata ptr %3, metadata !DIExpression()), !dbg !1992
  %5 = getelementptr inbounds %struct.prjm_eval_exptreenode, ptr %0, i64 0, i32 3, !dbg !1998
  %6 = load ptr, ptr %5, align 8, !dbg !1998, !tbaa !368
  %7 = load ptr, ptr %6, align 8, !dbg !1998, !tbaa !300
  %8 = load ptr, ptr %7, align 8, !dbg !1998, !tbaa !344
  call void %8(ptr noundef nonnull %7, ptr noundef nonnull %3) #9, !dbg !1998
  %9 = load ptr, ptr %3, align 8, !dbg !1999, !tbaa !300
  %10 = load double, ptr %9, align 8, !dbg !2000, !tbaa !312
  tail call void @llvm.dbg.value(metadata double poison, metadata !61, metadata !DIExpression()), !dbg !1992
  tail call void @llvm.dbg.value(metadata double %10, metadata !52, metadata !DIExpression()), !dbg !1992
  %11 = bitcast double %10 to i64, !dbg !2001
  %12 = lshr i64 %11, 1, !dbg !2002
  %13 = sub nsw i64 6910469410427058089, %12, !dbg !2003
  %14 = bitcast i64 %13 to double, !dbg !2004
  tail call void @llvm.dbg.value(metadata double %14, metadata !52, metadata !DIExpression()), !dbg !1992
  %15 = fmul fast double %10, 5.000000e-01, !dbg !2005
  %16 = fmul fast double %14, %14, !dbg !2005
  %17 = fmul fast double %16, %15, !dbg !2005
  %18 = fsub fast double 1.500000e+00, %17, !dbg !2006
  %19 = fmul fast double %18, %14, !dbg !2007
  tail call void @llvm.dbg.value(metadata double %19, metadata !52, metadata !DIExpression()), !dbg !1992
  %20 = load ptr, ptr %1, align 8, !dbg !2008, !tbaa !300
  store double %19, ptr %20, align 8, !dbg !2008, !tbaa !312
  call void @llvm.lifetime.end.p0(i64 8, ptr nonnull %3) #9, !dbg !2009
  ret void, !dbg !2009
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
declare i32 @llvm.abs.i32(i32, i1 immarg) #8

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
!3 = !DIFile(filename: "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit/i04-bits-v3-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c", directory: "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit/arithmetic-proposal/i04-only/bits-v3/arm64")
!4 = !{!5, !11, !14, !13}
!5 = !DIDerivedType(tag: DW_TAG_typedef, name: "PRJM_EVAL_I", file: !6, line: 18, baseType: !7)
!6 = !DIFile(filename: "i04-bits-v3-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c", directory: "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit")
!7 = !DIDerivedType(tag: DW_TAG_typedef, name: "int64_t", file: !8, line: 67, baseType: !9)
!8 = !DIFile(filename: "Library/Android/sdk/ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/sysroot/usr/include/stdint.h", directory: "/Users/jneerdael")
!9 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int64_t", file: !8, line: 43, baseType: !10)
!10 = !DIBasicType(name: "long", size: 64, encoding: DW_ATE_signed)
!11 = !DIDerivedType(tag: DW_TAG_typedef, name: "PRJM_EVAL_F", file: !12, line: 22, baseType: !13)
!12 = !DIFile(filename: "i04-bits-v3-engine/vendor/projectm-eval/projectm-eval/api/projectm-eval.h", directory: "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit")
!13 = !DIBasicType(name: "double", size: 64, encoding: DW_ATE_float)
!14 = !DIDerivedType(tag: DW_TAG_typedef, name: "int32_t", file: !8, line: 64, baseType: !15)
!15 = !DIDerivedType(tag: DW_TAG_typedef, name: "__int32_t", file: !8, line: 40, baseType: !16)
!16 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!17 = !{!18, !63, !65, !71, !76, !81, !86, !88, !93, !98, !103, !105, !107, !112, !114, !116, !118, !120, !122, !124, !126, !128, !130, !132, !134, !136, !138, !140, !142, !144, !146, !148, !150, !152, !154, !156, !158, !160, !162, !164, !166, !168, !170, !172, !174, !176, !178, !180, !182, !184, !186, !188, !190, !192, !194, !196, !198, !200, !202, !204, !206, !208, !210, !212, !214, !216, !218, !220, !222, !224, !226, !228, !230, !232, !0, !234, !253, !258}
!18 = !DIGlobalVariableExpression(var: !19, expr: !DIExpression())
!19 = distinct !DIGlobalVariable(name: "three_halfs", scope: !20, file: !6, line: 1256, type: !62, isLocal: true, isDefinition: true)
!20 = distinct !DISubprogram(name: "prjm_eval_func_invsqrt", scope: !6, file: !6, line: 1234, type: !21, scopeLine: 1235, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !49)
!21 = !DISubroutineType(types: !22)
!22 = !{null, !23, !38}
!23 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !24, size: 64)
!24 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "prjm_eval_exptreenode", file: !25, line: 72, size: 320, elements: !26)
!25 = !DIFile(filename: "i04-bits-v3-engine/vendor/projectm-eval/projectm-eval/CompilerTypes.h", directory: "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit")
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
!50 = !DILocalVariable(name: "ctx", arg: 1, scope: !20, file: !6, line: 1234, type: !23)
!51 = !DILocalVariable(name: "ret_val", arg: 2, scope: !20, file: !6, line: 1234, type: !38)
!52 = !DILocalVariable(name: "type_conv", scope: !20, file: !6, line: 1254, type: !53)
!53 = distinct !DICompositeType(tag: DW_TAG_union_type, scope: !20, file: !6, line: 1250, size: 64, elements: !54)
!54 = !{!55, !56}
!55 = !DIDerivedType(tag: DW_TAG_member, name: "PRJM_F_val", scope: !53, file: !6, line: 1252, baseType: !11, size: 64)
!56 = !DIDerivedType(tag: DW_TAG_member, name: "int_val", scope: !53, file: !6, line: 1253, baseType: !57, size: 64)
!57 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint64_t", file: !8, line: 68, baseType: !58)
!58 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint64_t", file: !8, line: 44, baseType: !59)
!59 = !DIBasicType(name: "unsigned long", size: 64, encoding: DW_ATE_unsigned)
!60 = !DILocalVariable(name: "value_ptr", scope: !20, file: !6, line: 1261, type: !35)
!61 = !DILocalVariable(name: "num2", scope: !20, file: !6, line: 1265, type: !11)
!62 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !11)
!63 = !DIGlobalVariableExpression(var: !64, expr: !DIExpression())
!64 = distinct !DIGlobalVariable(name: "one_half", scope: !20, file: !6, line: 1257, type: !62, isLocal: true, isDefinition: true)
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
!505 = !DIFile(filename: "i04-bits-v3-engine/vendor/projectm-eval/projectm-eval/MemoryBuffer.h", directory: "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit")
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
!913 = distinct !DISubprogram(name: "prjm_eval_func_mod", scope: !6, file: !6, line: 660, type: !21, scopeLine: 661, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !914)
!914 = !{!915, !916, !917, !918, !919, !920}
!915 = !DILocalVariable(name: "ctx", arg: 1, scope: !913, file: !6, line: 660, type: !23)
!916 = !DILocalVariable(name: "ret_val", arg: 2, scope: !913, file: !6, line: 660, type: !38)
!917 = !DILocalVariable(name: "val1", scope: !913, file: !6, line: 664, type: !11)
!918 = !DILocalVariable(name: "val2", scope: !913, file: !6, line: 665, type: !11)
!919 = !DILocalVariable(name: "val1_ptr", scope: !913, file: !6, line: 666, type: !35)
!920 = !DILocalVariable(name: "val2_ptr", scope: !913, file: !6, line: 667, type: !35)
!921 = distinct !DIAssignID()
!922 = !DILocation(line: 0, scope: !913)
!923 = distinct !DIAssignID()
!924 = distinct !DIAssignID()
!925 = distinct !DIAssignID()
!926 = !DILocation(line: 664, column: 5, scope: !913)
!927 = !DILocation(line: 664, column: 17, scope: !913)
!928 = distinct !DIAssignID()
!929 = !DILocation(line: 665, column: 5, scope: !913)
!930 = !DILocation(line: 665, column: 17, scope: !913)
!931 = distinct !DIAssignID()
!932 = !DILocation(line: 666, column: 5, scope: !913)
!933 = !DILocation(line: 666, column: 18, scope: !913)
!934 = distinct !DIAssignID()
!935 = !DILocation(line: 667, column: 5, scope: !913)
!936 = !DILocation(line: 667, column: 18, scope: !913)
!937 = distinct !DIAssignID()
!938 = !DILocation(line: 669, column: 5, scope: !913)
!939 = !DILocation(line: 670, column: 5, scope: !913)
!940 = !DILocation(line: 672, column: 5, scope: !913)
!941 = !DILocalVariable(name: "numerator", arg: 1, scope: !942, file: !6, line: 618, type: !11)
!942 = distinct !DISubprogram(name: "bounded_milkdrop_remainder", scope: !6, file: !6, line: 618, type: !943, scopeLine: 619, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !945)
!943 = !DISubroutineType(types: !944)
!944 = !{!11, !11, !11}
!945 = !{!941, !946, !947, !950, !951, !952, !953, !957, !958, !959, !961, !962, !963}
!946 = !DILocalVariable(name: "denominator", arg: 2, scope: !942, file: !6, line: 618, type: !11)
!947 = !DILocalVariable(name: "numeratorBits", scope: !942, file: !6, line: 620, type: !948)
!948 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !949)
!949 = !DIDerivedType(tag: DW_TAG_typedef, name: "remainder_bits_t", file: !6, line: 603, baseType: !57)
!950 = !DILocalVariable(name: "denominatorBits", scope: !942, file: !6, line: 621, type: !948)
!951 = !DILocalVariable(name: "numeratorMagnitude", scope: !942, file: !6, line: 622, type: !948)
!952 = !DILocalVariable(name: "denominatorMagnitude", scope: !942, file: !6, line: 623, type: !948)
!953 = !DILocalVariable(name: "dividend32", scope: !954, file: !6, line: 629, type: !956)
!954 = distinct !DILexicalBlock(scope: !955, file: !6, line: 628, column: 5)
!955 = distinct !DILexicalBlock(scope: !942, file: !6, line: 627, column: 9)
!956 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !14)
!957 = !DILocalVariable(name: "divisor32", scope: !954, file: !6, line: 630, type: !956)
!958 = !DILocalVariable(name: "remainder32", scope: !954, file: !6, line: 633, type: !956)
!959 = !DILocalVariable(name: "dividend", scope: !942, file: !6, line: 646, type: !960)
!960 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !5)
!961 = !DILocalVariable(name: "divisor", scope: !942, file: !6, line: 647, type: !960)
!962 = !DILocalVariable(name: "minimum", scope: !942, file: !6, line: 651, type: !960)
!963 = !DILocalVariable(name: "remainder", scope: !942, file: !6, line: 655, type: !62)
!964 = !DILocation(line: 0, scope: !942, inlinedAt: !965)
!965 = distinct !DILocation(line: 672, column: 5, scope: !913)
!966 = !DILocalVariable(name: "value", arg: 1, scope: !967, file: !6, line: 609, type: !11)
!967 = distinct !DISubprogram(name: "remainder_value_bits", scope: !6, file: !6, line: 609, type: !968, scopeLine: 610, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !970)
!968 = !DISubroutineType(types: !969)
!969 = !{!949, !11}
!970 = !{!966, !971}
!971 = !DILocalVariable(name: "bits", scope: !967, file: !6, line: 611, type: !949)
!972 = !DILocation(line: 0, scope: !967, inlinedAt: !973)
!973 = distinct !DILocation(line: 620, column: 44, scope: !942, inlinedAt: !965)
!974 = !DILocalVariable(name: "dst", arg: 1, scope: !975, file: !976, line: 50, type: !980)
!975 = distinct !DISubprogram(name: "memcpy", linkageName: "_ZL6memcpyPvU17pass_object_size0PKvm", scope: !976, file: !976, line: 50, type: !977, scopeLine: 52, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !985)
!976 = !DIFile(filename: "Library/Android/sdk/ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/sysroot/usr/include/bits/fortify/string.h", directory: "/Users/jneerdael")
!977 = !DISubroutineType(types: !978)
!978 = !{!979, !980, !59, !981, !983}
!979 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!980 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !979)
!981 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !982, size: 64)
!982 = !DIDerivedType(tag: DW_TAG_const_type, baseType: null)
!983 = !DIDerivedType(tag: DW_TAG_typedef, name: "size_t", file: !984, line: 13, baseType: !59)
!984 = !DIFile(filename: "Library/Android/sdk/ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/lib/clang/18/include/__stddef_size_t.h", directory: "/Users/jneerdael")
!985 = !{!974, !986, !987, !988}
!986 = !DILocalVariable(arg: 2, scope: !975, type: !59, flags: DIFlagArtificial)
!987 = !DILocalVariable(name: "src", arg: 3, scope: !975, file: !976, line: 50, type: !981)
!988 = !DILocalVariable(name: "copy_amount", arg: 4, scope: !975, file: !976, line: 50, type: !983)
!989 = !DILocation(line: 0, scope: !975, inlinedAt: !990)
!990 = distinct !DILocation(line: 612, column: 5, scope: !967, inlinedAt: !973)
!991 = !DILocation(line: 53, column: 12, scope: !975, inlinedAt: !990)
!992 = !DILocation(line: 0, scope: !967, inlinedAt: !993)
!993 = distinct !DILocation(line: 621, column: 46, scope: !942, inlinedAt: !965)
!994 = !DILocation(line: 0, scope: !975, inlinedAt: !995)
!995 = distinct !DILocation(line: 612, column: 5, scope: !967, inlinedAt: !993)
!996 = !DILocation(line: 53, column: 12, scope: !975, inlinedAt: !995)
!997 = !DILocation(line: 622, column: 63, scope: !942, inlinedAt: !965)
!998 = !DILocation(line: 623, column: 67, scope: !942, inlinedAt: !965)
!999 = !DILocation(line: 627, column: 29, scope: !955, inlinedAt: !965)
!1000 = !DILocation(line: 627, column: 53, scope: !955, inlinedAt: !965)
!1001 = !DILocation(line: 627, column: 9, scope: !942, inlinedAt: !965)
!1002 = !DILocation(line: 0, scope: !954, inlinedAt: !965)
!1003 = !DILocation(line: 630, column: 35, scope: !954, inlinedAt: !965)
!1004 = !DILocation(line: 631, column: 23, scope: !1005, inlinedAt: !965)
!1005 = distinct !DILexicalBlock(scope: !954, file: !6, line: 631, column: 13)
!1006 = !DILocation(line: 631, column: 13, scope: !954, inlinedAt: !965)
!1007 = !DILocation(line: 629, column: 36, scope: !954, inlinedAt: !965)
!1008 = !DILocation(line: 633, column: 48, scope: !954, inlinedAt: !965)
!1009 = !DILocation(line: 635, column: 31, scope: !954, inlinedAt: !965)
!1010 = !DILocation(line: 635, column: 16, scope: !954, inlinedAt: !965)
!1011 = !DILocation(line: 637, column: 55, scope: !1012, inlinedAt: !965)
!1012 = distinct !DILexicalBlock(scope: !942, file: !6, line: 637, column: 9)
!1013 = !DILocation(line: 642, column: 29, scope: !1014, inlinedAt: !965)
!1014 = distinct !DILexicalBlock(scope: !942, file: !6, line: 641, column: 9)
!1015 = !DILocation(line: 642, column: 58, scope: !1014, inlinedAt: !965)
!1016 = !DILocation(line: 642, column: 77, scope: !1014, inlinedAt: !965)
!1017 = !DILocation(line: 642, column: 100, scope: !1014, inlinedAt: !965)
!1018 = !DILocation(line: 643, column: 30, scope: !1014, inlinedAt: !965)
!1019 = !DILocation(line: 643, column: 58, scope: !1014, inlinedAt: !965)
!1020 = !DILocation(line: 644, column: 31, scope: !1014, inlinedAt: !965)
!1021 = !DILocation(line: 644, column: 60, scope: !1014, inlinedAt: !965)
!1022 = !DILocation(line: 646, column: 34, scope: !942, inlinedAt: !965)
!1023 = !DILocation(line: 647, column: 33, scope: !942, inlinedAt: !965)
!1024 = !DILocation(line: 653, column: 17, scope: !1025, inlinedAt: !965)
!1025 = distinct !DILexicalBlock(scope: !942, file: !6, line: 653, column: 9)
!1026 = !DILocation(line: 653, column: 22, scope: !1025, inlinedAt: !965)
!1027 = !DILocation(line: 653, column: 35, scope: !1025, inlinedAt: !965)
!1028 = !DILocation(line: 653, column: 46, scope: !1025, inlinedAt: !965)
!1029 = !DILocation(line: 655, column: 59, scope: !942, inlinedAt: !965)
!1030 = !DILocation(line: 655, column: 35, scope: !942, inlinedAt: !965)
!1031 = !DILocation(line: 656, column: 31, scope: !942, inlinedAt: !965)
!1032 = !DILocation(line: 656, column: 63, scope: !942, inlinedAt: !965)
!1033 = !DILocation(line: 673, column: 1, scope: !913)
!1034 = distinct !DISubprogram(name: "prjm_eval_func_boolean_and_op", scope: !6, file: !6, line: 675, type: !21, scopeLine: 676, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1035)
!1035 = !{!1036, !1037, !1038, !1039, !1040, !1041}
!1036 = !DILocalVariable(name: "ctx", arg: 1, scope: !1034, file: !6, line: 675, type: !23)
!1037 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1034, file: !6, line: 675, type: !38)
!1038 = !DILocalVariable(name: "val1", scope: !1034, file: !6, line: 679, type: !11)
!1039 = !DILocalVariable(name: "val1_ptr", scope: !1034, file: !6, line: 680, type: !35)
!1040 = !DILocalVariable(name: "val2", scope: !1034, file: !6, line: 681, type: !11)
!1041 = !DILocalVariable(name: "val2_ptr", scope: !1034, file: !6, line: 682, type: !35)
!1042 = distinct !DIAssignID()
!1043 = !DILocation(line: 0, scope: !1034)
!1044 = distinct !DIAssignID()
!1045 = distinct !DIAssignID()
!1046 = distinct !DIAssignID()
!1047 = !DILocation(line: 679, column: 5, scope: !1034)
!1048 = !DILocation(line: 679, column: 17, scope: !1034)
!1049 = distinct !DIAssignID()
!1050 = !DILocation(line: 680, column: 5, scope: !1034)
!1051 = !DILocation(line: 680, column: 18, scope: !1034)
!1052 = distinct !DIAssignID()
!1053 = !DILocation(line: 681, column: 5, scope: !1034)
!1054 = !DILocation(line: 681, column: 17, scope: !1034)
!1055 = distinct !DIAssignID()
!1056 = !DILocation(line: 682, column: 5, scope: !1034)
!1057 = !DILocation(line: 682, column: 18, scope: !1034)
!1058 = distinct !DIAssignID()
!1059 = !DILocation(line: 688, column: 5, scope: !1034)
!1060 = !DILocation(line: 690, column: 15, scope: !1061)
!1061 = distinct !DILexicalBlock(scope: !1034, file: !6, line: 690, column: 9)
!1062 = !DILocation(line: 690, column: 14, scope: !1061)
!1063 = !DILocation(line: 690, column: 9, scope: !1061)
!1064 = !DILocation(line: 690, column: 25, scope: !1061)
!1065 = !DILocation(line: 690, column: 9, scope: !1034)
!1066 = !DILocation(line: 692, column: 9, scope: !1067)
!1067 = distinct !DILexicalBlock(scope: !1061, file: !6, line: 691, column: 5)
!1068 = !DILocation(line: 694, column: 9, scope: !1067)
!1069 = !DILocation(line: 695, column: 5, scope: !1067)
!1070 = !DILocation(line: 0, scope: !1061)
!1071 = !DILocation(line: 700, column: 1, scope: !1034)
!1072 = distinct !DISubprogram(name: "prjm_eval_func_boolean_or_op", scope: !6, file: !6, line: 702, type: !21, scopeLine: 703, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1073)
!1073 = !{!1074, !1075, !1076, !1077, !1078, !1079}
!1074 = !DILocalVariable(name: "ctx", arg: 1, scope: !1072, file: !6, line: 702, type: !23)
!1075 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1072, file: !6, line: 702, type: !38)
!1076 = !DILocalVariable(name: "val1", scope: !1072, file: !6, line: 706, type: !11)
!1077 = !DILocalVariable(name: "val1_ptr", scope: !1072, file: !6, line: 707, type: !35)
!1078 = !DILocalVariable(name: "val2", scope: !1072, file: !6, line: 708, type: !11)
!1079 = !DILocalVariable(name: "val2_ptr", scope: !1072, file: !6, line: 709, type: !35)
!1080 = distinct !DIAssignID()
!1081 = !DILocation(line: 0, scope: !1072)
!1082 = distinct !DIAssignID()
!1083 = distinct !DIAssignID()
!1084 = distinct !DIAssignID()
!1085 = !DILocation(line: 706, column: 5, scope: !1072)
!1086 = !DILocation(line: 706, column: 17, scope: !1072)
!1087 = distinct !DIAssignID()
!1088 = !DILocation(line: 707, column: 5, scope: !1072)
!1089 = !DILocation(line: 707, column: 18, scope: !1072)
!1090 = distinct !DIAssignID()
!1091 = !DILocation(line: 708, column: 5, scope: !1072)
!1092 = !DILocation(line: 708, column: 17, scope: !1072)
!1093 = distinct !DIAssignID()
!1094 = !DILocation(line: 709, column: 5, scope: !1072)
!1095 = !DILocation(line: 709, column: 18, scope: !1072)
!1096 = distinct !DIAssignID()
!1097 = !DILocation(line: 715, column: 5, scope: !1072)
!1098 = !DILocation(line: 717, column: 15, scope: !1099)
!1099 = distinct !DILexicalBlock(scope: !1072, file: !6, line: 717, column: 9)
!1100 = !DILocation(line: 717, column: 14, scope: !1099)
!1101 = !DILocation(line: 717, column: 9, scope: !1099)
!1102 = !DILocation(line: 717, column: 25, scope: !1099)
!1103 = !DILocation(line: 717, column: 9, scope: !1072)
!1104 = !DILocation(line: 719, column: 9, scope: !1105)
!1105 = distinct !DILexicalBlock(scope: !1099, file: !6, line: 718, column: 5)
!1106 = !DILocation(line: 721, column: 9, scope: !1105)
!1107 = !DILocation(line: 722, column: 5, scope: !1105)
!1108 = !DILocation(line: 0, scope: !1099)
!1109 = !DILocation(line: 727, column: 1, scope: !1072)
!1110 = distinct !DISubprogram(name: "prjm_eval_func_boolean_and_func", scope: !6, file: !6, line: 729, type: !21, scopeLine: 730, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1111)
!1111 = !{!1112, !1113, !1114, !1115, !1116, !1117}
!1112 = !DILocalVariable(name: "ctx", arg: 1, scope: !1110, file: !6, line: 729, type: !23)
!1113 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1110, file: !6, line: 729, type: !38)
!1114 = !DILocalVariable(name: "val1", scope: !1110, file: !6, line: 733, type: !11)
!1115 = !DILocalVariable(name: "val2", scope: !1110, file: !6, line: 734, type: !11)
!1116 = !DILocalVariable(name: "val1_ptr", scope: !1110, file: !6, line: 735, type: !35)
!1117 = !DILocalVariable(name: "val2_ptr", scope: !1110, file: !6, line: 736, type: !35)
!1118 = distinct !DIAssignID()
!1119 = !DILocation(line: 0, scope: !1110)
!1120 = distinct !DIAssignID()
!1121 = distinct !DIAssignID()
!1122 = distinct !DIAssignID()
!1123 = !DILocation(line: 733, column: 5, scope: !1110)
!1124 = !DILocation(line: 733, column: 17, scope: !1110)
!1125 = distinct !DIAssignID()
!1126 = !DILocation(line: 734, column: 5, scope: !1110)
!1127 = !DILocation(line: 734, column: 17, scope: !1110)
!1128 = distinct !DIAssignID()
!1129 = !DILocation(line: 735, column: 5, scope: !1110)
!1130 = !DILocation(line: 735, column: 18, scope: !1110)
!1131 = distinct !DIAssignID()
!1132 = !DILocation(line: 736, column: 5, scope: !1110)
!1133 = !DILocation(line: 736, column: 18, scope: !1110)
!1134 = distinct !DIAssignID()
!1135 = !DILocation(line: 738, column: 5, scope: !1110)
!1136 = !DILocation(line: 739, column: 5, scope: !1110)
!1137 = !DILocation(line: 742, column: 5, scope: !1110)
!1138 = !DILocation(line: 743, column: 1, scope: !1110)
!1139 = distinct !DISubprogram(name: "prjm_eval_func_boolean_or_func", scope: !6, file: !6, line: 745, type: !21, scopeLine: 746, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1140)
!1140 = !{!1141, !1142, !1143, !1144, !1145, !1146}
!1141 = !DILocalVariable(name: "ctx", arg: 1, scope: !1139, file: !6, line: 745, type: !23)
!1142 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1139, file: !6, line: 745, type: !38)
!1143 = !DILocalVariable(name: "val1", scope: !1139, file: !6, line: 749, type: !11)
!1144 = !DILocalVariable(name: "val2", scope: !1139, file: !6, line: 750, type: !11)
!1145 = !DILocalVariable(name: "val1_ptr", scope: !1139, file: !6, line: 751, type: !35)
!1146 = !DILocalVariable(name: "val2_ptr", scope: !1139, file: !6, line: 752, type: !35)
!1147 = distinct !DIAssignID()
!1148 = !DILocation(line: 0, scope: !1139)
!1149 = distinct !DIAssignID()
!1150 = distinct !DIAssignID()
!1151 = distinct !DIAssignID()
!1152 = !DILocation(line: 749, column: 5, scope: !1139)
!1153 = !DILocation(line: 749, column: 17, scope: !1139)
!1154 = distinct !DIAssignID()
!1155 = !DILocation(line: 750, column: 5, scope: !1139)
!1156 = !DILocation(line: 750, column: 17, scope: !1139)
!1157 = distinct !DIAssignID()
!1158 = !DILocation(line: 751, column: 5, scope: !1139)
!1159 = !DILocation(line: 751, column: 18, scope: !1139)
!1160 = distinct !DIAssignID()
!1161 = !DILocation(line: 752, column: 5, scope: !1139)
!1162 = !DILocation(line: 752, column: 18, scope: !1139)
!1163 = distinct !DIAssignID()
!1164 = !DILocation(line: 754, column: 5, scope: !1139)
!1165 = !DILocation(line: 755, column: 5, scope: !1139)
!1166 = !DILocation(line: 758, column: 5, scope: !1139)
!1167 = !DILocation(line: 759, column: 1, scope: !1139)
!1168 = distinct !DISubprogram(name: "prjm_eval_func_neg", scope: !6, file: !6, line: 761, type: !21, scopeLine: 762, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1169)
!1169 = !{!1170, !1171, !1172, !1173}
!1170 = !DILocalVariable(name: "ctx", arg: 1, scope: !1168, file: !6, line: 761, type: !23)
!1171 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1168, file: !6, line: 761, type: !38)
!1172 = !DILocalVariable(name: "val1", scope: !1168, file: !6, line: 765, type: !11)
!1173 = !DILocalVariable(name: "val1_ptr", scope: !1168, file: !6, line: 766, type: !35)
!1174 = distinct !DIAssignID()
!1175 = !DILocation(line: 0, scope: !1168)
!1176 = distinct !DIAssignID()
!1177 = !DILocation(line: 765, column: 5, scope: !1168)
!1178 = !DILocation(line: 765, column: 17, scope: !1168)
!1179 = distinct !DIAssignID()
!1180 = !DILocation(line: 766, column: 5, scope: !1168)
!1181 = !DILocation(line: 766, column: 18, scope: !1168)
!1182 = distinct !DIAssignID()
!1183 = !DILocation(line: 768, column: 5, scope: !1168)
!1184 = !DILocation(line: 770, column: 5, scope: !1168)
!1185 = !DILocation(line: 771, column: 1, scope: !1168)
!1186 = distinct !DISubprogram(name: "prjm_eval_func_add_op", scope: !6, file: !6, line: 773, type: !21, scopeLine: 774, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1187)
!1187 = !{!1188, !1189, !1190, !1191}
!1188 = !DILocalVariable(name: "ctx", arg: 1, scope: !1186, file: !6, line: 773, type: !23)
!1189 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1186, file: !6, line: 773, type: !38)
!1190 = !DILocalVariable(name: "val2", scope: !1186, file: !6, line: 777, type: !11)
!1191 = !DILocalVariable(name: "val2_ptr", scope: !1186, file: !6, line: 778, type: !35)
!1192 = distinct !DIAssignID()
!1193 = !DILocation(line: 0, scope: !1186)
!1194 = distinct !DIAssignID()
!1195 = !DILocation(line: 777, column: 5, scope: !1186)
!1196 = !DILocation(line: 777, column: 17, scope: !1186)
!1197 = distinct !DIAssignID()
!1198 = !DILocation(line: 778, column: 5, scope: !1186)
!1199 = !DILocation(line: 778, column: 18, scope: !1186)
!1200 = distinct !DIAssignID()
!1201 = !DILocation(line: 780, column: 5, scope: !1186)
!1202 = !DILocation(line: 781, column: 5, scope: !1186)
!1203 = !DILocation(line: 783, column: 5, scope: !1186)
!1204 = !DILocation(line: 784, column: 1, scope: !1186)
!1205 = distinct !DISubprogram(name: "prjm_eval_func_sub_op", scope: !6, file: !6, line: 786, type: !21, scopeLine: 787, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1206)
!1206 = !{!1207, !1208, !1209, !1210}
!1207 = !DILocalVariable(name: "ctx", arg: 1, scope: !1205, file: !6, line: 786, type: !23)
!1208 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1205, file: !6, line: 786, type: !38)
!1209 = !DILocalVariable(name: "val2", scope: !1205, file: !6, line: 790, type: !11)
!1210 = !DILocalVariable(name: "val2_ptr", scope: !1205, file: !6, line: 791, type: !35)
!1211 = distinct !DIAssignID()
!1212 = !DILocation(line: 0, scope: !1205)
!1213 = distinct !DIAssignID()
!1214 = !DILocation(line: 790, column: 5, scope: !1205)
!1215 = !DILocation(line: 790, column: 17, scope: !1205)
!1216 = distinct !DIAssignID()
!1217 = !DILocation(line: 791, column: 5, scope: !1205)
!1218 = !DILocation(line: 791, column: 18, scope: !1205)
!1219 = distinct !DIAssignID()
!1220 = !DILocation(line: 793, column: 5, scope: !1205)
!1221 = !DILocation(line: 794, column: 5, scope: !1205)
!1222 = !DILocation(line: 796, column: 5, scope: !1205)
!1223 = !DILocation(line: 797, column: 1, scope: !1205)
!1224 = distinct !DISubprogram(name: "prjm_eval_func_mul_op", scope: !6, file: !6, line: 799, type: !21, scopeLine: 800, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1225)
!1225 = !{!1226, !1227, !1228, !1229}
!1226 = !DILocalVariable(name: "ctx", arg: 1, scope: !1224, file: !6, line: 799, type: !23)
!1227 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1224, file: !6, line: 799, type: !38)
!1228 = !DILocalVariable(name: "val2", scope: !1224, file: !6, line: 803, type: !11)
!1229 = !DILocalVariable(name: "val2_ptr", scope: !1224, file: !6, line: 804, type: !35)
!1230 = distinct !DIAssignID()
!1231 = !DILocation(line: 0, scope: !1224)
!1232 = distinct !DIAssignID()
!1233 = !DILocation(line: 803, column: 5, scope: !1224)
!1234 = !DILocation(line: 803, column: 17, scope: !1224)
!1235 = distinct !DIAssignID()
!1236 = !DILocation(line: 804, column: 5, scope: !1224)
!1237 = !DILocation(line: 804, column: 18, scope: !1224)
!1238 = distinct !DIAssignID()
!1239 = !DILocation(line: 806, column: 5, scope: !1224)
!1240 = !DILocation(line: 807, column: 5, scope: !1224)
!1241 = !DILocation(line: 809, column: 5, scope: !1224)
!1242 = !DILocation(line: 810, column: 1, scope: !1224)
!1243 = distinct !DISubprogram(name: "prjm_eval_func_div_op", scope: !6, file: !6, line: 812, type: !21, scopeLine: 813, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1244)
!1244 = !{!1245, !1246, !1247, !1248}
!1245 = !DILocalVariable(name: "ctx", arg: 1, scope: !1243, file: !6, line: 812, type: !23)
!1246 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1243, file: !6, line: 812, type: !38)
!1247 = !DILocalVariable(name: "val2", scope: !1243, file: !6, line: 816, type: !11)
!1248 = !DILocalVariable(name: "val2_ptr", scope: !1243, file: !6, line: 817, type: !35)
!1249 = distinct !DIAssignID()
!1250 = !DILocation(line: 0, scope: !1243)
!1251 = distinct !DIAssignID()
!1252 = !DILocation(line: 816, column: 5, scope: !1243)
!1253 = !DILocation(line: 816, column: 17, scope: !1243)
!1254 = distinct !DIAssignID()
!1255 = !DILocation(line: 817, column: 5, scope: !1243)
!1256 = !DILocation(line: 817, column: 18, scope: !1243)
!1257 = distinct !DIAssignID()
!1258 = !DILocation(line: 819, column: 5, scope: !1243)
!1259 = !DILocation(line: 820, column: 5, scope: !1243)
!1260 = !DILocation(line: 822, column: 14, scope: !1261)
!1261 = distinct !DILexicalBlock(scope: !1243, file: !6, line: 822, column: 8)
!1262 = !DILocation(line: 822, column: 13, scope: !1261)
!1263 = !DILocation(line: 822, column: 8, scope: !1261)
!1264 = !DILocation(line: 822, column: 24, scope: !1261)
!1265 = !DILocation(line: 822, column: 8, scope: !1243)
!1266 = !DILocation(line: 828, column: 5, scope: !1243)
!1267 = !DILocation(line: 829, column: 1, scope: !1243)
!1268 = distinct !DISubprogram(name: "prjm_eval_func_bitwise_or_op", scope: !6, file: !6, line: 831, type: !21, scopeLine: 832, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1269)
!1269 = !{!1270, !1271, !1272, !1273}
!1270 = !DILocalVariable(name: "ctx", arg: 1, scope: !1268, file: !6, line: 831, type: !23)
!1271 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1268, file: !6, line: 831, type: !38)
!1272 = !DILocalVariable(name: "val2", scope: !1268, file: !6, line: 835, type: !11)
!1273 = !DILocalVariable(name: "val2_ptr", scope: !1268, file: !6, line: 836, type: !35)
!1274 = distinct !DIAssignID()
!1275 = !DILocation(line: 0, scope: !1268)
!1276 = distinct !DIAssignID()
!1277 = !DILocation(line: 835, column: 5, scope: !1268)
!1278 = !DILocation(line: 835, column: 17, scope: !1268)
!1279 = distinct !DIAssignID()
!1280 = !DILocation(line: 836, column: 5, scope: !1268)
!1281 = !DILocation(line: 836, column: 18, scope: !1268)
!1282 = distinct !DIAssignID()
!1283 = !DILocation(line: 838, column: 5, scope: !1268)
!1284 = !DILocation(line: 839, column: 5, scope: !1268)
!1285 = !DILocation(line: 841, column: 5, scope: !1268)
!1286 = !DILocation(line: 842, column: 1, scope: !1268)
!1287 = distinct !DISubprogram(name: "prjm_eval_func_bitwise_or", scope: !6, file: !6, line: 844, type: !21, scopeLine: 845, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1288)
!1288 = !{!1289, !1290, !1291, !1292, !1293, !1294}
!1289 = !DILocalVariable(name: "ctx", arg: 1, scope: !1287, file: !6, line: 844, type: !23)
!1290 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1287, file: !6, line: 844, type: !38)
!1291 = !DILocalVariable(name: "val1", scope: !1287, file: !6, line: 848, type: !11)
!1292 = !DILocalVariable(name: "val1_ptr", scope: !1287, file: !6, line: 849, type: !35)
!1293 = !DILocalVariable(name: "val2", scope: !1287, file: !6, line: 850, type: !11)
!1294 = !DILocalVariable(name: "val2_ptr", scope: !1287, file: !6, line: 851, type: !35)
!1295 = distinct !DIAssignID()
!1296 = !DILocation(line: 0, scope: !1287)
!1297 = distinct !DIAssignID()
!1298 = distinct !DIAssignID()
!1299 = distinct !DIAssignID()
!1300 = !DILocation(line: 848, column: 5, scope: !1287)
!1301 = !DILocation(line: 848, column: 17, scope: !1287)
!1302 = distinct !DIAssignID()
!1303 = !DILocation(line: 849, column: 5, scope: !1287)
!1304 = !DILocation(line: 849, column: 18, scope: !1287)
!1305 = distinct !DIAssignID()
!1306 = !DILocation(line: 850, column: 5, scope: !1287)
!1307 = !DILocation(line: 850, column: 17, scope: !1287)
!1308 = distinct !DIAssignID()
!1309 = !DILocation(line: 851, column: 5, scope: !1287)
!1310 = !DILocation(line: 851, column: 18, scope: !1287)
!1311 = distinct !DIAssignID()
!1312 = !DILocation(line: 853, column: 5, scope: !1287)
!1313 = !DILocation(line: 854, column: 5, scope: !1287)
!1314 = !DILocation(line: 856, column: 5, scope: !1287)
!1315 = !DILocation(line: 857, column: 1, scope: !1287)
!1316 = distinct !DISubprogram(name: "prjm_eval_func_bitwise_and_op", scope: !6, file: !6, line: 859, type: !21, scopeLine: 860, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1317)
!1317 = !{!1318, !1319, !1320, !1321}
!1318 = !DILocalVariable(name: "ctx", arg: 1, scope: !1316, file: !6, line: 859, type: !23)
!1319 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1316, file: !6, line: 859, type: !38)
!1320 = !DILocalVariable(name: "val2", scope: !1316, file: !6, line: 863, type: !11)
!1321 = !DILocalVariable(name: "val2_ptr", scope: !1316, file: !6, line: 864, type: !35)
!1322 = distinct !DIAssignID()
!1323 = !DILocation(line: 0, scope: !1316)
!1324 = distinct !DIAssignID()
!1325 = !DILocation(line: 863, column: 5, scope: !1316)
!1326 = !DILocation(line: 863, column: 17, scope: !1316)
!1327 = distinct !DIAssignID()
!1328 = !DILocation(line: 864, column: 5, scope: !1316)
!1329 = !DILocation(line: 864, column: 18, scope: !1316)
!1330 = distinct !DIAssignID()
!1331 = !DILocation(line: 866, column: 5, scope: !1316)
!1332 = !DILocation(line: 867, column: 5, scope: !1316)
!1333 = !DILocation(line: 869, column: 5, scope: !1316)
!1334 = !DILocation(line: 870, column: 1, scope: !1316)
!1335 = distinct !DISubprogram(name: "prjm_eval_func_bitwise_and", scope: !6, file: !6, line: 872, type: !21, scopeLine: 873, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1336)
!1336 = !{!1337, !1338, !1339, !1340, !1341, !1342}
!1337 = !DILocalVariable(name: "ctx", arg: 1, scope: !1335, file: !6, line: 872, type: !23)
!1338 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1335, file: !6, line: 872, type: !38)
!1339 = !DILocalVariable(name: "val1", scope: !1335, file: !6, line: 876, type: !11)
!1340 = !DILocalVariable(name: "val1_ptr", scope: !1335, file: !6, line: 877, type: !35)
!1341 = !DILocalVariable(name: "val2", scope: !1335, file: !6, line: 878, type: !11)
!1342 = !DILocalVariable(name: "val2_ptr", scope: !1335, file: !6, line: 879, type: !35)
!1343 = distinct !DIAssignID()
!1344 = !DILocation(line: 0, scope: !1335)
!1345 = distinct !DIAssignID()
!1346 = distinct !DIAssignID()
!1347 = distinct !DIAssignID()
!1348 = !DILocation(line: 876, column: 5, scope: !1335)
!1349 = !DILocation(line: 876, column: 17, scope: !1335)
!1350 = distinct !DIAssignID()
!1351 = !DILocation(line: 877, column: 5, scope: !1335)
!1352 = !DILocation(line: 877, column: 18, scope: !1335)
!1353 = distinct !DIAssignID()
!1354 = !DILocation(line: 878, column: 5, scope: !1335)
!1355 = !DILocation(line: 878, column: 17, scope: !1335)
!1356 = distinct !DIAssignID()
!1357 = !DILocation(line: 879, column: 5, scope: !1335)
!1358 = !DILocation(line: 879, column: 18, scope: !1335)
!1359 = distinct !DIAssignID()
!1360 = !DILocation(line: 881, column: 5, scope: !1335)
!1361 = !DILocation(line: 882, column: 5, scope: !1335)
!1362 = !DILocation(line: 884, column: 5, scope: !1335)
!1363 = !DILocation(line: 885, column: 1, scope: !1335)
!1364 = distinct !DISubprogram(name: "prjm_eval_func_mod_op", scope: !6, file: !6, line: 887, type: !21, scopeLine: 888, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1365)
!1365 = !{!1366, !1367, !1368, !1369}
!1366 = !DILocalVariable(name: "ctx", arg: 1, scope: !1364, file: !6, line: 887, type: !23)
!1367 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1364, file: !6, line: 887, type: !38)
!1368 = !DILocalVariable(name: "val2", scope: !1364, file: !6, line: 891, type: !11)
!1369 = !DILocalVariable(name: "val2_ptr", scope: !1364, file: !6, line: 892, type: !35)
!1370 = distinct !DIAssignID()
!1371 = !DILocation(line: 0, scope: !1364)
!1372 = distinct !DIAssignID()
!1373 = !DILocation(line: 891, column: 5, scope: !1364)
!1374 = !DILocation(line: 891, column: 17, scope: !1364)
!1375 = distinct !DIAssignID()
!1376 = !DILocation(line: 892, column: 5, scope: !1364)
!1377 = !DILocation(line: 892, column: 18, scope: !1364)
!1378 = distinct !DIAssignID()
!1379 = !DILocation(line: 894, column: 5, scope: !1364)
!1380 = !DILocation(line: 895, column: 5, scope: !1364)
!1381 = !DILocation(line: 897, column: 5, scope: !1364)
!1382 = !DILocation(line: 0, scope: !942, inlinedAt: !1383)
!1383 = distinct !DILocation(line: 897, column: 5, scope: !1364)
!1384 = !DILocation(line: 0, scope: !967, inlinedAt: !1385)
!1385 = distinct !DILocation(line: 620, column: 44, scope: !942, inlinedAt: !1383)
!1386 = !DILocation(line: 0, scope: !975, inlinedAt: !1387)
!1387 = distinct !DILocation(line: 612, column: 5, scope: !967, inlinedAt: !1385)
!1388 = !DILocation(line: 53, column: 12, scope: !975, inlinedAt: !1387)
!1389 = !DILocation(line: 0, scope: !967, inlinedAt: !1390)
!1390 = distinct !DILocation(line: 621, column: 46, scope: !942, inlinedAt: !1383)
!1391 = !DILocation(line: 0, scope: !975, inlinedAt: !1392)
!1392 = distinct !DILocation(line: 612, column: 5, scope: !967, inlinedAt: !1390)
!1393 = !DILocation(line: 53, column: 12, scope: !975, inlinedAt: !1392)
!1394 = !DILocation(line: 622, column: 63, scope: !942, inlinedAt: !1383)
!1395 = !DILocation(line: 623, column: 67, scope: !942, inlinedAt: !1383)
!1396 = !DILocation(line: 627, column: 29, scope: !955, inlinedAt: !1383)
!1397 = !DILocation(line: 627, column: 53, scope: !955, inlinedAt: !1383)
!1398 = !DILocation(line: 627, column: 9, scope: !942, inlinedAt: !1383)
!1399 = !DILocation(line: 0, scope: !954, inlinedAt: !1383)
!1400 = !DILocation(line: 630, column: 35, scope: !954, inlinedAt: !1383)
!1401 = !DILocation(line: 631, column: 23, scope: !1005, inlinedAt: !1383)
!1402 = !DILocation(line: 631, column: 13, scope: !954, inlinedAt: !1383)
!1403 = !DILocation(line: 629, column: 36, scope: !954, inlinedAt: !1383)
!1404 = !DILocation(line: 633, column: 48, scope: !954, inlinedAt: !1383)
!1405 = !DILocation(line: 635, column: 31, scope: !954, inlinedAt: !1383)
!1406 = !DILocation(line: 635, column: 16, scope: !954, inlinedAt: !1383)
!1407 = !DILocation(line: 637, column: 55, scope: !1012, inlinedAt: !1383)
!1408 = !DILocation(line: 642, column: 29, scope: !1014, inlinedAt: !1383)
!1409 = !DILocation(line: 642, column: 58, scope: !1014, inlinedAt: !1383)
!1410 = !DILocation(line: 642, column: 77, scope: !1014, inlinedAt: !1383)
!1411 = !DILocation(line: 642, column: 100, scope: !1014, inlinedAt: !1383)
!1412 = !DILocation(line: 643, column: 30, scope: !1014, inlinedAt: !1383)
!1413 = !DILocation(line: 643, column: 58, scope: !1014, inlinedAt: !1383)
!1414 = !DILocation(line: 644, column: 31, scope: !1014, inlinedAt: !1383)
!1415 = !DILocation(line: 644, column: 60, scope: !1014, inlinedAt: !1383)
!1416 = !DILocation(line: 646, column: 34, scope: !942, inlinedAt: !1383)
!1417 = !DILocation(line: 647, column: 33, scope: !942, inlinedAt: !1383)
!1418 = !DILocation(line: 653, column: 17, scope: !1025, inlinedAt: !1383)
!1419 = !DILocation(line: 653, column: 22, scope: !1025, inlinedAt: !1383)
!1420 = !DILocation(line: 653, column: 35, scope: !1025, inlinedAt: !1383)
!1421 = !DILocation(line: 653, column: 46, scope: !1025, inlinedAt: !1383)
!1422 = !DILocation(line: 655, column: 59, scope: !942, inlinedAt: !1383)
!1423 = !DILocation(line: 655, column: 35, scope: !942, inlinedAt: !1383)
!1424 = !DILocation(line: 656, column: 31, scope: !942, inlinedAt: !1383)
!1425 = !DILocation(line: 656, column: 63, scope: !942, inlinedAt: !1383)
!1426 = !DILocation(line: 898, column: 1, scope: !1364)
!1427 = distinct !DISubprogram(name: "prjm_eval_func_pow_op", scope: !6, file: !6, line: 900, type: !21, scopeLine: 901, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1428)
!1428 = !{!1429, !1430, !1431, !1432, !1433}
!1429 = !DILocalVariable(name: "ctx", arg: 1, scope: !1427, file: !6, line: 900, type: !23)
!1430 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1427, file: !6, line: 900, type: !38)
!1431 = !DILocalVariable(name: "val2", scope: !1427, file: !6, line: 904, type: !11)
!1432 = !DILocalVariable(name: "val2_ptr", scope: !1427, file: !6, line: 905, type: !35)
!1433 = !DILocalVariable(name: "result", scope: !1427, file: !6, line: 916, type: !11)
!1434 = distinct !DIAssignID()
!1435 = !DILocation(line: 0, scope: !1427)
!1436 = distinct !DIAssignID()
!1437 = !DILocation(line: 904, column: 5, scope: !1427)
!1438 = !DILocation(line: 904, column: 17, scope: !1427)
!1439 = distinct !DIAssignID()
!1440 = !DILocation(line: 905, column: 5, scope: !1427)
!1441 = !DILocation(line: 905, column: 18, scope: !1427)
!1442 = distinct !DIAssignID()
!1443 = !DILocation(line: 907, column: 5, scope: !1427)
!1444 = !DILocation(line: 908, column: 5, scope: !1427)
!1445 = !DILocation(line: 910, column: 14, scope: !1446)
!1446 = distinct !DILexicalBlock(scope: !1427, file: !6, line: 910, column: 8)
!1447 = !DILocation(line: 910, column: 13, scope: !1446)
!1448 = !DILocation(line: 910, column: 8, scope: !1446)
!1449 = !DILocation(line: 910, column: 24, scope: !1446)
!1450 = !DILocation(line: 916, column: 42, scope: !1427)
!1451 = !DILocation(line: 916, column: 41, scope: !1427)
!1452 = !DILocation(line: 910, column: 46, scope: !1446)
!1453 = !DILocation(line: 919, column: 1, scope: !1427)
!1454 = distinct !DISubprogram(name: "prjm_eval_func_sin", scope: !6, file: !6, line: 923, type: !21, scopeLine: 924, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1455)
!1455 = !{!1456, !1457, !1458}
!1456 = !DILocalVariable(name: "ctx", arg: 1, scope: !1454, file: !6, line: 923, type: !23)
!1457 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1454, file: !6, line: 923, type: !38)
!1458 = !DILocalVariable(name: "math_arg_ptr", scope: !1454, file: !6, line: 928, type: !35)
!1459 = distinct !DIAssignID()
!1460 = !DILocation(line: 0, scope: !1454)
!1461 = !DILocation(line: 927, column: 10, scope: !1454)
!1462 = !DILocation(line: 927, column: 16, scope: !1454)
!1463 = !DILocation(line: 928, column: 5, scope: !1454)
!1464 = !DILocation(line: 928, column: 18, scope: !1454)
!1465 = distinct !DIAssignID()
!1466 = !DILocation(line: 930, column: 5, scope: !1454)
!1467 = !DILocation(line: 932, column: 5, scope: !1454)
!1468 = !DILocation(line: 933, column: 1, scope: !1454)
!1469 = distinct !DISubprogram(name: "prjm_eval_func_cos", scope: !6, file: !6, line: 935, type: !21, scopeLine: 936, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1470)
!1470 = !{!1471, !1472, !1473}
!1471 = !DILocalVariable(name: "ctx", arg: 1, scope: !1469, file: !6, line: 935, type: !23)
!1472 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1469, file: !6, line: 935, type: !38)
!1473 = !DILocalVariable(name: "math_arg_ptr", scope: !1469, file: !6, line: 940, type: !35)
!1474 = distinct !DIAssignID()
!1475 = !DILocation(line: 0, scope: !1469)
!1476 = !DILocation(line: 939, column: 10, scope: !1469)
!1477 = !DILocation(line: 939, column: 16, scope: !1469)
!1478 = !DILocation(line: 940, column: 5, scope: !1469)
!1479 = !DILocation(line: 940, column: 18, scope: !1469)
!1480 = distinct !DIAssignID()
!1481 = !DILocation(line: 942, column: 5, scope: !1469)
!1482 = !DILocation(line: 944, column: 5, scope: !1469)
!1483 = !DILocation(line: 945, column: 1, scope: !1469)
!1484 = distinct !DISubprogram(name: "prjm_eval_func_tan", scope: !6, file: !6, line: 947, type: !21, scopeLine: 948, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1485)
!1485 = !{!1486, !1487, !1488}
!1486 = !DILocalVariable(name: "ctx", arg: 1, scope: !1484, file: !6, line: 947, type: !23)
!1487 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1484, file: !6, line: 947, type: !38)
!1488 = !DILocalVariable(name: "math_arg_ptr", scope: !1484, file: !6, line: 952, type: !35)
!1489 = distinct !DIAssignID()
!1490 = !DILocation(line: 0, scope: !1484)
!1491 = !DILocation(line: 951, column: 10, scope: !1484)
!1492 = !DILocation(line: 951, column: 16, scope: !1484)
!1493 = !DILocation(line: 952, column: 5, scope: !1484)
!1494 = !DILocation(line: 952, column: 18, scope: !1484)
!1495 = distinct !DIAssignID()
!1496 = !DILocation(line: 954, column: 5, scope: !1484)
!1497 = !DILocation(line: 956, column: 5, scope: !1484)
!1498 = !DILocation(line: 957, column: 1, scope: !1484)
!1499 = !DISubprogram(name: "tan", scope: !1500, file: !1500, line: 100, type: !1501, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1500 = !DIFile(filename: "Library/Android/sdk/ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/sysroot/usr/include/math.h", directory: "/Users/jneerdael")
!1501 = !DISubroutineType(types: !1502)
!1502 = !{!13, !13}
!1503 = distinct !DISubprogram(name: "prjm_eval_func_asin", scope: !6, file: !6, line: 959, type: !21, scopeLine: 960, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1504)
!1504 = !{!1505, !1506, !1507}
!1505 = !DILocalVariable(name: "ctx", arg: 1, scope: !1503, file: !6, line: 959, type: !23)
!1506 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1503, file: !6, line: 959, type: !38)
!1507 = !DILocalVariable(name: "math_arg_ptr", scope: !1503, file: !6, line: 964, type: !35)
!1508 = distinct !DIAssignID()
!1509 = !DILocation(line: 0, scope: !1503)
!1510 = !DILocation(line: 963, column: 10, scope: !1503)
!1511 = !DILocation(line: 963, column: 16, scope: !1503)
!1512 = !DILocation(line: 964, column: 5, scope: !1503)
!1513 = !DILocation(line: 964, column: 18, scope: !1503)
!1514 = distinct !DIAssignID()
!1515 = !DILocation(line: 966, column: 5, scope: !1503)
!1516 = !DILocation(line: 968, column: 10, scope: !1517)
!1517 = distinct !DILexicalBlock(scope: !1503, file: !6, line: 968, column: 9)
!1518 = !DILocation(line: 968, column: 9, scope: !1517)
!1519 = !DILocation(line: 968, column: 23, scope: !1517)
!1520 = !DILocation(line: 968, column: 30, scope: !1517)
!1521 = !DILocation(line: 974, column: 5, scope: !1503)
!1522 = !DILocation(line: 975, column: 1, scope: !1503)
!1523 = !DISubprogram(name: "asin", scope: !1500, file: !1500, line: 80, type: !1501, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1524 = distinct !DISubprogram(name: "prjm_eval_func_acos", scope: !6, file: !6, line: 977, type: !21, scopeLine: 978, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1525)
!1525 = !{!1526, !1527, !1528}
!1526 = !DILocalVariable(name: "ctx", arg: 1, scope: !1524, file: !6, line: 977, type: !23)
!1527 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1524, file: !6, line: 977, type: !38)
!1528 = !DILocalVariable(name: "math_arg_ptr", scope: !1524, file: !6, line: 982, type: !35)
!1529 = distinct !DIAssignID()
!1530 = !DILocation(line: 0, scope: !1524)
!1531 = !DILocation(line: 981, column: 10, scope: !1524)
!1532 = !DILocation(line: 981, column: 16, scope: !1524)
!1533 = !DILocation(line: 982, column: 5, scope: !1524)
!1534 = !DILocation(line: 982, column: 18, scope: !1524)
!1535 = distinct !DIAssignID()
!1536 = !DILocation(line: 984, column: 5, scope: !1524)
!1537 = !DILocation(line: 986, column: 10, scope: !1538)
!1538 = distinct !DILexicalBlock(scope: !1524, file: !6, line: 986, column: 9)
!1539 = !DILocation(line: 986, column: 9, scope: !1538)
!1540 = !DILocation(line: 986, column: 23, scope: !1538)
!1541 = !DILocation(line: 986, column: 30, scope: !1538)
!1542 = !DILocation(line: 992, column: 5, scope: !1524)
!1543 = !DILocation(line: 993, column: 1, scope: !1524)
!1544 = !DISubprogram(name: "acos", scope: !1500, file: !1500, line: 76, type: !1501, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1545 = distinct !DISubprogram(name: "prjm_eval_func_atan", scope: !6, file: !6, line: 995, type: !21, scopeLine: 996, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1546)
!1546 = !{!1547, !1548, !1549}
!1547 = !DILocalVariable(name: "ctx", arg: 1, scope: !1545, file: !6, line: 995, type: !23)
!1548 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1545, file: !6, line: 995, type: !38)
!1549 = !DILocalVariable(name: "math_arg_ptr", scope: !1545, file: !6, line: 1000, type: !35)
!1550 = distinct !DIAssignID()
!1551 = !DILocation(line: 0, scope: !1545)
!1552 = !DILocation(line: 999, column: 10, scope: !1545)
!1553 = !DILocation(line: 999, column: 16, scope: !1545)
!1554 = !DILocation(line: 1000, column: 5, scope: !1545)
!1555 = !DILocation(line: 1000, column: 18, scope: !1545)
!1556 = distinct !DIAssignID()
!1557 = !DILocation(line: 1002, column: 5, scope: !1545)
!1558 = !DILocation(line: 1004, column: 5, scope: !1545)
!1559 = !DILocation(line: 1005, column: 1, scope: !1545)
!1560 = !DISubprogram(name: "atan", scope: !1500, file: !1500, line: 84, type: !1501, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1561 = distinct !DISubprogram(name: "prjm_eval_func_atan2", scope: !6, file: !6, line: 1007, type: !21, scopeLine: 1008, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1562)
!1562 = !{!1563, !1564, !1565, !1566, !1567, !1568}
!1563 = !DILocalVariable(name: "ctx", arg: 1, scope: !1561, file: !6, line: 1007, type: !23)
!1564 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1561, file: !6, line: 1007, type: !38)
!1565 = !DILocalVariable(name: "math_arg1", scope: !1561, file: !6, line: 1011, type: !11)
!1566 = !DILocalVariable(name: "math_arg2", scope: !1561, file: !6, line: 1012, type: !11)
!1567 = !DILocalVariable(name: "math_arg1_ptr", scope: !1561, file: !6, line: 1013, type: !35)
!1568 = !DILocalVariable(name: "math_arg2_ptr", scope: !1561, file: !6, line: 1014, type: !35)
!1569 = distinct !DIAssignID()
!1570 = !DILocation(line: 0, scope: !1561)
!1571 = distinct !DIAssignID()
!1572 = distinct !DIAssignID()
!1573 = distinct !DIAssignID()
!1574 = !DILocation(line: 1011, column: 5, scope: !1561)
!1575 = !DILocation(line: 1011, column: 17, scope: !1561)
!1576 = distinct !DIAssignID()
!1577 = !DILocation(line: 1012, column: 5, scope: !1561)
!1578 = !DILocation(line: 1012, column: 17, scope: !1561)
!1579 = distinct !DIAssignID()
!1580 = !DILocation(line: 1013, column: 5, scope: !1561)
!1581 = !DILocation(line: 1013, column: 18, scope: !1561)
!1582 = distinct !DIAssignID()
!1583 = !DILocation(line: 1014, column: 5, scope: !1561)
!1584 = !DILocation(line: 1014, column: 18, scope: !1561)
!1585 = distinct !DIAssignID()
!1586 = !DILocation(line: 1016, column: 5, scope: !1561)
!1587 = !DILocation(line: 1017, column: 5, scope: !1561)
!1588 = !DILocation(line: 1019, column: 5, scope: !1561)
!1589 = !DILocation(line: 1020, column: 1, scope: !1561)
!1590 = !DISubprogram(name: "atan2", scope: !1500, file: !1500, line: 88, type: !1591, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1591 = !DISubroutineType(types: !1592)
!1592 = !{!13, !13, !13}
!1593 = distinct !DISubprogram(name: "prjm_eval_func_sqrt", scope: !6, file: !6, line: 1022, type: !21, scopeLine: 1023, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1594)
!1594 = !{!1595, !1596, !1597}
!1595 = !DILocalVariable(name: "ctx", arg: 1, scope: !1593, file: !6, line: 1022, type: !23)
!1596 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1593, file: !6, line: 1022, type: !38)
!1597 = !DILocalVariable(name: "math_arg_ptr", scope: !1593, file: !6, line: 1027, type: !35)
!1598 = distinct !DIAssignID()
!1599 = !DILocation(line: 0, scope: !1593)
!1600 = !DILocation(line: 1026, column: 10, scope: !1593)
!1601 = !DILocation(line: 1026, column: 16, scope: !1593)
!1602 = !DILocation(line: 1027, column: 5, scope: !1593)
!1603 = !DILocation(line: 1027, column: 18, scope: !1593)
!1604 = distinct !DIAssignID()
!1605 = !DILocation(line: 1029, column: 5, scope: !1593)
!1606 = !DILocation(line: 1031, column: 5, scope: !1593)
!1607 = !DILocation(line: 1032, column: 1, scope: !1593)
!1608 = distinct !DISubprogram(name: "prjm_eval_func_pow", scope: !6, file: !6, line: 1034, type: !21, scopeLine: 1035, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1609)
!1609 = !{!1610, !1611, !1612, !1613, !1614, !1615, !1616}
!1610 = !DILocalVariable(name: "ctx", arg: 1, scope: !1608, file: !6, line: 1034, type: !23)
!1611 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1608, file: !6, line: 1034, type: !38)
!1612 = !DILocalVariable(name: "math_arg1", scope: !1608, file: !6, line: 1038, type: !11)
!1613 = !DILocalVariable(name: "math_arg2", scope: !1608, file: !6, line: 1039, type: !11)
!1614 = !DILocalVariable(name: "math_arg1_ptr", scope: !1608, file: !6, line: 1040, type: !35)
!1615 = !DILocalVariable(name: "math_arg2_ptr", scope: !1608, file: !6, line: 1041, type: !35)
!1616 = !DILocalVariable(name: "result", scope: !1608, file: !6, line: 1052, type: !11)
!1617 = distinct !DIAssignID()
!1618 = !DILocation(line: 0, scope: !1608)
!1619 = distinct !DIAssignID()
!1620 = distinct !DIAssignID()
!1621 = distinct !DIAssignID()
!1622 = !DILocation(line: 1038, column: 5, scope: !1608)
!1623 = !DILocation(line: 1038, column: 17, scope: !1608)
!1624 = distinct !DIAssignID()
!1625 = !DILocation(line: 1039, column: 5, scope: !1608)
!1626 = !DILocation(line: 1039, column: 17, scope: !1608)
!1627 = distinct !DIAssignID()
!1628 = !DILocation(line: 1040, column: 5, scope: !1608)
!1629 = !DILocation(line: 1040, column: 18, scope: !1608)
!1630 = distinct !DIAssignID()
!1631 = !DILocation(line: 1041, column: 5, scope: !1608)
!1632 = !DILocation(line: 1041, column: 18, scope: !1608)
!1633 = distinct !DIAssignID()
!1634 = !DILocation(line: 1043, column: 5, scope: !1608)
!1635 = !DILocation(line: 1044, column: 5, scope: !1608)
!1636 = !DILocation(line: 1046, column: 15, scope: !1637)
!1637 = distinct !DILexicalBlock(scope: !1608, file: !6, line: 1046, column: 9)
!1638 = !DILocation(line: 1046, column: 14, scope: !1637)
!1639 = !DILocation(line: 1046, column: 9, scope: !1637)
!1640 = !DILocation(line: 1046, column: 30, scope: !1637)
!1641 = !DILocation(line: 1052, column: 47, scope: !1608)
!1642 = !DILocation(line: 1052, column: 46, scope: !1608)
!1643 = !DILocation(line: 1046, column: 52, scope: !1637)
!1644 = !DILocation(line: 1055, column: 1, scope: !1608)
!1645 = distinct !DISubprogram(name: "prjm_eval_func_exp", scope: !6, file: !6, line: 1057, type: !21, scopeLine: 1058, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1646)
!1646 = !{!1647, !1648, !1649}
!1647 = !DILocalVariable(name: "ctx", arg: 1, scope: !1645, file: !6, line: 1057, type: !23)
!1648 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1645, file: !6, line: 1057, type: !38)
!1649 = !DILocalVariable(name: "math_arg_ptr", scope: !1645, file: !6, line: 1062, type: !35)
!1650 = distinct !DIAssignID()
!1651 = !DILocation(line: 0, scope: !1645)
!1652 = !DILocation(line: 1061, column: 10, scope: !1645)
!1653 = !DILocation(line: 1061, column: 16, scope: !1645)
!1654 = !DILocation(line: 1062, column: 5, scope: !1645)
!1655 = !DILocation(line: 1062, column: 18, scope: !1645)
!1656 = distinct !DIAssignID()
!1657 = !DILocation(line: 1064, column: 5, scope: !1645)
!1658 = !DILocation(line: 1066, column: 5, scope: !1645)
!1659 = !DILocation(line: 1067, column: 1, scope: !1645)
!1660 = distinct !DISubprogram(name: "prjm_eval_func_log", scope: !6, file: !6, line: 1069, type: !21, scopeLine: 1070, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1661)
!1661 = !{!1662, !1663, !1664}
!1662 = !DILocalVariable(name: "ctx", arg: 1, scope: !1660, file: !6, line: 1069, type: !23)
!1663 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1660, file: !6, line: 1069, type: !38)
!1664 = !DILocalVariable(name: "math_arg_ptr", scope: !1660, file: !6, line: 1074, type: !35)
!1665 = distinct !DIAssignID()
!1666 = !DILocation(line: 0, scope: !1660)
!1667 = !DILocation(line: 1073, column: 10, scope: !1660)
!1668 = !DILocation(line: 1073, column: 16, scope: !1660)
!1669 = !DILocation(line: 1074, column: 5, scope: !1660)
!1670 = !DILocation(line: 1074, column: 18, scope: !1660)
!1671 = distinct !DIAssignID()
!1672 = !DILocation(line: 1076, column: 5, scope: !1660)
!1673 = !DILocation(line: 1078, column: 10, scope: !1674)
!1674 = distinct !DILexicalBlock(scope: !1660, file: !6, line: 1078, column: 9)
!1675 = !DILocation(line: 1078, column: 9, scope: !1674)
!1676 = !DILocation(line: 1078, column: 23, scope: !1674)
!1677 = !DILocation(line: 1078, column: 9, scope: !1660)
!1678 = !DILocation(line: 1085, column: 1, scope: !1660)
!1679 = distinct !DISubprogram(name: "prjm_eval_func_log10", scope: !6, file: !6, line: 1087, type: !21, scopeLine: 1088, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1680)
!1680 = !{!1681, !1682, !1683}
!1681 = !DILocalVariable(name: "ctx", arg: 1, scope: !1679, file: !6, line: 1087, type: !23)
!1682 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1679, file: !6, line: 1087, type: !38)
!1683 = !DILocalVariable(name: "math_arg_ptr", scope: !1679, file: !6, line: 1092, type: !35)
!1684 = distinct !DIAssignID()
!1685 = !DILocation(line: 0, scope: !1679)
!1686 = !DILocation(line: 1091, column: 10, scope: !1679)
!1687 = !DILocation(line: 1091, column: 16, scope: !1679)
!1688 = !DILocation(line: 1092, column: 5, scope: !1679)
!1689 = !DILocation(line: 1092, column: 18, scope: !1679)
!1690 = distinct !DIAssignID()
!1691 = !DILocation(line: 1094, column: 5, scope: !1679)
!1692 = !DILocation(line: 1096, column: 10, scope: !1693)
!1693 = distinct !DILexicalBlock(scope: !1679, file: !6, line: 1096, column: 9)
!1694 = !DILocation(line: 1096, column: 9, scope: !1693)
!1695 = !DILocation(line: 1096, column: 23, scope: !1693)
!1696 = !DILocation(line: 1096, column: 9, scope: !1679)
!1697 = !DILocation(line: 1103, column: 1, scope: !1679)
!1698 = distinct !DISubprogram(name: "prjm_eval_func_floor", scope: !6, file: !6, line: 1105, type: !21, scopeLine: 1106, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1699)
!1699 = !{!1700, !1701, !1702}
!1700 = !DILocalVariable(name: "ctx", arg: 1, scope: !1698, file: !6, line: 1105, type: !23)
!1701 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1698, file: !6, line: 1105, type: !38)
!1702 = !DILocalVariable(name: "math_arg_ptr", scope: !1698, file: !6, line: 1110, type: !35)
!1703 = distinct !DIAssignID()
!1704 = !DILocation(line: 0, scope: !1698)
!1705 = !DILocation(line: 1109, column: 10, scope: !1698)
!1706 = !DILocation(line: 1109, column: 16, scope: !1698)
!1707 = !DILocation(line: 1110, column: 5, scope: !1698)
!1708 = !DILocation(line: 1110, column: 18, scope: !1698)
!1709 = distinct !DIAssignID()
!1710 = !DILocation(line: 1112, column: 5, scope: !1698)
!1711 = !DILocation(line: 1114, column: 5, scope: !1698)
!1712 = !DILocation(line: 1115, column: 1, scope: !1698)
!1713 = distinct !DISubprogram(name: "prjm_eval_func_ceil", scope: !6, file: !6, line: 1117, type: !21, scopeLine: 1118, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1714)
!1714 = !{!1715, !1716, !1717}
!1715 = !DILocalVariable(name: "ctx", arg: 1, scope: !1713, file: !6, line: 1117, type: !23)
!1716 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1713, file: !6, line: 1117, type: !38)
!1717 = !DILocalVariable(name: "math_arg_ptr", scope: !1713, file: !6, line: 1122, type: !35)
!1718 = distinct !DIAssignID()
!1719 = !DILocation(line: 0, scope: !1713)
!1720 = !DILocation(line: 1121, column: 10, scope: !1713)
!1721 = !DILocation(line: 1121, column: 16, scope: !1713)
!1722 = !DILocation(line: 1122, column: 5, scope: !1713)
!1723 = !DILocation(line: 1122, column: 18, scope: !1713)
!1724 = distinct !DIAssignID()
!1725 = !DILocation(line: 1124, column: 5, scope: !1713)
!1726 = !DILocation(line: 1126, column: 5, scope: !1713)
!1727 = !DILocation(line: 1127, column: 1, scope: !1713)
!1728 = distinct !DISubprogram(name: "prjm_eval_func_sigmoid", scope: !6, file: !6, line: 1129, type: !21, scopeLine: 1130, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1729)
!1729 = !{!1730, !1731, !1732, !1733, !1734, !1735, !1736}
!1730 = !DILocalVariable(name: "ctx", arg: 1, scope: !1728, file: !6, line: 1129, type: !23)
!1731 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1728, file: !6, line: 1129, type: !38)
!1732 = !DILocalVariable(name: "math_arg1", scope: !1728, file: !6, line: 1133, type: !11)
!1733 = !DILocalVariable(name: "math_arg2", scope: !1728, file: !6, line: 1134, type: !11)
!1734 = !DILocalVariable(name: "math_arg1_ptr", scope: !1728, file: !6, line: 1135, type: !35)
!1735 = !DILocalVariable(name: "math_arg2_ptr", scope: !1728, file: !6, line: 1136, type: !35)
!1736 = !DILocalVariable(name: "t", scope: !1728, file: !6, line: 1141, type: !13)
!1737 = distinct !DIAssignID()
!1738 = !DILocation(line: 0, scope: !1728)
!1739 = distinct !DIAssignID()
!1740 = distinct !DIAssignID()
!1741 = distinct !DIAssignID()
!1742 = !DILocation(line: 1133, column: 5, scope: !1728)
!1743 = !DILocation(line: 1133, column: 17, scope: !1728)
!1744 = distinct !DIAssignID()
!1745 = !DILocation(line: 1134, column: 5, scope: !1728)
!1746 = !DILocation(line: 1134, column: 17, scope: !1728)
!1747 = distinct !DIAssignID()
!1748 = !DILocation(line: 1135, column: 5, scope: !1728)
!1749 = !DILocation(line: 1135, column: 18, scope: !1728)
!1750 = distinct !DIAssignID()
!1751 = !DILocation(line: 1136, column: 5, scope: !1728)
!1752 = !DILocation(line: 1136, column: 18, scope: !1728)
!1753 = distinct !DIAssignID()
!1754 = !DILocation(line: 1138, column: 5, scope: !1728)
!1755 = !DILocation(line: 1139, column: 5, scope: !1728)
!1756 = !DILocation(line: 1141, column: 37, scope: !1728)
!1757 = !DILocation(line: 1141, column: 36, scope: !1728)
!1758 = !DILocation(line: 1141, column: 34, scope: !1728)
!1759 = !DILocation(line: 1141, column: 56, scope: !1728)
!1760 = !DILocation(line: 1141, column: 55, scope: !1728)
!1761 = !DILocation(line: 1141, column: 52, scope: !1728)
!1762 = !DILocation(line: 1141, column: 21, scope: !1728)
!1763 = !DILocation(line: 1141, column: 19, scope: !1728)
!1764 = !DILocation(line: 1142, column: 5, scope: !1728)
!1765 = !DILocation(line: 1143, column: 1, scope: !1728)
!1766 = distinct !DISubprogram(name: "prjm_eval_func_sqr", scope: !6, file: !6, line: 1145, type: !21, scopeLine: 1146, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1767)
!1767 = !{!1768, !1769, !1770}
!1768 = !DILocalVariable(name: "ctx", arg: 1, scope: !1766, file: !6, line: 1145, type: !23)
!1769 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1766, file: !6, line: 1145, type: !38)
!1770 = !DILocalVariable(name: "value_ptr", scope: !1766, file: !6, line: 1150, type: !35)
!1771 = distinct !DIAssignID()
!1772 = !DILocation(line: 0, scope: !1766)
!1773 = !DILocation(line: 1149, column: 10, scope: !1766)
!1774 = !DILocation(line: 1149, column: 16, scope: !1766)
!1775 = !DILocation(line: 1150, column: 5, scope: !1766)
!1776 = !DILocation(line: 1150, column: 18, scope: !1766)
!1777 = distinct !DIAssignID()
!1778 = !DILocation(line: 1152, column: 5, scope: !1766)
!1779 = !DILocation(line: 1154, column: 5, scope: !1766)
!1780 = !DILocation(line: 1155, column: 1, scope: !1766)
!1781 = distinct !DISubprogram(name: "prjm_eval_func_abs", scope: !6, file: !6, line: 1157, type: !21, scopeLine: 1158, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1782)
!1782 = !{!1783, !1784, !1785}
!1783 = !DILocalVariable(name: "ctx", arg: 1, scope: !1781, file: !6, line: 1157, type: !23)
!1784 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1781, file: !6, line: 1157, type: !38)
!1785 = !DILocalVariable(name: "value_ptr", scope: !1781, file: !6, line: 1162, type: !35)
!1786 = distinct !DIAssignID()
!1787 = !DILocation(line: 0, scope: !1781)
!1788 = !DILocation(line: 1161, column: 10, scope: !1781)
!1789 = !DILocation(line: 1161, column: 16, scope: !1781)
!1790 = !DILocation(line: 1162, column: 5, scope: !1781)
!1791 = !DILocation(line: 1162, column: 18, scope: !1781)
!1792 = distinct !DIAssignID()
!1793 = !DILocation(line: 1164, column: 5, scope: !1781)
!1794 = !DILocation(line: 1166, column: 5, scope: !1781)
!1795 = !DILocation(line: 1167, column: 1, scope: !1781)
!1796 = distinct !DISubprogram(name: "prjm_eval_func_min", scope: !6, file: !6, line: 1169, type: !21, scopeLine: 1170, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1797)
!1797 = !{!1798, !1799, !1800, !1801, !1802, !1803}
!1798 = !DILocalVariable(name: "ctx", arg: 1, scope: !1796, file: !6, line: 1169, type: !23)
!1799 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1796, file: !6, line: 1169, type: !38)
!1800 = !DILocalVariable(name: "math_arg1", scope: !1796, file: !6, line: 1173, type: !11)
!1801 = !DILocalVariable(name: "math_arg2", scope: !1796, file: !6, line: 1174, type: !11)
!1802 = !DILocalVariable(name: "math_arg1_ptr", scope: !1796, file: !6, line: 1175, type: !35)
!1803 = !DILocalVariable(name: "math_arg2_ptr", scope: !1796, file: !6, line: 1176, type: !35)
!1804 = distinct !DIAssignID()
!1805 = !DILocation(line: 0, scope: !1796)
!1806 = distinct !DIAssignID()
!1807 = distinct !DIAssignID()
!1808 = distinct !DIAssignID()
!1809 = !DILocation(line: 1173, column: 5, scope: !1796)
!1810 = !DILocation(line: 1173, column: 17, scope: !1796)
!1811 = distinct !DIAssignID()
!1812 = !DILocation(line: 1174, column: 5, scope: !1796)
!1813 = !DILocation(line: 1174, column: 17, scope: !1796)
!1814 = distinct !DIAssignID()
!1815 = !DILocation(line: 1175, column: 5, scope: !1796)
!1816 = !DILocation(line: 1175, column: 18, scope: !1796)
!1817 = distinct !DIAssignID()
!1818 = !DILocation(line: 1176, column: 5, scope: !1796)
!1819 = !DILocation(line: 1176, column: 18, scope: !1796)
!1820 = distinct !DIAssignID()
!1821 = !DILocation(line: 1178, column: 5, scope: !1796)
!1822 = !DILocation(line: 1179, column: 5, scope: !1796)
!1823 = !DILocation(line: 1181, column: 5, scope: !1796)
!1824 = !DILocation(line: 1182, column: 1, scope: !1796)
!1825 = distinct !DISubprogram(name: "prjm_eval_func_max", scope: !6, file: !6, line: 1184, type: !21, scopeLine: 1185, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1826)
!1826 = !{!1827, !1828, !1829, !1830, !1831, !1832}
!1827 = !DILocalVariable(name: "ctx", arg: 1, scope: !1825, file: !6, line: 1184, type: !23)
!1828 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1825, file: !6, line: 1184, type: !38)
!1829 = !DILocalVariable(name: "math_arg1", scope: !1825, file: !6, line: 1188, type: !11)
!1830 = !DILocalVariable(name: "math_arg2", scope: !1825, file: !6, line: 1189, type: !11)
!1831 = !DILocalVariable(name: "math_arg1_ptr", scope: !1825, file: !6, line: 1190, type: !35)
!1832 = !DILocalVariable(name: "math_arg2_ptr", scope: !1825, file: !6, line: 1191, type: !35)
!1833 = distinct !DIAssignID()
!1834 = !DILocation(line: 0, scope: !1825)
!1835 = distinct !DIAssignID()
!1836 = distinct !DIAssignID()
!1837 = distinct !DIAssignID()
!1838 = !DILocation(line: 1188, column: 5, scope: !1825)
!1839 = !DILocation(line: 1188, column: 17, scope: !1825)
!1840 = distinct !DIAssignID()
!1841 = !DILocation(line: 1189, column: 5, scope: !1825)
!1842 = !DILocation(line: 1189, column: 17, scope: !1825)
!1843 = distinct !DIAssignID()
!1844 = !DILocation(line: 1190, column: 5, scope: !1825)
!1845 = !DILocation(line: 1190, column: 18, scope: !1825)
!1846 = distinct !DIAssignID()
!1847 = !DILocation(line: 1191, column: 5, scope: !1825)
!1848 = !DILocation(line: 1191, column: 18, scope: !1825)
!1849 = distinct !DIAssignID()
!1850 = !DILocation(line: 1193, column: 5, scope: !1825)
!1851 = !DILocation(line: 1194, column: 5, scope: !1825)
!1852 = !DILocation(line: 1196, column: 5, scope: !1825)
!1853 = !DILocation(line: 1197, column: 1, scope: !1825)
!1854 = distinct !DISubprogram(name: "prjm_eval_func_sign", scope: !6, file: !6, line: 1199, type: !21, scopeLine: 1200, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1855)
!1855 = !{!1856, !1857, !1858}
!1856 = !DILocalVariable(name: "ctx", arg: 1, scope: !1854, file: !6, line: 1199, type: !23)
!1857 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1854, file: !6, line: 1199, type: !38)
!1858 = !DILocalVariable(name: "value_ptr", scope: !1854, file: !6, line: 1204, type: !35)
!1859 = distinct !DIAssignID()
!1860 = !DILocation(line: 0, scope: !1854)
!1861 = !DILocation(line: 1203, column: 10, scope: !1854)
!1862 = !DILocation(line: 1203, column: 16, scope: !1854)
!1863 = !DILocation(line: 1204, column: 5, scope: !1854)
!1864 = !DILocation(line: 1204, column: 18, scope: !1854)
!1865 = distinct !DIAssignID()
!1866 = !DILocation(line: 1206, column: 5, scope: !1854)
!1867 = !DILocation(line: 1208, column: 10, scope: !1868)
!1868 = distinct !DILexicalBlock(scope: !1854, file: !6, line: 1208, column: 9)
!1869 = !DILocation(line: 1208, column: 9, scope: !1868)
!1870 = !DILocation(line: 1208, column: 20, scope: !1868)
!1871 = !DILocation(line: 1208, column: 9, scope: !1854)
!1872 = !DILocation(line: 1214, column: 1, scope: !1854)
!1873 = distinct !DISubprogram(name: "prjm_eval_func_rand", scope: !6, file: !6, line: 1216, type: !21, scopeLine: 1217, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1874)
!1874 = !{!1875, !1876, !1877, !1878}
!1875 = !DILocalVariable(name: "ctx", arg: 1, scope: !1873, file: !6, line: 1216, type: !23)
!1876 = !DILocalVariable(name: "ret_val", arg: 2, scope: !1873, file: !6, line: 1216, type: !38)
!1877 = !DILocalVariable(name: "value_ptr", scope: !1873, file: !6, line: 1221, type: !35)
!1878 = !DILocalVariable(name: "rand_max", scope: !1873, file: !6, line: 1225, type: !11)
!1879 = distinct !DIAssignID()
!1880 = !DILocation(line: 0, scope: !1873)
!1881 = !DILocation(line: 1220, column: 10, scope: !1873)
!1882 = !DILocation(line: 1220, column: 16, scope: !1873)
!1883 = !DILocation(line: 1221, column: 5, scope: !1873)
!1884 = !DILocation(line: 1221, column: 18, scope: !1873)
!1885 = distinct !DIAssignID()
!1886 = !DILocation(line: 1223, column: 5, scope: !1873)
!1887 = !DILocation(line: 1225, column: 35, scope: !1873)
!1888 = !DILocation(line: 1225, column: 34, scope: !1873)
!1889 = !DILocation(line: 169, column: 10, scope: !246, inlinedAt: !1890)
!1890 = distinct !DILocation(line: 1231, column: 5, scope: !1873)
!1891 = !DILocation(line: 169, column: 9, scope: !236, inlinedAt: !1890)
!1892 = !DILocation(line: 0, scope: !245, inlinedAt: !1890)
!1893 = !DILocation(line: 172, column: 9, scope: !245, inlinedAt: !1890)
!1894 = !DILocation(line: 172, column: 15, scope: !245, inlinedAt: !1890)
!1895 = !DILocation(line: 173, scope: !1896, inlinedAt: !1890)
!1896 = distinct !DILexicalBlock(scope: !245, file: !6, line: 173, column: 9)
!1897 = !DILocation(line: 173, column: 9, scope: !1896, inlinedAt: !1890)
!1898 = !DILocation(line: 176, column: 41, scope: !1899, inlinedAt: !1890)
!1899 = distinct !DILexicalBlock(scope: !1900, file: !6, line: 174, column: 9)
!1900 = distinct !DILexicalBlock(scope: !1896, file: !6, line: 173, column: 9)
!1901 = !DILocation(line: 176, column: 34, scope: !1899, inlinedAt: !1890)
!1902 = !DILocation(line: 176, column: 61, scope: !1899, inlinedAt: !1890)
!1903 = !DILocation(line: 176, column: 46, scope: !1899, inlinedAt: !1890)
!1904 = !DILocation(line: 176, column: 31, scope: !1899, inlinedAt: !1890)
!1905 = !DILocation(line: 176, column: 71, scope: !1899, inlinedAt: !1890)
!1906 = !DILocation(line: 176, column: 69, scope: !1899, inlinedAt: !1890)
!1907 = !DILocation(line: 175, column: 13, scope: !1899, inlinedAt: !1890)
!1908 = !DILocation(line: 175, column: 21, scope: !1899, inlinedAt: !1890)
!1909 = !DILocation(line: 173, column: 35, scope: !1900, inlinedAt: !1890)
!1910 = !DILocation(line: 173, column: 27, scope: !1900, inlinedAt: !1890)
!1911 = distinct !{!1911, !1897, !1912, !349}
!1912 = !DILocation(line: 184, column: 9, scope: !1896, inlinedAt: !1890)
!1913 = !DILocation(line: 187, column: 13, scope: !249, inlinedAt: !1890)
!1914 = !DILocation(line: 187, column: 9, scope: !236, inlinedAt: !1890)
!1915 = !DILocation(line: 0, scope: !248, inlinedAt: !1890)
!1916 = !DILocation(line: 193, column: 18, scope: !1917, inlinedAt: !1890)
!1917 = distinct !DILexicalBlock(scope: !1918, file: !6, line: 192, column: 9)
!1918 = distinct !DILexicalBlock(scope: !1919, file: !6, line: 191, column: 9)
!1919 = distinct !DILexicalBlock(scope: !248, file: !6, line: 191, column: 9)
!1920 = !DILocation(line: 191, column: 9, scope: !1919, inlinedAt: !1890)
!1921 = !DILocation(line: 193, column: 48, scope: !1917, inlinedAt: !1890)
!1922 = !DILocation(line: 193, column: 42, scope: !1917, inlinedAt: !1890)
!1923 = !DILocation(line: 193, column: 25, scope: !1917, inlinedAt: !1890)
!1924 = !DILocation(line: 193, column: 53, scope: !1917, inlinedAt: !1890)
!1925 = !DILocation(line: 193, column: 39, scope: !1917, inlinedAt: !1890)
!1926 = !DILocation(line: 194, column: 28, scope: !1917, inlinedAt: !1890)
!1927 = !DILocation(line: 194, column: 22, scope: !1917, inlinedAt: !1890)
!1928 = !DILocation(line: 194, column: 38, scope: !1917, inlinedAt: !1890)
!1929 = !DILocation(line: 194, column: 54, scope: !1917, inlinedAt: !1890)
!1930 = !DILocation(line: 194, column: 46, scope: !1917, inlinedAt: !1890)
!1931 = !DILocation(line: 194, column: 33, scope: !1917, inlinedAt: !1890)
!1932 = !DILocation(line: 194, column: 44, scope: !1917, inlinedAt: !1890)
!1933 = !DILocation(line: 194, column: 20, scope: !1917, inlinedAt: !1890)
!1934 = distinct !{!1934, !1920, !1935, !349, !1936, !1937}
!1935 = !DILocation(line: 195, column: 9, scope: !1919, inlinedAt: !1890)
!1936 = !{!"llvm.loop.isvectorized", i32 1}
!1937 = !{!"llvm.loop.unroll.runtime.disable"}
!1938 = !DILocation(line: 0, scope: !236, inlinedAt: !1890)
!1939 = !DILocation(line: 198, column: 18, scope: !1940, inlinedAt: !1890)
!1940 = distinct !DILexicalBlock(scope: !1941, file: !6, line: 197, column: 9)
!1941 = distinct !DILexicalBlock(scope: !1942, file: !6, line: 196, column: 9)
!1942 = distinct !DILexicalBlock(scope: !248, file: !6, line: 196, column: 9)
!1943 = !DILocation(line: 196, column: 9, scope: !1942, inlinedAt: !1890)
!1944 = !DILocation(line: 198, column: 25, scope: !1940, inlinedAt: !1890)
!1945 = !DILocation(line: 198, column: 48, scope: !1940, inlinedAt: !1890)
!1946 = !DILocation(line: 198, column: 42, scope: !1940, inlinedAt: !1890)
!1947 = !DILocation(line: 198, column: 53, scope: !1940, inlinedAt: !1890)
!1948 = !DILocation(line: 198, column: 39, scope: !1940, inlinedAt: !1890)
!1949 = !DILocation(line: 199, column: 28, scope: !1940, inlinedAt: !1890)
!1950 = !DILocation(line: 199, column: 22, scope: !1940, inlinedAt: !1890)
!1951 = !DILocation(line: 199, column: 44, scope: !1940, inlinedAt: !1890)
!1952 = !DILocation(line: 199, column: 60, scope: !1940, inlinedAt: !1890)
!1953 = !DILocation(line: 199, column: 52, scope: !1940, inlinedAt: !1890)
!1954 = !DILocation(line: 199, column: 39, scope: !1940, inlinedAt: !1890)
!1955 = !DILocation(line: 199, column: 50, scope: !1940, inlinedAt: !1890)
!1956 = !DILocation(line: 199, column: 20, scope: !1940, inlinedAt: !1890)
!1957 = !DILocation(line: 196, column: 19, scope: !1941, inlinedAt: !1890)
!1958 = distinct !{!1958, !1943, !1959, !349}
!1959 = !DILocation(line: 200, column: 9, scope: !1942, inlinedAt: !1890)
!1960 = !DILocation(line: 201, column: 14, scope: !248, inlinedAt: !1890)
!1961 = !DILocation(line: 201, column: 24, scope: !248, inlinedAt: !1890)
!1962 = !DILocation(line: 201, column: 41, scope: !248, inlinedAt: !1890)
!1963 = !DILocation(line: 201, column: 47, scope: !248, inlinedAt: !1890)
!1964 = !DILocation(line: 201, column: 38, scope: !248, inlinedAt: !1890)
!1965 = !DILocation(line: 202, column: 21, scope: !248, inlinedAt: !1890)
!1966 = !DILocation(line: 202, column: 36, scope: !248, inlinedAt: !1890)
!1967 = !DILocation(line: 202, column: 52, scope: !248, inlinedAt: !1890)
!1968 = !DILocation(line: 202, column: 44, scope: !248, inlinedAt: !1890)
!1969 = !DILocation(line: 202, column: 31, scope: !248, inlinedAt: !1890)
!1970 = !DILocation(line: 202, column: 42, scope: !248, inlinedAt: !1890)
!1971 = !DILocation(line: 202, column: 19, scope: !248, inlinedAt: !1890)
!1972 = !DILocation(line: 205, column: 5, scope: !248, inlinedAt: !1890)
!1973 = !DILocation(line: 207, column: 9, scope: !236, inlinedAt: !1890)
!1974 = !DILocation(line: 207, column: 15, scope: !236, inlinedAt: !1890)
!1975 = !DILocation(line: 1225, column: 28, scope: !1873)
!1976 = !DILocation(line: 1226, column: 18, scope: !1977)
!1977 = distinct !DILexicalBlock(scope: !1873, file: !6, line: 1226, column: 9)
!1978 = !DILocation(line: 1226, column: 9, scope: !1873)
!1979 = !DILocation(line: 210, column: 13, scope: !236, inlinedAt: !1890)
!1980 = !DILocation(line: 210, column: 7, scope: !236, inlinedAt: !1890)
!1981 = !DILocation(line: 211, column: 13, scope: !236, inlinedAt: !1890)
!1982 = !DILocation(line: 211, column: 19, scope: !236, inlinedAt: !1890)
!1983 = !DILocation(line: 211, column: 7, scope: !236, inlinedAt: !1890)
!1984 = !DILocation(line: 212, column: 13, scope: !236, inlinedAt: !1890)
!1985 = !DILocation(line: 212, column: 20, scope: !236, inlinedAt: !1890)
!1986 = !DILocation(line: 212, column: 7, scope: !236, inlinedAt: !1890)
!1987 = !DILocation(line: 213, column: 13, scope: !236, inlinedAt: !1890)
!1988 = !DILocation(line: 213, column: 7, scope: !236, inlinedAt: !1890)
!1989 = !DILocation(line: 1231, column: 5, scope: !1873)
!1990 = !DILocation(line: 1232, column: 1, scope: !1873)
!1991 = distinct !DIAssignID()
!1992 = !DILocation(line: 0, scope: !20)
!1993 = !DILocation(line: 1260, column: 10, scope: !20)
!1994 = !DILocation(line: 1260, column: 16, scope: !20)
!1995 = !DILocation(line: 1261, column: 5, scope: !20)
!1996 = !DILocation(line: 1261, column: 18, scope: !20)
!1997 = distinct !DIAssignID()
!1998 = !DILocation(line: 1263, column: 5, scope: !20)
!1999 = !DILocation(line: 1265, column: 26, scope: !20)
!2000 = !DILocation(line: 1265, column: 25, scope: !20)
!2001 = !DILocation(line: 1267, column: 59, scope: !20)
!2002 = !DILocation(line: 1267, column: 67, scope: !20)
!2003 = !DILocation(line: 1267, column: 46, scope: !20)
!2004 = !DILocation(line: 1267, column: 23, scope: !20)
!2005 = !DILocation(line: 1268, column: 95, scope: !20)
!2006 = !DILocation(line: 1268, column: 64, scope: !20)
!2007 = !DILocation(line: 1268, column: 49, scope: !20)
!2008 = !DILocation(line: 1270, column: 5, scope: !20)
!2009 = !DILocation(line: 1271, column: 1, scope: !20)
