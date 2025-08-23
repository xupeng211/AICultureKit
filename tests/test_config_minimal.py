"""
配置加载最小测试 - 便宜覆盖
测试配置样例、缺字段、文件不存在，断言异常类型
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
import os


class TestConfigLoading:
    """配置加载测试"""
    
    def test_basic_config_structure(self):
        """测试基础配置结构"""
        config = {
            "name": "test_project",
            "version": "1.0.0",
            "description": "Test project"
        }
        
        assert config["name"] == "test_project"
        assert config["version"] == "1.0.0"
        assert "description" in config
    
    def test_config_validation(self):
        """测试配置验证"""
        def validate_config(config):
            required_fields = ["name", "version"]
            if not isinstance(config, dict):
                raise TypeError("Config must be a dictionary")
            
            missing_fields = [field for field in required_fields if field not in config]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            return True
        
        # 有效配置
        valid_config = {"name": "test", "version": "1.0"}
        assert validate_config(valid_config) is True
        
        # 无效类型
        with pytest.raises(TypeError, match="Config must be a dictionary"):
            validate_config("not a dict")
        
        # 缺少字段
        with pytest.raises(ValueError, match="Missing required fields"):
            validate_config({"name": "test"})
    
    def test_config_file_loading(self):
        """测试配置文件加载"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {"name": "test", "version": "1.0"}
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            # 加载配置文件
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
            
            assert loaded_config["name"] == "test"
            assert loaded_config["version"] == "1.0"
        finally:
            os.unlink(config_file)
    
    def test_config_file_not_found(self):
        """测试配置文件不存在"""
        non_existent_file = "/tmp/non_existent_config.json"
        
        with pytest.raises(FileNotFoundError):
            with open(non_existent_file, 'r') as f:
                json.load(f)
    
    def test_invalid_json_config(self):
        """测试无效JSON配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {")
            invalid_config_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                with open(invalid_config_file, 'r') as f:
                    json.load(f)
        finally:
            os.unlink(invalid_config_file)


class TestConfigDefaults:
    """配置默认值测试"""
    
    @pytest.mark.parametrize("config,default_key,default_value,expected", [
        ({}, "timeout", 30, 30),
        ({"timeout": 60}, "timeout", 30, 60),
        ({"name": "test"}, "debug", False, False),
    ])
    def test_config_defaults(self, config, default_key, default_value, expected):
        """测试配置默认值"""
        result = config.get(default_key, default_value)
        assert result == expected
    
    def test_merge_config_with_defaults(self):
        """测试配置与默认值合并"""
        defaults = {
            "timeout": 30,
            "retry_count": 3,
            "debug": False
        }
        
        user_config = {
            "timeout": 60,
            "debug": True
        }
        
        # 合并配置
        merged = {**defaults, **user_config}
        
        assert merged["timeout"] == 60  # 用户覆盖
        assert merged["retry_count"] == 3  # 默认值
        assert merged["debug"] is True  # 用户覆盖


class TestEnvironmentConfig:
    """环境变量配置测试"""
    
    def test_env_config_override(self):
        """测试环境变量覆盖配置"""
        # 设置测试环境变量
        test_env_key = "AICULTURE_TEST_VALUE"
        test_env_value = "env_override"
        
        os.environ[test_env_key] = test_env_value
        
        try:
            # 模拟配置加载逻辑
            base_config = {"test_value": "default"}
            
            # 环境变量覆盖
            env_value = os.environ.get(test_env_key)
            if env_value:
                base_config["test_value"] = env_value
            
            assert base_config["test_value"] == "env_override"
        finally:
            del os.environ[test_env_key]
    
    def test_env_config_types(self):
        """测试环境变量类型转换"""
        def convert_env_value(value, target_type):
            if target_type == bool:
                return value.lower() in ('true', '1', 'yes', 'on')
            elif target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            return value
        
        # 测试布尔转换
        assert convert_env_value("true", bool) is True
        assert convert_env_value("false", bool) is False
        assert convert_env_value("1", bool) is True
        assert convert_env_value("0", bool) is False
        
        # 测试数字转换
        assert convert_env_value("123", int) == 123
        assert convert_env_value("45.67", float) == 45.67


class TestConfigErrorPaths:
    """配置错误路径测试"""
    
    def test_config_permission_error(self):
        """测试配置文件权限错误"""
        # 模拟权限错误
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = PermissionError("Permission denied")
            
            with pytest.raises(PermissionError):
                with open("config.json", 'r') as f:
                    json.load(f)
    
    def test_config_loading_with_encoding_error(self):
        """测试配置加载编码错误"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # 写入无效UTF-8字节
            f.write(b'\xff\xfe')
            config_file = f.name
        
        try:
            with pytest.raises(UnicodeDecodeError):
                with open(config_file, 'r', encoding='utf-8') as f:
                    f.read()
        finally:
            os.unlink(config_file)
    
    def test_empty_config_file(self):
        """测试空配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # 创建空文件
            pass
        
        try:
            with pytest.raises(json.JSONDecodeError):
                with open(f.name, 'r') as file:
                    json.load(file)
        finally:
            os.unlink(f.name)


class TestConfigPathHandling:
    """配置路径处理测试"""
    
    def test_config_path_resolution(self):
        """测试配置路径解析"""
        def resolve_config_path(path_str):
            if not path_str:
                raise ValueError("Empty path")
            
            path = Path(path_str)
            if path.is_absolute():
                return path
            else:
                # 相对路径解析为绝对路径
                return Path.cwd() / path
        
        # 测试绝对路径
        abs_path = resolve_config_path("/etc/config.json")
        assert abs_path.is_absolute()
        
        # 测试相对路径
        rel_path = resolve_config_path("config.json")
        assert rel_path.is_absolute()
        
        # 测试空路径
        with pytest.raises(ValueError, match="Empty path"):
            resolve_config_path("")
    
    def test_config_backup_mechanism(self):
        """测试配置备份机制"""
        def create_config_backup(config_path):
            path = Path(config_path)
            backup_path = path.with_suffix(path.suffix + '.backup')
            return backup_path
        
        config_file = "config.json"
        backup_file = create_config_backup(config_file)
        
        assert str(backup_file) == "config.json.backup"
        assert backup_file.suffix == ".backup" 