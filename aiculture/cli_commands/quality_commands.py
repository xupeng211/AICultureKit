"""
质量检查相关的CLI命令
"""

import subprocess
from pathlib import Path
from typing import Any

import click

from ..core import QualityTools


@click.group()
def quality_group() -> Any:
    """代码质量检查命令"""
    pass


@quality_group.command()
@click.option('--path', '-p', default='.', help='项目路径')
@click.option('--tool', '-t', multiple=True, help='指定检查工具 (flake8, mypy, pytest)')
@click.option('--fix', is_flag=True, help='自动修复可修复的问题')
def check(path: str, tool: tuple, fix: bool) -> None:
    """运行代码质量检查"""
    click.echo(f"🔍 运行质量检查: {path}")

    try:
        project_path = Path(path)
        tools = QualityTools(str(project_path))

        # 如果没有指定工具，运行所有工具
        if not tool:
            tool = ('flake8', 'mypy', 'pytest')

        results = {}

        # 运行指定的工具
        for tool_name in tool:
            click.echo(f"\n📋 运行 {tool_name}...")

            if tool_name == 'flake8':
                result = tools.run_flake8()
            elif tool_name == 'mypy':
                result = tools.run_mypy()
            elif tool_name == 'pytest':
                result = tools.run_pytest()
            else:
                click.echo(f"❌ 未知工具: {tool_name}")
                continue

            results[tool_name] = result

            # 显示结果
            if result.get('success', False):
                click.echo(f"✅ {tool_name} 检查通过")
            else:
                click.echo(f"❌ {tool_name} 检查失败")
                if 'output' in result:
                    click.echo(result['output'])

        # 自动修复
        if fix:
            click.echo("\n🔧 尝试自动修复...")
            _auto_fix_issues(project_path)

        # 显示总结
        _show_quality_summary(results)

    except Exception as e:
        click.echo(f"❌ 质量检查失败: {e}", err=True)
        raise click.Abort()


@quality_group.command()
@click.option('--path', '-p', default='.', help='项目路径')
def format(path: str) -> None:
    """格式化代码"""
    click.echo(f"🎨 格式化代码: {path}")

    try:
        project_path = Path(path)

        # 运行 black
        click.echo("📋 运行 black...")
        result = subprocess.run(
            ['black', str(project_path)], capture_output=True, text=True
        )

        if result.returncode == 0:
            click.echo("✅ black 格式化完成")
        else:
            click.echo(f"❌ black 格式化失败: {result.stderr}")

        # 运行 isort
        click.echo("📋 运行 isort...")
        result = subprocess.run(
            ['isort', str(project_path)], capture_output=True, text=True
        )

        if result.returncode == 0:
            click.echo("✅ isort 导入排序完成")
        else:
            click.echo(f"❌ isort 导入排序失败: {result.stderr}")

        click.echo("🎉 代码格式化完成！")

    except FileNotFoundError:
        click.echo("❌ 格式化工具未安装，请运行: pip install black isort")
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ 格式化失败: {e}", err=True)
        raise click.Abort()


@quality_group.command()
@click.option('--path', '-p', default='.', help='项目路径')
@click.option(
    '--output', '-o', default='coverage-report.html', help='覆盖率报告输出文件'
)
def coverage(path: str, output: str) -> None:
    """生成测试覆盖率报告"""
    click.echo(f"📊 生成覆盖率报告: {path}")

    try:
        project_path = Path(path)

        # 运行 pytest 与覆盖率
        click.echo("🧪 运行测试并收集覆盖率...")
        result = subprocess.run(
            [
                'pytest',
                '--cov=.',
                f'--cov-report=html:{output}',
                '--cov-report=term',
                str(project_path),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            click.echo("✅ 覆盖率报告生成成功")
            click.echo(f"📁 HTML报告: {output}")
            click.echo("\n📊 覆盖率摘要:")
            click.echo(result.stdout)
        else:
            click.echo(f"❌ 覆盖率报告生成失败: {result.stderr}")

    except FileNotFoundError:
        click.echo("❌ pytest-cov 未安装，请运行: pip install pytest-cov")
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ 生成覆盖率报告失败: {e}", err=True)
        raise click.Abort()


@quality_group.command()
@click.option('--path', '-p', default='.', help='项目路径')
def metrics(path: str) -> None:
    """显示代码质量指标"""
    click.echo(f"📊 代码质量指标: {path}")

    try:
        project_path = Path(path)

        # 统计文件数量
        python_files = list(project_path.rglob("*.py"))
        test_files = [f for f in python_files if 'test' in str(f).lower()]

        click.echo(f"📄 Python 文件数: {len(python_files)}")
        click.echo(f"🧪 测试文件数: {len(test_files)}")

        if python_files:
            test_ratio = len(test_files) / len(python_files)
            click.echo(f"📊 测试文件比例: {test_ratio:.1%}")

        # 统计代码行数
        total_lines = 0
        total_blank_lines = 0
        total_comment_lines = 0

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    total_lines += len(lines)

                    for line in lines:
                        stripped = line.strip()
                        if not stripped:
                            total_blank_lines += 1
                        elif stripped.startswith('#'):
                            total_comment_lines += 1
            except UnicodeDecodeError:
                continue

        code_lines = total_lines - total_blank_lines - total_comment_lines

        click.echo(f"📏 总行数: {total_lines}")
        click.echo(f"📝 代码行数: {code_lines}")
        click.echo(f"💬 注释行数: {total_comment_lines}")
        click.echo(f"⬜ 空行数: {total_blank_lines}")

        if total_lines > 0:
            comment_ratio = total_comment_lines / total_lines
            click.echo(f"📊 注释比例: {comment_ratio:.1%}")

        # 平均文件大小
        if python_files:
            avg_file_size = code_lines / len(python_files)
            click.echo(f"📊 平均文件大小: {avg_file_size:.1f} 行")

    except Exception as e:
        click.echo(f"❌ 获取指标失败: {e}", err=True)
        raise click.Abort()


def _auto_fix_issues(project_path: Path) -> None:
    """自动修复代码问题"""
    try:
        # 运行 autopep8
        click.echo("🔧 运行 autopep8...")
        result = subprocess.run(
            ['autopep8', '--in-place', '--recursive', str(project_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            click.echo("✅ autopep8 修复完成")
        else:
            click.echo(f"⚠️  autopep8 修复失败: {result.stderr}")

    except FileNotFoundError:
        click.echo("⚠️  autopep8 未安装，跳过自动修复")


def _show_quality_summary(results: dict) -> None:
    """显示质量检查总结"""
    click.echo("\n📊 质量检查总结:")

    passed = 0
    total = len(results)

    for tool_name, result in results.items():
        status = "✅ 通过" if result.get('success', False) else "❌ 失败"
        click.echo(f"  {tool_name:<10} - {status}")

        if result.get('success', False):
            passed += 1

    click.echo(f"\n📈 总体通过率: {passed}/{total} ({passed/max(total, 1):.1%})")

    if passed == total:
        click.echo("🎉 所有检查都通过了！")
    else:
        click.echo("💡 建议修复失败的检查项")
        click.echo("   使用 --fix 选项尝试自动修复")
