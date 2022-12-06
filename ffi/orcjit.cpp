#include "core.h"

namespace llvm {

// wrap/unwrap for LLVMTargetMachineRef.
// Ripped from lib/Target/TargetMachineC.cpp.

inline TargetMachine *unwrap(LLVMTargetMachineRef P) {
    return reinterpret_cast<TargetMachine *>(P);
}
inline LLVMTargetMachineRef wrap(const TargetMachine *P) {
    return reinterpret_cast<LLVMTargetMachineRef>(
        const_cast<TargetMachine *>(P));
}


API_EXPORT(LLVMLLJITRef)
LLVMPY_CreateLLJITCompiler(LLVMModuleRef M, LLVMTargetMachineRef TM,
                           const char **OutError) {
    return create_execution_engine(M, TM, OutError);
}

} // namespace llvm
