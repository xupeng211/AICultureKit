"""
AI代码一致性检查器

检测AI生成代码是否符合项目的编码风格和约定。
解决痛点：AI生成的代码风格不一致
"""

import ast
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from .context_generator import ProjectContextGenerator


@dataclass
class ConsistencyIssue:
    """一致性问题"""
    file_path: str
    line_number: int
    issue_type: str
    message: str
    suggestion: Optional[str] = None
    auto_fixable: bool = False


@dataclass 
class ConsistencyReport:
    """一致性检查报告"""
    total_files: int
    total_issues: int
    auto_fixable_issues: int
    issues_by_type: Dict[str, int]
    issues: List[ConsistencyIssue]
    project_style: Dict[str, Any]


class AICodeConsistencyChecker:
    """
    AI代码一致性检查器
    
    专门检测AI生成代码的常见问题：
    - 命名约定不一致
    - 导入顺序混乱  
    - 文档字符串格式不统一
    - 代码风格偏离项目规范
    - 类型注解缺失或不规范
    """
    
    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.context_generator = ProjectContextGenerator(project_path)
        self.project_context = self.context_generator.generate_context()
        
    def check_files(self, file_paths: List[Path], auto_fix: bool = False) -> ConsistencyReport:
        """检查多个文件的一致性"""
        all_issues = []
        issues_by_type = {}
        
        for file_path in file_paths:
            if file_path.suffix == '.py':
                issues = self._check_python_file(file_path)
                all_issues.extend(issues)
                
                # 统计问题类型
                for issue in issues:
                    issues_by_type[issue.issue_type] = issues_by_type.get(issue.issue_type, 0) + 1
                    
                # 自动修复
                if auto_fix:
                    self._auto_fix_file(file_path, issues)
        
        auto_fixable_count = sum(1 for issue in all_issues if issue.auto_fixable)
        
        return ConsistencyReport(
            total_files=len(file_paths),
            total_issues=len(all_issues),
            auto_fixable_issues=auto_fixable_count,
            issues_by_type=issues_by_type,
            issues=all_issues,
            project_style=self.project_context.coding_style
        )
    
    def _check_python_file(self, file_path: Path) -> List[ConsistencyIssue]:
        """检查Python文件的一致性"""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # 各种检查
            issues.extend(self._check_naming_conventions(file_path, tree, content))
            issues.extend(self._check_import_order(file_path, content))
            issues.extend(self._check_docstring_format(file_path, tree))
            issues.extend(self._check_type_annotations(file_path, tree))
            issues.extend(self._check_line_length(file_path, content))
            issues.extend(self._check_code_formatting(file_path, content))
            
        except SyntaxError as e:
            issues.append(ConsistencyIssue(
                file_path=str(file_path),
                line_number=e.lineno or 1,
                issue_type="syntax_error",
                message=f"语法错误: {e.msg}",
                auto_fixable=False
            ))
        except Exception as e:
            issues.append(ConsistencyIssue(
                file_path=str(file_path),
                line_number=1,
                issue_type="parse_error", 
                message=f"文件解析失败: {e}",
                auto_fixable=False
            ))
            
        return issues
    
    def _check_naming_conventions(self, file_path: Path, tree: ast.AST, content: str) -> List[ConsistencyIssue]:
        """检查命名约定"""
        issues = []
        
        class NamingVisitor(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
            
            def visit_FunctionDef(self, node):
                # 检查函数命名（应该是snake_case）
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('_'):
                    if re.match(r'^[a-z]+([A-Z][a-z]*)*$', node.name):  # camelCase
                        suggestion = self._camel_to_snake(node.name)
                        self.issues.append(ConsistencyIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="naming_function_camelcase",
                            message=f"函数名 '{node.name}' 应该使用snake_case命名",
                            suggestion=f"建议改为: {suggestion}",
                            auto_fixable=True
                        ))
                    elif any(c.isupper() for c in node.name):
                        self.issues.append(ConsistencyIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="naming_function_mixed_case",
                            message=f"函数名 '{node.name}' 包含大写字母，应该使用snake_case",
                            auto_fixable=False
                        ))
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # 检查类命名（应该是PascalCase）
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    if '_' in node.name:
                        suggestion = self._snake_to_pascal(node.name)
                        self.issues.append(ConsistencyIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="naming_class_snake_case",
                            message=f"类名 '{node.name}' 应该使用PascalCase命名",
                            suggestion=f"建议改为: {suggestion}",
                            auto_fixable=True
                        ))
                    else:
                        self.issues.append(ConsistencyIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="naming_class_format",
                            message=f"类名 '{node.name}' 格式不规范，应该使用PascalCase",
                            auto_fixable=False
                        ))
                self.generic_visit(node)
            
            def visit_Name(self, node):
                # 检查常量命名（应该是UPPER_CASE）
                if isinstance(node.ctx, ast.Store) and node.id.isupper() and len(node.id) > 1:
                    if not re.match(r'^[A-Z][A-Z0-9_]*$', node.id):
                        self.issues.append(ConsistencyIssue(
                            file_path=str(file_path),
                            line_number=getattr(node, 'lineno', 1),
                            issue_type="naming_constant_format",
                            message=f"常量 '{node.id}' 应该使用UPPER_CASE_WITH_UNDERSCORES",
                            auto_fixable=False
                        ))
                self.generic_visit(node)
            
            def _camel_to_snake(self, name):
                """camelCase转snake_case"""
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
                return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
            
            def _snake_to_pascal(self, name):
                """snake_case转PascalCase"""
                return ''.join(word.capitalize() for word in name.split('_'))
        
        visitor = NamingVisitor()
        visitor.visit(tree)
        issues.extend(visitor.issues)
        
        return issues
    
    def _check_import_order(self, file_path: Path, content: str) -> List[ConsistencyIssue]:
        """检查导入顺序（根据PEP 8和项目配置）"""
        issues = []
        lines = content.split('\n')
        
        import_lines = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (stripped.startswith('import ') or stripped.startswith('from ')) and not stripped.startswith('#'):
                import_lines.append((i + 1, stripped))
        
        if len(import_lines) < 2:
            return issues
        
        # 检查导入分组（标准库 -> 第三方 -> 本地）
        import_groups = self._categorize_imports(import_lines)
        
        # 检查是否按正确顺序排列
        expected_order = ['stdlib', 'third_party', 'local']
        current_group_index = 0
        
        for line_no, import_line in import_lines:
            group = self._get_import_group(import_line)
            expected_group = expected_order[current_group_index] if current_group_index < len(expected_order) else 'local'
            
            if group != expected_group:
                # 如果是向后跳跃（比如在第三方库后面出现标准库），这是错误
                if expected_order.index(group) < current_group_index:
                    issues.append(ConsistencyIssue(
                        file_path=str(file_path),
                        line_number=line_no,
                        issue_type="import_order",
                        message=f"导入顺序错误: {group}应该在{expected_group}之前",
                        suggestion="建议使用isort自动排序导入",
                        auto_fixable=True
                    ))
            
            # 更新当前组索引
            if group in expected_order:
                group_index = expected_order.index(group)
                current_group_index = max(current_group_index, group_index)
        
        # 检查同组内是否按字母顺序
        for group_name, group_imports in import_groups.items():
            if len(group_imports) > 1:
                sorted_imports = sorted(group_imports, key=lambda x: x[1])
                if [imp[1] for imp in group_imports] != [imp[1] for imp in sorted_imports]:
                    first_line = group_imports[0][0]
                    issues.append(ConsistencyIssue(
                        file_path=str(file_path),
                        line_number=first_line,
                        issue_type="import_alphabetical",
                        message=f"{group_name}组内导入应该按字母顺序排列",
                        suggestion="建议使用isort自动排序",
                        auto_fixable=True
                    ))
        
        return issues
    
    def _categorize_imports(self, import_lines: List[Tuple[int, str]]) -> Dict[str, List[Tuple[int, str]]]:
        """将导入分类"""
        groups = {'stdlib': [], 'third_party': [], 'local': []}
        
        for line_no, import_line in import_lines:
            group = self._get_import_group(import_line)
            groups[group].append((line_no, import_line))
        
        return groups
    
    def _get_import_group(self, import_line: str) -> str:
        """确定导入属于哪个组"""
        # 提取模块名
        if import_line.startswith('from '):
            module = import_line.split(' ')[1].split('.')[0]
        else:  # import
            module = import_line.split(' ')[1].split('.')[0]
        
        # 标准库模块
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'pathlib', 'subprocess', 'typing',
            'collections', 'itertools', 'functools', 're', 'math', 'random',
            'io', 'time', 'urllib', 'http', 'ast', 'inspect', 'logging'
        }
        
        if module in stdlib_modules:
            return 'stdlib'
        
        # 本地模块（项目内部）
        if module.startswith('.') or module.startswith(self.project_context.name.replace('-', '_')):
            return 'local'
        
        # 第三方模块
        return 'third_party'
    
    def _check_docstring_format(self, file_path: Path, tree: ast.AST) -> List[ConsistencyIssue]:
        """检查文档字符串格式"""
        issues = []
        
        class DocstringVisitor(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
            
            def visit_FunctionDef(self, node):
                if not self._has_docstring(node):
                    # 跳过私有方法和简单的getter/setter
                    if not node.name.startswith('_') and len(node.body) > 1:
                        self.issues.append(ConsistencyIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="missing_docstring_function",
                            message=f"函数 '{node.name}' 缺少文档字符串",
                            suggestion="添加描述函数功能、参数和返回值的文档字符串",
                            auto_fixable=False
                        ))
                else:
                    docstring = self._get_docstring(node)
                    if docstring:
                        doc_issues = self._check_docstring_content(node.lineno, docstring, 'function')
                        self.issues.extend(doc_issues)
                
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                if not self._has_docstring(node):
                    self.issues.append(ConsistencyIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        issue_type="missing_docstring_class",
                        message=f"类 '{node.name}' 缺少文档字符串",
                        suggestion="添加描述类功能和用法的文档字符串",
                        auto_fixable=False
                    ))
                else:
                    docstring = self._get_docstring(node)
                    if docstring:
                        doc_issues = self._check_docstring_content(node.lineno, docstring, 'class')
                        self.issues.extend(doc_issues)
                
                self.generic_visit(node)
            
            def _has_docstring(self, node):
                """检查节点是否有文档字符串"""
                return (len(node.body) > 0 and
                        isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant) and
                        isinstance(node.body[0].value.value, str))
            
            def _get_docstring(self, node):
                """获取文档字符串内容"""
                if self._has_docstring(node):
                    return node.body[0].value.value
                return None
            
            def _check_docstring_content(self, line_no, docstring, node_type):
                """检查文档字符串内容格式"""
                doc_issues = []
                
                # 检查是否为空或过短
                if not docstring.strip():
                    doc_issues.append(ConsistencyIssue(
                        file_path=str(file_path),
                        line_number=line_no,
                        issue_type="empty_docstring",
                        message="文档字符串为空",
                        auto_fixable=False
                    ))
                    return doc_issues
                
                if len(docstring.strip()) < 10:
                    doc_issues.append(ConsistencyIssue(
                        file_path=str(file_path),
                        line_number=line_no,
                        issue_type="docstring_too_short",
                        message="文档字符串过短，应该提供更详细的描述",
                        auto_fixable=False
                    ))
                
                # 检查是否以句号结尾（单行文档字符串）
                lines = docstring.strip().split('\n')
                if len(lines) == 1 and not lines[0].endswith('.'):
                    doc_issues.append(ConsistencyIssue(
                        file_path=str(file_path),
                        line_number=line_no,
                        issue_type="docstring_no_period",
                        message="单行文档字符串应该以句号结尾",
                        suggestion=f"在文档字符串末尾添加句号",
                        auto_fixable=True
                    ))
                
                return doc_issues
        
        visitor = DocstringVisitor()
        visitor.visit(tree)
        issues.extend(visitor.issues)
        
        return issues
    
    def _check_type_annotations(self, file_path: Path, tree: ast.AST) -> List[ConsistencyIssue]:
        """检查类型注解"""
        issues = []
        
        class TypeAnnotationVisitor(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
            
            def visit_FunctionDef(self, node):
                # 跳过私有方法
                if node.name.startswith('_'):
                    self.generic_visit(node)
                    return
                
                # 检查参数类型注解
                for arg in node.args.args:
                    if arg.annotation is None and arg.arg != 'self':
                        self.issues.append(ConsistencyIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="missing_type_annotation_param",
                            message=f"参数 '{arg.arg}' 缺少类型注解",
                            suggestion="添加类型注解提高代码可读性",
                            auto_fixable=False
                        ))
                
                # 检查返回值类型注解
                if node.returns is None and node.name != '__init__':
                    # 检查是否有return语句
                    has_return = any(isinstance(n, ast.Return) and n.value is not None 
                                   for n in ast.walk(node))
                    if has_return:
                        self.issues.append(ConsistencyIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="missing_type_annotation_return",
                            message=f"函数 '{node.name}' 缺少返回值类型注解",
                            suggestion="添加返回值类型注解",
                            auto_fixable=False
                        ))
                
                self.generic_visit(node)
        
        visitor = TypeAnnotationVisitor()
        visitor.visit(tree)
        issues.extend(visitor.issues)
        
        return issues
    
    def _check_line_length(self, file_path: Path, content: str) -> List[ConsistencyIssue]:
        """检查行长度"""
        issues = []
        
        # 从项目配置获取行长度限制
        max_length = 88  # 默认值
        if 'python' in self.project_context.coding_style.get('formatting', {}):
            max_length = self.project_context.coding_style['formatting']['python'].get('line_length', 88)
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                # 跳过URL和长字符串
                if 'http://' in line or 'https://' in line:
                    continue
                if line.strip().startswith('#'):  # 注释
                    continue
                
                issues.append(ConsistencyIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type="line_too_long",
                    message=f"行长度 {len(line)} 超过限制 {max_length}",
                    suggestion="考虑断行或重构以减少行长度",
                    auto_fixable=True
                ))
        
        return issues
    
    def _check_code_formatting(self, file_path: Path, content: str) -> List[ConsistencyIssue]:
        """检查代码格式"""
        issues = []
        
        # 检查是否有多余的空行
        lines = content.split('\n')
        consecutive_empty = 0
        
        for i, line in enumerate(lines, 1):
            if line.strip() == '':
                consecutive_empty += 1
                if consecutive_empty > 2:
                    issues.append(ConsistencyIssue(
                        file_path=str(file_path),
                        line_number=i,
                        issue_type="too_many_blank_lines",
                        message="连续空行超过2行",
                        suggestion="删除多余的空行",
                        auto_fixable=True
                    ))
            else:
                consecutive_empty = 0
        
        # 检查尾随空格
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                issues.append(ConsistencyIssue(
                    file_path=str(file_path),
                    line_number=i,
                    issue_type="trailing_whitespace",
                    message="行尾有多余空格",
                    suggestion="删除尾随空格",
                    auto_fixable=True
                ))
        
        return issues
    
    def _auto_fix_file(self, file_path: Path, issues: List[ConsistencyIssue]) -> bool:
        """自动修复文件中的可修复问题"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            modified = False
            
            # 按行号倒序处理，避免行号偏移
            auto_fixable_issues = [issue for issue in issues if issue.auto_fixable]
            auto_fixable_issues.sort(key=lambda x: x.line_number, reverse=True)
            
            for issue in auto_fixable_issues:
                if issue.issue_type == "trailing_whitespace":
                    if issue.line_number <= len(lines):
                        lines[issue.line_number - 1] = lines[issue.line_number - 1].rstrip()
                        modified = True
                
                elif issue.issue_type == "too_many_blank_lines":
                    # 删除多余的空行
                    if issue.line_number <= len(lines) and lines[issue.line_number - 1].strip() == '':
                        lines.pop(issue.line_number - 1)
                        modified = True
                
                elif issue.issue_type == "docstring_no_period":
                    # 给文档字符串添加句号
                    if issue.line_number <= len(lines):
                        line = lines[issue.line_number - 1]
                        if '"""' in line and not line.rstrip().endswith('.'):
                            lines[issue.line_number - 1] = line.rstrip() + '.'
                            modified = True
            
            if modified:
                file_path.write_text('\n'.join(lines), encoding='utf-8')
                return True
                
        except Exception as e:
            print(f"自动修复 {file_path} 失败: {e}")
            
        return False
    
    def run_external_tools(self, file_paths: List[Path]) -> Dict[str, Any]:
        """运行外部代码格式化和检查工具"""
        results = {}
        
        # 运行black格式化
        if 'python' in self.project_context.coding_style.get('formatting', {}):
            formatter = self.project_context.coding_style['formatting']['python'].get('formatter')
            
            if formatter == 'black':
                try:
                    for file_path in file_paths:
                        if file_path.suffix == '.py':
                            result = subprocess.run(
                                ['black', '--check', str(file_path)],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            if result.returncode != 0:
                                results[f'black_{file_path}'] = {
                                    'tool': 'black',
                                    'status': 'needs_formatting',
                                    'output': result.stdout
                                }
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    results['black_error'] = 'Black工具不可用'
        
        # 运行isort检查
        if 'isort' in str(self.project_context.coding_style):
            try:
                for file_path in file_paths:
                    if file_path.suffix == '.py':
                        result = subprocess.run(
                            ['isort', '--check-only', str(file_path)],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        if result.returncode != 0:
                            results[f'isort_{file_path}'] = {
                                'tool': 'isort',
                                'status': 'needs_sorting',
                                'output': result.stdout
                            }
            except (subprocess.TimeoutExpired, FileNotFoundError):
                results['isort_error'] = 'isort工具不可用'
        
        return results 