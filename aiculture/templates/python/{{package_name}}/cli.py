"""
命令行接口模块

遵循Click最佳实践和AICultureKit开发文化标准
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from . import __version__
from .core import AppConfig, create_app

# 设置Rich控制台
console = Console()


def setup_logging(verbose: bool = False) -> None:
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@click.group()
@click.version_option(version=__version__, prog_name="{{project_name}}")
@click.option('--verbose', '-v', is_flag=True, help='启用详细输出')
@click.option('--config-file', type=click.Path(exists=True), help='配置文件路径')
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config_file: Optional[str]) -> None:
    """
    {{project_name}} - {{project_description}}

    基于AICultureKit最佳实践构建的命令行工具
    """
    # 确保context对象存在
    ctx.ensure_object(dict)

    # 设置日志
    setup_logging(verbose)

    # 存储全局配置
    ctx.obj['verbose'] = verbose
    ctx.obj['config_file'] = config_file

    logger = logging.getLogger(__name__)
    logger.debug(f"启动 {{project_name}} v{__version__}")


@cli.command()
@click.option(
    '--environment',
    '-e',
    type=click.Choice(['development', 'staging', 'production']),
    default='development',
    help='运行环境',
)
@click.option('--host', default='localhost', help='服务器地址')
@click.option('--port', default=8000, type=int, help='端口号')
@click.pass_context
def run(ctx: click.Context, environment: str, host: str, port: int) -> None:
    """启动应用程序"""
    logger = logging.getLogger(__name__)

    try:
        # 创建配置
        config = AppConfig(environment=environment, api_host=host, api_port=port)

        console.print(f"🚀 启动 {{project_name}}", style="bold green")
        console.print(f"环境: {environment}")
        console.print(f"地址: http://{host}:{port}")

        # 创建应用程序
        app = create_app(config)

        # 运行应用程序
        success = app.run()

        if success:
            console.print("✅ 应用程序运行成功", style="bold green")
        else:
            console.print("❌ 应用程序运行失败", style="bold red")
            sys.exit(1)

    except Exception as e:
        logger.error(f"启动失败: {e}")
        console.print(f"❌ 启动失败: {e}", style="bold red")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option('--name', prompt='用户名', help='用户名')
@click.option('--email', prompt='邮箱', help='用户邮箱')
@click.option('--age', type=int, help='用户年龄')
@click.pass_context
def create_user(ctx: click.Context, name: str, email: str, age: Optional[int]) -> None:
    """创建新用户"""
    logger = logging.getLogger(__name__)

    try:
        # 创建应用程序
        app = create_app()

        # 准备用户数据
        user_data = {'name': name, 'email': email}

        if age is not None:
            user_data['age'] = age

        console.print(f"📝 创建用户: {name} ({email})")

        # 创建用户
        result = app.user_service.process(user_data)

        if result['success']:
            console.print("✅ 用户创建成功", style="bold green")
            console.print(f"用户ID: {result['user_id']}")
        else:
            console.print(f"❌ 用户创建失败: {result['message']}", style="bold red")
            sys.exit(1)

    except Exception as e:
        logger.error(f"创建用户失败: {e}")
        console.print(f"❌ 创建用户失败: {e}", style="bold red")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('user_id')
@click.pass_context
def get_user(ctx: click.Context, user_id: str) -> None:
    """获取用户信息"""
    logger = logging.getLogger(__name__)

    try:
        # 创建应用程序
        app = create_app()

        console.print(f"🔍 查找用户: {user_id}")

        # 获取用户
        user_data = app.user_service.get_user(user_id)

        if user_data:
            # 创建用户信息表格
            table = Table(title=f"用户信息: {user_id}")
            table.add_column("字段", style="cyan", no_wrap=True)
            table.add_column("值", style="magenta")

            for key, value in user_data.items():
                table.add_row(key, str(value))

            console.print(table)
        else:
            console.print(f"❌ 用户不存在: {user_id}", style="bold red")
            sys.exit(1)

    except Exception as e:
        logger.error(f"获取用户失败: {e}")
        console.print(f"❌ 获取用户失败: {e}", style="bold red")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """显示应用程序状态"""
    try:
        # 创建应用程序
        app = create_app()

        # 创建状态表格
        table = Table(title="应用程序状态")
        table.add_column("项目", style="cyan", no_wrap=True)
        table.add_column("值", style="magenta")

        table.add_row("应用名称", app.config.app_name)
        table.add_row("版本", app.config.version)
        table.add_row("环境", app.config.environment)
        table.add_row("调试模式", "是" if app.config.debug else "否")
        table.add_row("日志级别", app.config.log_level)
        table.add_row("API地址", f"{app.config.api_host}:{app.config.api_port}")

        console.print(table)

        # 检查数据目录
        data_dir = Path("data") / app.config.environment
        if data_dir.exists():
            user_files = list(data_dir.glob("*.yaml"))
            console.print(f"\n📁 数据目录: {data_dir}")
            console.print(f"用户数量: {len(user_files)}")
        else:
            console.print(f"\n📁 数据目录: {data_dir} (不存在)")

    except Exception as e:
        console.print(f"❌ 获取状态失败: {e}", style="bold red")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.confirmation_option(prompt='确定要初始化项目吗？这将创建必要的目录和配置文件。')
@click.pass_context
def init(ctx: click.Context) -> None:
    """初始化项目"""
    logger = logging.getLogger(__name__)

    try:
        console.print("🏗️ 初始化项目...", style="bold blue")

        # 创建必要的目录
        directories = [
            Path("data/development"),
            Path("data/staging"),
            Path("data/production"),
            Path("logs"),
            Path("config"),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            console.print(f"✅ 创建目录: {directory}")

        # 创建配置文件
        config_file = Path(".env")
        if not config_file.exists():
            with open(config_file, 'w') as f:
                f.write(
                    """# {{project_name}} 环境配置
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# API配置
API_HOST=localhost
API_PORT=8000

# 安全配置 (生产环境必须修改)
SECRET_KEY=your-secret-key-here

# 数据库配置 (如果需要)
# DATABASE_URL=postgresql://user:password@localhost/dbname

# 其他配置
# REDIS_URL=redis://localhost:6379/0
"""
                )
            console.print(f"✅ 创建配置文件: {config_file}")
        else:
            console.print(f"⚠️  配置文件已存在: {config_file}")

        console.print("🎉 项目初始化完成！", style="bold green")
        console.print("💡 提示: 请编辑 .env 文件设置您的配置")

    except Exception as e:
        logger.error(f"初始化失败: {e}")
        console.print(f"❌ 初始化失败: {e}", style="bold red")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


def main() -> None:
    """主入口函数"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n👋 用户中断，程序退出", style="yellow")
        sys.exit(0)
    except Exception as e:
        console.print(f"❌ 未处理的错误: {e}", style="bold red")
        sys.exit(1)


if __name__ == '__main__':
    main()
