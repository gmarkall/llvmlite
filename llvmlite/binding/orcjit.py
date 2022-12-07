from ctypes import (POINTER, c_char_p, c_bool, c_void_p,
                    c_int, c_uint64, c_size_t, CFUNCTYPE, string_at, cast,
                    py_object, Structure)

from llvmlite.binding import ffi, targets, object_file

class LLJIT(ffi.ObjectRef):
    def __init__(self, ptr):
        self._modules = set()
        self._td = None
        ffi.ObjectRef.__init__(self, ptr)

    def add_ir_module(self, m):
        ffi.lib.LLVMPY_AddIRModule(self, m)
        m._owned = True

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


def create_lljit_compiler():
    """
    Create an LLJIT instance
    """
    with ffi.OutputString() as outerr:
        lljit = ffi.lib.LLVMPY_CreateLLJITCompiler(outerr)
        if not lljit:
            raise RuntimeError(str(outerr))

    return LLJIT(lljit)

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

