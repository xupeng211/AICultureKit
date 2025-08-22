#!/usr/bin/env python3
"""
文化深度渗透设置脚本
自动配置文化渗透系统，确保开发文化在项目中彻底执行
"""

import json
import os
from pathlib import Path


def setup_git_hooks(project_path: Path) -> None:
    """设置Git钩子以强制执行文化检查"""
    hooks_dir = project_path / ".git" / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    # Pre-commit钩子
    pre_commit_hook = hooks_dir / "pre-commit"
    pre_commit_content = """#!/bin/bash
# AICultureKit Pre-commit Hook
echo "🔍 执行文化检查..."

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 执行文化检查
PYTHONPATH=. python -c "
from aiculture.culture_penetration_system import AIDevCultureAssistant
from pathlib import Path
import sys

assistant = AIDevCultureAssistant(Path('.'))
can_commit = assistant.check_before_commit()

if not can_commit:
    print('❌ 提交被阻止：文化检查未通过')
    print('💡 请修复违规后重新提交')
    sys.exit(1)
else:
    print('✅ 文化检查通过，允许提交')
    sys.exit(0)
"

exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "❌ 提交被阻止：请修复文化违规"
    exit 1
fi

echo "✅ 文化检查通过"
"""

    with open(pre_commit_hook, "w") as f:
        f.write(pre_commit_content)

    # 设置执行权限
    os.chmod(pre_commit_hook, 0o755)
    print(f"✅ 已设置 pre-commit 钩子: {pre_commit_hook}")

    # Pre-push钩子
    pre_push_hook = hooks_dir / "pre-push"
    pre_push_content = """#!/bin/bash
# AICultureKit Pre-push Hook
echo "🔍 执行推送前文化检查..."

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 执行完整的文化检查
PYTHONPATH=. python -c "
from aiculture.culture_enforcer import CultureEnforcer
import sys

enforcer = CultureEnforcer('.')
result = enforcer.enforce_all()

print(f'📊 文化质量评分: {result[\"score\"]}/100')
print(f'❌ 错误: {result[\"errors\"]} 个')
print(f'⚠️  警告: {result[\"warnings\"]} 个')

# 如果有阻塞性错误，阻止推送
if result['errors'] > 0:
    print('❌ 推送被阻止：存在阻塞性错误')
    sys.exit(1)

# 如果质量评分过低，警告但不阻止
if result['score'] < 70:
    print('⚠️  警告：文化质量评分较低，建议改进')

print('✅ 推送检查通过')
"
"""

    with open(pre_push_hook, "w") as f:
        f.write(pre_push_content)

    os.chmod(pre_push_hook, 0o755)
    print(f"✅ 已设置 pre-push 钩子: {pre_push_hook}")


def setup_vscode_integration(project_path: Path) -> None:
    """设置VSCode集成"""
    vscode_dir = project_path / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    # 设置任务
    tasks_json = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "文化检查",
                "type": "shell",
                "command": "python",
                "args": [
                    "-c",
                    "from aiculture.culture_enforcer import CultureEnforcer; result = CultureEnforcer('.').enforce_all(); print(f'质量评分: {result[\"score\"]}/100')",
                ],
                "group": "test",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "启动文化监控",
                "type": "shell",
                "command": "python",
                "args": [
                    "-c",
                    "from aiculture.culture_penetration_system import AIDevCultureAssistant; from pathlib import Path; assistant = AIDevCultureAssistant(Path('.')); assistant.start_assistance(); input('按Enter停止监控...'); assistant.stop_assistance()",
                ],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": True,
                    "panel": "dedicated",
                },
            },
        ],
    }

    with open(vscode_dir / "tasks.json", "w") as f:
        json.dump(tasks_json, f, indent=2)

    # 设置设置
    settings_json = {
        "python.defaultInterpreterPath": "./venv/bin/python",
        "python.linting.enabled": True,
        "python.linting.flake8Enabled": True,
        "python.formatting.provider": "black",
        "editor.formatOnSave": True,
        "files.associations": {"*.aiculture": "json"},
        "python.testing.pytestEnabled": True,
        "python.testing.pytestArgs": ["--cov=aiculture", "--cov-report=html"],
    }

    with open(vscode_dir / "settings.json", "w") as f:
        json.dump(settings_json, f, indent=2)

    print(f"✅ 已设置 VSCode 集成: {vscode_dir}")


def setup_github_actions(project_path: Path) -> None:
    """设置GitHub Actions工作流"""
    workflows_dir = project_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    culture_check_workflow = {
        "name": "文化检查",
        "on": {
            "push": {"branches": ["main", "develop"]},
            "pull_request": {"branches": ["main", "develop"]},
        },
        "jobs": {
            "culture-check": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"uses": "actions/checkout@v3"},
                    {
                        "name": "设置Python",
                        "uses": "actions/setup-python@v4",
                        "with": {"python-version": "3.11"},
                    },
                    {"name": "安装依赖", "run": "pip install -r requirements.txt"},
                    {
                        "name": "执行文化检查",
                        "run": "PYTHONPATH=. python -c \"from aiculture.culture_enforcer import CultureEnforcer; result = CultureEnforcer('.').enforce_all(); print(f'质量评分: {result[\\\"score\\\"]}/100'); exit(1 if result['errors'] > 0 else 0)\"",
                    },
                    {
                        "name": "运行测试",
                        "run": "python -m pytest --cov=aiculture --cov-report=xml",
                    },
                    {
                        "name": "上传覆盖率报告",
                        "uses": "codecov/codecov-action@v3",
                        "with": {"file": "./coverage.xml"},
                    },
                ],
            }
        },
    }

    import yaml

    with open(workflows_dir / "culture-check.yml", "w") as f:
        yaml.dump(culture_check_workflow, f, default_flow_style=False)

    print(f"✅ 已设置 GitHub Actions: {workflows_dir / 'culture-check.yml'}")


