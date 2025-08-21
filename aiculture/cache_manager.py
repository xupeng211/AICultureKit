"""
智能缓存管理器 - 用于提升性能和避免重复检查。
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Set

# 常量定义
HOURS_PER_DAY = 24


# 常量定义
SECONDS_PER_HOUR = 3600


@dataclass
class CacheEntry:
    """缓存条目"""

    file_hash: str
    last_modified: float
    violations: list
    created_at: float


class SmartCacheManager:
    """智能缓存管理器"""

    def __init__(self, project_path: Path, cache_dir: Optional[Path] = None) -> None:
        """初始化缓存管理器"""
        self.project_path = project_path
        self.cache_dir = cache_dir or project_path / ".aiculture" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 缓存文件路径
        self.culture_cache_file = self.cache_dir / "culture_check.json"
        self.dependency_cache_file = self.cache_dir / "dependencies.json"
        self.security_cache_file = self.cache_dir / "security.json"

        # 内存缓存
        self._memory_cache: Dict[str, CacheEntry] = {}

    @property
    def cache_data(self) -> Dict[str, CacheEntry]:
        """获取缓存数据"""
        return self._memory_cache

    def get_file_hash(self, file_path: Path) -> str:
        """计算文件内容哈希"""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            return hashlib.sha256(content).hexdigest()  # P0 Security Fix: MD5 -> SHA256
        except (OSError, IOError):
            return ""

    def is_file_cached(self, file_path: Path) -> bool:
        """检查文件是否已缓存且有效"""
        file_key = str(file_path.relative_to(self.project_path))

        # 检查内存缓存
        if file_key in self._memory_cache:
            cache_entry = self._memory_cache[file_key]
            current_hash = self.get_file_hash(file_path)
            current_mtime = file_path.stat().st_mtime

            # 验证缓存是否仍然有效
            if (
                cache_entry.file_hash == current_hash
                and cache_entry.last_modified == current_mtime
            ):
                return True

        return False

    def get_cached_violations(self, file_path: Path) -> Optional[list]:
        """获取缓存的违规记录"""
        file_key = str(file_path.relative_to(self.project_path))

        if file_key in self._memory_cache:
            return self._memory_cache[file_key].violations

        return None

    def cache_file_violations(self, file_path: Path, violations: list) -> None:
        """缓存文件的违规记录"""
        file_key = str(file_path.relative_to(self.project_path))

        cache_entry = CacheEntry(
            file_hash=self.get_file_hash(file_path),
            last_modified=file_path.stat().st_mtime,
            violations=violations,
            created_at=time.time(),
        )

        self._memory_cache[file_key] = cache_entry

    def load_cache(self) -> None:
        """从磁盘加载缓存"""
        try:
            if self.culture_cache_file.exists():
                with open(self.culture_cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                # 转换为CacheEntry对象
                for file_key, entry_data in cache_data.items():
                    self._memory_cache[file_key] = CacheEntry(**entry_data)

        except (json.JSONDecodeError, KeyError, TypeError):
            # 缓存文件损坏，忽略
            pass

    def save_cache(self) -> None:
        """保存缓存到磁盘"""
        try:
            # 清理过期缓存（超过7天）
            current_time = time.time()
            expired_keys = []

            for file_key, cache_entry in self._memory_cache.items():
                if (
                    current_time - cache_entry.created_at
                    > 7 * HOURS_PER_DAY * SECONDS_PER_HOUR
                ):  # 7天
                    expired_keys.append(file_key)

            for key in expired_keys:
                del self._memory_cache[key]

            # 转换为可序列化的格式
            cache_data = {}
            for file_key, cache_entry in self._memory_cache.items():
                cache_data[file_key] = asdict(cache_entry)

            # 保存到文件
            with open(self.culture_cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)

        except (OSError, IOError):
            # 保存失败，忽略
            pass

    def get_changed_files(self, since_timestamp: Optional[float] = None) -> Set[Path]:
        """获取自指定时间戳以来发生变化的文件"""
        changed_files = set()

        if since_timestamp is None:
            # 返回所有Python文件
            return set(self.project_path.rglob("*.py"))

        for file_path in self.project_path.rglob("*.py"):
            if any(part.startswith(".") for part in file_path.parts):
                continue

            try:
                if file_path.stat().st_mtime > since_timestamp:
                    changed_files.add(file_path)
            except OSError:
                continue

        return changed_files

    def clear_cache(self) -> None:
        """清空所有缓存"""
        self._memory_cache.clear()

        # 删除缓存文件
        for cache_file in [
            self.culture_cache_file,
            self.dependency_cache_file,
            self.security_cache_file,
        ]:
            if cache_file.exists():
                try:
                    cache_file.unlink()
                except OSError:
                    pass

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_files = len(list(self.project_path.rglob("*.py")))
        cached_files = len(self._memory_cache)

        cache_size = 0
        if self.culture_cache_file.exists():
            cache_size = self.culture_cache_file.stat().st_size

        return {
            "total_files": total_files,
            "cached_files": cached_files,
            "cache_hit_ratio": cached_files / total_files if total_files > 0 else 0,
            "cache_size_bytes": cache_size,
            "cache_dir": str(self.cache_dir),
        }


class IncrementalChecker:
    """增量检查器 - 只检查发生变化的文件"""

    def __init__(self, project_path: Path) -> None:
        """初始化增量检查器"""
        self.project_path = project_path
        self.cache_manager = SmartCacheManager(project_path)
        self.last_check_file = project_path / ".aiculture" / "last_check.txt"

    def get_last_check_timestamp(self) -> Optional[float]:
        """获取上次检查的时间戳"""
        try:
            if self.last_check_file.exists():
                with open(self.last_check_file, "r") as f:
                    return float(f.read().strip())
        except (ValueError, OSError):
            pass
        return None

    def update_last_check_timestamp(self) -> None:
        """更新最后检查时间戳"""
        try:
            self.last_check_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.last_check_file, "w") as f:
                f.write(str(time.time()))
        except OSError:
            pass

    def get_files_to_check(self) -> Set[Path]:
        """获取需要检查的文件列表"""
        last_check = self.get_last_check_timestamp()

        if last_check is None:
            # 首次检查，检查所有文件
            return set(self.project_path.rglob("*.py"))

        # 增量检查，只检查变化的文件
        changed_files = self.cache_manager.get_changed_files(last_check)

        # 过滤掉已缓存且有效的文件
        files_to_check = set()
        for file_path in changed_files:
            if not self.cache_manager.is_file_cached(file_path):
                files_to_check.add(file_path)

        return files_to_check

    def _get_current_timestamp(self) -> str:
        """获取当前时间戳字符串"""
        import datetime

        return datetime.datetime.now().isoformat()

    def should_force_full_check(self) -> bool:
        """判断是否应该强制进行全量检查"""
        last_check = self.get_last_check_timestamp()

        if last_check is None:
            return True

        # 如果超过24小时没有全量检查，强制全量检查
        return time.time() - last_check > HOURS_PER_DAY * SECONDS_PER_HOUR
