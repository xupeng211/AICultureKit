"""
项目上下文生成器

自动分析项目结构、代码风格、依赖关系，生成适合AI理解的项目摘要。
解决痛点：给AI传递项目信息很繁琐
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess
import ast


@dataclass
class ProjectContext:
    """项目上下文数据结构"""
    name: str
    description: str
    structure: Dict[str, Any]
    technologies: List[str]
    coding_style: Dict[str, Any]
    key_files: List[str]
    dependencies: List[str]
    recent_changes: List[str]
    ai_instructions: str


class ProjectContextGenerator:
    """
    智能项目上下文生成器
    
    为AI协作自动生成项目摘要，包括：
    - 项目结构和关键文件
    - 编码风格和约定
    - 技术栈和依赖
    - 最近的变更记录
    - AI协作指导原则
    """
    
    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.context_cache_file = self.project_path / ".aiculture" / "context.json"
        
    def generate_context(self, include_recent_changes: bool = True) -> ProjectContext:
        """生成完整的项目上下文"""
        
        # 1. 基础项目信息
        project_info = self._analyze_project_basics()
        
        # 2. 项目结构分析
        structure = self._analyze_project_structure()
        
        # 3. 技术栈识别
        technologies = self._detect_technologies()
        
        # 4. 编码风格分析
        coding_style = self._analyze_coding_style()
        
        # 5. 关键文件识别
        key_files = self._identify_key_files()
        
        # 6. 依赖分析
        dependencies = self._analyze_dependencies()
        
        # 7. 最近变更
        recent_changes = []
        if include_recent_changes:
            recent_changes = self._get_recent_changes()
            
        # 8. 生成AI指导
        ai_instructions = self._generate_ai_instructions(
            technologies, coding_style, project_info
        )
        
        return ProjectContext(
            name=project_info.get('name', 'Unknown Project'),
            description=project_info.get('description', ''),
            structure=structure,
            technologies=technologies,
            coding_style=coding_style,
            key_files=key_files,
            dependencies=dependencies,
            recent_changes=recent_changes,
            ai_instructions=ai_instructions
        )
    
    def export_for_ai(self, format: str = 'markdown') -> str:
        """导出适合AI理解的格式"""
        context = self.generate_context()
        
        if format.lower() == 'markdown':
            return self._format_as_markdown(context)
        elif format.lower() == 'json':
            return self._format_as_json(context)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _analyze_project_basics(self) -> Dict[str, str]:
        """分析项目基础信息"""
        info = {}
        
        # 从pyproject.toml读取
        pyproject_file = self.project_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                import tomllib
                with open(pyproject_file, 'rb') as f:
                    data = tomllib.load(f)
                    if 'project' in data:
                        info['name'] = data['project'].get('name', '')
                        info['description'] = data['project'].get('description', '')
            except ImportError:
                # 如果没有tomllib，用简单的文本解析
                content = pyproject_file.read_text(encoding='utf-8')
                for line in content.split('\n'):
                    if line.startswith('name ='):
                        info['name'] = line.split('=')[1].strip().strip('"\'')
                    elif line.startswith('description ='):
                        info['description'] = line.split('=')[1].strip().strip('"\'')
        
        # 从package.json读取
        package_file = self.project_path / "package.json"
        if package_file.exists():
            try:
                with open(package_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    info['name'] = data.get('name', '')
                    info['description'] = data.get('description', '')
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # 从README读取
        readme_files = ['README.md', 'README.rst', 'README.txt', 'readme.md']
        for readme_name in readme_files:
            readme_file = self.project_path / readme_name
            if readme_file.exists():
                try:
                    content = readme_file.read_text(encoding='utf-8')
                    # 提取第一行作为项目名（如果是#标题）
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('# ') and not info.get('name'):
                            info['name'] = line[2:].strip()
                        elif line.strip() and not line.startswith('#') and not info.get('description'):
                            info['description'] = line.strip()
                            break
                except UnicodeDecodeError:
                    continue
                break
        
        return info
    
    def _analyze_project_structure(self) -> Dict[str, Any]:
        """分析项目结构"""
        structure = {
            'type': 'unknown',
            'main_directories': [],
            'config_files': [],
            'test_directories': []
        }
        
        # 识别项目类型
        if (self.project_path / "pyproject.toml").exists() or (self.project_path / "setup.py").exists():
            structure['type'] = 'python'
        elif (self.project_path / "package.json").exists():
            structure['type'] = 'javascript'
        elif (self.project_path / "Cargo.toml").exists():
            structure['type'] = 'rust'
        elif (self.project_path / "go.mod").exists():
            structure['type'] = 'go'
        
        # 扫描主要目录
        for item in self.project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if item.name in ['src', 'lib', 'app', 'core']:
                    structure['main_directories'].append(item.name)
                elif 'test' in item.name.lower():
                    structure['test_directories'].append(item.name)
        
        # 识别配置文件
        config_patterns = [
            '*.toml', '*.yaml', '*.yml', '*.json', '*.ini', '*.cfg',
            'Dockerfile', 'docker-compose.*', '.env*', 'requirements*.txt'
        ]
        
        for pattern in config_patterns:
            for config_file in self.project_path.glob(pattern):
                if config_file.is_file():
                    structure['config_files'].append(config_file.name)
        
        return structure
    
    def _detect_technologies(self) -> List[str]:
        """检测使用的技术栈"""
        technologies = []
        
        # 基于文件检测
        tech_indicators = {
            'Python': ['*.py', 'pyproject.toml', 'requirements.txt', 'setup.py'],
            'JavaScript': ['*.js', 'package.json', '*.jsx'],
            'TypeScript': ['*.ts', '*.tsx', 'tsconfig.json'],
            'React': ['package.json'],  # 需要进一步检查dependencies
            'FastAPI': ['*.py'],  # 需要检查imports
            'Flask': ['*.py'],
            'Django': ['*.py', 'manage.py'],
            'Docker': ['Dockerfile', 'docker-compose.yml'],
            'GitHub Actions': ['.github/workflows/*.yml'],
            'Pytest': ['*.py'],  # 需要检查imports或配置
        }
        
        for tech, patterns in tech_indicators.items():
            for pattern in patterns:
                if list(self.project_path.glob(pattern)):
                    if tech not in technologies:
                        technologies.append(tech)
                    break
        
        # 进一步检查特定技术
        self._detect_specific_technologies(technologies)
        
        return technologies
    
    def _detect_specific_technologies(self, technologies: List[str]) -> None:
        """检测特定技术的使用"""
        
        # 检查Python框架
        if 'Python' in technologies:
            python_files = list(self.project_path.glob('**/*.py'))
            for py_file in python_files[:10]:  # 只检查前10个文件避免过慢
                try:
                    content = py_file.read_text(encoding='utf-8')
                    if 'fastapi' in content.lower() and 'FastAPI' not in technologies:
                        technologies.append('FastAPI')
                    if 'flask' in content.lower() and 'Flask' not in technologies:
                        technologies.append('Flask')
                    if 'django' in content.lower() and 'Django' not in technologies:
                        technologies.append('Django')
                    if 'pytest' in content.lower() and 'Pytest' not in technologies:
                        technologies.append('Pytest')
                except (UnicodeDecodeError, PermissionError):
                    continue
        
        # 检查JavaScript/React
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    if 'react' in deps and 'React' not in technologies:
                        technologies.append('React')
                    if 'vue' in deps and 'Vue' not in technologies:
                        technologies.append('Vue')
                    if 'next' in deps and 'Next.js' not in technologies:
                        technologies.append('Next.js')
            except (json.JSONDecodeError, FileNotFoundError):
                pass
    
    def _analyze_coding_style(self) -> Dict[str, Any]:
        """分析编码风格和约定"""
        style = {
            'language_specific': {},
            'formatting': {},
            'linting': {},
            'testing': {}
        }
        
        # Python风格检测
        if (self.project_path / "pyproject.toml").exists():
            style['formatting']['python'] = self._detect_python_style()
        
        # JavaScript/TypeScript风格检测
        if (self.project_path / "package.json").exists():
            style['formatting']['javascript'] = self._detect_js_style()
        
        # 通用风格检测
        style['linting'] = self._detect_linting_config()
        style['testing'] = self._detect_testing_config()
        
        return style
    
    def _detect_python_style(self) -> Dict[str, Any]:
        """检测Python编码风格"""
        style = {'formatter': 'unknown', 'line_length': 88, 'imports': 'unknown'}
        
        # 检查pyproject.toml中的配置
        pyproject_file = self.project_path / "pyproject.toml"
        if pyproject_file.exists():
            content = pyproject_file.read_text(encoding='utf-8')
            if '[tool.black]' in content:
                style['formatter'] = 'black'
                # 尝试提取line-length
                for line in content.split('\n'):
                    if 'line-length' in line:
                        try:
                            style['line_length'] = int(line.split('=')[1].strip())
                        except (ValueError, IndexError):
                            pass
            elif '[tool.autopep8]' in content:
                style['formatter'] = 'autopep8'
            
            if '[tool.isort]' in content:
                style['imports'] = 'isort'
        
        # 检查其他配置文件
        if (self.project_path / ".flake8").exists():
            style['linter'] = 'flake8'
        if (self.project_path / "setup.cfg").exists():
            style['config_file'] = 'setup.cfg'
        
        return style
    
    def _detect_js_style(self) -> Dict[str, Any]:
        """检测JavaScript/TypeScript编码风格"""
        style = {}
        
        # 检查prettier配置
        prettier_files = ['.prettierrc', '.prettierrc.js', '.prettierrc.json', 'prettier.config.js']
        for prettier_file in prettier_files:
            if (self.project_path / prettier_file).exists():
                style['formatter'] = 'prettier'
                break
        
        # 检查ESLint配置
        eslint_files = ['.eslintrc', '.eslintrc.js', '.eslintrc.json', 'eslint.config.js']
        for eslint_file in eslint_files:
            if (self.project_path / eslint_file).exists():
                style['linter'] = 'eslint'
                break
        
        return style
    
    def _detect_linting_config(self) -> Dict[str, Any]:
        """检测代码检查配置"""
        linting = {}
        
        # pre-commit配置
        if (self.project_path / ".pre-commit-config.yaml").exists():
            linting['pre_commit'] = True
        
        # GitHub Actions
        if (self.project_path / ".github" / "workflows").exists():
            linting['ci_cd'] = 'github_actions'
        
        return linting
    
    def _detect_testing_config(self) -> Dict[str, Any]:
        """检测测试配置"""
        testing = {}
        
        # Python测试
        if (self.project_path / "tests").exists() or list(self.project_path.glob("test_*.py")):
            testing['python'] = 'pytest'  # 假设使用pytest
        
        # JavaScript测试
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    if 'jest' in deps:
                        testing['javascript'] = 'jest'
                    elif 'mocha' in deps:
                        testing['javascript'] = 'mocha'
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return testing
    
    def _identify_key_files(self) -> List[str]:
        """识别项目关键文件"""
        key_files = []
        
        # 必看文件
        important_files = [
            'README.md', 'README.rst', 'CHANGELOG.md', 'CONTRIBUTING.md',
            'pyproject.toml', 'setup.py', 'package.json', 'requirements.txt',
            'Dockerfile', 'docker-compose.yml', '.env.example'
        ]
        
        for file_name in important_files:
            file_path = self.project_path / file_name
            if file_path.exists():
                key_files.append(file_name)
        
        # 主要代码文件（入口点）
        entry_patterns = [
            'main.py', 'app.py', 'server.py', 'index.js', 'index.ts', 
            'app.js', 'app.ts', 'manage.py'
        ]
        
        for pattern in entry_patterns:
            for entry_file in self.project_path.glob(pattern):
                if entry_file.is_file():
                    key_files.append(str(entry_file.relative_to(self.project_path)))
        
        return key_files
    
    def _analyze_dependencies(self) -> List[str]:
        """分析项目依赖"""
        dependencies = []
        
        # Python依赖
        req_files = ['requirements.txt', 'requirements-dev.txt', 'pyproject.toml']
        for req_file in req_files:
            file_path = self.project_path / req_file
            if file_path.exists():
                if req_file.endswith('.txt'):
                    content = file_path.read_text(encoding='utf-8')
                    for line in content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            pkg = line.split('=')[0].split('>')[0].split('<')[0]
                            dependencies.append(pkg)
                elif req_file == 'pyproject.toml':
                    # 简单解析pyproject.toml的dependencies
                    content = file_path.read_text(encoding='utf-8')
                    in_deps = False
                    for line in content.split('\n'):
                        if '[project]' in line or 'dependencies' in line:
                            in_deps = True
                        elif in_deps and line.strip().startswith('"'):
                            dep = line.strip().strip('",')
                            if dep:
                                dependencies.append(dep.split('=')[0].split('>')[0].split('<')[0])
        
        # JavaScript依赖
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    dependencies.extend(list(deps.keys()))
                    dependencies.extend([f"{k} (dev)" for k in dev_deps.keys()])
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return dependencies[:20]  # 限制数量避免过长
    
    def _get_recent_changes(self) -> List[str]:
        """获取最近的代码变更"""
        changes = []
        
        try:
            # 获取最近的git提交
            result = subprocess.run(
                ['git', 'log', '--oneline', '-n', '5'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        changes.append(line.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return changes
    
    def _generate_ai_instructions(self, technologies: List[str], 
                                coding_style: Dict[str, Any], 
                                project_info: Dict[str, str]) -> str:
        """生成AI协作指导原则"""
        
        instructions = []
        
        # 项目特定指导
        instructions.append(f"这是一个{project_info.get('name', '项目')}项目，主要技术栈：{', '.join(technologies[:5])}")
        
        # 编码风格指导
        if 'python' in coding_style.get('formatting', {}):
            py_style = coding_style['formatting']['python']
            formatter = py_style.get('formatter', 'unknown')
            line_length = py_style.get('line_length', 88)
            instructions.append(f"Python代码使用{formatter}格式化，行长度限制{line_length}")
        
        if 'javascript' in coding_style.get('formatting', {}):
            js_style = coding_style['formatting']['javascript']
            if 'formatter' in js_style:
                instructions.append(f"JavaScript代码使用{js_style['formatter']}格式化")
        
        # 质量要求
        instructions.append("代码需要包含适当的注释和文档字符串")
        instructions.append("新功能必须包含对应的测试用例")
        instructions.append("遵循项目现有的代码结构和命名约定")
        
        # 具体的协作指导
        instructions.append("在修改代码前，先理解现有的实现逻辑和设计模式")
        instructions.append("对于重要的代码变更，请先询问是否符合项目架构")
        instructions.append("提供代码时请解释关键的设计决策和实现思路")
        
        return "\n".join(f"- {instruction}" for instruction in instructions)
    
    def _format_as_markdown(self, context: ProjectContext) -> str:
        """格式化为Markdown供AI理解"""
        
        md = f"""# 🤖 {context.name} - AI协作上下文

