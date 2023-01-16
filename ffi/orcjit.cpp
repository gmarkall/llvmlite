#include "core.h"

#include "llvm-c/ExecutionEngine.h"
#include "llvm-c/LLJIT.h"
#include "llvm-c/Orc.h"
#include "llvm/ExecutionEngine/Orc/ExecutionUtils.h"
#include "llvm/ExecutionEngine/Orc/LLJIT.h"

using namespace llvm;
using namespace llvm::orc;


inline LLJIT *unwrap(LLVMOrcLLJITRef P) {
    return reinterpret_cast<LLJIT *>(P);
}

inline TargetMachine *unwrap(LLVMTargetMachineRef TM) {
    return reinterpret_cast<TargetMachine *>(TM);
}

inline LLVMOrcJITTargetMachineBuilderRef wrap(JITTargetMachineBuilder *JTMB) {
    return reinterpret_cast<LLVMOrcJITTargetMachineBuilderRef>(JTMB);
}


// Like LLVMOrcJITTargetMachineBuilderCreateFromTargetMachine but doesn't destroy the target machine.
static LLVMOrcJITTargetMachineBuilderRef
create_jit_target_machine_builder_from_target_machine(LLVMTargetMachineRef TM) {   
    auto *TemplateTM = unwrap(TM);     
       
    auto JTMB =     
        std::make_unique<JITTargetMachineBuilder>(TemplateTM->getTargetTriple());
       
    (*JTMB)     
        .setCPU(TemplateTM->getTargetCPU().str())     
        .setRelocationModel(TemplateTM->getRelocationModel())     
        .setCodeModel(TemplateTM->getCodeModel())     
        .setCodeGenOptLevel(TemplateTM->getOptLevel())     
        .setFeatures(TemplateTM->getTargetFeatureString())     
        .setOptions(TemplateTM->Options);     
       
    return wrap(JTMB.release());   
}


extern "C" {

API_EXPORT(LLVMOrcLLJITRef)
LLVMPY_CreateLLJITCompiler(const char **OutError) {
    LLVMOrcLLJITRef JIT;
    auto error = LLVMOrcCreateLLJIT(&JIT, nullptr);

    if (error) {
        char* message = LLVMGetErrorMessage(error);
        *OutError = LLVMPY_CreateString(message);
    }

    return JIT;
}

API_EXPORT(LLVMOrcLLJITRef)
LLVMPY_CreateLLJITCompilerFromTargetMachine(LLVMTargetMachineRef tm,
                                            const char **OutError) {
    LLVMOrcJITTargetMachineBuilderRef jtmb =
        create_jit_target_machine_builder_from_target_machine(tm);
    LLVMOrcLLJITBuilderRef builder = LLVMOrcCreateLLJITBuilder();
    LLVMOrcLLJITBuilderSetJITTargetMachineBuilder(builder, jtmb);
    LLVMOrcLLJITRef JIT;
    auto error = LLVMOrcCreateLLJIT(&JIT, builder);

    if (error) {
        char* message = LLVMGetErrorMessage(error);
        *OutError = LLVMPY_CreateString(message);
        return nullptr;
    }

    // FIXME: This needs moving into a separate function with its own Python API
    // and unit testing. It enables looking up symbols in the current process when
    // JIT linking.
    auto lljit = unwrap(JIT);
    auto &JD = lljit->getMainJITDylib();
    auto DLSGOrErr =
        DynamicLibrarySearchGenerator::GetForCurrentProcess('\0');
    if (DLSGOrErr)
        JD.addGenerator(std::move(*DLSGOrErr));
    else
        abort();

    return JIT;
}

API_EXPORT(void)
LLVMPY_AddIRModule(LLVMOrcLLJITRef JIT, LLVMModuleRef M) {
    auto llvm_ts_ctx = LLVMOrcCreateNewThreadSafeContext();
    auto tsm = LLVMOrcCreateNewThreadSafeModule(M, llvm_ts_ctx);
    LLVMOrcLLJITAddLLVMIRModule(JIT, LLVMOrcLLJITGetMainJITDylib(JIT), tsm);
    LLVMOrcDisposeThreadSafeContext(llvm_ts_ctx);
}

API_EXPORT(uint64_t)
LLVMPY_LLJITLookup(LLVMOrcLLJITRef JIT, const char *name) {
    LLVMOrcExecutorAddress ea;
    LLVMOrcLLJITLookup(JIT, &ea, name);
    return ea;
}

API_EXPORT(LLVMTargetDataRef)
LLVMPY_LLJITGetDataLayout(LLVMOrcLLJITRef JIT) {
    return wrap(&unwrap(JIT)->getDataLayout());
}

API_EXPORT(void)
LLVMPY_LLJITDispose(LLVMOrcLLJITRef JIT) { LLVMOrcDisposeLLJIT(JIT); }

API_EXPORT(void)
LLVMPY_LLJITRunInitializers(LLVMOrcLLJITRef JIT) {
    auto lljit = unwrap(JIT);
    auto error = lljit->initialize(lljit->getMainJITDylib());

    if (error)
        abort();
}

API_EXPORT(void)
LLVMPY_LLJITRunDeinitializers(LLVMOrcLLJITRef JIT) {
    auto lljit = unwrap(JIT);
    auto error = lljit->deinitialize(lljit->getMainJITDylib());

    if (error)
        abort();
}

API_EXPORT(void)
LLVMPY_LLJITDefineSymbol(LLVMOrcLLJITRef JIT, const char *name, void *addr) {
    auto lljit = unwrap(JIT);
    auto &JD = lljit->getMainJITDylib();
    SymbolStringPtr mangled = lljit->mangleAndIntern(name);
    JITEvaluatedSymbol symbol = JITEvaluatedSymbol::fromPointer(addr);
    auto error = JD.define(absoluteSymbols({{mangled, symbol}}));

    if (error)
        abort();
}

} // extern "C"
