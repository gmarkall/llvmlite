from ctypes import POINTER, c_char_p, c_void_p, c_uint64

from llvmlite.binding import ffi, targets
from llvmlite.binding.common import _encode_string


class LLJIT(ffi.ObjectRef):
    def __init__(self, ptr):
        self._td = None
        self._resource_trackers = {}
        ffi.ObjectRef.__init__(self, ptr)

    def add_ir_module(self, m):
        if m in self._resource_trackers:
            raise KeyError("module already added to this engine")
        rt = ffi.lib.LLVMPY_AddIRModule(self, m)
        m._owned = True
        self._resource_trackers[m] = rt

    def remove_ir_module(self, m):
        if m not in self._resource_trackers:
            raise KeyError('Module not added to this LLJIT instance')
        rt = self._resource_trackers.pop(m)
        ffi.lib.LLVMPY_RemoveIRModule(rt)

    def lookup(self, fn):
        with ffi.OutputString() as outerr:
            ptr = ffi.lib.LLVMPY_LLJITLookup(self, fn.encode("ascii"), outerr)
            if not ptr:
                raise RuntimeError(str(outerr))

        return ptr

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
        """
        Register the *address* of global symbol *name*.  This will make
        it usable (e.g. callable) from LLVM-compiled functions.
        """
        ffi.lib.LLVMPY_LLJITDefineSymbol(self, _encode_string(name),
                                         c_void_p(address))

    def add_current_process_search(self):
        """
        Enable searching for global symbols in the current process when
        linking.
        """
        ffi.lib.LLVMPY_LLJITAddCurrentProcessSearch(self)

    def _dispose(self):
        # The modules will be cleaned up by the EE
        for mod, rt in self._resource_trackers.items():
            ffi.lib.LLVMPY_ReleaseResourceTracker(rt)
            mod.detach()
        if self._td is not None:
            self._td.detach()
        self._resource_trackers.clear()
        self._capi.LLVMPY_LLJITDispose(self)


def create_lljit_compiler(target_machine=None):
    """
    Create an LLJIT instance
    """
    with ffi.OutputString() as outerr:
        lljit = ffi.lib.LLVMPY_CreateLLJITCompiler(target_machine, outerr)
        if not lljit:
            raise RuntimeError(str(outerr))

    return LLJIT(lljit)


ffi.lib.LLVMPY_AddIRModule.argtypes = [
    ffi.LLVMOrcLLJITRef,
    ffi.LLVMModuleRef,
]


ffi.lib.LLVMPY_LLJITLookup.argtypes = [
    ffi.LLVMOrcLLJITRef,
    c_char_p,
    POINTER(c_char_p),
]
ffi.lib.LLVMPY_LLJITLookup.restype = c_uint64

ffi.lib.LLVMPY_LLJITGetDataLayout.argtypes = [
    ffi.LLVMOrcLLJITRef,
]
ffi.lib.LLVMPY_LLJITGetDataLayout.restype = ffi.LLVMTargetDataRef

ffi.lib.LLVMPY_CreateLLJITCompiler.argtypes = [
    ffi.LLVMTargetMachineRef,
    POINTER(c_char_p),
]
ffi.lib.LLVMPY_CreateLLJITCompiler.restype = ffi.LLVMOrcLLJITRef

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

ffi.lib.LLVMPY_LLJITAddCurrentProcessSearch.argtypes = [
    ffi.LLVMOrcLLJITRef,
]

ffi.lib.LLVMPY_AddIRModule.argtypes = [
    ffi.LLVMOrcLLJITRef,
    ffi.LLVMModuleRef,
]
ffi.lib.LLVMPY_AddIRModule.restype = ffi.LLVMOrcResourceTrackerRef


ffi.lib.LLVMPY_ReleaseResourceTracker.argtypes = [
    ffi.LLVMOrcResourceTrackerRef,
]