## 📝 项目概述
{context.description or '暂无描述'}

## 🛠️ 技术栈
{', '.join(context.technologies) if context.technologies else '未检测到'}

## 📁 项目结构
- 项目类型: {context.structure.get('type', 'unknown')}
- 主要目录: {', '.join(context.structure.get('main_directories', [])) or '无'}
- 测试目录: {', '.join(context.structure.get('test_directories', [])) or '无'}
- 配置文件: {', '.join(context.structure.get('config_files', [])) or '无'}

## 📋 关键文件
{chr(10).join(f'- {f}' for f in context.key_files) if context.key_files else '- 无'}

## 📦 主要依赖
{chr(10).join(f'- {dep}' for dep in context.dependencies[:10]) if context.dependencies else '- 无'}

## 🎨 编码风格
### 格式化工具
{json.dumps(context.coding_style.get('formatting', {}), indent=2, ensure_ascii=False)}

### 代码检查
{json.dumps(context.coding_style.get('linting', {}), indent=2, ensure_ascii=False)}

## 📈 最近变更
{chr(10).join(f'- {change}' for change in context.recent_changes[:5]) if context.recent_changes else '- 暂无Git历史'}

## 🤖 AI协作指导原则
{context.ai_instructions}

---
*此上下文由AICultureKit自动生成，建议在与AI协作时参考以上信息*
"""
        return md
    
    def _format_as_json(self, context: ProjectContext) -> str:
        """格式化为JSON格式"""
        return json.dumps({
            'name': context.name,
            'description': context.description,
            'structure': context.structure,
            'technologies': context.technologies,
            'coding_style': context.coding_style,
            'key_files': context.key_files,
            'dependencies': context.dependencies,
            'recent_changes': context.recent_changes,
            'ai_instructions': context.ai_instructions
        }, indent=2, ensure_ascii=False) 