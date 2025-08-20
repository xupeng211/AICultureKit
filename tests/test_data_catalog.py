#!/usr/bin/env python3
"""
数据目录测试
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from aiculture.data_catalog import DataAsset, DataCatalog


class TestDataCatalog:
    """测试数据目录"""

    def setup_method(self):
        """设置测试"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.catalog = DataCatalog(self.temp_dir)

    def test_catalog_initialization(self):
        """测试目录初始化"""
        assert self.catalog.project_path == self.temp_dir
        assert self.catalog.catalog_dir == self.temp_dir / ".aiculture" / "data_catalog"
        assert (
            self.catalog.catalog_file == self.catalog.catalog_dir / "data_catalog.json"
        )
        assert isinstance(self.catalog.assets, dict)

    def test_scan_data_files(self):
        """测试扫描数据文件"""
        # 创建测试数据文件
        data_dir = self.temp_dir / "data"
        data_dir.mkdir(exist_ok=True)

        # CSV文件
        csv_file = data_dir / "test.csv"
        csv_file.write_text("name,age\nJohn,25\nJane,30")

        # JSON文件
        json_file = data_dir / "test.json"
        json_file.write_text('{"users": [{"name": "John", "age": 25}]}')

        # 扫描文件
        self.catalog.scan_data_files()

        # 验证资产被发现
        assert len(self.catalog.assets) >= 2

        # 检查CSV文件资产
        csv_asset_key = str(csv_file.relative_to(self.temp_dir))
        assert csv_asset_key in self.catalog.assets
        csv_asset = self.catalog.assets[csv_asset_key]
        assert csv_asset.file_type == 'csv'
        assert csv_asset.size > 0

    def test_add_asset(self):
        """测试添加资产"""
        asset = DataAsset(
            name="test_dataset",
            file_path="data/test.csv",
            file_type="csv",
            size=1024,
            description="Test dataset",
            tags=["test", "sample"],
            owner="test_user",
        )

        self.catalog.add_asset("test_key", asset)
        assert "test_key" in self.catalog.assets
        assert self.catalog.assets["test_key"] == asset

    def test_get_asset(self):
        """测试获取资产"""
        # 添加测试资产
        asset = DataAsset(
            name="test_dataset", file_path="data/test.csv", file_type="csv", size=1024
        )
        self.catalog.add_asset("test_key", asset)

        # 获取资产
        retrieved_asset = self.catalog.get_asset("test_key")
        assert retrieved_asset == asset

        # 获取不存在的资产
        assert self.catalog.get_asset("nonexistent") is None

    def test_search_assets(self):
        """测试搜索资产"""
        # 添加测试资产
        asset1 = DataAsset(
            name="user_data",
            file_path="data/users.csv",
            file_type="csv",
            tags=["users", "personal"],
        )
        asset2 = DataAsset(
            name="product_data",
            file_path="data/products.json",
            file_type="json",
            tags=["products", "catalog"],
        )

        self.catalog.add_asset("users", asset1)
        self.catalog.add_asset("products", asset2)

        # 按标签搜索
        user_assets = self.catalog.search_assets(tags=["users"])
        assert len(user_assets) == 1
        assert user_assets[0] == asset1

        # 按文件类型搜索
        csv_assets = self.catalog.search_assets(file_type="csv")
        assert len(csv_assets) == 1
        assert csv_assets[0] == asset1

        # 按名称搜索
        product_assets = self.catalog.search_assets(name_pattern="product")
        assert len(product_assets) == 1
        assert product_assets[0] == asset2

    def test_update_asset_metadata(self):
        """测试更新资产元数据"""
        # 添加测试资产
        asset = DataAsset(
            name="test_dataset",
            file_path="data/test.csv",
            file_type="csv",
            description="Original description",
        )
        self.catalog.add_asset("test_key", asset)

        # 更新元数据
        updates = {
            "description": "Updated description",
            "tags": ["updated", "test"],
            "owner": "new_owner",
        }

        success = self.catalog.update_asset_metadata("test_key", updates)
        assert success

        # 验证更新
        updated_asset = self.catalog.get_asset("test_key")
        assert updated_asset.description == "Updated description"
        assert updated_asset.tags == ["updated", "test"]
        assert updated_asset.owner == "new_owner"

        # 测试更新不存在的资产
        assert not self.catalog.update_asset_metadata("nonexistent", updates)

    def test_remove_asset(self):
        """测试移除资产"""
        # 添加测试资产
        asset = DataAsset(
            name="test_dataset", file_path="data/test.csv", file_type="csv"
        )
        self.catalog.add_asset("test_key", asset)
        assert "test_key" in self.catalog.assets

        # 移除资产
        success = self.catalog.remove_asset("test_key")
        assert success
        assert "test_key" not in self.catalog.assets

        # 测试移除不存在的资产
        assert not self.catalog.remove_asset("nonexistent")

    def test_generate_catalog_report(self):
        """测试生成目录报告"""
        # 添加测试资产
        asset1 = DataAsset(
            name="users",
            file_path="data/users.csv",
            file_type="csv",
            size=1024,
            owner="team_a",
        )
        asset2 = DataAsset(
            name="products",
            file_path="data/products.json",
            file_type="json",
            size=2048,
            owner="team_b",
        )

        self.catalog.add_asset("users", asset1)
        self.catalog.add_asset("products", asset2)

        # 生成报告
        report = self.catalog.generate_catalog_report()

        # 验证报告结构
        assert isinstance(report, dict)
        assert 'total_assets' in report
        assert 'by_type' in report
        assert 'by_owner' in report
        assert 'total_size' in report
        assert 'generated_at' in report

        # 验证报告内容
        assert report['total_assets'] == 2
        assert report['by_type']['csv'] == 1
        assert report['by_type']['json'] == 1
        assert report['by_owner']['team_a'] == 1
        assert report['by_owner']['team_b'] == 1
        assert report['total_size'] == 3072  # 1024 + 2048

    def test_save_and_load_catalog(self):
        """测试保存和加载目录"""
        # 添加测试资产
        asset = DataAsset(
            name="test_dataset",
            file_path="data/test.csv",
            file_type="csv",
            size=1024,
            description="Test dataset",
        )
        self.catalog.add_asset("test_key", asset)

        # 保存目录
        self.catalog._save_catalog()
        assert self.catalog.catalog_file.exists()

        # 创建新的目录实例并加载
        new_catalog = DataCatalog(self.temp_dir)
        new_catalog._load_catalog()

        # 验证加载的数据
        assert "test_key" in new_catalog.assets
        loaded_asset = new_catalog.assets["test_key"]
        assert loaded_asset.name == asset.name
        assert loaded_asset.file_path == asset.file_path
        assert loaded_asset.file_type == asset.file_type
        assert loaded_asset.size == asset.size
        assert loaded_asset.description == asset.description

    def test_get_asset_lineage(self):
        """测试获取资产血缘"""
        # 添加测试资产
        source_asset = DataAsset(
            name="raw_data", file_path="data/raw.csv", file_type="csv"
        )
        processed_asset = DataAsset(
            name="processed_data",
            file_path="data/processed.csv",
            file_type="csv",
            lineage={"source": "raw_data", "transformation": "clean_data"},
        )

        self.catalog.add_asset("raw", source_asset)
        self.catalog.add_asset("processed", processed_asset)

        # 获取血缘信息
        lineage = self.catalog.get_asset_lineage("processed")
        assert lineage is not None
        assert lineage["source"] == "raw_data"
        assert lineage["transformation"] == "clean_data"

        # 测试没有血缘的资产
        assert self.catalog.get_asset_lineage("raw") is None
        assert self.catalog.get_asset_lineage("nonexistent") is None

    def test_validate_asset_integrity(self):
        """测试验证资产完整性"""
        # 创建测试文件
        test_file = self.temp_dir / "test.csv"
        test_file.write_text("name,age\nJohn,25")

        # 添加资产
        asset = DataAsset(
            name="test_data",
            file_path=str(test_file.relative_to(self.temp_dir)),
            file_type="csv",
            size=test_file.stat().st_size,
        )
        self.catalog.add_asset("test", asset)

        # 验证完整性
        is_valid = self.catalog.validate_asset_integrity("test")
        assert is_valid

        # 测试文件不存在的情况
        asset.file_path = "nonexistent.csv"
        self.catalog.assets["test"] = asset
        assert not self.catalog.validate_asset_integrity("test")

        # 测试不存在的资产
        assert not self.catalog.validate_asset_integrity("nonexistent")


if __name__ == '__main__':
    pytest.main([__file__])
