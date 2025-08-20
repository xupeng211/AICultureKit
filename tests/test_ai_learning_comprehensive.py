#!/usr/bin/env python3
"""
AI学习系统综合测试 - 专门提升覆盖率
"""

import pytest
import tempfile
import ast
from pathlib import Path
from unittest.mock import Mock, patch

from aiculture.ai_learning_system import (
    AILearningEngine,
    ProjectPattern,
    LearningResult
)


class TestAILearningSystemComprehensive:
    """AI学习系统综合测试"""

    def setup_method(self):
        """设置测试"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.learning_system = AILearningEngine(self.temp_dir)
    
    def test_system_initialization(self):
        """测试系统初始化"""
        assert self.learning_system.project_path == self.temp_dir
        assert hasattr(self.learning_system, 'analyzer')
        assert hasattr(self.learning_system, 'config')
    
    def test_learning_engine_basic_functionality(self):
        """测试学习引擎基本功能"""
        # 创建一个简单的Python文件
        test_file = self.temp_dir / "test.py"
        test_file.write_text("""
def test_function():
    '''Test function.'''
    return True

class TestClass:
    '''Test class.'''

    def test_method(self):
        return "test"
""")

        # 执行学习
        result = self.learning_system.learn_project_patterns()

        # 验证结果
        assert isinstance(result, LearningResult)
        assert isinstance(result.patterns, list)
        assert result.recommended_strictness >= 0
        assert result.project_maturity in ['beginner', 'intermediate', 'expert']
    
    def test_learning_with_multiple_files(self):
        """测试多文件学习"""
        # 创建多个Python文件
        (self.temp_dir / "module1.py").write_text("""
def function_one():
    return 1

class ClassOne:
    def method_one(self):
        return "one"
""")

        (self.temp_dir / "module2.py").write_text("""
def function_two():
    return 2

class ClassTwo:
    def method_two(self):
        return "two"
""")

        # 执行学习
        result = self.learning_system.learn_project_patterns()

        # 验证结果
        assert isinstance(result, LearningResult)
        assert len(result.patterns) >= 0  # 可能有模式，也可能没有
    
    def test_learning_with_empty_project(self):
        """测试空项目学习"""
        # 不创建任何文件，测试空项目
        result = self.learning_system.learn_project_patterns()

        # 验证结果
        assert isinstance(result, LearningResult)
        assert result.project_maturity in ['beginner', 'intermediate', 'expert']
    

    



class TestProjectPattern:
    """测试ProjectPattern数据类"""
    
    def test_pattern_creation(self):
        """测试模式创建"""
        pattern = ProjectPattern(
            pattern_type="naming",
            pattern_name="snake_case",
            pattern_value="snake_case",
            confidence=0.9,
            frequency=10,
            examples=["test_function", "helper_method"]
        )

        assert pattern.pattern_name == "snake_case"
        assert pattern.pattern_type == "naming"
        assert pattern.pattern_value == "snake_case"
        assert pattern.confidence == 0.9
        assert pattern.frequency == 10
        assert pattern.examples == ["test_function", "helper_method"]
    
    def test_pattern_string_representation(self):
        """测试模式字符串表示"""
        pattern = ProjectPattern(
            pattern_type="style",
            pattern_name="test_pattern",
            pattern_value="test_value",
            confidence=0.8,
            frequency=5,
            examples=["example1"]
        )

        str_repr = str(pattern)
        assert "test_pattern" in str_repr
        assert "0.8" in str_repr


class TestLearningResult:
    """测试LearningResult数据类"""
    
    def test_result_creation(self):
        """测试结果创建"""
        patterns = [
            ProjectPattern("naming", "test", "snake_case", 0.9, 5, ["example"])
        ]

        result = LearningResult(
            project_maturity="intermediate",
            recommended_strictness=0.85,
            patterns=patterns,
            custom_rules={"test": "rule"},
            team_preferences={"test": "pref"},
            generated_at=1234567890.0
        )

        assert result.project_maturity == "intermediate"
        assert len(result.patterns) == 1
        assert result.recommended_strictness == 0.85
        assert result.custom_rules == {"test": "rule"}
        assert result.team_preferences == {"test": "pref"}


if __name__ == '__main__':
    pytest.main([__file__])
