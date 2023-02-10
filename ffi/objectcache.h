//
// Object cache
//

#ifndef LLVMPY_OBJECTCACHE_H_
#define LLVMPY_OBJECTCACHE_H_

#include "llvm-c/Object.h"
#include "llvm/ExecutionEngine/ObjectCache.h"

//extern "C" {

typedef struct {
    LLVMModuleRef modref;
    const char *buf_ptr;
    size_t buf_len;
} ObjectCacheData;

typedef void (*ObjectCacheNotifyFunc)(void *, const ObjectCacheData *);
typedef void (*ObjectCacheGetObjectFunc)(void *, ObjectCacheData *);


class LLVMPYObjectCache : public llvm::ObjectCache {
  public:
    LLVMPYObjectCache(ObjectCacheNotifyFunc notify_func,
                      ObjectCacheGetObjectFunc getobject_func, void *user_data);

    virtual void notifyObjectCompiled(const llvm::Module *M,
                                      llvm::MemoryBufferRef MBR);

    // MCJIT will call this function before compiling any module
    // MCJIT takes ownership of both the MemoryBuffer object and the memory
    // to which it refers.
    virtual std::unique_ptr<llvm::MemoryBuffer>
    getObject(const llvm::Module *M);

  private:
    ObjectCacheNotifyFunc notify_func;
    ObjectCacheGetObjectFunc getobject_func;
    void *user_data;
};

typedef LLVMPYObjectCache *LLVMPYObjectCacheRef;

//}

#endif /* LLVMPY_OBJECTCACHE_H_ */
