from ctypes import (POINTER, c_char_p, c_bool, c_void_p,
                    c_int, c_uint64, c_size_t, CFUNCTYPE, string_at, cast,
                    py_object, Structure)

from llvmlite.binding import ffi, targets, object_file
from llvmlite.binding.common import _encode_string

class LLJIT(ffi.ObjectRef):
    def __init__(self, ptr):
        self._modules = set()
        self._td = None
        ffi.ObjectRef.__init__(self, ptr)

    def add_ir_module(self, m):
        if m in self._modules:
            raise KeyError("module already added to this engine")
        ffi.lib.LLVMPY_AddIRModule(self, m)
        m._owned = True
        self._modules.add(m)

    def lookup(self, fn):
        return ffi.lib.LLVMPY_LLJITLookup(self, fn.encode("ascii"))

    @property
    def target_data(self):
        """
        The TargetData for this LLJIT instance.
        """
        if self._td is not None:
            return self._td
        ptr = ffi.lib.LLVMPY_LLJITGetDataLayout(self)
        self._td = targets.TargetData(ptr)
        self._td._owned = True
        return self._td

    def run_static_constructors(self):
        """
        Run static constructors which initialize module-level static objects.
        """
        ffi.lib.LLVMPY_LLJITRunInitializers(self)

    def run_static_destructors(self):
        """
        Run static destructors which perform module-level cleanup of static
        resources.
        """
        ffi.lib.LLVMPY_LLJITRunDeinitializers(self)

    def define_symbol(self, name, address):
        ffi.lib.LLVMPY_LLJITDefineSymbol(self, _encode_string(name), c_void_p(address))


    def _dispose(self):
        # The modules will be cleaned up by the EE
        for mod in self._modules:
            mod.detach()
        if self._td is not None:
            self._td.detach()
        self._modules.clear()
        self._capi.LLVMPY_LLJITDispose(self)


def create_lljit_compiler(target_machine=None):
    """
    Create an LLJIT instance
    """
    with ffi.OutputString() as outerr:
        if target_machine is None:
            lljit = ffi.lib.LLVMPY_CreateLLJITCompiler(outerr)
        else:
            lljit = ffi.lib.LLVMPY_CreateLLJITCompilerFromTargetMachine(target_machine, outerr)
        if not lljit:
            raise RuntimeError(str(outerr))

    pylljit = LLJIT(lljit)

    for name, address in _known_symbols.items():
        pylljit.define_symbol(name, address)

    return pylljit


_known_symbols = {}


def define_symbol(name, address):
    """
    Register the *address* of global symbol *name*.  This will make
    it usable (e.g. callable) from LLVM-compiled functions.
    """
    _known_symbols[name] = address


ffi.lib.LLVMPY_CreateLLJITCompiler.argtypes = [
    POINTER(c_char_p),
]
ffi.lib.LLVMPY_CreateLLJITCompiler.restype = ffi.LLVMOrcLLJITRef

ffi.lib.LLVMPY_AddIRModule.argtypes = [
    ffi.LLVMOrcLLJITRef,
    ffi.LLVMModuleRef,
]


ffi.lib.LLVMPY_LLJITLookup.argtypes = [
    ffi.LLVMOrcLLJITRef,
    c_char_p,
]
ffi.lib.LLVMPY_LLJITLookup.restype = c_uint64

ffi.lib.LLVMPY_LLJITGetDataLayout.argtypes = [
    ffi.LLVMOrcLLJITRef,
]
ffi.lib.LLVMPY_LLJITGetDataLayout.restype = ffi.LLVMTargetDataRef

ffi.lib.LLVMPY_CreateLLJITCompilerFromTargetMachine.argtypes = [
    ffi.LLVMTargetMachineRef,
    POINTER(c_char_p),
]
ffi.lib.LLVMPY_CreateLLJITCompilerFromTargetMachine.restype = ffi.LLVMOrcLLJITRef

ffi.lib.LLVMPY_LLJITDispose.argtypes = [
    ffi.LLVMOrcLLJITRef,
]

ffi.lib.LLVMPY_LLJITRunInitializers.argtypes = [
    ffi.LLVMOrcLLJITRef,
]

ffi.lib.LLVMPY_LLJITRunDeinitializers.argtypes = [
    ffi.LLVMOrcLLJITRef,
]


ffi.lib.LLVMPY_LLJITDefineSymbol.argtypes = [
    ffi.LLVMOrcLLJITRef,
    c_char_p,
    c_void_p,
]
