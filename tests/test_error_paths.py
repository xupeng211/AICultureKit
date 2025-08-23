"""
错误路径测试 - 便宜覆盖
专注于负路径、空列表/None/越界/错误类型，断言 ValueError/TypeError
"""
import pytest
from unittest.mock import Mock, patch
import tempfile
from pathlib import Path


class TestErrorHandlingPatterns:
    """错误处理模式测试"""
    
    @pytest.mark.parametrize("invalid_input,expected_error", [
        (None, TypeError),
        ("", ValueError),
        ([], ValueError),
        (-1, ValueError),
        (float('inf'), ValueError),
    ])
    def test_input_validation_errors(self, invalid_input, expected_error):
        """测试输入验证错误"""
        def validate_input(value):
            if value is None:
                raise TypeError("Input cannot be None")
            if isinstance(value, str) and not value.strip():
                raise ValueError("Input cannot be empty string")
            if isinstance(value, list) and len(value) == 0:
                raise ValueError("Input cannot be empty list")
            if isinstance(value, (int, float)) and value < 0:
                raise ValueError("Input cannot be negative")
            if isinstance(value, float) and not isinstance(value, bool) and (value == float('inf') or value != value):
                raise ValueError("Input cannot be infinity or NaN")
            return True
        
        with pytest.raises(expected_error):
            validate_input(invalid_input)
    
    def test_type_conversion_errors(self):
        """测试类型转换错误"""
        def safe_int_conversion(value):
            try:
                return int(value)
            except (ValueError, TypeError) as e:
                raise TypeError(f"Cannot convert {value} to int: {e}")
        
        # 测试无效转换
        with pytest.raises(TypeError):
            safe_int_conversion("not_a_number")
        
        with pytest.raises(TypeError):
            safe_int_conversion([1, 2, 3])
        
        # 测试有效转换
        assert safe_int_conversion("123") == 123
        assert safe_int_conversion(45.7) == 45


class TestCollectionBoundaryErrors:
    """集合边界错误测试"""
    
    def test_list_index_errors(self):
        """测试列表索引错误"""
        def safe_list_access(lst, index):
            if not isinstance(lst, list):
                raise TypeError("First argument must be a list")
            if not isinstance(index, int):
                raise TypeError("Index must be an integer")
            if index < 0 or index >= len(lst):
                raise IndexError(f"Index {index} out of range for list of length {len(lst)}")
            return lst[index]
        
        test_list = [1, 2, 3]
        
        # 有效访问
        assert safe_list_access(test_list, 0) == 1
        assert safe_list_access(test_list, 2) == 3
        
        # 越界访问
        with pytest.raises(IndexError):
            safe_list_access(test_list, 3)
        
        with pytest.raises(IndexError):
            safe_list_access(test_list, -1)
        
        # 类型错误
        with pytest.raises(TypeError):
            safe_list_access("not a list", 0)
        
        with pytest.raises(TypeError):
            safe_list_access(test_list, "not an int")
    
    def test_dict_key_errors(self):
        """测试字典键错误"""
        def safe_dict_access(d, key, default=None):
            if not isinstance(d, dict):
                raise TypeError("First argument must be a dictionary")
            if key is None:
                raise ValueError("Key cannot be None")
            return d.get(key, default)
        
        test_dict = {"a": 1, "b": 2}
        
        # 有效访问
        assert safe_dict_access(test_dict, "a") == 1
        assert safe_dict_access(test_dict, "nonexistent", "default") == "default"
        
        # 错误情况
        with pytest.raises(TypeError):
            safe_dict_access("not a dict", "key")
        
        with pytest.raises(ValueError):
            safe_dict_access(test_dict, None)
    
    def test_empty_collection_handling(self):
        """测试空集合处理"""
        def process_collection(collection):
            if collection is None:
                raise TypeError("Collection cannot be None")
            if len(collection) == 0:
                raise ValueError("Collection cannot be empty")
            return len(collection)
        
        # 有效集合
        assert process_collection([1, 2, 3]) == 3
        assert process_collection("hello") == 5
        assert process_collection({"a": 1}) == 1
        
        # 空集合
        with pytest.raises(ValueError):
            process_collection([])
        
        with pytest.raises(ValueError):
            process_collection("")
        
        with pytest.raises(ValueError):
            process_collection({})
        
        # None
        with pytest.raises(TypeError):
            process_collection(None)


class TestFileOperationErrors:
    """文件操作错误测试"""
    
    def test_file_not_found_errors(self):
        """测试文件未找到错误"""
        def read_config_file(file_path):
            if not file_path:
                raise ValueError("File path cannot be empty")
            
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Config file not found: {file_path}")
            
            if not path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            return "config_content"
        
        # 测试空路径
        with pytest.raises(ValueError, match="File path cannot be empty"):
            read_config_file("")
        
        # 测试不存在的文件
        with pytest.raises(FileNotFoundError):
            read_config_file("/non/existent/file.txt")
        
        # 测试目录而非文件
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="Path is not a file"):
                read_config_file(temp_dir)
        
        # 测试有效文件
        with tempfile.NamedTemporaryFile() as temp_file:
            result = read_config_file(temp_file.name)
            assert result == "config_content"
    
    def test_permission_errors(self):
        """测试权限错误"""
        def write_file_safely(file_path, content):
            if not file_path:
                raise ValueError("File path is required")
            if content is None:
                raise ValueError("Content cannot be None")
            
            try:
                with open(file_path, 'w') as f:
                    f.write(str(content))
                return True
            except PermissionError:
                raise PermissionError(f"No permission to write to {file_path}")
        
        # 测试参数验证
        with pytest.raises(ValueError):
            write_file_safely("", "content")
        
        with pytest.raises(ValueError):
            write_file_safely("/tmp/test.txt", None)
        
        # 模拟权限错误
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                write_file_safely("/tmp/test.txt", "content")


