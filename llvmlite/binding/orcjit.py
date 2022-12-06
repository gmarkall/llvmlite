def create_orcjit_compiler(module, target_machine):
    """
    Create an ORC ExecutionEngine from the given *module* and
    *target_machine*.
    """
    with ffi.OutputString() as outerr:
        engine = ffi.lib.LLVMPY_CreateORCJITCompiler(
            module, target_machine, outerr)
        if not engine:
            raise RuntimeError(str(outerr))

    target_machine._owned = True
    return ExecutionEngine(engine, module=module)


