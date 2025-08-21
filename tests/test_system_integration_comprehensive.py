"""AI生成的系统集成全面测试"""

import sys
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestSystemIntegrationComprehensive(unittest.TestCase):
    """系统集成全面测试"""

    def test_module_imports(self):
        """测试所有核心模块导入"""
        try:
            from aiculture.ai_behavior_enforcer import AIBehaviorEnforcer
            from aiculture.culture_enforcer import CultureEnforcer
            from aiculture.data_governance_culture import DataPrivacyScanner
            from aiculture.problem_aggregator import ProblemAggregator

            self.assertTrue(True, "所有核心模块导入成功")
        except ImportError as e:
            self.fail(f"模块导入失败: {e}")

    def test_system_workflow(self):
        """测试系统工作流程"""
        try:
            from aiculture.culture_enforcer import CultureEnforcer

            # 测试基本工作流程
            enforcer = CultureEnforcer('.')
            result = enforcer.enforce_all()

            self.assertIsInstance(result, dict)
            self.assertIn('score', result)

        except Exception as e:
            self.fail(f"系统工作流程测试失败: {e}")

    def test_error_handling(self):
        """测试错误处理"""
        try:
            from aiculture.error_handling import get_logger

            logger = get_logger("test")
            self.assertIsNotNone(logger)

        except Exception as e:
            self.fail(f"错误处理测试失败: {e}")


if __name__ == "__main__":
    unittest.main()
