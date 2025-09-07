#!/usr/bin/env python3
"""
🚀 Python项目生成器

基于AICultureKit模板生成新的Python项目。

使用方法:
    python generate_project.py --name MyProject --description "我的项目描述"
"""

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Dict


class ProjectGenerator:
    """项目生成器类"""

    def __init__(self, template_dir: str):
        self.template_dir = Path(template_dir)
        self.config = self._load_template_config()

    def _load_template_config(self) -> Dict:
        """加载模板配置"""
        config_file = self.template_dir / "template_config.json"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def generate_project(self, project_name: str, output_dir: str, **kwargs):
        """生成新项目"""
        print(f"🚀 开始生成项目: {project_name}")

        variables = self._prepare_variables(project_name, **kwargs)
        project_path = Path(output_dir) / project_name
        project_path.mkdir(parents=True, exist_ok=True)

        self._copy_template_files(project_path, variables)
        self._initialize_git(project_path)
        self._generate_requirements(project_path)

        print(f"✅ 项目生成完成: {project_path}")
        print("\n📚 接下来的步骤:")
        print(f"   cd {project_name}")
        print("   make install    # 安装依赖")
        print("   make env-check  # 检查环境")
        print("   make test       # 运行测试")

    def _prepare_variables(self, project_name: str, **kwargs) -> Dict[str, str]:
        """准备变量替换字典"""
        return {
            "{{PROJECT_NAME}}": project_name,
            "{{PROJECT_NAME_LOWER}}": project_name.lower().replace("-", "_"),
            "{{PROJECT_DESCRIPTION}}": kwargs.get("description")
            or f"{project_name} - Python项目",
            "{{AUTHOR_NAME}}": kwargs.get("author") or "Your Name",
            "{{AUTHOR_EMAIL}}": kwargs.get("email") or "your.email@example.com",
            "{{GITHUB_USERNAME}}": kwargs.get("github_user") or "yourusername",
            "{{PYTHON_VERSION}}": kwargs.get("python_version") or "3.11",
        }

    def _copy_template_files(self, project_path: Path, variables: Dict[str, str]):
        """复制并处理模板文件"""
        template_files = self.config.get("template_files", [])

        for root, dirs, files in os.walk(self.template_dir):
            # 跳过配置文件和生成器脚本
            files = [
                f
                for f in files
                if f not in ["template_config.json", "generate_project.py"]
            ]

            for file in files:
                source_path = Path(root) / file
                rel_path = source_path.relative_to(self.template_dir)

                # 替换路径中的变量
                target_rel_path = str(rel_path)
                for var, value in variables.items():
                    target_rel_path = target_rel_path.replace(var, value)

                target_path = project_path / target_rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # 处理文件内容
                if str(rel_path) in template_files:
                    # 变量替换文件
                    with open(source_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    for var, value in variables.items():
                        content = content.replace(var, value)

                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write(content)
                else:
                    # 直接复制文件
                    shutil.copy2(source_path, target_path)

    def _initialize_git(self, project_path: Path):
        """初始化Git仓库"""
        try:
            import subprocess

            subprocess.run(
                ["git", "init"], cwd=project_path, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "add", "."], cwd=project_path, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit from template"],
                cwd=project_path,
                check=True,
                capture_output=True,
            )
            print("  ✅ Git仓库初始化完成")
        except Exception as e:
            print(f"  ⚠️ Git初始化失败: {e}")

    def _generate_requirements(self, project_path: Path):
        """生成基础requirements.txt"""
        basic_requirements = [
            "# 基础依赖",
            "requests>=2.31.0",
            "click>=8.1.0",
            "pydantic>=2.0.0",
            "",
            "# 开发依赖请参考 requirements-dev.txt",
        ]

        with open(project_path / "requirements.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(basic_requirements))


def main():
    parser = argparse.ArgumentParser(description="Python项目生成器")
    parser.add_argument("--name", required=True, help="项目名称")
    parser.add_argument("--output", default=".", help="输出目录")
    parser.add_argument("--description", help="项目描述")
    parser.add_argument("--author", help="作者姓名")
    parser.add_argument("--email", help="作者邮箱")
    parser.add_argument("--github-user", help="GitHub用户名")
    parser.add_argument("--python-version", default="3.11", help="Python版本")

    args = parser.parse_args()

    template_dir = Path(__file__).parent
    generator = ProjectGenerator(template_dir)
    generator.generate_project(
        project_name=args.name,
        output_dir=args.output,
        description=args.description,
        author=args.author,
        email=args.email,
        github_user=args.github_user,
        python_version=args.python_version,
    )


if __name__ == "__main__":
    main()
