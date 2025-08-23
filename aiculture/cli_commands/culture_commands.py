"""
文化标准相关的CLI命令
"""

from pathlib import Path
from typing import Any

import click

from ..accessibility_culture import AccessibilityCultureManager
from ..culture_enforcer import CultureEnforcer


@click.group()
def culture_group() -> Any:
    """文化标准检查命令"""


@culture_group.command()
@click.option("--path", "-p", default=".", help="项目路径")
@click.option(
    "--type", "-t", multiple=True, help="检查类型 (accessibility, i18n, performance)"
)
def check(path: str, type: tuple) -> None:
    """检查文化标准合规性"""
    click.echo(f"🌍 检查文化标准: {path}")

    try:
        project_path = Path(path)

        # 如果没有指定类型，检查所有类型
        if not type:
            type = ("accessibility", "i18n", "performance")

        total_issues = 0

        # 可访问性和国际化检查
        if "accessibility" in type or "i18n" in type:
            click.echo("\n🔍 检查可访问性和国际化...")

            accessibility_manager = AccessibilityCultureManager(project_path)
            result = accessibility_manager.check_project_accessibility()

            i18n_issues = result.get("i18n_issues", [])
            accessibility_issues = result.get("accessibility_issues", [])

            click.echo(f"  🌐 国际化问题: {len(i18n_issues)}")
            click.echo(f"  ♿ 可访问性问题: {len(accessibility_issues)}")

            total_issues += len(i18n_issues) + len(accessibility_issues)

            # 显示详细问题
            if i18n_issues:
                click.echo("\n  📋 国际化问题详情:")
                for issue in i18n_issues[:5]:  # 只显示前5个
                    click.echo(
                        f"    • {issue.description} ({issue.file_path}:{issue.line_number})"
                    )

                if len(i18n_issues) > 5:
                    click.echo(f"    ... 还有 {len(i18n_issues) - 5} 个问题")

            if accessibility_issues:
                click.echo("\n  📋 可访问性问题详情:")
                for issue in accessibility_issues[:5]:  # 只显示前5个
                    click.echo(f"    • {issue}")

                if len(accessibility_issues) > 5:
                    click.echo(f"    ... 还有 {len(accessibility_issues) - 5} 个问题")

        # 性能检查
        if "performance" in type:
            click.echo("\n🚀 检查性能标准...")
            # 这里可以添加性能检查逻辑
            click.echo("  📊 性能检查功能开发中...")

        # 显示总结
        click.echo(f"\n📊 检查完成，发现 {total_issues} 个问题")

        if total_issues == 0:
            click.echo("🎉 恭喜！项目符合所有文化标准")
        else:
            click.echo("💡 建议修复发现的问题以提高项目质量")

    except Exception as e:
        click.echo(f"❌ 文化标准检查失败: {e}", err=True)
        raise click.Abort() from e


@culture_group.command()
@click.option("--path", "-p", default=".", help="项目路径")
@click.option("--output", "-o", default="culture-report.md", help="报告输出文件")
def report(path: str, output: str) -> None:
    """生成文化标准报告"""
    click.echo(f"📊 生成文化标准报告: {path}")

    try:
        project_path = Path(path)
        output_file = Path(output)

        # 运行检查
        accessibility_manager = AccessibilityCultureManager(project_path)
        report_data = accessibility_manager.generate_accessibility_report()

        # 生成报告内容
        report_content = f"""# 文化标准报告

## 项目概览

- **项目路径**: {project_path.absolute()}
- **生成时间**: {click.DateTime().now()}

## 检查摘要

"""

        summary = report_data.get("summary", {})
        report_content += f"""- **检查文件数**: {summary.get("total_files_checked", 0)}
- **发现问题数**: {summary.get("total_issues_found", 0)}
- **国际化问题**: {summary.get("i18n_issues_count", 0)}
- **可访问性问题**: {summary.get("accessibility_issues_count", 0)}

## 详细问题

"""

        # 添加详细问题
        detailed_issues = report_data.get("detailed_issues", [])
        if detailed_issues:
            for issue in detailed_issues:
                report_content += f"### {issue.get('type', '未知类型')}\n\n"
                report_content += f"- **文件**: {issue.get('file', '未知')}\n"
                report_content += f"- **描述**: {issue.get('description', '无描述')}\n"
                report_content += (
                    f"- **建议**: {issue.get('recommendation', '无建议')}\n\n"
                )
        else:
            report_content += "🎉 未发现任何问题！\n\n"

        # 添加建议
        recommendations = report_data.get("recommendations", [])
        if recommendations:
            report_content += "## 改进建议\n\n"
            for i, rec in enumerate(recommendations, 1):
                report_content += f"{i}. {rec}\n"

        report_content += """
---
*此报告由 AICultureKit 自动生成*
"""

        # 写入报告文件
        output_file.write_text(report_content)

        click.echo(f"✅ 文化标准报告已生成: {output_file}")

    except Exception as e:
        click.echo(f"❌ 生成报告失败: {e}", err=True)
        raise click.Abort() from e


