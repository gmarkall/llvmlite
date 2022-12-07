from ctypes import CFUNCTYPE, c_double, c_int

import llvmlite.binding as llvm

llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()  # yes, even this one

llvm_ir = """
   ; ModuleID = "examples/ir_intadd.py"
   target triple = "unknown-unknown-unknown"
   target datalayout = ""

   define i32 @"intadd"(i32 %".1", i32 %".2")
   {
   entry:
     %"res" = add i32 %".1", %".2"
     ret i32 %"res"
   }
   """

mod = llvm.parse_assembly(llvm_ir)
mod.verify()

lljit = llvm.create_lljit_compiler()
lljit.add_ir_module(mod)

func_ptr = lljit.get_function_address('intadd')

cfunc = CFUNCTYPE(c_int, c_int, c_int)(func_ptr)
res = cfunc(1, 4)
print("intadd(...) =", res)
