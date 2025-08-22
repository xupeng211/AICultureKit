"""AI生成的文化执行器全面测试"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from aiculture.culture_enforcer import CultureEnforcer


class TestCultureEnforcerComprehensive(unittest.TestCase):
    """文化执行器全面测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.enforcer = CultureEnforcer(self.temp_dir)

    def test_enforcer_initialization(self):
        """测试执行器初始化"""
        self.assertIsNotNone(self.enforcer)
        self.assertEqual(str(self.enforcer.project_path), self.temp_dir)

    def test_enforce_all_basic(self):
        """测试基本执行功能"""
        try:
            result = self.enforcer.enforce_all()
            self.assertIsInstance(result, dict)
            self.assertIn("score", result)
            self.assertIn("violations", result)
        except Exception as e:
            self.fail(f"基本执行功能失败: {e}")

    def test_culture_principles_loading(self):
        """测试文化原则加载"""
        try:
            # 测试是否能正确加载文化原则
            self.assertTrue(hasattr(self.enforcer, "culture_principles"))
        except Exception as e:
            self.fail(f"文化原则加载失败: {e}")

    def test_violation_detection(self):
        """测试违规检测"""
        # 创建一个包含问题的测试文件
        test_file = Path(self.temp_dir) / "test_code.py"
        with open(test_file, "w") as f:
            f.write('# 测试代码\nprint("hello world")\n')

        try:
            result = self.enforcer.enforce_all()
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.fail(f"违规检测失败: {e}")

    def tearDown(self):
        """测试后清理"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
