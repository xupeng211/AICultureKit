# tests/conftest.py
import os
from pathlib import Path
import pytest

QUARANTINE_FILE = Path(__file__).parent / "_ci_quarantine.txt"

def pytest_collection_modifyitems(items):
    """在采集阶段动态标记隔离测试用例"""
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
        # 检查完整 nodeid 匹配或部分匹配（支持文件级隔离）
        for quarantine_pattern in quarantined:
            if quarantine_pattern in item.nodeid or item.nodeid.startswith(quarantine_pattern):
                item.add_marker(pytest.mark.quarantine)
                break

def pytest_ignore_collect(path, config):
    """在采集阶段忽略整个测试文件"""
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
    
    # 检查是否应该忽略这个文件（兼容 py.path.local 和 pathlib）
    try:
        if hasattr(path, 'relative_to'):
            # pathlib.Path
            relative_path = str(path.relative_to(Path(__file__).parent.parent))
        else:
            # py.path.local
            relative_path = str(path.relto(Path(__file__).parent.parent))
        return relative_path in quarantined
    except Exception:
        # 回退：直接检查文件名
        path_str = str(path)
        return any(quarantine in path_str for quarantine in quarantined) 