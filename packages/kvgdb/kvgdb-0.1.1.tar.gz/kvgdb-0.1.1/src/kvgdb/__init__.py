"""
kvgdb - A Python library for key-value graph database
"""

__version__ = "0.1.1"

import os
import json
import subprocess
from typing import Any, List, Iterator
import fnmatch
import re
import tempfile
import fs
import shutil
from threading import Lock
from kvgdb.utils import LRUCache, is_valid_path
from kvgdb.exceptions import (
    InvalidPathError, KeyNotFoundError,
    GitError, StorageError, SerializationError
)


class GitKVDB:
    _instances = set()  # 跟踪所有实例

    def __init__(self, file_path: str, cache_size: int = 1000):
        """
        初始化数据库
        :param file_path: 数据库文件路径
        :param cache_size: 缓存大小（默认1000条）
        :raises StorageError: 存储初始化失败
        """
        self.repo_path = os.path.abspath(file_path)
        self._cache = LRUCache(cache_size)
        self._dirty_keys = set()
        self._lock = Lock()
        self._closed = False

        try:
            is_exist = os.path.exists(self.repo_path)

            self._is_zip = (os.path.isfile(
                self.repo_path) or not is_exist) and self.repo_path.lower().endswith('.kvb')
            self._work_dir = None
            if self._is_zip:
                self._work_dir = tempfile.mkdtemp()
                if is_exist:
                    zip_fs = fs.open_fs(f'zip://{self.repo_path}')
                    zip_fs.copydir('/', self._work_dir)
            else:
                if not is_exist:
                    os.makedirs(self.repo_path)
                self._work_dir = self.repo_path
            if not os.path.exists(os.path.join(self._work_dir, '.git')):
                self._git_init()
                
            # 注册实例
            self.__class__._instances.add(self)
        except Exception as e:
            raise StorageError(f"Failed to initialize storage: {str(e)}")

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器时自动关闭"""
        self.close()
        return False  # 不吞异常

    def __del__(self):
        """析构时自动关闭"""
        try:
            if not self._closed:
                self.close()
        except:
            pass  # 析构时的错误静默处理
        finally:
            # 从实例集合中移除
            self.__class__._instances.discard(self)

    @classmethod
    def _cleanup_all(cls):
        """清理所有未关闭的实例"""
        for instance in list(cls._instances):
            try:
                if not instance._closed:
                    instance.close()
            except:
                pass  # 清理时的错误静默处理

    def _git_init(self):
        """初始化Git仓库"""
        try:
            subprocess.run(['git', 'init'], cwd=self._work_dir, check=True)
        except subprocess.CalledProcessError as e:
            raise GitError("init", str(e))

    def _git_add(self, key: str):
        """添加文件到Git"""
        try:
            subprocess.run(['git', 'add', key], cwd=self.repo_path, check=True)
        except subprocess.CalledProcessError as e:
            raise GitError("add", str(e))

    def _git_rm(self, key: str):
        """从Git中删除文件"""
        try:
            subprocess.run(['git', 'rm', key], cwd=self.repo_path, check=True)
        except subprocess.CalledProcessError as e:
            raise GitError("rm", str(e))

    def _full_path(self, key: str | List[str]) -> str:
        split_keys = []
        # 处理列表路径
        if isinstance(key, list):
            for k in key:
                # 先统一分隔符为/，再分割
                k = str(k).replace('\\', '/')
                sub_keys = [x.strip() for x in k.split('/') if x.strip()]
                split_keys.extend(sub_keys)
        else:
            # 先统一分隔符为/，再分割
            key = str(key).replace('\\', '/')
            split_keys = [x.strip() for x in key.split('/') if x.strip()]

        if not is_valid_path(split_keys):
            raise InvalidPathError(str(key))

        # 构建完整路径并规范化
        full_path = os.path.join(self._work_dir, *split_keys)
        return os.path.normpath(full_path)

    def _key(self, path: str) -> str:
        """获取相对路径"""
        rel_path = os.path.relpath(path, self._work_dir)
        return rel_path.replace('\\', '/')

    def put(self, key: str | List[str], value: Any):
        """
        存储键值对
        :raises InvalidPathError: 路径非法
        :raises SerializationError: 序列化失败
        :raises GitError: Git操作失败
        :raises StorageError: 数据库已关闭
        """
        self._check_closed()
        with self._lock:
            path = self._full_path(key)
            inner_key = self._key(path)
            os.makedirs(os.path.dirname(path), exist_ok=True)

            try:
                if os.path.isdir(path):
                    raise KeyError(f"key {inner_key} is used as directory")
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(value, f, ensure_ascii=False, indent=2)
            except (TypeError, ValueError) as e:
                raise SerializationError("write", str(e))
                
            self._git_add(key)
            self._cache.put(inner_key, value)
            self._dirty_keys.add(inner_key)

    def get(self, key: str | List[str]) -> Any:
        """
        获取值
        :raises InvalidPathError: 路径非法
        :raises KeyNotFoundError: 键不存在
        :raises SerializationError: 反序列化失败
        :raises StorageError: 数据库已关闭
        """
        self._check_closed()

        path = self._full_path(key)
        inner_key = self._key(path)

        if not os.path.exists(path):
            raise KeyNotFoundError(str(key))

        # 先查缓存
        cached_value = self._cache.get(inner_key)
        if cached_value is not None:
            return cached_value

        try:
            with open(path, 'r', encoding='utf-8') as f:
                value = json.load(f)
        except json.JSONDecodeError as e:
            raise SerializationError("read", str(e))

        self._cache.put(inner_key, value)
        return value

    def delete(self, key: str | List[str]):
        """
        删除键值对
        :raises InvalidPathError: 路径非法
        :raises KeyNotFoundError: 键不存在
        :raises GitError: Git操作失败
        :raises StorageError: 数据库已关闭
        """
        self._check_closed()
        with self._lock:
            path = self._full_path(key)
            inner_key = self._key(path)

            if not os.path.exists(path):
                raise KeyNotFoundError(str(key))

            os.remove(path)
            self._git_rm(key)
            self._cache.remove(inner_key)
            self._dirty_keys.add(inner_key)

    def commit(self, message: str | None = None):
        """
        提交更改
        :raises GitError: Git操作失败
        :raises StorageError: 数据库已关闭
        """
        self._check_closed()
        if message is None:
            message = f"Update {len(self._dirty_keys)} items"

        with self._lock:
            if self._dirty_keys:
                try:
                    subprocess.run(['git', 'commit', '-m', message],
                               cwd=self.repo_path, check=True)
                    self._dirty_keys.clear()
                except subprocess.CalledProcessError as e:
                    raise GitError("commit", str(e))

    def list_versions(self, key: str):
        """返回该 key 的所有 commit hash（新到旧）。"""
        result = subprocess.run(
            ['git', 'log', '--pretty=format:%H', '--', key],
            cwd=self.repo_path, capture_output=True, text=True, check=True
        )
        return result.stdout.strip().splitlines()

    def get_version(self, key: str, commit_hash: str):
        """获取指定 commit 下该 key 的内容。"""
        result = subprocess.run(
            ['git', 'show', f'{commit_hash}:{key}'],
            cwd=self.repo_path, capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)

    def query_keys(self, prefix: str = '', pattern: str = '', regex: str = '') -> Iterator[str]:
        """批量查找 key，支持前缀、通配符、正则。返回迭代器。"""
        for root, _, files in os.walk(self.repo_path):
            for f in files:
                rel_path = os.path.relpath(
                    os.path.join(root, f), self.repo_path)
                if rel_path.startswith('.git'):
                    continue
                rel_path = rel_path.replace('\\', '/')
                # 过滤
                if prefix and not rel_path.startswith(prefix):
                    continue
                if pattern and not fnmatch.fnmatch(rel_path, pattern):
                    continue
                if regex and not re.search(regex, rel_path):
                    continue
                yield rel_path

    def discard_changes(self):
        """放弃所有未提交的更改，恢复到上一次 commit 状态"""
        with self._lock:
            subprocess.run(['git', 'reset', '--hard'],
                           cwd=self.repo_path, check=True)
            subprocess.run(['git', 'clean', '-fd'],
                           cwd=self.repo_path, check=True)
            # 清理缓存和脏键记录
            self._cache.clear()
            self._dirty_keys.clear()

    def close(self):
        """
        关闭数据库
        :raises StorageError: 关闭失败
        """
        if self._closed:
            return

        try:
            if self._is_zip and self._work_dir:
                # 保存未提交的更改
                if self._dirty_keys:
                    try:
                        self.commit("Auto commit on close")
                    except GitError:
                        pass  # 忽略提交错误

                # 写回zip文件
                zip_fs = fs.open_fs(f'zip://{self.repo_path}')
                zip_fs.removetree('/')
                fs.osfs.OSFS(self._work_dir).copydir('/', zip_fs)
                shutil.rmtree(self._work_dir)
                self._work_dir = None

            self._cache.clear()
            self._dirty_keys.clear()
            self._closed = True
        except Exception as e:
            raise StorageError(f"Failed to close database: {str(e)}")

    def _check_closed(self):
        """检查数据库是否已关闭"""
        if self._closed:
            raise StorageError("Database is closed")


if __name__ == '__main__':
    with GitKVDB("testdb") as db:
        db.put("a/b/c", 1)
        db.put("a/b/d", 2)

        for k in db.query_keys(pattern="a/b/*"):
            print(k, db.get(k))
