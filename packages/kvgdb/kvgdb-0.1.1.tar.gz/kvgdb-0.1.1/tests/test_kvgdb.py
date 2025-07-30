"""
Basic tests for kvgdb package.
"""
from kvgdb import __version__
import pytest
from kvgdb import GitKVDB


def test_version():
    """Test that version is set correctly."""
    assert __version__ == "0.1.1"


def test_git_kvdb_basic():

    db = GitKVDB("testdb")

    db.put("a/b/c", 1)
    db.put("a/b/d", 2)

    for k in db.query_keys(prefix="a"):
        print(k)

    db.close()


if __name__ == '__main__':
    test_git_kvdb_basic()
    print('GitKVDB 示例测试通过')
