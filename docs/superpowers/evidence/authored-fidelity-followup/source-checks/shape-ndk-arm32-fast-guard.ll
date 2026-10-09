  %139 = load i8, ptr %72, align 1, !dbg !24276, !tbaa !17306, !range !19244, !noundef !219
  %140 = icmp ne i8 %139, 0, !dbg !24276
  call void @llvm.dbg.value(metadata double %138, metadata !24277, metadata !DIExpression()), !dbg !24288
  call void @llvm.dbg.value(metadata i1 %140, metadata !24283, metadata !DIExpression(DW_OP_LLVM_convert, 1, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value)), !dbg !24288
  call void @llvm.dbg.value(metadata i64 0, metadata !24284, metadata !DIExpression()), !dbg !24288
  call void @llvm.dbg.value(metadata ptr undef, metadata !16529, metadata !DIExpression()), !dbg !24290
  call void @llvm.dbg.value(metadata i32 8, metadata !16530, metadata !DIExpression()), !dbg !24290
  call void @llvm.dbg.value(metadata ptr undef, metadata !16531, metadata !DIExpression()), !dbg !24290
  call void @llvm.dbg.value(metadata i32 8, metadata !16532, metadata !DIExpression()), !dbg !24290
  %141 = bitcast double %138 to i64, !dbg !24292
  call void @llvm.dbg.value(metadata i64 %141, metadata !24284, metadata !DIExpression()), !dbg !24288
  %142 = call double @llvm.fabs.f64(double %138), !dbg !24293
  %143 = bitcast double %142 to i64, !dbg !24293
  call void @llvm.dbg.value(metadata i64 %143, metadata !24285, metadata !DIExpression()), !dbg !24288
  %144 = icmp sgt i64 %141, -1, !dbg !24294
  %145 = select i1 %144, i64 4746794007248502784, i64 4746794007250599936, !dbg !24294
  call void @llvm.dbg.value(metadata i64 %145, metadata !24287, metadata !DIExpression()), !dbg !24288
  %146 = icmp ugt i64 %145, %143, !dbg !24295
  %147 = icmp ugt i64 %143, 4607182418800017407, !dbg !24297
  %148 = select i1 %146, i1 %147, i1 %140, !dbg !24297
  %149 = zext i1 %148 to i8, !dbg !24298
  tail call void @llvm.dbg.value(metadata i8 %149, metadata !15845, metadata !DIExpression(DW_OP_LLVM_fragment, 16, 8)), !dbg !24244
  %150 = load ptr, ptr %73, align 8, !dbg !24299, !tbaa !24300
  %151 = load double, ptr %150, align 8, !dbg !24301, !tbaa !17334
