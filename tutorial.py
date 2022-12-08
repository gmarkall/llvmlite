from ctypes import CFUNCTYPE, c_double, c_int

import llvmlite.binding as llvm

llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()  # yes, even this one

llvm_ir = """
   ; ModuleID = "examples/ir_fpadd.py"
   target triple = "unknown-unknown-unknown"
   target datalayout = ""

   define double @"fpadd"(double %".1", double %".2")
   {
   entry:
     %"res" = fadd double %".1", %".2"
     ret double %"res"
   }
   """

mod = llvm.parse_assembly(llvm_ir)
mod.verify()

triple = 'riscv64-linux-gnu'
target = llvm.Target.from_triple(triple)
target_machine = target.create_target_machine(features='+f,+d')
lljit = llvm.create_lljit_compiler(target_machine)
lljit.add_ir_module(mod)

func_ptr = lljit.lookup('fpadd')

cfunc = CFUNCTYPE(c_double, c_double, c_double)(func_ptr)
res = cfunc(1.0, 3.5)
print("fpadd(...) =", res)
