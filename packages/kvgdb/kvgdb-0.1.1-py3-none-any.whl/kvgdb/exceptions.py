"""
kvgdb exceptions
"""

class KVGDBError(Exception):
    """KVGDB基础异常类"""
    pass

class PathError(KVGDBError):
    """路径相关错误"""
    pass

class InvalidPathError(PathError):
    """非法路径错误"""
    def __init__(self, path: str, reason: str = None):
        self.path = path
        self.reason = reason
        msg = f"Invalid path: {path}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)

class KeyNotFoundError(KVGDBError):
    """键不存在错误"""
    def __init__(self, key: str):
        self.key = key
        super().__init__(f"Key not found: {key}")

class GitError(KVGDBError):
    """Git操作错误"""
    def __init__(self, operation: str, details: str = None):
        self.operation = operation
        self.details = details
        msg = f"Git operation failed: {operation}"
        if details:
            msg += f"\nDetails: {details}"
        super().__init__(msg)

class StorageError(KVGDBError):
    """存储相关错误"""
    pass

class SerializationError(KVGDBError):
    """序列化/反序列化错误"""
    def __init__(self, operation: str, details: str = None):
        self.operation = operation
        self.details = details
        msg = f"Serialization error during {operation}"
        if details:
            msg += f"\nDetails: {details}"
        super().__init__(msg)

class LockError(KVGDBError):
    """锁相关错误"""
    def __init__(self, operation: str, details: str = None):
        self.operation = operation
        self.details = details
        msg = f"Lock operation failed: {operation}"
        if details:
            msg += f"\nDetails: {details}"
        super().__init__(msg)

class ConflictError(KVGDBError):
    """合并冲突错误"""
    def __init__(self, key: str, details: str = None):
        self.key = key
        self.details = details
        msg = f"Merge conflict in key: {key}"
        if details:
            msg += f"\nDetails: {details}"
        super().__init__(msg) 