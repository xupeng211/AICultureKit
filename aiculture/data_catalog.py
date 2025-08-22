"""
数据清单管理模块
提供数据资产的分类、管理和追踪功能
"""

import json
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .i18n import _


class DataAssetType(Enum):
    """数据资产类型"""

    TABLE = "table"
    VIEW = "view"
    FILE = "file"
    API = "api"
    STREAM = "stream"
    CACHE = "cache"


class DataClassification(Enum):
    """数据分类"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class DataFormat(Enum):
    """数据格式"""

    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PARQUET = "parquet"
    AVRO = "avro"
    BINARY = "binary"
    TEXT = "text"


@dataclass
class DataLineage:
    """数据血缘"""

    source_asset: str
    target_asset: str
    transformation: str
    created_at: float
    metadata: dict[str, Any]


@dataclass
class DataQualityMetrics:
    """数据质量指标"""

    completeness: float  # 完整性 (0-100)
    accuracy: float  # 准确性 (0-100)
    consistency: float  # 一致性 (0-100)
    timeliness: float  # 及时性 (0-100)
    validity: float  # 有效性 (0-100)
    last_updated: float


@dataclass
class DataAsset:
    """数据资产"""

    id: str
    name: str
    description: str
    asset_type: DataAssetType
    classification: DataClassification
    format: DataFormat
    owner: str
    steward: str
    location: str
    schema: dict[str, Any]
    tags: list[str]
    quality_metrics: DataQualityMetrics | None
    lineage: list[DataLineage]
    created_at: float
    updated_at: float
    metadata: dict[str, Any]


class DataCatalog:
    """数据目录"""

    def __init__(self, catalog_dir: Path):
        """__init__函数"""
        self.catalog_dir = catalog_dir
        self.catalog_file = catalog_dir / "data_catalog.json"
        self.lineage_file = catalog_dir / "data_lineage.json"

        # 确保目录存在
        catalog_dir.mkdir(parents=True, exist_ok=True)

        # 加载现有数据
        self.assets: dict[str, DataAsset] = {}
        self.lineages: list[DataLineage] = []
        self._load_catalog()

    def _load_catalog(self) -> None:
        """加载数据目录"""
        try:
            if self.catalog_file.exists():
                with open(self.catalog_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for asset_data in data.get("assets", []):
                        asset = self._dict_to_asset(asset_data)
                        self.assets[asset.id] = asset

            if self.lineage_file.exists():
                with open(self.lineage_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for lineage_data in data.get("lineages", []):
                        lineage = DataLineage(**lineage_data)
                        self.lineages.append(lineage)

        except Exception as e:
            print(f"Warning: Failed to load data catalog: {e}")

    def _dict_to_asset(self, data: dict[str, Any]) -> DataAsset:
        """将字典转换为数据资产对象"""
        # 处理枚举类型
        data["asset_type"] = DataAssetType(data["asset_type"])
        data["classification"] = DataClassification(data["classification"])
        data["format"] = DataFormat(data["format"])

        # 处理质量指标
        if data.get("quality_metrics"):
            data["quality_metrics"] = DataQualityMetrics(**data["quality_metrics"])

        # 处理血缘
        lineages = []
        for lineage_data in data.get("lineage", []):
            lineages.append(DataLineage(**lineage_data))
        data["lineage"] = lineages

        return DataAsset(**data)

    def _asset_to_dict(self, asset: DataAsset) -> dict[str, Any]:
        """将数据资产对象转换为字典"""
        data = asdict(asset)

        # 处理枚举类型
        data["asset_type"] = asset.asset_type.value
        data["classification"] = asset.classification.value
        data["format"] = asset.format.value

        return data

    def add_asset(self, asset: DataAsset) -> None:
        """添加数据资产"""
        asset.updated_at = time.time()
        self.assets[asset.id] = asset
        self._save_catalog()

    def update_asset(self, asset_id: str, updates: dict[str, Any]) -> bool:
        """更新数据资产"""
        if asset_id not in self.assets:
            return False

        asset = self.assets[asset_id]
        for key, value in updates.items():
            if hasattr(asset, key):
                setattr(asset, key, value)

        asset.updated_at = time.time()
        self._save_catalog()
        return True

    def remove_asset(self, asset_id: str) -> bool:
        """移除数据资产"""
        if asset_id not in self.assets:
            return False

        del self.assets[asset_id]

        # 移除相关血缘
        self.lineages = [
            lineage
            for lineage in self.lineages
            if lineage.source_asset != asset_id and lineage.target_asset != asset_id
        ]

        self._save_catalog()
        return True

    def get_asset(self, asset_id: str) -> DataAsset | None:
        """获取数据资产"""
        return self.assets.get(asset_id)

    def search_assets(
        self,
        query: str = None,
        asset_type: DataAssetType = None,
        classification: DataClassification = None,
        tags: list[str] = None,
    ) -> list[DataAsset]:
        """搜索数据资产"""
        results = list(self.assets.values())

        # 按查询条件过滤
        if query:
            query_lower = query.lower()
            results = [
                asset
                for asset in results
                if query_lower in asset.name.lower() or query_lower in asset.description.lower()
            ]

        if asset_type:
            results = [asset for asset in results if asset.asset_type == asset_type]

        if classification:
            results = [asset for asset in results if asset.classification == classification]

        if tags:
            results = [asset for asset in results if any(tag in asset.tags for tag in tags)]

        return results

    def add_lineage(
        self,
        source_asset: str,
        target_asset: str,
        transformation: str,
        metadata: dict[str, Any] = None,
    ) -> None:
        """添加数据血缘"""
        lineage = DataLineage(
            source_asset=source_asset,
            target_asset=target_asset,
            transformation=transformation,
            created_at=time.time(),
            metadata=metadata or {},
        )

        self.lineages.append(lineage)

        # 更新资产的血缘信息
        if source_asset in self.assets:
            self.assets[source_asset].lineage.append(lineage)
        if target_asset in self.assets:
            self.assets[target_asset].lineage.append(lineage)

        self._save_catalog()

    def get_lineage(self, asset_id: str, direction: str = "both") -> list[DataLineage]:
        """获取数据血缘"""
        lineages = []

        for lineage in self.lineages:
            if direction == "upstream" and lineage.target_asset == asset_id:
                lineages.append(lineage)
            elif direction == "downstream" and lineage.source_asset == asset_id:
                lineages.append(lineage)
            elif direction == "both" and (
                lineage.source_asset == asset_id or lineage.target_asset == asset_id
            ):
                lineages.append(lineage)

        return lineages

    def update_quality_metrics(self, asset_id: str, metrics: DataQualityMetrics) -> bool:
        """更新数据质量指标"""
        if asset_id not in self.assets:
            return False

        metrics.last_updated = time.time()
        self.assets[asset_id].quality_metrics = metrics
        self.assets[asset_id].updated_at = time.time()

        self._save_catalog()
        return True

    def get_quality_report(self) -> dict[str, Any]:
        """获取数据质量报告"""
        total_assets = len(self.assets)
        assets_with_metrics = sum(
            1 for asset in self.assets.values() if asset.quality_metrics is not None
        )

        if assets_with_metrics == 0:
            return {
                "total_assets": total_assets,
                "assets_with_metrics": 0,
                "coverage": 0,
                "average_quality": 0,
                "quality_breakdown": {},
            }

        # 计算平均质量分数
        total_completeness = 0
        total_accuracy = 0
        total_consistency = 0
        total_timeliness = 0
        total_validity = 0

        for asset in self.assets.values():
            if asset.quality_metrics:
                total_completeness += asset.quality_metrics.completeness
                total_accuracy += asset.quality_metrics.accuracy
                total_consistency += asset.quality_metrics.consistency
                total_timeliness += asset.quality_metrics.timeliness
                total_validity += asset.quality_metrics.validity

        avg_completeness = total_completeness / assets_with_metrics
        avg_accuracy = total_accuracy / assets_with_metrics
        avg_consistency = total_consistency / assets_with_metrics
        avg_timeliness = total_timeliness / assets_with_metrics
        avg_validity = total_validity / assets_with_metrics

        average_quality = (
            avg_completeness + avg_accuracy + avg_consistency + avg_timeliness + avg_validity
        ) / 5

        return {
            "total_assets": total_assets,
            "assets_with_metrics": assets_with_metrics,
            "coverage": (assets_with_metrics / total_assets) * 100,
            "average_quality": average_quality,
            "quality_breakdown": {
                "completeness": avg_completeness,
                "accuracy": avg_accuracy,
                "consistency": avg_consistency,
                "timeliness": avg_timeliness,
                "validity": avg_validity,
            },
        }

    def generate_catalog_report(self) -> dict[str, Any]:
        """生成数据目录报告"""
        # 按类型统计
        type_counts = {}
        for asset in self.assets.values():
            asset_type = asset.asset_type.value
            type_counts[asset_type] = type_counts.get(asset_type, 0) + 1

        # 按分类统计
        classification_counts = {}
        for asset in self.assets.values():
            classification = asset.classification.value
            classification_counts[classification] = classification_counts.get(classification, 0) + 1

        # 按所有者统计
        owner_counts = {}
        for asset in self.assets.values():
            owner = asset.owner
            owner_counts[owner] = owner_counts.get(owner, 0) + 1

        # 质量报告
        quality_report = self.get_quality_report()

        return {
            "total_assets": len(self.assets),
            "total_lineages": len(self.lineages),
            "by_type": type_counts,
            "by_classification": classification_counts,
            "by_owner": owner_counts,
            "quality_metrics": quality_report,
            "generated_at": time.time(),
        }

    def _save_catalog(self) -> None:
        """保存数据目录"""
        try:
            # 保存资产
            catalog_data = {
                "assets": [self._asset_to_dict(asset) for asset in self.assets.values()],
                "updated_at": time.time(),
            }

            with open(self.catalog_file, "w", encoding="utf-8") as f:
                json.dump(catalog_data, f, ensure_ascii=False, indent=2)

            # 保存血缘
            lineage_data = {
                "lineages": [asdict(lineage) for lineage in self.lineages],
                "updated_at": time.time(),
            }

            with open(self.lineage_file, "w", encoding="utf-8") as f:
                json.dump(lineage_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving data catalog: {e}")


# 使用示例
if __name__ == "__main__":
    # 创建数据目录
    catalog = DataCatalog(Path("./data_catalog"))

    # 创建示例数据资产
    user_table = DataAsset(
        id="user_table",
        name=_("User Table"),
        description=_("Main user information table"),
        asset_type=DataAssetType.TABLE,
        classification=DataClassification.CONFIDENTIAL,
        format=DataFormat.JSON,
        owner="data_team",
        steward="john.doe",
        location="database.users",
        schema={
            "user_id": {"type": "string", "required": True},
            "email": {"type": "string", "required": True},
            "name": {"type": "string", "required": True},
            "created_at": {"type": "datetime", "required": True},
        },
        tags=["user", "personal", "core"],
        quality_metrics=DataQualityMetrics(
            completeness=95.5,
            accuracy=98.2,
            consistency=92.1,
            timeliness=89.7,
            validity=96.8,
            last_updated=time.time(),
        ),
        lineage=[],
        created_at=time.time(),
        updated_at=time.time(),
        metadata={"retention_days": 365, "backup_enabled": True},
    )

    # 添加到目录
    catalog.add_asset(user_table)

    # 生成报告
    report = catalog.generate_catalog_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