@culture_group.command()
@click.option("--path", "-p", default=".", help="项目路径")
@click.option(
    "--strictness", "-s", default=0.7, type=float, help="执行严格度 (0.0-1.0)"
)
def enforce(path: str, strictness: float) -> None:
    """执行文化标准"""
    click.echo(f"⚖️  执行文化标准: {path}")
    click.echo(f"📊 严格度: {strictness}")

    try:
        project_path = Path(path)

        # 初始化文化执行器
        enforcer = CultureEnforcer(project_path)

        # 设置严格度
        enforcer.set_strictness(strictness)

        # 执行检查
        click.echo("🔍 执行文化标准检查...")
        result = enforcer.enforce_standards()

        # 显示结果
        if result.get("success", False):
            click.echo("✅ 文化标准执行成功")
        else:
            click.echo("❌ 文化标准执行失败")

            violations = result.get("violations", [])
            if violations:
                click.echo(f"\n📋 发现 {len(violations)} 个违规:")
                for violation in violations[:10]:  # 只显示前10个
                    click.echo(f"  • {violation}")

                if len(violations) > 10:
                    click.echo(f"  ... 还有 {len(violations) - 10} 个违规")

        # 显示统计信息
        stats = result.get("statistics", {})
        if stats:
            click.echo("\n📊 统计信息:")
            for key, value in stats.items():
                click.echo(f"  {key}: {value}")

    except Exception as e:
        click.echo(f"❌ 执行文化标准失败: {e}", err=True)
        raise click.Abort() from e


@culture_group.command()
@click.option("--path", "-p", default=".", help="项目路径")
def learn(path: str) -> None:
    """学习项目文化模式"""
    click.echo(f"🧠 学习项目文化模式: {path}")

    try:
        project_path = Path(path)

        # 这里可以集成AI学习系统
        from ..ai_learning_system import AILearningEngine

        learning_engine = AILearningEngine(project_path)
        result = learning_engine.learn_project_patterns()

        click.echo(f"📊 项目成熟度: {result.project_maturity}")
        click.echo(f"📈 推荐严格度: {result.recommended_strictness:.2f}")
        click.echo(f"🔍 发现模式数: {len(result.patterns)}")

        # 显示主要模式
        if result.patterns:
            click.echo("\n📋 主要模式:")
            for pattern in result.patterns[:5]:  # 只显示前5个
                click.echo(
                    f"  • {pattern.pattern_name}: {pattern.pattern_value} (置信度: {pattern.confidence:.2f})"
                )

        # 显示团队偏好
        if result.team_preferences:
            click.echo("\n👥 团队偏好:")
            for key, value in result.team_preferences.items():
                click.echo(f"  • {key}: {value}")

        click.echo("\n✅ 学习完成！结果已保存到 .aiculture/learning_result.json")

    except Exception as e:
        click.echo(f"❌ 学习失败: {e}", err=True)
        raise click.Abort() from e


@culture_group.command()
def standards() -> None:
    """显示支持的文化标准"""
    click.echo("📋 支持的文化标准:")

    standards = {
        "🌐 国际化 (i18n)": [
            "硬编码文本检测",
            "日期时间格式检查",
            "翻译完整性验证",
            "字符编码标准",
        ],
        "♿ 可访问性": [
            "HTML语义化检查",
            "图片alt属性验证",
            "颜色对比度检查",
            "键盘导航支持",
        ],
        "🚀 性能标准": [
            "响应时间要求",
            "资源使用优化",
            "缓存策略检查",
            "数据库查询优化",
        ],
        "📊 可观测性": [
            "日志记录标准",
            "错误处理规范",
            "监控指标定义",
            "调试信息完整性",
        ],
    }

    for category, items in standards.items():
        click.echo(f"\n{category}:")
        for item in items:
            click.echo(f"  • {item}")

    click.echo("\n💡 使用方法:")
    click.echo("   aiculture culture check --type accessibility")
    click.echo("   aiculture culture check --type i18n")
