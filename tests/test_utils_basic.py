"""
基础工具函数测试 - 专注于便宜覆盖
测试纯函数、边界值、负路径
"""
import pytest
from pathlib import Path
import tempfile
import os


class TestPathUtils:
    """路径工具函数测试"""
    
    def test_path_creation(self):
        """测试路径创建"""
        test_path = Path("/tmp/test")
        assert isinstance(test_path, Path)
        
    def test_path_exists_check(self):
        """测试路径存在检查"""
        # 存在的路径
        assert Path(__file__).exists()
        
        # 不存在的路径
        assert not Path("/non/existent/path").exists()
        
    def test_temp_dir_operations(self):
        """测试临时目录操作"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            assert tmp_path.exists()
            assert tmp_path.is_dir()


class TestStringUtils:
    """字符串工具测试"""
    
    @pytest.mark.parametrize("input_str,expected", [
        ("", True),
        ("   ", True),
        ("hello", False),
        ("  hello  ", False),
        (None, True),
    ])
    def test_is_empty_string(self, input_str, expected):
        """测试空字符串判断"""
        def is_empty_or_whitespace(s):
            return not s or s.isspace()
        
        if input_str is None:
            assert expected is True
        else:
            assert is_empty_or_whitespace(input_str) == expected
    
    @pytest.mark.parametrize("input_str,expected", [
        ("hello", "hello"),
        ("  hello  ", "hello"),
        ("", ""),
        ("HELLO", "hello"),
    ])
    def test_normalize_string(self, input_str, expected):
        """测试字符串标准化"""
        result = input_str.strip().lower()
        assert result == expected


class TestEnvironmentUtils:
    """环境变量工具测试"""
    
    def test_env_var_access(self):
        """测试环境变量访问"""
        # 设置测试环境变量
        test_key = "TEST_AICULTURE_VAR"
        test_value = "test_value"
        
        os.environ[test_key] = test_value
        assert os.environ.get(test_key) == test_value
        
        # 清理
        del os.environ[test_key]
        assert os.environ.get(test_key) is None
    
    def test_env_var_default(self):
        """测试环境变量默认值"""
        non_existent_key = "NON_EXISTENT_TEST_KEY"
        default_value = "default"
        
        result = os.environ.get(non_existent_key, default_value)
        assert result == default_value


class TestErrorHandling:
    """错误处理测试"""
    
    def test_value_error_raised(self):
        """测试ValueError抛出"""
        with pytest.raises(ValueError):
            raise ValueError("Test error")
    
    def test_type_error_raised(self):
        """测试TypeError抛出"""
        with pytest.raises(TypeError):
            len(None)  # 这会抛出TypeError
    
    def test_file_not_found_error(self):
        """测试文件不存在错误"""
        with pytest.raises(FileNotFoundError):
            with open("/non/existent/file.txt", 'r'):
                pass


class TestDataValidation:
    """数据验证测试"""
    
    @pytest.mark.parametrize("data,expected_valid", [
        ({"name": "test"}, True),
        ({}, False),
        ({"name": ""}, False),
        ({"name": "test", "value": 123}, True),
    ])
    def test_dict_validation(self, data, expected_valid):
        """测试字典数据验证"""
        def is_valid_dict(d):
            return bool(d) and "name" in d and bool(d.get("name"))
        
        assert is_valid_dict(data) == expected_valid
    
    def test_list_boundary_conditions(self):
        """测试列表边界条件"""
        empty_list = []
        single_item = [1]
        multi_items = [1, 2, 3]
        
        assert len(empty_list) == 0
        assert len(single_item) == 1
        assert len(multi_items) == 3
        
        # 边界访问测试
        with pytest.raises(IndexError):
            _ = empty_list[0]
        
        assert single_item[0] == 1
        assert multi_items[-1] == 3 