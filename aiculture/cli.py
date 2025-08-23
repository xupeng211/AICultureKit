"""
AICultureKit CLI 命令行接口

提供便捷的命令行工具来管理AI开发文化和项目模板。

注意：此模块已重构为模块化结构，主要命令已迁移到cli_commands子包中。
"""

import click

from .cli_commands import (
    project_group,
    quality_group,
    culture_group,
    template_group,
    ai_group,  # 新增AI协作命令组
    ai_context  # 快捷命令
)


@click.group()
@click.version_option(version="0.2.0")  # 版本升级到0.2.0
def main() -> None:
    """
    🤖 AICultureKit - AI协作增效工具包
    
    专注解决AI开发中的实际痛点：
    • 上下文传递 - 自动生成项目摘要给AI
    • 代码一致性 - 检测AI生成代码的风格问题  
    • 增量迭代 - 维护AI协作的历史上下文
    • 质量把控 - 智能代码审查和改进建议
    
    快速开始：
    \b
    aiculture ai context              # 生成项目上下文给AI
    aiculture ai context -o ctx.md   # 保存到文件
    """
    pass


# 注册命令组 - AI协作是核心功能
main.add_command(ai_group, name='ai')           # 🤖 AI协作 (新的核心功能)
main.add_command(project_group, name='project') # 📁 项目管理
main.add_command(quality_group, name='quality') # 🔍 质量检查  
main.add_command(culture_group, name='culture') # 📚 开发文化
main.add_command(template_group, name='template') # 📋 模板管理

# 快捷命令 - 最常用的功能
main.add_command(ai_context, name='ctx')  # 快捷上下文生成


# 向后兼容的快捷命令
@main.command()
@click.argument('project_name')
@click.option('--path', '-p', default='.', help='项目创建路径')
@click.option('--template', '-t', default='python-basic', help='项目模板')
def create(project_name: str, path: str, template: str) -> None:
    """快速创建项目 (向后兼容)"""
    from .cli_commands.project_commands import create as project_create

    # 调用项目创建命令
    ctx = click.get_current_context()
    ctx.invoke(project_create, project_name=project_name, path=path, template=template)


@main.command()
@click.option('--fix', is_flag=True, help='自动修复发现的问题')
def check(fix: bool) -> None:
    """快速质量检查 (向后兼容)"""
    from .cli_commands.quality_commands import check as quality_check
    
    ctx = click.get_current_context()
    ctx.invoke(quality_check, fix=fix)


if __name__ == '__main__':
    main()