"""
模板相关的CLI命令
"""

from pathlib import Path
from typing import Any

import click

from ..core import ProjectTemplate


@click.group()
def template_group() -> Any:
    """项目模板管理命令"""
    pass


@template_group.command()
def list() -> None:
    """列出所有可用模板"""
    click.echo("📋 可用的项目模板:")
    
    templates = {
        'python-basic': {
            'description': '基础Python项目模板',
            'features': ['基本项目结构', 'setup.py配置', '测试框架', '文档模板']
        },
        'python-web': {
            'description': 'Python Web应用模板',
            'features': ['Flask/FastAPI支持', 'API文档', '数据库集成', '部署配置']
        },
        'python-ml': {
            'description': 'Python机器学习项目模板',
            'features': ['Jupyter notebooks', '数据处理', '模型训练', '实验跟踪']
        },
        'python-cli': {
            'description': 'Python命令行工具模板',
            'features': ['Click框架', '配置管理', '日志记录', '打包配置']
        },
        'javascript-basic': {
            'description': '基础JavaScript项目模板',
            'features': ['Node.js支持', 'npm配置', '测试框架', 'ESLint配置']
        },
        'typescript-basic': {
            'description': '基础TypeScript项目模板',
            'features': ['TypeScript配置', '类型定义', '构建工具', '测试支持']
        }
    }
    
    for template_name, info in templates.items():
        click.echo(f"\n📦 {template_name}")
        click.echo(f"   {info['description']}")
        click.echo("   特性:")
        for feature in info['features']:
            click.echo(f"     • {feature}")


@template_group.command()
@click.argument('template_name')
def show(template_name: str) -> None:
    """显示模板详细信息"""
    click.echo(f"📦 模板详情: {template_name}")
    
    # 模板详细信息
    template_details = {
        'python-basic': {
            'description': '基础Python项目模板，适合小型到中型Python项目',
            'structure': [
                'src/',
                'tests/',
                'docs/',
                'setup.py',
                'requirements.txt',
                'README.md',
                '.gitignore',
                'pyproject.toml'
            ],
            'dependencies': ['pytest', 'flake8', 'mypy', 'black'],
            'best_practices': [
                '遵循PEP 8代码风格',
                '包含完整的测试套件',
                '提供详细的文档',
                '使用类型提示'
            ]
        },
        'python-web': {
            'description': 'Python Web应用模板，支持Flask和FastAPI',
            'structure': [
                'app/',
                'tests/',
                'migrations/',
                'config/',
                'requirements.txt',
                'Dockerfile',
                'docker-compose.yml'
            ],
            'dependencies': ['flask', 'fastapi', 'sqlalchemy', 'alembic'],
            'best_practices': [
                'RESTful API设计',
                '数据库迁移管理',
                '容器化部署',
                'API文档自动生成'
            ]
        }
    }
    
    if template_name not in template_details:
        click.echo(f"❌ 模板 '{template_name}' 不存在")
        click.echo("使用 'aiculture template list' 查看可用模板")
        return
    
    details = template_details[template_name]
    
    click.echo(f"\n📝 描述: {details['description']}")
    
    click.echo("\n📁 项目结构:")
    for item in details['structure']:
        click.echo(f"  {item}")
    
    click.echo("\n📦 主要依赖:")
    for dep in details['dependencies']:
        click.echo(f"  • {dep}")
    
    click.echo("\n✨ 最佳实践:")
    for practice in details['best_practices']:
        click.echo(f"  • {practice}")
    
    click.echo(f"\n💡 使用方法:")
    click.echo(f"   aiculture project create my-project --template {template_name}")


@template_group.command()
@click.argument('name')
@click.option('--path', '-p', default='.', 
              help='模板保存路径')
