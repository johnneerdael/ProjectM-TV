	.text
	.file	"TreeFunctions.c"
	.file	1 "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit" "i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/api/projectm-eval.h"
	.file	2 "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit" "i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c"
	.file	3 "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit" "i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/CompilerTypes.h"
	.file	4 "/Users/jneerdael" "Library/Android/sdk/ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/sysroot/usr/include/stdint.h"
	.section	.text.prjm_eval_intrinsic_functions,"ax",@progbits
	.hidden	prjm_eval_intrinsic_functions   // -- Begin function prjm_eval_intrinsic_functions
	.globl	prjm_eval_intrinsic_functions
	.p2align	2
	.type	prjm_eval_intrinsic_functions,@function
prjm_eval_intrinsic_functions:          // @prjm_eval_intrinsic_functions
.Lfunc_begin0:
	.loc	2 152 0                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:152:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_intrinsic_functions:list <- $x0
	//DEBUG_VALUE: prjm_eval_intrinsic_functions:count <- $x1
	mov	w8, #72                         // =0x48
.Ltmp0:
	.loc	2 153 12 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:153:12
	str	w8, [x1]
	.loc	2 154 11                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:154:11
	adrp	x8, intrinsic_function_table
	add	x8, x8, :lo12:intrinsic_function_table
	str	x8, [x0]
	.loc	2 155 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:155:1
	ret
.Ltmp1:
.Lfunc_end0:
	.size	prjm_eval_intrinsic_functions, .Lfunc_end0-prjm_eval_intrinsic_functions
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_const,"ax",@progbits
	.hidden	prjm_eval_func_const            // -- Begin function prjm_eval_func_const
	.globl	prjm_eval_func_const
	.p2align	2
	.type	prjm_eval_func_const,@function
prjm_eval_func_const:                   // @prjm_eval_func_const
.Lfunc_begin1:
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_const:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_const:ret_val <- $x1
	.loc	2 223 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:223:5
	ldr	d0, [x0, #8]
	ldr	x8, [x1]
	str	d0, [x8]
	.loc	2 224 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:224:1
	ret
.Ltmp2:
.Lfunc_end1:
	.size	prjm_eval_func_const, .Lfunc_end1-prjm_eval_func_const
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_var,"ax",@progbits
	.hidden	prjm_eval_func_var              // -- Begin function prjm_eval_func_var
	.globl	prjm_eval_func_var
	.p2align	2
	.type	prjm_eval_func_var,@function
prjm_eval_func_var:                     // @prjm_eval_func_var
.Lfunc_begin2:
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_var:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_var:ret_val <- $x1
	.loc	2 231 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:231:5
	ldr	x8, [x0, #16]
	str	x8, [x1]
	.loc	2 232 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:232:1
	ret
.Ltmp3:
.Lfunc_end2:
	.size	prjm_eval_func_var, .Lfunc_end2-prjm_eval_func_var
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_execute_list,"ax",@progbits
	.hidden	prjm_eval_func_execute_list     // -- Begin function prjm_eval_func_execute_list
	.globl	prjm_eval_func_execute_list
	.p2align	2
	.type	prjm_eval_func_execute_list,@function
prjm_eval_func_execute_list:            // @prjm_eval_func_execute_list
.Lfunc_begin3:
	.loc	2 237 0                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:237:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_execute_list:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_execute_list:ret_val <- $x1
	sub	sp, sp, #64
	.cfi_def_cfa_offset 64
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x22, x21, [sp, #32]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #48]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -24
	.cfi_offset w22, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x19, x0
.Ltmp4:
	//DEBUG_VALUE: prjm_eval_func_execute_list:ctx <- $x19
	//DEBUG_VALUE: prjm_eval_func_execute_list:ctx <- $x19
	mov	x20, x1
.Ltmp5:
	//DEBUG_VALUE: prjm_eval_func_execute_list:ret_val <- $x20
	//DEBUG_VALUE: prjm_eval_func_execute_list:ret_val <- $x20
	ldr	x8, [x21, #40]
	str	x8, [sp, #8]
.Ltmp6:
	.loc	2 241 16 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:241:16
	str	xzr, [x19, #8]!
.Ltmp7:
	//DEBUG_VALUE: prjm_eval_func_execute_list:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_execute_list:value_ptr <- $x19
	.loc	2 0 0 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	ldr	x22, [x19, #24]
.Ltmp8:
	//DEBUG_VALUE: prjm_eval_func_execute_list:item <- $x22
	.loc	2 244 5 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:244:5
	cbz	x22, .LBB3_3
.Ltmp9:
.LBB3_1:                                // =>This Inner Loop Header: Depth=1
	//DEBUG_VALUE: prjm_eval_func_execute_list:item <- $x22
	//DEBUG_VALUE: prjm_eval_func_execute_list:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_execute_list:ret_val <- $x20
	.loc	2 250 19                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:250:19
	str	x19, [sp]
.Ltmp10:
	//DEBUG_VALUE: prjm_eval_func_execute_list:value_ptr <- [DW_OP_deref] $sp
	.loc	2 251 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:251:9
	mov	x1, sp
	.loc	2 251 15 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:251:15
	ldr	x0, [x22]
	.loc	2 249 20 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:249:20
	str	xzr, [x19]
	.loc	2 251 21                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:251:21
	ldr	x8, [x0]
	.loc	2 251 9 is_stmt 0               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:251:9
	blr	x8
.Ltmp11:
	//DEBUG_VALUE: prjm_eval_func_execute_list:item <- undef
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	ldr	x22, [x22, #8]
.Ltmp12:
	//DEBUG_VALUE: prjm_eval_func_execute_list:item <- $x22
	.loc	2 244 5 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:244:5
	cbnz	x22, .LBB3_1
.Ltmp13:
// %bb.2:
	//DEBUG_VALUE: prjm_eval_func_execute_list:value_ptr <- [DW_OP_deref] $sp
	//DEBUG_VALUE: prjm_eval_func_execute_list:item <- $x22
	//DEBUG_VALUE: prjm_eval_func_execute_list:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_execute_list:ret_val <- $x20
	.loc	2 255 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:255:5
	ldr	x19, [sp]
.Ltmp14:
.LBB3_3:
	//DEBUG_VALUE: prjm_eval_func_execute_list:item <- $x22
	//DEBUG_VALUE: prjm_eval_func_execute_list:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_execute_list:ret_val <- $x20
	str	x19, [x20]
	.loc	2 256 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:256:1
	ldr	x8, [x21, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB3_5
.Ltmp15:
// %bb.4:
	//DEBUG_VALUE: prjm_eval_func_execute_list:item <- $x22
	//DEBUG_VALUE: prjm_eval_func_execute_list:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_execute_list:ret_val <- $x20
	.cfi_def_cfa wsp, 64
	.loc	2 256 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:256:1
	ldp	x20, x19, [sp, #48]             // 16-byte Folded Reload
.Ltmp16:
	//DEBUG_VALUE: prjm_eval_func_execute_list:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x22, x21, [sp, #32]             // 16-byte Folded Reload
.Ltmp17:
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #64
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w22
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp18:
.LBB3_5:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_execute_list:item <- $x22
	//DEBUG_VALUE: prjm_eval_func_execute_list:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_execute_list:ret_val <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp19:
.Lfunc_end3:
	.size	prjm_eval_func_execute_list, .Lfunc_end3-prjm_eval_func_execute_list
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_execute_loop,"ax",@progbits
	.hidden	prjm_eval_func_execute_loop     // -- Begin function prjm_eval_func_execute_loop
	.globl	prjm_eval_func_execute_loop
	.p2align	2
	.type	prjm_eval_func_execute_loop,@function
prjm_eval_func_execute_loop:            // @prjm_eval_func_execute_loop
.Lfunc_begin4:
	.loc	2 259 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:259:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ret_val <- $x1
	sub	sp, sp, #80
	.cfi_def_cfa_offset 80
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	str	x23, [sp, #32]                  // 8-byte Folded Spill
	stp	x22, x21, [sp, #48]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #64]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 64
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -24
	.cfi_offset w22, -32
	.cfi_offset w23, -48
	.cfi_offset w30, -56
	.cfi_offset w29, -64
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
.Ltmp20:
	.loc	2 262 16 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:262:16
	mov	x22, x0
	mov	x19, x0
.Ltmp21:
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ctx <- $x19
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ctx <- $x19
	.loc	2 0 16 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:16
	ldr	x8, [x21, #40]
	mov	x20, x1
.Ltmp22:
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ret_val <- $x20
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ret_val <- $x20
	.loc	2 264 5 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:264:5
	mov	x1, sp
	str	x8, [sp, #8]
	.loc	2 262 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:262:16
	str	xzr, [x22, #8]!
	.loc	2 264 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:264:5
	ldr	x8, [x22, #16]
	.loc	2 263 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:263:18
	str	x22, [sp]
	.loc	2 264 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:264:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp23:
	.loc	2 266 50                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:266:50
	ldr	x8, [sp]
	mov	w10, #1048576                   // =0x100000
	.loc	2 266 49 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:266:49
	ldr	d0, [x8]
	.loc	2 266 34                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:266:34
	fcvtzs	x9, d0
.Ltmp24:
	//DEBUG_VALUE: prjm_eval_func_execute_loop:loop_count_int <- $x9
	.loc	2 268 9 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:268:9
	cmp	x9, #256, lsl #12               // =1048576
	csel	x23, x9, x10, lt
.Ltmp25:
	//DEBUG_VALUE: i <- 0
	//DEBUG_VALUE: prjm_eval_func_execute_loop:loop_count_int <- $x23
	.loc	2 273 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:273:5
	cmp	x9, #1
	b.lt	.LBB4_3
.Ltmp26:
.LBB4_1:                                // =>This Inner Loop Header: Depth=1
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ret_val <- $x20
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ctx <- $x19
	//DEBUG_VALUE: i <- undef
	.loc	2 277 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:277:9
	ldr	x8, [x19, #24]
	.loc	2 276 19                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:276:19
	str	x22, [sp]
	.loc	2 277 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:277:9
	mov	x1, sp
	.loc	2 275 20                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:275:20
	str	xzr, [x19, #8]
	.loc	2 277 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:277:9
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp27:
	.loc	2 273 31                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:273:31
	subs	x23, x23, #1
.Ltmp28:
	.loc	2 273 5 is_stmt 0               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:273:5
	b.ne	.LBB4_1
.Ltmp29:
// %bb.2:
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ret_val <- $x20
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ctx <- $x19
	.loc	2 280 5 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:280:5
	ldr	x8, [sp]
.Ltmp30:
.LBB4_3:
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ret_val <- $x20
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ctx <- $x19
	str	x8, [x20]
	.loc	2 281 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:281:1
	ldr	x8, [x21, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB4_5
.Ltmp31:
// %bb.4:
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ret_val <- $x20
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ctx <- $x19
	.cfi_def_cfa wsp, 80
	.loc	2 281 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:281:1
	ldp	x20, x19, [sp, #64]             // 16-byte Folded Reload
.Ltmp32:
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x23, [sp, #32]                  // 8-byte Folded Reload
	ldp	x22, x21, [sp, #48]             // 16-byte Folded Reload
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #80
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w22
	.cfi_restore w23
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp33:
.LBB4_5:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ret_val <- $x20
	//DEBUG_VALUE: prjm_eval_func_execute_loop:ctx <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp34:
.Lfunc_end4:
	.size	prjm_eval_func_execute_loop, .Lfunc_end4-prjm_eval_func_execute_loop
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_execute_while
.LCPI5_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_execute_while,"ax",@progbits
	.hidden	prjm_eval_func_execute_while
	.globl	prjm_eval_func_execute_while
	.p2align	2
	.type	prjm_eval_func_execute_while,@function
prjm_eval_func_execute_while:           // @prjm_eval_func_execute_while
.Lfunc_begin5:
	.loc	2 284 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:284:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_execute_while:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_execute_while:ret_val <- $x1
	sub	sp, sp, #80
	.cfi_def_cfa_offset 80
	str	d8, [sp, #16]                   // 8-byte Folded Spill
	stp	x29, x30, [sp, #32]             // 16-byte Folded Spill
	stp	x22, x21, [sp, #48]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #64]             // 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -24
	.cfi_offset w22, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_offset b8, -64
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	adrp	x9, .LCPI5_0
	mov	x19, x1
.Ltmp35:
	//DEBUG_VALUE: prjm_eval_func_execute_while:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_execute_while:ret_val <- $x19
	ldr	x8, [x21, #40]
	ldr	d8, [x9, :lo12:.LCPI5_0]
	mov	x20, x0
.Ltmp36:
	//DEBUG_VALUE: prjm_eval_func_execute_while:ctx <- $x20
	.loc	2 287 16 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:287:16
	mov	x10, x0
	mov	x22, #-1048575                  // =0xfffffffffff00001
.Ltmp37:
	//DEBUG_VALUE: prjm_eval_func_execute_while:loop_count_int <- 1048576
	.loc	2 0 16 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:16
	str	x8, [sp, #8]
	.loc	2 287 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:287:16
	str	xzr, [x10, #8]!
	.loc	2 288 18 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:288:18
	str	x10, [sp]
.Ltmp38:
.LBB5_1:                                // =>This Inner Loop Header: Depth=1
	//DEBUG_VALUE: prjm_eval_func_execute_while:ctx <- $x20
	//DEBUG_VALUE: prjm_eval_func_execute_while:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_execute_while:loop_count_int <- [DW_OP_consts 18446744073708503041, DW_OP_minus, DW_OP_consts 18446744073709551615, DW_OP_mul, DW_OP_consts 1048576, DW_OP_plus, DW_OP_stack_value] $x22
	.loc	2 292 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:292:9
	ldr	x8, [x20, #24]
	mov	x1, sp
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp39:
	.loc	2 293 20                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:293:20
	ldr	x8, [sp]
	.loc	2 293 19 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:293:19
	ldr	d0, [x8]
	.loc	2 293 14                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:293:14
	fabs	d0, d0
.Ltmp40:
	//DEBUG_VALUE: prjm_eval_func_execute_while:loop_count_int <- [DW_OP_consts 18446744073708503041, DW_OP_minus, DW_OP_consts 18446744073709551615, DW_OP_mul, DW_OP_consts 1048575, DW_OP_plus, DW_OP_stack_value] $x22
	.loc	2 293 53                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:293:53
	fcmp	d0, d8
	ccmp	x22, #0, #4, gt
	add	x22, x22, #1
.Ltmp41:
	b.ne	.LBB5_1
.Ltmp42:
// %bb.2:
	//DEBUG_VALUE: prjm_eval_func_execute_while:ctx <- $x20
	//DEBUG_VALUE: prjm_eval_func_execute_while:ret_val <- $x19
	.loc	2 295 5 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:295:5
	str	x8, [x19]
	.loc	2 296 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:296:1
	ldr	x8, [x21, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB5_4
.Ltmp43:
// %bb.3:
	//DEBUG_VALUE: prjm_eval_func_execute_while:ctx <- $x20
	//DEBUG_VALUE: prjm_eval_func_execute_while:ret_val <- $x19
	.cfi_def_cfa wsp, 80
	.loc	2 296 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:296:1
	ldp	x20, x19, [sp, #64]             // 16-byte Folded Reload
.Ltmp44:
	//DEBUG_VALUE: prjm_eval_func_execute_while:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_execute_while:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	d8, [sp, #16]                   // 8-byte Folded Reload
	ldp	x22, x21, [sp, #48]             // 16-byte Folded Reload
	ldp	x29, x30, [sp, #32]             // 16-byte Folded Reload
	add	sp, sp, #80
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w22
	.cfi_restore w30
	.cfi_restore w29
	.cfi_restore b8
	ret
.Ltmp45:
.LBB5_4:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_execute_while:ctx <- $x20
	//DEBUG_VALUE: prjm_eval_func_execute_while:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp46:
.Lfunc_end5:
	.size	prjm_eval_func_execute_while, .Lfunc_end5-prjm_eval_func_execute_while
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_if,"ax",@progbits
	.hidden	prjm_eval_func_if               // -- Begin function prjm_eval_func_if
	.globl	prjm_eval_func_if
	.p2align	2
	.type	prjm_eval_func_if,@function
prjm_eval_func_if:                      // @prjm_eval_func_if
.Lfunc_begin6:
	.loc	2 299 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:299:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_if:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_if:ret_val <- $x1
	sub	sp, sp, #64
	.cfi_def_cfa_offset 64
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	str	x21, [sp, #32]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #48]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x19, x0
.Ltmp47:
	//DEBUG_VALUE: prjm_eval_func_if:ctx <- $x19
	mov	x20, x1
.Ltmp48:
	//DEBUG_VALUE: prjm_eval_func_if:ret_val <- $x20
	//DEBUG_VALUE: prjm_eval_func_if:ret_val <- $x20
	ldr	x8, [x21, #40]
.Ltmp49:
	.loc	2 304 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:304:5
	mov	x1, sp
	str	x8, [sp, #8]
	.loc	2 302 33                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:302:33
	add	x8, x0, #8
	.loc	2 304 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:304:5
	ldr	x9, [x0, #24]
	.loc	2 302 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:302:18
	str	x8, [sp]
	.loc	2 304 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:304:5
	ldr	x0, [x9]
	ldr	x8, [x0]
	blr	x8
.Ltmp50:
	.loc	2 306 11                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:306:11
	ldr	x8, [sp]
	mov	w9, #16                         // =0x10
	mov	w10, #8                         // =0x8
.Ltmp51:
	.loc	2 0 0 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	mov	x1, x20
.Ltmp52:
	//DEBUG_VALUE: prjm_eval_func_if:ret_val <- $x1
	.loc	2 306 10                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:306:10
	ldr	d0, [x8]
.Ltmp53:
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	ldr	x8, [x19, #24]
	fcmp	d0, #0.0
	csel	x9, x10, x9, ne
	ldr	x0, [x8, x9]
	ldr	x8, [x0]
	blr	x8
.Ltmp54:
	.loc	2 312 1 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:312:1
	ldr	x8, [x21, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB6_2
.Ltmp55:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_if:ctx <- $x19
	.cfi_def_cfa wsp, 64
	.loc	2 312 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:312:1
	ldp	x20, x19, [sp, #48]             // 16-byte Folded Reload
.Ltmp56:
	//DEBUG_VALUE: prjm_eval_func_if:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	ldr	x21, [sp, #32]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #64
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp57:
.LBB6_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_if:ctx <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp58:
.Lfunc_end6:
	.size	prjm_eval_func_if, .Lfunc_end6-prjm_eval_func_if
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_exec2,"ax",@progbits
	.hidden	prjm_eval_func_exec2            // -- Begin function prjm_eval_func_exec2
	.globl	prjm_eval_func_exec2
	.p2align	2
	.type	prjm_eval_func_exec2,@function
prjm_eval_func_exec2:                   // @prjm_eval_func_exec2
.Lfunc_begin7:
	.loc	2 315 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:315:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_exec2:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_exec2:ret_val <- $x1
	sub	sp, sp, #64
	.cfi_def_cfa_offset 64
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	str	x21, [sp, #32]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #48]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x19, x0
.Ltmp59:
	//DEBUG_VALUE: prjm_eval_func_exec2:ctx <- $x19
	//DEBUG_VALUE: prjm_eval_func_exec2:ctx <- $x19
	mov	x20, x1
.Ltmp60:
	//DEBUG_VALUE: prjm_eval_func_exec2:ret_val <- $x20
	//DEBUG_VALUE: prjm_eval_func_exec2:ret_val <- $x20
	ldr	x8, [x21, #40]
.Ltmp61:
	.loc	2 321 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:321:5
	mov	x1, sp
	str	x8, [sp, #8]
	.loc	2 318 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:318:16
	str	xzr, [x19, #8]!
.Ltmp62:
	//DEBUG_VALUE: prjm_eval_func_exec2:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 321 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:321:5
	ldr	x8, [x19, #16]
	.loc	2 319 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:319:18
	str	x19, [sp]
	.loc	2 321 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:321:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp63:
	.loc	2 322 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:322:5
	ldr	x8, [x19, #16]
	mov	x1, x20
.Ltmp64:
	//DEBUG_VALUE: prjm_eval_func_exec2:ret_val <- $x1
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp65:
	.loc	2 323 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:323:1
	ldr	x8, [x21, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB7_2
.Ltmp66:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_exec2:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.cfi_def_cfa wsp, 64
	.loc	2 323 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:323:1
	ldp	x20, x19, [sp, #48]             // 16-byte Folded Reload
	ldr	x21, [sp, #32]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #64
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp67:
.LBB7_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_exec2:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp68:
.Lfunc_end7:
	.size	prjm_eval_func_exec2, .Lfunc_end7-prjm_eval_func_exec2
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_exec3,"ax",@progbits
	.hidden	prjm_eval_func_exec3            // -- Begin function prjm_eval_func_exec3
	.globl	prjm_eval_func_exec3
	.p2align	2
	.type	prjm_eval_func_exec3,@function
prjm_eval_func_exec3:                   // @prjm_eval_func_exec3
.Lfunc_begin8:
	.loc	2 326 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:326:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_exec3:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_exec3:ret_val <- $x1
	sub	sp, sp, #64
	.cfi_def_cfa_offset 64
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	str	x21, [sp, #32]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #48]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x19, x0
.Ltmp69:
	//DEBUG_VALUE: prjm_eval_func_exec3:ctx <- $x19
	//DEBUG_VALUE: prjm_eval_func_exec3:ctx <- $x19
	mov	x20, x1
.Ltmp70:
	//DEBUG_VALUE: prjm_eval_func_exec3:ret_val <- $x20
	//DEBUG_VALUE: prjm_eval_func_exec3:ret_val <- $x20
	ldr	x8, [x21, #40]
.Ltmp71:
	.loc	2 332 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:332:5
	mov	x1, sp
	str	x8, [sp, #8]
	.loc	2 329 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:329:16
	str	xzr, [x19, #8]!
.Ltmp72:
	//DEBUG_VALUE: prjm_eval_func_exec3:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 332 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:332:5
	ldr	x8, [x19, #16]
	.loc	2 330 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:330:18
	str	x19, [sp]
	.loc	2 332 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:332:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp73:
	.loc	2 333 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:333:5
	ldr	x8, [x19, #16]
	mov	x1, sp
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp74:
	.loc	2 334 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:334:5
	ldr	x8, [x19, #16]
	mov	x1, x20
.Ltmp75:
	//DEBUG_VALUE: prjm_eval_func_exec3:ret_val <- $x1
	ldr	x0, [x8, #16]
	ldr	x8, [x0]
	blr	x8
.Ltmp76:
	.loc	2 335 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:335:1
	ldr	x8, [x21, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB8_2
.Ltmp77:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_exec3:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.cfi_def_cfa wsp, 64
	.loc	2 335 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:335:1
	ldp	x20, x19, [sp, #48]             // 16-byte Folded Reload
	ldr	x21, [sp, #32]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #64
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp78:
.LBB8_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_exec3:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp79:
.Lfunc_end8:
	.size	prjm_eval_func_exec3, .Lfunc_end8-prjm_eval_func_exec3
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_set,"ax",@progbits
	.hidden	prjm_eval_func_set              // -- Begin function prjm_eval_func_set
	.globl	prjm_eval_func_set
	.p2align	2
	.type	prjm_eval_func_set,@function
prjm_eval_func_set:                     // @prjm_eval_func_set
.Lfunc_begin9:
	.loc	2 338 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:338:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_set:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_set:ret_val <- $x1
	sub	sp, sp, #64
	.cfi_def_cfa_offset 64
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	str	x21, [sp, #32]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #48]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x19, x0
.Ltmp80:
	//DEBUG_VALUE: prjm_eval_func_set:ctx <- $x19
	//DEBUG_VALUE: prjm_eval_func_set:ctx <- $x19
	mov	x20, x1
.Ltmp81:
	//DEBUG_VALUE: prjm_eval_func_set:ret_val <- $x20
	ldr	x8, [x21, #40]
	str	x8, [sp, #8]
.Ltmp82:
	.loc	2 341 16 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:341:16
	str	xzr, [x19, #8]!
.Ltmp83:
	//DEBUG_VALUE: prjm_eval_func_set:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 344 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:344:5
	ldr	x8, [x19, #16]
	.loc	2 342 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:342:18
	str	x19, [sp]
	.loc	2 344 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:344:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp84:
	.loc	2 345 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:345:5
	ldr	x8, [x19, #16]
	mov	x1, sp
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp85:
	.loc	2 347 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:347:5
	ldr	x8, [sp]
	ldr	d0, [x8]
	ldr	x8, [x20]
	str	d0, [x8]
	.loc	2 348 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:348:1
	ldr	x8, [x21, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB9_2
.Ltmp86:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_set:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_set:ret_val <- $x20
	.cfi_def_cfa wsp, 64
	.loc	2 348 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:348:1
	ldp	x20, x19, [sp, #48]             // 16-byte Folded Reload
.Ltmp87:
	//DEBUG_VALUE: prjm_eval_func_set:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #32]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #64
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp88:
.LBB9_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_set:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_set:ret_val <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp89:
.Lfunc_end9:
	.size	prjm_eval_func_set, .Lfunc_end9-prjm_eval_func_set
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_mem
.LCPI10_0:
	.xword	0x3f1a36e2eb1c432d              // double 1.0E-4
	.section	.text.prjm_eval_func_mem,"ax",@progbits
	.hidden	prjm_eval_func_mem
	.globl	prjm_eval_func_mem
	.p2align	2
	.type	prjm_eval_func_mem,@function
prjm_eval_func_mem:                     // @prjm_eval_func_mem
.Lfunc_begin10:
	.loc	2 353 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:353:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_mem:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_mem:ret_val <- $x1
	sub	sp, sp, #64
	.cfi_def_cfa_offset 64
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	str	x21, [sp, #32]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #48]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp90:
	//DEBUG_VALUE: prjm_eval_func_mem:ctx <- $x20
	//DEBUG_VALUE: prjm_eval_func_mem:ctx <- $x20
	mov	x19, x1
.Ltmp91:
	//DEBUG_VALUE: prjm_eval_func_mem:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mem:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp92:
	.loc	2 359 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:359:5
	mov	x1, sp
	str	x8, [sp, #8]
	.loc	2 357 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:357:16
	str	xzr, [x20, #8]!
.Ltmp93:
	//DEBUG_VALUE: prjm_eval_func_mem:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 359 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:359:5
	ldr	x8, [x20, #16]
	.loc	2 358 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:358:18
	str	x20, [sp]
	.loc	2 359 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:359:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp94:
	.loc	2 362 87                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:362:87
	ldr	x8, [sp]
	adrp	x9, .LCPI10_0
	.loc	2 362 60 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:362:60
	ldr	x0, [x20, #8]
	ldr	d1, [x9, :lo12:.LCPI10_0]
	.loc	2 362 86                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:362:86
	ldr	d0, [x8]
	.loc	2 362 97                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:362:97
	fadd	d0, d0, d1
	.loc	2 362 75                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:362:75
	fcvtzs	w1, d0
	.loc	2 362 29                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:362:29
	bl	prjm_eval_memory_allocate
.Ltmp95:
	//DEBUG_VALUE: prjm_eval_func_mem:mem_addr <- $x0
	.loc	2 363 9 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:363:9
	cbz	x0, .LBB10_3
.Ltmp96:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_mem:mem_addr <- $x0
	//DEBUG_VALUE: prjm_eval_func_mem:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_mem:ret_val <- $x19
	.loc	2 365 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:365:9
	str	x0, [x19]
.Ltmp97:
	.loc	2 370 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:370:1
	ldr	x8, [x21, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB10_4
.Ltmp98:
.LBB10_2:
	//DEBUG_VALUE: prjm_eval_func_mem:mem_addr <- $x0
	//DEBUG_VALUE: prjm_eval_func_mem:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_mem:ret_val <- $x19
	.cfi_def_cfa wsp, 64
	.loc	2 370 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:370:1
	ldp	x20, x19, [sp, #48]             // 16-byte Folded Reload
.Ltmp99:
	//DEBUG_VALUE: prjm_eval_func_mem:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #32]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #64
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp100:
.LBB10_3:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_mem:mem_addr <- $x0
	//DEBUG_VALUE: prjm_eval_func_mem:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_mem:ret_val <- $x19
	.loc	2 369 5 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:369:5
	ldr	x8, [x19]
	str	xzr, [x8]
	.loc	2 370 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:370:1
	ldr	x8, [x21, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.eq	.LBB10_2
.Ltmp101:
.LBB10_4:
	//DEBUG_VALUE: prjm_eval_func_mem:mem_addr <- $x0
	//DEBUG_VALUE: prjm_eval_func_mem:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_mem:ret_val <- $x19
	.loc	2 0 0 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp102:
.Lfunc_end10:
	.size	prjm_eval_func_mem, .Lfunc_end10-prjm_eval_func_mem
	.cfi_endproc
	.file	5 "/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit" "i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/MemoryBuffer.h"
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_freembuf
.LCPI11_0:
	.xword	0x3f1a36e2eb1c432d              // double 1.0E-4
	.section	.text.prjm_eval_func_freembuf,"ax",@progbits
	.hidden	prjm_eval_func_freembuf
	.globl	prjm_eval_func_freembuf
	.p2align	2
	.type	prjm_eval_func_freembuf,@function
prjm_eval_func_freembuf:                // @prjm_eval_func_freembuf
.Lfunc_begin11:
	.loc	2 373 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:373:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_freembuf:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_freembuf:ret_val <- $x1
	stp	x29, x30, [sp, #-32]!           // 16-byte Folded Spill
	.cfi_def_cfa_offset 32
	stp	x20, x19, [sp, #16]             // 16-byte Folded Spill
	mov	x29, sp
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
.Ltmp103:
	.loc	2 377 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:377:5
	ldr	x8, [x0, #24]
	mov	x19, x0
.Ltmp104:
	//DEBUG_VALUE: prjm_eval_func_freembuf:ctx <- $x19
	//DEBUG_VALUE: prjm_eval_func_freembuf:ctx <- $x19
	.loc	2 0 5 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:5
	mov	x20, x1
.Ltmp105:
	//DEBUG_VALUE: prjm_eval_func_freembuf:ret_val <- $x20
	.loc	2 377 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:377:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp106:
	.loc	2 380 65 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:380:65
	ldr	x8, [x20]
	adrp	x9, .LCPI11_0
	ldr	d1, [x9, :lo12:.LCPI11_0]
	.loc	2 380 64 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:380:64
	ldr	d0, [x8]
	.loc	2 380 74                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:380:74
	fadd	d0, d0, d1
	.loc	2 380 53                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:380:53
	fcvtzs	w1, d0
	.loc	2 380 38                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:380:38
	ldr	x0, [x19, #16]
	.cfi_def_cfa wsp, 32
	.loc	2 380 5 epilogue_begin          // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:380:5
	ldp	x20, x19, [sp, #16]             // 16-byte Folded Reload
.Ltmp107:
	//DEBUG_VALUE: prjm_eval_func_freembuf:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	//DEBUG_VALUE: prjm_eval_func_freembuf:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	ldp	x29, x30, [sp], #32             // 16-byte Folded Reload
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
.Ltmp108:
	b	prjm_eval_memory_free_block
.Ltmp109:
.Lfunc_end11:
	.size	prjm_eval_func_freembuf, .Lfunc_end11-prjm_eval_func_freembuf
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_memcpy,"ax",@progbits
	.hidden	prjm_eval_func_memcpy           // -- Begin function prjm_eval_func_memcpy
	.globl	prjm_eval_func_memcpy
	.p2align	2
	.type	prjm_eval_func_memcpy,@function
prjm_eval_func_memcpy:                  // @prjm_eval_func_memcpy
.Lfunc_begin12:
	.loc	2 384 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:384:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_memcpy:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_memcpy:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp110:
	//DEBUG_VALUE: prjm_eval_func_memcpy:ctx <- $x20
	//DEBUG_VALUE: prjm_eval_func_memcpy:ctx <- $x20
	mov	x19, x1
.Ltmp111:
	//DEBUG_VALUE: prjm_eval_func_memcpy:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_memcpy:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp112:
	.loc	2 394 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:394:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 387 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:387:16
	str	xzr, [x20, #8]!
.Ltmp113:
	//DEBUG_VALUE: prjm_eval_func_memcpy:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 394 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:394:5
	ldr	x9, [x20, #16]
	.loc	2 390 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:390:18
	stp	x8, x20, [sp, #8]
	add	x8, sp, #24
	.loc	2 392 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:392:18
	str	x8, [sp]
	.loc	2 394 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:394:5
	ldr	x0, [x9]
	.loc	2 388 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:388:17
	stur	xzr, [x29, #-16]
	.loc	2 389 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:389:17
	str	xzr, [sp, #24]
	.loc	2 394 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:394:5
	ldr	x8, [x0]
	blr	x8
.Ltmp114:
	.loc	2 395 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:395:5
	ldr	x8, [x20, #16]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp115:
	.loc	2 396 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:396:5
	ldr	x8, [x20, #16]
	mov	x1, sp
	ldr	x0, [x8, #16]
	ldr	x8, [x0]
	blr	x8
.Ltmp116:
	.loc	2 398 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:398:5
	ldp	x2, x1, [sp, #8]
	ldr	x0, [x20, #8]
	ldr	x3, [sp]
	bl	prjm_eval_memory_copy
.Ltmp117:
	str	x0, [x19]
	.loc	2 399 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:399:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB12_2
.Ltmp118:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_memcpy:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_memcpy:ret_val <- $x19
	.cfi_def_cfa wsp, 96
	.loc	2 399 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:399:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp119:
	//DEBUG_VALUE: prjm_eval_func_memcpy:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp120:
.LBB12_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_memcpy:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_memcpy:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp121:
.Lfunc_end12:
	.size	prjm_eval_func_memcpy, .Lfunc_end12-prjm_eval_func_memcpy
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_memset,"ax",@progbits
	.hidden	prjm_eval_func_memset           // -- Begin function prjm_eval_func_memset
	.globl	prjm_eval_func_memset
	.p2align	2
	.type	prjm_eval_func_memset,@function
prjm_eval_func_memset:                  // @prjm_eval_func_memset
.Lfunc_begin13:
	.loc	2 402 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:402:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_memset:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_memset:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp122:
	//DEBUG_VALUE: prjm_eval_func_memset:ctx <- $x20
	//DEBUG_VALUE: prjm_eval_func_memset:ctx <- $x20
	mov	x19, x1
.Ltmp123:
	//DEBUG_VALUE: prjm_eval_func_memset:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_memset:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp124:
	.loc	2 412 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:412:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 405 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:405:16
	str	xzr, [x20, #8]!
.Ltmp125:
	//DEBUG_VALUE: prjm_eval_func_memset:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 412 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:412:5
	ldr	x9, [x20, #16]
	.loc	2 408 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:408:18
	stp	x8, x20, [sp, #8]
	add	x8, sp, #24
	.loc	2 410 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:410:18
	str	x8, [sp]
	.loc	2 412 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:412:5
	ldr	x0, [x9]
	.loc	2 406 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:406:17
	stur	xzr, [x29, #-16]
	.loc	2 407 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:407:17
	str	xzr, [sp, #24]
	.loc	2 412 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:412:5
	ldr	x8, [x0]
	blr	x8
.Ltmp126:
	.loc	2 413 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:413:5
	ldr	x8, [x20, #16]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp127:
	.loc	2 414 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:414:5
	ldr	x8, [x20, #16]
	mov	x1, sp
	ldr	x0, [x8, #16]
	ldr	x8, [x0]
	blr	x8
.Ltmp128:
	.loc	2 416 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:416:5
	ldp	x2, x1, [sp, #8]
	ldr	x0, [x20, #8]
	ldr	x3, [sp]
	bl	prjm_eval_memory_set
.Ltmp129:
	str	x0, [x19]
	.loc	2 417 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:417:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB13_2
.Ltmp130:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_memset:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_memset:ret_val <- $x19
	.cfi_def_cfa wsp, 96
	.loc	2 417 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:417:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp131:
	//DEBUG_VALUE: prjm_eval_func_memset:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp132:
.LBB13_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_memset:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_memset:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp133:
.Lfunc_end13:
	.size	prjm_eval_func_memset, .Lfunc_end13-prjm_eval_func_memset
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_bnot
.LCPI14_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_bnot,"ax",@progbits
	.hidden	prjm_eval_func_bnot
	.globl	prjm_eval_func_bnot
	.p2align	2
	.type	prjm_eval_func_bnot,@function
prjm_eval_func_bnot:                    // @prjm_eval_func_bnot
.Lfunc_begin14:
	.loc	2 424 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:424:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_bnot:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_bnot:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp134:
	//DEBUG_VALUE: prjm_eval_func_bnot:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_bnot:ret_val <- $x19
	.loc	2 430 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:430:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 427 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:427:16
	str	xzr, [x0, #8]!
.Ltmp135:
	//DEBUG_VALUE: prjm_eval_func_bnot:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 430 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:430:5
	ldr	x8, [x0, #16]
	.loc	2 428 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:428:18
	str	x0, [sp]
	.loc	2 430 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:430:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp136:
	.loc	2 432 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:432:5
	ldr	x8, [sp]
	movi	d2, #0000000000000000
	ldr	d0, [x8]
	adrp	x8, .LCPI14_0
	ldr	d1, [x8, :lo12:.LCPI14_0]
	ldr	x8, [x19]
	fabs	d0, d0
	fcmp	d0, d1
	fmov	d0, #1.00000000
	fcsel	d0, d0, d2, lt
	str	d0, [x8]
	.loc	2 433 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:433:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB14_2
.Ltmp137:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_bnot:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_bnot:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 433 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:433:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp138:
	//DEBUG_VALUE: prjm_eval_func_bnot:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp139:
.LBB14_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_bnot:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_bnot:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp140:
.Lfunc_end14:
	.size	prjm_eval_func_bnot, .Lfunc_end14-prjm_eval_func_bnot
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_equal
.LCPI15_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_equal,"ax",@progbits
	.hidden	prjm_eval_func_equal
	.globl	prjm_eval_func_equal
	.p2align	2
	.type	prjm_eval_func_equal,@function
prjm_eval_func_equal:                   // @prjm_eval_func_equal
.Lfunc_begin15:
	.loc	2 436 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:436:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_equal:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_equal:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp141:
	//DEBUG_VALUE: prjm_eval_func_equal:ctx <- $x20
	mov	x19, x1
.Ltmp142:
	//DEBUG_VALUE: prjm_eval_func_equal:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_equal:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp143:
	.loc	2 444 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:444:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 441 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:441:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 444 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:444:5
	ldr	x9, [x0, #24]
	.loc	2 442 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:442:18
	str	x8, [sp, #8]
	.loc	2 444 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:444:5
	ldr	x0, [x9]
	.loc	2 439 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:439:17
	stur	xzr, [x29, #-16]
	.loc	2 440 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:440:17
	str	xzr, [sp, #24]
	.loc	2 444 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:444:5
	ldr	x8, [x0]
	blr	x8
.Ltmp144:
	.loc	2 445 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:445:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp145:
	.loc	2 447 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:447:5
	ldp	x9, x8, [sp, #8]
	movi	d2, #0000000000000000
	ldr	d0, [x8]
	ldr	d1, [x9]
	adrp	x8, .LCPI15_0
	fabd	d0, d0, d1
	ldr	d1, [x8, :lo12:.LCPI15_0]
	ldr	x8, [x19]
	fcmp	d0, d1
	fmov	d0, #1.00000000
	fcsel	d0, d0, d2, lt
	str	d0, [x8]
	.loc	2 448 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:448:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB15_2
.Ltmp146:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_equal:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_equal:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 448 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:448:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp147:
	//DEBUG_VALUE: prjm_eval_func_equal:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_equal:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp148:
.LBB15_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_equal:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_equal:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp149:
.Lfunc_end15:
	.size	prjm_eval_func_equal, .Lfunc_end15-prjm_eval_func_equal
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_notequal
.LCPI16_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_notequal,"ax",@progbits
	.hidden	prjm_eval_func_notequal
	.globl	prjm_eval_func_notequal
	.p2align	2
	.type	prjm_eval_func_notequal,@function
prjm_eval_func_notequal:                // @prjm_eval_func_notequal
.Lfunc_begin16:
	.loc	2 451 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:451:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_notequal:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_notequal:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp150:
	//DEBUG_VALUE: prjm_eval_func_notequal:ctx <- $x20
	mov	x19, x1
.Ltmp151:
	//DEBUG_VALUE: prjm_eval_func_notequal:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_notequal:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp152:
	.loc	2 458 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:458:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 456 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:456:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 458 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:458:5
	ldr	x9, [x0, #24]
	.loc	2 457 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:457:18
	str	x8, [sp, #8]
	.loc	2 458 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:458:5
	ldr	x0, [x9]
	.loc	2 454 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:454:17
	stur	xzr, [x29, #-16]
	.loc	2 455 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:455:17
	str	xzr, [sp, #24]
	.loc	2 458 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:458:5
	ldr	x8, [x0]
	blr	x8
.Ltmp153:
	.loc	2 459 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:459:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp154:
	.loc	2 461 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:461:5
	ldp	x9, x8, [sp, #8]
	movi	d2, #0000000000000000
	ldr	d0, [x8]
	ldr	d1, [x9]
	adrp	x8, .LCPI16_0
	fabd	d0, d0, d1
	ldr	d1, [x8, :lo12:.LCPI16_0]
	ldr	x8, [x19]
	fcmp	d0, d1
	fmov	d0, #1.00000000
	fcsel	d0, d0, d2, gt
	str	d0, [x8]
	.loc	2 462 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:462:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB16_2
.Ltmp155:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_notequal:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_notequal:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 462 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:462:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp156:
	//DEBUG_VALUE: prjm_eval_func_notequal:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_notequal:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp157:
.LBB16_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_notequal:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_notequal:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp158:
.Lfunc_end16:
	.size	prjm_eval_func_notequal, .Lfunc_end16-prjm_eval_func_notequal
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_below,"ax",@progbits
	.hidden	prjm_eval_func_below            // -- Begin function prjm_eval_func_below
	.globl	prjm_eval_func_below
	.p2align	2
	.type	prjm_eval_func_below,@function
prjm_eval_func_below:                   // @prjm_eval_func_below
.Lfunc_begin17:
	.loc	2 465 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:465:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_below:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_below:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp159:
	//DEBUG_VALUE: prjm_eval_func_below:ctx <- $x20
	mov	x19, x1
.Ltmp160:
	//DEBUG_VALUE: prjm_eval_func_below:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_below:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp161:
	.loc	2 473 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:473:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 470 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:470:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 473 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:473:5
	ldr	x9, [x0, #24]
	.loc	2 471 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:471:18
	str	x8, [sp, #8]
	.loc	2 473 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:473:5
	ldr	x0, [x9]
	.loc	2 468 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:468:17
	stur	xzr, [x29, #-16]
	.loc	2 469 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:469:17
	str	xzr, [sp, #24]
	.loc	2 473 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:473:5
	ldr	x8, [x0]
	blr	x8
.Ltmp162:
	.loc	2 474 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:474:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp163:
	.loc	2 476 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:476:5
	ldp	x9, x8, [sp, #8]
	movi	d2, #0000000000000000
	ldr	d0, [x8]
	ldr	d1, [x9]
	ldr	x8, [x19]
	fcmp	d0, d1
	fmov	d0, #1.00000000
	fcsel	d0, d0, d2, lt
	str	d0, [x8]
	.loc	2 477 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:477:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB17_2
.Ltmp164:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_below:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_below:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 477 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:477:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp165:
	//DEBUG_VALUE: prjm_eval_func_below:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_below:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp166:
.LBB17_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_below:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_below:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp167:
.Lfunc_end17:
	.size	prjm_eval_func_below, .Lfunc_end17-prjm_eval_func_below
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_above,"ax",@progbits
	.hidden	prjm_eval_func_above            // -- Begin function prjm_eval_func_above
	.globl	prjm_eval_func_above
	.p2align	2
	.type	prjm_eval_func_above,@function
prjm_eval_func_above:                   // @prjm_eval_func_above
.Lfunc_begin18:
	.loc	2 480 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:480:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_above:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_above:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp168:
	//DEBUG_VALUE: prjm_eval_func_above:ctx <- $x20
	mov	x19, x1
.Ltmp169:
	//DEBUG_VALUE: prjm_eval_func_above:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_above:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp170:
	.loc	2 488 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:488:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 485 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:485:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 488 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:488:5
	ldr	x9, [x0, #24]
	.loc	2 486 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:486:18
	str	x8, [sp, #8]
	.loc	2 488 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:488:5
	ldr	x0, [x9]
	.loc	2 483 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:483:17
	stur	xzr, [x29, #-16]
	.loc	2 484 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:484:17
	str	xzr, [sp, #24]
	.loc	2 488 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:488:5
	ldr	x8, [x0]
	blr	x8
.Ltmp171:
	.loc	2 489 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:489:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp172:
	.loc	2 491 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:491:5
	ldp	x9, x8, [sp, #8]
	movi	d2, #0000000000000000
	ldr	d0, [x8]
	ldr	d1, [x9]
	ldr	x8, [x19]
	fcmp	d0, d1
	fmov	d0, #1.00000000
	fcsel	d0, d0, d2, gt
	str	d0, [x8]
	.loc	2 492 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:492:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB18_2
.Ltmp173:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_above:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_above:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 492 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:492:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp174:
	//DEBUG_VALUE: prjm_eval_func_above:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_above:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp175:
.LBB18_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_above:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_above:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp176:
.Lfunc_end18:
	.size	prjm_eval_func_above, .Lfunc_end18-prjm_eval_func_above
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_beloweq,"ax",@progbits
	.hidden	prjm_eval_func_beloweq          // -- Begin function prjm_eval_func_beloweq
	.globl	prjm_eval_func_beloweq
	.p2align	2
	.type	prjm_eval_func_beloweq,@function
prjm_eval_func_beloweq:                 // @prjm_eval_func_beloweq
.Lfunc_begin19:
	.loc	2 495 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:495:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_beloweq:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_beloweq:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp177:
	//DEBUG_VALUE: prjm_eval_func_beloweq:ctx <- $x20
	mov	x19, x1
.Ltmp178:
	//DEBUG_VALUE: prjm_eval_func_beloweq:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_beloweq:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp179:
	.loc	2 503 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:503:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 500 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:500:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 503 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:503:5
	ldr	x9, [x0, #24]
	.loc	2 501 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:501:18
	str	x8, [sp, #8]
	.loc	2 503 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:503:5
	ldr	x0, [x9]
	.loc	2 498 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:498:17
	stur	xzr, [x29, #-16]
	.loc	2 499 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:499:17
	str	xzr, [sp, #24]
	.loc	2 503 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:503:5
	ldr	x8, [x0]
	blr	x8
.Ltmp180:
	.loc	2 504 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:504:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp181:
	.loc	2 506 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:506:5
	ldp	x9, x8, [sp, #8]
	movi	d2, #0000000000000000
	ldr	d0, [x8]
	ldr	d1, [x9]
	ldr	x8, [x19]
	fcmp	d0, d1
	fmov	d0, #1.00000000
	fcsel	d0, d0, d2, le
	str	d0, [x8]
	.loc	2 507 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:507:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB19_2
.Ltmp182:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_beloweq:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_beloweq:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 507 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:507:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp183:
	//DEBUG_VALUE: prjm_eval_func_beloweq:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_beloweq:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp184:
.LBB19_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_beloweq:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_beloweq:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp185:
.Lfunc_end19:
	.size	prjm_eval_func_beloweq, .Lfunc_end19-prjm_eval_func_beloweq
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_aboveeq,"ax",@progbits
	.hidden	prjm_eval_func_aboveeq          // -- Begin function prjm_eval_func_aboveeq
	.globl	prjm_eval_func_aboveeq
	.p2align	2
	.type	prjm_eval_func_aboveeq,@function
prjm_eval_func_aboveeq:                 // @prjm_eval_func_aboveeq
.Lfunc_begin20:
	.loc	2 510 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:510:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_aboveeq:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_aboveeq:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp186:
	//DEBUG_VALUE: prjm_eval_func_aboveeq:ctx <- $x20
	mov	x19, x1
.Ltmp187:
	//DEBUG_VALUE: prjm_eval_func_aboveeq:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_aboveeq:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp188:
	.loc	2 518 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:518:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 515 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:515:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 518 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:518:5
	ldr	x9, [x0, #24]
	.loc	2 516 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:516:18
	str	x8, [sp, #8]
	.loc	2 518 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:518:5
	ldr	x0, [x9]
	.loc	2 513 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:513:17
	stur	xzr, [x29, #-16]
	.loc	2 514 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:514:17
	str	xzr, [sp, #24]
	.loc	2 518 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:518:5
	ldr	x8, [x0]
	blr	x8
.Ltmp189:
	.loc	2 519 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:519:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp190:
	.loc	2 521 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:521:5
	ldp	x9, x8, [sp, #8]
	movi	d2, #0000000000000000
	ldr	d0, [x8]
	ldr	d1, [x9]
	ldr	x8, [x19]
	fcmp	d0, d1
	fmov	d0, #1.00000000
	fcsel	d0, d0, d2, ge
	str	d0, [x8]
	.loc	2 522 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:522:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB20_2
.Ltmp191:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_aboveeq:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_aboveeq:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 522 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:522:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp192:
	//DEBUG_VALUE: prjm_eval_func_aboveeq:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_aboveeq:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp193:
.LBB20_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_aboveeq:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_aboveeq:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp194:
.Lfunc_end20:
	.size	prjm_eval_func_aboveeq, .Lfunc_end20-prjm_eval_func_aboveeq
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_add,"ax",@progbits
	.hidden	prjm_eval_func_add              // -- Begin function prjm_eval_func_add
	.globl	prjm_eval_func_add
	.p2align	2
	.type	prjm_eval_func_add,@function
prjm_eval_func_add:                     // @prjm_eval_func_add
.Lfunc_begin21:
	.loc	2 525 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:525:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_add:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_add:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp195:
	//DEBUG_VALUE: prjm_eval_func_add:ctx <- $x20
	mov	x19, x1
.Ltmp196:
	//DEBUG_VALUE: prjm_eval_func_add:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_add:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp197:
	.loc	2 533 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:533:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 530 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:530:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 533 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:533:5
	ldr	x9, [x0, #24]
	.loc	2 531 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:531:18
	str	x8, [sp, #8]
	.loc	2 533 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:533:5
	ldr	x0, [x9]
	.loc	2 528 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:528:17
	stur	xzr, [x29, #-16]
	.loc	2 529 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:529:17
	str	xzr, [sp, #24]
	.loc	2 533 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:533:5
	ldr	x8, [x0]
	blr	x8
.Ltmp198:
	.loc	2 534 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:534:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp199:
	.loc	2 536 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:536:5
	ldp	x9, x8, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	ldr	x8, [x19]
	fadd	d0, d1, d0
	str	d0, [x8]
	.loc	2 537 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:537:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB21_2
.Ltmp200:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_add:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_add:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 537 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:537:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp201:
	//DEBUG_VALUE: prjm_eval_func_add:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_add:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp202:
.LBB21_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_add:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_add:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp203:
.Lfunc_end21:
	.size	prjm_eval_func_add, .Lfunc_end21-prjm_eval_func_add
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_sub,"ax",@progbits
	.hidden	prjm_eval_func_sub              // -- Begin function prjm_eval_func_sub
	.globl	prjm_eval_func_sub
	.p2align	2
	.type	prjm_eval_func_sub,@function
prjm_eval_func_sub:                     // @prjm_eval_func_sub
.Lfunc_begin22:
	.loc	2 540 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:540:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_sub:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_sub:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp204:
	//DEBUG_VALUE: prjm_eval_func_sub:ctx <- $x20
	mov	x19, x1
.Ltmp205:
	//DEBUG_VALUE: prjm_eval_func_sub:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_sub:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp206:
	.loc	2 548 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:548:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 545 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:545:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 548 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:548:5
	ldr	x9, [x0, #24]
	.loc	2 546 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:546:18
	str	x8, [sp, #8]
	.loc	2 548 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:548:5
	ldr	x0, [x9]
	.loc	2 543 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:543:17
	stur	xzr, [x29, #-16]
	.loc	2 544 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:544:17
	str	xzr, [sp, #24]
	.loc	2 548 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:548:5
	ldr	x8, [x0]
	blr	x8
.Ltmp207:
	.loc	2 549 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:549:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp208:
	.loc	2 551 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:551:5
	ldp	x9, x8, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	ldr	x8, [x19]
	fsub	d0, d0, d1
	str	d0, [x8]
	.loc	2 552 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:552:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB22_2
.Ltmp209:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_sub:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_sub:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 552 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:552:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp210:
	//DEBUG_VALUE: prjm_eval_func_sub:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_sub:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp211:
.LBB22_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_sub:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_sub:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp212:
.Lfunc_end22:
	.size	prjm_eval_func_sub, .Lfunc_end22-prjm_eval_func_sub
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_mul,"ax",@progbits
	.hidden	prjm_eval_func_mul              // -- Begin function prjm_eval_func_mul
	.globl	prjm_eval_func_mul
	.p2align	2
	.type	prjm_eval_func_mul,@function
prjm_eval_func_mul:                     // @prjm_eval_func_mul
.Lfunc_begin23:
	.loc	2 555 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:555:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_mul:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_mul:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp213:
	//DEBUG_VALUE: prjm_eval_func_mul:ctx <- $x20
	mov	x19, x1
.Ltmp214:
	//DEBUG_VALUE: prjm_eval_func_mul:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mul:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp215:
	.loc	2 563 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:563:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 560 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:560:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 563 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:563:5
	ldr	x9, [x0, #24]
	.loc	2 561 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:561:18
	str	x8, [sp, #8]
	.loc	2 563 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:563:5
	ldr	x0, [x9]
	.loc	2 558 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:558:17
	stur	xzr, [x29, #-16]
	.loc	2 559 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:559:17
	str	xzr, [sp, #24]
	.loc	2 563 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:563:5
	ldr	x8, [x0]
	blr	x8
.Ltmp216:
	.loc	2 564 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:564:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp217:
	.loc	2 566 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:566:5
	ldp	x9, x8, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	ldr	x8, [x19]
	fmul	d0, d1, d0
	str	d0, [x8]
	.loc	2 567 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:567:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB23_2
.Ltmp218:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_mul:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mul:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 567 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:567:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp219:
	//DEBUG_VALUE: prjm_eval_func_mul:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_mul:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp220:
.LBB23_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_mul:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mul:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp221:
.Lfunc_end23:
	.size	prjm_eval_func_mul, .Lfunc_end23-prjm_eval_func_mul
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_div
.LCPI24_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_div,"ax",@progbits
	.hidden	prjm_eval_func_div
	.globl	prjm_eval_func_div
	.p2align	2
	.type	prjm_eval_func_div,@function
prjm_eval_func_div:                     // @prjm_eval_func_div
.Lfunc_begin24:
	.loc	2 570 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:570:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_div:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_div:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp222:
	//DEBUG_VALUE: prjm_eval_func_div:ctx <- $x20
	mov	x19, x1
.Ltmp223:
	//DEBUG_VALUE: prjm_eval_func_div:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_div:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp224:
	.loc	2 578 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:578:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 575 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:575:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 578 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:578:5
	ldr	x9, [x0, #24]
	.loc	2 576 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:576:18
	str	x8, [sp, #8]
	.loc	2 578 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:578:5
	ldr	x0, [x9]
	.loc	2 573 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:573:17
	stur	xzr, [x29, #-16]
	.loc	2 574 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:574:17
	str	xzr, [sp, #24]
	.loc	2 578 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:578:5
	ldr	x8, [x0]
	blr	x8
.Ltmp225:
	.loc	2 579 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:579:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp226:
	.loc	2 581 14                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:581:14
	ldr	x8, [sp, #8]
	movi	d1, #0000000000000000
	.loc	2 581 13 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:581:13
	ldr	d0, [x8]
	adrp	x8, .LCPI24_0
	ldr	d3, [x8, :lo12:.LCPI24_0]
	.loc	2 581 8                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:581:8
	fabs	d2, d0
.Ltmp227:
	.loc	2 581 8                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:581:8
	fcmp	d2, d3
	b.lt	.LBB24_2
.Ltmp228:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_div:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_div:ctx <- $x20
	.loc	2 587 5 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:587:5
	ldr	x8, [sp, #16]
	ldr	d1, [x8]
	fdiv	d1, d1, d0
.Ltmp229:
.LBB24_2:
	//DEBUG_VALUE: prjm_eval_func_div:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_div:ctx <- $x20
	.loc	2 0 0 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	ldr	x8, [x19]
	str	d1, [x8]
	.loc	2 588 1 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:588:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB24_4
.Ltmp230:
// %bb.3:
	//DEBUG_VALUE: prjm_eval_func_div:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_div:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 588 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:588:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp231:
	//DEBUG_VALUE: prjm_eval_func_div:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_div:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp232:
.LBB24_4:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_div:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_div:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp233:
.Lfunc_end24:
	.size	prjm_eval_func_div, .Lfunc_end24-prjm_eval_func_div
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_mod,"ax",@progbits
	.hidden	prjm_eval_func_mod              // -- Begin function prjm_eval_func_mod
	.globl	prjm_eval_func_mod
	.p2align	2
	.type	prjm_eval_func_mod,@function
prjm_eval_func_mod:                     // @prjm_eval_func_mod
.Lfunc_begin25:
	.loc	2 648 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:648:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp234:
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	mov	x19, x1
.Ltmp235:
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp236:
	.loc	2 656 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:656:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 653 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:653:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 656 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:656:5
	ldr	x9, [x0, #24]
	.loc	2 654 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:654:18
	str	x8, [sp, #8]
	.loc	2 656 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:656:5
	ldr	x0, [x9]
	.loc	2 651 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:651:17
	stur	xzr, [x29, #-16]
	.loc	2 652 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:652:17
	str	xzr, [sp, #24]
	.loc	2 656 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:656:5
	ldr	x8, [x0]
	blr	x8
.Ltmp237:
	.loc	2 657 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:657:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp238:
	.loc	2 659 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:659:5
	ldr	x8, [sp, #16]
	movi	d0, #0000000000000000
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorBits <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:numerator <- $d1
	mov	x9, #4890909195324358656        // =0x43e0000000000000
	ldr	d1, [x8]
.Ltmp239:
	//DEBUG_VALUE: memcpy:copy_amount <- 8
	//DEBUG_VALUE: memcpy: <- 8
	//DEBUG_VALUE: remainder_value_bits:value <- $d1
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- undef
	fmov	x10, d1
.Ltmp240:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- undef
	//DEBUG_VALUE: remainder_value_bits:bits <- undef
	//DEBUG_VALUE: memcpy:copy_amount <- 8
	//DEBUG_VALUE: memcpy: <- 8
	//DEBUG_VALUE: remainder_value_bits:value <- undef
	//DEBUG_VALUE: remainder_value_bits:bits <- $x10
	.loc	2 622 63                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:622:63
	and	x8, x10, #0x7fffffffffffffff
.Ltmp241:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- undef
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x8
	.loc	2 624 55                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:624:55
	cmp	x8, x9
	b.hi	.LBB25_12
.Ltmp242:
// %bb.1:
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x8
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	.loc	2 659 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:659:5
	ldr	x9, [sp, #8]
	ldr	d2, [x9]
.Ltmp243:
	//DEBUG_VALUE: remainder_value_bits:value <- $d2
	fmov	x11, d2
.Ltmp244:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x11
	//DEBUG_VALUE: remainder_value_bits:bits <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	.loc	2 0 0 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	and	x9, x11, #0x7fffffffffffffff
.Ltmp245:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x9
	.loc	2 624 55 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:624:55
	lsr	x12, x9, #52
	cmp	x12, #2046
	b.hi	.LBB25_12
.Ltmp246:
// %bb.2:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x9
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x8
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	.loc	2 0 55 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:55
	mov	x12, #4890909195324358656       // =0x43e0000000000000
.Ltmp247:
	.loc	2 629 58 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:629:58
	cmp	x8, x12
	b.ne	.LBB25_5
.Ltmp248:
// %bb.3:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x9
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x8
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	.loc	2 629 100 is_stmt 0             // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:629:100
	tbz	x10, #63, .LBB25_12
.Ltmp249:
// %bb.4:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x9
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x8
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	.loc	2 0 100                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:100
	mov	x10, #4890909195324358656       // =0x43e0000000000000
	.loc	2 629 100                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:629:100
	cmp	x9, x10
	b.ls	.LBB25_6
	b	.LBB25_12
.Ltmp250:
.LBB25_5:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x9
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x8
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	.loc	2 630 58 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:630:58
	cmp	x9, x12
	b.hi	.LBB25_12
.Ltmp251:
.LBB25_6:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x9
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x8
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	.loc	2 631 60                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:631:60
	tbnz	x11, #63, .LBB25_8
.Ltmp252:
// %bb.7:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x9
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x8
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	.loc	2 0 60 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:60
	mov	x10, #4890909195324358656       // =0x43e0000000000000
	.loc	2 631 60                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:631:60
	cmp	x9, x10
	b.eq	.LBB25_12
.Ltmp253:
.LBB25_8:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x9
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x8
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	//DEBUG_VALUE: bounded_milkdrop_remainder:dividend <- undef
	.loc	2 634 33 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:634:33
	fcvtzs	x10, d2
.Ltmp254:
	//DEBUG_VALUE: bounded_milkdrop_remainder:minimum <- -9223372036854775808
	//DEBUG_VALUE: bounded_milkdrop_remainder:divisor <- $x10
	.loc	2 640 22                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:640:22
	cbz	x10, .LBB25_12
.Ltmp255:
// %bb.9:
	//DEBUG_VALUE: bounded_milkdrop_remainder:divisor <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:minimum <- -9223372036854775808
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x9
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x8
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	.loc	2 0 22 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:22
	fcvtzs	x11, d1
.Ltmp256:
	//DEBUG_VALUE: bounded_milkdrop_remainder:dividend <- $x11
	mov	x12, #-9223372036854775808      // =0x8000000000000000
	.loc	2 640 46                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:640:46
	cmp	x11, x12
	b.ne	.LBB25_11
.Ltmp257:
// %bb.10:
	//DEBUG_VALUE: bounded_milkdrop_remainder:dividend <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:divisor <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:minimum <- -9223372036854775808
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x9
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x8
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	cmn	x10, #1
	b.eq	.LBB25_12
.Ltmp258:
.LBB25_11:
	//DEBUG_VALUE: bounded_milkdrop_remainder:dividend <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:divisor <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:minimum <- -9223372036854775808
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x9
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x8
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	.loc	2 642 59 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:642:59
	sdiv	x12, x11, x10
	lsr	x9, x9, #53
.Ltmp259:
	.loc	2 643 31                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:643:31
	lsr	x8, x8, #53
.Ltmp260:
	.loc	2 0 31 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:31
	cmp	x9, #527
	mov	w9, #527                        // =0x20f
	.loc	2 643 31                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:643:31
	ccmp	x8, x9, #2, lo
	.loc	2 642 59 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:642:59
	msub	x10, x12, x10, x11
.Ltmp261:
	.loc	2 642 35 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:642:35
	scvtf	d0, x10
.Ltmp262:
	//DEBUG_VALUE: bounded_milkdrop_remainder:remainder <- $d0
	.loc	2 643 63 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:643:63
	fabs	d1, d0
	fcsel	d0, d1, d0, lo
.Ltmp263:
.LBB25_12:
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	.loc	2 659 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:659:5
	ldr	x8, [x19]
	str	d0, [x8]
	.loc	2 660 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:660:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB25_14
.Ltmp264:
// %bb.13:
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 660 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:660:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp265:
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp266:
.LBB25_14:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_mod:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp267:
.Lfunc_end25:
	.size	prjm_eval_func_mod, .Lfunc_end25-prjm_eval_func_mod
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_boolean_and_op
.LCPI26_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_boolean_and_op,"ax",@progbits
	.hidden	prjm_eval_func_boolean_and_op
	.globl	prjm_eval_func_boolean_and_op
	.p2align	2
	.type	prjm_eval_func_boolean_and_op,@function
prjm_eval_func_boolean_and_op:          // @prjm_eval_func_boolean_and_op
.Lfunc_begin26:
	.loc	2 663 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:663:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	str	d8, [sp, #48]                   // 8-byte Folded Spill
	stp	x29, x30, [sp, #56]             // 16-byte Folded Spill
	str	x21, [sp, #72]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #56
	.cfi_def_cfa w29, 40
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -24
	.cfi_offset w30, -32
	.cfi_offset w29, -40
	.cfi_offset b8, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp268:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ctx <- $x20
	mov	x19, x1
.Ltmp269:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp270:
	.loc	2 675 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:675:5
	add	x1, sp, #24
	stur	x8, [x29, #-16]
	sub	x8, x29, #24
	.loc	2 667 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:667:18
	str	x8, [sp, #24]
	add	x8, sp, #16
	.loc	2 675 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:675:5
	ldr	x9, [x0, #24]
	.loc	2 669 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:669:18
	str	x8, [sp, #8]
	.loc	2 675 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:675:5
	ldr	x0, [x9]
	.loc	2 666 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:666:17
	stur	xzr, [x29, #-24]
	.loc	2 668 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:668:17
	str	xzr, [sp, #16]
	.loc	2 675 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:675:5
	ldr	x8, [x0]
	blr	x8
.Ltmp271:
	.loc	2 677 15                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:677:15
	ldr	x8, [sp, #24]
	.loc	2 677 14 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:677:14
	ldr	d0, [x8]
	adrp	x8, .LCPI26_0
	ldr	d8, [x8, :lo12:.LCPI26_0]
	.loc	2 677 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:677:9
	fabs	d1, d0
	movi	d0, #0000000000000000
.Ltmp272:
	.loc	2 677 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:677:9
	fcmp	d1, d8
	b.le	.LBB26_2
.Ltmp273:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ctx <- $x20
	.loc	2 679 9 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:679:9
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp274:
	.loc	2 681 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:681:9
	ldr	x8, [sp, #8]
	movi	d1, #0000000000000000
	ldr	d0, [x8]
	fabs	d0, d0
	fcmp	d0, d8
	fmov	d0, #1.00000000
	fcsel	d0, d0, d1, gt
.Ltmp275:
.LBB26_2:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ctx <- $x20
	.loc	2 0 0 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	ldr	x8, [x19]
	str	d0, [x8]
.Ltmp276:
	.loc	2 687 1 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:687:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-16]
	cmp	x8, x9
	b.ne	.LBB26_4
.Ltmp277:
// %bb.3:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 687 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:687:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp278:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #72]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #56]             // 16-byte Folded Reload
	ldr	d8, [sp, #48]                   // 8-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	.cfi_restore b8
	ret
.Ltmp279:
.LBB26_4:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_and_op:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp280:
.Lfunc_end26:
	.size	prjm_eval_func_boolean_and_op, .Lfunc_end26-prjm_eval_func_boolean_and_op
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_boolean_or_op
.LCPI27_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_boolean_or_op,"ax",@progbits
	.hidden	prjm_eval_func_boolean_or_op
	.globl	prjm_eval_func_boolean_or_op
	.p2align	2
	.type	prjm_eval_func_boolean_or_op,@function
prjm_eval_func_boolean_or_op:           // @prjm_eval_func_boolean_or_op
.Lfunc_begin27:
	.loc	2 690 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:690:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	str	d8, [sp, #48]                   // 8-byte Folded Spill
	stp	x29, x30, [sp, #56]             // 16-byte Folded Spill
	str	x21, [sp, #72]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #56
	.cfi_def_cfa w29, 40
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -24
	.cfi_offset w30, -32
	.cfi_offset w29, -40
	.cfi_offset b8, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp281:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ctx <- $x20
	mov	x19, x1
.Ltmp282:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp283:
	.loc	2 702 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:702:5
	add	x1, sp, #24
	stur	x8, [x29, #-16]
	sub	x8, x29, #24
	.loc	2 694 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:694:18
	str	x8, [sp, #24]
	add	x8, sp, #16
	.loc	2 702 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:702:5
	ldr	x9, [x0, #24]
	.loc	2 696 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:696:18
	str	x8, [sp, #8]
	.loc	2 702 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:702:5
	ldr	x0, [x9]
	.loc	2 693 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:693:17
	stur	xzr, [x29, #-24]
	.loc	2 695 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:695:17
	str	xzr, [sp, #16]
	.loc	2 702 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:702:5
	ldr	x8, [x0]
	blr	x8
.Ltmp284:
	.loc	2 704 15                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:704:15
	ldr	x8, [sp, #24]
	.loc	2 704 14 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:704:14
	ldr	d0, [x8]
	adrp	x8, .LCPI27_0
	ldr	d8, [x8, :lo12:.LCPI27_0]
	.loc	2 704 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:704:9
	fabs	d0, d0
.Ltmp285:
	.loc	2 704 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:704:9
	fcmp	d0, d8
	fmov	d0, #1.00000000
	b.ge	.LBB27_2
.Ltmp286:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ctx <- $x20
	.loc	2 706 9 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:706:9
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp287:
	.loc	2 708 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:708:9
	ldr	x8, [sp, #8]
	movi	d1, #0000000000000000
	ldr	d0, [x8]
	fabs	d0, d0
	fcmp	d0, d8
	fmov	d0, #1.00000000
	fcsel	d0, d0, d1, gt
.Ltmp288:
.LBB27_2:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ctx <- $x20
	.loc	2 0 0 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	ldr	x8, [x19]
	str	d0, [x8]
.Ltmp289:
	.loc	2 714 1 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:714:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-16]
	cmp	x8, x9
	b.ne	.LBB27_4
.Ltmp290:
// %bb.3:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 714 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:714:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp291:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #72]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #56]             // 16-byte Folded Reload
	ldr	d8, [sp, #48]                   // 8-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	.cfi_restore b8
	ret
.Ltmp292:
.LBB27_4:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_or_op:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp293:
.Lfunc_end27:
	.size	prjm_eval_func_boolean_or_op, .Lfunc_end27-prjm_eval_func_boolean_or_op
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_boolean_and_func
.LCPI28_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_boolean_and_func,"ax",@progbits
	.hidden	prjm_eval_func_boolean_and_func
	.globl	prjm_eval_func_boolean_and_func
	.p2align	2
	.type	prjm_eval_func_boolean_and_func,@function
prjm_eval_func_boolean_and_func:        // @prjm_eval_func_boolean_and_func
.Lfunc_begin28:
	.loc	2 717 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:717:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp294:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ctx <- $x20
	mov	x19, x1
.Ltmp295:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp296:
	.loc	2 725 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:725:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 722 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:722:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 725 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:725:5
	ldr	x9, [x0, #24]
	.loc	2 723 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:723:18
	str	x8, [sp, #8]
	.loc	2 725 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:725:5
	ldr	x0, [x9]
	.loc	2 720 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:720:17
	stur	xzr, [x29, #-16]
	.loc	2 721 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:721:17
	str	xzr, [sp, #24]
	.loc	2 725 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:725:5
	ldr	x8, [x0]
	blr	x8
.Ltmp297:
	.loc	2 726 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:726:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp298:
	.loc	2 729 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:729:5
	ldr	x8, [sp, #16]
	movi	d1, #0000000000000000
	ldr	d0, [x8]
	adrp	x8, .LCPI28_0
	fabs	d2, d0
	ldr	d0, [x8, :lo12:.LCPI28_0]
	fcmp	d2, d0
	b.le	.LBB28_2
.Ltmp299:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ctx <- $x20
	ldr	x8, [sp, #8]
	movi	d2, #0000000000000000
	ldr	d1, [x8]
	fabs	d1, d1
	fcmp	d1, d0
	fmov	d0, #1.00000000
	fcsel	d1, d0, d2, gt
.Ltmp300:
.LBB28_2:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ctx <- $x20
	ldr	x8, [x19]
	str	d1, [x8]
	.loc	2 730 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:730:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB28_4
.Ltmp301:
// %bb.3:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 730 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:730:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp302:
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp303:
.LBB28_4:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_and_func:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp304:
.Lfunc_end28:
	.size	prjm_eval_func_boolean_and_func, .Lfunc_end28-prjm_eval_func_boolean_and_func
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_boolean_or_func
.LCPI29_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_boolean_or_func,"ax",@progbits
	.hidden	prjm_eval_func_boolean_or_func
	.globl	prjm_eval_func_boolean_or_func
	.p2align	2
	.type	prjm_eval_func_boolean_or_func,@function
prjm_eval_func_boolean_or_func:         // @prjm_eval_func_boolean_or_func
.Lfunc_begin29:
	.loc	2 733 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:733:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp305:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ctx <- $x20
	mov	x19, x1
.Ltmp306:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp307:
	.loc	2 741 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:741:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 738 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:738:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 741 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:741:5
	ldr	x9, [x0, #24]
	.loc	2 739 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:739:18
	str	x8, [sp, #8]
	.loc	2 741 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:741:5
	ldr	x0, [x9]
	.loc	2 736 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:736:17
	stur	xzr, [x29, #-16]
	.loc	2 737 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:737:17
	str	xzr, [sp, #24]
	.loc	2 741 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:741:5
	ldr	x8, [x0]
	blr	x8
.Ltmp308:
	.loc	2 742 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:742:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp309:
	.loc	2 745 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:745:5
	ldr	x8, [sp, #16]
	ldr	d0, [x8]
	adrp	x8, .LCPI29_0
	fabs	d1, d0
	ldr	d0, [x8, :lo12:.LCPI29_0]
	fcmp	d1, d0
	fmov	d1, #1.00000000
	b.gt	.LBB29_2
.Ltmp310:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ctx <- $x20
	ldr	x8, [sp, #8]
	movi	d2, #0000000000000000
	ldr	d1, [x8]
	fabs	d1, d1
	fcmp	d1, d0
	fmov	d0, #1.00000000
	fcsel	d1, d0, d2, gt
.Ltmp311:
.LBB29_2:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ctx <- $x20
	ldr	x8, [x19]
	str	d1, [x8]
	.loc	2 746 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:746:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB29_4
.Ltmp312:
// %bb.3:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 746 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:746:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp313:
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp314:
.LBB29_4:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_boolean_or_func:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp315:
.Lfunc_end29:
	.size	prjm_eval_func_boolean_or_func, .Lfunc_end29-prjm_eval_func_boolean_or_func
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_neg,"ax",@progbits
	.hidden	prjm_eval_func_neg              // -- Begin function prjm_eval_func_neg
	.globl	prjm_eval_func_neg
	.p2align	2
	.type	prjm_eval_func_neg,@function
prjm_eval_func_neg:                     // @prjm_eval_func_neg
.Lfunc_begin30:
	.loc	2 749 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:749:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_neg:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_neg:ret_val <- $x1
	sub	sp, sp, #64
	.cfi_def_cfa_offset 64
	stp	x29, x30, [sp, #32]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #48]             // 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp316:
	//DEBUG_VALUE: prjm_eval_func_neg:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_neg:ret_val <- $x19
	.loc	2 755 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:755:5
	add	x1, sp, #8
	ldr	x8, [x20, #40]
	stur	x8, [x29, #-8]
	add	x8, sp, #16
	ldr	x9, [x0, #24]
	.loc	2 753 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:753:18
	stp	x8, xzr, [sp, #8]
	.loc	2 755 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:755:5
	ldr	x0, [x9]
.Ltmp317:
	//DEBUG_VALUE: prjm_eval_func_neg:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	ldr	x8, [x0]
	blr	x8
.Ltmp318:
	.loc	2 757 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:757:5
	ldr	x8, [sp, #8]
	ldr	d0, [x8]
	ldr	x8, [x19]
	fneg	d0, d0
	str	d0, [x8]
	.loc	2 758 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:758:1
	ldr	x8, [x20, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB30_2
.Ltmp319:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_neg:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_neg:ret_val <- $x19
	.cfi_def_cfa wsp, 64
	.loc	2 758 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:758:1
	ldp	x20, x19, [sp, #48]             // 16-byte Folded Reload
.Ltmp320:
	//DEBUG_VALUE: prjm_eval_func_neg:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #32]             // 16-byte Folded Reload
	add	sp, sp, #64
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp321:
.LBB30_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_neg:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_neg:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp322:
.Lfunc_end30:
	.size	prjm_eval_func_neg, .Lfunc_end30-prjm_eval_func_neg
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_add_op,"ax",@progbits
	.hidden	prjm_eval_func_add_op           // -- Begin function prjm_eval_func_add_op
	.globl	prjm_eval_func_add_op
	.p2align	2
	.type	prjm_eval_func_add_op,@function
prjm_eval_func_add_op:                  // @prjm_eval_func_add_op
.Lfunc_begin31:
	.loc	2 761 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:761:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_add_op:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_add_op:ret_val <- $x1
	sub	sp, sp, #80
	.cfi_def_cfa_offset 80
	stp	x29, x30, [sp, #32]             // 16-byte Folded Spill
	str	x21, [sp, #48]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #64]             // 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp323:
	//DEBUG_VALUE: prjm_eval_func_add_op:ctx <- $x20
	mov	x19, x1
.Ltmp324:
	//DEBUG_VALUE: prjm_eval_func_add_op:ret_val <- $x19
	ldr	x8, [x21, #40]
	stur	x8, [x29, #-8]
	add	x8, sp, #16
.Ltmp325:
	.loc	2 767 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:767:5
	ldr	x9, [x0, #24]
	.loc	2 765 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:765:18
	stp	x8, xzr, [sp, #8]
	.loc	2 767 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:767:5
	ldr	x0, [x9]
	ldr	x8, [x0]
	blr	x8
.Ltmp326:
	.loc	2 768 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:768:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp327:
	.loc	2 770 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:770:5
	ldr	x8, [x19]
	ldr	x9, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	fadd	d0, d1, d0
	str	d0, [x8]
	.loc	2 771 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:771:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB31_2
.Ltmp328:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_add_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_add_op:ctx <- $x20
	.cfi_def_cfa wsp, 80
	.loc	2 771 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:771:1
	ldp	x20, x19, [sp, #64]             // 16-byte Folded Reload
.Ltmp329:
	//DEBUG_VALUE: prjm_eval_func_add_op:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_add_op:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #48]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #32]             // 16-byte Folded Reload
	add	sp, sp, #80
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp330:
.LBB31_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_add_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_add_op:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp331:
.Lfunc_end31:
	.size	prjm_eval_func_add_op, .Lfunc_end31-prjm_eval_func_add_op
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_sub_op,"ax",@progbits
	.hidden	prjm_eval_func_sub_op           // -- Begin function prjm_eval_func_sub_op
	.globl	prjm_eval_func_sub_op
	.p2align	2
	.type	prjm_eval_func_sub_op,@function
prjm_eval_func_sub_op:                  // @prjm_eval_func_sub_op
.Lfunc_begin32:
	.loc	2 774 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:774:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_sub_op:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_sub_op:ret_val <- $x1
	sub	sp, sp, #80
	.cfi_def_cfa_offset 80
	stp	x29, x30, [sp, #32]             // 16-byte Folded Spill
	str	x21, [sp, #48]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #64]             // 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp332:
	//DEBUG_VALUE: prjm_eval_func_sub_op:ctx <- $x20
	mov	x19, x1
.Ltmp333:
	//DEBUG_VALUE: prjm_eval_func_sub_op:ret_val <- $x19
	ldr	x8, [x21, #40]
	stur	x8, [x29, #-8]
	add	x8, sp, #16
.Ltmp334:
	.loc	2 780 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:780:5
	ldr	x9, [x0, #24]
	.loc	2 778 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:778:18
	stp	x8, xzr, [sp, #8]
	.loc	2 780 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:780:5
	ldr	x0, [x9]
	ldr	x8, [x0]
	blr	x8
.Ltmp335:
	.loc	2 781 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:781:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp336:
	.loc	2 783 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:783:5
	ldr	x8, [x19]
	ldr	x9, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	fsub	d0, d0, d1
	str	d0, [x8]
	.loc	2 784 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:784:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB32_2
.Ltmp337:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_sub_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_sub_op:ctx <- $x20
	.cfi_def_cfa wsp, 80
	.loc	2 784 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:784:1
	ldp	x20, x19, [sp, #64]             // 16-byte Folded Reload
.Ltmp338:
	//DEBUG_VALUE: prjm_eval_func_sub_op:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_sub_op:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #48]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #32]             // 16-byte Folded Reload
	add	sp, sp, #80
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp339:
.LBB32_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_sub_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_sub_op:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp340:
.Lfunc_end32:
	.size	prjm_eval_func_sub_op, .Lfunc_end32-prjm_eval_func_sub_op
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_mul_op,"ax",@progbits
	.hidden	prjm_eval_func_mul_op           // -- Begin function prjm_eval_func_mul_op
	.globl	prjm_eval_func_mul_op
	.p2align	2
	.type	prjm_eval_func_mul_op,@function
prjm_eval_func_mul_op:                  // @prjm_eval_func_mul_op
.Lfunc_begin33:
	.loc	2 787 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:787:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_mul_op:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_mul_op:ret_val <- $x1
	sub	sp, sp, #80
	.cfi_def_cfa_offset 80
	stp	x29, x30, [sp, #32]             // 16-byte Folded Spill
	str	x21, [sp, #48]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #64]             // 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp341:
	//DEBUG_VALUE: prjm_eval_func_mul_op:ctx <- $x20
	mov	x19, x1
.Ltmp342:
	//DEBUG_VALUE: prjm_eval_func_mul_op:ret_val <- $x19
	ldr	x8, [x21, #40]
	stur	x8, [x29, #-8]
	add	x8, sp, #16
.Ltmp343:
	.loc	2 793 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:793:5
	ldr	x9, [x0, #24]
	.loc	2 791 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:791:18
	stp	x8, xzr, [sp, #8]
	.loc	2 793 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:793:5
	ldr	x0, [x9]
	ldr	x8, [x0]
	blr	x8
.Ltmp344:
	.loc	2 794 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:794:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp345:
	.loc	2 796 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:796:5
	ldr	x8, [x19]
	ldr	x9, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	fmul	d0, d1, d0
	str	d0, [x8]
	.loc	2 797 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:797:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB33_2
.Ltmp346:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_mul_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mul_op:ctx <- $x20
	.cfi_def_cfa wsp, 80
	.loc	2 797 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:797:1
	ldp	x20, x19, [sp, #64]             // 16-byte Folded Reload
.Ltmp347:
	//DEBUG_VALUE: prjm_eval_func_mul_op:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_mul_op:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #48]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #32]             // 16-byte Folded Reload
	add	sp, sp, #80
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp348:
.LBB33_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_mul_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mul_op:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp349:
.Lfunc_end33:
	.size	prjm_eval_func_mul_op, .Lfunc_end33-prjm_eval_func_mul_op
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_div_op
.LCPI34_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_div_op,"ax",@progbits
	.hidden	prjm_eval_func_div_op
	.globl	prjm_eval_func_div_op
	.p2align	2
	.type	prjm_eval_func_div_op,@function
prjm_eval_func_div_op:                  // @prjm_eval_func_div_op
.Lfunc_begin34:
	.loc	2 800 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:800:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_div_op:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_div_op:ret_val <- $x1
	sub	sp, sp, #80
	.cfi_def_cfa_offset 80
	stp	x29, x30, [sp, #32]             // 16-byte Folded Spill
	str	x21, [sp, #48]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #64]             // 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp350:
	//DEBUG_VALUE: prjm_eval_func_div_op:ctx <- $x20
	mov	x19, x1
.Ltmp351:
	//DEBUG_VALUE: prjm_eval_func_div_op:ret_val <- $x19
	ldr	x8, [x21, #40]
	stur	x8, [x29, #-8]
	add	x8, sp, #16
.Ltmp352:
	.loc	2 806 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:806:5
	ldr	x9, [x0, #24]
	.loc	2 804 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:804:18
	stp	x8, xzr, [sp, #8]
	.loc	2 806 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:806:5
	ldr	x0, [x9]
	ldr	x8, [x0]
	blr	x8
.Ltmp353:
	.loc	2 807 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:807:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp354:
	.loc	2 809 14                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:809:14
	ldr	x8, [sp, #8]
	movi	d1, #0000000000000000
	.loc	2 809 13 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:809:13
	ldr	d0, [x8]
	adrp	x8, .LCPI34_0
	ldr	d3, [x8, :lo12:.LCPI34_0]
.Ltmp355:
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	ldr	x8, [x19]
.Ltmp356:
	.loc	2 809 8                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:809:8
	fabs	d2, d0
.Ltmp357:
	.loc	2 809 8                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:809:8
	fcmp	d2, d3
	b.lt	.LBB34_2
.Ltmp358:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_div_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_div_op:ctx <- $x20
	.loc	2 815 5 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:815:5
	ldr	d1, [x8]
	fdiv	d1, d1, d0
.Ltmp359:
.LBB34_2:
	//DEBUG_VALUE: prjm_eval_func_div_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_div_op:ctx <- $x20
	.loc	2 0 0 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	str	d1, [x8]
	.loc	2 816 1 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:816:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB34_4
.Ltmp360:
// %bb.3:
	//DEBUG_VALUE: prjm_eval_func_div_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_div_op:ctx <- $x20
	.cfi_def_cfa wsp, 80
	.loc	2 816 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:816:1
	ldp	x20, x19, [sp, #64]             // 16-byte Folded Reload
.Ltmp361:
	//DEBUG_VALUE: prjm_eval_func_div_op:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_div_op:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #48]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #32]             // 16-byte Folded Reload
	add	sp, sp, #80
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp362:
.LBB34_4:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_div_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_div_op:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp363:
.Lfunc_end34:
	.size	prjm_eval_func_div_op, .Lfunc_end34-prjm_eval_func_div_op
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_bitwise_or_op,"ax",@progbits
	.hidden	prjm_eval_func_bitwise_or_op    // -- Begin function prjm_eval_func_bitwise_or_op
	.globl	prjm_eval_func_bitwise_or_op
	.p2align	2
	.type	prjm_eval_func_bitwise_or_op,@function
prjm_eval_func_bitwise_or_op:           // @prjm_eval_func_bitwise_or_op
.Lfunc_begin35:
	.loc	2 819 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:819:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_bitwise_or_op:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_bitwise_or_op:ret_val <- $x1
	sub	sp, sp, #80
	.cfi_def_cfa_offset 80
	stp	x29, x30, [sp, #32]             // 16-byte Folded Spill
	str	x21, [sp, #48]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #64]             // 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp364:
	//DEBUG_VALUE: prjm_eval_func_bitwise_or_op:ctx <- $x20
	mov	x19, x1
.Ltmp365:
	//DEBUG_VALUE: prjm_eval_func_bitwise_or_op:ret_val <- $x19
	ldr	x8, [x21, #40]
	stur	x8, [x29, #-8]
	add	x8, sp, #16
.Ltmp366:
	.loc	2 825 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:825:5
	ldr	x9, [x0, #24]
	.loc	2 823 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:823:18
	stp	x8, xzr, [sp, #8]
	.loc	2 825 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:825:5
	ldr	x0, [x9]
	ldr	x8, [x0]
	blr	x8
.Ltmp367:
	.loc	2 826 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:826:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp368:
	.loc	2 828 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:828:5
	ldr	x8, [x19]
	ldr	x9, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	fcvtzs	x9, d0
	fcvtzs	x10, d1
	orr	x9, x10, x9
	scvtf	d0, x9
	str	d0, [x8]
	.loc	2 829 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:829:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB35_2
.Ltmp369:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_bitwise_or_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_bitwise_or_op:ctx <- $x20
	.cfi_def_cfa wsp, 80
	.loc	2 829 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:829:1
	ldp	x20, x19, [sp, #64]             // 16-byte Folded Reload
.Ltmp370:
	//DEBUG_VALUE: prjm_eval_func_bitwise_or_op:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_bitwise_or_op:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #48]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #32]             // 16-byte Folded Reload
	add	sp, sp, #80
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp371:
.LBB35_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_bitwise_or_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_bitwise_or_op:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp372:
.Lfunc_end35:
	.size	prjm_eval_func_bitwise_or_op, .Lfunc_end35-prjm_eval_func_bitwise_or_op
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_bitwise_or,"ax",@progbits
	.hidden	prjm_eval_func_bitwise_or       // -- Begin function prjm_eval_func_bitwise_or
	.globl	prjm_eval_func_bitwise_or
	.p2align	2
	.type	prjm_eval_func_bitwise_or,@function
prjm_eval_func_bitwise_or:              // @prjm_eval_func_bitwise_or
.Lfunc_begin36:
	.loc	2 832 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:832:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_bitwise_or:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_bitwise_or:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp373:
	//DEBUG_VALUE: prjm_eval_func_bitwise_or:ctx <- $x20
	mov	x19, x1
.Ltmp374:
	//DEBUG_VALUE: prjm_eval_func_bitwise_or:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_bitwise_or:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp375:
	.loc	2 840 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:840:5
	add	x1, sp, #24
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 836 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:836:18
	str	x8, [sp, #24]
	add	x8, sp, #16
	.loc	2 840 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:840:5
	ldr	x9, [x0, #24]
	.loc	2 838 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:838:18
	str	x8, [sp, #8]
	.loc	2 840 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:840:5
	ldr	x0, [x9]
	.loc	2 835 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:835:17
	stur	xzr, [x29, #-16]
	.loc	2 837 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:837:17
	str	xzr, [sp, #16]
	.loc	2 840 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:840:5
	ldr	x8, [x0]
	blr	x8
.Ltmp376:
	.loc	2 841 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:841:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp377:
	.loc	2 843 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:843:5
	ldr	x8, [sp, #24]
	ldr	x9, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	fcvtzs	x8, d0
	fcvtzs	x9, d1
	orr	x8, x9, x8
	scvtf	d0, x8
	ldr	x8, [x19]
	str	d0, [x8]
	.loc	2 844 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:844:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB36_2
.Ltmp378:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_bitwise_or:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_bitwise_or:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 844 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:844:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp379:
	//DEBUG_VALUE: prjm_eval_func_bitwise_or:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_bitwise_or:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp380:
.LBB36_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_bitwise_or:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_bitwise_or:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp381:
.Lfunc_end36:
	.size	prjm_eval_func_bitwise_or, .Lfunc_end36-prjm_eval_func_bitwise_or
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_bitwise_and_op,"ax",@progbits
	.hidden	prjm_eval_func_bitwise_and_op   // -- Begin function prjm_eval_func_bitwise_and_op
	.globl	prjm_eval_func_bitwise_and_op
	.p2align	2
	.type	prjm_eval_func_bitwise_and_op,@function
prjm_eval_func_bitwise_and_op:          // @prjm_eval_func_bitwise_and_op
.Lfunc_begin37:
	.loc	2 847 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:847:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_bitwise_and_op:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_bitwise_and_op:ret_val <- $x1
	sub	sp, sp, #80
	.cfi_def_cfa_offset 80
	stp	x29, x30, [sp, #32]             // 16-byte Folded Spill
	str	x21, [sp, #48]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #64]             // 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp382:
	//DEBUG_VALUE: prjm_eval_func_bitwise_and_op:ctx <- $x20
	mov	x19, x1
.Ltmp383:
	//DEBUG_VALUE: prjm_eval_func_bitwise_and_op:ret_val <- $x19
	ldr	x8, [x21, #40]
	stur	x8, [x29, #-8]
	add	x8, sp, #16
.Ltmp384:
	.loc	2 853 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:853:5
	ldr	x9, [x0, #24]
	.loc	2 851 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:851:18
	stp	x8, xzr, [sp, #8]
	.loc	2 853 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:853:5
	ldr	x0, [x9]
	ldr	x8, [x0]
	blr	x8
.Ltmp385:
	.loc	2 854 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:854:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp386:
	.loc	2 856 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:856:5
	ldr	x8, [x19]
	ldr	x9, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	fcvtzs	x9, d0
	fcvtzs	x10, d1
	and	x9, x10, x9
	scvtf	d0, x9
	str	d0, [x8]
	.loc	2 857 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:857:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB37_2
.Ltmp387:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_bitwise_and_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_bitwise_and_op:ctx <- $x20
	.cfi_def_cfa wsp, 80
	.loc	2 857 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:857:1
	ldp	x20, x19, [sp, #64]             // 16-byte Folded Reload
.Ltmp388:
	//DEBUG_VALUE: prjm_eval_func_bitwise_and_op:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_bitwise_and_op:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #48]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #32]             // 16-byte Folded Reload
	add	sp, sp, #80
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp389:
.LBB37_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_bitwise_and_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_bitwise_and_op:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp390:
.Lfunc_end37:
	.size	prjm_eval_func_bitwise_and_op, .Lfunc_end37-prjm_eval_func_bitwise_and_op
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_bitwise_and,"ax",@progbits
	.hidden	prjm_eval_func_bitwise_and      // -- Begin function prjm_eval_func_bitwise_and
	.globl	prjm_eval_func_bitwise_and
	.p2align	2
	.type	prjm_eval_func_bitwise_and,@function
prjm_eval_func_bitwise_and:             // @prjm_eval_func_bitwise_and
.Lfunc_begin38:
	.loc	2 860 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:860:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_bitwise_and:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_bitwise_and:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp391:
	//DEBUG_VALUE: prjm_eval_func_bitwise_and:ctx <- $x20
	mov	x19, x1
.Ltmp392:
	//DEBUG_VALUE: prjm_eval_func_bitwise_and:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_bitwise_and:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp393:
	.loc	2 868 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:868:5
	add	x1, sp, #24
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 864 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:864:18
	str	x8, [sp, #24]
	add	x8, sp, #16
	.loc	2 868 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:868:5
	ldr	x9, [x0, #24]
	.loc	2 866 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:866:18
	str	x8, [sp, #8]
	.loc	2 868 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:868:5
	ldr	x0, [x9]
	.loc	2 863 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:863:17
	stur	xzr, [x29, #-16]
	.loc	2 865 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:865:17
	str	xzr, [sp, #16]
	.loc	2 868 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:868:5
	ldr	x8, [x0]
	blr	x8
.Ltmp394:
	.loc	2 869 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:869:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp395:
	.loc	2 871 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:871:5
	ldr	x8, [sp, #24]
	ldr	x9, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	fcvtzs	x8, d0
	fcvtzs	x9, d1
	and	x8, x9, x8
	scvtf	d0, x8
	ldr	x8, [x19]
	str	d0, [x8]
	.loc	2 872 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:872:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB38_2
.Ltmp396:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_bitwise_and:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_bitwise_and:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 872 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:872:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp397:
	//DEBUG_VALUE: prjm_eval_func_bitwise_and:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_bitwise_and:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp398:
.LBB38_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_bitwise_and:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_bitwise_and:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp399:
.Lfunc_end38:
	.size	prjm_eval_func_bitwise_and, .Lfunc_end38-prjm_eval_func_bitwise_and
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_mod_op,"ax",@progbits
	.hidden	prjm_eval_func_mod_op           // -- Begin function prjm_eval_func_mod_op
	.globl	prjm_eval_func_mod_op
	.p2align	2
	.type	prjm_eval_func_mod_op,@function
prjm_eval_func_mod_op:                  // @prjm_eval_func_mod_op
.Lfunc_begin39:
	.loc	2 875 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:875:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x1
	sub	sp, sp, #80
	.cfi_def_cfa_offset 80
	stp	x29, x30, [sp, #32]             // 16-byte Folded Spill
	str	x21, [sp, #48]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #64]             // 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp400:
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	mov	x19, x1
.Ltmp401:
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	ldr	x8, [x21, #40]
	stur	x8, [x29, #-8]
	add	x8, sp, #16
.Ltmp402:
	.loc	2 881 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:881:5
	ldr	x9, [x0, #24]
	.loc	2 879 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:879:18
	stp	x8, xzr, [sp, #8]
	.loc	2 881 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:881:5
	ldr	x0, [x9]
	ldr	x8, [x0]
	blr	x8
.Ltmp403:
	.loc	2 882 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:882:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp404:
	.loc	2 884 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:884:5
	ldr	x8, [x19]
	movi	d0, #0000000000000000
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorBits <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:numerator <- $d1
	mov	x10, #4890909195324358656       // =0x43e0000000000000
	ldr	d1, [x8]
.Ltmp405:
	//DEBUG_VALUE: memcpy:copy_amount <- 8
	//DEBUG_VALUE: memcpy: <- 8
	//DEBUG_VALUE: remainder_value_bits:value <- $d1
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- undef
	fmov	x11, d1
.Ltmp406:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- undef
	//DEBUG_VALUE: remainder_value_bits:bits <- undef
	//DEBUG_VALUE: memcpy:copy_amount <- 8
	//DEBUG_VALUE: memcpy: <- 8
	//DEBUG_VALUE: remainder_value_bits:value <- undef
	//DEBUG_VALUE: remainder_value_bits:bits <- $x11
	.loc	2 622 63                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:622:63
	and	x9, x11, #0x7fffffffffffffff
.Ltmp407:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- undef
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x9
	.loc	2 624 55                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:624:55
	cmp	x9, x10
	b.hi	.LBB39_12
.Ltmp408:
// %bb.1:
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x9
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	.loc	2 884 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:884:5
	ldr	x10, [sp, #8]
	ldr	d2, [x10]
.Ltmp409:
	//DEBUG_VALUE: remainder_value_bits:value <- $d2
	fmov	x12, d2
.Ltmp410:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x12
	//DEBUG_VALUE: remainder_value_bits:bits <- $x12
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	.loc	2 0 0 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	and	x10, x12, #0x7fffffffffffffff
.Ltmp411:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x10
	.loc	2 624 55 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:624:55
	lsr	x13, x10, #52
	cmp	x13, #2046
	b.hi	.LBB39_12
.Ltmp412:
// %bb.2:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x12
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x9
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	.loc	2 0 55 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:55
	mov	x13, #4890909195324358656       // =0x43e0000000000000
.Ltmp413:
	.loc	2 629 58 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:629:58
	cmp	x9, x13
	b.ne	.LBB39_5
.Ltmp414:
// %bb.3:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x12
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x9
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	.loc	2 629 100 is_stmt 0             // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:629:100
	tbz	x11, #63, .LBB39_12
.Ltmp415:
// %bb.4:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x12
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x9
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	.loc	2 0 100                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:100
	mov	x11, #4890909195324358656       // =0x43e0000000000000
	.loc	2 629 100                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:629:100
	cmp	x10, x11
	b.ls	.LBB39_6
	b	.LBB39_12
.Ltmp416:
.LBB39_5:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x12
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x9
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	.loc	2 630 58 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:630:58
	cmp	x10, x13
	b.hi	.LBB39_12
.Ltmp417:
.LBB39_6:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x12
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x9
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	.loc	2 631 60                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:631:60
	tbnz	x12, #63, .LBB39_8
.Ltmp418:
// %bb.7:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x12
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x9
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	.loc	2 0 60 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:60
	mov	x11, #4890909195324358656       // =0x43e0000000000000
	.loc	2 631 60                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:631:60
	cmp	x10, x11
	b.eq	.LBB39_12
.Ltmp419:
.LBB39_8:
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x12
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x9
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	//DEBUG_VALUE: bounded_milkdrop_remainder:dividend <- undef
	.loc	2 634 33 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:634:33
	fcvtzs	x11, d2
.Ltmp420:
	//DEBUG_VALUE: bounded_milkdrop_remainder:minimum <- -9223372036854775808
	//DEBUG_VALUE: bounded_milkdrop_remainder:divisor <- $x11
	.loc	2 640 22                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:640:22
	cbz	x11, .LBB39_12
.Ltmp421:
// %bb.9:
	//DEBUG_VALUE: bounded_milkdrop_remainder:divisor <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:minimum <- -9223372036854775808
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorBits <- $x12
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x9
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	.loc	2 0 22 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:22
	fcvtzs	x12, d1
.Ltmp422:
	//DEBUG_VALUE: bounded_milkdrop_remainder:dividend <- $x12
	mov	x13, #-9223372036854775808      // =0x8000000000000000
	.loc	2 640 46                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:640:46
	cmp	x12, x13
	b.ne	.LBB39_11
.Ltmp423:
// %bb.10:
	//DEBUG_VALUE: bounded_milkdrop_remainder:dividend <- $x12
	//DEBUG_VALUE: bounded_milkdrop_remainder:divisor <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:minimum <- -9223372036854775808
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x9
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	cmn	x11, #1
	b.eq	.LBB39_12
.Ltmp424:
.LBB39_11:
	//DEBUG_VALUE: bounded_milkdrop_remainder:dividend <- $x12
	//DEBUG_VALUE: bounded_milkdrop_remainder:divisor <- $x11
	//DEBUG_VALUE: bounded_milkdrop_remainder:minimum <- -9223372036854775808
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominatorMagnitude <- $x10
	//DEBUG_VALUE: bounded_milkdrop_remainder:denominator <- $d2
	//DEBUG_VALUE: bounded_milkdrop_remainder:numeratorMagnitude <- $x9
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	.loc	2 642 59 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:642:59
	sdiv	x13, x12, x11
	lsr	x10, x10, #53
.Ltmp425:
	.loc	2 643 31                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:643:31
	lsr	x9, x9, #53
.Ltmp426:
	.loc	2 0 31 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:31
	cmp	x10, #527
	mov	w10, #527                       // =0x20f
	.loc	2 643 31                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:643:31
	ccmp	x9, x10, #2, lo
	.loc	2 642 59 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:642:59
	msub	x11, x13, x11, x12
.Ltmp427:
	.loc	2 642 35 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:642:35
	scvtf	d0, x11
.Ltmp428:
	//DEBUG_VALUE: bounded_milkdrop_remainder:remainder <- $d0
	.loc	2 643 63 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:643:63
	fabs	d1, d0
	fcsel	d0, d1, d0, lo
.Ltmp429:
.LBB39_12:
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	.loc	2 884 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:884:5
	str	d0, [x8]
	.loc	2 885 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:885:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB39_14
.Ltmp430:
// %bb.13:
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	.cfi_def_cfa wsp, 80
	.loc	2 885 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:885:1
	ldp	x20, x19, [sp, #64]             // 16-byte Folded Reload
.Ltmp431:
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #48]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #32]             // 16-byte Folded Reload
	add	sp, sp, #80
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp432:
.LBB39_14:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_mod_op:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_mod_op:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp433:
.Lfunc_end39:
	.size	prjm_eval_func_mod_op, .Lfunc_end39-prjm_eval_func_mod_op
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_pow_op
.LCPI40_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_pow_op,"ax",@progbits
	.hidden	prjm_eval_func_pow_op
	.globl	prjm_eval_func_pow_op
	.p2align	2
	.type	prjm_eval_func_pow_op,@function
prjm_eval_func_pow_op:                  // @prjm_eval_func_pow_op
.Lfunc_begin40:
	.loc	2 888 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:888:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_pow_op:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_pow_op:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	d9, d8, [sp, #32]               // 16-byte Folded Spill
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_offset b8, -56
	.cfi_offset b9, -64
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp434:
	//DEBUG_VALUE: prjm_eval_func_pow_op:ctx <- $x20
	mov	x19, x1
.Ltmp435:
	//DEBUG_VALUE: prjm_eval_func_pow_op:ret_val <- $x19
	ldr	x8, [x21, #40]
	str	x8, [sp, #24]
	add	x8, sp, #16
.Ltmp436:
	.loc	2 894 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:894:5
	ldr	x9, [x0, #24]
	.loc	2 892 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:892:18
	stp	x8, xzr, [sp, #8]
	.loc	2 894 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:894:5
	ldr	x0, [x9]
	ldr	x8, [x0]
	blr	x8
.Ltmp437:
	.loc	2 895 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:895:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp438:
	.loc	2 903 42                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:903:42
	ldr	x8, [sp, #8]
.Ltmp439:
	.loc	2 897 14                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:897:14
	ldr	x19, [x19]
.Ltmp440:
	//DEBUG_VALUE: prjm_eval_func_pow_op:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	.loc	2 903 41                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:903:41
	ldr	d8, [x8]
.Ltmp441:
	.loc	2 897 13                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:897:13
	ldr	d0, [x19]
	.loc	2 897 46 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:897:46
	fmov	d1, d8
	.loc	2 897 8                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:897:8
	fabs	d9, d0
	.loc	2 897 46                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:897:46
	bl	pow
.Ltmp442:
	.loc	2 0 46                          // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:46
	fcmp	d8, #0.0
	adrp	x8, .LCPI40_0
	movi	d2, #0000000000000000
	ldr	d1, [x8, :lo12:.LCPI40_0]
	.loc	2 897 24                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:897:24
	fccmp	d9, d1, #0, lt
	.loc	2 897 46                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:897:46
	fcsel	d0, d2, d0, lt
.Ltmp443:
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	str	d0, [x19]
	.loc	2 906 1 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:906:1
	ldr	x8, [x21, #40]
	ldr	x9, [sp, #24]
	cmp	x8, x9
	b.ne	.LBB40_2
.Ltmp444:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_pow_op:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	//DEBUG_VALUE: prjm_eval_func_pow_op:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 906 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:906:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp445:
	//DEBUG_VALUE: prjm_eval_func_pow_op:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	ldp	d9, d8, [sp, #32]               // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	.cfi_restore b8
	.cfi_restore b9
	ret
.Ltmp446:
.LBB40_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_pow_op:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	//DEBUG_VALUE: prjm_eval_func_pow_op:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp447:
.Lfunc_end40:
	.size	prjm_eval_func_pow_op, .Lfunc_end40-prjm_eval_func_pow_op
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_sin,"ax",@progbits
	.hidden	prjm_eval_func_sin              // -- Begin function prjm_eval_func_sin
	.globl	prjm_eval_func_sin
	.p2align	2
	.type	prjm_eval_func_sin,@function
prjm_eval_func_sin:                     // @prjm_eval_func_sin
.Lfunc_begin41:
	.loc	2 911 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:911:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_sin:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_sin:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp448:
	//DEBUG_VALUE: prjm_eval_func_sin:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_sin:ret_val <- $x19
	.loc	2 917 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:917:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 914 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:914:16
	str	xzr, [x0, #8]!
.Ltmp449:
	//DEBUG_VALUE: prjm_eval_func_sin:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 917 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:917:5
	ldr	x8, [x0, #16]
	.loc	2 915 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:915:18
	str	x0, [sp]
	.loc	2 917 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:917:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp450:
	.loc	2 919 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:919:5
	ldr	x8, [sp]
	ldr	d0, [x8]
	bl	sin
.Ltmp451:
	ldr	x8, [x19]
	str	d0, [x8]
	.loc	2 920 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:920:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB41_2
.Ltmp452:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_sin:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_sin:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 920 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:920:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp453:
	//DEBUG_VALUE: prjm_eval_func_sin:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp454:
.LBB41_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_sin:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_sin:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp455:
.Lfunc_end41:
	.size	prjm_eval_func_sin, .Lfunc_end41-prjm_eval_func_sin
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_cos,"ax",@progbits
	.hidden	prjm_eval_func_cos              // -- Begin function prjm_eval_func_cos
	.globl	prjm_eval_func_cos
	.p2align	2
	.type	prjm_eval_func_cos,@function
prjm_eval_func_cos:                     // @prjm_eval_func_cos
.Lfunc_begin42:
	.loc	2 923 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:923:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_cos:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_cos:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp456:
	//DEBUG_VALUE: prjm_eval_func_cos:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_cos:ret_val <- $x19
	.loc	2 929 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:929:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 926 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:926:16
	str	xzr, [x0, #8]!
.Ltmp457:
	//DEBUG_VALUE: prjm_eval_func_cos:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 929 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:929:5
	ldr	x8, [x0, #16]
	.loc	2 927 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:927:18
	str	x0, [sp]
	.loc	2 929 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:929:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp458:
	.loc	2 931 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:931:5
	ldr	x8, [sp]
	ldr	d0, [x8]
	bl	cos
.Ltmp459:
	ldr	x8, [x19]
	str	d0, [x8]
	.loc	2 932 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:932:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB42_2
.Ltmp460:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_cos:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_cos:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 932 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:932:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp461:
	//DEBUG_VALUE: prjm_eval_func_cos:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp462:
.LBB42_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_cos:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_cos:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp463:
.Lfunc_end42:
	.size	prjm_eval_func_cos, .Lfunc_end42-prjm_eval_func_cos
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_tan,"ax",@progbits
	.hidden	prjm_eval_func_tan              // -- Begin function prjm_eval_func_tan
	.globl	prjm_eval_func_tan
	.p2align	2
	.type	prjm_eval_func_tan,@function
prjm_eval_func_tan:                     // @prjm_eval_func_tan
.Lfunc_begin43:
	.loc	2 935 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:935:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_tan:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_tan:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp464:
	//DEBUG_VALUE: prjm_eval_func_tan:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_tan:ret_val <- $x19
	.loc	2 941 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:941:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 938 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:938:16
	str	xzr, [x0, #8]!
.Ltmp465:
	//DEBUG_VALUE: prjm_eval_func_tan:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 941 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:941:5
	ldr	x8, [x0, #16]
	.loc	2 939 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:939:18
	str	x0, [sp]
	.loc	2 941 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:941:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp466:
	.loc	2 943 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:943:5
	ldr	x8, [sp]
	ldr	d0, [x8]
	bl	tan
.Ltmp467:
	ldr	x8, [x19]
	str	d0, [x8]
	.loc	2 944 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:944:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB43_2
.Ltmp468:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_tan:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_tan:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 944 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:944:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp469:
	//DEBUG_VALUE: prjm_eval_func_tan:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp470:
.LBB43_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_tan:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_tan:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp471:
.Lfunc_end43:
	.size	prjm_eval_func_tan, .Lfunc_end43-prjm_eval_func_tan
	.cfi_endproc
	.file	6 "/Users/jneerdael" "Library/Android/sdk/ndk/27.3.13750724/toolchains/llvm/prebuilt/darwin-x86_64/sysroot/usr/include/math.h"
                                        // -- End function
	.section	.text.prjm_eval_func_asin,"ax",@progbits
	.hidden	prjm_eval_func_asin             // -- Begin function prjm_eval_func_asin
	.globl	prjm_eval_func_asin
	.p2align	2
	.type	prjm_eval_func_asin,@function
prjm_eval_func_asin:                    // @prjm_eval_func_asin
.Lfunc_begin44:
	.loc	2 947 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:947:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_asin:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_asin:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp472:
	//DEBUG_VALUE: prjm_eval_func_asin:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_asin:ret_val <- $x19
	.loc	2 953 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:953:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 950 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:950:16
	str	xzr, [x0, #8]!
.Ltmp473:
	//DEBUG_VALUE: prjm_eval_func_asin:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 953 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:953:5
	ldr	x8, [x0, #16]
	.loc	2 951 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:951:18
	str	x0, [sp]
	.loc	2 953 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:953:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp474:
	.loc	2 955 10                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:955:10
	ldr	x8, [sp]
	fmov	d0, #-1.00000000
	fmov	d2, #1.00000000
	.loc	2 955 9 is_stmt 0               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:955:9
	ldr	d1, [x8]
	.loc	2 955 30                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:955:30
	fcmp	d1, d0
	movi	d0, #0000000000000000
	fccmp	d1, d2, #0, ge
	b.gt	.LBB44_2
.Ltmp475:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_asin:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_asin:ret_val <- $x19
	.loc	2 961 5 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:961:5
	fmov	d0, d1
	bl	asin
.Ltmp476:
.LBB44_2:
	//DEBUG_VALUE: prjm_eval_func_asin:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_asin:ret_val <- $x19
	.loc	2 0 0 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	ldr	x8, [x19]
	str	d0, [x8]
	.loc	2 962 1 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:962:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB44_4
.Ltmp477:
// %bb.3:
	//DEBUG_VALUE: prjm_eval_func_asin:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_asin:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 962 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:962:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp478:
	//DEBUG_VALUE: prjm_eval_func_asin:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp479:
.LBB44_4:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_asin:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_asin:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp480:
.Lfunc_end44:
	.size	prjm_eval_func_asin, .Lfunc_end44-prjm_eval_func_asin
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_acos,"ax",@progbits
	.hidden	prjm_eval_func_acos             // -- Begin function prjm_eval_func_acos
	.globl	prjm_eval_func_acos
	.p2align	2
	.type	prjm_eval_func_acos,@function
prjm_eval_func_acos:                    // @prjm_eval_func_acos
.Lfunc_begin45:
	.loc	2 965 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:965:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_acos:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_acos:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp481:
	//DEBUG_VALUE: prjm_eval_func_acos:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_acos:ret_val <- $x19
	.loc	2 971 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:971:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 968 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:968:16
	str	xzr, [x0, #8]!
.Ltmp482:
	//DEBUG_VALUE: prjm_eval_func_acos:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 971 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:971:5
	ldr	x8, [x0, #16]
	.loc	2 969 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:969:18
	str	x0, [sp]
	.loc	2 971 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:971:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp483:
	.loc	2 973 10                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:973:10
	ldr	x8, [sp]
	fmov	d0, #-1.00000000
	fmov	d2, #1.00000000
	.loc	2 973 9 is_stmt 0               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:973:9
	ldr	d1, [x8]
	.loc	2 973 30                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:973:30
	fcmp	d1, d0
	movi	d0, #0000000000000000
	fccmp	d1, d2, #0, ge
	b.gt	.LBB45_2
.Ltmp484:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_acos:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_acos:ret_val <- $x19
	.loc	2 979 5 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:979:5
	fmov	d0, d1
	bl	acos
.Ltmp485:
.LBB45_2:
	//DEBUG_VALUE: prjm_eval_func_acos:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_acos:ret_val <- $x19
	.loc	2 0 0 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	ldr	x8, [x19]
	str	d0, [x8]
	.loc	2 980 1 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:980:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB45_4
.Ltmp486:
// %bb.3:
	//DEBUG_VALUE: prjm_eval_func_acos:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_acos:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 980 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:980:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp487:
	//DEBUG_VALUE: prjm_eval_func_acos:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp488:
.LBB45_4:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_acos:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_acos:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp489:
.Lfunc_end45:
	.size	prjm_eval_func_acos, .Lfunc_end45-prjm_eval_func_acos
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_atan,"ax",@progbits
	.hidden	prjm_eval_func_atan             // -- Begin function prjm_eval_func_atan
	.globl	prjm_eval_func_atan
	.p2align	2
	.type	prjm_eval_func_atan,@function
prjm_eval_func_atan:                    // @prjm_eval_func_atan
.Lfunc_begin46:
	.loc	2 983 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:983:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_atan:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_atan:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp490:
	//DEBUG_VALUE: prjm_eval_func_atan:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_atan:ret_val <- $x19
	.loc	2 989 5 prologue_end            // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:989:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 986 16                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:986:16
	str	xzr, [x0, #8]!
.Ltmp491:
	//DEBUG_VALUE: prjm_eval_func_atan:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 989 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:989:5
	ldr	x8, [x0, #16]
	.loc	2 987 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:987:18
	str	x0, [sp]
	.loc	2 989 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:989:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp492:
	.loc	2 991 5                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:991:5
	ldr	x8, [sp]
	ldr	d0, [x8]
	bl	atan
.Ltmp493:
	ldr	x8, [x19]
	str	d0, [x8]
	.loc	2 992 1                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:992:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB46_2
.Ltmp494:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_atan:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_atan:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 992 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:992:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp495:
	//DEBUG_VALUE: prjm_eval_func_atan:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp496:
.LBB46_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_atan:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_atan:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp497:
.Lfunc_end46:
	.size	prjm_eval_func_atan, .Lfunc_end46-prjm_eval_func_atan
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_atan2,"ax",@progbits
	.hidden	prjm_eval_func_atan2            // -- Begin function prjm_eval_func_atan2
	.globl	prjm_eval_func_atan2
	.p2align	2
	.type	prjm_eval_func_atan2,@function
prjm_eval_func_atan2:                   // @prjm_eval_func_atan2
.Lfunc_begin47:
	.loc	2 995 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:995:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_atan2:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_atan2:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp498:
	//DEBUG_VALUE: prjm_eval_func_atan2:ctx <- $x20
	mov	x19, x1
.Ltmp499:
	//DEBUG_VALUE: prjm_eval_func_atan2:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_atan2:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp500:
	.loc	2 1003 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1003:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 1000 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1000:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 1003 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1003:5
	ldr	x9, [x0, #24]
	.loc	2 1001 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1001:18
	str	x8, [sp, #8]
	.loc	2 1003 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1003:5
	ldr	x0, [x9]
	.loc	2 998 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:998:17
	stur	xzr, [x29, #-16]
	.loc	2 999 17                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:999:17
	str	xzr, [sp, #24]
	.loc	2 1003 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1003:5
	ldr	x8, [x0]
	blr	x8
.Ltmp501:
	.loc	2 1004 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1004:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp502:
	.loc	2 1006 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1006:5
	ldp	x9, x8, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	bl	atan2
.Ltmp503:
	ldr	x8, [x19]
	str	d0, [x8]
	.loc	2 1007 1                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1007:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB47_2
.Ltmp504:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_atan2:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_atan2:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 1007 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1007:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp505:
	//DEBUG_VALUE: prjm_eval_func_atan2:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_atan2:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp506:
.LBB47_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_atan2:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_atan2:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp507:
.Lfunc_end47:
	.size	prjm_eval_func_atan2, .Lfunc_end47-prjm_eval_func_atan2
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_sqrt,"ax",@progbits
	.hidden	prjm_eval_func_sqrt             // -- Begin function prjm_eval_func_sqrt
	.globl	prjm_eval_func_sqrt
	.p2align	2
	.type	prjm_eval_func_sqrt,@function
prjm_eval_func_sqrt:                    // @prjm_eval_func_sqrt
.Lfunc_begin48:
	.loc	2 1010 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1010:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_sqrt:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_sqrt:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp508:
	//DEBUG_VALUE: prjm_eval_func_sqrt:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_sqrt:ret_val <- $x19
	.loc	2 1016 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1016:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 1013 16                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1013:16
	str	xzr, [x0, #8]!
.Ltmp509:
	//DEBUG_VALUE: prjm_eval_func_sqrt:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 1016 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1016:5
	ldr	x8, [x0, #16]
	.loc	2 1014 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1014:18
	str	x0, [sp]
	.loc	2 1016 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1016:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp510:
	.loc	2 1018 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1018:5
	ldr	x8, [sp]
	ldr	d0, [x8]
	ldr	x8, [x19]
	fabs	d0, d0
	fsqrt	d0, d0
	str	d0, [x8]
	.loc	2 1019 1                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1019:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB48_2
.Ltmp511:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_sqrt:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_sqrt:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 1019 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1019:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp512:
	//DEBUG_VALUE: prjm_eval_func_sqrt:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp513:
.LBB48_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_sqrt:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_sqrt:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp514:
.Lfunc_end48:
	.size	prjm_eval_func_sqrt, .Lfunc_end48-prjm_eval_func_sqrt
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_pow
.LCPI49_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_pow,"ax",@progbits
	.hidden	prjm_eval_func_pow
	.globl	prjm_eval_func_pow
	.p2align	2
	.type	prjm_eval_func_pow,@function
prjm_eval_func_pow:                     // @prjm_eval_func_pow
.Lfunc_begin49:
	.loc	2 1022 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1022:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_pow:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_pow:ret_val <- $x1
	sub	sp, sp, #112
	.cfi_def_cfa_offset 112
	stp	d9, d8, [sp, #48]               // 16-byte Folded Spill
	stp	x29, x30, [sp, #64]             // 16-byte Folded Spill
	str	x21, [sp, #80]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #96]             // 16-byte Folded Spill
	add	x29, sp, #64
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_offset b8, -56
	.cfi_offset b9, -64
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp515:
	//DEBUG_VALUE: prjm_eval_func_pow:ctx <- $x20
	mov	x19, x1
.Ltmp516:
	//DEBUG_VALUE: prjm_eval_func_pow:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_pow:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp517:
	.loc	2 1030 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1030:5
	add	x1, sp, #16
	stur	x8, [x29, #-24]
	add	x8, sp, #32
	.loc	2 1027 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1027:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 1030 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1030:5
	ldr	x9, [x0, #24]
	.loc	2 1028 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1028:18
	str	x8, [sp, #8]
	.loc	2 1030 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1030:5
	ldr	x0, [x9]
	.loc	2 1025 17                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1025:17
	stp	xzr, xzr, [sp, #24]
	.loc	2 1030 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1030:5
	ldr	x8, [x0]
	blr	x8
.Ltmp518:
	.loc	2 1031 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1031:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp519:
	.loc	2 1033 15                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1033:15
	ldp	x8, x9, [sp, #8]
.Ltmp520:
	.loc	2 1039 46                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1039:46
	ldr	d8, [x8]
.Ltmp521:
	.loc	2 1033 14                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1033:14
	ldr	d0, [x9]
	.loc	2 1033 52 is_stmt 0             // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1033:52
	fmov	d1, d8
	.loc	2 1033 9                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1033:9
	fabs	d9, d0
	.loc	2 1033 52                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1033:52
	bl	pow
.Ltmp522:
	.loc	2 0 52                          // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:52
	fcmp	d8, #0.0
	adrp	x8, .LCPI49_0
	movi	d2, #0000000000000000
	ldr	d1, [x8, :lo12:.LCPI49_0]
.Ltmp523:
	ldr	x8, [x19]
.Ltmp524:
	.loc	2 1033 30                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1033:30
	fccmp	d9, d1, #0, lt
	.loc	2 1033 52                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1033:52
	fcsel	d0, d2, d0, lt
.Ltmp525:
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	str	d0, [x8]
	.loc	2 1042 1 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1042:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-24]
	cmp	x8, x9
	b.ne	.LBB49_2
.Ltmp526:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_pow:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_pow:ctx <- $x20
	.cfi_def_cfa wsp, 112
	.loc	2 1042 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1042:1
	ldp	x20, x19, [sp, #96]             // 16-byte Folded Reload
.Ltmp527:
	//DEBUG_VALUE: prjm_eval_func_pow:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_pow:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #80]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #64]             // 16-byte Folded Reload
	ldp	d9, d8, [sp, #48]               // 16-byte Folded Reload
	add	sp, sp, #112
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	.cfi_restore b8
	.cfi_restore b9
	ret
.Ltmp528:
.LBB49_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_pow:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_pow:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp529:
.Lfunc_end49:
	.size	prjm_eval_func_pow, .Lfunc_end49-prjm_eval_func_pow
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_exp,"ax",@progbits
	.hidden	prjm_eval_func_exp              // -- Begin function prjm_eval_func_exp
	.globl	prjm_eval_func_exp
	.p2align	2
	.type	prjm_eval_func_exp,@function
prjm_eval_func_exp:                     // @prjm_eval_func_exp
.Lfunc_begin50:
	.loc	2 1045 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1045:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_exp:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_exp:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp530:
	//DEBUG_VALUE: prjm_eval_func_exp:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_exp:ret_val <- $x19
	.loc	2 1051 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1051:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 1048 16                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1048:16
	str	xzr, [x0, #8]!
.Ltmp531:
	//DEBUG_VALUE: prjm_eval_func_exp:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 1051 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1051:5
	ldr	x8, [x0, #16]
	.loc	2 1049 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1049:18
	str	x0, [sp]
	.loc	2 1051 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1051:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp532:
	.loc	2 1053 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1053:5
	ldr	x8, [sp]
	ldr	d0, [x8]
	bl	exp
.Ltmp533:
	ldr	x8, [x19]
	str	d0, [x8]
	.loc	2 1054 1                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1054:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB50_2
.Ltmp534:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_exp:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_exp:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 1054 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1054:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp535:
	//DEBUG_VALUE: prjm_eval_func_exp:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp536:
.LBB50_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_exp:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_exp:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp537:
.Lfunc_end50:
	.size	prjm_eval_func_exp, .Lfunc_end50-prjm_eval_func_exp
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_log,"ax",@progbits
	.hidden	prjm_eval_func_log              // -- Begin function prjm_eval_func_log
	.globl	prjm_eval_func_log
	.p2align	2
	.type	prjm_eval_func_log,@function
prjm_eval_func_log:                     // @prjm_eval_func_log
.Lfunc_begin51:
	.loc	2 1057 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1057:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_log:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_log:ret_val <- $x1
	sub	sp, sp, #64
	.cfi_def_cfa_offset 64
	str	d8, [sp, #16]                   // 8-byte Folded Spill
	stp	x29, x30, [sp, #32]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #48]             // 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_offset b8, -48
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp538:
	//DEBUG_VALUE: prjm_eval_func_log:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_log:ret_val <- $x19
	.loc	2 1063 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1063:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 1060 16                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1060:16
	str	xzr, [x0, #8]!
.Ltmp539:
	//DEBUG_VALUE: prjm_eval_func_log:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 1063 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1063:5
	ldr	x8, [x0, #16]
	.loc	2 1061 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1061:18
	str	x0, [sp]
	.loc	2 1063 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1063:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp540:
	.loc	2 1065 10                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1065:10
	ldr	x8, [sp]
	.loc	2 1065 9 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1065:9
	ldr	d8, [x8]
.Ltmp541:
	.loc	2 1065 9                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1065:9
	fmov	d0, d8
	bl	log
.Ltmp542:
	.loc	2 0 9                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:9
	movi	d1, #0000000000000000
	.loc	2 1065 9                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1065:9
	fcmp	d8, #0.0
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	ldr	x8, [x19]
	.loc	2 1065 9                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1065:9
	fcsel	d0, d0, d1, gt
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	str	d0, [x8]
	.loc	2 1072 1 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1072:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB51_2
.Ltmp543:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_log:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_log:ret_val <- $x19
	.cfi_def_cfa wsp, 64
	.loc	2 1072 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1072:1
	ldp	x20, x19, [sp, #48]             // 16-byte Folded Reload
.Ltmp544:
	//DEBUG_VALUE: prjm_eval_func_log:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	d8, [sp, #16]                   // 8-byte Folded Reload
	ldp	x29, x30, [sp, #32]             // 16-byte Folded Reload
	add	sp, sp, #64
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	.cfi_restore b8
	ret
.Ltmp545:
.LBB51_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_log:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_log:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp546:
.Lfunc_end51:
	.size	prjm_eval_func_log, .Lfunc_end51-prjm_eval_func_log
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_log10,"ax",@progbits
	.hidden	prjm_eval_func_log10            // -- Begin function prjm_eval_func_log10
	.globl	prjm_eval_func_log10
	.p2align	2
	.type	prjm_eval_func_log10,@function
prjm_eval_func_log10:                   // @prjm_eval_func_log10
.Lfunc_begin52:
	.loc	2 1075 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1075:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_log10:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_log10:ret_val <- $x1
	sub	sp, sp, #64
	.cfi_def_cfa_offset 64
	str	d8, [sp, #16]                   // 8-byte Folded Spill
	stp	x29, x30, [sp, #32]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #48]             // 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_offset b8, -48
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp547:
	//DEBUG_VALUE: prjm_eval_func_log10:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_log10:ret_val <- $x19
	.loc	2 1081 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1081:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 1078 16                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1078:16
	str	xzr, [x0, #8]!
.Ltmp548:
	//DEBUG_VALUE: prjm_eval_func_log10:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 1081 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1081:5
	ldr	x8, [x0, #16]
	.loc	2 1079 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1079:18
	str	x0, [sp]
	.loc	2 1081 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1081:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp549:
	.loc	2 1083 10                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1083:10
	ldr	x8, [sp]
	.loc	2 1083 9 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1083:9
	ldr	d8, [x8]
.Ltmp550:
	.loc	2 1083 9                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1083:9
	fmov	d0, d8
	bl	log10
.Ltmp551:
	.loc	2 0 9                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:9
	movi	d1, #0000000000000000
	.loc	2 1083 9                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1083:9
	fcmp	d8, #0.0
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	ldr	x8, [x19]
	.loc	2 1083 9                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1083:9
	fcsel	d0, d0, d1, gt
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	str	d0, [x8]
	.loc	2 1090 1 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1090:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB52_2
.Ltmp552:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_log10:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_log10:ret_val <- $x19
	.cfi_def_cfa wsp, 64
	.loc	2 1090 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1090:1
	ldp	x20, x19, [sp, #48]             // 16-byte Folded Reload
.Ltmp553:
	//DEBUG_VALUE: prjm_eval_func_log10:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	d8, [sp, #16]                   // 8-byte Folded Reload
	ldp	x29, x30, [sp, #32]             // 16-byte Folded Reload
	add	sp, sp, #64
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	.cfi_restore b8
	ret
.Ltmp554:
.LBB52_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_log10:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_log10:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp555:
.Lfunc_end52:
	.size	prjm_eval_func_log10, .Lfunc_end52-prjm_eval_func_log10
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_floor,"ax",@progbits
	.hidden	prjm_eval_func_floor            // -- Begin function prjm_eval_func_floor
	.globl	prjm_eval_func_floor
	.p2align	2
	.type	prjm_eval_func_floor,@function
prjm_eval_func_floor:                   // @prjm_eval_func_floor
.Lfunc_begin53:
	.loc	2 1093 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1093:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_floor:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_floor:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp556:
	//DEBUG_VALUE: prjm_eval_func_floor:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_floor:ret_val <- $x19
	.loc	2 1099 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1099:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 1096 16                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1096:16
	str	xzr, [x0, #8]!
.Ltmp557:
	//DEBUG_VALUE: prjm_eval_func_floor:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 1099 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1099:5
	ldr	x8, [x0, #16]
	.loc	2 1097 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1097:18
	str	x0, [sp]
	.loc	2 1099 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1099:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp558:
	.loc	2 1101 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1101:5
	ldr	x8, [sp]
	ldr	d0, [x8]
	ldr	x8, [x19]
	frintm	d0, d0
	str	d0, [x8]
	.loc	2 1102 1                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1102:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB53_2
.Ltmp559:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_floor:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_floor:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 1102 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1102:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp560:
	//DEBUG_VALUE: prjm_eval_func_floor:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp561:
.LBB53_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_floor:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_floor:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp562:
.Lfunc_end53:
	.size	prjm_eval_func_floor, .Lfunc_end53-prjm_eval_func_floor
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_ceil,"ax",@progbits
	.hidden	prjm_eval_func_ceil             // -- Begin function prjm_eval_func_ceil
	.globl	prjm_eval_func_ceil
	.p2align	2
	.type	prjm_eval_func_ceil,@function
prjm_eval_func_ceil:                    // @prjm_eval_func_ceil
.Lfunc_begin54:
	.loc	2 1105 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1105:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_ceil:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_ceil:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp563:
	//DEBUG_VALUE: prjm_eval_func_ceil:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_ceil:ret_val <- $x19
	.loc	2 1111 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1111:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 1108 16                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1108:16
	str	xzr, [x0, #8]!
.Ltmp564:
	//DEBUG_VALUE: prjm_eval_func_ceil:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 1111 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1111:5
	ldr	x8, [x0, #16]
	.loc	2 1109 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1109:18
	str	x0, [sp]
	.loc	2 1111 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1111:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp565:
	.loc	2 1113 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1113:5
	ldr	x8, [sp]
	ldr	d0, [x8]
	ldr	x8, [x19]
	frintp	d0, d0
	str	d0, [x8]
	.loc	2 1114 1                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1114:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB54_2
.Ltmp566:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_ceil:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_ceil:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 1114 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1114:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp567:
	//DEBUG_VALUE: prjm_eval_func_ceil:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp568:
.LBB54_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_ceil:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_ceil:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp569:
.Lfunc_end54:
	.size	prjm_eval_func_ceil, .Lfunc_end54-prjm_eval_func_ceil
	.cfi_endproc
                                        // -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          // -- Begin function prjm_eval_func_sigmoid
.LCPI55_0:
	.xword	0x3ee4f8b588e368f1              // double 1.0000000000000001E-5
	.section	.text.prjm_eval_func_sigmoid,"ax",@progbits
	.hidden	prjm_eval_func_sigmoid
	.globl	prjm_eval_func_sigmoid
	.p2align	2
	.type	prjm_eval_func_sigmoid,@function
prjm_eval_func_sigmoid:                 // @prjm_eval_func_sigmoid
.Lfunc_begin55:
	.loc	2 1117 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1117:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_sigmoid:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_sigmoid:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp570:
	//DEBUG_VALUE: prjm_eval_func_sigmoid:ctx <- $x20
	mov	x19, x1
.Ltmp571:
	//DEBUG_VALUE: prjm_eval_func_sigmoid:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_sigmoid:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp572:
	.loc	2 1125 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1125:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 1122 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1122:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 1125 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1125:5
	ldr	x9, [x0, #24]
	.loc	2 1123 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1123:18
	str	x8, [sp, #8]
	.loc	2 1125 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1125:5
	ldr	x0, [x9]
	.loc	2 1120 17                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1120:17
	stur	xzr, [x29, #-16]
	.loc	2 1121 17                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1121:17
	str	xzr, [sp, #24]
	.loc	2 1125 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1125:5
	ldr	x8, [x0]
	blr	x8
.Ltmp573:
	.loc	2 1126 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1126:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp574:
	.loc	2 1128 37                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1128:37
	ldp	x9, x8, [sp, #8]
	.loc	2 1128 36 is_stmt 0             // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1128:36
	ldr	d0, [x8]
	.loc	2 1128 55                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1128:55
	ldr	d1, [x9]
	.loc	2 1128 52                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1128:52
	fnmul	d0, d0, d1
	.loc	2 1128 21                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1128:21
	bl	exp
.Ltmp575:
	.loc	2 0 21                          // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:21
	fmov	d1, #1.00000000
	adrp	x8, .LCPI55_0
	movi	d3, #0000000000000000
	ldr	d2, [x8, :lo12:.LCPI55_0]
	.loc	2 1129 5 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1129:5
	ldr	x8, [x19]
	.loc	2 1128 19                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1128:19
	fadd	d0, d0, d1
.Ltmp576:
	//DEBUG_VALUE: prjm_eval_func_sigmoid:t <- $d0
	.loc	2 1129 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1129:5
	fdiv	d1, d1, d0
	fcmp	d0, d2
	fcsel	d0, d1, d3, gt
.Ltmp577:
	str	d0, [x8]
	.loc	2 1130 1                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1130:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB55_2
.Ltmp578:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_sigmoid:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_sigmoid:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 1130 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1130:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp579:
	//DEBUG_VALUE: prjm_eval_func_sigmoid:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_sigmoid:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp580:
.LBB55_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_sigmoid:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_sigmoid:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp581:
.Lfunc_end55:
	.size	prjm_eval_func_sigmoid, .Lfunc_end55-prjm_eval_func_sigmoid
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_sqr,"ax",@progbits
	.hidden	prjm_eval_func_sqr              // -- Begin function prjm_eval_func_sqr
	.globl	prjm_eval_func_sqr
	.p2align	2
	.type	prjm_eval_func_sqr,@function
prjm_eval_func_sqr:                     // @prjm_eval_func_sqr
.Lfunc_begin56:
	.loc	2 1133 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1133:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_sqr:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_sqr:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp582:
	//DEBUG_VALUE: prjm_eval_func_sqr:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_sqr:ret_val <- $x19
	.loc	2 1139 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1139:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 1136 16                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1136:16
	str	xzr, [x0, #8]!
.Ltmp583:
	//DEBUG_VALUE: prjm_eval_func_sqr:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 1139 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1139:5
	ldr	x8, [x0, #16]
	.loc	2 1137 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1137:18
	str	x0, [sp]
	.loc	2 1139 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1139:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp584:
	.loc	2 1141 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1141:5
	ldr	x8, [sp]
	ldr	d0, [x8]
	ldr	x8, [x19]
	fmul	d0, d0, d0
	str	d0, [x8]
	.loc	2 1142 1                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1142:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB56_2
.Ltmp585:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_sqr:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_sqr:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 1142 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1142:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp586:
	//DEBUG_VALUE: prjm_eval_func_sqr:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp587:
.LBB56_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_sqr:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_sqr:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp588:
.Lfunc_end56:
	.size	prjm_eval_func_sqr, .Lfunc_end56-prjm_eval_func_sqr
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_abs,"ax",@progbits
	.hidden	prjm_eval_func_abs              // -- Begin function prjm_eval_func_abs
	.globl	prjm_eval_func_abs
	.p2align	2
	.type	prjm_eval_func_abs,@function
prjm_eval_func_abs:                     // @prjm_eval_func_abs
.Lfunc_begin57:
	.loc	2 1145 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1145:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_abs:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_abs:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp589:
	//DEBUG_VALUE: prjm_eval_func_abs:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_abs:ret_val <- $x19
	.loc	2 1151 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1151:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 1148 16                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1148:16
	str	xzr, [x0, #8]!
.Ltmp590:
	//DEBUG_VALUE: prjm_eval_func_abs:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 1151 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1151:5
	ldr	x8, [x0, #16]
	.loc	2 1149 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1149:18
	str	x0, [sp]
	.loc	2 1151 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1151:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp591:
	.loc	2 1153 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1153:5
	ldr	x8, [sp]
	ldr	d0, [x8]
	ldr	x8, [x19]
	fabs	d0, d0
	str	d0, [x8]
	.loc	2 1154 1                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1154:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB57_2
.Ltmp592:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_abs:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_abs:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 1154 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1154:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp593:
	//DEBUG_VALUE: prjm_eval_func_abs:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp594:
.LBB57_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_abs:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_abs:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp595:
.Lfunc_end57:
	.size	prjm_eval_func_abs, .Lfunc_end57-prjm_eval_func_abs
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_min,"ax",@progbits
	.hidden	prjm_eval_func_min              // -- Begin function prjm_eval_func_min
	.globl	prjm_eval_func_min
	.p2align	2
	.type	prjm_eval_func_min,@function
prjm_eval_func_min:                     // @prjm_eval_func_min
.Lfunc_begin58:
	.loc	2 1157 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1157:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_min:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_min:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp596:
	//DEBUG_VALUE: prjm_eval_func_min:ctx <- $x20
	mov	x19, x1
.Ltmp597:
	//DEBUG_VALUE: prjm_eval_func_min:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_min:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp598:
	.loc	2 1165 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1165:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 1162 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1162:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 1165 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1165:5
	ldr	x9, [x0, #24]
	.loc	2 1163 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1163:18
	str	x8, [sp, #8]
	.loc	2 1165 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1165:5
	ldr	x0, [x9]
	.loc	2 1160 17                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1160:17
	stur	xzr, [x29, #-16]
	.loc	2 1161 17                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1161:17
	str	xzr, [sp, #24]
	.loc	2 1165 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1165:5
	ldr	x8, [x0]
	blr	x8
.Ltmp599:
	.loc	2 1166 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1166:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp600:
	.loc	2 1168 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1168:5
	ldp	x9, x8, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	ldr	x8, [x19]
	fminnm	d0, d0, d1
	str	d0, [x8]
	.loc	2 1169 1                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1169:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB58_2
.Ltmp601:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_min:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_min:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 1169 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1169:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp602:
	//DEBUG_VALUE: prjm_eval_func_min:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_min:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp603:
.LBB58_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_min:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_min:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp604:
.Lfunc_end58:
	.size	prjm_eval_func_min, .Lfunc_end58-prjm_eval_func_min
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_max,"ax",@progbits
	.hidden	prjm_eval_func_max              // -- Begin function prjm_eval_func_max
	.globl	prjm_eval_func_max
	.p2align	2
	.type	prjm_eval_func_max,@function
prjm_eval_func_max:                     // @prjm_eval_func_max
.Lfunc_begin59:
	.loc	2 1172 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1172:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_max:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_max:ret_val <- $x1
	sub	sp, sp, #96
	.cfi_def_cfa_offset 96
	stp	x29, x30, [sp, #48]             // 16-byte Folded Spill
	str	x21, [sp, #64]                  // 8-byte Folded Spill
	stp	x20, x19, [sp, #80]             // 16-byte Folded Spill
	add	x29, sp, #48
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x20, x0
.Ltmp605:
	//DEBUG_VALUE: prjm_eval_func_max:ctx <- $x20
	mov	x19, x1
.Ltmp606:
	//DEBUG_VALUE: prjm_eval_func_max:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_max:ret_val <- $x19
	ldr	x8, [x21, #40]
.Ltmp607:
	.loc	2 1180 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1180:5
	add	x1, sp, #16
	stur	x8, [x29, #-8]
	sub	x8, x29, #16
	.loc	2 1177 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1177:18
	str	x8, [sp, #16]
	add	x8, sp, #24
	.loc	2 1180 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1180:5
	ldr	x9, [x0, #24]
	.loc	2 1178 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1178:18
	str	x8, [sp, #8]
	.loc	2 1180 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1180:5
	ldr	x0, [x9]
	.loc	2 1175 17                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1175:17
	stur	xzr, [x29, #-16]
	.loc	2 1176 17                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1176:17
	str	xzr, [sp, #24]
	.loc	2 1180 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1180:5
	ldr	x8, [x0]
	blr	x8
.Ltmp608:
	.loc	2 1181 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1181:5
	ldr	x8, [x20, #24]
	add	x1, sp, #8
	ldr	x0, [x8, #8]
	ldr	x8, [x0]
	blr	x8
.Ltmp609:
	.loc	2 1183 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1183:5
	ldp	x9, x8, [sp, #8]
	ldr	d0, [x8]
	ldr	d1, [x9]
	ldr	x8, [x19]
	fmaxnm	d0, d0, d1
	str	d0, [x8]
	.loc	2 1184 1                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1184:1
	ldr	x8, [x21, #40]
	ldur	x9, [x29, #-8]
	cmp	x8, x9
	b.ne	.LBB59_2
.Ltmp610:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_max:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_max:ctx <- $x20
	.cfi_def_cfa wsp, 96
	.loc	2 1184 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1184:1
	ldp	x20, x19, [sp, #80]             // 16-byte Folded Reload
.Ltmp611:
	//DEBUG_VALUE: prjm_eval_func_max:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_max:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	x21, [sp, #64]                  // 8-byte Folded Reload
	ldp	x29, x30, [sp, #48]             // 16-byte Folded Reload
	add	sp, sp, #96
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp612:
.LBB59_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_max:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_max:ctx <- $x20
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp613:
.Lfunc_end59:
	.size	prjm_eval_func_max, .Lfunc_end59-prjm_eval_func_max
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_sign,"ax",@progbits
	.hidden	prjm_eval_func_sign             // -- Begin function prjm_eval_func_sign
	.globl	prjm_eval_func_sign
	.p2align	2
	.type	prjm_eval_func_sign,@function
prjm_eval_func_sign:                    // @prjm_eval_func_sign
.Lfunc_begin60:
	.loc	2 1187 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1187:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_sign:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_sign:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp614:
	//DEBUG_VALUE: prjm_eval_func_sign:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_sign:ret_val <- $x19
	.loc	2 1193 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1193:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 1190 16                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1190:16
	str	xzr, [x0, #8]!
.Ltmp615:
	//DEBUG_VALUE: prjm_eval_func_sign:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 1193 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1193:5
	ldr	x8, [x0, #16]
	.loc	2 1191 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1191:18
	str	x0, [sp]
	.loc	2 1193 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1193:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp616:
	.loc	2 1195 10                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1195:10
	ldr	x8, [sp]
	fmov	d1, #1.00000000
	fmov	d2, #-1.00000000
	.loc	2 1195 9 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1195:9
	ldr	d0, [x8]
.Ltmp617:
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	ldr	x8, [x19]
	.loc	2 1195 9                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1195:9
	fcmp	d0, #0.0
	fcsel	d1, d2, d1, lt
	fcsel	d0, d0, d1, eq
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	str	d0, [x8]
	.loc	2 1201 1 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1201:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB60_2
.Ltmp618:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_sign:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_sign:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 1201 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1201:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp619:
	//DEBUG_VALUE: prjm_eval_func_sign:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp620:
.LBB60_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_sign:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_sign:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp621:
.Lfunc_end60:
	.size	prjm_eval_func_sign, .Lfunc_end60-prjm_eval_func_sign
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_rand,"ax",@progbits
	.hidden	prjm_eval_func_rand             // -- Begin function prjm_eval_func_rand
	.globl	prjm_eval_func_rand
	.p2align	2
	.type	prjm_eval_func_rand,@function
prjm_eval_func_rand:                    // @prjm_eval_func_rand
.Lfunc_begin61:
	.loc	2 1204 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1204:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x1
	sub	sp, sp, #80
	.cfi_def_cfa_offset 80
	str	d8, [sp, #16]                   // 8-byte Folded Spill
	stp	x29, x30, [sp, #32]             // 16-byte Folded Spill
	stp	x22, x21, [sp, #48]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #64]             // 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 48
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w21, -24
	.cfi_offset w22, -32
	.cfi_offset w30, -40
	.cfi_offset w29, -48
	.cfi_offset b8, -64
	.cfi_remember_state
	mrs	x21, TPIDR_EL0
	mov	x19, x1
.Ltmp622:
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	.loc	2 1210 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1210:5
	mov	x1, sp
	ldr	x8, [x21, #40]
	str	x8, [sp, #8]
	.loc	2 1207 16                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1207:16
	str	xzr, [x0, #8]!
.Ltmp623:
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 1210 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1210:5
	ldr	x8, [x0, #16]
	.loc	2 1208 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1208:18
	str	x0, [sp]
	.loc	2 1210 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1210:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp624:
	.loc	2 1212 35                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1212:35
	ldr	x8, [sp]
.Ltmp625:
	.loc	2 169 10                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:169:10
	adrp	x0, __emutls_v.prjm_eval_genrand_int32.mti
	add	x0, x0, :lo12:__emutls_v.prjm_eval_genrand_int32.mti
.Ltmp626:
	.loc	2 1212 34                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1212:34
	ldr	d8, [x8]
.Ltmp627:
	.loc	2 169 10                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:169:10
	bl	__emutls_get_address
.Ltmp628:
	ldr	w22, [x0]
	mov	x20, x0
.Ltmp629:
	.loc	2 169 9 is_stmt 0               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:169:9
	cbz	w22, .LBB61_2
.Ltmp630:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	.loc	2 0 9                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:9
	adrp	x0, __emutls_v.prjm_eval_genrand_int32.mt
	add	x0, x0, :lo12:__emutls_v.prjm_eval_genrand_int32.mt
	bl	__emutls_get_address
.Ltmp631:
	.loc	2 187 9 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:187:9
	cmp	w22, #624
	b.ge	.LBB61_4
	b	.LBB61_9
.Ltmp632:
.LBB61_2:
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	//DEBUG_VALUE: s <- 1094840333
	.loc	2 172 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:172:9
	adrp	x0, __emutls_v.prjm_eval_genrand_int32.mt
	add	x0, x0, :lo12:__emutls_v.prjm_eval_genrand_int32.mt
	bl	__emutls_get_address
.Ltmp633:
	.loc	2 0 9 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:9
	mov	w9, #61453                      // =0xf00d
	mov	w8, #1                          // =0x1
	movk	w9, #16705, lsl #16
	.loc	2 172 15                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:172:15
	str	w9, [x0]
	mov	w9, #35173                      // =0x8965
	movk	w9, #27655, lsl #16
.Ltmp634:
	.loc	2 173 0 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:173:0
	str	w8, [x20]
.Ltmp635:
.LBB61_3:                               // =>This Inner Loop Header: Depth=1
	//DEBUG_VALUE: s <- 1094840333
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	.loc	2 175 13                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:175:13
	add	x10, x0, w8, sxtw #2
	.loc	2 176 34                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:176:34
	ldur	w11, [x10, #-4]
	.loc	2 176 46 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:176:46
	eor	w11, w11, w11, lsr #30
	.loc	2 176 69                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:176:69
	madd	w8, w11, w9, w8
	.loc	2 175 21 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:175:21
	str	w8, [x10]
.Ltmp636:
	.loc	2 173 35                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:173:35
	ldr	w10, [x20]
	add	w8, w10, #1
.Ltmp637:
	.loc	2 173 9 is_stmt 0               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:173:9
	cmp	w10, #623
	.loc	2 173 0                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:173:0
	str	w8, [x20]
	.loc	2 173 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:173:9
	b.lt	.LBB61_3
.Ltmp638:
.LBB61_4:
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	.loc	2 193 18 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:18
	ldr	w9, [x0]
	mov	x10, xzr
.Ltmp639:
	//DEBUG_VALUE: kk <- 0
	.loc	2 0 18 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:18
	adrp	x8, prjm_eval_genrand_int32.mag01
	add	x8, x8, :lo12:prjm_eval_genrand_int32.mag01
.Ltmp640:
.LBB61_5:                               // =>This Inner Loop Header: Depth=1
	//DEBUG_VALUE: kk <- 0
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	.loc	2 193 18                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:18
	add	x11, x0, x10
	mov	w13, w9
	.loc	2 193 48                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:48
	add	x10, x10, #8
	ldp	w12, w9, [x11, #4]
	.loc	2 193 25                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:25
	and	w13, w13, #0x80000000
	.loc	2 194 22 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:22
	ldr	w14, [x11, #1588]
	.loc	2 193 48                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:48
	cmp	x10, #904
	.loc	2 194 54                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:54
	and	x15, x12, #0x1
	.loc	2 193 53                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:53
	and	w16, w12, #0x7ffffffe
	.loc	2 194 54                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:54
	and	x17, x9, #0x1
	.loc	2 194 46 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:46
	ldr	w15, [x8, x15, lsl #2]
	.loc	2 193 39 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:39
	orr	w13, w16, w13
	.loc	2 194 22                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:22
	ldr	w16, [x11, #1592]
	.loc	2 194 46 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:46
	ldr	w17, [x8, x17, lsl #2]
	.loc	2 193 25 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:25
	and	w12, w12, #0x80000000
	.loc	2 194 33                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:33
	eor	w14, w15, w14
	.loc	2 193 53                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:53
	and	w15, w9, #0x7ffffffe
	.loc	2 193 39 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:39
	orr	w12, w15, w12
	.loc	2 194 33 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:33
	eor	w15, w17, w16
	.loc	2 194 44 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:44
	eor	w13, w14, w13, lsr #1
	eor	w12, w15, w12, lsr #1
	.loc	2 194 20                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:20
	stp	w13, w12, [x11]
	.loc	2 193 48 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:48
	b.ne	.LBB61_5
.Ltmp641:
// %bb.6:
	//DEBUG_VALUE: kk <- 0
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	//DEBUG_VALUE: kk <- 226
	.loc	2 0 48 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:48
	ldr	w11, [x0, #908]
	.loc	2 194 22 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:22
	ldr	w13, [x0, #2492]
	.loc	2 193 25                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:25
	and	w9, w9, #0x80000000
	mov	x10, xzr
	.loc	2 194 54                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:54
	and	x12, x11, #0x1
	.loc	2 193 53                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:53
	and	w14, w11, #0x7ffffffe
	.loc	2 194 46                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:46
	ldr	w12, [x8, x12, lsl #2]
	.loc	2 193 39                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:193:39
	orr	w9, w14, w9
.Ltmp642:
	//DEBUG_VALUE: prjm_eval_genrand_int32:y <- [DW_OP_LLVM_arg 0, DW_OP_LLVM_arg 0, DW_OP_constu 2147483647, DW_OP_and, DW_OP_or, DW_OP_stack_value] undef
	.loc	2 194 33                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:33
	eor	w12, w12, w13
	.loc	2 194 44 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:44
	eor	w9, w12, w9, lsr #1
	.loc	2 194 20                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:194:20
	str	w9, [x0, #904]
.Ltmp643:
	//DEBUG_VALUE: kk <- [DW_OP_stack_value] 227
	.loc	2 0 20                          // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:20
	mov	w9, w11
.Ltmp644:
.LBB61_7:                               // =>This Inner Loop Header: Depth=1
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	//DEBUG_VALUE: kk <- [DW_OP_consts 4, DW_OP_div, DW_OP_consts 227, DW_OP_plus, DW_OP_stack_value] $x10
	.loc	2 198 25 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:198:25
	add	x11, x0, x10
	and	w12, w9, #0x80000000
.Ltmp645:
	.loc	2 196 19                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:196:19
	add	x10, x10, #4
.Ltmp646:
	.loc	2 0 19 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:19
	ldr	w9, [x11, #912]
.Ltmp647:
	.loc	2 199 22 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:199:22
	ldr	w14, [x11]
.Ltmp648:
	.loc	2 196 9                         // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:196:9
	cmp	x10, #1584
.Ltmp649:
	.loc	2 199 60                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:199:60
	and	x13, x9, #0x1
	.loc	2 198 53                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:198:53
	and	w15, w9, #0x7ffffffe
	.loc	2 199 52                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:199:52
	ldr	w13, [x8, x13, lsl #2]
	.loc	2 198 39                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:198:39
	orr	w12, w15, w12
.Ltmp650:
	//DEBUG_VALUE: prjm_eval_genrand_int32:y <- [DW_OP_LLVM_arg 0, DW_OP_LLVM_arg 0, DW_OP_constu 2147483647, DW_OP_and, DW_OP_or, DW_OP_stack_value] undef
	.loc	2 199 39                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:199:39
	eor	w13, w13, w14
	.loc	2 199 50 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:199:50
	eor	w12, w13, w12, lsr #1
	.loc	2 199 20                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:199:20
	str	w12, [x11, #908]
.Ltmp651:
	//DEBUG_VALUE: kk <- [DW_OP_consts 4, DW_OP_div, DW_OP_consts 228, DW_OP_plus, DW_OP_stack_value] $x10
	.loc	2 196 9 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:196:9
	b.ne	.LBB61_7
.Ltmp652:
// %bb.8:
	//DEBUG_VALUE: kk <- [DW_OP_consts 4, DW_OP_div, DW_OP_consts 228, DW_OP_plus, DW_OP_stack_value] $x10
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	.loc	2 0 9 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:9
	ldr	w9, [x0]
	.loc	2 201 14 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:201:14
	ldr	w10, [x0, #2492]
.Ltmp653:
	.loc	2 0 14 is_stmt 0                // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:14
	mov	w22, wzr
	.loc	2 202 21 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:202:21
	ldr	w12, [x0, #1584]
	.loc	2 202 52 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:202:52
	and	x11, x9, #0x1
	.loc	2 201 24 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:201:24
	and	w10, w10, #0x80000000
	.loc	2 201 47 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:201:47
	and	w9, w9, #0x7ffffffe
	.loc	2 202 44 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:202:44
	ldr	w8, [x8, x11, lsl #2]
	.loc	2 201 38                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:201:38
	orr	w9, w9, w10
.Ltmp654:
	//DEBUG_VALUE: prjm_eval_genrand_int32:y <- [DW_OP_LLVM_arg 0, DW_OP_LLVM_arg 0, DW_OP_constu 2147483647, DW_OP_and, DW_OP_or, DW_OP_stack_value] undef
	.loc	2 202 31                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:202:31
	eor	w8, w8, w12
	.loc	2 202 42 is_stmt 0              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:202:42
	eor	w8, w8, w9, lsr #1
	.loc	2 202 19                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:202:19
	str	w8, [x0, #2492]
.Ltmp655:
.LBB61_9:
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	.loc	2 207 15 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:207:15
	add	w8, w22, #1
	mov	w9, #22144                      // =0x5680
.Ltmp656:
	.loc	2 1212 28                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1212:28
	frintm	d0, d8
.Ltmp657:
	//DEBUG_VALUE: prjm_eval_func_rand:rand_max <- $d0
	.loc	2 207 15                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:207:15
	str	w8, [x20]
	movk	w9, #40236, lsl #16
	fmov	d1, #1.00000000
	.loc	2 207 9 is_stmt 0               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:207:9
	ldr	w8, [x0, w22, sxtw #2]
.Ltmp658:
	//DEBUG_VALUE: prjm_eval_genrand_int32:y <- $w8
	.loc	2 210 7 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:210:7
	eor	w8, w8, w8, lsr #11
.Ltmp659:
	//DEBUG_VALUE: prjm_eval_genrand_int32:y <- $w8
	.loc	2 1213 9                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1213:9
	fmaxnm	d0, d0, d1
.Ltmp660:
	//DEBUG_VALUE: prjm_eval_func_rand:rand_max <- $d0
	.loc	2 211 19                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:211:19
	and	w9, w9, w8, lsl #7
	.loc	2 211 7 is_stmt 0               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:211:7
	eor	w8, w9, w8
.Ltmp661:
	//DEBUG_VALUE: prjm_eval_genrand_int32:y <- $w8
	.loc	2 0 7                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:7
	mov	w9, #-272236544                 // =0xefc60000
	.loc	2 212 20 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:212:20
	and	w9, w9, w8, lsl #15
	.loc	2 212 7 is_stmt 0               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:212:7
	eor	w8, w9, w8
.Ltmp662:
	//DEBUG_VALUE: prjm_eval_genrand_int32:y <- $w8
	.loc	2 0 7                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:7
	mov	x9, #1048576                    // =0x100000
	movk	x9, #15856, lsl #48
	.loc	2 213 7 is_stmt 1               // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:213:7
	eor	w8, w8, w8, lsr #18
.Ltmp663:
	//DEBUG_VALUE: prjm_eval_genrand_int32:y <- $w8
	.loc	2 0 7 is_stmt 0                 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:7
	fmov	d1, x9
.Ltmp664:
	.loc	2 1218 5 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1218:5
	ucvtf	d2, w8
	ldr	x8, [x19]
.Ltmp665:
	fmul	d0, d0, d1
.Ltmp666:
	fmul	d0, d0, d2
	str	d0, [x8]
	.loc	2 1219 1                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1219:1
	ldr	x8, [x21, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB61_11
.Ltmp667:
// %bb.10:
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	.cfi_def_cfa wsp, 80
	.loc	2 1219 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1219:1
	ldp	x20, x19, [sp, #64]             // 16-byte Folded Reload
.Ltmp668:
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldr	d8, [sp, #16]                   // 8-byte Folded Reload
	ldp	x22, x21, [sp, #48]             // 16-byte Folded Reload
	ldp	x29, x30, [sp, #32]             // 16-byte Folded Reload
	add	sp, sp, #80
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w21
	.cfi_restore w22
	.cfi_restore w30
	.cfi_restore w29
	.cfi_restore b8
	ret
.Ltmp669:
.LBB61_11:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_rand:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_rand:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp670:
.Lfunc_end61:
	.size	prjm_eval_func_rand, .Lfunc_end61-prjm_eval_func_rand
	.cfi_endproc
                                        // -- End function
	.section	.text.prjm_eval_func_invsqrt,"ax",@progbits
	.hidden	prjm_eval_func_invsqrt          // -- Begin function prjm_eval_func_invsqrt
	.globl	prjm_eval_func_invsqrt
	.p2align	2
	.type	prjm_eval_func_invsqrt,@function
prjm_eval_func_invsqrt:                 // @prjm_eval_func_invsqrt
.Lfunc_begin62:
	.loc	2 1222 0 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1222:0
	.cfi_startproc
// %bb.0:
	//DEBUG_VALUE: prjm_eval_func_invsqrt:ctx <- $x0
	//DEBUG_VALUE: prjm_eval_func_invsqrt:ret_val <- $x1
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	stp	x29, x30, [sp, #16]             // 16-byte Folded Spill
	stp	x20, x19, [sp, #32]             // 16-byte Folded Spill
	add	x29, sp, #16
	.cfi_def_cfa w29, 32
	.cfi_offset w19, -8
	.cfi_offset w20, -16
	.cfi_offset w30, -24
	.cfi_offset w29, -32
	.cfi_remember_state
	mrs	x20, TPIDR_EL0
	mov	x19, x1
.Ltmp671:
	//DEBUG_VALUE: prjm_eval_func_invsqrt:ret_val <- $x19
	//DEBUG_VALUE: prjm_eval_func_invsqrt:ret_val <- $x19
	.loc	2 1250 5 prologue_end           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1250:5
	mov	x1, sp
	ldr	x8, [x20, #40]
	str	x8, [sp, #8]
	.loc	2 1247 16                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1247:16
	str	xzr, [x0, #8]!
.Ltmp672:
	//DEBUG_VALUE: prjm_eval_func_invsqrt:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	.loc	2 1250 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1250:5
	ldr	x8, [x0, #16]
	.loc	2 1248 18                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1248:18
	str	x0, [sp]
	.loc	2 1250 5                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1250:5
	ldr	x0, [x8]
	ldr	x8, [x0]
	blr	x8
.Ltmp673:
	.loc	2 1252 26                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1252:26
	ldr	x8, [sp]
	mov	x9, #14249                      // =0x37a9
	fmov	d1, #-0.50000000
	movk	x9, #51125, lsl #16
	fmov	d3, #1.50000000
	.loc	2 1252 25 is_stmt 0             // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1252:25
	ldr	d0, [x8]
.Ltmp674:
	//DEBUG_VALUE: prjm_eval_func_invsqrt:type_conv <- $d0
	.loc	2 0 25                          // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:25
	movk	x9, #60240, lsl #32
	movk	x9, #24550, lsl #48
	.loc	2 1254 59 is_stmt 1             // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1254:59
	fmov	x8, d0
	.loc	2 1255 95                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1255:95
	fmul	d0, d0, d1
.Ltmp675:
	.loc	2 1254 46                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1254:46
	sub	x8, x9, x8, lsr #1
	.loc	2 1254 23 is_stmt 0             // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1254:23
	fmov	d2, x8
.Ltmp676:
	//DEBUG_VALUE: prjm_eval_func_invsqrt:type_conv <- $d2
	.loc	2 1257 5 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1257:5
	ldr	x8, [x19]
	.loc	2 1255 95                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1255:95
	fmul	d1, d2, d2
	.loc	2 1255 64 is_stmt 0             // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1255:64
	fmadd	d0, d1, d0, d3
	.loc	2 1255 49                       // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1255:49
	fmul	d0, d0, d2
.Ltmp677:
	//DEBUG_VALUE: prjm_eval_func_invsqrt:type_conv <- $d0
	.loc	2 1257 5 is_stmt 1              // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1257:5
	str	d0, [x8]
	.loc	2 1258 1                        // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1258:1
	ldr	x8, [x20, #40]
	ldr	x9, [sp, #8]
	cmp	x8, x9
	b.ne	.LBB62_2
.Ltmp678:
// %bb.1:
	//DEBUG_VALUE: prjm_eval_func_invsqrt:type_conv <- $d0
	//DEBUG_VALUE: prjm_eval_func_invsqrt:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_invsqrt:ret_val <- $x19
	.cfi_def_cfa wsp, 48
	.loc	2 1258 1 epilogue_begin is_stmt 0 // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:1258:1
	ldp	x20, x19, [sp, #32]             // 16-byte Folded Reload
.Ltmp679:
	//DEBUG_VALUE: prjm_eval_func_invsqrt:ret_val <- [DW_OP_LLVM_entry_value 1] $x1
	ldp	x29, x30, [sp, #16]             // 16-byte Folded Reload
	add	sp, sp, #48
	.cfi_def_cfa_offset 0
	.cfi_restore w19
	.cfi_restore w20
	.cfi_restore w30
	.cfi_restore w29
	ret
.Ltmp680:
.LBB62_2:
	.cfi_restore_state
	//DEBUG_VALUE: prjm_eval_func_invsqrt:type_conv <- $d0
	//DEBUG_VALUE: prjm_eval_func_invsqrt:ctx <- [DW_OP_LLVM_entry_value 1] $x0
	//DEBUG_VALUE: prjm_eval_func_invsqrt:ret_val <- $x19
	.loc	2 0 0                           // i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c:0:0
	bl	__stack_chk_fail
.Ltmp681:
.Lfunc_end62:
	.size	prjm_eval_func_invsqrt, .Lfunc_end62-prjm_eval_func_invsqrt
	.cfi_endproc
                                        // -- End function
	.type	intrinsic_function_table,@object // @intrinsic_function_table
	.section	.data.intrinsic_function_table,"aw",@progbits
	.p2align	3, 0x0
intrinsic_function_table:
	.xword	.L.str
	.xword	prjm_eval_func_const
	.word	0                               // 0x0
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.1
	.xword	prjm_eval_func_var
	.word	0                               // 0x0
	.byte	0                               // 0x0
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.2
	.xword	prjm_eval_func_execute_list
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.3
	.xword	prjm_eval_func_bitwise_or
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.4
	.xword	prjm_eval_func_bitwise_and
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.5
	.xword	prjm_eval_func_if
	.word	3                               // 0x3
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.6
	.xword	prjm_eval_func_if
	.word	3                               // 0x3
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.7
	.xword	prjm_eval_func_boolean_and_op
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.8
	.xword	prjm_eval_func_boolean_or_op
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.9
	.xword	prjm_eval_func_execute_loop
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.10
	.xword	prjm_eval_func_execute_while
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.11
	.xword	prjm_eval_func_bnot
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.12
	.xword	prjm_eval_func_bnot
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.13
	.xword	prjm_eval_func_equal
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.14
	.xword	prjm_eval_func_equal
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.15
	.xword	prjm_eval_func_notequal
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.16
	.xword	prjm_eval_func_below
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.17
	.xword	prjm_eval_func_below
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.18
	.xword	prjm_eval_func_above
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.19
	.xword	prjm_eval_func_above
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.20
	.xword	prjm_eval_func_beloweq
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.21
	.xword	prjm_eval_func_aboveeq
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.22
	.xword	prjm_eval_func_set
	.word	2                               // 0x2
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.23
	.xword	prjm_eval_func_set
	.word	2                               // 0x2
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.24
	.xword	prjm_eval_func_add
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.25
	.xword	prjm_eval_func_sub
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.26
	.xword	prjm_eval_func_mul
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.27
	.xword	prjm_eval_func_div
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.28
	.xword	prjm_eval_func_mod
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.29
	.xword	prjm_eval_func_mul_op
	.word	2                               // 0x2
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.30
	.xword	prjm_eval_func_div_op
	.word	2                               // 0x2
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.31
	.xword	prjm_eval_func_bitwise_or_op
	.word	2                               // 0x2
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.32
	.xword	prjm_eval_func_bitwise_and_op
	.word	2                               // 0x2
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.33
	.xword	prjm_eval_func_add_op
	.word	2                               // 0x2
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.34
	.xword	prjm_eval_func_sub_op
	.word	2                               // 0x2
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.35
	.xword	prjm_eval_func_mod_op
	.word	2                               // 0x2
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.36
	.xword	prjm_eval_func_sin
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.37
	.xword	prjm_eval_func_cos
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.38
	.xword	prjm_eval_func_tan
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.39
	.xword	prjm_eval_func_asin
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.40
	.xword	prjm_eval_func_acos
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.41
	.xword	prjm_eval_func_atan
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.42
	.xword	prjm_eval_func_atan2
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.43
	.xword	prjm_eval_func_sqr
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.44
	.xword	prjm_eval_func_sqrt
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.45
	.xword	prjm_eval_func_pow
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.46
	.xword	prjm_eval_func_pow_op
	.word	2                               // 0x2
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.47
	.xword	prjm_eval_func_exp
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.48
	.xword	prjm_eval_func_neg
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.49
	.xword	prjm_eval_func_log
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.50
	.xword	prjm_eval_func_log10
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.51
	.xword	prjm_eval_func_abs
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.52
	.xword	prjm_eval_func_min
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.53
	.xword	prjm_eval_func_max
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.54
	.xword	prjm_eval_func_sign
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.55
	.xword	prjm_eval_func_rand
	.word	1                               // 0x1
	.byte	0                               // 0x0
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.56
	.xword	prjm_eval_func_floor
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.57
	.xword	prjm_eval_func_floor
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.58
	.xword	prjm_eval_func_ceil
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.59
	.xword	prjm_eval_func_invsqrt
	.word	1                               // 0x1
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.60
	.xword	prjm_eval_func_sigmoid
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.61
	.xword	prjm_eval_func_boolean_and_func
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.62
	.xword	prjm_eval_func_boolean_or_func
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.63
	.xword	prjm_eval_func_exec2
	.word	2                               // 0x2
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.64
	.xword	prjm_eval_func_exec3
	.word	3                               // 0x3
	.byte	1                               // 0x1
	.byte	0                               // 0x0
	.zero	2
	.xword	.L.str.65
	.xword	prjm_eval_func_mem
	.word	1                               // 0x1
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.66
	.xword	prjm_eval_func_mem
	.word	1                               // 0x1
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.67
	.xword	prjm_eval_func_mem
	.word	1                               // 0x1
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.68
	.xword	prjm_eval_func_mem
	.word	1                               // 0x1
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.69
	.xword	prjm_eval_func_freembuf
	.word	1                               // 0x1
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.70
	.xword	prjm_eval_func_memcpy
	.word	3                               // 0x3
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.xword	.L.str.71
	.xword	prjm_eval_func_memset
	.word	3                               // 0x3
	.byte	0                               // 0x0
	.byte	1                               // 0x1
	.zero	2
	.size	intrinsic_function_table, 1728

	.type	.L.str,@object                  // @.str
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str:
	.asciz	"/*const*/"
	.size	.L.str, 10

	.type	.L.str.1,@object                // @.str.1
.L.str.1:
	.asciz	"/*var*/"
	.size	.L.str.1, 8

	.type	.L.str.2,@object                // @.str.2
.L.str.2:
	.asciz	"/*list*/"
	.size	.L.str.2, 9

	.type	.L.str.3,@object                // @.str.3
.L.str.3:
	.asciz	"/*or*/"
	.size	.L.str.3, 7

	.type	.L.str.4,@object                // @.str.4
.L.str.4:
	.asciz	"/*and*/"
	.size	.L.str.4, 8

	.type	.L.str.5,@object                // @.str.5
.L.str.5:
	.asciz	"if"
	.size	.L.str.5, 3

	.type	.L.str.6,@object                // @.str.6
.L.str.6:
	.asciz	"_if"
	.size	.L.str.6, 4

	.type	.L.str.7,@object                // @.str.7
.L.str.7:
	.asciz	"_and"
	.size	.L.str.7, 5

	.type	.L.str.8,@object                // @.str.8
.L.str.8:
	.asciz	"_or"
	.size	.L.str.8, 4

	.type	.L.str.9,@object                // @.str.9
.L.str.9:
	.asciz	"loop"
	.size	.L.str.9, 5

	.type	.L.str.10,@object               // @.str.10
.L.str.10:
	.asciz	"while"
	.size	.L.str.10, 6

	.type	.L.str.11,@object               // @.str.11
.L.str.11:
	.asciz	"_not"
	.size	.L.str.11, 5

	.type	.L.str.12,@object               // @.str.12
.L.str.12:
	.asciz	"bnot"
	.size	.L.str.12, 5

	.type	.L.str.13,@object               // @.str.13
.L.str.13:
	.asciz	"_equal"
	.size	.L.str.13, 7

	.type	.L.str.14,@object               // @.str.14
.L.str.14:
	.asciz	"equal"
	.size	.L.str.14, 6

	.type	.L.str.15,@object               // @.str.15
.L.str.15:
	.asciz	"_noteq"
	.size	.L.str.15, 7

	.type	.L.str.16,@object               // @.str.16
.L.str.16:
	.asciz	"_below"
	.size	.L.str.16, 7

	.type	.L.str.17,@object               // @.str.17
.L.str.17:
	.asciz	"below"
	.size	.L.str.17, 6

	.type	.L.str.18,@object               // @.str.18
.L.str.18:
	.asciz	"_above"
	.size	.L.str.18, 7

	.type	.L.str.19,@object               // @.str.19
.L.str.19:
	.asciz	"above"
	.size	.L.str.19, 6

	.type	.L.str.20,@object               // @.str.20
.L.str.20:
	.asciz	"_beleq"
	.size	.L.str.20, 7

	.type	.L.str.21,@object               // @.str.21
.L.str.21:
	.asciz	"_aboeq"
	.size	.L.str.21, 7

	.type	.L.str.22,@object               // @.str.22
.L.str.22:
	.asciz	"_set"
	.size	.L.str.22, 5

	.type	.L.str.23,@object               // @.str.23
.L.str.23:
	.asciz	"assign"
	.size	.L.str.23, 7

	.type	.L.str.24,@object               // @.str.24
.L.str.24:
	.asciz	"_add"
	.size	.L.str.24, 5

	.type	.L.str.25,@object               // @.str.25
.L.str.25:
	.asciz	"_sub"
	.size	.L.str.25, 5

	.type	.L.str.26,@object               // @.str.26
.L.str.26:
	.asciz	"_mul"
	.size	.L.str.26, 5

	.type	.L.str.27,@object               // @.str.27
.L.str.27:
	.asciz	"_div"
	.size	.L.str.27, 5

	.type	.L.str.28,@object               // @.str.28
.L.str.28:
	.asciz	"_mod"
	.size	.L.str.28, 5

	.type	.L.str.29,@object               // @.str.29
.L.str.29:
	.asciz	"_mulop"
	.size	.L.str.29, 7

	.type	.L.str.30,@object               // @.str.30
.L.str.30:
	.asciz	"_divop"
	.size	.L.str.30, 7

	.type	.L.str.31,@object               // @.str.31
.L.str.31:
	.asciz	"_orop"
	.size	.L.str.31, 6

	.type	.L.str.32,@object               // @.str.32
.L.str.32:
	.asciz	"_andop"
	.size	.L.str.32, 7

	.type	.L.str.33,@object               // @.str.33
.L.str.33:
	.asciz	"_addop"
	.size	.L.str.33, 7

	.type	.L.str.34,@object               // @.str.34
.L.str.34:
	.asciz	"_subop"
	.size	.L.str.34, 7

	.type	.L.str.35,@object               // @.str.35
.L.str.35:
	.asciz	"_modop"
	.size	.L.str.35, 7

	.type	.L.str.36,@object               // @.str.36
.L.str.36:
	.asciz	"sin"
	.size	.L.str.36, 4

	.type	.L.str.37,@object               // @.str.37
.L.str.37:
	.asciz	"cos"
	.size	.L.str.37, 4

	.type	.L.str.38,@object               // @.str.38
.L.str.38:
	.asciz	"tan"
	.size	.L.str.38, 4

	.type	.L.str.39,@object               // @.str.39
.L.str.39:
	.asciz	"asin"
	.size	.L.str.39, 5

	.type	.L.str.40,@object               // @.str.40
.L.str.40:
	.asciz	"acos"
	.size	.L.str.40, 5

	.type	.L.str.41,@object               // @.str.41
.L.str.41:
	.asciz	"atan"
	.size	.L.str.41, 5

	.type	.L.str.42,@object               // @.str.42
.L.str.42:
	.asciz	"atan2"
	.size	.L.str.42, 6

	.type	.L.str.43,@object               // @.str.43
.L.str.43:
	.asciz	"sqr"
	.size	.L.str.43, 4

	.type	.L.str.44,@object               // @.str.44
.L.str.44:
	.asciz	"sqrt"
	.size	.L.str.44, 5

	.type	.L.str.45,@object               // @.str.45
.L.str.45:
	.asciz	"pow"
	.size	.L.str.45, 4

	.type	.L.str.46,@object               // @.str.46
.L.str.46:
	.asciz	"_powop"
	.size	.L.str.46, 7

	.type	.L.str.47,@object               // @.str.47
.L.str.47:
	.asciz	"exp"
	.size	.L.str.47, 4

	.type	.L.str.48,@object               // @.str.48
.L.str.48:
	.asciz	"_neg"
	.size	.L.str.48, 5

	.type	.L.str.49,@object               // @.str.49
.L.str.49:
	.asciz	"log"
	.size	.L.str.49, 4

	.type	.L.str.50,@object               // @.str.50
.L.str.50:
	.asciz	"log10"
	.size	.L.str.50, 6

	.type	.L.str.51,@object               // @.str.51
.L.str.51:
	.asciz	"abs"
	.size	.L.str.51, 4

	.type	.L.str.52,@object               // @.str.52
.L.str.52:
	.asciz	"min"
	.size	.L.str.52, 4

	.type	.L.str.53,@object               // @.str.53
.L.str.53:
	.asciz	"max"
	.size	.L.str.53, 4

	.type	.L.str.54,@object               // @.str.54
.L.str.54:
	.asciz	"sign"
	.size	.L.str.54, 5

	.type	.L.str.55,@object               // @.str.55
.L.str.55:
	.asciz	"rand"
	.size	.L.str.55, 5

	.type	.L.str.56,@object               // @.str.56
.L.str.56:
	.asciz	"floor"
	.size	.L.str.56, 6

	.type	.L.str.57,@object               // @.str.57
.L.str.57:
	.asciz	"int"
	.size	.L.str.57, 4

	.type	.L.str.58,@object               // @.str.58
.L.str.58:
	.asciz	"ceil"
	.size	.L.str.58, 5

	.type	.L.str.59,@object               // @.str.59
.L.str.59:
	.asciz	"invsqrt"
	.size	.L.str.59, 8

	.type	.L.str.60,@object               // @.str.60
.L.str.60:
	.asciz	"sigmoid"
	.size	.L.str.60, 8

	.type	.L.str.61,@object               // @.str.61
.L.str.61:
	.asciz	"band"
	.size	.L.str.61, 5

	.type	.L.str.62,@object               // @.str.62
.L.str.62:
	.asciz	"bor"
	.size	.L.str.62, 4

	.type	.L.str.63,@object               // @.str.63
.L.str.63:
	.asciz	"exec2"
	.size	.L.str.63, 6

	.type	.L.str.64,@object               // @.str.64
.L.str.64:
	.asciz	"exec3"
	.size	.L.str.64, 6

	.type	.L.str.65,@object               // @.str.65
.L.str.65:
	.asciz	"_mem"
	.size	.L.str.65, 5

	.type	.L.str.66,@object               // @.str.66
.L.str.66:
	.asciz	"megabuf"
	.size	.L.str.66, 8

	.type	.L.str.67,@object               // @.str.67
.L.str.67:
	.asciz	"_gmem"
	.size	.L.str.67, 6

	.type	.L.str.68,@object               // @.str.68
.L.str.68:
	.asciz	"gmegabuf"
	.size	.L.str.68, 9

	.type	.L.str.69,@object               // @.str.69
.L.str.69:
	.asciz	"freembuf"
	.size	.L.str.69, 9

	.type	.L.str.70,@object               // @.str.70
.L.str.70:
	.asciz	"memcpy"
	.size	.L.str.70, 7

	.type	.L.str.71,@object               // @.str.71
.L.str.71:
	.asciz	"memset"
	.size	.L.str.71, 7

	.type	prjm_eval_genrand_int32.mag01,@object // @prjm_eval_genrand_int32.mag01
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	2, 0x0
prjm_eval_genrand_int32.mag01:
	.word	0                               // 0x0
	.word	2567483615                      // 0x9908b0df
	.size	prjm_eval_genrand_int32.mag01, 8

	.type	__emutls_v.prjm_eval_genrand_int32.mt,@object // @__emutls_v.prjm_eval_genrand_int32.mt
	.section	.data.__emutls_v.prjm_eval_genrand_int32.mt,"aw",@progbits
	.p2align	3, 0x0
__emutls_v.prjm_eval_genrand_int32.mt:
	.xword	2496                            // 0x9c0
	.xword	4                               // 0x4
	.xword	0
	.xword	0
	.size	__emutls_v.prjm_eval_genrand_int32.mt, 32

	.type	__emutls_v.prjm_eval_genrand_int32.mti,@object // @__emutls_v.prjm_eval_genrand_int32.mti
	.section	.data.__emutls_v.prjm_eval_genrand_int32.mti,"aw",@progbits
	.p2align	3, 0x0
__emutls_v.prjm_eval_genrand_int32.mti:
	.xword	4                               // 0x4
	.xword	4                               // 0x4
	.xword	0
	.xword	0
	.size	__emutls_v.prjm_eval_genrand_int32.mti, 32

	.section	.debug_loc,"",@progbits
.Ldebug_loc0:
	.xword	-1
	.xword	.Lfunc_begin3                   //   base address
	.xword	.Lfunc_begin3-.Lfunc_begin3
	.xword	.Ltmp4-.Lfunc_begin3
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp4-.Lfunc_begin3
	.xword	.Ltmp7-.Lfunc_begin3
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp7-.Lfunc_begin3
	.xword	.Lfunc_end3-.Lfunc_begin3
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc1:
	.xword	-1
	.xword	.Lfunc_begin3                   //   base address
	.xword	.Lfunc_begin3-.Lfunc_begin3
	.xword	.Ltmp5-.Lfunc_begin3
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp5-.Lfunc_begin3
	.xword	.Ltmp16-.Lfunc_begin3
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp16-.Lfunc_begin3
	.xword	.Ltmp18-.Lfunc_begin3
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp18-.Lfunc_begin3
	.xword	.Lfunc_end3-.Lfunc_begin3
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc2:
	.xword	-1
	.xword	.Lfunc_begin3                   //   base address
	.xword	.Ltmp7-.Lfunc_begin3
	.xword	.Ltmp9-.Lfunc_begin3
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp10-.Lfunc_begin3
	.xword	.Ltmp14-.Lfunc_begin3
	.hword	2                               // Loc expr size
	.byte	143                             // DW_OP_breg31
	.byte	0                               // 0
	.xword	0
	.xword	0
.Ldebug_loc3:
	.xword	-1
	.xword	.Lfunc_begin3                   //   base address
	.xword	.Ltmp8-.Lfunc_begin3
	.xword	.Ltmp11-.Lfunc_begin3
	.hword	1                               // Loc expr size
	.byte	102                             // DW_OP_reg22
	.xword	.Ltmp12-.Lfunc_begin3
	.xword	.Ltmp17-.Lfunc_begin3
	.hword	1                               // Loc expr size
	.byte	102                             // DW_OP_reg22
	.xword	.Ltmp18-.Lfunc_begin3
	.xword	.Lfunc_end3-.Lfunc_begin3
	.hword	1                               // Loc expr size
	.byte	102                             // DW_OP_reg22
	.xword	0
	.xword	0
.Ldebug_loc4:
	.xword	-1
	.xword	.Lfunc_begin4                   //   base address
	.xword	.Lfunc_begin4-.Lfunc_begin4
	.xword	.Ltmp21-.Lfunc_begin4
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp21-.Lfunc_begin4
	.xword	.Ltmp32-.Lfunc_begin4
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp33-.Lfunc_begin4
	.xword	.Lfunc_end4-.Lfunc_begin4
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc5:
	.xword	-1
	.xword	.Lfunc_begin4                   //   base address
	.xword	.Lfunc_begin4-.Lfunc_begin4
	.xword	.Ltmp22-.Lfunc_begin4
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp22-.Lfunc_begin4
	.xword	.Ltmp32-.Lfunc_begin4
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp32-.Lfunc_begin4
	.xword	.Ltmp33-.Lfunc_begin4
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp33-.Lfunc_begin4
	.xword	.Lfunc_end4-.Lfunc_begin4
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc6:
	.xword	-1
	.xword	.Lfunc_begin4                   //   base address
	.xword	.Ltmp24-.Lfunc_begin4
	.xword	.Ltmp25-.Lfunc_begin4
	.hword	1                               // Loc expr size
	.byte	89                              // DW_OP_reg9
	.xword	.Ltmp25-.Lfunc_begin4
	.xword	.Ltmp26-.Lfunc_begin4
	.hword	1                               // Loc expr size
	.byte	103                             // DW_OP_reg23
	.xword	0
	.xword	0
.Ldebug_loc7:
	.xword	-1
	.xword	.Lfunc_begin4                   //   base address
	.xword	.Ltmp25-.Lfunc_begin4
	.xword	.Ltmp26-.Lfunc_begin4
	.hword	2                               // Loc expr size
	.byte	48                              // DW_OP_lit0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc8:
	.xword	-1
	.xword	.Lfunc_begin5                   //   base address
	.xword	.Lfunc_begin5-.Lfunc_begin5
	.xword	.Ltmp36-.Lfunc_begin5
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp36-.Lfunc_begin5
	.xword	.Ltmp44-.Lfunc_begin5
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp44-.Lfunc_begin5
	.xword	.Ltmp45-.Lfunc_begin5
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp45-.Lfunc_begin5
	.xword	.Lfunc_end5-.Lfunc_begin5
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc9:
	.xword	-1
	.xword	.Lfunc_begin5                   //   base address
	.xword	.Lfunc_begin5-.Lfunc_begin5
	.xword	.Ltmp35-.Lfunc_begin5
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp35-.Lfunc_begin5
	.xword	.Ltmp44-.Lfunc_begin5
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp44-.Lfunc_begin5
	.xword	.Ltmp45-.Lfunc_begin5
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp45-.Lfunc_begin5
	.xword	.Lfunc_end5-.Lfunc_begin5
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc10:
	.xword	-1
	.xword	.Lfunc_begin5                   //   base address
	.xword	.Ltmp37-.Lfunc_begin5
	.xword	.Ltmp38-.Lfunc_begin5
	.hword	5                               // Loc expr size
	.byte	16                              // DW_OP_constu
	.byte	128                             // 1048576
	.byte	128                             // 
	.byte	64                              // 
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp38-.Lfunc_begin5
	.xword	.Ltmp40-.Lfunc_begin5
	.hword	17                              // Loc expr size
	.byte	134                             // DW_OP_breg22
	.byte	0                               // 0
	.byte	17                              // DW_OP_consts
	.byte	129                             // -1048575
	.byte	128                             // 
	.byte	64                              // 
	.byte	28                              // DW_OP_minus
	.byte	17                              // DW_OP_consts
	.byte	127                             // -1
	.byte	30                              // DW_OP_mul
	.byte	17                              // DW_OP_consts
	.byte	128                             // 1048576
	.byte	128                             // 
	.byte	192                             // 
	.byte	0                               // 
	.byte	34                              // DW_OP_plus
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp40-.Lfunc_begin5
	.xword	.Ltmp41-.Lfunc_begin5
	.hword	16                              // Loc expr size
	.byte	134                             // DW_OP_breg22
	.byte	0                               // 0
	.byte	17                              // DW_OP_consts
	.byte	129                             // -1048575
	.byte	128                             // 
	.byte	64                              // 
	.byte	28                              // DW_OP_minus
	.byte	17                              // DW_OP_consts
	.byte	127                             // -1
	.byte	30                              // DW_OP_mul
	.byte	17                              // DW_OP_consts
	.byte	255                             // 1048575
	.byte	255                             // 
	.byte	63                              // 
	.byte	34                              // DW_OP_plus
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc11:
	.xword	-1
	.xword	.Lfunc_begin6                   //   base address
	.xword	.Lfunc_begin6-.Lfunc_begin6
	.xword	.Ltmp47-.Lfunc_begin6
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp47-.Lfunc_begin6
	.xword	.Ltmp56-.Lfunc_begin6
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp56-.Lfunc_begin6
	.xword	.Ltmp57-.Lfunc_begin6
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp57-.Lfunc_begin6
	.xword	.Lfunc_end6-.Lfunc_begin6
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc12:
	.xword	-1
	.xword	.Lfunc_begin6                   //   base address
	.xword	.Lfunc_begin6-.Lfunc_begin6
	.xword	.Ltmp48-.Lfunc_begin6
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp48-.Lfunc_begin6
	.xword	.Ltmp52-.Lfunc_begin6
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp52-.Lfunc_begin6
	.xword	.Ltmp54-.Lfunc_begin6
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	0
	.xword	0
.Ldebug_loc13:
	.xword	-1
	.xword	.Lfunc_begin7                   //   base address
	.xword	.Lfunc_begin7-.Lfunc_begin7
	.xword	.Ltmp59-.Lfunc_begin7
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp59-.Lfunc_begin7
	.xword	.Ltmp62-.Lfunc_begin7
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp62-.Lfunc_begin7
	.xword	.Lfunc_end7-.Lfunc_begin7
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc14:
	.xword	-1
	.xword	.Lfunc_begin7                   //   base address
	.xword	.Lfunc_begin7-.Lfunc_begin7
	.xword	.Ltmp60-.Lfunc_begin7
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp60-.Lfunc_begin7
	.xword	.Ltmp64-.Lfunc_begin7
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp64-.Lfunc_begin7
	.xword	.Ltmp65-.Lfunc_begin7
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	0
	.xword	0
.Ldebug_loc15:
	.xword	-1
	.xword	.Lfunc_begin8                   //   base address
	.xword	.Lfunc_begin8-.Lfunc_begin8
	.xword	.Ltmp69-.Lfunc_begin8
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp69-.Lfunc_begin8
	.xword	.Ltmp72-.Lfunc_begin8
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp72-.Lfunc_begin8
	.xword	.Lfunc_end8-.Lfunc_begin8
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc16:
	.xword	-1
	.xword	.Lfunc_begin8                   //   base address
	.xword	.Lfunc_begin8-.Lfunc_begin8
	.xword	.Ltmp70-.Lfunc_begin8
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp70-.Lfunc_begin8
	.xword	.Ltmp75-.Lfunc_begin8
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp75-.Lfunc_begin8
	.xword	.Ltmp76-.Lfunc_begin8
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	0
	.xword	0
.Ldebug_loc17:
	.xword	-1
	.xword	.Lfunc_begin9                   //   base address
	.xword	.Lfunc_begin9-.Lfunc_begin9
	.xword	.Ltmp80-.Lfunc_begin9
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp80-.Lfunc_begin9
	.xword	.Ltmp83-.Lfunc_begin9
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp83-.Lfunc_begin9
	.xword	.Lfunc_end9-.Lfunc_begin9
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc18:
	.xword	-1
	.xword	.Lfunc_begin9                   //   base address
	.xword	.Lfunc_begin9-.Lfunc_begin9
	.xword	.Ltmp81-.Lfunc_begin9
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp81-.Lfunc_begin9
	.xword	.Ltmp87-.Lfunc_begin9
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp87-.Lfunc_begin9
	.xword	.Ltmp88-.Lfunc_begin9
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp88-.Lfunc_begin9
	.xword	.Lfunc_end9-.Lfunc_begin9
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc19:
	.xword	-1
	.xword	.Lfunc_begin10                  //   base address
	.xword	.Lfunc_begin10-.Lfunc_begin10
	.xword	.Ltmp90-.Lfunc_begin10
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp90-.Lfunc_begin10
	.xword	.Ltmp93-.Lfunc_begin10
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp93-.Lfunc_begin10
	.xword	.Lfunc_end10-.Lfunc_begin10
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc20:
	.xword	-1
	.xword	.Lfunc_begin10                  //   base address
	.xword	.Lfunc_begin10-.Lfunc_begin10
	.xword	.Ltmp91-.Lfunc_begin10
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp91-.Lfunc_begin10
	.xword	.Ltmp99-.Lfunc_begin10
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp99-.Lfunc_begin10
	.xword	.Ltmp100-.Lfunc_begin10
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp100-.Lfunc_begin10
	.xword	.Lfunc_end10-.Lfunc_begin10
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc21:
	.xword	-1
	.xword	.Lfunc_begin10                  //   base address
	.xword	.Ltmp95-.Lfunc_begin10
	.xword	.Ltmp102-.Lfunc_begin10
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	0
	.xword	0
.Ldebug_loc22:
	.xword	-1
	.xword	.Lfunc_begin11                  //   base address
	.xword	.Lfunc_begin11-.Lfunc_begin11
	.xword	.Ltmp104-.Lfunc_begin11
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp104-.Lfunc_begin11
	.xword	.Ltmp107-.Lfunc_begin11
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp107-.Lfunc_begin11
	.xword	.Lfunc_end11-.Lfunc_begin11
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc23:
	.xword	-1
	.xword	.Lfunc_begin11                  //   base address
	.xword	.Lfunc_begin11-.Lfunc_begin11
	.xword	.Ltmp105-.Lfunc_begin11
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp105-.Lfunc_begin11
	.xword	.Ltmp107-.Lfunc_begin11
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp107-.Lfunc_begin11
	.xword	.Lfunc_end11-.Lfunc_begin11
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc24:
	.xword	-1
	.xword	.Lfunc_begin12                  //   base address
	.xword	.Lfunc_begin12-.Lfunc_begin12
	.xword	.Ltmp110-.Lfunc_begin12
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp110-.Lfunc_begin12
	.xword	.Ltmp113-.Lfunc_begin12
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp113-.Lfunc_begin12
	.xword	.Lfunc_end12-.Lfunc_begin12
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc25:
	.xword	-1
	.xword	.Lfunc_begin12                  //   base address
	.xword	.Lfunc_begin12-.Lfunc_begin12
	.xword	.Ltmp111-.Lfunc_begin12
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp111-.Lfunc_begin12
	.xword	.Ltmp119-.Lfunc_begin12
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp119-.Lfunc_begin12
	.xword	.Ltmp120-.Lfunc_begin12
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp120-.Lfunc_begin12
	.xword	.Lfunc_end12-.Lfunc_begin12
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc26:
	.xword	-1
	.xword	.Lfunc_begin13                  //   base address
	.xword	.Lfunc_begin13-.Lfunc_begin13
	.xword	.Ltmp122-.Lfunc_begin13
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp122-.Lfunc_begin13
	.xword	.Ltmp125-.Lfunc_begin13
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp125-.Lfunc_begin13
	.xword	.Lfunc_end13-.Lfunc_begin13
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc27:
	.xword	-1
	.xword	.Lfunc_begin13                  //   base address
	.xword	.Lfunc_begin13-.Lfunc_begin13
	.xword	.Ltmp123-.Lfunc_begin13
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp123-.Lfunc_begin13
	.xword	.Ltmp131-.Lfunc_begin13
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp131-.Lfunc_begin13
	.xword	.Ltmp132-.Lfunc_begin13
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp132-.Lfunc_begin13
	.xword	.Lfunc_end13-.Lfunc_begin13
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc28:
	.xword	-1
	.xword	.Lfunc_begin14                  //   base address
	.xword	.Lfunc_begin14-.Lfunc_begin14
	.xword	.Ltmp135-.Lfunc_begin14
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp135-.Lfunc_begin14
	.xword	.Lfunc_end14-.Lfunc_begin14
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc29:
	.xword	-1
	.xword	.Lfunc_begin14                  //   base address
	.xword	.Lfunc_begin14-.Lfunc_begin14
	.xword	.Ltmp134-.Lfunc_begin14
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp134-.Lfunc_begin14
	.xword	.Ltmp138-.Lfunc_begin14
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp138-.Lfunc_begin14
	.xword	.Ltmp139-.Lfunc_begin14
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp139-.Lfunc_begin14
	.xword	.Lfunc_end14-.Lfunc_begin14
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc30:
	.xword	-1
	.xword	.Lfunc_begin15                  //   base address
	.xword	.Lfunc_begin15-.Lfunc_begin15
	.xword	.Ltmp141-.Lfunc_begin15
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp141-.Lfunc_begin15
	.xword	.Ltmp147-.Lfunc_begin15
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp147-.Lfunc_begin15
	.xword	.Ltmp148-.Lfunc_begin15
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp148-.Lfunc_begin15
	.xword	.Lfunc_end15-.Lfunc_begin15
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc31:
	.xword	-1
	.xword	.Lfunc_begin15                  //   base address
	.xword	.Lfunc_begin15-.Lfunc_begin15
	.xword	.Ltmp142-.Lfunc_begin15
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp142-.Lfunc_begin15
	.xword	.Ltmp147-.Lfunc_begin15
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp147-.Lfunc_begin15
	.xword	.Ltmp148-.Lfunc_begin15
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp148-.Lfunc_begin15
	.xword	.Lfunc_end15-.Lfunc_begin15
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc32:
	.xword	-1
	.xword	.Lfunc_begin16                  //   base address
	.xword	.Lfunc_begin16-.Lfunc_begin16
	.xword	.Ltmp150-.Lfunc_begin16
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp150-.Lfunc_begin16
	.xword	.Ltmp156-.Lfunc_begin16
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp156-.Lfunc_begin16
	.xword	.Ltmp157-.Lfunc_begin16
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp157-.Lfunc_begin16
	.xword	.Lfunc_end16-.Lfunc_begin16
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc33:
	.xword	-1
	.xword	.Lfunc_begin16                  //   base address
	.xword	.Lfunc_begin16-.Lfunc_begin16
	.xword	.Ltmp151-.Lfunc_begin16
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp151-.Lfunc_begin16
	.xword	.Ltmp156-.Lfunc_begin16
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp156-.Lfunc_begin16
	.xword	.Ltmp157-.Lfunc_begin16
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp157-.Lfunc_begin16
	.xword	.Lfunc_end16-.Lfunc_begin16
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc34:
	.xword	-1
	.xword	.Lfunc_begin17                  //   base address
	.xword	.Lfunc_begin17-.Lfunc_begin17
	.xword	.Ltmp159-.Lfunc_begin17
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp159-.Lfunc_begin17
	.xword	.Ltmp165-.Lfunc_begin17
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp165-.Lfunc_begin17
	.xword	.Ltmp166-.Lfunc_begin17
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp166-.Lfunc_begin17
	.xword	.Lfunc_end17-.Lfunc_begin17
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc35:
	.xword	-1
	.xword	.Lfunc_begin17                  //   base address
	.xword	.Lfunc_begin17-.Lfunc_begin17
	.xword	.Ltmp160-.Lfunc_begin17
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp160-.Lfunc_begin17
	.xword	.Ltmp165-.Lfunc_begin17
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp165-.Lfunc_begin17
	.xword	.Ltmp166-.Lfunc_begin17
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp166-.Lfunc_begin17
	.xword	.Lfunc_end17-.Lfunc_begin17
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc36:
	.xword	-1
	.xword	.Lfunc_begin18                  //   base address
	.xword	.Lfunc_begin18-.Lfunc_begin18
	.xword	.Ltmp168-.Lfunc_begin18
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp168-.Lfunc_begin18
	.xword	.Ltmp174-.Lfunc_begin18
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp174-.Lfunc_begin18
	.xword	.Ltmp175-.Lfunc_begin18
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp175-.Lfunc_begin18
	.xword	.Lfunc_end18-.Lfunc_begin18
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc37:
	.xword	-1
	.xword	.Lfunc_begin18                  //   base address
	.xword	.Lfunc_begin18-.Lfunc_begin18
	.xword	.Ltmp169-.Lfunc_begin18
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp169-.Lfunc_begin18
	.xword	.Ltmp174-.Lfunc_begin18
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp174-.Lfunc_begin18
	.xword	.Ltmp175-.Lfunc_begin18
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp175-.Lfunc_begin18
	.xword	.Lfunc_end18-.Lfunc_begin18
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc38:
	.xword	-1
	.xword	.Lfunc_begin19                  //   base address
	.xword	.Lfunc_begin19-.Lfunc_begin19
	.xword	.Ltmp177-.Lfunc_begin19
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp177-.Lfunc_begin19
	.xword	.Ltmp183-.Lfunc_begin19
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp183-.Lfunc_begin19
	.xword	.Ltmp184-.Lfunc_begin19
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp184-.Lfunc_begin19
	.xword	.Lfunc_end19-.Lfunc_begin19
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc39:
	.xword	-1
	.xword	.Lfunc_begin19                  //   base address
	.xword	.Lfunc_begin19-.Lfunc_begin19
	.xword	.Ltmp178-.Lfunc_begin19
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp178-.Lfunc_begin19
	.xword	.Ltmp183-.Lfunc_begin19
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp183-.Lfunc_begin19
	.xword	.Ltmp184-.Lfunc_begin19
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp184-.Lfunc_begin19
	.xword	.Lfunc_end19-.Lfunc_begin19
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc40:
	.xword	-1
	.xword	.Lfunc_begin20                  //   base address
	.xword	.Lfunc_begin20-.Lfunc_begin20
	.xword	.Ltmp186-.Lfunc_begin20
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp186-.Lfunc_begin20
	.xword	.Ltmp192-.Lfunc_begin20
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp192-.Lfunc_begin20
	.xword	.Ltmp193-.Lfunc_begin20
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp193-.Lfunc_begin20
	.xword	.Lfunc_end20-.Lfunc_begin20
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc41:
	.xword	-1
	.xword	.Lfunc_begin20                  //   base address
	.xword	.Lfunc_begin20-.Lfunc_begin20
	.xword	.Ltmp187-.Lfunc_begin20
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp187-.Lfunc_begin20
	.xword	.Ltmp192-.Lfunc_begin20
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp192-.Lfunc_begin20
	.xword	.Ltmp193-.Lfunc_begin20
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp193-.Lfunc_begin20
	.xword	.Lfunc_end20-.Lfunc_begin20
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc42:
	.xword	-1
	.xword	.Lfunc_begin21                  //   base address
	.xword	.Lfunc_begin21-.Lfunc_begin21
	.xword	.Ltmp195-.Lfunc_begin21
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp195-.Lfunc_begin21
	.xword	.Ltmp201-.Lfunc_begin21
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp201-.Lfunc_begin21
	.xword	.Ltmp202-.Lfunc_begin21
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp202-.Lfunc_begin21
	.xword	.Lfunc_end21-.Lfunc_begin21
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc43:
	.xword	-1
	.xword	.Lfunc_begin21                  //   base address
	.xword	.Lfunc_begin21-.Lfunc_begin21
	.xword	.Ltmp196-.Lfunc_begin21
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp196-.Lfunc_begin21
	.xword	.Ltmp201-.Lfunc_begin21
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp201-.Lfunc_begin21
	.xword	.Ltmp202-.Lfunc_begin21
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp202-.Lfunc_begin21
	.xword	.Lfunc_end21-.Lfunc_begin21
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc44:
	.xword	-1
	.xword	.Lfunc_begin22                  //   base address
	.xword	.Lfunc_begin22-.Lfunc_begin22
	.xword	.Ltmp204-.Lfunc_begin22
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp204-.Lfunc_begin22
	.xword	.Ltmp210-.Lfunc_begin22
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp210-.Lfunc_begin22
	.xword	.Ltmp211-.Lfunc_begin22
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp211-.Lfunc_begin22
	.xword	.Lfunc_end22-.Lfunc_begin22
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc45:
	.xword	-1
	.xword	.Lfunc_begin22                  //   base address
	.xword	.Lfunc_begin22-.Lfunc_begin22
	.xword	.Ltmp205-.Lfunc_begin22
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp205-.Lfunc_begin22
	.xword	.Ltmp210-.Lfunc_begin22
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp210-.Lfunc_begin22
	.xword	.Ltmp211-.Lfunc_begin22
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp211-.Lfunc_begin22
	.xword	.Lfunc_end22-.Lfunc_begin22
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc46:
	.xword	-1
	.xword	.Lfunc_begin23                  //   base address
	.xword	.Lfunc_begin23-.Lfunc_begin23
	.xword	.Ltmp213-.Lfunc_begin23
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp213-.Lfunc_begin23
	.xword	.Ltmp219-.Lfunc_begin23
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp219-.Lfunc_begin23
	.xword	.Ltmp220-.Lfunc_begin23
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp220-.Lfunc_begin23
	.xword	.Lfunc_end23-.Lfunc_begin23
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc47:
	.xword	-1
	.xword	.Lfunc_begin23                  //   base address
	.xword	.Lfunc_begin23-.Lfunc_begin23
	.xword	.Ltmp214-.Lfunc_begin23
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp214-.Lfunc_begin23
	.xword	.Ltmp219-.Lfunc_begin23
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp219-.Lfunc_begin23
	.xword	.Ltmp220-.Lfunc_begin23
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp220-.Lfunc_begin23
	.xword	.Lfunc_end23-.Lfunc_begin23
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc48:
	.xword	-1
	.xword	.Lfunc_begin24                  //   base address
	.xword	.Lfunc_begin24-.Lfunc_begin24
	.xword	.Ltmp222-.Lfunc_begin24
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp222-.Lfunc_begin24
	.xword	.Ltmp231-.Lfunc_begin24
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp231-.Lfunc_begin24
	.xword	.Ltmp232-.Lfunc_begin24
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp232-.Lfunc_begin24
	.xword	.Lfunc_end24-.Lfunc_begin24
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc49:
	.xword	-1
	.xword	.Lfunc_begin24                  //   base address
	.xword	.Lfunc_begin24-.Lfunc_begin24
	.xword	.Ltmp223-.Lfunc_begin24
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp223-.Lfunc_begin24
	.xword	.Ltmp231-.Lfunc_begin24
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp231-.Lfunc_begin24
	.xword	.Ltmp232-.Lfunc_begin24
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp232-.Lfunc_begin24
	.xword	.Lfunc_end24-.Lfunc_begin24
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc50:
	.xword	-1
	.xword	.Lfunc_begin25                  //   base address
	.xword	.Lfunc_begin25-.Lfunc_begin25
	.xword	.Ltmp234-.Lfunc_begin25
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp234-.Lfunc_begin25
	.xword	.Ltmp265-.Lfunc_begin25
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp265-.Lfunc_begin25
	.xword	.Ltmp266-.Lfunc_begin25
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp266-.Lfunc_begin25
	.xword	.Lfunc_end25-.Lfunc_begin25
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc51:
	.xword	-1
	.xword	.Lfunc_begin25                  //   base address
	.xword	.Lfunc_begin25-.Lfunc_begin25
	.xword	.Ltmp235-.Lfunc_begin25
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp235-.Lfunc_begin25
	.xword	.Ltmp265-.Lfunc_begin25
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp265-.Lfunc_begin25
	.xword	.Ltmp266-.Lfunc_begin25
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp266-.Lfunc_begin25
	.xword	.Lfunc_end25-.Lfunc_begin25
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc52:
	.xword	-1
	.xword	.Lfunc_begin25                  //   base address
	.xword	.Ltmp244-.Lfunc_begin25
	.xword	.Ltmp263-.Lfunc_begin25
	.hword	2                               // Loc expr size
	.byte	144                             // DW_OP_regx
	.byte	66                              // 66
	.xword	0
	.xword	0
.Ldebug_loc53:
	.xword	-1
	.xword	.Lfunc_begin25                  //   base address
	.xword	.Ltmp244-.Lfunc_begin25
	.xword	.Ltmp256-.Lfunc_begin25
	.hword	1                               // Loc expr size
	.byte	91                              // DW_OP_reg11
	.xword	0
	.xword	0
.Ldebug_loc54:
	.xword	-1
	.xword	.Lfunc_begin25                  //   base address
	.xword	.Ltmp245-.Lfunc_begin25
	.xword	.Ltmp259-.Lfunc_begin25
	.hword	1                               // Loc expr size
	.byte	89                              // DW_OP_reg9
	.xword	0
	.xword	0
.Ldebug_loc55:
	.xword	-1
	.xword	.Lfunc_begin25                  //   base address
	.xword	.Ltmp241-.Lfunc_begin25
	.xword	.Ltmp260-.Lfunc_begin25
	.hword	1                               // Loc expr size
	.byte	88                              // DW_OP_reg8
	.xword	0
	.xword	0
.Ldebug_loc56:
	.xword	-1
	.xword	.Lfunc_begin25                  //   base address
	.xword	.Ltmp256-.Lfunc_begin25
	.xword	.Ltmp263-.Lfunc_begin25
	.hword	1                               // Loc expr size
	.byte	91                              // DW_OP_reg11
	.xword	0
	.xword	0
.Ldebug_loc57:
	.xword	-1
	.xword	.Lfunc_begin25                  //   base address
	.xword	.Ltmp254-.Lfunc_begin25
	.xword	.Ltmp263-.Lfunc_begin25
	.hword	12                              // Loc expr size
	.byte	16                              // DW_OP_constu
	.byte	128                             // 9223372036854775808
	.byte	128                             // 
	.byte	128                             // 
	.byte	128                             // 
	.byte	128                             // 
	.byte	128                             // 
	.byte	128                             // 
	.byte	128                             // 
	.byte	128                             // 
	.byte	1                               // 
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc58:
	.xword	-1
	.xword	.Lfunc_begin25                  //   base address
	.xword	.Ltmp254-.Lfunc_begin25
	.xword	.Ltmp261-.Lfunc_begin25
	.hword	1                               // Loc expr size
	.byte	90                              // DW_OP_reg10
	.xword	0
	.xword	0
.Ldebug_loc59:
	.xword	-1
	.xword	.Lfunc_begin25                  //   base address
	.xword	.Ltmp262-.Lfunc_begin25
	.xword	.Ltmp263-.Lfunc_begin25
	.hword	2                               // Loc expr size
	.byte	144                             // DW_OP_regx
	.byte	64                              // 64
	.xword	0
	.xword	0
.Ldebug_loc60:
	.xword	-1
	.xword	.Lfunc_begin26                  //   base address
	.xword	.Lfunc_begin26-.Lfunc_begin26
	.xword	.Ltmp268-.Lfunc_begin26
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp268-.Lfunc_begin26
	.xword	.Ltmp278-.Lfunc_begin26
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp278-.Lfunc_begin26
	.xword	.Ltmp279-.Lfunc_begin26
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp279-.Lfunc_begin26
	.xword	.Lfunc_end26-.Lfunc_begin26
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc61:
	.xword	-1
	.xword	.Lfunc_begin26                  //   base address
	.xword	.Lfunc_begin26-.Lfunc_begin26
	.xword	.Ltmp269-.Lfunc_begin26
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp269-.Lfunc_begin26
	.xword	.Ltmp278-.Lfunc_begin26
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp278-.Lfunc_begin26
	.xword	.Ltmp279-.Lfunc_begin26
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp279-.Lfunc_begin26
	.xword	.Lfunc_end26-.Lfunc_begin26
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc62:
	.xword	-1
	.xword	.Lfunc_begin27                  //   base address
	.xword	.Lfunc_begin27-.Lfunc_begin27
	.xword	.Ltmp281-.Lfunc_begin27
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp281-.Lfunc_begin27
	.xword	.Ltmp291-.Lfunc_begin27
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp291-.Lfunc_begin27
	.xword	.Ltmp292-.Lfunc_begin27
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp292-.Lfunc_begin27
	.xword	.Lfunc_end27-.Lfunc_begin27
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc63:
	.xword	-1
	.xword	.Lfunc_begin27                  //   base address
	.xword	.Lfunc_begin27-.Lfunc_begin27
	.xword	.Ltmp282-.Lfunc_begin27
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp282-.Lfunc_begin27
	.xword	.Ltmp291-.Lfunc_begin27
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp291-.Lfunc_begin27
	.xword	.Ltmp292-.Lfunc_begin27
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp292-.Lfunc_begin27
	.xword	.Lfunc_end27-.Lfunc_begin27
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc64:
	.xword	-1
	.xword	.Lfunc_begin28                  //   base address
	.xword	.Lfunc_begin28-.Lfunc_begin28
	.xword	.Ltmp294-.Lfunc_begin28
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp294-.Lfunc_begin28
	.xword	.Ltmp302-.Lfunc_begin28
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp302-.Lfunc_begin28
	.xword	.Ltmp303-.Lfunc_begin28
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp303-.Lfunc_begin28
	.xword	.Lfunc_end28-.Lfunc_begin28
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc65:
	.xword	-1
	.xword	.Lfunc_begin28                  //   base address
	.xword	.Lfunc_begin28-.Lfunc_begin28
	.xword	.Ltmp295-.Lfunc_begin28
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp295-.Lfunc_begin28
	.xword	.Ltmp302-.Lfunc_begin28
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp302-.Lfunc_begin28
	.xword	.Ltmp303-.Lfunc_begin28
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp303-.Lfunc_begin28
	.xword	.Lfunc_end28-.Lfunc_begin28
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc66:
	.xword	-1
	.xword	.Lfunc_begin29                  //   base address
	.xword	.Lfunc_begin29-.Lfunc_begin29
	.xword	.Ltmp305-.Lfunc_begin29
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp305-.Lfunc_begin29
	.xword	.Ltmp313-.Lfunc_begin29
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp313-.Lfunc_begin29
	.xword	.Ltmp314-.Lfunc_begin29
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp314-.Lfunc_begin29
	.xword	.Lfunc_end29-.Lfunc_begin29
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc67:
	.xword	-1
	.xword	.Lfunc_begin29                  //   base address
	.xword	.Lfunc_begin29-.Lfunc_begin29
	.xword	.Ltmp306-.Lfunc_begin29
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp306-.Lfunc_begin29
	.xword	.Ltmp313-.Lfunc_begin29
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp313-.Lfunc_begin29
	.xword	.Ltmp314-.Lfunc_begin29
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp314-.Lfunc_begin29
	.xword	.Lfunc_end29-.Lfunc_begin29
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc68:
	.xword	-1
	.xword	.Lfunc_begin30                  //   base address
	.xword	.Lfunc_begin30-.Lfunc_begin30
	.xword	.Ltmp317-.Lfunc_begin30
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp317-.Lfunc_begin30
	.xword	.Lfunc_end30-.Lfunc_begin30
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc69:
	.xword	-1
	.xword	.Lfunc_begin30                  //   base address
	.xword	.Lfunc_begin30-.Lfunc_begin30
	.xword	.Ltmp316-.Lfunc_begin30
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp316-.Lfunc_begin30
	.xword	.Ltmp320-.Lfunc_begin30
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp320-.Lfunc_begin30
	.xword	.Ltmp321-.Lfunc_begin30
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp321-.Lfunc_begin30
	.xword	.Lfunc_end30-.Lfunc_begin30
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc70:
	.xword	-1
	.xword	.Lfunc_begin31                  //   base address
	.xword	.Lfunc_begin31-.Lfunc_begin31
	.xword	.Ltmp323-.Lfunc_begin31
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp323-.Lfunc_begin31
	.xword	.Ltmp329-.Lfunc_begin31
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp329-.Lfunc_begin31
	.xword	.Ltmp330-.Lfunc_begin31
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp330-.Lfunc_begin31
	.xword	.Lfunc_end31-.Lfunc_begin31
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc71:
	.xword	-1
	.xword	.Lfunc_begin31                  //   base address
	.xword	.Lfunc_begin31-.Lfunc_begin31
	.xword	.Ltmp324-.Lfunc_begin31
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp324-.Lfunc_begin31
	.xword	.Ltmp329-.Lfunc_begin31
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp329-.Lfunc_begin31
	.xword	.Ltmp330-.Lfunc_begin31
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp330-.Lfunc_begin31
	.xword	.Lfunc_end31-.Lfunc_begin31
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc72:
	.xword	-1
	.xword	.Lfunc_begin32                  //   base address
	.xword	.Lfunc_begin32-.Lfunc_begin32
	.xword	.Ltmp332-.Lfunc_begin32
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp332-.Lfunc_begin32
	.xword	.Ltmp338-.Lfunc_begin32
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp338-.Lfunc_begin32
	.xword	.Ltmp339-.Lfunc_begin32
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp339-.Lfunc_begin32
	.xword	.Lfunc_end32-.Lfunc_begin32
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc73:
	.xword	-1
	.xword	.Lfunc_begin32                  //   base address
	.xword	.Lfunc_begin32-.Lfunc_begin32
	.xword	.Ltmp333-.Lfunc_begin32
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp333-.Lfunc_begin32
	.xword	.Ltmp338-.Lfunc_begin32
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp338-.Lfunc_begin32
	.xword	.Ltmp339-.Lfunc_begin32
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp339-.Lfunc_begin32
	.xword	.Lfunc_end32-.Lfunc_begin32
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc74:
	.xword	-1
	.xword	.Lfunc_begin33                  //   base address
	.xword	.Lfunc_begin33-.Lfunc_begin33
	.xword	.Ltmp341-.Lfunc_begin33
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp341-.Lfunc_begin33
	.xword	.Ltmp347-.Lfunc_begin33
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp347-.Lfunc_begin33
	.xword	.Ltmp348-.Lfunc_begin33
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp348-.Lfunc_begin33
	.xword	.Lfunc_end33-.Lfunc_begin33
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc75:
	.xword	-1
	.xword	.Lfunc_begin33                  //   base address
	.xword	.Lfunc_begin33-.Lfunc_begin33
	.xword	.Ltmp342-.Lfunc_begin33
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp342-.Lfunc_begin33
	.xword	.Ltmp347-.Lfunc_begin33
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp347-.Lfunc_begin33
	.xword	.Ltmp348-.Lfunc_begin33
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp348-.Lfunc_begin33
	.xword	.Lfunc_end33-.Lfunc_begin33
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc76:
	.xword	-1
	.xword	.Lfunc_begin34                  //   base address
	.xword	.Lfunc_begin34-.Lfunc_begin34
	.xword	.Ltmp350-.Lfunc_begin34
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp350-.Lfunc_begin34
	.xword	.Ltmp361-.Lfunc_begin34
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp361-.Lfunc_begin34
	.xword	.Ltmp362-.Lfunc_begin34
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp362-.Lfunc_begin34
	.xword	.Lfunc_end34-.Lfunc_begin34
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc77:
	.xword	-1
	.xword	.Lfunc_begin34                  //   base address
	.xword	.Lfunc_begin34-.Lfunc_begin34
	.xword	.Ltmp351-.Lfunc_begin34
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp351-.Lfunc_begin34
	.xword	.Ltmp361-.Lfunc_begin34
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp361-.Lfunc_begin34
	.xword	.Ltmp362-.Lfunc_begin34
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp362-.Lfunc_begin34
	.xword	.Lfunc_end34-.Lfunc_begin34
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc78:
	.xword	-1
	.xword	.Lfunc_begin35                  //   base address
	.xword	.Lfunc_begin35-.Lfunc_begin35
	.xword	.Ltmp364-.Lfunc_begin35
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp364-.Lfunc_begin35
	.xword	.Ltmp370-.Lfunc_begin35
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp370-.Lfunc_begin35
	.xword	.Ltmp371-.Lfunc_begin35
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp371-.Lfunc_begin35
	.xword	.Lfunc_end35-.Lfunc_begin35
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc79:
	.xword	-1
	.xword	.Lfunc_begin35                  //   base address
	.xword	.Lfunc_begin35-.Lfunc_begin35
	.xword	.Ltmp365-.Lfunc_begin35
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp365-.Lfunc_begin35
	.xword	.Ltmp370-.Lfunc_begin35
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp370-.Lfunc_begin35
	.xword	.Ltmp371-.Lfunc_begin35
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp371-.Lfunc_begin35
	.xword	.Lfunc_end35-.Lfunc_begin35
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc80:
	.xword	-1
	.xword	.Lfunc_begin36                  //   base address
	.xword	.Lfunc_begin36-.Lfunc_begin36
	.xword	.Ltmp373-.Lfunc_begin36
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp373-.Lfunc_begin36
	.xword	.Ltmp379-.Lfunc_begin36
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp379-.Lfunc_begin36
	.xword	.Ltmp380-.Lfunc_begin36
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp380-.Lfunc_begin36
	.xword	.Lfunc_end36-.Lfunc_begin36
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc81:
	.xword	-1
	.xword	.Lfunc_begin36                  //   base address
	.xword	.Lfunc_begin36-.Lfunc_begin36
	.xword	.Ltmp374-.Lfunc_begin36
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp374-.Lfunc_begin36
	.xword	.Ltmp379-.Lfunc_begin36
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp379-.Lfunc_begin36
	.xword	.Ltmp380-.Lfunc_begin36
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp380-.Lfunc_begin36
	.xword	.Lfunc_end36-.Lfunc_begin36
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc82:
	.xword	-1
	.xword	.Lfunc_begin37                  //   base address
	.xword	.Lfunc_begin37-.Lfunc_begin37
	.xword	.Ltmp382-.Lfunc_begin37
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp382-.Lfunc_begin37
	.xword	.Ltmp388-.Lfunc_begin37
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp388-.Lfunc_begin37
	.xword	.Ltmp389-.Lfunc_begin37
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp389-.Lfunc_begin37
	.xword	.Lfunc_end37-.Lfunc_begin37
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc83:
	.xword	-1
	.xword	.Lfunc_begin37                  //   base address
	.xword	.Lfunc_begin37-.Lfunc_begin37
	.xword	.Ltmp383-.Lfunc_begin37
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp383-.Lfunc_begin37
	.xword	.Ltmp388-.Lfunc_begin37
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp388-.Lfunc_begin37
	.xword	.Ltmp389-.Lfunc_begin37
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp389-.Lfunc_begin37
	.xword	.Lfunc_end37-.Lfunc_begin37
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc84:
	.xword	-1
	.xword	.Lfunc_begin38                  //   base address
	.xword	.Lfunc_begin38-.Lfunc_begin38
	.xword	.Ltmp391-.Lfunc_begin38
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp391-.Lfunc_begin38
	.xword	.Ltmp397-.Lfunc_begin38
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp397-.Lfunc_begin38
	.xword	.Ltmp398-.Lfunc_begin38
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp398-.Lfunc_begin38
	.xword	.Lfunc_end38-.Lfunc_begin38
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc85:
	.xword	-1
	.xword	.Lfunc_begin38                  //   base address
	.xword	.Lfunc_begin38-.Lfunc_begin38
	.xword	.Ltmp392-.Lfunc_begin38
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp392-.Lfunc_begin38
	.xword	.Ltmp397-.Lfunc_begin38
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp397-.Lfunc_begin38
	.xword	.Ltmp398-.Lfunc_begin38
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp398-.Lfunc_begin38
	.xword	.Lfunc_end38-.Lfunc_begin38
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc86:
	.xword	-1
	.xword	.Lfunc_begin39                  //   base address
	.xword	.Lfunc_begin39-.Lfunc_begin39
	.xword	.Ltmp400-.Lfunc_begin39
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp400-.Lfunc_begin39
	.xword	.Ltmp431-.Lfunc_begin39
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp431-.Lfunc_begin39
	.xword	.Ltmp432-.Lfunc_begin39
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp432-.Lfunc_begin39
	.xword	.Lfunc_end39-.Lfunc_begin39
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc87:
	.xword	-1
	.xword	.Lfunc_begin39                  //   base address
	.xword	.Lfunc_begin39-.Lfunc_begin39
	.xword	.Ltmp401-.Lfunc_begin39
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp401-.Lfunc_begin39
	.xword	.Ltmp431-.Lfunc_begin39
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp431-.Lfunc_begin39
	.xword	.Ltmp432-.Lfunc_begin39
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp432-.Lfunc_begin39
	.xword	.Lfunc_end39-.Lfunc_begin39
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc88:
	.xword	-1
	.xword	.Lfunc_begin39                  //   base address
	.xword	.Ltmp410-.Lfunc_begin39
	.xword	.Ltmp429-.Lfunc_begin39
	.hword	2                               // Loc expr size
	.byte	144                             // DW_OP_regx
	.byte	66                              // 66
	.xword	0
	.xword	0
.Ldebug_loc89:
	.xword	-1
	.xword	.Lfunc_begin39                  //   base address
	.xword	.Ltmp410-.Lfunc_begin39
	.xword	.Ltmp422-.Lfunc_begin39
	.hword	1                               // Loc expr size
	.byte	92                              // DW_OP_reg12
	.xword	0
	.xword	0
.Ldebug_loc90:
	.xword	-1
	.xword	.Lfunc_begin39                  //   base address
	.xword	.Ltmp411-.Lfunc_begin39
	.xword	.Ltmp425-.Lfunc_begin39
	.hword	1                               // Loc expr size
	.byte	90                              // DW_OP_reg10
	.xword	0
	.xword	0
.Ldebug_loc91:
	.xword	-1
	.xword	.Lfunc_begin39                  //   base address
	.xword	.Ltmp407-.Lfunc_begin39
	.xword	.Ltmp426-.Lfunc_begin39
	.hword	1                               // Loc expr size
	.byte	89                              // DW_OP_reg9
	.xword	0
	.xword	0
.Ldebug_loc92:
	.xword	-1
	.xword	.Lfunc_begin39                  //   base address
	.xword	.Ltmp422-.Lfunc_begin39
	.xword	.Ltmp429-.Lfunc_begin39
	.hword	1                               // Loc expr size
	.byte	92                              // DW_OP_reg12
	.xword	0
	.xword	0
.Ldebug_loc93:
	.xword	-1
	.xword	.Lfunc_begin39                  //   base address
	.xword	.Ltmp420-.Lfunc_begin39
	.xword	.Ltmp429-.Lfunc_begin39
	.hword	12                              // Loc expr size
	.byte	16                              // DW_OP_constu
	.byte	128                             // 9223372036854775808
	.byte	128                             // 
	.byte	128                             // 
	.byte	128                             // 
	.byte	128                             // 
	.byte	128                             // 
	.byte	128                             // 
	.byte	128                             // 
	.byte	128                             // 
	.byte	1                               // 
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc94:
	.xword	-1
	.xword	.Lfunc_begin39                  //   base address
	.xword	.Ltmp420-.Lfunc_begin39
	.xword	.Ltmp427-.Lfunc_begin39
	.hword	1                               // Loc expr size
	.byte	91                              // DW_OP_reg11
	.xword	0
	.xword	0
.Ldebug_loc95:
	.xword	-1
	.xword	.Lfunc_begin39                  //   base address
	.xword	.Ltmp428-.Lfunc_begin39
	.xword	.Ltmp429-.Lfunc_begin39
	.hword	2                               // Loc expr size
	.byte	144                             // DW_OP_regx
	.byte	64                              // 64
	.xword	0
	.xword	0
.Ldebug_loc96:
	.xword	-1
	.xword	.Lfunc_begin40                  //   base address
	.xword	.Lfunc_begin40-.Lfunc_begin40
	.xword	.Ltmp434-.Lfunc_begin40
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp434-.Lfunc_begin40
	.xword	.Ltmp445-.Lfunc_begin40
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp445-.Lfunc_begin40
	.xword	.Ltmp446-.Lfunc_begin40
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp446-.Lfunc_begin40
	.xword	.Lfunc_end40-.Lfunc_begin40
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc97:
	.xword	-1
	.xword	.Lfunc_begin40                  //   base address
	.xword	.Lfunc_begin40-.Lfunc_begin40
	.xword	.Ltmp435-.Lfunc_begin40
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp435-.Lfunc_begin40
	.xword	.Ltmp440-.Lfunc_begin40
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp440-.Lfunc_begin40
	.xword	.Lfunc_end40-.Lfunc_begin40
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc98:
	.xword	-1
	.xword	.Lfunc_begin41                  //   base address
	.xword	.Lfunc_begin41-.Lfunc_begin41
	.xword	.Ltmp449-.Lfunc_begin41
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp449-.Lfunc_begin41
	.xword	.Lfunc_end41-.Lfunc_begin41
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc99:
	.xword	-1
	.xword	.Lfunc_begin41                  //   base address
	.xword	.Lfunc_begin41-.Lfunc_begin41
	.xword	.Ltmp448-.Lfunc_begin41
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp448-.Lfunc_begin41
	.xword	.Ltmp453-.Lfunc_begin41
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp453-.Lfunc_begin41
	.xword	.Ltmp454-.Lfunc_begin41
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp454-.Lfunc_begin41
	.xword	.Lfunc_end41-.Lfunc_begin41
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc100:
	.xword	-1
	.xword	.Lfunc_begin42                  //   base address
	.xword	.Lfunc_begin42-.Lfunc_begin42
	.xword	.Ltmp457-.Lfunc_begin42
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp457-.Lfunc_begin42
	.xword	.Lfunc_end42-.Lfunc_begin42
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc101:
	.xword	-1
	.xword	.Lfunc_begin42                  //   base address
	.xword	.Lfunc_begin42-.Lfunc_begin42
	.xword	.Ltmp456-.Lfunc_begin42
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp456-.Lfunc_begin42
	.xword	.Ltmp461-.Lfunc_begin42
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp461-.Lfunc_begin42
	.xword	.Ltmp462-.Lfunc_begin42
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp462-.Lfunc_begin42
	.xword	.Lfunc_end42-.Lfunc_begin42
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc102:
	.xword	-1
	.xword	.Lfunc_begin43                  //   base address
	.xword	.Lfunc_begin43-.Lfunc_begin43
	.xword	.Ltmp465-.Lfunc_begin43
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp465-.Lfunc_begin43
	.xword	.Lfunc_end43-.Lfunc_begin43
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc103:
	.xword	-1
	.xword	.Lfunc_begin43                  //   base address
	.xword	.Lfunc_begin43-.Lfunc_begin43
	.xword	.Ltmp464-.Lfunc_begin43
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp464-.Lfunc_begin43
	.xword	.Ltmp469-.Lfunc_begin43
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp469-.Lfunc_begin43
	.xword	.Ltmp470-.Lfunc_begin43
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp470-.Lfunc_begin43
	.xword	.Lfunc_end43-.Lfunc_begin43
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc104:
	.xword	-1
	.xword	.Lfunc_begin44                  //   base address
	.xword	.Lfunc_begin44-.Lfunc_begin44
	.xword	.Ltmp473-.Lfunc_begin44
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp473-.Lfunc_begin44
	.xword	.Lfunc_end44-.Lfunc_begin44
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc105:
	.xword	-1
	.xword	.Lfunc_begin44                  //   base address
	.xword	.Lfunc_begin44-.Lfunc_begin44
	.xword	.Ltmp472-.Lfunc_begin44
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp472-.Lfunc_begin44
	.xword	.Ltmp478-.Lfunc_begin44
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp478-.Lfunc_begin44
	.xword	.Ltmp479-.Lfunc_begin44
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp479-.Lfunc_begin44
	.xword	.Lfunc_end44-.Lfunc_begin44
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc106:
	.xword	-1
	.xword	.Lfunc_begin45                  //   base address
	.xword	.Lfunc_begin45-.Lfunc_begin45
	.xword	.Ltmp482-.Lfunc_begin45
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp482-.Lfunc_begin45
	.xword	.Lfunc_end45-.Lfunc_begin45
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc107:
	.xword	-1
	.xword	.Lfunc_begin45                  //   base address
	.xword	.Lfunc_begin45-.Lfunc_begin45
	.xword	.Ltmp481-.Lfunc_begin45
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp481-.Lfunc_begin45
	.xword	.Ltmp487-.Lfunc_begin45
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp487-.Lfunc_begin45
	.xword	.Ltmp488-.Lfunc_begin45
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp488-.Lfunc_begin45
	.xword	.Lfunc_end45-.Lfunc_begin45
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc108:
	.xword	-1
	.xword	.Lfunc_begin46                  //   base address
	.xword	.Lfunc_begin46-.Lfunc_begin46
	.xword	.Ltmp491-.Lfunc_begin46
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp491-.Lfunc_begin46
	.xword	.Lfunc_end46-.Lfunc_begin46
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc109:
	.xword	-1
	.xword	.Lfunc_begin46                  //   base address
	.xword	.Lfunc_begin46-.Lfunc_begin46
	.xword	.Ltmp490-.Lfunc_begin46
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp490-.Lfunc_begin46
	.xword	.Ltmp495-.Lfunc_begin46
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp495-.Lfunc_begin46
	.xword	.Ltmp496-.Lfunc_begin46
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp496-.Lfunc_begin46
	.xword	.Lfunc_end46-.Lfunc_begin46
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc110:
	.xword	-1
	.xword	.Lfunc_begin47                  //   base address
	.xword	.Lfunc_begin47-.Lfunc_begin47
	.xword	.Ltmp498-.Lfunc_begin47
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp498-.Lfunc_begin47
	.xword	.Ltmp505-.Lfunc_begin47
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp505-.Lfunc_begin47
	.xword	.Ltmp506-.Lfunc_begin47
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp506-.Lfunc_begin47
	.xword	.Lfunc_end47-.Lfunc_begin47
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc111:
	.xword	-1
	.xword	.Lfunc_begin47                  //   base address
	.xword	.Lfunc_begin47-.Lfunc_begin47
	.xword	.Ltmp499-.Lfunc_begin47
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp499-.Lfunc_begin47
	.xword	.Ltmp505-.Lfunc_begin47
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp505-.Lfunc_begin47
	.xword	.Ltmp506-.Lfunc_begin47
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp506-.Lfunc_begin47
	.xword	.Lfunc_end47-.Lfunc_begin47
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc112:
	.xword	-1
	.xword	.Lfunc_begin48                  //   base address
	.xword	.Lfunc_begin48-.Lfunc_begin48
	.xword	.Ltmp509-.Lfunc_begin48
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp509-.Lfunc_begin48
	.xword	.Lfunc_end48-.Lfunc_begin48
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc113:
	.xword	-1
	.xword	.Lfunc_begin48                  //   base address
	.xword	.Lfunc_begin48-.Lfunc_begin48
	.xword	.Ltmp508-.Lfunc_begin48
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp508-.Lfunc_begin48
	.xword	.Ltmp512-.Lfunc_begin48
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp512-.Lfunc_begin48
	.xword	.Ltmp513-.Lfunc_begin48
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp513-.Lfunc_begin48
	.xword	.Lfunc_end48-.Lfunc_begin48
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc114:
	.xword	-1
	.xword	.Lfunc_begin49                  //   base address
	.xword	.Lfunc_begin49-.Lfunc_begin49
	.xword	.Ltmp515-.Lfunc_begin49
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp515-.Lfunc_begin49
	.xword	.Ltmp527-.Lfunc_begin49
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp527-.Lfunc_begin49
	.xword	.Ltmp528-.Lfunc_begin49
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp528-.Lfunc_begin49
	.xword	.Lfunc_end49-.Lfunc_begin49
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc115:
	.xword	-1
	.xword	.Lfunc_begin49                  //   base address
	.xword	.Lfunc_begin49-.Lfunc_begin49
	.xword	.Ltmp516-.Lfunc_begin49
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp516-.Lfunc_begin49
	.xword	.Ltmp527-.Lfunc_begin49
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp527-.Lfunc_begin49
	.xword	.Ltmp528-.Lfunc_begin49
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp528-.Lfunc_begin49
	.xword	.Lfunc_end49-.Lfunc_begin49
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc116:
	.xword	-1
	.xword	.Lfunc_begin50                  //   base address
	.xword	.Lfunc_begin50-.Lfunc_begin50
	.xword	.Ltmp531-.Lfunc_begin50
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp531-.Lfunc_begin50
	.xword	.Lfunc_end50-.Lfunc_begin50
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc117:
	.xword	-1
	.xword	.Lfunc_begin50                  //   base address
	.xword	.Lfunc_begin50-.Lfunc_begin50
	.xword	.Ltmp530-.Lfunc_begin50
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp530-.Lfunc_begin50
	.xword	.Ltmp535-.Lfunc_begin50
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp535-.Lfunc_begin50
	.xword	.Ltmp536-.Lfunc_begin50
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp536-.Lfunc_begin50
	.xword	.Lfunc_end50-.Lfunc_begin50
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc118:
	.xword	-1
	.xword	.Lfunc_begin51                  //   base address
	.xword	.Lfunc_begin51-.Lfunc_begin51
	.xword	.Ltmp539-.Lfunc_begin51
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp539-.Lfunc_begin51
	.xword	.Lfunc_end51-.Lfunc_begin51
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc119:
	.xword	-1
	.xword	.Lfunc_begin51                  //   base address
	.xword	.Lfunc_begin51-.Lfunc_begin51
	.xword	.Ltmp538-.Lfunc_begin51
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp538-.Lfunc_begin51
	.xword	.Ltmp544-.Lfunc_begin51
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp544-.Lfunc_begin51
	.xword	.Ltmp545-.Lfunc_begin51
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp545-.Lfunc_begin51
	.xword	.Lfunc_end51-.Lfunc_begin51
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc120:
	.xword	-1
	.xword	.Lfunc_begin52                  //   base address
	.xword	.Lfunc_begin52-.Lfunc_begin52
	.xword	.Ltmp548-.Lfunc_begin52
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp548-.Lfunc_begin52
	.xword	.Lfunc_end52-.Lfunc_begin52
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc121:
	.xword	-1
	.xword	.Lfunc_begin52                  //   base address
	.xword	.Lfunc_begin52-.Lfunc_begin52
	.xword	.Ltmp547-.Lfunc_begin52
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp547-.Lfunc_begin52
	.xword	.Ltmp553-.Lfunc_begin52
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp553-.Lfunc_begin52
	.xword	.Ltmp554-.Lfunc_begin52
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp554-.Lfunc_begin52
	.xword	.Lfunc_end52-.Lfunc_begin52
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc122:
	.xword	-1
	.xword	.Lfunc_begin53                  //   base address
	.xword	.Lfunc_begin53-.Lfunc_begin53
	.xword	.Ltmp557-.Lfunc_begin53
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp557-.Lfunc_begin53
	.xword	.Lfunc_end53-.Lfunc_begin53
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc123:
	.xword	-1
	.xword	.Lfunc_begin53                  //   base address
	.xword	.Lfunc_begin53-.Lfunc_begin53
	.xword	.Ltmp556-.Lfunc_begin53
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp556-.Lfunc_begin53
	.xword	.Ltmp560-.Lfunc_begin53
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp560-.Lfunc_begin53
	.xword	.Ltmp561-.Lfunc_begin53
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp561-.Lfunc_begin53
	.xword	.Lfunc_end53-.Lfunc_begin53
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc124:
	.xword	-1
	.xword	.Lfunc_begin54                  //   base address
	.xword	.Lfunc_begin54-.Lfunc_begin54
	.xword	.Ltmp564-.Lfunc_begin54
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp564-.Lfunc_begin54
	.xword	.Lfunc_end54-.Lfunc_begin54
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc125:
	.xword	-1
	.xword	.Lfunc_begin54                  //   base address
	.xword	.Lfunc_begin54-.Lfunc_begin54
	.xword	.Ltmp563-.Lfunc_begin54
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp563-.Lfunc_begin54
	.xword	.Ltmp567-.Lfunc_begin54
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp567-.Lfunc_begin54
	.xword	.Ltmp568-.Lfunc_begin54
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp568-.Lfunc_begin54
	.xword	.Lfunc_end54-.Lfunc_begin54
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc126:
	.xword	-1
	.xword	.Lfunc_begin55                  //   base address
	.xword	.Lfunc_begin55-.Lfunc_begin55
	.xword	.Ltmp570-.Lfunc_begin55
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp570-.Lfunc_begin55
	.xword	.Ltmp579-.Lfunc_begin55
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp579-.Lfunc_begin55
	.xword	.Ltmp580-.Lfunc_begin55
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp580-.Lfunc_begin55
	.xword	.Lfunc_end55-.Lfunc_begin55
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc127:
	.xword	-1
	.xword	.Lfunc_begin55                  //   base address
	.xword	.Lfunc_begin55-.Lfunc_begin55
	.xword	.Ltmp571-.Lfunc_begin55
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp571-.Lfunc_begin55
	.xword	.Ltmp579-.Lfunc_begin55
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp579-.Lfunc_begin55
	.xword	.Ltmp580-.Lfunc_begin55
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp580-.Lfunc_begin55
	.xword	.Lfunc_end55-.Lfunc_begin55
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc128:
	.xword	-1
	.xword	.Lfunc_begin55                  //   base address
	.xword	.Ltmp576-.Lfunc_begin55
	.xword	.Ltmp577-.Lfunc_begin55
	.hword	2                               // Loc expr size
	.byte	144                             // DW_OP_regx
	.byte	64                              // 64
	.xword	0
	.xword	0
.Ldebug_loc129:
	.xword	-1
	.xword	.Lfunc_begin56                  //   base address
	.xword	.Lfunc_begin56-.Lfunc_begin56
	.xword	.Ltmp583-.Lfunc_begin56
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp583-.Lfunc_begin56
	.xword	.Lfunc_end56-.Lfunc_begin56
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc130:
	.xword	-1
	.xword	.Lfunc_begin56                  //   base address
	.xword	.Lfunc_begin56-.Lfunc_begin56
	.xword	.Ltmp582-.Lfunc_begin56
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp582-.Lfunc_begin56
	.xword	.Ltmp586-.Lfunc_begin56
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp586-.Lfunc_begin56
	.xword	.Ltmp587-.Lfunc_begin56
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp587-.Lfunc_begin56
	.xword	.Lfunc_end56-.Lfunc_begin56
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc131:
	.xword	-1
	.xword	.Lfunc_begin57                  //   base address
	.xword	.Lfunc_begin57-.Lfunc_begin57
	.xword	.Ltmp590-.Lfunc_begin57
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp590-.Lfunc_begin57
	.xword	.Lfunc_end57-.Lfunc_begin57
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc132:
	.xword	-1
	.xword	.Lfunc_begin57                  //   base address
	.xword	.Lfunc_begin57-.Lfunc_begin57
	.xword	.Ltmp589-.Lfunc_begin57
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp589-.Lfunc_begin57
	.xword	.Ltmp593-.Lfunc_begin57
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp593-.Lfunc_begin57
	.xword	.Ltmp594-.Lfunc_begin57
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp594-.Lfunc_begin57
	.xword	.Lfunc_end57-.Lfunc_begin57
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc133:
	.xword	-1
	.xword	.Lfunc_begin58                  //   base address
	.xword	.Lfunc_begin58-.Lfunc_begin58
	.xword	.Ltmp596-.Lfunc_begin58
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp596-.Lfunc_begin58
	.xword	.Ltmp602-.Lfunc_begin58
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp602-.Lfunc_begin58
	.xword	.Ltmp603-.Lfunc_begin58
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp603-.Lfunc_begin58
	.xword	.Lfunc_end58-.Lfunc_begin58
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc134:
	.xword	-1
	.xword	.Lfunc_begin58                  //   base address
	.xword	.Lfunc_begin58-.Lfunc_begin58
	.xword	.Ltmp597-.Lfunc_begin58
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp597-.Lfunc_begin58
	.xword	.Ltmp602-.Lfunc_begin58
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp602-.Lfunc_begin58
	.xword	.Ltmp603-.Lfunc_begin58
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp603-.Lfunc_begin58
	.xword	.Lfunc_end58-.Lfunc_begin58
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc135:
	.xword	-1
	.xword	.Lfunc_begin59                  //   base address
	.xword	.Lfunc_begin59-.Lfunc_begin59
	.xword	.Ltmp605-.Lfunc_begin59
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp605-.Lfunc_begin59
	.xword	.Ltmp611-.Lfunc_begin59
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	.Ltmp611-.Lfunc_begin59
	.xword	.Ltmp612-.Lfunc_begin59
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp612-.Lfunc_begin59
	.xword	.Lfunc_end59-.Lfunc_begin59
	.hword	1                               // Loc expr size
	.byte	100                             // DW_OP_reg20
	.xword	0
	.xword	0
.Ldebug_loc136:
	.xword	-1
	.xword	.Lfunc_begin59                  //   base address
	.xword	.Lfunc_begin59-.Lfunc_begin59
	.xword	.Ltmp606-.Lfunc_begin59
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp606-.Lfunc_begin59
	.xword	.Ltmp611-.Lfunc_begin59
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp611-.Lfunc_begin59
	.xword	.Ltmp612-.Lfunc_begin59
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp612-.Lfunc_begin59
	.xword	.Lfunc_end59-.Lfunc_begin59
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc137:
	.xword	-1
	.xword	.Lfunc_begin60                  //   base address
	.xword	.Lfunc_begin60-.Lfunc_begin60
	.xword	.Ltmp615-.Lfunc_begin60
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp615-.Lfunc_begin60
	.xword	.Lfunc_end60-.Lfunc_begin60
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc138:
	.xword	-1
	.xword	.Lfunc_begin60                  //   base address
	.xword	.Lfunc_begin60-.Lfunc_begin60
	.xword	.Ltmp614-.Lfunc_begin60
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp614-.Lfunc_begin60
	.xword	.Ltmp619-.Lfunc_begin60
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp619-.Lfunc_begin60
	.xword	.Ltmp620-.Lfunc_begin60
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp620-.Lfunc_begin60
	.xword	.Lfunc_end60-.Lfunc_begin60
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc139:
	.xword	-1
	.xword	.Lfunc_begin61                  //   base address
	.xword	.Lfunc_begin61-.Lfunc_begin61
	.xword	.Ltmp623-.Lfunc_begin61
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp623-.Lfunc_begin61
	.xword	.Lfunc_end61-.Lfunc_begin61
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc140:
	.xword	-1
	.xword	.Lfunc_begin61                  //   base address
	.xword	.Lfunc_begin61-.Lfunc_begin61
	.xword	.Ltmp622-.Lfunc_begin61
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp622-.Lfunc_begin61
	.xword	.Ltmp668-.Lfunc_begin61
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp668-.Lfunc_begin61
	.xword	.Ltmp669-.Lfunc_begin61
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp669-.Lfunc_begin61
	.xword	.Lfunc_end61-.Lfunc_begin61
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc141:
	.xword	-1
	.xword	.Lfunc_begin61                  //   base address
	.xword	.Ltmp639-.Lfunc_begin61
	.xword	.Ltmp641-.Lfunc_begin61
	.hword	2                               // Loc expr size
	.byte	48                              // DW_OP_lit0
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp641-.Lfunc_begin61
	.xword	.Ltmp643-.Lfunc_begin61
	.hword	4                               // Loc expr size
	.byte	16                              // DW_OP_constu
	.byte	226                             // 226
	.byte	1                               // 
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp643-.Lfunc_begin61
	.xword	.Ltmp644-.Lfunc_begin61
	.hword	4                               // Loc expr size
	.byte	16                              // DW_OP_constu
	.byte	227                             // 227
	.byte	1                               // 
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp644-.Lfunc_begin61
	.xword	.Ltmp646-.Lfunc_begin61
	.hword	10                              // Loc expr size
	.byte	122                             // DW_OP_breg10
	.byte	0                               // 0
	.byte	17                              // DW_OP_consts
	.byte	4                               // 4
	.byte	27                              // DW_OP_div
	.byte	17                              // DW_OP_consts
	.byte	227                             // 227
	.byte	1                               // 
	.byte	34                              // DW_OP_plus
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp651-.Lfunc_begin61
	.xword	.Ltmp653-.Lfunc_begin61
	.hword	10                              // Loc expr size
	.byte	122                             // DW_OP_breg10
	.byte	0                               // 0
	.byte	17                              // DW_OP_consts
	.byte	4                               // 4
	.byte	27                              // DW_OP_div
	.byte	17                              // DW_OP_consts
	.byte	228                             // 228
	.byte	1                               // 
	.byte	34                              // DW_OP_plus
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc142:
	.xword	-1
	.xword	.Lfunc_begin61                  //   base address
	.xword	.Ltmp658-.Lfunc_begin61
	.xword	.Ltmp665-.Lfunc_begin61
	.hword	1                               // Loc expr size
	.byte	88                              // DW_OP_reg8
	.xword	0
	.xword	0
.Ldebug_loc143:
	.xword	-1
	.xword	.Lfunc_begin61                  //   base address
	.xword	.Ltmp657-.Lfunc_begin61
	.xword	.Ltmp666-.Lfunc_begin61
	.hword	2                               // Loc expr size
	.byte	144                             // DW_OP_regx
	.byte	64                              // 64
	.xword	0
	.xword	0
.Ldebug_loc144:
	.xword	-1
	.xword	.Lfunc_begin62                  //   base address
	.xword	.Lfunc_begin62-.Lfunc_begin62
	.xword	.Ltmp672-.Lfunc_begin62
	.hword	1                               // Loc expr size
	.byte	80                              // DW_OP_reg0
	.xword	.Ltmp672-.Lfunc_begin62
	.xword	.Lfunc_end62-.Lfunc_begin62
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	80                              // DW_OP_reg0
	.byte	159                             // DW_OP_stack_value
	.xword	0
	.xword	0
.Ldebug_loc145:
	.xword	-1
	.xword	.Lfunc_begin62                  //   base address
	.xword	.Lfunc_begin62-.Lfunc_begin62
	.xword	.Ltmp671-.Lfunc_begin62
	.hword	1                               // Loc expr size
	.byte	81                              // DW_OP_reg1
	.xword	.Ltmp671-.Lfunc_begin62
	.xword	.Ltmp679-.Lfunc_begin62
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	.Ltmp679-.Lfunc_begin62
	.xword	.Ltmp680-.Lfunc_begin62
	.hword	4                               // Loc expr size
	.byte	243                             // DW_OP_GNU_entry_value
	.byte	1                               // 1
	.byte	81                              // DW_OP_reg1
	.byte	159                             // DW_OP_stack_value
	.xword	.Ltmp680-.Lfunc_begin62
	.xword	.Lfunc_end62-.Lfunc_begin62
	.hword	1                               // Loc expr size
	.byte	99                              // DW_OP_reg19
	.xword	0
	.xword	0
.Ldebug_loc146:
	.xword	-1
	.xword	.Lfunc_begin62                  //   base address
	.xword	.Ltmp674-.Lfunc_begin62
	.xword	.Ltmp675-.Lfunc_begin62
	.hword	2                               // Loc expr size
	.byte	144                             // DW_OP_regx
	.byte	64                              // 64
	.xword	.Ltmp676-.Lfunc_begin62
	.xword	.Ltmp677-.Lfunc_begin62
	.hword	2                               // Loc expr size
	.byte	144                             // DW_OP_regx
	.byte	66                              // 66
	.xword	.Ltmp677-.Lfunc_begin62
	.xword	.Ltmp681-.Lfunc_begin62
	.hword	2                               // Loc expr size
	.byte	144                             // DW_OP_regx
	.byte	64                              // 64
	.xword	0
	.xword	0
	.section	.debug_abbrev,"",@progbits
	.byte	1                               // Abbreviation Code
	.byte	17                              // DW_TAG_compile_unit
	.byte	1                               // DW_CHILDREN_yes
	.byte	37                              // DW_AT_producer
	.byte	14                              // DW_FORM_strp
	.byte	19                              // DW_AT_language
	.byte	5                               // DW_FORM_data2
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	16                              // DW_AT_stmt_list
	.byte	23                              // DW_FORM_sec_offset
	.byte	27                              // DW_AT_comp_dir
	.byte	14                              // DW_FORM_strp
	.byte	17                              // DW_AT_low_pc
	.byte	1                               // DW_FORM_addr
	.byte	85                              // DW_AT_ranges
	.byte	23                              // DW_FORM_sec_offset
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	2                               // Abbreviation Code
	.byte	46                              // DW_TAG_subprogram
	.byte	1                               // DW_CHILDREN_yes
	.byte	17                              // DW_AT_low_pc
	.byte	1                               // DW_FORM_addr
	.byte	18                              // DW_AT_high_pc
	.byte	6                               // DW_FORM_data4
	.byte	64                              // DW_AT_frame_base
	.byte	24                              // DW_FORM_exprloc
	.ascii	"\227B"                         // DW_AT_GNU_all_call_sites
	.byte	25                              // DW_FORM_flag_present
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	5                               // DW_FORM_data2
	.byte	39                              // DW_AT_prototyped
	.byte	25                              // DW_FORM_flag_present
	.byte	63                              // DW_AT_external
	.byte	25                              // DW_FORM_flag_present
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	3                               // Abbreviation Code
	.byte	52                              // DW_TAG_variable
	.byte	0                               // DW_CHILDREN_no
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	5                               // DW_FORM_data2
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	4                               // Abbreviation Code
	.byte	5                               // DW_TAG_formal_parameter
	.byte	0                               // DW_CHILDREN_no
	.byte	2                               // DW_AT_location
	.byte	23                              // DW_FORM_sec_offset
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	5                               // DW_FORM_data2
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	5                               // Abbreviation Code
	.byte	52                              // DW_TAG_variable
	.byte	0                               // DW_CHILDREN_no
	.byte	2                               // DW_AT_location
	.byte	24                              // DW_FORM_exprloc
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	5                               // DW_FORM_data2
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	6                               // Abbreviation Code
	.byte	52                              // DW_TAG_variable
	.byte	0                               // DW_CHILDREN_no
	.byte	2                               // DW_AT_location
	.byte	23                              // DW_FORM_sec_offset
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	5                               // DW_FORM_data2
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	7                               // Abbreviation Code
	.byte	52                              // DW_TAG_variable
	.byte	0                               // DW_CHILDREN_no
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	5                               // DW_FORM_data2
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	8                               // Abbreviation Code
	.ascii	"\211\202\001"                  // DW_TAG_GNU_call_site
	.byte	1                               // DW_CHILDREN_yes
	.ascii	"\223B"                         // DW_AT_GNU_call_site_target
	.byte	24                              // DW_FORM_exprloc
	.byte	17                              // DW_AT_low_pc
	.byte	1                               // DW_FORM_addr
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	9                               // Abbreviation Code
	.ascii	"\212\202\001"                  // DW_TAG_GNU_call_site_parameter
	.byte	0                               // DW_CHILDREN_no
	.byte	2                               // DW_AT_location
	.byte	24                              // DW_FORM_exprloc
	.ascii	"\221B"                         // DW_AT_GNU_call_site_value
	.byte	24                              // DW_FORM_exprloc
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	10                              // Abbreviation Code
	.byte	23                              // DW_TAG_union_type
	.byte	1                               // DW_CHILDREN_yes
	.byte	11                              // DW_AT_byte_size
	.byte	11                              // DW_FORM_data1
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	5                               // DW_FORM_data2
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	11                              // Abbreviation Code
	.byte	13                              // DW_TAG_member
	.byte	0                               // DW_CHILDREN_no
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	5                               // DW_FORM_data2
	.byte	56                              // DW_AT_data_member_location
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	12                              // Abbreviation Code
	.byte	38                              // DW_TAG_const_type
	.byte	0                               // DW_CHILDREN_no
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	13                              // Abbreviation Code
	.byte	22                              // DW_TAG_typedef
	.byte	0                               // DW_CHILDREN_no
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	14                              // Abbreviation Code
	.byte	36                              // DW_TAG_base_type
	.byte	0                               // DW_CHILDREN_no
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	62                              // DW_AT_encoding
	.byte	11                              // DW_FORM_data1
	.byte	11                              // DW_AT_byte_size
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	15                              // Abbreviation Code
	.byte	52                              // DW_TAG_variable
	.byte	0                               // DW_CHILDREN_no
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	2                               // DW_AT_location
	.byte	24                              // DW_FORM_exprloc
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	16                              // Abbreviation Code
	.byte	1                               // DW_TAG_array_type
	.byte	1                               // DW_CHILDREN_yes
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	17                              // Abbreviation Code
	.byte	33                              // DW_TAG_subrange_type
	.byte	0                               // DW_CHILDREN_no
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	55                              // DW_AT_count
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	18                              // Abbreviation Code
	.byte	36                              // DW_TAG_base_type
	.byte	0                               // DW_CHILDREN_no
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	11                              // DW_AT_byte_size
	.byte	11                              // DW_FORM_data1
	.byte	62                              // DW_AT_encoding
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	19                              // Abbreviation Code
	.byte	52                              // DW_TAG_variable
	.byte	0                               // DW_CHILDREN_no
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	2                               // DW_AT_location
	.byte	24                              // DW_FORM_exprloc
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	20                              // Abbreviation Code
	.byte	19                              // DW_TAG_structure_type
	.byte	1                               // DW_CHILDREN_yes
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	11                              // DW_AT_byte_size
	.byte	11                              // DW_FORM_data1
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	21                              // Abbreviation Code
	.byte	13                              // DW_TAG_member
	.byte	0                               // DW_CHILDREN_no
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	56                              // DW_AT_data_member_location
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	22                              // Abbreviation Code
	.byte	15                              // DW_TAG_pointer_type
	.byte	0                               // DW_CHILDREN_no
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	23                              // Abbreviation Code
	.byte	21                              // DW_TAG_subroutine_type
	.byte	1                               // DW_CHILDREN_yes
	.byte	39                              // DW_AT_prototyped
	.byte	25                              // DW_FORM_flag_present
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	24                              // Abbreviation Code
	.byte	5                               // DW_TAG_formal_parameter
	.byte	0                               // DW_CHILDREN_no
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	25                              // Abbreviation Code
	.byte	13                              // DW_TAG_member
	.byte	0                               // DW_CHILDREN_no
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	56                              // DW_AT_data_member_location
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	26                              // Abbreviation Code
	.byte	23                              // DW_TAG_union_type
	.byte	1                               // DW_CHILDREN_yes
	.byte	11                              // DW_AT_byte_size
	.byte	11                              // DW_FORM_data1
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	27                              // Abbreviation Code
	.byte	46                              // DW_TAG_subprogram
	.byte	1                               // DW_CHILDREN_yes
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	28                              // Abbreviation Code
	.byte	52                              // DW_TAG_variable
	.byte	0                               // DW_CHILDREN_no
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	29                              // Abbreviation Code
	.byte	33                              // DW_TAG_subrange_type
	.byte	0                               // DW_CHILDREN_no
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	55                              // DW_AT_count
	.byte	5                               // DW_FORM_data2
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	30                              // Abbreviation Code
	.byte	46                              // DW_TAG_subprogram
	.byte	1                               // DW_CHILDREN_yes
	.byte	17                              // DW_AT_low_pc
	.byte	1                               // DW_FORM_addr
	.byte	18                              // DW_AT_high_pc
	.byte	6                               // DW_FORM_data4
	.byte	64                              // DW_AT_frame_base
	.byte	24                              // DW_FORM_exprloc
	.ascii	"\227B"                         // DW_AT_GNU_all_call_sites
	.byte	25                              // DW_FORM_flag_present
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	39                              // DW_AT_prototyped
	.byte	25                              // DW_FORM_flag_present
	.byte	63                              // DW_AT_external
	.byte	25                              // DW_FORM_flag_present
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	31                              // Abbreviation Code
	.byte	5                               // DW_TAG_formal_parameter
	.byte	0                               // DW_CHILDREN_no
	.byte	2                               // DW_AT_location
	.byte	24                              // DW_FORM_exprloc
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	32                              // Abbreviation Code
	.byte	5                               // DW_TAG_formal_parameter
	.byte	0                               // DW_CHILDREN_no
	.byte	2                               // DW_AT_location
	.byte	23                              // DW_FORM_sec_offset
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	33                              // Abbreviation Code
	.byte	52                              // DW_TAG_variable
	.byte	0                               // DW_CHILDREN_no
	.byte	2                               // DW_AT_location
	.byte	23                              // DW_FORM_sec_offset
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	34                              // Abbreviation Code
	.byte	11                              // DW_TAG_lexical_block
	.byte	1                               // DW_CHILDREN_yes
	.byte	17                              // DW_AT_low_pc
	.byte	1                               // DW_FORM_addr
	.byte	18                              // DW_AT_high_pc
	.byte	6                               // DW_FORM_data4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	35                              // Abbreviation Code
	.ascii	"\211\202\001"                  // DW_TAG_GNU_call_site
	.byte	0                               // DW_CHILDREN_no
	.byte	49                              // DW_AT_abstract_origin
	.byte	19                              // DW_FORM_ref4
	.byte	17                              // DW_AT_low_pc
	.byte	1                               // DW_FORM_addr
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	36                              // Abbreviation Code
	.byte	46                              // DW_TAG_subprogram
	.byte	1                               // DW_CHILDREN_yes
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	39                              // DW_AT_prototyped
	.byte	25                              // DW_FORM_flag_present
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	60                              // DW_AT_declaration
	.byte	25                              // DW_FORM_flag_present
	.byte	63                              // DW_AT_external
	.byte	25                              // DW_FORM_flag_present
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	37                              // Abbreviation Code
	.ascii	"\211\202\001"                  // DW_TAG_GNU_call_site
	.byte	0                               // DW_CHILDREN_no
	.byte	49                              // DW_AT_abstract_origin
	.byte	19                              // DW_FORM_ref4
	.ascii	"\225B"                         // DW_AT_GNU_tail_call
	.byte	25                              // DW_FORM_flag_present
	.byte	17                              // DW_AT_low_pc
	.byte	1                               // DW_FORM_addr
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	38                              // Abbreviation Code
	.byte	46                              // DW_TAG_subprogram
	.byte	1                               // DW_CHILDREN_yes
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	39                              // DW_AT_prototyped
	.byte	25                              // DW_FORM_flag_present
	.byte	60                              // DW_AT_declaration
	.byte	25                              // DW_FORM_flag_present
	.byte	63                              // DW_AT_external
	.byte	25                              // DW_FORM_flag_present
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	39                              // Abbreviation Code
	.byte	46                              // DW_TAG_subprogram
	.byte	1                               // DW_CHILDREN_yes
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	5                               // DW_FORM_data2
	.byte	39                              // DW_AT_prototyped
	.byte	25                              // DW_FORM_flag_present
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	32                              // DW_AT_inline
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	40                              // Abbreviation Code
	.byte	5                               // DW_TAG_formal_parameter
	.byte	0                               // DW_CHILDREN_no
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	5                               // DW_FORM_data2
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	41                              // Abbreviation Code
	.byte	22                              // DW_TAG_typedef
	.byte	0                               // DW_CHILDREN_no
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	5                               // DW_FORM_data2
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	42                              // Abbreviation Code
	.byte	29                              // DW_TAG_inlined_subroutine
	.byte	1                               // DW_CHILDREN_yes
	.byte	49                              // DW_AT_abstract_origin
	.byte	19                              // DW_FORM_ref4
	.byte	85                              // DW_AT_ranges
	.byte	23                              // DW_FORM_sec_offset
	.byte	88                              // DW_AT_call_file
	.byte	11                              // DW_FORM_data1
	.byte	89                              // DW_AT_call_line
	.byte	5                               // DW_FORM_data2
	.byte	87                              // DW_AT_call_column
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	43                              // Abbreviation Code
	.byte	5                               // DW_TAG_formal_parameter
	.byte	0                               // DW_CHILDREN_no
	.byte	2                               // DW_AT_location
	.byte	23                              // DW_FORM_sec_offset
	.byte	49                              // DW_AT_abstract_origin
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	44                              // Abbreviation Code
	.byte	52                              // DW_TAG_variable
	.byte	0                               // DW_CHILDREN_no
	.byte	2                               // DW_AT_location
	.byte	23                              // DW_FORM_sec_offset
	.byte	49                              // DW_AT_abstract_origin
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	45                              // Abbreviation Code
	.byte	46                              // DW_TAG_subprogram
	.byte	1                               // DW_CHILDREN_yes
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	39                              // DW_AT_prototyped
	.byte	25                              // DW_FORM_flag_present
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	32                              // DW_AT_inline
	.byte	11                              // DW_FORM_data1
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	46                              // Abbreviation Code
	.byte	52                              // DW_TAG_variable
	.byte	0                               // DW_CHILDREN_no
	.byte	3                               // DW_AT_name
	.byte	14                              // DW_FORM_strp
	.byte	58                              // DW_AT_decl_file
	.byte	11                              // DW_FORM_data1
	.byte	59                              // DW_AT_decl_line
	.byte	11                              // DW_FORM_data1
	.byte	73                              // DW_AT_type
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	47                              // Abbreviation Code
	.byte	11                              // DW_TAG_lexical_block
	.byte	1                               // DW_CHILDREN_yes
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	48                              // Abbreviation Code
	.byte	52                              // DW_TAG_variable
	.byte	0                               // DW_CHILDREN_no
	.byte	28                              // DW_AT_const_value
	.byte	15                              // DW_FORM_udata
	.byte	49                              // DW_AT_abstract_origin
	.byte	19                              // DW_FORM_ref4
	.byte	0                               // EOM(1)
	.byte	0                               // EOM(2)
	.byte	0                               // EOM(3)
	.section	.debug_info,"",@progbits
.Lcu_begin0:
	.word	.Ldebug_info_end0-.Ldebug_info_start0 // Length of Unit
.Ldebug_info_start0:
	.hword	4                               // DWARF version number
	.word	.debug_abbrev                   // Offset Into Abbrev. Section
	.byte	8                               // Address Size (in bytes)
	.byte	1                               // Abbrev [1] 0xb:0x285d DW_TAG_compile_unit
	.word	.Linfo_string0                  // DW_AT_producer
	.hword	29                              // DW_AT_language
	.word	.Linfo_string1                  // DW_AT_name
	.word	.Lline_table_start0             // DW_AT_stmt_list
	.word	.Linfo_string2                  // DW_AT_comp_dir
	.xword	0                               // DW_AT_low_pc
	.word	.Ldebug_ranges3                 // DW_AT_ranges
	.byte	2                               // Abbrev [2] 0x2a:0xac DW_TAG_subprogram
	.xword	.Lfunc_begin62                  // DW_AT_low_pc
	.word	.Lfunc_end62-.Lfunc_begin62     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string133                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1221                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	3                               // Abbrev [3] 0x40:0xc DW_TAG_variable
	.word	.Linfo_string3                  // DW_AT_name
	.word	214                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.hword	1243                            // DW_AT_decl_line
	.byte	3                               // Abbrev [3] 0x4c:0xc DW_TAG_variable
	.word	.Linfo_string6                  // DW_AT_name
	.word	214                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.hword	1244                            // DW_AT_decl_line
	.byte	4                               // Abbrev [4] 0x58:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc144                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1221                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x68:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc145                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1221                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x78:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1248                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	6                               // Abbrev [6] 0x87:0x10 DW_TAG_variable
	.word	.Ldebug_loc146                  // DW_AT_location
	.word	.Linfo_string162                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1241                            // DW_AT_decl_line
	.word	181                             // DW_AT_type
	.byte	7                               // Abbrev [7] 0x97:0xc DW_TAG_variable
	.word	.Linfo_string165                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1252                            // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	8                               // Abbrev [8] 0xa3:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp673                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xae:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	10                              // Abbrev [10] 0xb5:0x20 DW_TAG_union_type
	.byte	8                               // DW_AT_byte_size
	.byte	2                               // DW_AT_decl_file
	.hword	1237                            // DW_AT_decl_line
	.byte	11                              // Abbrev [11] 0xba:0xd DW_TAG_member
	.word	.Linfo_string163                // DW_AT_name
	.word	219                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.hword	1239                            // DW_AT_decl_line
	.byte	0                               // DW_AT_data_member_location
	.byte	11                              // Abbrev [11] 0xc7:0xd DW_TAG_member
	.word	.Linfo_string164                // DW_AT_name
	.word	5465                            // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.hword	1240                            // DW_AT_decl_line
	.byte	0                               // DW_AT_data_member_location
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	12                              // Abbrev [12] 0xd6:0x5 DW_TAG_const_type
	.word	219                             // DW_AT_type
	.byte	13                              // Abbrev [13] 0xdb:0xb DW_TAG_typedef
	.word	230                             // DW_AT_type
	.word	.Linfo_string5                  // DW_AT_name
	.byte	1                               // DW_AT_decl_file
	.byte	22                              // DW_AT_decl_line
	.byte	14                              // Abbrev [14] 0xe6:0x7 DW_TAG_base_type
	.word	.Linfo_string4                  // DW_AT_name
	.byte	4                               // DW_AT_encoding
	.byte	8                               // DW_AT_byte_size
	.byte	15                              // Abbrev [15] 0xed:0x11 DW_TAG_variable
	.word	254                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	28                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str
	.byte	16                              // Abbrev [16] 0xfe:0xc DW_TAG_array_type
	.word	266                             // DW_AT_type
	.byte	17                              // Abbrev [17] 0x103:0x6 DW_TAG_subrange_type
	.word	273                             // DW_AT_type
	.byte	10                              // DW_AT_count
	.byte	0                               // End Of Children Mark
	.byte	14                              // Abbrev [14] 0x10a:0x7 DW_TAG_base_type
	.word	.Linfo_string7                  // DW_AT_name
	.byte	8                               // DW_AT_encoding
	.byte	1                               // DW_AT_byte_size
	.byte	18                              // Abbrev [18] 0x111:0x7 DW_TAG_base_type
	.word	.Linfo_string8                  // DW_AT_name
	.byte	8                               // DW_AT_byte_size
	.byte	7                               // DW_AT_encoding
	.byte	15                              // Abbrev [15] 0x118:0x11 DW_TAG_variable
	.word	297                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	29                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.1
	.byte	16                              // Abbrev [16] 0x129:0xc DW_TAG_array_type
	.word	266                             // DW_AT_type
	.byte	17                              // Abbrev [17] 0x12e:0x6 DW_TAG_subrange_type
	.word	273                             // DW_AT_type
	.byte	8                               // DW_AT_count
	.byte	0                               // End Of Children Mark
	.byte	15                              // Abbrev [15] 0x135:0x11 DW_TAG_variable
	.word	326                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	30                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.2
	.byte	16                              // Abbrev [16] 0x146:0xc DW_TAG_array_type
	.word	266                             // DW_AT_type
	.byte	17                              // Abbrev [17] 0x14b:0x6 DW_TAG_subrange_type
	.word	273                             // DW_AT_type
	.byte	9                               // DW_AT_count
	.byte	0                               // End Of Children Mark
	.byte	15                              // Abbrev [15] 0x152:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	31                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.3
	.byte	16                              // Abbrev [16] 0x163:0xc DW_TAG_array_type
	.word	266                             // DW_AT_type
	.byte	17                              // Abbrev [17] 0x168:0x6 DW_TAG_subrange_type
	.word	273                             // DW_AT_type
	.byte	7                               // DW_AT_count
	.byte	0                               // End Of Children Mark
	.byte	15                              // Abbrev [15] 0x16f:0x11 DW_TAG_variable
	.word	297                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	32                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.4
	.byte	15                              // Abbrev [15] 0x180:0x11 DW_TAG_variable
	.word	401                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	34                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.5
	.byte	16                              // Abbrev [16] 0x191:0xc DW_TAG_array_type
	.word	266                             // DW_AT_type
	.byte	17                              // Abbrev [17] 0x196:0x6 DW_TAG_subrange_type
	.word	273                             // DW_AT_type
	.byte	3                               // DW_AT_count
	.byte	0                               // End Of Children Mark
	.byte	15                              // Abbrev [15] 0x19d:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	35                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.6
	.byte	16                              // Abbrev [16] 0x1ae:0xc DW_TAG_array_type
	.word	266                             // DW_AT_type
	.byte	17                              // Abbrev [17] 0x1b3:0x6 DW_TAG_subrange_type
	.word	273                             // DW_AT_type
	.byte	4                               // DW_AT_count
	.byte	0                               // End Of Children Mark
	.byte	15                              // Abbrev [15] 0x1ba:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	36                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.7
	.byte	16                              // Abbrev [16] 0x1cb:0xc DW_TAG_array_type
	.word	266                             // DW_AT_type
	.byte	17                              // Abbrev [17] 0x1d0:0x6 DW_TAG_subrange_type
	.word	273                             // DW_AT_type
	.byte	5                               // DW_AT_count
	.byte	0                               // End Of Children Mark
	.byte	15                              // Abbrev [15] 0x1d7:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	37                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.8
	.byte	15                              // Abbrev [15] 0x1e8:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	38                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.9
	.byte	15                              // Abbrev [15] 0x1f9:0x11 DW_TAG_variable
	.word	522                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	39                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.10
	.byte	16                              // Abbrev [16] 0x20a:0xc DW_TAG_array_type
	.word	266                             // DW_AT_type
	.byte	17                              // Abbrev [17] 0x20f:0x6 DW_TAG_subrange_type
	.word	273                             // DW_AT_type
	.byte	6                               // DW_AT_count
	.byte	0                               // End Of Children Mark
	.byte	15                              // Abbrev [15] 0x216:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	41                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.11
	.byte	15                              // Abbrev [15] 0x227:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	42                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.12
	.byte	15                              // Abbrev [15] 0x238:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	43                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.13
	.byte	15                              // Abbrev [15] 0x249:0x11 DW_TAG_variable
	.word	522                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	44                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.14
	.byte	15                              // Abbrev [15] 0x25a:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	45                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.15
	.byte	15                              // Abbrev [15] 0x26b:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	46                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.16
	.byte	15                              // Abbrev [15] 0x27c:0x11 DW_TAG_variable
	.word	522                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	47                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.17
	.byte	15                              // Abbrev [15] 0x28d:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	48                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.18
	.byte	15                              // Abbrev [15] 0x29e:0x11 DW_TAG_variable
	.word	522                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	49                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.19
	.byte	15                              // Abbrev [15] 0x2af:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	50                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.20
	.byte	15                              // Abbrev [15] 0x2c0:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	51                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.21
	.byte	15                              // Abbrev [15] 0x2d1:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	53                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.22
	.byte	15                              // Abbrev [15] 0x2e2:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	54                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.23
	.byte	15                              // Abbrev [15] 0x2f3:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	55                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.24
	.byte	15                              // Abbrev [15] 0x304:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	56                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.25
	.byte	15                              // Abbrev [15] 0x315:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	57                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.26
	.byte	15                              // Abbrev [15] 0x326:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	58                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.27
	.byte	15                              // Abbrev [15] 0x337:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	59                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.28
	.byte	15                              // Abbrev [15] 0x348:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	60                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.29
	.byte	15                              // Abbrev [15] 0x359:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	61                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.30
	.byte	15                              // Abbrev [15] 0x36a:0x11 DW_TAG_variable
	.word	522                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	62                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.31
	.byte	15                              // Abbrev [15] 0x37b:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	63                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.32
	.byte	15                              // Abbrev [15] 0x38c:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	64                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.33
	.byte	15                              // Abbrev [15] 0x39d:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	65                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.34
	.byte	15                              // Abbrev [15] 0x3ae:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	66                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.35
	.byte	15                              // Abbrev [15] 0x3bf:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	68                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.36
	.byte	15                              // Abbrev [15] 0x3d0:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	69                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.37
	.byte	15                              // Abbrev [15] 0x3e1:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	70                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.38
	.byte	15                              // Abbrev [15] 0x3f2:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	71                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.39
	.byte	15                              // Abbrev [15] 0x403:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	72                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.40
	.byte	15                              // Abbrev [15] 0x414:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	73                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.41
	.byte	15                              // Abbrev [15] 0x425:0x11 DW_TAG_variable
	.word	522                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	74                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.42
	.byte	15                              // Abbrev [15] 0x436:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	75                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.43
	.byte	15                              // Abbrev [15] 0x447:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	76                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.44
	.byte	15                              // Abbrev [15] 0x458:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	77                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.45
	.byte	15                              // Abbrev [15] 0x469:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	78                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.46
	.byte	15                              // Abbrev [15] 0x47a:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	79                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.47
	.byte	15                              // Abbrev [15] 0x48b:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	80                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.48
	.byte	15                              // Abbrev [15] 0x49c:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	82                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.49
	.byte	15                              // Abbrev [15] 0x4ad:0x11 DW_TAG_variable
	.word	522                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	83                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.50
	.byte	15                              // Abbrev [15] 0x4be:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	84                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.51
	.byte	15                              // Abbrev [15] 0x4cf:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	85                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.52
	.byte	15                              // Abbrev [15] 0x4e0:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	86                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.53
	.byte	15                              // Abbrev [15] 0x4f1:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	87                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.54
	.byte	15                              // Abbrev [15] 0x502:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	88                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.55
	.byte	15                              // Abbrev [15] 0x513:0x11 DW_TAG_variable
	.word	522                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	89                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.56
	.byte	15                              // Abbrev [15] 0x524:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	90                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.57
	.byte	15                              // Abbrev [15] 0x535:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	91                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.58
	.byte	15                              // Abbrev [15] 0x546:0x11 DW_TAG_variable
	.word	297                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	92                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.59
	.byte	15                              // Abbrev [15] 0x557:0x11 DW_TAG_variable
	.word	297                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	93                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.60
	.byte	15                              // Abbrev [15] 0x568:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	95                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.61
	.byte	15                              // Abbrev [15] 0x579:0x11 DW_TAG_variable
	.word	430                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	96                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.62
	.byte	15                              // Abbrev [15] 0x58a:0x11 DW_TAG_variable
	.word	522                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	98                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.63
	.byte	15                              // Abbrev [15] 0x59b:0x11 DW_TAG_variable
	.word	522                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	99                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.64
	.byte	15                              // Abbrev [15] 0x5ac:0x11 DW_TAG_variable
	.word	459                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	100                             // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.65
	.byte	15                              // Abbrev [15] 0x5bd:0x11 DW_TAG_variable
	.word	297                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	101                             // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.66
	.byte	15                              // Abbrev [15] 0x5ce:0x11 DW_TAG_variable
	.word	522                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	102                             // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.67
	.byte	15                              // Abbrev [15] 0x5df:0x11 DW_TAG_variable
	.word	326                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	103                             // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.68
	.byte	15                              // Abbrev [15] 0x5f0:0x11 DW_TAG_variable
	.word	326                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	104                             // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.69
	.byte	15                              // Abbrev [15] 0x601:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	105                             // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.70
	.byte	15                              // Abbrev [15] 0x612:0x11 DW_TAG_variable
	.word	355                             // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	106                             // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	.L.str.71
	.byte	19                              // Abbrev [19] 0x623:0x15 DW_TAG_variable
	.word	.Linfo_string9                  // DW_AT_name
	.word	1592                            // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	26                              // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	intrinsic_function_table
	.byte	16                              // Abbrev [16] 0x638:0xc DW_TAG_array_type
	.word	1604                            // DW_AT_type
	.byte	17                              // Abbrev [17] 0x63d:0x6 DW_TAG_subrange_type
	.word	273                             // DW_AT_type
	.byte	72                              // DW_AT_count
	.byte	0                               // End Of Children Mark
	.byte	13                              // Abbrev [13] 0x644:0xb DW_TAG_typedef
	.word	1615                            // DW_AT_type
	.word	.Linfo_string30                 // DW_AT_name
	.byte	3                               // DW_AT_decl_file
	.byte	26                              // DW_AT_decl_line
	.byte	20                              // Abbrev [20] 0x64f:0x45 DW_TAG_structure_type
	.word	.Linfo_string29                 // DW_AT_name
	.byte	24                              // DW_AT_byte_size
	.byte	3                               // DW_AT_decl_file
	.byte	19                              // DW_AT_decl_line
	.byte	21                              // Abbrev [21] 0x657:0xc DW_TAG_member
	.word	.Linfo_string10                 // DW_AT_name
	.word	1684                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	21                              // DW_AT_decl_line
	.byte	0                               // DW_AT_data_member_location
	.byte	21                              // Abbrev [21] 0x663:0xc DW_TAG_member
	.word	.Linfo_string11                 // DW_AT_name
	.word	1689                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	22                              // DW_AT_decl_line
	.byte	8                               // DW_AT_data_member_location
	.byte	21                              // Abbrev [21] 0x66f:0xc DW_TAG_member
	.word	.Linfo_string24                 // DW_AT_name
	.word	1896                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	23                              // DW_AT_decl_line
	.byte	16                              // DW_AT_data_member_location
	.byte	21                              // Abbrev [21] 0x67b:0xc DW_TAG_member
	.word	.Linfo_string26                 // DW_AT_name
	.word	1903                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	24                              // DW_AT_decl_line
	.byte	20                              // DW_AT_data_member_location
	.byte	21                              // Abbrev [21] 0x687:0xc DW_TAG_member
	.word	.Linfo_string28                 // DW_AT_name
	.word	1903                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	25                              // DW_AT_decl_line
	.byte	21                              // DW_AT_data_member_location
	.byte	0                               // End Of Children Mark
	.byte	22                              // Abbrev [22] 0x694:0x5 DW_TAG_pointer_type
	.word	266                             // DW_AT_type
	.byte	22                              // Abbrev [22] 0x699:0x5 DW_TAG_pointer_type
	.word	1694                            // DW_AT_type
	.byte	13                              // Abbrev [13] 0x69e:0xb DW_TAG_typedef
	.word	1705                            // DW_AT_type
	.word	.Linfo_string23                 // DW_AT_name
	.byte	3                               // DW_AT_decl_file
	.byte	12                              // DW_AT_decl_line
	.byte	23                              // Abbrev [23] 0x6a9:0xc DW_TAG_subroutine_type
                                        // DW_AT_prototyped
	.byte	24                              // Abbrev [24] 0x6aa:0x5 DW_TAG_formal_parameter
	.word	1717                            // DW_AT_type
	.byte	24                              // Abbrev [24] 0x6af:0x5 DW_TAG_formal_parameter
	.word	1832                            // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	22                              // Abbrev [22] 0x6b5:0x5 DW_TAG_pointer_type
	.word	1722                            // DW_AT_type
	.byte	20                              // Abbrev [20] 0x6ba:0x5e DW_TAG_structure_type
	.word	.Linfo_string22                 // DW_AT_name
	.byte	40                              // DW_AT_byte_size
	.byte	3                               // DW_AT_decl_file
	.byte	72                              // DW_AT_decl_line
	.byte	21                              // Abbrev [21] 0x6c2:0xc DW_TAG_member
	.word	.Linfo_string11                 // DW_AT_name
	.word	1689                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	74                              // DW_AT_decl_line
	.byte	0                               // DW_AT_data_member_location
	.byte	21                              // Abbrev [21] 0x6ce:0xc DW_TAG_member
	.word	.Linfo_string12                 // DW_AT_name
	.word	219                             // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	75                              // DW_AT_decl_line
	.byte	8                               // DW_AT_data_member_location
	.byte	25                              // Abbrev [25] 0x6da:0x8 DW_TAG_member
	.word	1762                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	76                              // DW_AT_decl_line
	.byte	16                              // DW_AT_data_member_location
	.byte	26                              // Abbrev [26] 0x6e2:0x1d DW_TAG_union_type
	.byte	8                               // DW_AT_byte_size
	.byte	3                               // DW_AT_decl_file
	.byte	76                              // DW_AT_decl_line
	.byte	21                              // Abbrev [21] 0x6e6:0xc DW_TAG_member
	.word	.Linfo_string13                 // DW_AT_name
	.word	1816                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	78                              // DW_AT_decl_line
	.byte	0                               // DW_AT_data_member_location
	.byte	21                              // Abbrev [21] 0x6f2:0xc DW_TAG_member
	.word	.Linfo_string14                 // DW_AT_name
	.word	1821                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	79                              // DW_AT_decl_line
	.byte	0                               // DW_AT_data_member_location
	.byte	0                               // End Of Children Mark
	.byte	21                              // Abbrev [21] 0x6ff:0xc DW_TAG_member
	.word	.Linfo_string16                 // DW_AT_name
	.word	1837                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	81                              // DW_AT_decl_line
	.byte	24                              // DW_AT_data_member_location
	.byte	21                              // Abbrev [21] 0x70b:0xc DW_TAG_member
	.word	.Linfo_string17                 // DW_AT_name
	.word	1842                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	82                              // DW_AT_decl_line
	.byte	32                              // DW_AT_data_member_location
	.byte	0                               // End Of Children Mark
	.byte	22                              // Abbrev [22] 0x718:0x5 DW_TAG_pointer_type
	.word	219                             // DW_AT_type
	.byte	13                              // Abbrev [13] 0x71d:0xb DW_TAG_typedef
	.word	1832                            // DW_AT_type
	.word	.Linfo_string15                 // DW_AT_name
	.byte	1                               // DW_AT_decl_file
	.byte	43                              // DW_AT_decl_line
	.byte	22                              // Abbrev [22] 0x728:0x5 DW_TAG_pointer_type
	.word	1816                            // DW_AT_type
	.byte	22                              // Abbrev [22] 0x72d:0x5 DW_TAG_pointer_type
	.word	1717                            // DW_AT_type
	.byte	22                              // Abbrev [22] 0x732:0x5 DW_TAG_pointer_type
	.word	1847                            // DW_AT_type
	.byte	13                              // Abbrev [13] 0x737:0xb DW_TAG_typedef
	.word	1858                            // DW_AT_type
	.word	.Linfo_string21                 // DW_AT_name
	.byte	3                               // DW_AT_decl_file
	.byte	66                              // DW_AT_decl_line
	.byte	20                              // Abbrev [20] 0x742:0x21 DW_TAG_structure_type
	.word	.Linfo_string20                 // DW_AT_name
	.byte	16                              // DW_AT_byte_size
	.byte	3                               // DW_AT_decl_file
	.byte	62                              // DW_AT_decl_line
	.byte	21                              // Abbrev [21] 0x74a:0xc DW_TAG_member
	.word	.Linfo_string18                 // DW_AT_name
	.word	1717                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	64                              // DW_AT_decl_line
	.byte	0                               // DW_AT_data_member_location
	.byte	21                              // Abbrev [21] 0x756:0xc DW_TAG_member
	.word	.Linfo_string19                 // DW_AT_name
	.word	1891                            // DW_AT_type
	.byte	3                               // DW_AT_decl_file
	.byte	65                              // DW_AT_decl_line
	.byte	8                               // DW_AT_data_member_location
	.byte	0                               // End Of Children Mark
	.byte	22                              // Abbrev [22] 0x763:0x5 DW_TAG_pointer_type
	.word	1858                            // DW_AT_type
	.byte	14                              // Abbrev [14] 0x768:0x7 DW_TAG_base_type
	.word	.Linfo_string25                 // DW_AT_name
	.byte	5                               // DW_AT_encoding
	.byte	4                               // DW_AT_byte_size
	.byte	14                              // Abbrev [14] 0x76f:0x7 DW_TAG_base_type
	.word	.Linfo_string27                 // DW_AT_name
	.byte	2                               // DW_AT_encoding
	.byte	1                               // DW_AT_byte_size
	.byte	27                              // Abbrev [27] 0x776:0x2d DW_TAG_subprogram
	.byte	19                              // Abbrev [19] 0x777:0x15 DW_TAG_variable
	.word	.Linfo_string31                 // DW_AT_name
	.word	1955                            // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	161                             // DW_AT_decl_line
	.byte	9                               // DW_AT_location
	.byte	3
	.xword	prjm_eval_genrand_int32.mag01
	.byte	28                              // Abbrev [28] 0x78c:0xb DW_TAG_variable
	.word	.Linfo_string35                 // DW_AT_name
	.word	1996                            // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	165                             // DW_AT_decl_line
	.byte	28                              // Abbrev [28] 0x797:0xb DW_TAG_variable
	.word	.Linfo_string36                 // DW_AT_name
	.word	2009                            // DW_AT_type
	.byte	2                               // DW_AT_decl_file
	.byte	166                             // DW_AT_decl_line
	.byte	0                               // End Of Children Mark
	.byte	16                              // Abbrev [16] 0x7a3:0xc DW_TAG_array_type
	.word	1967                            // DW_AT_type
	.byte	17                              // Abbrev [17] 0x7a8:0x6 DW_TAG_subrange_type
	.word	273                             // DW_AT_type
	.byte	2                               // DW_AT_count
	.byte	0                               // End Of Children Mark
	.byte	13                              // Abbrev [13] 0x7af:0xb DW_TAG_typedef
	.word	1978                            // DW_AT_type
	.word	.Linfo_string34                 // DW_AT_name
	.byte	4                               // DW_AT_decl_file
	.byte	65                              // DW_AT_decl_line
	.byte	13                              // Abbrev [13] 0x7ba:0xb DW_TAG_typedef
	.word	1989                            // DW_AT_type
	.word	.Linfo_string33                 // DW_AT_name
	.byte	4                               // DW_AT_decl_file
	.byte	41                              // DW_AT_decl_line
	.byte	14                              // Abbrev [14] 0x7c5:0x7 DW_TAG_base_type
	.word	.Linfo_string32                 // DW_AT_name
	.byte	7                               // DW_AT_encoding
	.byte	4                               // DW_AT_byte_size
	.byte	16                              // Abbrev [16] 0x7cc:0xd DW_TAG_array_type
	.word	1967                            // DW_AT_type
	.byte	29                              // Abbrev [29] 0x7d1:0x7 DW_TAG_subrange_type
	.word	273                             // DW_AT_type
	.hword	624                             // DW_AT_count
	.byte	0                               // End Of Children Mark
	.byte	13                              // Abbrev [13] 0x7d9:0xb DW_TAG_typedef
	.word	2020                            // DW_AT_type
	.word	.Linfo_string38                 // DW_AT_name
	.byte	4                               // DW_AT_decl_file
	.byte	64                              // DW_AT_decl_line
	.byte	13                              // Abbrev [13] 0x7e4:0xb DW_TAG_typedef
	.word	1896                            // DW_AT_type
	.word	.Linfo_string37                 // DW_AT_name
	.byte	4                               // DW_AT_decl_file
	.byte	40                              // DW_AT_decl_line
	.byte	13                              // Abbrev [13] 0x7ef:0xb DW_TAG_typedef
	.word	2042                            // DW_AT_type
	.word	.Linfo_string42                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	18                              // DW_AT_decl_line
	.byte	13                              // Abbrev [13] 0x7fa:0xb DW_TAG_typedef
	.word	2053                            // DW_AT_type
	.word	.Linfo_string41                 // DW_AT_name
	.byte	4                               // DW_AT_decl_file
	.byte	67                              // DW_AT_decl_line
	.byte	13                              // Abbrev [13] 0x805:0xb DW_TAG_typedef
	.word	2064                            // DW_AT_type
	.word	.Linfo_string40                 // DW_AT_name
	.byte	4                               // DW_AT_decl_file
	.byte	43                              // DW_AT_decl_line
	.byte	14                              // Abbrev [14] 0x810:0x7 DW_TAG_base_type
	.word	.Linfo_string39                 // DW_AT_name
	.byte	5                               // DW_AT_encoding
	.byte	8                               // DW_AT_byte_size
	.byte	30                              // Abbrev [30] 0x817:0x30 DW_TAG_subprogram
	.xword	.Lfunc_begin0                   // DW_AT_low_pc
	.word	.Lfunc_end0-.Lfunc_begin0       // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	111
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string71                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	151                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	31                              // Abbrev [31] 0x82c:0xd DW_TAG_formal_parameter
	.byte	1                               // DW_AT_location
	.byte	80
	.word	.Linfo_string17                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	151                             // DW_AT_decl_line
	.word	10301                           // DW_AT_type
	.byte	31                              // Abbrev [31] 0x839:0xd DW_TAG_formal_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.word	.Linfo_string136                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	151                             // DW_AT_decl_line
	.word	10338                           // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	30                              // Abbrev [30] 0x847:0x30 DW_TAG_subprogram
	.xword	.Lfunc_begin1                   // DW_AT_low_pc
	.word	.Lfunc_end1-.Lfunc_begin1       // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	111
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string72                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	219                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	31                              // Abbrev [31] 0x85c:0xd DW_TAG_formal_parameter
	.byte	1                               // DW_AT_location
	.byte	80
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	219                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	31                              // Abbrev [31] 0x869:0xd DW_TAG_formal_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	219                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	30                              // Abbrev [30] 0x877:0x30 DW_TAG_subprogram
	.xword	.Lfunc_begin2                   // DW_AT_low_pc
	.word	.Lfunc_end2-.Lfunc_begin2       // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	111
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string73                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	226                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	31                              // Abbrev [31] 0x88c:0xd DW_TAG_formal_parameter
	.byte	1                               // DW_AT_location
	.byte	80
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	226                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	31                              // Abbrev [31] 0x899:0xd DW_TAG_formal_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	226                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	30                              // Abbrev [30] 0x8a7:0x64 DW_TAG_subprogram
	.xword	.Lfunc_begin3                   // DW_AT_low_pc
	.word	.Lfunc_end3-.Lfunc_begin3       // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string74                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	236                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	32                              // Abbrev [32] 0x8bc:0xf DW_TAG_formal_parameter
	.word	.Ldebug_loc0                    // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	236                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	32                              // Abbrev [32] 0x8cb:0xf DW_TAG_formal_parameter
	.word	.Ldebug_loc1                    // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	236                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	33                              // Abbrev [33] 0x8da:0xf DW_TAG_variable
	.word	.Ldebug_loc2                    // DW_AT_location
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	242                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	33                              // Abbrev [33] 0x8e9:0xf DW_TAG_variable
	.word	.Ldebug_loc3                    // DW_AT_location
	.word	.Linfo_string140                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	243                             // DW_AT_decl_line
	.word	1842                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x8f8:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp11                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x903:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x90b:0x98 DW_TAG_subprogram
	.xword	.Lfunc_begin4                   // DW_AT_low_pc
	.word	.Lfunc_end4-.Lfunc_begin4       // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string75                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	258                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x921:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc4                    // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	258                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x931:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc5                    // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	258                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x941:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	263                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	6                               // Abbrev [6] 0x950:0x10 DW_TAG_variable
	.word	.Ldebug_loc6                    // DW_AT_location
	.word	.Linfo_string141                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	266                             // DW_AT_decl_line
	.word	2031                            // DW_AT_type
	.byte	34                              // Abbrev [34] 0x960:0x1e DW_TAG_lexical_block
	.xword	.Ltmp25                         // DW_AT_low_pc
	.word	.Ltmp29-.Ltmp25                 // DW_AT_high_pc
	.byte	6                               // Abbrev [6] 0x96d:0x10 DW_TAG_variable
	.word	.Ldebug_loc7                    // DW_AT_location
	.word	.Linfo_string142                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	273                             // DW_AT_decl_line
	.word	2031                            // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x97e:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp23                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x989:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x990:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp27                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x99b:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x9a3:0x68 DW_TAG_subprogram
	.xword	.Lfunc_begin5                   // DW_AT_low_pc
	.word	.Lfunc_end5-.Lfunc_begin5       // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string76                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	283                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x9b9:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc8                    // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	283                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x9c9:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc9                    // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	283                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x9d9:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	288                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	6                               // Abbrev [6] 0x9e8:0x10 DW_TAG_variable
	.word	.Ldebug_loc10                   // DW_AT_location
	.word	.Linfo_string141                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	289                             // DW_AT_decl_line
	.word	2031                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x9f8:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp39                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xa03:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0xa0b:0x6a DW_TAG_subprogram
	.xword	.Lfunc_begin6                   // DW_AT_low_pc
	.word	.Lfunc_end6-.Lfunc_begin6       // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string77                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	298                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0xa21:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc11                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	298                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0xa31:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc12                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	298                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xa41:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string143                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	302                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0xa50:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp50                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xa5b:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0xa62:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp54                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xa6d:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	132
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0xa75:0x6a DW_TAG_subprogram
	.xword	.Lfunc_begin7                   // DW_AT_low_pc
	.word	.Lfunc_end7-.Lfunc_begin7       // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string78                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	314                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0xa8b:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc13                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	314                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0xa9b:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc14                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	314                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xaab:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	319                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0xaba:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp63                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xac5:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0xacc:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp65                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xad7:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	132
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0xadf:0x7c DW_TAG_subprogram
	.xword	.Lfunc_begin8                   // DW_AT_low_pc
	.word	.Lfunc_end8-.Lfunc_begin8       // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string79                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	325                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0xaf5:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc15                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	325                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0xb05:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc16                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	325                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xb15:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	330                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0xb24:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp73                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xb2f:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0xb36:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp74                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xb41:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0xb48:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp76                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xb53:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	132
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0xb5b:0x6b DW_TAG_subprogram
	.xword	.Lfunc_begin9                   // DW_AT_low_pc
	.word	.Lfunc_end9-.Lfunc_begin9       // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string80                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	337                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0xb71:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc17                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	337                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0xb81:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc18                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	337                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xb91:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	342                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0xba0:0x13 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp84                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xbab:0x7 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	3                               // DW_AT_GNU_call_site_value
	.byte	243
	.byte	1
	.byte	81
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0xbb3:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp85                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xbbe:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0xbc6:0x75 DW_TAG_subprogram
	.xword	.Lfunc_begin10                  // DW_AT_low_pc
	.word	.Lfunc_end10-.Lfunc_begin10     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string81                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	352                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0xbdc:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc19                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	352                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0xbec:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc20                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	352                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xbfc:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string144                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	358                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	6                               // Abbrev [6] 0xc0b:0x10 DW_TAG_variable
	.word	.Ldebug_loc21                   // DW_AT_location
	.word	.Linfo_string145                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	362                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0xc1b:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp94                         // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xc26:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	35                              // Abbrev [35] 0xc2d:0xd DW_TAG_GNU_call_site
	.word	3131                            // DW_AT_abstract_origin
	.xword	.Ltmp95                         // DW_AT_low_pc
	.byte	0                               // End Of Children Mark
	.byte	36                              // Abbrev [36] 0xc3b:0x16 DW_TAG_subprogram
	.word	.Linfo_string43                 // DW_AT_name
	.byte	5                               // DW_AT_decl_file
	.byte	56                              // DW_AT_decl_line
                                        // DW_AT_prototyped
	.word	1816                            // DW_AT_type
                                        // DW_AT_declaration
                                        // DW_AT_external
	.byte	24                              // Abbrev [24] 0xc46:0x5 DW_TAG_formal_parameter
	.word	1821                            // DW_AT_type
	.byte	24                              // Abbrev [24] 0xc4b:0x5 DW_TAG_formal_parameter
	.word	1896                            // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0xc51:0x57 DW_TAG_subprogram
	.xword	.Lfunc_begin11                  // DW_AT_low_pc
	.word	.Lfunc_end11-.Lfunc_begin11     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string82                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	372                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0xc67:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc22                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	372                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0xc77:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc23                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	372                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0xc87:0x13 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp106                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xc92:0x7 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	3                               // DW_AT_GNU_call_site_value
	.byte	243
	.byte	1
	.byte	81
	.byte	0                               // End Of Children Mark
	.byte	37                              // Abbrev [37] 0xc9a:0xd DW_TAG_GNU_call_site
	.word	3240                            // DW_AT_abstract_origin
                                        // DW_AT_GNU_tail_call
	.xword	.Ltmp109                        // DW_AT_low_pc
	.byte	0                               // End Of Children Mark
	.byte	38                              // Abbrev [38] 0xca8:0x12 DW_TAG_subprogram
	.word	.Linfo_string44                 // DW_AT_name
	.byte	5                               // DW_AT_decl_file
	.byte	48                              // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_declaration
                                        // DW_AT_external
	.byte	24                              // Abbrev [24] 0xcaf:0x5 DW_TAG_formal_parameter
	.word	1821                            // DW_AT_type
	.byte	24                              // Abbrev [24] 0xcb4:0x5 DW_TAG_formal_parameter
	.word	1896                            // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0xcba:0xc5 DW_TAG_subprogram
	.xword	.Lfunc_begin12                  // DW_AT_low_pc
	.word	.Lfunc_end12-.Lfunc_begin12     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string83                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	383                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0xcd0:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc24                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	383                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0xce0:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc25                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	383                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xcf0:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string146                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	388                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0xcff:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string136                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	389                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0xd0e:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string147                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	390                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xd1d:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string148                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	391                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xd2c:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string149                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	392                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0xd3b:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp114                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xd46:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0xd4d:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp115                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xd58:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0xd5f:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp116                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xd6a:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	35                              // Abbrev [35] 0xd71:0xd DW_TAG_GNU_call_site
	.word	3455                            // DW_AT_abstract_origin
	.xword	.Ltmp117                        // DW_AT_low_pc
	.byte	0                               // End Of Children Mark
	.byte	36                              // Abbrev [36] 0xd7f:0x20 DW_TAG_subprogram
	.word	.Linfo_string45                 // DW_AT_name
	.byte	5                               // DW_AT_decl_file
	.byte	66                              // DW_AT_decl_line
                                        // DW_AT_prototyped
	.word	1816                            // DW_AT_type
                                        // DW_AT_declaration
                                        // DW_AT_external
	.byte	24                              // Abbrev [24] 0xd8a:0x5 DW_TAG_formal_parameter
	.word	1821                            // DW_AT_type
	.byte	24                              // Abbrev [24] 0xd8f:0x5 DW_TAG_formal_parameter
	.word	1816                            // DW_AT_type
	.byte	24                              // Abbrev [24] 0xd94:0x5 DW_TAG_formal_parameter
	.word	1816                            // DW_AT_type
	.byte	24                              // Abbrev [24] 0xd99:0x5 DW_TAG_formal_parameter
	.word	1816                            // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0xd9f:0xc5 DW_TAG_subprogram
	.xword	.Lfunc_begin13                  // DW_AT_low_pc
	.word	.Lfunc_end13-.Lfunc_begin13     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string84                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	401                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0xdb5:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc26                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	401                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0xdc5:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc27                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	401                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xdd5:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string12                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	406                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0xde4:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string136                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	407                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0xdf3:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string147                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	408                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xe02:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	409                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xe11:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string149                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	410                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0xe20:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp126                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xe2b:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0xe32:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp127                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xe3d:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0xe44:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp128                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xe4f:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	35                              // Abbrev [35] 0xe56:0xd DW_TAG_GNU_call_site
	.word	3684                            // DW_AT_abstract_origin
	.xword	.Ltmp129                        // DW_AT_low_pc
	.byte	0                               // End Of Children Mark
	.byte	36                              // Abbrev [36] 0xe64:0x20 DW_TAG_subprogram
	.word	.Linfo_string46                 // DW_AT_name
	.byte	5                               // DW_AT_decl_file
	.byte	79                              // DW_AT_decl_line
                                        // DW_AT_prototyped
	.word	1816                            // DW_AT_type
                                        // DW_AT_declaration
                                        // DW_AT_external
	.byte	24                              // Abbrev [24] 0xe6f:0x5 DW_TAG_formal_parameter
	.word	1821                            // DW_AT_type
	.byte	24                              // Abbrev [24] 0xe74:0x5 DW_TAG_formal_parameter
	.word	1816                            // DW_AT_type
	.byte	24                              // Abbrev [24] 0xe79:0x5 DW_TAG_formal_parameter
	.word	1816                            // DW_AT_type
	.byte	24                              // Abbrev [24] 0xe7e:0x5 DW_TAG_formal_parameter
	.word	1816                            // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0xe84:0x58 DW_TAG_subprogram
	.xword	.Lfunc_begin14                  // DW_AT_low_pc
	.word	.Lfunc_end14-.Lfunc_begin14     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string85                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	423                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0xe9a:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc28                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	423                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0xeaa:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc29                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	423                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xeba:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	428                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0xec9:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp136                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xed4:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0xedc:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin15                  // DW_AT_low_pc
	.word	.Lfunc_end15-.Lfunc_begin15     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string86                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	435                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0xef2:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc30                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	435                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0xf02:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc31                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	435                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xf12:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	439                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0xf21:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	440                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0xf30:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	441                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xf3f:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	442                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0xf4e:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp144                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xf59:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0xf60:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp145                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xf6b:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0xf73:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin16                  // DW_AT_low_pc
	.word	.Lfunc_end16-.Lfunc_begin16     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string87                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	450                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0xf89:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc32                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	450                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0xf99:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc33                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	450                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xfa9:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	454                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0xfb8:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	455                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0xfc7:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	456                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0xfd6:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	457                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0xfe5:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp153                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0xff0:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0xff7:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp154                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1002:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x100a:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin17                  // DW_AT_low_pc
	.word	.Lfunc_end17-.Lfunc_begin17     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string88                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	464                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1020:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc34                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	464                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1030:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc35                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	464                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1040:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	468                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x104f:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	469                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x105e:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	470                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x106d:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	471                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x107c:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp162                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1087:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x108e:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp163                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1099:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x10a1:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin18                  // DW_AT_low_pc
	.word	.Lfunc_end18-.Lfunc_begin18     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string89                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	479                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x10b7:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc36                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	479                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x10c7:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc37                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	479                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x10d7:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	483                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x10e6:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	484                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x10f5:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	485                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1104:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	486                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1113:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp171                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x111e:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1125:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp172                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1130:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1138:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin19                  // DW_AT_low_pc
	.word	.Lfunc_end19-.Lfunc_begin19     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string90                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	494                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x114e:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc38                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	494                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x115e:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc39                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	494                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x116e:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	498                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x117d:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	499                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x118c:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	500                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x119b:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	501                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x11aa:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp180                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x11b5:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x11bc:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp181                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x11c7:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x11cf:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin20                  // DW_AT_low_pc
	.word	.Lfunc_end20-.Lfunc_begin20     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string91                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	509                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x11e5:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc40                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	509                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x11f5:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc41                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	509                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1205:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	513                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1214:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	514                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1223:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	515                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1232:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	516                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1241:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp189                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x124c:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1253:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp190                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x125e:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1266:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin21                  // DW_AT_low_pc
	.word	.Lfunc_end21-.Lfunc_begin21     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string92                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	524                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x127c:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc42                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	524                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x128c:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc43                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	524                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x129c:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	528                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x12ab:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	529                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x12ba:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	530                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x12c9:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	531                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x12d8:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp198                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x12e3:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x12ea:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp199                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x12f5:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x12fd:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin22                  // DW_AT_low_pc
	.word	.Lfunc_end22-.Lfunc_begin22     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string93                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	539                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1313:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc44                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	539                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1323:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc45                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	539                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1333:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	543                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1342:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	544                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1351:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	545                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1360:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	546                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x136f:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp207                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x137a:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1381:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp208                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x138c:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1394:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin23                  // DW_AT_low_pc
	.word	.Lfunc_end23-.Lfunc_begin23     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string94                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	554                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x13aa:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc46                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	554                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x13ba:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc47                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	554                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x13ca:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	558                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x13d9:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	559                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x13e8:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	560                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x13f7:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	561                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1406:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp216                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1411:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1418:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp217                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1423:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x142b:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin24                  // DW_AT_low_pc
	.word	.Lfunc_end24-.Lfunc_begin24     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string95                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	569                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1441:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc48                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	569                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1451:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc49                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	569                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1461:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	573                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1470:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	574                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x147f:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	575                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x148e:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	576                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x149d:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp225                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x14a8:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x14af:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp226                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x14ba:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	39                              // Abbrev [39] 0x14c2:0x86 DW_TAG_subprogram
	.word	.Linfo_string47                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	618                             // DW_AT_decl_line
                                        // DW_AT_prototyped
	.word	219                             // DW_AT_type
	.byte	1                               // DW_AT_inline
	.byte	40                              // Abbrev [40] 0x14cf:0xc DW_TAG_formal_parameter
	.word	.Linfo_string48                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	618                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	40                              // Abbrev [40] 0x14db:0xc DW_TAG_formal_parameter
	.word	.Linfo_string49                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	618                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	7                               // Abbrev [7] 0x14e7:0xc DW_TAG_variable
	.word	.Linfo_string50                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	621                             // DW_AT_decl_line
	.word	5448                            // DW_AT_type
	.byte	7                               // Abbrev [7] 0x14f3:0xc DW_TAG_variable
	.word	.Linfo_string55                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	623                             // DW_AT_decl_line
	.word	5448                            // DW_AT_type
	.byte	7                               // Abbrev [7] 0x14ff:0xc DW_TAG_variable
	.word	.Linfo_string56                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	622                             // DW_AT_decl_line
	.word	5448                            // DW_AT_type
	.byte	7                               // Abbrev [7] 0x150b:0xc DW_TAG_variable
	.word	.Linfo_string57                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	633                             // DW_AT_decl_line
	.word	5494                            // DW_AT_type
	.byte	7                               // Abbrev [7] 0x1517:0xc DW_TAG_variable
	.word	.Linfo_string58                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	638                             // DW_AT_decl_line
	.word	5494                            // DW_AT_type
	.byte	7                               // Abbrev [7] 0x1523:0xc DW_TAG_variable
	.word	.Linfo_string59                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	634                             // DW_AT_decl_line
	.word	5494                            // DW_AT_type
	.byte	7                               // Abbrev [7] 0x152f:0xc DW_TAG_variable
	.word	.Linfo_string60                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	642                             // DW_AT_decl_line
	.word	214                             // DW_AT_type
	.byte	7                               // Abbrev [7] 0x153b:0xc DW_TAG_variable
	.word	.Linfo_string61                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	620                             // DW_AT_decl_line
	.word	5448                            // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	12                              // Abbrev [12] 0x1548:0x5 DW_TAG_const_type
	.word	5453                            // DW_AT_type
	.byte	41                              // Abbrev [41] 0x154d:0xc DW_TAG_typedef
	.word	5465                            // DW_AT_type
	.word	.Linfo_string54                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	603                             // DW_AT_decl_line
	.byte	13                              // Abbrev [13] 0x1559:0xb DW_TAG_typedef
	.word	5476                            // DW_AT_type
	.word	.Linfo_string53                 // DW_AT_name
	.byte	4                               // DW_AT_decl_file
	.byte	68                              // DW_AT_decl_line
	.byte	13                              // Abbrev [13] 0x1564:0xb DW_TAG_typedef
	.word	5487                            // DW_AT_type
	.word	.Linfo_string52                 // DW_AT_name
	.byte	4                               // DW_AT_decl_file
	.byte	44                              // DW_AT_decl_line
	.byte	14                              // Abbrev [14] 0x156f:0x7 DW_TAG_base_type
	.word	.Linfo_string51                 // DW_AT_name
	.byte	7                               // DW_AT_encoding
	.byte	8                               // DW_AT_byte_size
	.byte	12                              // Abbrev [12] 0x1576:0x5 DW_TAG_const_type
	.word	2031                            // DW_AT_type
	.byte	2                               // Abbrev [2] 0x157b:0xed DW_TAG_subprogram
	.xword	.Lfunc_begin25                  // DW_AT_low_pc
	.word	.Lfunc_end25-.Lfunc_begin25     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string96                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	647                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1591:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc50                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	647                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x15a1:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc51                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	647                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x15b1:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	651                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x15c0:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	652                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x15cf:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	653                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x15de:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	654                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	42                              // Abbrev [42] 0x15ed:0x56 DW_TAG_inlined_subroutine
	.word	5314                            // DW_AT_abstract_origin
	.word	.Ldebug_ranges0                 // DW_AT_ranges
	.byte	2                               // DW_AT_call_file
	.hword	659                             // DW_AT_call_line
	.byte	5                               // DW_AT_call_column
	.byte	43                              // Abbrev [43] 0x15fa:0x9 DW_TAG_formal_parameter
	.word	.Ldebug_loc52                   // DW_AT_location
	.word	5339                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x1603:0x9 DW_TAG_variable
	.word	.Ldebug_loc53                   // DW_AT_location
	.word	5351                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x160c:0x9 DW_TAG_variable
	.word	.Ldebug_loc54                   // DW_AT_location
	.word	5363                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x1615:0x9 DW_TAG_variable
	.word	.Ldebug_loc55                   // DW_AT_location
	.word	5375                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x161e:0x9 DW_TAG_variable
	.word	.Ldebug_loc56                   // DW_AT_location
	.word	5387                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x1627:0x9 DW_TAG_variable
	.word	.Ldebug_loc57                   // DW_AT_location
	.word	5399                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x1630:0x9 DW_TAG_variable
	.word	.Ldebug_loc58                   // DW_AT_location
	.word	5411                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x1639:0x9 DW_TAG_variable
	.word	.Ldebug_loc59                   // DW_AT_location
	.word	5423                            // DW_AT_abstract_origin
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1643:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp237                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x164e:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1655:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp238                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1660:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1668:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin26                  // DW_AT_low_pc
	.word	.Lfunc_end26-.Lfunc_begin26     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string97                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	662                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x167e:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc60                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	662                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x168e:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc61                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	662                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x169e:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	104
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	666                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x16ad:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	667                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x16bc:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	668                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x16cb:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	669                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x16da:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp271                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x16e5:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	24
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x16ec:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp274                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x16f7:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x16ff:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin27                  // DW_AT_low_pc
	.word	.Lfunc_end27-.Lfunc_begin27     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string98                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	689                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1715:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc62                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	689                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1725:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc63                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	689                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1735:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	104
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	693                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1744:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	694                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1753:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	695                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1762:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	696                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1771:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp284                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x177c:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	24
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1783:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp287                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x178e:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1796:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin28                  // DW_AT_low_pc
	.word	.Lfunc_end28-.Lfunc_begin28     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string99                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	716                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x17ac:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc64                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	716                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x17bc:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc65                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	716                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x17cc:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	720                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x17db:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	721                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x17ea:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	722                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x17f9:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	723                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1808:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp297                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1813:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x181a:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp298                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1825:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x182d:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin29                  // DW_AT_low_pc
	.word	.Lfunc_end29-.Lfunc_begin29     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string100                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	732                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1843:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc66                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	732                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1853:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc67                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	732                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1863:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	736                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1872:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	737                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1881:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	738                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1890:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	739                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x189f:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp308                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x18aa:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x18b1:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp309                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x18bc:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x18c4:0x67 DW_TAG_subprogram
	.xword	.Lfunc_begin30                  // DW_AT_low_pc
	.word	.Lfunc_end30-.Lfunc_begin30     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string101                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	748                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x18da:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc68                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	748                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x18ea:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc69                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	748                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x18fa:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	752                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1909:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	753                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1918:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp318                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1923:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x192b:0x7a DW_TAG_subprogram
	.xword	.Lfunc_begin31                  // DW_AT_low_pc
	.word	.Lfunc_end31-.Lfunc_begin31     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string102                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	760                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1941:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc70                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	760                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1951:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc71                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	760                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1961:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	764                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1970:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	765                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x197f:0x13 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp326                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x198a:0x7 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	3                               // DW_AT_GNU_call_site_value
	.byte	243
	.byte	1
	.byte	81
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1992:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp327                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x199d:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x19a5:0x7a DW_TAG_subprogram
	.xword	.Lfunc_begin32                  // DW_AT_low_pc
	.word	.Lfunc_end32-.Lfunc_begin32     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string103                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	773                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x19bb:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc72                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	773                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x19cb:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc73                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	773                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x19db:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	777                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x19ea:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	778                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x19f9:0x13 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp335                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1a04:0x7 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	3                               // DW_AT_GNU_call_site_value
	.byte	243
	.byte	1
	.byte	81
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1a0c:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp336                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1a17:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1a1f:0x7a DW_TAG_subprogram
	.xword	.Lfunc_begin33                  // DW_AT_low_pc
	.word	.Lfunc_end33-.Lfunc_begin33     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string104                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	786                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1a35:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc74                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	786                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1a45:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc75                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	786                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1a55:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	790                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1a64:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	791                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1a73:0x13 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp344                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1a7e:0x7 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	3                               // DW_AT_GNU_call_site_value
	.byte	243
	.byte	1
	.byte	81
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1a86:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp345                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1a91:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1a99:0x7a DW_TAG_subprogram
	.xword	.Lfunc_begin34                  // DW_AT_low_pc
	.word	.Lfunc_end34-.Lfunc_begin34     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string105                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	799                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1aaf:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc76                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	799                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1abf:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc77                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	799                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1acf:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	803                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1ade:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	804                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1aed:0x13 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp353                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1af8:0x7 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	3                               // DW_AT_GNU_call_site_value
	.byte	243
	.byte	1
	.byte	81
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1b00:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp354                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1b0b:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1b13:0x7a DW_TAG_subprogram
	.xword	.Lfunc_begin35                  // DW_AT_low_pc
	.word	.Lfunc_end35-.Lfunc_begin35     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string106                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	818                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1b29:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc78                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	818                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1b39:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc79                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	818                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1b49:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	822                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1b58:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	823                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1b67:0x13 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp367                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1b72:0x7 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	3                               // DW_AT_GNU_call_site_value
	.byte	243
	.byte	1
	.byte	81
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1b7a:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp368                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1b85:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1b8d:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin36                  // DW_AT_low_pc
	.word	.Lfunc_end36-.Lfunc_begin36     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string107                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	831                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1ba3:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc80                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	831                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1bb3:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc81                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	831                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1bc3:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	835                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1bd2:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	836                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1be1:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	837                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1bf0:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	838                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1bff:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp376                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1c0a:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	24
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1c11:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp377                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1c1c:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1c24:0x7a DW_TAG_subprogram
	.xword	.Lfunc_begin37                  // DW_AT_low_pc
	.word	.Lfunc_end37-.Lfunc_begin37     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string108                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	846                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1c3a:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc82                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	846                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1c4a:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc83                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	846                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1c5a:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	850                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1c69:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	851                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1c78:0x13 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp385                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1c83:0x7 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	3                               // DW_AT_GNU_call_site_value
	.byte	243
	.byte	1
	.byte	81
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1c8b:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp386                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1c96:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1c9e:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin38                  // DW_AT_low_pc
	.word	.Lfunc_end38-.Lfunc_begin38     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string109                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	859                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1cb4:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc84                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	859                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1cc4:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc85                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	859                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1cd4:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string150                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	863                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1ce3:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string152                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	864                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1cf2:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	865                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1d01:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	866                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1d10:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp394                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1d1b:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	24
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1d22:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp395                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1d2d:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1d35:0xd0 DW_TAG_subprogram
	.xword	.Lfunc_begin39                  // DW_AT_low_pc
	.word	.Lfunc_end39-.Lfunc_begin39     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string110                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	874                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1d4b:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc86                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	874                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1d5b:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc87                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	874                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1d6b:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	878                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1d7a:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	879                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	42                              // Abbrev [42] 0x1d89:0x56 DW_TAG_inlined_subroutine
	.word	5314                            // DW_AT_abstract_origin
	.word	.Ldebug_ranges1                 // DW_AT_ranges
	.byte	2                               // DW_AT_call_file
	.hword	884                             // DW_AT_call_line
	.byte	5                               // DW_AT_call_column
	.byte	43                              // Abbrev [43] 0x1d96:0x9 DW_TAG_formal_parameter
	.word	.Ldebug_loc88                   // DW_AT_location
	.word	5339                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x1d9f:0x9 DW_TAG_variable
	.word	.Ldebug_loc89                   // DW_AT_location
	.word	5351                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x1da8:0x9 DW_TAG_variable
	.word	.Ldebug_loc90                   // DW_AT_location
	.word	5363                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x1db1:0x9 DW_TAG_variable
	.word	.Ldebug_loc91                   // DW_AT_location
	.word	5375                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x1dba:0x9 DW_TAG_variable
	.word	.Ldebug_loc92                   // DW_AT_location
	.word	5387                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x1dc3:0x9 DW_TAG_variable
	.word	.Ldebug_loc93                   // DW_AT_location
	.word	5399                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x1dcc:0x9 DW_TAG_variable
	.word	.Ldebug_loc94                   // DW_AT_location
	.word	5411                            // DW_AT_abstract_origin
	.byte	44                              // Abbrev [44] 0x1dd5:0x9 DW_TAG_variable
	.word	.Ldebug_loc95                   // DW_AT_location
	.word	5423                            // DW_AT_abstract_origin
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1ddf:0x13 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp403                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1dea:0x7 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	3                               // DW_AT_GNU_call_site_value
	.byte	243
	.byte	1
	.byte	81
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1df2:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp404                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1dfd:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1e05:0x86 DW_TAG_subprogram
	.xword	.Lfunc_begin40                  // DW_AT_low_pc
	.word	.Lfunc_end40-.Lfunc_begin40     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string111                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	887                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1e1b:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc96                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	887                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1e2b:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc97                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	887                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1e3b:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string151                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	891                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1e4a:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string153                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	892                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	7                               // Abbrev [7] 0x1e59:0xc DW_TAG_variable
	.word	.Linfo_string154                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	903                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1e65:0x13 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp437                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1e70:0x7 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	3                               // DW_AT_GNU_call_site_value
	.byte	243
	.byte	1
	.byte	81
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x1e78:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp438                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1e83:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1e8b:0x58 DW_TAG_subprogram
	.xword	.Lfunc_begin41                  // DW_AT_low_pc
	.word	.Lfunc_end41-.Lfunc_begin41     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string112                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	910                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1ea1:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc98                   // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	910                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1eb1:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc99                   // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	910                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1ec1:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string155                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	915                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1ed0:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp450                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1edb:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1ee3:0x58 DW_TAG_subprogram
	.xword	.Lfunc_begin42                  // DW_AT_low_pc
	.word	.Lfunc_end42-.Lfunc_begin42     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string113                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	922                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1ef9:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc100                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	922                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1f09:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc101                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	922                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1f19:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string155                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	927                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1f28:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp458                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1f33:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1f3b:0x65 DW_TAG_subprogram
	.xword	.Lfunc_begin43                  // DW_AT_low_pc
	.word	.Lfunc_end43-.Lfunc_begin43     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string114                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	934                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1f51:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc102                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	934                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1f61:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc103                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	934                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1f71:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string155                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	939                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1f80:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp466                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x1f8b:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	35                              // Abbrev [35] 0x1f92:0xd DW_TAG_GNU_call_site
	.word	8096                            // DW_AT_abstract_origin
	.xword	.Ltmp467                        // DW_AT_low_pc
	.byte	0                               // End Of Children Mark
	.byte	36                              // Abbrev [36] 0x1fa0:0x11 DW_TAG_subprogram
	.word	.Linfo_string62                 // DW_AT_name
	.byte	6                               // DW_AT_decl_file
	.byte	100                             // DW_AT_decl_line
                                        // DW_AT_prototyped
	.word	230                             // DW_AT_type
                                        // DW_AT_declaration
                                        // DW_AT_external
	.byte	24                              // Abbrev [24] 0x1fab:0x5 DW_TAG_formal_parameter
	.word	230                             // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x1fb1:0x65 DW_TAG_subprogram
	.xword	.Lfunc_begin44                  // DW_AT_low_pc
	.word	.Lfunc_end44-.Lfunc_begin44     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string115                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	946                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x1fc7:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc104                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	946                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x1fd7:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc105                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	946                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x1fe7:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string155                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	951                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x1ff6:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp474                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x2001:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	35                              // Abbrev [35] 0x2008:0xd DW_TAG_GNU_call_site
	.word	8214                            // DW_AT_abstract_origin
	.xword	.Ltmp476                        // DW_AT_low_pc
	.byte	0                               // End Of Children Mark
	.byte	36                              // Abbrev [36] 0x2016:0x11 DW_TAG_subprogram
	.word	.Linfo_string63                 // DW_AT_name
	.byte	6                               // DW_AT_decl_file
	.byte	80                              // DW_AT_decl_line
                                        // DW_AT_prototyped
	.word	230                             // DW_AT_type
                                        // DW_AT_declaration
                                        // DW_AT_external
	.byte	24                              // Abbrev [24] 0x2021:0x5 DW_TAG_formal_parameter
	.word	230                             // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x2027:0x65 DW_TAG_subprogram
	.xword	.Lfunc_begin45                  // DW_AT_low_pc
	.word	.Lfunc_end45-.Lfunc_begin45     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string116                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	964                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x203d:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc106                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	964                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x204d:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc107                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	964                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x205d:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string155                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	969                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x206c:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp483                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x2077:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	35                              // Abbrev [35] 0x207e:0xd DW_TAG_GNU_call_site
	.word	8332                            // DW_AT_abstract_origin
	.xword	.Ltmp485                        // DW_AT_low_pc
	.byte	0                               // End Of Children Mark
	.byte	36                              // Abbrev [36] 0x208c:0x11 DW_TAG_subprogram
	.word	.Linfo_string64                 // DW_AT_name
	.byte	6                               // DW_AT_decl_file
	.byte	76                              // DW_AT_decl_line
                                        // DW_AT_prototyped
	.word	230                             // DW_AT_type
                                        // DW_AT_declaration
                                        // DW_AT_external
	.byte	24                              // Abbrev [24] 0x2097:0x5 DW_TAG_formal_parameter
	.word	230                             // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x209d:0x65 DW_TAG_subprogram
	.xword	.Lfunc_begin46                  // DW_AT_low_pc
	.word	.Lfunc_end46-.Lfunc_begin46     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string117                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	982                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x20b3:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc108                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	982                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x20c3:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc109                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	982                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x20d3:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string155                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	987                             // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x20e2:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp492                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x20ed:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	35                              // Abbrev [35] 0x20f4:0xd DW_TAG_GNU_call_site
	.word	8450                            // DW_AT_abstract_origin
	.xword	.Ltmp493                        // DW_AT_low_pc
	.byte	0                               // End Of Children Mark
	.byte	36                              // Abbrev [36] 0x2102:0x11 DW_TAG_subprogram
	.word	.Linfo_string65                 // DW_AT_name
	.byte	6                               // DW_AT_decl_file
	.byte	84                              // DW_AT_decl_line
                                        // DW_AT_prototyped
	.word	230                             // DW_AT_type
                                        // DW_AT_declaration
                                        // DW_AT_external
	.byte	24                              // Abbrev [24] 0x210d:0x5 DW_TAG_formal_parameter
	.word	230                             // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x2113:0xa4 DW_TAG_subprogram
	.xword	.Lfunc_begin47                  // DW_AT_low_pc
	.word	.Lfunc_end47-.Lfunc_begin47     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string118                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	994                             // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x2129:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc110                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	994                             // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x2139:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc111                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	994                             // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x2149:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string156                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	998                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x2158:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string157                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	999                             // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x2167:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string158                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1000                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x2176:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string159                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1001                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x2185:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp501                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x2190:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x2197:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp502                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x21a2:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	35                              // Abbrev [35] 0x21a9:0xd DW_TAG_GNU_call_site
	.word	8631                            // DW_AT_abstract_origin
	.xword	.Ltmp503                        // DW_AT_low_pc
	.byte	0                               // End Of Children Mark
	.byte	36                              // Abbrev [36] 0x21b7:0x16 DW_TAG_subprogram
	.word	.Linfo_string66                 // DW_AT_name
	.byte	6                               // DW_AT_decl_file
	.byte	88                              // DW_AT_decl_line
                                        // DW_AT_prototyped
	.word	230                             // DW_AT_type
                                        // DW_AT_declaration
                                        // DW_AT_external
	.byte	24                              // Abbrev [24] 0x21c2:0x5 DW_TAG_formal_parameter
	.word	230                             // DW_AT_type
	.byte	24                              // Abbrev [24] 0x21c7:0x5 DW_TAG_formal_parameter
	.word	230                             // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x21cd:0x58 DW_TAG_subprogram
	.xword	.Lfunc_begin48                  // DW_AT_low_pc
	.word	.Lfunc_end48-.Lfunc_begin48     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string119                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1009                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x21e3:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc112                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1009                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x21f3:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc113                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1009                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x2203:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string155                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1014                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x2212:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp510                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x221d:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x2225:0xa3 DW_TAG_subprogram
	.xword	.Lfunc_begin49                  // DW_AT_low_pc
	.word	.Lfunc_end49-.Lfunc_begin49     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string120                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1021                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x223b:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc114                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1021                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x224b:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc115                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1021                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x225b:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	32
	.word	.Linfo_string156                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1025                            // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x226a:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string157                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1026                            // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x2279:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string158                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1027                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x2288:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string159                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1028                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	7                               // Abbrev [7] 0x2297:0xc DW_TAG_variable
	.word	.Linfo_string154                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1039                            // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	8                               // Abbrev [8] 0x22a3:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp518                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x22ae:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x22b5:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp519                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x22c0:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x22c8:0x58 DW_TAG_subprogram
	.xword	.Lfunc_begin50                  // DW_AT_low_pc
	.word	.Lfunc_end50-.Lfunc_begin50     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string121                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1044                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x22de:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc116                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1044                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x22ee:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc117                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1044                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x22fe:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string155                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1049                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x230d:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp532                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x2318:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x2320:0x58 DW_TAG_subprogram
	.xword	.Lfunc_begin51                  // DW_AT_low_pc
	.word	.Lfunc_end51-.Lfunc_begin51     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string122                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1056                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x2336:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc118                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1056                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x2346:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc119                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1056                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x2356:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string155                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1061                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x2365:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp540                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x2370:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x2378:0x58 DW_TAG_subprogram
	.xword	.Lfunc_begin52                  // DW_AT_low_pc
	.word	.Lfunc_end52-.Lfunc_begin52     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string123                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1074                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x238e:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc120                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1074                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x239e:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc121                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1074                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x23ae:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string155                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1079                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x23bd:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp549                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x23c8:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x23d0:0x58 DW_TAG_subprogram
	.xword	.Lfunc_begin53                  // DW_AT_low_pc
	.word	.Lfunc_end53-.Lfunc_begin53     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string124                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1092                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x23e6:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc122                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1092                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x23f6:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc123                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1092                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x2406:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string155                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1097                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x2415:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp558                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x2420:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x2428:0x58 DW_TAG_subprogram
	.xword	.Lfunc_begin54                  // DW_AT_low_pc
	.word	.Lfunc_end54-.Lfunc_begin54     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string125                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1104                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x243e:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc124                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1104                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x244e:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc125                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1104                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x245e:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string155                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1109                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x246d:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp565                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x2478:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x2480:0xa7 DW_TAG_subprogram
	.xword	.Lfunc_begin55                  // DW_AT_low_pc
	.word	.Lfunc_end55-.Lfunc_begin55     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string126                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1116                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x2496:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc126                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1116                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x24a6:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc127                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1116                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x24b6:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string156                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1120                            // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x24c5:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string157                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1121                            // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x24d4:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string158                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1122                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x24e3:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string159                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1123                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	6                               // Abbrev [6] 0x24f2:0x10 DW_TAG_variable
	.word	.Ldebug_loc128                  // DW_AT_location
	.word	.Linfo_string160                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1128                            // DW_AT_decl_line
	.word	230                             // DW_AT_type
	.byte	8                               // Abbrev [8] 0x2502:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp573                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x250d:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x2514:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp574                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x251f:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x2527:0x58 DW_TAG_subprogram
	.xword	.Lfunc_begin56                  // DW_AT_low_pc
	.word	.Lfunc_end56-.Lfunc_begin56     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string127                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1132                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x253d:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc129                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1132                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x254d:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc130                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1132                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x255d:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1137                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x256c:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp584                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x2577:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x257f:0x58 DW_TAG_subprogram
	.xword	.Lfunc_begin57                  // DW_AT_low_pc
	.word	.Lfunc_end57-.Lfunc_begin57     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string128                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1144                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x2595:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc131                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1144                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x25a5:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc132                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1144                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x25b5:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1149                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x25c4:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp591                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x25cf:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x25d7:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin58                  // DW_AT_low_pc
	.word	.Lfunc_end58-.Lfunc_begin58     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string129                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1156                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x25ed:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc133                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1156                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x25fd:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc134                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1156                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x260d:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string156                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1160                            // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x261c:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string157                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1161                            // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x262b:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string158                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1162                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x263a:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string159                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1163                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x2649:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp599                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x2654:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x265b:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp600                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x2666:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x266e:0x97 DW_TAG_subprogram
	.xword	.Lfunc_begin59                  // DW_AT_low_pc
	.word	.Lfunc_end59-.Lfunc_begin59     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string130                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1171                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x2684:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc135                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1171                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x2694:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc136                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1171                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x26a4:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	145
	.byte	112
	.word	.Linfo_string156                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1175                            // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x26b3:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	24
	.word	.Linfo_string157                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1176                            // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	5                               // Abbrev [5] 0x26c2:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	16
	.word	.Linfo_string158                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1177                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x26d1:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	8
	.word	.Linfo_string159                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1178                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x26e0:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp608                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x26eb:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	16
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x26f2:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp609                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x26fd:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	8
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x2705:0x58 DW_TAG_subprogram
	.xword	.Lfunc_begin60                  // DW_AT_low_pc
	.word	.Lfunc_end60-.Lfunc_begin60     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string131                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1186                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x271b:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc137                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1186                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x272b:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc138                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1186                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x273b:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1191                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	8                               // Abbrev [8] 0x274a:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp616                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x2755:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	45                              // Abbrev [45] 0x275d:0x32 DW_TAG_subprogram
	.word	.Linfo_string67                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	158                             // DW_AT_decl_line
                                        // DW_AT_prototyped
	.word	1967                            // DW_AT_type
	.byte	1                               // DW_AT_inline
	.byte	46                              // Abbrev [46] 0x2769:0xb DW_TAG_variable
	.word	.Linfo_string68                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	160                             // DW_AT_decl_line
	.word	1967                            // DW_AT_type
	.byte	47                              // Abbrev [47] 0x2774:0xd DW_TAG_lexical_block
	.byte	46                              // Abbrev [46] 0x2775:0xb DW_TAG_variable
	.word	.Linfo_string69                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	171                             // DW_AT_decl_line
	.word	1967                            // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	47                              // Abbrev [47] 0x2781:0xd DW_TAG_lexical_block
	.byte	46                              // Abbrev [46] 0x2782:0xb DW_TAG_variable
	.word	.Linfo_string70                 // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.byte	189                             // DW_AT_decl_line
	.word	2009                            // DW_AT_type
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	2                               // Abbrev [2] 0x278f:0xae DW_TAG_subprogram
	.xword	.Lfunc_begin61                  // DW_AT_low_pc
	.word	.Lfunc_end61-.Lfunc_begin61     // DW_AT_high_pc
	.byte	1                               // DW_AT_frame_base
	.byte	109
                                        // DW_AT_GNU_all_call_sites
	.word	.Linfo_string132                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1203                            // DW_AT_decl_line
                                        // DW_AT_prototyped
                                        // DW_AT_external
	.byte	4                               // Abbrev [4] 0x27a5:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc139                  // DW_AT_location
	.word	.Linfo_string137                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1203                            // DW_AT_decl_line
	.word	1717                            // DW_AT_type
	.byte	4                               // Abbrev [4] 0x27b5:0x10 DW_TAG_formal_parameter
	.word	.Ldebug_loc140                  // DW_AT_location
	.word	.Linfo_string138                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1203                            // DW_AT_decl_line
	.word	1832                            // DW_AT_type
	.byte	5                               // Abbrev [5] 0x27c5:0xf DW_TAG_variable
	.byte	2                               // DW_AT_location
	.byte	143
	.byte	0
	.word	.Linfo_string139                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1208                            // DW_AT_decl_line
	.word	1816                            // DW_AT_type
	.byte	6                               // Abbrev [6] 0x27d4:0x10 DW_TAG_variable
	.word	.Ldebug_loc143                  // DW_AT_location
	.word	.Linfo_string161                // DW_AT_name
	.byte	2                               // DW_AT_decl_file
	.hword	1212                            // DW_AT_decl_line
	.word	219                             // DW_AT_type
	.byte	42                              // Abbrev [42] 0x27e4:0x46 DW_TAG_inlined_subroutine
	.word	10077                           // DW_AT_abstract_origin
	.word	.Ldebug_ranges2                 // DW_AT_ranges
	.byte	2                               // DW_AT_call_file
	.hword	1218                            // DW_AT_call_line
	.byte	5                               // DW_AT_call_column
	.byte	44                              // Abbrev [44] 0x27f1:0x9 DW_TAG_variable
	.word	.Ldebug_loc142                  // DW_AT_location
	.word	10089                           // DW_AT_abstract_origin
	.byte	34                              // Abbrev [34] 0x27fa:0x18 DW_TAG_lexical_block
	.xword	.Ltmp632                        // DW_AT_low_pc
	.word	.Ltmp638-.Ltmp632               // DW_AT_high_pc
	.byte	48                              // Abbrev [48] 0x2807:0xa DW_TAG_variable
	.ascii	"\215\340\207\212\004"          // DW_AT_const_value
	.word	10101                           // DW_AT_abstract_origin
	.byte	0                               // End Of Children Mark
	.byte	34                              // Abbrev [34] 0x2812:0x17 DW_TAG_lexical_block
	.xword	.Ltmp638                        // DW_AT_low_pc
	.word	.Ltmp655-.Ltmp638               // DW_AT_high_pc
	.byte	44                              // Abbrev [44] 0x281f:0x9 DW_TAG_variable
	.word	.Ldebug_loc141                  // DW_AT_location
	.word	10114                           // DW_AT_abstract_origin
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	8                               // Abbrev [8] 0x282a:0x12 DW_TAG_GNU_call_site
	.byte	1                               // DW_AT_GNU_call_site_target
	.byte	88
	.xword	.Ltmp624                        // DW_AT_low_pc
	.byte	9                               // Abbrev [9] 0x2835:0x6 DW_TAG_GNU_call_site_parameter
	.byte	1                               // DW_AT_location
	.byte	81
	.byte	2                               // DW_AT_GNU_call_site_value
	.byte	143
	.byte	0
	.byte	0                               // End Of Children Mark
	.byte	0                               // End Of Children Mark
	.byte	13                              // Abbrev [13] 0x283d:0xb DW_TAG_typedef
	.word	10312                           // DW_AT_type
	.word	.Linfo_string135                // DW_AT_name
	.byte	3                               // DW_AT_decl_file
	.byte	40                              // DW_AT_decl_line
	.byte	22                              // Abbrev [22] 0x2848:0x5 DW_TAG_pointer_type
	.word	10317                           // DW_AT_type
	.byte	13                              // Abbrev [13] 0x284d:0xb DW_TAG_typedef
	.word	10328                           // DW_AT_type
	.word	.Linfo_string134                // DW_AT_name
	.byte	3                               // DW_AT_decl_file
	.byte	39                              // DW_AT_decl_line
	.byte	22                              // Abbrev [22] 0x2858:0x5 DW_TAG_pointer_type
	.word	10333                           // DW_AT_type
	.byte	12                              // Abbrev [12] 0x285d:0x5 DW_TAG_const_type
	.word	1604                            // DW_AT_type
	.byte	22                              // Abbrev [22] 0x2862:0x5 DW_TAG_pointer_type
	.word	1967                            // DW_AT_type
	.byte	0                               // End Of Children Mark
.Ldebug_info_end0:
	.section	.debug_ranges,"",@progbits
.Ldebug_ranges0:
	.xword	.Ltmp240
	.xword	.Ltmp242
	.xword	.Ltmp244
	.xword	.Ltmp263
	.xword	0
	.xword	0
.Ldebug_ranges1:
	.xword	.Ltmp406
	.xword	.Ltmp408
	.xword	.Ltmp410
	.xword	.Ltmp429
	.xword	0
	.xword	0
.Ldebug_ranges2:
	.xword	.Ltmp625
	.xword	.Ltmp626
	.xword	.Ltmp627
	.xword	.Ltmp656
	.xword	.Ltmp657
	.xword	.Ltmp659
	.xword	.Ltmp660
	.xword	.Ltmp664
	.xword	0
	.xword	0
.Ldebug_ranges3:
	.xword	.Lfunc_begin0
	.xword	.Lfunc_end0
	.xword	.Lfunc_begin1
	.xword	.Lfunc_end1
	.xword	.Lfunc_begin2
	.xword	.Lfunc_end2
	.xword	.Lfunc_begin3
	.xword	.Lfunc_end3
	.xword	.Lfunc_begin4
	.xword	.Lfunc_end4
	.xword	.Lfunc_begin5
	.xword	.Lfunc_end5
	.xword	.Lfunc_begin6
	.xword	.Lfunc_end6
	.xword	.Lfunc_begin7
	.xword	.Lfunc_end7
	.xword	.Lfunc_begin8
	.xword	.Lfunc_end8
	.xword	.Lfunc_begin9
	.xword	.Lfunc_end9
	.xword	.Lfunc_begin10
	.xword	.Lfunc_end10
	.xword	.Lfunc_begin11
	.xword	.Lfunc_end11
	.xword	.Lfunc_begin12
	.xword	.Lfunc_end12
	.xword	.Lfunc_begin13
	.xword	.Lfunc_end13
	.xword	.Lfunc_begin14
	.xword	.Lfunc_end14
	.xword	.Lfunc_begin15
	.xword	.Lfunc_end15
	.xword	.Lfunc_begin16
	.xword	.Lfunc_end16
	.xword	.Lfunc_begin17
	.xword	.Lfunc_end17
	.xword	.Lfunc_begin18
	.xword	.Lfunc_end18
	.xword	.Lfunc_begin19
	.xword	.Lfunc_end19
	.xword	.Lfunc_begin20
	.xword	.Lfunc_end20
	.xword	.Lfunc_begin21
	.xword	.Lfunc_end21
	.xword	.Lfunc_begin22
	.xword	.Lfunc_end22
	.xword	.Lfunc_begin23
	.xword	.Lfunc_end23
	.xword	.Lfunc_begin24
	.xword	.Lfunc_end24
	.xword	.Lfunc_begin25
	.xword	.Lfunc_end25
	.xword	.Lfunc_begin26
	.xword	.Lfunc_end26
	.xword	.Lfunc_begin27
	.xword	.Lfunc_end27
	.xword	.Lfunc_begin28
	.xword	.Lfunc_end28
	.xword	.Lfunc_begin29
	.xword	.Lfunc_end29
	.xword	.Lfunc_begin30
	.xword	.Lfunc_end30
	.xword	.Lfunc_begin31
	.xword	.Lfunc_end31
	.xword	.Lfunc_begin32
	.xword	.Lfunc_end32
	.xword	.Lfunc_begin33
	.xword	.Lfunc_end33
	.xword	.Lfunc_begin34
	.xword	.Lfunc_end34
	.xword	.Lfunc_begin35
	.xword	.Lfunc_end35
	.xword	.Lfunc_begin36
	.xword	.Lfunc_end36
	.xword	.Lfunc_begin37
	.xword	.Lfunc_end37
	.xword	.Lfunc_begin38
	.xword	.Lfunc_end38
	.xword	.Lfunc_begin39
	.xword	.Lfunc_end39
	.xword	.Lfunc_begin40
	.xword	.Lfunc_end40
	.xword	.Lfunc_begin41
	.xword	.Lfunc_end41
	.xword	.Lfunc_begin42
	.xword	.Lfunc_end42
	.xword	.Lfunc_begin43
	.xword	.Lfunc_end43
	.xword	.Lfunc_begin44
	.xword	.Lfunc_end44
	.xword	.Lfunc_begin45
	.xword	.Lfunc_end45
	.xword	.Lfunc_begin46
	.xword	.Lfunc_end46
	.xword	.Lfunc_begin47
	.xword	.Lfunc_end47
	.xword	.Lfunc_begin48
	.xword	.Lfunc_end48
	.xword	.Lfunc_begin49
	.xword	.Lfunc_end49
	.xword	.Lfunc_begin50
	.xword	.Lfunc_end50
	.xword	.Lfunc_begin51
	.xword	.Lfunc_end51
	.xword	.Lfunc_begin52
	.xword	.Lfunc_end52
	.xword	.Lfunc_begin53
	.xword	.Lfunc_end53
	.xword	.Lfunc_begin54
	.xword	.Lfunc_end54
	.xword	.Lfunc_begin55
	.xword	.Lfunc_end55
	.xword	.Lfunc_begin56
	.xword	.Lfunc_end56
	.xword	.Lfunc_begin57
	.xword	.Lfunc_end57
	.xword	.Lfunc_begin58
	.xword	.Lfunc_end58
	.xword	.Lfunc_begin59
	.xword	.Lfunc_end59
	.xword	.Lfunc_begin60
	.xword	.Lfunc_end60
	.xword	.Lfunc_begin61
	.xword	.Lfunc_end61
	.xword	.Lfunc_begin62
	.xword	.Lfunc_end62
	.xword	0
	.xword	0
	.section	.debug_str,"MS",@progbits,1
.Linfo_string0:
	.asciz	"Android (13691557, +pgo, -bolt, +lto, -mlgo, based on r522817d) clang version 18.0.4 (https://android.googlesource.com/toolchain/llvm-project d8003a456d14a3deb8054cdaa529ffbf02d9b262)" // string offset=0
.Linfo_string1:
	.asciz	"/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit/i04-bits-v2-engine/vendor/projectm-eval/projectm-eval/TreeFunctions.c" // string offset=184
.Linfo_string2:
	.asciz	"/Users/jneerdael/Scripts/Projectm-TV/.worktrees/milkdrop-audit-repairs/build/audit/arithmetic-proposal/i04-only/bits-v2/arm64" // string offset=337
.Linfo_string3:
	.asciz	"three_halfs"                   // string offset=463
.Linfo_string4:
	.asciz	"double"                        // string offset=475
.Linfo_string5:
	.asciz	"PRJM_EVAL_F"                   // string offset=482
.Linfo_string6:
	.asciz	"one_half"                      // string offset=494
.Linfo_string7:
	.asciz	"char"                          // string offset=503
.Linfo_string8:
	.asciz	"__ARRAY_SIZE_TYPE__"           // string offset=508
.Linfo_string9:
	.asciz	"intrinsic_function_table"      // string offset=528
.Linfo_string10:
	.asciz	"name"                          // string offset=553
.Linfo_string11:
	.asciz	"func"                          // string offset=558
.Linfo_string12:
	.asciz	"value"                         // string offset=563
.Linfo_string13:
	.asciz	"var"                           // string offset=569
.Linfo_string14:
	.asciz	"memory_buffer"                 // string offset=573
.Linfo_string15:
	.asciz	"projectm_eval_mem_buffer"      // string offset=587
.Linfo_string16:
	.asciz	"args"                          // string offset=612
.Linfo_string17:
	.asciz	"list"                          // string offset=617
.Linfo_string18:
	.asciz	"expr"                          // string offset=622
.Linfo_string19:
	.asciz	"next"                          // string offset=627
.Linfo_string20:
	.asciz	"prjm_eval_exptreenode_list_item" // string offset=632
.Linfo_string21:
	.asciz	"prjm_eval_exptreenode_list_item_t" // string offset=664
.Linfo_string22:
	.asciz	"prjm_eval_exptreenode"         // string offset=698
.Linfo_string23:
	.asciz	"prjm_eval_expr_func_t"         // string offset=720
.Linfo_string24:
	.asciz	"arg_count"                     // string offset=742
.Linfo_string25:
	.asciz	"int"                           // string offset=752
.Linfo_string26:
	.asciz	"is_const_eval"                 // string offset=756
.Linfo_string27:
	.asciz	"_Bool"                         // string offset=770
.Linfo_string28:
	.asciz	"is_state_changing"             // string offset=776
.Linfo_string29:
	.asciz	"prjm_eval_function_def"        // string offset=794
.Linfo_string30:
	.asciz	"prjm_eval_function_def_t"      // string offset=817
.Linfo_string31:
	.asciz	"mag01"                         // string offset=842
.Linfo_string32:
	.asciz	"unsigned int"                  // string offset=848
.Linfo_string33:
	.asciz	"__uint32_t"                    // string offset=861
.Linfo_string34:
	.asciz	"uint32_t"                      // string offset=872
.Linfo_string35:
	.asciz	"mt"                            // string offset=881
.Linfo_string36:
	.asciz	"mti"                           // string offset=884
.Linfo_string37:
	.asciz	"__int32_t"                     // string offset=888
.Linfo_string38:
	.asciz	"int32_t"                       // string offset=898
.Linfo_string39:
	.asciz	"long"                          // string offset=906
.Linfo_string40:
	.asciz	"__int64_t"                     // string offset=911
.Linfo_string41:
	.asciz	"int64_t"                       // string offset=921
.Linfo_string42:
	.asciz	"PRJM_EVAL_I"                   // string offset=929
.Linfo_string43:
	.asciz	"prjm_eval_memory_allocate"     // string offset=941
.Linfo_string44:
	.asciz	"prjm_eval_memory_free_block"   // string offset=967
.Linfo_string45:
	.asciz	"prjm_eval_memory_copy"         // string offset=995
.Linfo_string46:
	.asciz	"prjm_eval_memory_set"          // string offset=1017
.Linfo_string47:
	.asciz	"bounded_milkdrop_remainder"    // string offset=1038
.Linfo_string48:
	.asciz	"numerator"                     // string offset=1065
.Linfo_string49:
	.asciz	"denominator"                   // string offset=1075
.Linfo_string50:
	.asciz	"denominatorBits"               // string offset=1087
.Linfo_string51:
	.asciz	"unsigned long"                 // string offset=1103
.Linfo_string52:
	.asciz	"__uint64_t"                    // string offset=1117
.Linfo_string53:
	.asciz	"uint64_t"                      // string offset=1128
.Linfo_string54:
	.asciz	"remainder_bits_t"              // string offset=1137
.Linfo_string55:
	.asciz	"denominatorMagnitude"          // string offset=1154
.Linfo_string56:
	.asciz	"numeratorMagnitude"            // string offset=1175
.Linfo_string57:
	.asciz	"dividend"                      // string offset=1194
.Linfo_string58:
	.asciz	"minimum"                       // string offset=1203
.Linfo_string59:
	.asciz	"divisor"                       // string offset=1211
.Linfo_string60:
	.asciz	"remainder"                     // string offset=1219
.Linfo_string61:
	.asciz	"numeratorBits"                 // string offset=1229
.Linfo_string62:
	.asciz	"tan"                           // string offset=1243
.Linfo_string63:
	.asciz	"asin"                          // string offset=1247
.Linfo_string64:
	.asciz	"acos"                          // string offset=1252
.Linfo_string65:
	.asciz	"atan"                          // string offset=1257
.Linfo_string66:
	.asciz	"atan2"                         // string offset=1262
.Linfo_string67:
	.asciz	"prjm_eval_genrand_int32"       // string offset=1268
.Linfo_string68:
	.asciz	"y"                             // string offset=1292
.Linfo_string69:
	.asciz	"s"                             // string offset=1294
.Linfo_string70:
	.asciz	"kk"                            // string offset=1296
.Linfo_string71:
	.asciz	"prjm_eval_intrinsic_functions" // string offset=1299
.Linfo_string72:
	.asciz	"prjm_eval_func_const"          // string offset=1329
.Linfo_string73:
	.asciz	"prjm_eval_func_var"            // string offset=1350
.Linfo_string74:
	.asciz	"prjm_eval_func_execute_list"   // string offset=1369
.Linfo_string75:
	.asciz	"prjm_eval_func_execute_loop"   // string offset=1397
.Linfo_string76:
	.asciz	"prjm_eval_func_execute_while"  // string offset=1425
.Linfo_string77:
	.asciz	"prjm_eval_func_if"             // string offset=1454
.Linfo_string78:
	.asciz	"prjm_eval_func_exec2"          // string offset=1472
.Linfo_string79:
	.asciz	"prjm_eval_func_exec3"          // string offset=1493
.Linfo_string80:
	.asciz	"prjm_eval_func_set"            // string offset=1514
.Linfo_string81:
	.asciz	"prjm_eval_func_mem"            // string offset=1533
.Linfo_string82:
	.asciz	"prjm_eval_func_freembuf"       // string offset=1552
.Linfo_string83:
	.asciz	"prjm_eval_func_memcpy"         // string offset=1576
.Linfo_string84:
	.asciz	"prjm_eval_func_memset"         // string offset=1598
.Linfo_string85:
	.asciz	"prjm_eval_func_bnot"           // string offset=1620
.Linfo_string86:
	.asciz	"prjm_eval_func_equal"          // string offset=1640
.Linfo_string87:
	.asciz	"prjm_eval_func_notequal"       // string offset=1661
.Linfo_string88:
	.asciz	"prjm_eval_func_below"          // string offset=1685
.Linfo_string89:
	.asciz	"prjm_eval_func_above"          // string offset=1706
.Linfo_string90:
	.asciz	"prjm_eval_func_beloweq"        // string offset=1727
.Linfo_string91:
	.asciz	"prjm_eval_func_aboveeq"        // string offset=1750
.Linfo_string92:
	.asciz	"prjm_eval_func_add"            // string offset=1773
.Linfo_string93:
	.asciz	"prjm_eval_func_sub"            // string offset=1792
.Linfo_string94:
	.asciz	"prjm_eval_func_mul"            // string offset=1811
.Linfo_string95:
	.asciz	"prjm_eval_func_div"            // string offset=1830
.Linfo_string96:
	.asciz	"prjm_eval_func_mod"            // string offset=1849
.Linfo_string97:
	.asciz	"prjm_eval_func_boolean_and_op" // string offset=1868
.Linfo_string98:
	.asciz	"prjm_eval_func_boolean_or_op"  // string offset=1898
.Linfo_string99:
	.asciz	"prjm_eval_func_boolean_and_func" // string offset=1927
.Linfo_string100:
	.asciz	"prjm_eval_func_boolean_or_func" // string offset=1959
.Linfo_string101:
	.asciz	"prjm_eval_func_neg"            // string offset=1990
.Linfo_string102:
	.asciz	"prjm_eval_func_add_op"         // string offset=2009
.Linfo_string103:
	.asciz	"prjm_eval_func_sub_op"         // string offset=2031
.Linfo_string104:
	.asciz	"prjm_eval_func_mul_op"         // string offset=2053
.Linfo_string105:
	.asciz	"prjm_eval_func_div_op"         // string offset=2075
.Linfo_string106:
	.asciz	"prjm_eval_func_bitwise_or_op"  // string offset=2097
.Linfo_string107:
	.asciz	"prjm_eval_func_bitwise_or"     // string offset=2126
.Linfo_string108:
	.asciz	"prjm_eval_func_bitwise_and_op" // string offset=2152
.Linfo_string109:
	.asciz	"prjm_eval_func_bitwise_and"    // string offset=2182
.Linfo_string110:
	.asciz	"prjm_eval_func_mod_op"         // string offset=2209
.Linfo_string111:
	.asciz	"prjm_eval_func_pow_op"         // string offset=2231
.Linfo_string112:
	.asciz	"prjm_eval_func_sin"            // string offset=2253
.Linfo_string113:
	.asciz	"prjm_eval_func_cos"            // string offset=2272
.Linfo_string114:
	.asciz	"prjm_eval_func_tan"            // string offset=2291
.Linfo_string115:
	.asciz	"prjm_eval_func_asin"           // string offset=2310
.Linfo_string116:
	.asciz	"prjm_eval_func_acos"           // string offset=2330
.Linfo_string117:
	.asciz	"prjm_eval_func_atan"           // string offset=2350
.Linfo_string118:
	.asciz	"prjm_eval_func_atan2"          // string offset=2370
.Linfo_string119:
	.asciz	"prjm_eval_func_sqrt"           // string offset=2391
.Linfo_string120:
	.asciz	"prjm_eval_func_pow"            // string offset=2411
.Linfo_string121:
	.asciz	"prjm_eval_func_exp"            // string offset=2430
.Linfo_string122:
	.asciz	"prjm_eval_func_log"            // string offset=2449
.Linfo_string123:
	.asciz	"prjm_eval_func_log10"          // string offset=2468
.Linfo_string124:
	.asciz	"prjm_eval_func_floor"          // string offset=2489
.Linfo_string125:
	.asciz	"prjm_eval_func_ceil"           // string offset=2510
.Linfo_string126:
	.asciz	"prjm_eval_func_sigmoid"        // string offset=2530
.Linfo_string127:
	.asciz	"prjm_eval_func_sqr"            // string offset=2553
.Linfo_string128:
	.asciz	"prjm_eval_func_abs"            // string offset=2572
.Linfo_string129:
	.asciz	"prjm_eval_func_min"            // string offset=2591
.Linfo_string130:
	.asciz	"prjm_eval_func_max"            // string offset=2610
.Linfo_string131:
	.asciz	"prjm_eval_func_sign"           // string offset=2629
.Linfo_string132:
	.asciz	"prjm_eval_func_rand"           // string offset=2649
.Linfo_string133:
	.asciz	"prjm_eval_func_invsqrt"        // string offset=2669
.Linfo_string134:
	.asciz	"prjm_eval_intrinsic_function_list" // string offset=2692
.Linfo_string135:
	.asciz	"prjm_eval_intrinsic_function_list_ptr" // string offset=2726
.Linfo_string136:
	.asciz	"count"                         // string offset=2764
.Linfo_string137:
	.asciz	"ctx"                           // string offset=2770
.Linfo_string138:
	.asciz	"ret_val"                       // string offset=2774
.Linfo_string139:
	.asciz	"value_ptr"                     // string offset=2782
.Linfo_string140:
	.asciz	"item"                          // string offset=2792
.Linfo_string141:
	.asciz	"loop_count_int"                // string offset=2797
.Linfo_string142:
	.asciz	"i"                             // string offset=2812
.Linfo_string143:
	.asciz	"if_arg"                        // string offset=2814
.Linfo_string144:
	.asciz	"index_ptr"                     // string offset=2821
.Linfo_string145:
	.asciz	"mem_addr"                      // string offset=2831
.Linfo_string146:
	.asciz	"src_index"                     // string offset=2840
.Linfo_string147:
	.asciz	"dest_index_ptr"                // string offset=2850
.Linfo_string148:
	.asciz	"src_index_ptr"                 // string offset=2865
.Linfo_string149:
	.asciz	"count_ptr"                     // string offset=2879
.Linfo_string150:
	.asciz	"val1"                          // string offset=2889
.Linfo_string151:
	.asciz	"val2"                          // string offset=2894
.Linfo_string152:
	.asciz	"val1_ptr"                      // string offset=2899
.Linfo_string153:
	.asciz	"val2_ptr"                      // string offset=2908
.Linfo_string154:
	.asciz	"result"                        // string offset=2917
.Linfo_string155:
	.asciz	"math_arg_ptr"                  // string offset=2924
.Linfo_string156:
	.asciz	"math_arg1"                     // string offset=2937
.Linfo_string157:
	.asciz	"math_arg2"                     // string offset=2947
.Linfo_string158:
	.asciz	"math_arg1_ptr"                 // string offset=2957
.Linfo_string159:
	.asciz	"math_arg2_ptr"                 // string offset=2971
.Linfo_string160:
	.asciz	"t"                             // string offset=2985
.Linfo_string161:
	.asciz	"rand_max"                      // string offset=2987
.Linfo_string162:
	.asciz	"type_conv"                     // string offset=2996
.Linfo_string163:
	.asciz	"PRJM_F_val"                    // string offset=3006
.Linfo_string164:
	.asciz	"int_val"                       // string offset=3017
.Linfo_string165:
	.asciz	"num2"                          // string offset=3025
	.ident	"Android (13691557, +pgo, -bolt, +lto, -mlgo, based on r522817d) clang version 18.0.4 (https://android.googlesource.com/toolchain/llvm-project d8003a456d14a3deb8054cdaa529ffbf02d9b262)"
	.section	".note.GNU-stack","",@progbits
	.section	.debug_line,"",@progbits
.Lline_table_start0:
