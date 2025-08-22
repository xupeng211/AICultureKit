"""
项目相关的CLI命令
"""

from pathlib import Path
from typing import Any

import click

from ..core import ProjectTemplate


@click.group()
def project_group() -> Any:
    """项目管理命令"""


@project_group.command()
@click.argument("name")
@click.option(
    "--template",
    "-t",
    default="python-basic",
    help="项目模板类型 (python-basic, python-web, python-ml)",
)
@click.option("--path", "-p", default=".", help="项目创建路径")
def create(name: str, template: str, path: str) -> None:
    """创建新项目"""
    click.echo(f"🚀 创建项目: {name}")
    click.echo(f"📋 使用模板: {template}")
    click.echo(f"📁 创建路径: {path}")

    try:
        project_path = Path(path) / name
        template_manager = ProjectTemplate()

        # 创建项目
        template_manager.create_project(name, template, project_path)

        click.echo(f"✅ 项目 '{name}' 创建成功！")
        click.echo(f"📁 项目路径: {project_path.absolute()}")

        # 显示下一步操作
        click.echo("\n📋 下一步操作:")
        click.echo(f"   cd {name}")
        click.echo("   aiculture quality check")

    except Exception as e:
        click.echo(f"❌ 创建项目失败: {e}", err=True)
        raise click.Abort()


@project_group.command()
@click.option("--path", "-p", default=".", help="项目路径")
def init(path: str) -> None:
    """初始化现有项目的AI文化配置"""
    click.echo(f"🔧 初始化项目配置: {path}")

    try:
        project_path = Path(path)

        # 检查是否已经初始化
        config_file = project_path / ".aiculture" / "config.yaml"
        if config_file.exists():
            click.echo("⚠️  项目已经初始化过了")
            if not click.confirm("是否要重新初始化？"):
                return

        # 创建配置目录
        config_dir = project_path / ".aiculture"
        config_dir.mkdir(exist_ok=True)

        # 创建基本配置文件
        config_content = """# AICultureKit 配置文件
version: "1.0"

# 质量检查配置
quality:
  enabled: true
  tools:
    - flake8
    - mypy
    - pytest

  # 严格度设置 (0.0-1.0)
  strictness: 0.7

# 文化标准配置
culture:
  accessibility:
    enabled: true
    check_i18n: true
    check_html: true

  performance:
    enabled: true
    max_response_time: 200

  observability:
    enabled: true
    require_logging: true

# 项目模板配置
template:
  type: "auto-detect"

# 自定义规则
custom_rules: {}
"""

        config_file.write_text(config_content)

        # 创建忽略文件
        ignore_file = project_path / ".aiculture" / ".ignore"
        ignore_content = """# AICultureKit 忽略文件
__pycache__/
*.pyc
.git/
.pytest_cache/
.mypy_cache/
venv/
env/
.env
node_modules/
"""
        ignore_file.write_text(ignore_content)

        click.echo("✅ 项目初始化完成！")
        click.echo(f"📁 配置文件: {config_file}")
        click.echo("\n📋 下一步操作:")
        click.echo("   aiculture quality check")
        click.echo("   aiculture culture check")

    except Exception as e:
        click.echo(f"❌ 初始化失败: {e}", err=True)
        raise click.Abort()


@project_group.command()
@click.option("--path", "-p", default=".", help="项目路径")
def status(path: str) -> None:
    """显示项目状态"""
    click.echo(f"📊 项目状态: {path}")

    try:
        project_path = Path(path)

        # 检查配置文件
        config_file = project_path / ".aiculture" / "config.yaml"
        if config_file.exists():
            click.echo("✅ 已初始化 AICultureKit")
        else:
            click.echo("❌ 未初始化 AICultureKit")
            click.echo("   运行 'aiculture project init' 来初始化")
            return

        # 检查项目类型
        if (project_path / "pyproject.toml").exists():
            click.echo("🐍 Python 项目 (pyproject.toml)")
        elif (project_path / "setup.py").exists():
            click.echo("🐍 Python 项目 (setup.py)")
        elif (project_path / "package.json").exists():
            click.echo("📦 Node.js 项目")
        else:
            click.echo("❓ 未知项目类型")

        # 统计文件数量
        python_files = list(project_path.rglob("*.py"))
        js_files = list(project_path.rglob("*.js"))

        click.echo(f"📄 Python 文件: {len(python_files)}")
        click.echo(f"📄 JavaScript 文件: {len(js_files)}")

        # 检查测试文件
        test_files = [f for f in python_files if "test" in str(f).lower()]
        click.echo(f"🧪 测试文件: {len(test_files)}")

        if python_files:
            test_ratio = len(test_files) / len(python_files)
            click.echo(f"📊 测试覆盖率估算: {test_ratio:.1%}")

    except Exception as e:
        click.echo(f"❌ 获取状态失败: {e}", err=True)
        raise click.Abort()


@project_group.command()
def templates() -> None:
    """列出可用的项目模板"""
    click.echo("📋 可用的项目模板:")

    templates = {
        "python-basic": "基础Python项目模板",
        "python-web": "Python Web应用模板 (Flask/FastAPI)",
        "python-ml": "Python机器学习项目模板",
        "python-cli": "Python命令行工具模板",
        "javascript-basic": "基础JavaScript项目模板",
        "javascript-web": "JavaScript Web应用模板",
        "typescript-basic": "基础TypeScript项目模板",
    }

    for template_name, description in templates.items():
        click.echo(f"  • {template_name:<20} - {description}")

    click.echo("\n💡 使用方法:")
    click.echo("   aiculture project create my-project --template python-web")


@project_group.command()
@click.option("--path", "-p", default=".", help="项目路径")
@click.option("--output", "-o", default="project-report.md", help="报告输出文件")
def report(path: str, output: str) -> None:
    """生成项目报告"""
    click.echo(f"📊 生成项目报告: {path}")

    try:
        project_path = Path(path)
        output_file = Path(output)

        # 收集项目信息
        python_files = list(project_path.rglob("*.py"))
        test_files = [f for f in python_files if "test" in str(f).lower()]

        # 生成报告内容
        report_content = f"""# 项目报告

## 项目概览

- **项目路径**: {project_path.absolute()}
- **生成时间**: {click.DateTime().now()}

## 文件统计

- **Python 文件**: {len(python_files)}
- **测试文件**: {len(test_files)}
- **测试覆盖率估算**: {len(test_files)/max(len(python_files), 1):.1%}

## 项目结构

```
{project_path.name}/
"""

        # 添加目录结构
        for item in sorted(project_path.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                report_content += f"├── {item.name}/\n"
            elif item.is_file() and not item.name.startswith("."):
                report_content += f"├── {item.name}\n"

        report_content += """```

## 建议

1. 运行质量检查: `aiculture quality check`
2. 检查文化标准: `aiculture culture check`
3. 增加测试覆盖率
4. 完善文档

---
*此报告由 AICultureKit 自动生成*
"""

        # 写入报告文件
        output_file.write_text(report_content)

        click.echo(f"✅ 报告已生成: {output_file}")

    except Exception as e:
        click.echo(f"❌ 生成报告失败: {e}", err=True)
        raise click.Abort()