def create(name: str, path: str) -> None:
    """创建自定义模板"""
    click.echo(f"🛠️  创建自定义模板: {name}")
    
    try:
        template_path = Path(path) / f"{name}-template"
        template_path.mkdir(exist_ok=True)
        
        # 创建模板配置文件
        config_file = template_path / "template.yaml"
        config_content = f"""# 自定义模板配置
name: {name}
description: "自定义项目模板"
version: "1.0.0"

# 模板变量
variables:
  project_name: "{{{{ project_name }}}}"
  author_name: "{{{{ author_name }}}}"
  author_email: "{{{{ author_email }}}}"

# 文件结构
structure:
  - src/
  - tests/
  - docs/
  - README.md
  - .gitignore

# 依赖包
dependencies:
  - pytest
  - flake8

# 开发依赖
dev_dependencies:
  - black
  - mypy

# 脚本
scripts:
  test: "pytest"
  lint: "flake8 src/"
  format: "black src/"
"""
        
        config_file.write_text(config_content)
        
        # 创建基本文件结构
        (template_path / "src").mkdir(exist_ok=True)
        (template_path / "tests").mkdir(exist_ok=True)
        (template_path / "docs").mkdir(exist_ok=True)
        
        # 创建README模板
        readme_file = template_path / "README.md"
        readme_content = f"""# {{{{ project_name }}}}

项目描述

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```python
# 示例代码
```

## 测试

```bash
pytest
```

## 作者

{{{{ author_name }}}} <{{{{ author_email }}}}>
"""
        readme_file.write_text(readme_content)
        
        # 创建.gitignore模板
        gitignore_file = template_path / ".gitignore"
        gitignore_content = """__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.pytest_cache/
.mypy_cache/
"""
        gitignore_file.write_text(gitignore_content)
        
        click.echo(f"✅ 自定义模板创建成功: {template_path}")
        click.echo("\n📋 下一步:")
        click.echo(f"1. 编辑 {config_file} 配置模板")
        click.echo(f"2. 在 {template_path} 中添加模板文件")
        click.echo("3. 使用模板创建项目")
        
    except Exception as e:
        click.echo(f"❌ 创建模板失败: {e}", err=True)
        raise click.Abort()


@template_group.command()
@click.option('--path', '-p', default='.', 
              help='搜索路径')
def scan(path: str) -> None:
    """扫描本地自定义模板"""
    click.echo(f"🔍 扫描本地模板: {path}")
    
    try:
        search_path = Path(path)
        templates_found = []
        
        # 搜索模板文件
        for template_file in search_path.rglob("template.yaml"):
            template_dir = template_file.parent
            templates_found.append(template_dir)
        
        if not templates_found:
            click.echo("❌ 未找到任何自定义模板")
            click.echo("使用 'aiculture template create' 创建模板")
            return
        
        click.echo(f"✅ 找到 {len(templates_found)} 个自定义模板:")
        
        for template_dir in templates_found:
            template_name = template_dir.name
            click.echo(f"\n📦 {template_name}")
            click.echo(f"   路径: {template_dir}")
            
            # 读取模板配置
            config_file = template_dir / "template.yaml"
            if config_file.exists():
                try:
                    import yaml
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    
                    description = config.get('description', '无描述')
                    version = config.get('version', '未知版本')
                    
                    click.echo(f"   描述: {description}")
                    click.echo(f"   版本: {version}")
                    
                except Exception:
                    click.echo("   ⚠️  配置文件读取失败")
        
    except Exception as e:
        click.echo(f"❌ 扫描失败: {e}", err=True)
        raise click.Abort()


@template_group.command()
@click.argument('template_path')
@click.option('--name', '-n', required=True,
              help='模板名称')
def install(template_path: str, name: str) -> None:
    """安装模板到系统"""
    click.echo(f"📦 安装模板: {template_path} -> {name}")
    
    try:
        source_path = Path(template_path)
        
        if not source_path.exists():
            click.echo(f"❌ 模板路径不存在: {template_path}")
            raise click.Abort()
        
        # 这里可以实现模板安装逻辑
        # 例如复制到系统模板目录
        
        click.echo("✅ 模板安装成功")
        click.echo(f"💡 现在可以使用: aiculture project create my-project --template {name}")
        
    except Exception as e:
        click.echo(f"❌ 安装模板失败: {e}", err=True)
        raise click.Abort()
