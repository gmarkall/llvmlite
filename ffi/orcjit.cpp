#include "core.h"

#include "llvm-c/ExecutionEngine.h"
#include "llvm-c/LLJIT.h"
#include "llvm-c/Orc.h"
#include "llvm/ExecutionEngine/Orc/LLJIT.h"

namespace llvm {
namespace orc {

inline LLJIT *unwrap(LLVMOrcLLJITRef P) {
    return reinterpret_cast<LLJIT *>(P);
}

inline LLVMOrcLLJITRef wrap(const LLJIT *P) {
    return reinterpret_cast<LLVMOrcLLJITRef>(
        const_cast<LLJIT *>(P));
}

inline ThreadSafeModule *unwrap(LLVMOrcThreadSafeModuleRef P) {
    return reinterpret_cast<ThreadSafeModule *>(P);
}

inline LLVMOrcThreadSafeModuleRef wrap(const ThreadSafeModule *P) {
    return reinterpret_cast<LLVMOrcThreadSafeModuleRef>(
        const_cast<ThreadSafeModule *>(P));
}


} // namespace orc
} // namespace llvm

using namespace llvm;

extern "C" {

API_EXPORT(LLVMOrcLLJITRef)
LLVMPY_CreateLLJITCompiler(const char **OutError) {
    auto builder = LLVMOrcCreateLLJITBuilder();
    LLVMOrcLLJITRef JIT;// = orc::LLJITBuilder().create();
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

API_EXPORT(LLVMOrcThreadSafeModuleRef)
LLVMPY_CreateThreadSafeModule(LLVMModuleRef module/*, LLVMContextRef context*/)
{
  auto llvm_ts_ctx = LLVMOrcCreateNewThreadSafeContext();
  auto tsm = LLVMOrcCreateNewThreadSafeModule(module, llvm_ts_ctx);
  return tsm;
  //return wrap(new orc::ThreadSafeModule(
  //      std::move(
  //        std::unique_ptr<Module>(unwrap(module))),
  //        std::unique_ptr<LLVMContext>(std::move(unwrap(context)))));
}

} // extern "C"
