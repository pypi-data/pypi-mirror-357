import os
from typing import Any, List
from collections import OrderedDict
from threading import Lock

class LRUCache:
    """LRU缓存实现"""

    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = Lock()

    def get(self, key: str) -> Any | None:
        with self.lock:
            if key not in self.cache:
                return None
            # 移动到最新
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: str, value: Any) -> None:
        with self.lock:
            if key in self.cache:
                # 已存在则更新并移动到最新
                self.cache.move_to_end(key)
            self.cache[key] = value
            # 超出容量则删除最旧的
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)

    def remove(self, key: str) -> None:
        with self.lock:
            self.cache.pop(key, None)

    def clear(self) -> None:
        with self.lock:
            self.cache.clear()


# 不允许的字符
INVALID_CHARS = '<>:"|?*\x00-\x1f'

def is_valid_path(path_parts: List[str]) -> bool:
    """检查路径是否合法
    
    Args:
        path_parts: 分割好的路径部分列表
        
    规则：
    1. 不能是空列表
    2. 每个部分不能为空
    3. 不能包含特殊字符
    4. 不能是 '.git' 相关路径
    5. 不能包含 '.' 或 '..' (当前目录或上级目录)
    6. 每个部分不能以点开头
    """
    # 检查空列表
    if not path_parts:
        return False
        
    # 检查每个部分
    for part in path_parts:
        # 检查空部分
        if not part or part.isspace():
            return False
            
        # 检查特殊字符
        if any(c in part for c in INVALID_CHARS):
            return False
            
        # 检查点号开头
        if part.startswith('.'):
            return False
            
        # 检查当前目录和上级目录
        if part in {'.', '..'}:
            return False
            
    # 检查 .git 路径
    if path_parts[0] == '.git' or '.git' in path_parts:
        return False
        
    return True