"""AI生成的AI行为系统全面测试"""

import sys
import tempfile
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from aiculture.ai_behavior_enforcer import AIBehaviorEnforcer


class TestAIBehaviorComprehensive(unittest.TestCase):
    """AI行为系统全面测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.enforcer = AIBehaviorEnforcer(self.temp_dir)

    def test_ai_behavior_enforcer_init(self):
        """测试AI行为执行器初始化"""
        self.assertIsNotNone(self.enforcer)
        self.assertEqual(str(self.enforcer.project_path), self.temp_dir)

    def test_enforce_ai_behavior(self):
        """测试AI行为执行"""
        try:
            result = self.enforcer.enforce_ai_behavior()
            self.assertIsInstance(result, dict)
            self.assertIn("violations_detected", result)
            self.assertIn("culture_compliance", result)
        except Exception as e:
            self.fail(f"AI行为执行测试失败: {e}")

    def test_violation_detection_rules(self):
        """测试违规检测规则"""
        try:
            # 测试是否有违规检测规则
            self.assertTrue(hasattr(self.enforcer, "violation_rules"))
        except Exception as e:
            self.fail(f"违规检测规则测试失败: {e}")

    def tearDown(self):
        """测试后清理"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
