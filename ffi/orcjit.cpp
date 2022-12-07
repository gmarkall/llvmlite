#include "core.h"

#include "llvm-c/ExecutionEngine.h"
#include "llvm-c/LLJIT.h"
#include "llvm-c/Orc.h"
#include "llvm/ExecutionEngine/Orc/LLJIT.h"

using namespace llvm;

namespace llvm {

inline orc::LLJIT *unwrap(LLVMOrcLLJITRef P) {
    return reinterpret_cast<orc::LLJIT *>(P);
}

} // namespace llvm

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

API_EXPORT(LLVMTargetDataRef)
LLVMPY_LLJITGetDataLayout(LLVMOrcLLJITRef JIT)
{
    return wrap(&unwrap(JIT)->getDataLayout());
}

} // extern "C"
