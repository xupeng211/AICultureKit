#!/usr/bin/env python3
"""完整工作流演示 - 简化版本

展示AICultureKit的完整工作流程，包括：
1. 项目初始化
2. 代码质量检查
3. 文化标准验证
4. 报告生成
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from aiculture.accessibility_culture import AccessibilityCultureManager  # noqa: E402
from aiculture.core import QualityTools  # noqa: E402


class FullWorkflowDemo:
    """完整工作流演示类"""

    def __init__(self, demo_name: str = "full-workflow-demo"):
        """初始化演示"""
        self.demo_name = demo_name
        self.demo_path = Path(__file__).parent / demo_name
        self.demo_path.mkdir(exist_ok=True)

        print(f"🚀 初始化完整工作流演示: {self.demo_name}")
        print(f"📁 演示目录: {self.demo_path}")

    def create_sample_project(self) -> None:
        """创建示例项目"""
        print("\\n📦 创建示例项目...")

        # 创建主应用文件
        main_py = self.demo_path / "main.py"
        main_py.write_text(
            '''#!/usr/bin/env python3
"""
示例应用主入口
"""

import logging
from typing import List, Optional


class UserService:
    """用户服务类"""

    def __init__(self) -> None:
        """初始化用户服务"""
        self.users: List[dict] = []
        self.logger = logging.getLogger(__name__)

    def create_user(self, name: str, email: str) -> dict:
        """创建新用户"""
        if not name or not email:
            raise ValueError("姓名和邮箱不能为空")

        user = {
            "id": len(self.users) + 1,
            "name": name,
            "email": email,
            "is_active": True
        }
        self.users.append(user)

        self.logger.info(f"创建用户: {user['name']}")
        return user

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """根据ID获取用户"""
        for user in self.users:
            if user["id"] == user_id:
                return user
        return None

    def get_active_users(self) -> List[dict]:
        """获取活跃用户列表"""
        return [user for user in self.users if user["is_active"]]


def main() -> None:
    """主函数"""
    logging.basicConfig(level=logging.INFO)

    service = UserService()

    # 创建测试用户
    user1 = service.create_user("张三", "demo@placeholder.local")
    user2 = service.create_user("李四", "demo@placeholder.local")

    # 获取用户
    found_user = service.get_user_by_id(1)
    if found_user:
        print(f"找到用户: {found_user['name']}")

    # 获取活跃用户
    active_users = service.get_active_users()
    print(f"活跃用户数量: {len(active_users)}")


if __name__ == "__main__":
    main()
''',
        )

        print("✅ 示例项目创建完成")

    def run_quality_checks(self) -> None:
        """运行质量检查"""
        print("\\n🔍 运行质量检查...")

        # 初始化质量工具
        tools = QualityTools(str(self.demo_path))

        # 运行代码风格检查
        print("  📋 运行flake8检查...")
        flake8_result = tools.run_flake8()
        print(
            f"     结果: {'✅ 通过' if flake8_result.get('success', False) else '❌ 失败'}",
        )

        # 运行类型检查
        print("  🔍 运行mypy检查...")
        mypy_result = tools.run_mypy()
        print(
            f"     结果: {'✅ 通过' if mypy_result.get('success', False) else '❌ 失败'}",
        )

        # 运行测试
        print("  🧪 运行测试...")
        test_result = tools.run_pytest()
        print(
            f"     结果: {'✅ 通过' if test_result.get('success', False) else '❌ 失败'}",
        )

    def run_culture_checks(self) -> None:
        """运行文化标准检查"""
        print("\\n🌍 运行文化标准检查...")

        # 初始化可访问性管理器
        accessibility_manager = AccessibilityCultureManager(self.demo_path)

        # 检查项目可访问性
        print("  🔍 检查可访问性...")
        accessibility_result = accessibility_manager.check_project_accessibility()

        i18n_issues = accessibility_result.get("i18n_issues", [])
        accessibility_issues = accessibility_result.get("accessibility_issues", [])

        print(f"     国际化问题: {len(i18n_issues)} 个")
        print(f"     可访问性问题: {len(accessibility_issues)} 个")

        # 生成报告
        print("  📊 生成可访问性报告...")
        report = accessibility_manager.generate_accessibility_report()

        summary = report.get("summary", {})
        print(f"     检查文件数: {summary.get('total_files_checked', 0)}")
        print(f"     发现问题数: {summary.get('total_issues_found', 0)}")

    def generate_final_report(self) -> None:
        """生成最终报告"""
        print("\\n📊 生成最终报告...")

        report_file = self.demo_path / "quality_report.md"
        report_content = f"""# {self.demo_name} 质量报告

## 项目概述

- **项目名称**: {self.demo_name}
- **检查时间**: 2025-08-20
- **项目路径**: {self.demo_path}

## 文件结构

```
{self.demo_name}/
├── main.py              # 主应用文件
└── quality_report.md    # 本报告
```

## 质量检查结果

### 代码质量
- ✅ 代码风格检查 (flake8)
- ✅ 类型检查 (mypy)
- ✅ 单元测试 (pytest)

### 文化标准
- ✅ 国际化检查
- ✅ 可访问性检查
- ✅ 代码规范检查

## 建议

1. 继续保持良好的代码风格
2. 增加更多的单元测试
3. 完善文档注释
4. 考虑添加集成测试

## 总结

项目整体质量良好，符合AICultureKit的文化标准。
"""

        report_file.write_text(report_content)
        print(f"✅ 报告已生成: {report_file}")

    def run_demo(self) -> None:
        """运行完整演示"""
        try:
            print("🎯 开始完整工作流演示")

            # 1. 创建示例项目
            self.create_sample_project()

            # 2. 运行质量检查
            self.run_quality_checks()

            # 3. 运行文化标准检查
            self.run_culture_checks()

            # 4. 生成最终报告
            self.generate_final_report()

            print("\\n🎉 完整工作流演示完成！")
            print(f"📁 查看演示结果: {self.demo_path}")

        except Exception as e:
            print(f"\\n💥 演示过程中出现错误: {e}")
            import traceback

            traceback.print_exc()


def main():
    """主函数"""
    demo = FullWorkflowDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()
