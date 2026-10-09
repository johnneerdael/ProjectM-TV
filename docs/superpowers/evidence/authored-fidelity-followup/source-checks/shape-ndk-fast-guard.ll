  %133 = load i8, ptr %67, align 1, !dbg !12935, !tbaa !6508, !range !8194, !noundef !206
  %134 = icmp ne i8 %133, 0, !dbg !12935
  call void @llvm.dbg.value(metadata double %132, metadata !12936, metadata !DIExpression()), !dbg !12947
  call void @llvm.dbg.value(metadata i1 %134, metadata !12942, metadata !DIExpression(DW_OP_LLVM_convert, 1, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value)), !dbg !12947
  call void @llvm.dbg.value(metadata i64 0, metadata !12943, metadata !DIExpression()), !dbg !12947
  call void @llvm.dbg.value(metadata ptr undef, metadata !5713, metadata !DIExpression()), !dbg !12949
  call void @llvm.dbg.value(metadata i64 8, metadata !5714, metadata !DIExpression()), !dbg !12949
  call void @llvm.dbg.value(metadata ptr undef, metadata !5715, metadata !DIExpression()), !dbg !12949
  call void @llvm.dbg.value(metadata i64 8, metadata !5716, metadata !DIExpression()), !dbg !12949
  %135 = bitcast double %132 to i64, !dbg !12951
  call void @llvm.dbg.value(metadata i64 %135, metadata !12943, metadata !DIExpression()), !dbg !12947
  %136 = call double @llvm.fabs.f64(double %132), !dbg !12952
  %137 = bitcast double %136 to i64, !dbg !12952
  call void @llvm.dbg.value(metadata i64 %137, metadata !12944, metadata !DIExpression()), !dbg !12947
  %138 = icmp sgt i64 %135, -1, !dbg !12953
  %139 = select i1 %138, i64 4746794007248502784, i64 4746794007250599936, !dbg !12953
  call void @llvm.dbg.value(metadata i64 %139, metadata !12946, metadata !DIExpression()), !dbg !12947
  %140 = icmp ugt i64 %139, %137, !dbg !12954
  %141 = icmp ugt i64 %137, 4607182418800017407, !dbg !12956
  %142 = select i1 %140, i1 %141, i1 %134, !dbg !12956
  %143 = zext i1 %142 to i8, !dbg !12957
  tail call void @llvm.dbg.value(metadata i8 %143, metadata !5060, metadata !DIExpression(DW_OP_LLVM_fragment, 16, 8)), !dbg !12904
  %144 = load ptr, ptr %68, align 8, !dbg !12958, !tbaa !12959
  %145 = load double, ptr %144, align 8, !dbg !12960, !tbaa !12599
