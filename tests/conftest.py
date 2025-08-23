"""
Pytest 配置和隔离机制
"""
import os
from pathlib import Path
import pytest

QUARANTINE_FILE = Path(__file__).parent / "_ci_quarantine.txt"


def pytest_collection_modifyitems(items):
    """动态标记隔离的测试"""
    if not QUARANTINE_FILE.exists():
        return
    
    try:
        quarantined = {
            line.strip()
            for line in QUARANTINE_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        }
        if not quarantined:
            return
    except Exception:
        return

    for item in items:
        # item.nodeid 形如 "tests/test_xxx.py::TestClass::test_func[param]"
        if any(quarantine_pattern in item.nodeid for quarantine_pattern in quarantined):
            item.add_marker(pytest.mark.quarantine)


def pytest_ignore_collect(collection_path, config):
    """忽略整个测试文件"""
    if not QUARANTINE_FILE.exists():
        return False
        
    try:
        quarantined = {
            line.strip()
            for line in QUARANTINE_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        }
        if not quarantined:
            return False
    except Exception:
        return False
    
    # 处理 pathlib.Path 对象
    if hasattr(collection_path, 'relative_to'):
        try:
            relative_path = str(collection_path.relative_to(Path.cwd()))
        except ValueError:
            relative_path = str(collection_path)
    else:
        # 兼容 py.path.local 对象
        relative_path = str(collection_path)
        if hasattr(collection_path, 'relto'):
            try:
                relative_path = collection_path.relto(Path.cwd()) or str(collection_path)
            except:
                pass
    
    return any(quarantine_pattern in relative_path for quarantine_pattern in quarantined) 