def setup_culture_config(project_path: Path) -> None:
    """设置文化配置文件"""
    config_dir = project_path / ".aiculture"
    config_dir.mkdir(exist_ok=True)

    # 文化渗透配置
    penetration_config = {
        "real_time_monitoring": {
            "enabled": True,
            "interval": 5,
            "monitored_extensions": [
                ".py",
                ".js",
                ".ts",
                ".jsx",
                ".tsx",
                ".html",
                ".css",
            ],
            "excluded_paths": ["venv", "__pycache__", "node_modules", ".git"],
        },
        "quality_gates": {
            "commit_gate": {
                "enabled": True,
                "blocking_rules": ["security", "syntax_error"],
                "critical_threshold": 0,
                "warning_threshold": 5,
            },
            "merge_gate": {
                "enabled": True,
                "blocking_rules": ["security", "testing", "documentation"],
                "critical_threshold": 0,
                "warning_threshold": 3,
            },
            "release_gate": {
                "enabled": True,
                "blocking_rules": [
                    "security",
                    "testing",
                    "documentation",
                    "performance",
                ],
                "critical_threshold": 0,
                "warning_threshold": 0,
            },
        },
        "auto_fix": {
            "enabled": True,
            "safe_fixes_only": True,
            "backup_before_fix": True,
        },
        "notifications": {"console": True, "file": True, "webhook": False},
    }

    with open(config_dir / "penetration_config.json", "w") as f:
        json.dump(penetration_config, f, indent=2, ensure_ascii=False)

    print(f"✅ 已设置文化渗透配置: {config_dir / 'penetration_config.json'}")


def setup_culture_dashboard(project_path: Path) -> None:
    """设置文化仪表板"""
    dashboard_dir = project_path / ".aiculture" / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)

    # 创建简单的HTML仪表板
    dashboard_html = """<!DOCTYPE html>
<html>
<head>
    <title>AICultureKit 文化仪表板</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { display: inline-block; margin: 10px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .score { font-size: 2em; font-weight: bold; }
        .good { color: green; }
        .warning { color: orange; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>🏆 AICultureKit 文化仪表板</h1>

    <div class="metric">
        <h3>📊 质量评分</h3>
        <div class="score" id="quality-score">--</div>
    </div>

    <div class="metric">
        <h3>🧪 测试覆盖率</h3>
        <div class="score" id="test-coverage">--</div>
    </div>

    <div class="metric">
        <h3>🔒 安全问题</h3>
        <div class="score" id="security-issues">--</div>
    </div>

    <div class="metric">
        <h3>📝 文档完整性</h3>
        <div class="score" id="doc-completeness">--</div>
    </div>

    <script>
        // 这里可以添加JavaScript来动态更新指标
        // 实际项目中可以通过API获取实时数据

        function updateMetrics() {
            // 模拟数据更新
            document.getElementById('quality-score').textContent = '85/100';
            document.getElementById('test-coverage').textContent = '24%';
            document.getElementById('security-issues').textContent = '3';
            document.getElementById('doc-completeness').textContent = '78%';
        }

        // 页面加载时更新一次
        updateMetrics();

        // 每30秒更新一次
        setInterval(updateMetrics, 30000);
    </script>
</body>
</html>"""

    with open(dashboard_dir / "index.html", "w") as f:
        f.write(dashboard_html)

    print(f"✅ 已设置文化仪表板: {dashboard_dir / 'index.html'}")


def main():
    """主函数"""
    project_path = Path(".")

    print("🚀 开始设置文化深度渗透系统")
    print("=" * 60)

    try:
        # 1. 设置Git钩子
        print("\n1. 设置Git钩子...")
        setup_git_hooks(project_path)

        # 2. 设置VSCode集成
        print("\n2. 设置VSCode集成...")
        setup_vscode_integration(project_path)

        # 3. 设置GitHub Actions
        print("\n3. 设置GitHub Actions...")
        setup_github_actions(project_path)

        # 4. 设置文化配置
        print("\n4. 设置文化配置...")
        setup_culture_config(project_path)

        # 5. 设置文化仪表板
        print("\n5. 设置文化仪表板...")
        setup_culture_dashboard(project_path)

        print("\n" + "=" * 60)
        print("🎉 文化深度渗透系统设置完成！")
        print("\n📋 已配置的功能:")
        print("   ✅ Git钩子 - 提交和推送时自动检查")
        print("   ✅ VSCode集成 - 编辑器内文化检查")
        print("   ✅ GitHub Actions - CI/CD文化检查")
        print("   ✅ 实时监控 - 文件变更时自动检查")
        print("   ✅ 质量门禁 - 强制性文化标准")
        print("   ✅ 文化仪表板 - 可视化文化指标")

        print("\n🚀 立即启用:")
        print(
            "   1. 启动实时监控: python -c \"from aiculture.culture_penetration_system import AIDevCultureAssistant; from pathlib import Path; assistant = AIDevCultureAssistant(Path('.')); assistant.start_assistance()\""
        )
        print("   2. 查看仪表板: open .aiculture/dashboard/index.html")
        print('   3. 测试Git钩子: git add . && git commit -m "test culture check"')

        print("\n💡 现在你的项目将自动执行文化检查，确保开发文化彻底渗透！")

    except Exception as e:
        print(f"❌ 设置过程中出现错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
