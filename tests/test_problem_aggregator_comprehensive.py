"""AI生成的问题聚合器全面测试"""

import sys
import tempfile
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from aiculture.problem_aggregator import ProblemAggregator


class TestProblemAggregatorComprehensive(unittest.TestCase):
    """问题聚合器全面测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.aggregator = ProblemAggregator(self.temp_dir)

    def test_aggregator_initialization(self):
        """测试聚合器初始化"""
        self.assertIsNotNone(self.aggregator)
        self.assertEqual(str(self.aggregator.project_path), self.temp_dir)

    def test_collect_all_problems(self):
        """测试问题收集功能"""
        try:
            problems = self.aggregator.collect_all_problems()
            self.assertIsInstance(problems, dict)
            self.assertIn('summary', problems)
            self.assertIn('categories', problems)
        except Exception as e:
            self.fail(f"问题收集失败: {e}")

    def test_problem_categorization(self):
        """测试问题分类"""
        try:
            problems = self.aggregator.collect_all_problems()
            categories = problems.get('categories', {})

            # 检查预期的分类是否存在
            expected_categories = [
                'ai_behavior_violations',
                'culture_errors',
                'culture_warnings',
                'security_issues',
            ]

            for category in expected_categories:
                self.assertIn(category, categories)

        except Exception as e:
            self.fail(f"问题分类测试失败: {e}")

    def tearDown(self):
        """测试后清理"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
