"""
AICultureKit CLI 命令行接口

提供便捷的命令行工具来管理AI开发文化和项目模板。

注意：此模块已重构为模块化结构，主要命令已迁移到cli_commands子包中。
"""

import click

from .cli_commands import culture_group, project_group, quality_group, template_group


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """
    AICultureKit - 标准化AI主导开发的文化和最佳实践工具包

    使用这个工具来：
    - 创建遵循最佳实践的新项目
    - 检查代码质量和文化标准
    - 生成项目模板和配置文件
    - 集成CI/CD流水线
    """


# 注册命令组
main.add_command(project_group, name="project")
main.add_command(quality_group, name="quality")
main.add_command(culture_group, name="culture")
main.add_command(template_group, name="template")


# 向后兼容的快捷命令
@main.command()
@click.argument("project_name")
@click.option("--path", "-p", default=".", help="项目创建路径")
@click.option("--template", "-t", default="python-basic", help="项目模板")
def create(project_name: str, path: str, template: str) -> None:
    """快速创建项目 (向后兼容)"""
    from .cli_commands.project_commands import create as project_create

    # 调用项目创建命令
    ctx = click.get_current_context()
    ctx.invoke(project_create, name=project_name, template=template, path=path)


@main.command()
@click.option("--path", "-p", default=".", help="项目路径")
def check(path: str) -> None:
    """快速质量检查 (向后兼容)"""
    from .cli_commands.quality_commands import check as quality_check

    # 调用质量检查命令
    ctx = click.get_current_context()
    ctx.invoke(quality_check, path=path, tool=(), fix=False)


@main.command()
@click.option("--path", "-p", default=".", help="项目路径")
def init(path: str) -> None:
    """快速初始化项目 (向后兼容)"""
    from .cli_commands.project_commands import init as project_init

    # 调用项目初始化命令
    ctx = click.get_current_context()
    ctx.invoke(project_init, path=path)


if __name__ == "__main__":
    main()
