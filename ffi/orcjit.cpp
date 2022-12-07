#include "core.h"

#include "llvm-c/ExecutionEngine.h"
#include "llvm-c/LLJIT.h"
#include "llvm-c/Orc.h"
#include "llvm/ExecutionEngine/Orc/LLJIT.h"

using namespace llvm;

extern "C" {

API_EXPORT(LLVMOrcLLJITRef)
LLVMPY_CreateLLJITCompiler(const char **OutError) {
    auto builder = LLVMOrcCreateLLJITBuilder();
    LLVMOrcLLJITRef JIT;
    auto error = LLVMOrcCreateLLJIT(&JIT, builder);

    if (error) {
        *OutError = LLVMPY_CreateString("Error creating LLJIT"); //JIT.takeError().getPtr()->message());
    }  
    
    return JIT;
}

API_EXPORT(void)
LLVMPY_AddIRModule(LLVMOrcLLJITRef JIT, LLVMModuleRef M) {
  auto llvm_ts_ctx = LLVMOrcCreateNewThreadSafeContext();
  auto tsm = LLVMOrcCreateNewThreadSafeModule(M, llvm_ts_ctx);
  LLVMOrcLLJITAddLLVMIRModule(
      JIT, 
      LLVMOrcLLJITGetMainJITDylib(JIT),
      tsm);
}

API_EXPORT(uint64_t)
LLVMPY_LLJITLookup(LLVMOrcLLJITRef JIT, const char *name)
{
    LLVMOrcExecutorAddress ea;
    LLVMOrcLLJITLookup(JIT, &ea, name);
    return ea;
}

} // extern "C"
