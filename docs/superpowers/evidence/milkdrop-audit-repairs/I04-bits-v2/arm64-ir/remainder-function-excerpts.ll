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
