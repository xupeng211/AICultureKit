"""
AI质量审查器

分析代码质量并提供改进建议，专门针对AI生成的代码。
解决痛点：AI代码需要人工审查
"""

import ast
import re
import math
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from collections import defaultdict
from .context_generator import ProjectContextGenerator


@dataclass
class QualityIssue:
    """质量问题"""
    file_path: str
    line_number: int
    severity: str  # 'low', 'medium', 'high', 'critical'
    category: str
    message: str
    suggestion: str
    code_snippet: Optional[str] = None
    confidence: float = 1.0  # 0.0-1.0，置信度


@dataclass
class QualityMetrics:
    """质量指标"""
    complexity_score: float
    maintainability_index: float
    test_coverage_estimate: float
    documentation_score: float
    overall_score: float


@dataclass
class QualityReport:
    """质量审查报告"""
    file_path: str
    metrics: QualityMetrics
    issues: List[QualityIssue]
    suggestions: List[str]
    ai_feedback: str


class AIQualityReviewer:
    """
    AI代码质量审查器
    
    专门针对AI生成代码的质量问题：
    - 代码复杂度过高
    - 可能的逻辑错误
    - 性能问题
    - 安全隐患
    - 可维护性问题
    - 测试覆盖度估算
    """
    
    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.context_generator = ProjectContextGenerator(project_path)
        self.project_context = self.context_generator.generate_context()
        
    def review_file(self, file_path: Path) -> QualityReport:
        """审查单个文件的质量"""
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # 计算质量指标
            metrics = self._calculate_metrics(tree, content)
            
            # 检测质量问题
            issues = []
            issues.extend(self._check_complexity(file_path, tree))
            issues.extend(self._check_logic_issues(file_path, tree, content))
            issues.extend(self._check_performance_issues(file_path, tree))
            issues.extend(self._check_security_issues(file_path, tree, content))
            issues.extend(self._check_maintainability(file_path, tree, content))
            issues.extend(self._check_ai_specific_issues(file_path, tree, content))
            
            # 生成改进建议
            suggestions = self._generate_suggestions(metrics, issues)
            
            # 生成AI反馈
            ai_feedback = self._generate_ai_feedback(file_path, metrics, issues)
            
            return QualityReport(
                file_path=str(file_path),
                metrics=metrics,
                issues=issues,
                suggestions=suggestions,
                ai_feedback=ai_feedback
            )
            
        except SyntaxError as e:
            return QualityReport(
                file_path=str(file_path),
                metrics=QualityMetrics(0, 0, 0, 0, 0),
                issues=[QualityIssue(
                    file_path=str(file_path),
                    line_number=e.lineno or 1,
                    severity='critical',
                    category='syntax',
                    message=f"语法错误: {e.msg}",
                    suggestion="修复语法错误后重新审查"
                )],
                suggestions=["修复语法错误"],
                ai_feedback="代码存在语法错误，无法进行质量分析"
            )
    
    def _calculate_metrics(self, tree: ast.AST, content: str) -> QualityMetrics:
        """计算代码质量指标"""
        
        # 1. 复杂度评分 (基于圈复杂度)
        complexity_score = self._calculate_complexity_score(tree)
        
        # 2. 可维护性指数
        maintainability_index = self._calculate_maintainability_index(tree, content)
        
        # 3. 测试覆盖度估算
        test_coverage_estimate = self._estimate_test_coverage(tree)
        
        # 4. 文档评分
        documentation_score = self._calculate_documentation_score(tree)
        
        # 5. 总体评分 (加权平均)
        overall_score = (
            complexity_score * 0.25 +
            maintainability_index * 0.25 +
            test_coverage_estimate * 0.20 +
            documentation_score * 0.30
        )
        
        return QualityMetrics(
            complexity_score=complexity_score,
            maintainability_index=maintainability_index,
            test_coverage_estimate=test_coverage_estimate,
            documentation_score=documentation_score,
            overall_score=overall_score
        )
    
    def _calculate_complexity_score(self, tree: ast.AST) -> float:
        """计算复杂度评分 (0-100, 越高越好)"""
        
        class ComplexityCalculator(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 1  # 基础复杂度
                self.function_complexities = []
                self.current_function_complexity = 0
                
            def visit_FunctionDef(self, node):
                old_complexity = self.current_function_complexity
                self.current_function_complexity = 1  # 函数基础复杂度
                
                self.generic_visit(node)
                
                self.function_complexities.append(self.current_function_complexity)
                self.current_function_complexity = old_complexity
                
            def visit_If(self, node):
                self.complexity += 1
                self.current_function_complexity += 1
                self.generic_visit(node)
                
            def visit_While(self, node):
                self.complexity += 1
                self.current_function_complexity += 1
                self.generic_visit(node)
                
            def visit_For(self, node):
                self.complexity += 1
                self.current_function_complexity += 1
                self.generic_visit(node)
                
            def visit_Try(self, node):
                self.complexity += 1
                self.current_function_complexity += 1
                self.generic_visit(node)
                
            def visit_With(self, node):
                self.complexity += 1
                self.current_function_complexity += 1
                self.generic_visit(node)
        
        calculator = ComplexityCalculator()
        calculator.visit(tree)
        
        # 基于圈复杂度计算评分
        avg_complexity = calculator.complexity / max(len(calculator.function_complexities), 1)
        
        # 转换为0-100分（复杂度越低分数越高）
        if avg_complexity <= 5:
            return 100
        elif avg_complexity <= 10:
            return max(80, 100 - (avg_complexity - 5) * 4)
        elif avg_complexity <= 20:
            return max(50, 80 - (avg_complexity - 10) * 3)
        else:
            return max(0, 50 - (avg_complexity - 20) * 2)
    
    def _calculate_maintainability_index(self, tree: ast.AST, content: str) -> float:
        """计算可维护性指数"""
        
        lines = content.split('\n')
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        class MaintainabilityCalculator(ast.NodeVisitor):
            def __init__(self):
                self.functions = 0
                self.classes = 0
                self.operators = 0
                self.operands = 0
                
            def visit_FunctionDef(self, node):
                self.functions += 1
                self.generic_visit(node)
                
            def visit_ClassDef(self, node):
                self.classes += 1
                self.generic_visit(node)
                
            def visit_BinOp(self, node):
                self.operators += 1
                self.generic_visit(node)
                
            def visit_Name(self, node):
                self.operands += 1
                self.generic_visit(node)
        
        calc = MaintainabilityCalculator()
        calc.visit(tree)
        
        # 简化的可维护性指数计算
        # 基于Halstead指标和代码行数
        program_length = calc.operators + calc.operands
        vocabulary = calc.functions + calc.classes + 10  # 估算
        
        if vocabulary > 0 and program_length > 0:
            volume = program_length * math.log2(vocabulary)
            maintainability = max(0, 171 - 5.2 * math.log(volume) - 0.23 * 10 - 16.2 * math.log(code_lines))
            return min(100, max(0, maintainability))
        
        return 50  # 默认值
    
    def _estimate_test_coverage(self, tree: ast.AST) -> float:
        """估算测试覆盖度"""
        
        class TestCoverageEstimator(ast.NodeVisitor):
            def __init__(self):
                self.public_functions = 0
                self.documented_functions = 0
                self.simple_functions = 0
                self.complex_functions = 0
                
            def visit_FunctionDef(self, node):
                if not node.name.startswith('_'):  # 公开函数
                    self.public_functions += 1
                    
                    # 检查是否有文档字符串
                    if (len(node.body) > 0 and
                        isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant)):
                        self.documented_functions += 1
                    
                    # 估算函数复杂度
                    complexity = self._estimate_function_complexity(node)
                    if complexity <= 3:
                        self.simple_functions += 1
                    else:
                        self.complex_functions += 1
                
                self.generic_visit(node)
                
            def _estimate_function_complexity(self, node):
                complexity = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                        complexity += 1
                return complexity
        
        estimator = TestCoverageEstimator()
        estimator.visit(tree)
        
        if estimator.public_functions == 0:
            return 100  # 没有公开函数，认为覆盖度满分
        
        # 基于函数复杂度和文档完整性估算测试覆盖度
        documentation_bonus = estimator.documented_functions / estimator.public_functions * 20
        simplicity_bonus = estimator.simple_functions / estimator.public_functions * 30
        
        # 基础覆盖度假设 + 奖励分
        base_coverage = 40  # 假设基础覆盖度40%
        estimated_coverage = base_coverage + documentation_bonus + simplicity_bonus
        
        return min(100, max(0, estimated_coverage))
    
    def _calculate_documentation_score(self, tree: ast.AST) -> float:
        """计算文档评分"""
        
        class DocumentationScorer(ast.NodeVisitor):
            def __init__(self):
                self.total_items = 0
                self.documented_items = 0
                self.high_quality_docs = 0
                
            def visit_FunctionDef(self, node):
                self.total_items += 1
                docstring = self._get_docstring(node)
                if docstring:
                    self.documented_items += 1
                    if len(docstring.strip()) > 50:  # 高质量文档
                        self.high_quality_docs += 1
                self.generic_visit(node)
                
            def visit_ClassDef(self, node):
                self.total_items += 1
                docstring = self._get_docstring(node)
                if docstring:
                    self.documented_items += 1
                    if len(docstring.strip()) > 50:
                        self.high_quality_docs += 1
                self.generic_visit(node)
                
            def _get_docstring(self, node):
                if (len(node.body) > 0 and
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)):
                    return node.body[0].value.value
                return None
        
        scorer = DocumentationScorer()
        scorer.visit(tree)
        
        if scorer.total_items == 0:
            return 100
        
        basic_score = (scorer.documented_items / scorer.total_items) * 70
        quality_bonus = (scorer.high_quality_docs / scorer.total_items) * 30
        
        return min(100, basic_score + quality_bonus)
    
    def _check_complexity(self, file_path: Path, tree: ast.AST) -> List[QualityIssue]:
        """检查复杂度问题"""
        issues = []
        
        class ComplexityChecker(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                complexity = self._calculate_function_complexity(node)
                
                if complexity > 20:
                    issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        severity='critical',
                        category='complexity',
                        message=f"函数 '{node.name}' 复杂度过高 (复杂度: {complexity})",
                        suggestion="考虑拆分函数，使用提取方法重构",
                        confidence=0.9
                    ))
                elif complexity > 10:
                    issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        severity='medium',
                        category='complexity',
                        message=f"函数 '{node.name}' 复杂度较高 (复杂度: {complexity})",
                        suggestion="考虑简化逻辑或拆分函数",
                        confidence=0.8
                    ))
                
                self.generic_visit(node)
            
            def _calculate_function_complexity(self, node):
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                        complexity += 1
                return complexity
        
        checker = ComplexityChecker()
        checker.visit(tree)
        
        return issues
    
    def _check_logic_issues(self, file_path: Path, tree: ast.AST, content: str) -> List[QualityIssue]:
        """检查逻辑问题"""
        issues = []
        
        class LogicChecker(ast.NodeVisitor):
            def visit_Compare(self, node):
                # 检查可能的比较错误
                if len(node.ops) > 1:
                    issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        severity='medium',
                        category='logic',
                        message="复杂的链式比较可能导致逻辑错误",
                        suggestion="考虑拆分为多个简单的比较",
                        confidence=0.6
                    ))
                
                self.generic_visit(node)
            
            def visit_BoolOp(self, node):
                # 检查复杂的布尔表达式
                if len(node.values) > 3:
                    issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        severity='low',
                        category='logic',
                        message="复杂的布尔表达式可能难以理解",
                        suggestion="考虑提取中间变量或使用括号明确优先级",
                        confidence=0.7
                    ))
                
                self.generic_visit(node)
            
            def visit_If(self, node):
                # 检查深度嵌套的if语句
                depth = self._count_nested_ifs(node)
                if depth > 3:
                    issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        severity='medium',
                        category='logic',
                        message=f"if语句嵌套过深 (深度: {depth})",
                        suggestion="考虑使用早期返回或提取函数来减少嵌套",
                        confidence=0.8
                    ))
                
                self.generic_visit(node)
            
            def _count_nested_ifs(self, node, depth=0):
                max_depth = depth
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, ast.If):
                        child_depth = self._count_nested_ifs(child, depth + 1)
                        max_depth = max(max_depth, child_depth)
                return max_depth
        
        checker = LogicChecker()
        checker.visit(tree)
        
        return issues
    
    def _check_performance_issues(self, file_path: Path, tree: ast.AST) -> List[QualityIssue]:
        """检查性能问题"""
        issues = []
        
        class PerformanceChecker(ast.NodeVisitor):
            def visit_ListComp(self, node):
                # 检查嵌套列表推导式
                nested_comps = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp)):
                        nested_comps += 1
                
                if nested_comps > 2:
                    issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        severity='medium',
                        category='performance',
                        message="嵌套的列表推导式可能影响性能",
                        suggestion="考虑使用循环或分步处理",
                        confidence=0.7
                    ))
                
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # 检查循环中的函数调用
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    
                    # 检查可能的性能问题函数
                    expensive_funcs = {'len', 'sum', 'max', 'min'}
                    if func_name in expensive_funcs:
                        # 检查是否在循环中
                        parent = getattr(node, 'parent', None)
                        while parent:
                            if isinstance(parent, (ast.For, ast.While)):
                                issues.append(QualityIssue(
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    severity='low',
                                    category='performance',
                                    message=f"在循环中调用 '{func_name}' 可能影响性能",
                                    suggestion="考虑将结果缓存在循环外",
                                    confidence=0.6
                                ))
                                break
                            parent = getattr(parent, 'parent', None)
                
                self.generic_visit(node)
        
        checker = PerformanceChecker()
        
        # 为AST节点添加父节点引用
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        checker.visit(tree)
        
        return issues
    
    def _check_security_issues(self, file_path: Path, tree: ast.AST, content: str) -> List[QualityIssue]:
        """检查安全问题"""
        issues = []
        
        # 检查危险函数调用
        dangerous_patterns = [
            ('eval', 'critical', '使用eval()函数存在代码注入风险'),
            ('exec', 'critical', '使用exec()函数存在代码注入风险'),
            ('input', 'medium', '使用input()函数要注意输入验证'),
            ('os.system', 'high', '使用os.system()存在命令注入风险'),
            ('subprocess.call', 'medium', '使用subprocess要注意参数验证'),
        ]
        
        for pattern, severity, message in dangerous_patterns:
            if pattern in content:
                # 简单的行号查找
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if pattern in line and not line.strip().startswith('#'):
                        issues.append(QualityIssue(
                            file_path=str(file_path),
                            line_number=i,
                            severity=severity,
                            category='security',
                            message=message,
                            suggestion="考虑使用更安全的替代方案",
                            code_snippet=line.strip(),
                            confidence=0.8
                        ))
        
        return issues
    
    def _check_maintainability(self, file_path: Path, tree: ast.AST, content: str) -> List[QualityIssue]:
        """检查可维护性问题"""
        issues = []
        
        class MaintainabilityChecker(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # 检查函数长度
                function_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 20
                
                if function_lines > 50:
                    issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        severity='medium',
                        category='maintainability',
                        message=f"函数 '{node.name}' 过长 ({function_lines} 行)",
                        suggestion="考虑拆分函数提高可读性",
                        confidence=0.8
                    ))
                
                # 检查参数数量
                param_count = len(node.args.args)
                if param_count > 7:
                    issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        severity='medium',
                        category='maintainability',
                        message=f"函数 '{node.name}' 参数过多 ({param_count} 个)",
                        suggestion="考虑使用配置对象或拆分函数",
                        confidence=0.9
                    ))
                
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # 检查类的方法数量
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 20:
                    issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        severity='low',
                        category='maintainability',
                        message=f"类 '{node.name}' 方法过多 ({len(methods)} 个)",
                        suggestion="考虑拆分类或使用组合模式",
                        confidence=0.7
                    ))
                
                self.generic_visit(node)
        
        checker = MaintainabilityChecker()
        checker.visit(tree)
        
        return issues
    
    def _check_ai_specific_issues(self, file_path: Path, tree: ast.AST, content: str) -> List[QualityIssue]:
        """检查AI生成代码的特定问题"""
        issues = []
        
        # 检查AI生成代码的常见模式
        ai_indicators = [
            ('# TODO: implement', 'medium', 'AI可能生成了未实现的TODO项'),
            ('# Generated by', 'low', '代码包含AI生成标记'),
            ('# This is a placeholder', 'medium', '包含占位符代码'),
            ('def function_name(', 'high', '可能包含未重命名的模板函数'),
            ('class ClassName(', 'high', '可能包含未重命名的模板类'),
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            for pattern, severity, message in ai_indicators:
                if pattern.lower() in line_lower:
                    issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=i,
                        severity=severity,
                        category='ai_specific',
                        message=message,
                        suggestion="检查并完善AI生成的代码",
                        code_snippet=line.strip(),
                        confidence=0.6
                    ))
        
        # 检查重复的代码块
        self._check_code_duplication(file_path, content, issues)
        
        return issues
    
    def _check_code_duplication(self, file_path: Path, content: str, issues: List[QualityIssue]):
        """检查代码重复"""
        lines = content.split('\n')
        line_hashes = {}
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if len(stripped) > 10 and not stripped.startswith('#'):
                if stripped in line_hashes:
                    issues.append(QualityIssue(
                        file_path=str(file_path),
                        line_number=i,
                        severity='low',
                        category='duplication',
                        message=f"发现重复代码行 (与第{line_hashes[stripped]}行相同)",
                        suggestion="考虑提取公共函数消除重复",
                        code_snippet=stripped,
                        confidence=0.8
                    ))
                else:
                    line_hashes[stripped] = i
    
    def _generate_suggestions(self, metrics: QualityMetrics, issues: List[QualityIssue]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于质量指标的建议
        if metrics.complexity_score < 60:
            suggestions.append("🔧 降低代码复杂度：考虑拆分复杂函数，使用更清晰的逻辑结构")
        
        if metrics.documentation_score < 70:
            suggestions.append("📝 改善文档：为函数和类添加详细的文档字符串")
        
        if metrics.test_coverage_estimate < 60:
            suggestions.append("🧪 增加测试：编写更多测试用例提高代码可靠性")
        
        # 基于问题类型的建议
        issue_categories = defaultdict(int)
        for issue in issues:
            issue_categories[issue.category] += 1
        
        if issue_categories['complexity'] > 0:
            suggestions.append("⚡ 简化复杂逻辑：使用设计模式重构复杂代码")
        
        if issue_categories['security'] > 0:
            suggestions.append("🔒 加强安全性：审查潜在的安全风险点")
        
        if issue_categories['performance'] > 0:
            suggestions.append("🚀 优化性能：关注循环效率和数据结构选择")
        
        if issue_categories['ai_specific'] > 0:
            suggestions.append("🤖 完善AI代码：检查并改进AI生成的模板代码")
        
        return suggestions[:5]  # 最多5条建议
    
    def _generate_ai_feedback(self, file_path: Path, metrics: QualityMetrics, issues: List[QualityIssue]) -> str:
        """生成AI反馈"""
        
        # 总体评价
        if metrics.overall_score >= 80:
            quality_level = "优秀"
            emoji = "🌟"
        elif metrics.overall_score >= 60:
            quality_level = "良好"
            emoji = "👍"
        elif metrics.overall_score >= 40:
            quality_level = "一般"
            emoji = "⚠️"
        else:
            quality_level = "需要改进"
            emoji = "🚨"
        
        feedback = f"""{emoji} **代码质量评估: {quality_level} ({metrics.overall_score:.1f}/100)**

📊 **详细指标:**
• 复杂度控制: {metrics.complexity_score:.1f}/100
• 可维护性: {metrics.maintainability_index:.1f}/100  
• 文档完整性: {metrics.documentation_score:.1f}/100
• 测试覆盖估算: {metrics.test_coverage_estimate:.1f}/100

"""
        
        # 重点问题
        critical_issues = [issue for issue in issues if issue.severity == 'critical']
        high_issues = [issue for issue in issues if issue.severity == 'high']
        
        if critical_issues:
            feedback += f"🚨 **严重问题** ({len(critical_issues)}个):\n"
            for issue in critical_issues[:3]:
                feedback += f"• 行{issue.line_number}: {issue.message}\n"
        
        if high_issues:
            feedback += f"\n⚠️ **重要问题** ({len(high_issues)}个):\n"
            for issue in high_issues[:3]:
                feedback += f"• 行{issue.line_number}: {issue.message}\n"
        
        # AI协作建议
        feedback += f"\n🤖 **AI协作建议:**\n"
        
        if metrics.overall_score >= 70:
            feedback += "• 代码质量较好，可以继续在此基础上开发\n"
            feedback += "• 建议与AI讨论具体的功能扩展和优化方向\n"
        else:
            feedback += "• 建议先与AI一起重构代码结构\n"
            feedback += "• 可以请AI解释复杂逻辑并提供简化方案\n"
            feedback += "• 逐步改进，每次专注解决一类问题\n"
        
        return feedback 