class TestNumericBoundaryErrors:
    """数值边界错误测试"""
    
    @pytest.mark.parametrize("value,min_val,max_val,should_raise", [
        (5, 1, 10, False),  # 有效范围
        (0, 1, 10, True),   # 小于最小值
        (11, 1, 10, True),  # 大于最大值
        (1, 1, 10, False),  # 边界值（最小）
        (10, 1, 10, False), # 边界值（最大）
    ])
    def test_range_validation(self, value, min_val, max_val, should_raise):
        """测试范围验证"""
        def validate_range(val, min_v, max_v):
            if not isinstance(val, (int, float)):
                raise TypeError("Value must be numeric")
            if val < min_v or val > max_v:
                raise ValueError(f"Value {val} must be between {min_v} and {max_v}")
            return val
        
        if should_raise:
            with pytest.raises(ValueError):
                validate_range(value, min_val, max_val)
        else:
            result = validate_range(value, min_val, max_val)
            assert result == value
    
    def test_division_by_zero(self):
        """测试除零错误"""
        def safe_division(numerator, denominator):
            if denominator == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)):
                raise TypeError("Both arguments must be numeric")
            return numerator / denominator
        
        # 有效除法
        assert safe_division(10, 2) == 5.0
        assert safe_division(7, 3) == pytest.approx(2.333, rel=1e-2)
        
        # 除零错误
        with pytest.raises(ZeroDivisionError):
            safe_division(10, 0)
        
        # 类型错误
        with pytest.raises(TypeError):
            safe_division("10", 2)
    
    def test_negative_value_handling(self):
        """测试负值处理"""
        def process_positive_value(value):
            if not isinstance(value, (int, float)):
                raise TypeError("Value must be numeric")
            if value < 0:
                raise ValueError("Value must be positive")
            if value == 0:
                raise ValueError("Value must be greater than zero")
            return value * 2
        
        # 有效值
        assert process_positive_value(5) == 10
        assert process_positive_value(0.5) == 1.0
        
        # 负值
        with pytest.raises(ValueError, match="Value must be positive"):
            process_positive_value(-1)
        
        # 零值
        with pytest.raises(ValueError, match="Value must be greater than zero"):
            process_positive_value(0)
        
        # 类型错误
        with pytest.raises(TypeError):
            process_positive_value("not a number")


class TestConfigurationErrors:
    """配置错误测试"""
    
    def test_missing_required_config(self):
        """测试缺少必需配置"""
        def validate_config(config):
            if not isinstance(config, dict):
                raise TypeError("Config must be a dictionary")
            
            required_keys = ["name", "version", "description"]
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                raise ValueError(f"Missing required configuration keys: {missing_keys}")
            
            # 验证值不为空
            empty_keys = [key for key in required_keys if not config[key]]
            if empty_keys:
                raise ValueError(f"Configuration keys cannot be empty: {empty_keys}")
            
            return True
        
        # 有效配置
        valid_config = {
            "name": "test_app",
            "version": "1.0.0",
            "description": "Test application"
        }
        assert validate_config(valid_config) is True
        
        # 缺少键
        with pytest.raises(ValueError, match="Missing required configuration keys"):
            validate_config({"name": "test_app"})
        
        # 空值
        with pytest.raises(ValueError, match="Configuration keys cannot be empty"):
            validate_config({"name": "", "version": "1.0.0", "description": "Test"})
        
        # 类型错误
        with pytest.raises(TypeError):
            validate_config("not a dict")
    
    def test_invalid_config_format(self):
        """测试无效配置格式"""
        def parse_json_config(json_string):
            if not json_string:
                raise ValueError("JSON string cannot be empty")
            
            import json
            try:
                config = json.loads(json_string)
                if not isinstance(config, dict):
                    raise ValueError("Configuration must be a JSON object")
                return config
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {e}")
        
        # 有效JSON
        valid_json = '{"name": "test", "version": "1.0"}'
        result = parse_json_config(valid_json)
        assert result["name"] == "test"
        
        # 空字符串
        with pytest.raises(ValueError, match="JSON string cannot be empty"):
            parse_json_config("")
        
        # 无效JSON
        with pytest.raises(ValueError, match="Invalid JSON format"):
            parse_json_config('{"invalid": json}')
        
        # 非对象JSON
        with pytest.raises(ValueError, match="Configuration must be a JSON object"):
            parse_json_config('["array", "not", "object"]') 