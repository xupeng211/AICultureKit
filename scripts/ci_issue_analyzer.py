#!/usr/bin/env python3
"""
CI问题智能分析器 - 深度分析CI失败原因并提供精确解决方案

这个模块专门负责：
1. 深度解析各种CI工具的输出格式
2. 智能分类CI问题并评估影响程度  
3. 提供针对性的解决方案建议
4. 生成问题趋势分析报告

作者：AI CI Guardian System  
版本：v1.0.0
"""

import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import click


class CIToolOutput:
    """CI工具输出解析器基类"""
    
    def parse(self, output: str) -> List[Dict]:
        """解析工具输出并返回标准化的问题列表"""
        raise NotImplementedError


class RuffOutputParser(CIToolOutput):
    """Ruff代码检查输出解析器"""
    
    def parse(self, output: str) -> List[Dict]:
        """解析Ruff输出"""
        issues = []
        
        # Ruff输出格式: path/to/file.py:line:col: CODE message
        pattern = r'([^:]+):(\d+):(\d+): (\w+) (.+)'
        
        for line in output.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                file_path, line_num, col_num, code, message = match.groups()
                
                issues.append({
                    'tool': 'ruff',
                    'file_path': file_path,
                    'line_number': int(line_num),
                    'column': int(col_num),
                    'rule_code': code,
                    'message': message,
                    'severity': self._get_ruff_severity(code),
                    'category': self._get_ruff_category(code)
                })
        
        return issues
    
    def _get_ruff_severity(self, code: str) -> str:
        """根据Ruff规则代码确定严重程度"""
        if code.startswith(('E9', 'F')):  # 语法错误、未定义名称
            return 'high'
        elif code.startswith(('E', 'W')):  # 一般错误和警告
            return 'medium'
        else:
            return 'low'
    
    def _get_ruff_category(self, code: str) -> str:
        """根据Ruff规则代码确定问题分类"""
        if code.startswith('F'):
            return 'logic_error'
        elif code.startswith('E'):
            return 'style_error'  
        elif code.startswith('W'):
            return 'style_warning'
        elif code.startswith('I'):
            return 'import_issue'
        else:
            return 'other'


class MyPyOutputParser(CIToolOutput):
    """MyPy类型检查输出解析器"""
    
    def parse(self, output: str) -> List[Dict]:
        """解析MyPy输出"""
        issues = []
        
        # MyPy输出格式: path/to/file.py:line: error: message
        pattern = r'([^:]+):(\d+): (\w+): (.+)'
        
        for line in output.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                file_path, line_num, level, message = match.groups()
                
                issues.append({
                    'tool': 'mypy',
                    'file_path': file_path,
                    'line_number': int(line_num),
                    'level': level,
                    'message': message,
                    'severity': 'high' if level == 'error' else 'medium',
                    'category': self._get_mypy_category(message)
                })
        
        return issues
    
    def _get_mypy_category(self, message: str) -> str:
        """根据MyPy错误信息确定问题分类"""
        if 'incompatible types' in message.lower():
            return 'type_mismatch'
        elif 'missing type annotation' in message.lower():
            return 'missing_annotation'
        elif 'has no attribute' in message.lower():
            return 'attribute_error'
        elif 'cannot determine type' in message.lower():
            return 'type_inference_failed'
        else:
            return 'type_error'


class PytestOutputParser(CIToolOutput):
    """Pytest测试输出解析器"""
    
    def parse(self, output: str) -> List[Dict]:
        """解析Pytest输出"""
        issues = []
        
        # 解析失败的测试
        in_failure_section = False
        current_test = None
        failure_lines = []
        
        for line in output.split('\n'):
            # 检测失败测试开始
            if '= FAILURES =' in line:
                in_failure_section = True
                continue
            
            # 检测失败测试结束
            if line.startswith('=') and 'short test summary' in line:
                in_failure_section = False
                if current_test and failure_lines:
                    issues.append(self._parse_test_failure(current_test, failure_lines))
                break
            
            if in_failure_section:
                # 解析测试名称
                if line.startswith('_' * 20):
                    if current_test and failure_lines:
                        issues.append(self._parse_test_failure(current_test, failure_lines))
                    
                    # 提取新的测试名称
                    test_match = re.search(r'([^:]+)::\w+::(test_\w+)', line)
                    if test_match:
                        current_test = {
                            'file_path': test_match.group(1),
                            'test_name': test_match.group(2)
                        }
                        failure_lines = []
                elif current_test:
                    failure_lines.append(line)
        
        # 处理最后一个失败测试
        if current_test and failure_lines:
            issues.append(self._parse_test_failure(current_test, failure_lines))
        
        return issues
    
    def _parse_test_failure(self, test_info: Dict, failure_lines: List[str]) -> Dict:
        """解析单个测试失败信息"""
        failure_text = '\n'.join(failure_lines)
        
        # 检测断言错误
        assert_match = re.search(r'assert (.+)', failure_text)
        assertion = assert_match.group(1) if assert_match else ""
        
        # 检测异常类型
        exception_match = re.search(r'(\w+Error): (.+)', failure_text)
        exception_type = exception_match.group(1) if exception_match else "AssertionError"
        exception_message = exception_match.group(2) if exception_match else ""
        
        return {
            'tool': 'pytest',
            'file_path': test_info['file_path'],
            'test_name': test_info['test_name'],
            'assertion': assertion,
            'exception_type': exception_type,
            'exception_message': exception_message,
            'failure_text': failure_text,
            'severity': 'high',
            'category': self._get_test_failure_category(exception_type, failure_text)
        }
    
    def _get_test_failure_category(self, exception_type: str, failure_text: str) -> str:
        """根据测试失败信息确定问题分类"""
        if 'ImportError' in exception_type or 'ModuleNotFoundError' in exception_type:
            return 'import_error'
        elif 'AssertionError' in exception_type:
            return 'assertion_failure'
        elif 'AttributeError' in exception_type:
            return 'attribute_error'
        elif 'TypeError' in exception_type:
            return 'type_error'
        else:
            return 'test_failure'


class BanditOutputParser(CIToolOutput):
    """Bandit安全检查输出解析器"""
    
    def parse(self, output: str) -> List[Dict]:
        """解析Bandit输出"""
        issues = []
        
        # Bandit通常输出JSON格式，但也可能是文本格式
        try:
            # 尝试解析JSON格式
            data = json.loads(output)
            if 'results' in data:
                for result in data['results']:
                    issues.append({
                        'tool': 'bandit',
                        'file_path': result.get('filename', ''),
                        'line_number': result.get('line_number', 0),
                        'test_id': result.get('test_id', ''),
                        'test_name': result.get('test_name', ''),
                        'issue_text': result.get('issue_text', ''),
                        'issue_severity': result.get('issue_severity', 'MEDIUM'),
                        'issue_confidence': result.get('issue_confidence', 'MEDIUM'),
                        'severity': self._get_bandit_severity(result.get('issue_severity', 'MEDIUM')),
                        'category': 'security_issue'
                    })
        except json.JSONDecodeError:
            # 解析文本格式
            pattern = r'>> Issue: \[([^\]]+)\] (.+)'
            for line in output.split('\n'):
                match = re.search(pattern, line)
                if match:
                    test_id, description = match.groups()
                    issues.append({
                        'tool': 'bandit',
                        'test_id': test_id,
                        'description': description,
                        'severity': 'medium',
                        'category': 'security_issue'
                    })
        
        return issues
    
    def _get_bandit_severity(self, bandit_severity: str) -> str:
        """转换Bandit严重程度到标准格式"""
        severity_map = {
            'HIGH': 'high',
            'MEDIUM': 'medium', 
            'LOW': 'low'
        }
        return severity_map.get(bandit_severity.upper(), 'medium')


class CoverageOutputParser(CIToolOutput):
    """Coverage覆盖率输出解析器"""
    
    def parse(self, output: str) -> List[Dict]:
        """解析Coverage输出"""
        issues = []
        
        # 解析覆盖率摘要
        pattern = r'TOTAL\s+\d+\s+\d+\s+(\d+)%'
        match = re.search(pattern, output)
        if match:
            total_coverage = int(match.group(1))
            
            if total_coverage < 80:  # 假设80%是最低要求
                issues.append({
                    'tool': 'coverage',
                    'message': f'总覆盖率 {total_coverage}% 低于要求的80%',
                    'total_coverage': total_coverage,
                    'severity': 'high' if total_coverage < 60 else 'medium',
                    'category': 'coverage_low'
                })
        
        # 解析具体文件的覆盖率
        file_pattern = r'([^\s]+\.py)\s+\d+\s+\d+\s+(\d+)%'
        for line in output.split('\n'):
            match = re.search(file_pattern, line)
            if match:
                file_path, coverage = match.groups()
                coverage_pct = int(coverage)
                
                if coverage_pct < 80:
                    issues.append({
                        'tool': 'coverage',
                        'file_path': file_path,
                        'coverage_percentage': coverage_pct,
                        'message': f'{file_path} 覆盖率 {coverage_pct}% 过低',
                        'severity': 'medium',
                        'category': 'file_coverage_low'
                    })
        
        return issues


class CIAnalyzer:
    """CI问题智能分析器主控制器"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.parsers = {
            'ruff': RuffOutputParser(),
            'mypy': MyPyOutputParser(), 
            'pytest': PytestOutputParser(),
            'bandit': BanditOutputParser(),
            'coverage': CoverageOutputParser()
        }
        
    def analyze_tool_output(self, tool_name: str, output: str) -> List[Dict]:
        """分析特定工具的输出"""
        parser = self.parsers.get(tool_name.lower())
        if not parser:
            click.echo(f"⚠️ 不支持的工具: {tool_name}")
            return []
        
        return parser.parse(output)
    
    def analyze_quality_check_log(self, log_file: Path = None) -> Dict[str, List[Dict]]:
        """分析质量检查日志文件"""
        if not log_file:
            log_file = self.project_root / "logs" / "quality_check.json"
        
        if not log_file.exists():
            click.echo(f"❌ 日志文件不存在: {log_file}")
            return {}
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        except Exception as e:
            click.echo(f"❌ 读取日志文件失败: {e}")
            return {}
        
        all_issues = {}
        
        if 'checks' in log_data:
            for check_name, check_data in log_data['checks'].items():
                if not check_data.get('success', True):
                    output = check_data.get('output', '')
                    issues = self.analyze_tool_output(check_name, output)
                    if issues:
                        all_issues[check_name] = issues
        
        return all_issues
    
    def generate_problem_analysis_report(self, issues_by_tool: Dict[str, List[Dict]]) -> Dict:
        """生成问题分析报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_issues': 0,
                'by_severity': defaultdict(int),
                'by_category': defaultdict(int),
                'by_tool': defaultdict(int)
            },
            'detailed_analysis': {},
            'recommendations': []
        }
        
        all_issues = []
        for tool, issues in issues_by_tool.items():
            all_issues.extend(issues)
            report['summary']['by_tool'][tool] = len(issues)
        
        report['summary']['total_issues'] = len(all_issues)
        
        # 统计分析
        for issue in all_issues:
            severity = issue.get('severity', 'medium')
            category = issue.get('category', 'other')
            
            report['summary']['by_severity'][severity] += 1
            report['summary']['by_category'][category] += 1
        
        # 详细分析
        report['detailed_analysis'] = self._generate_detailed_analysis(issues_by_tool)
        
        # 生成建议
        report['recommendations'] = self._generate_recommendations(issues_by_tool)
        
        return report
    
    def _generate_detailed_analysis(self, issues_by_tool: Dict[str, List[Dict]]) -> Dict:
        """生成详细分析"""
        analysis = {}
        
        for tool, issues in issues_by_tool.items():
            tool_analysis = {
                'issue_count': len(issues),
                'severity_distribution': defaultdict(int),
                'common_problems': defaultdict(int),
                'affected_files': set()
            }
            
            for issue in issues:
                severity = issue.get('severity', 'medium')
                category = issue.get('category', 'other')
                file_path = issue.get('file_path', '')
                
                tool_analysis['severity_distribution'][severity] += 1
                tool_analysis['common_problems'][category] += 1
                
                if file_path:
                    tool_analysis['affected_files'].add(file_path)
            
            # 转换set为list以便JSON序列化
            tool_analysis['affected_files'] = list(tool_analysis['affected_files'])
            
            analysis[tool] = tool_analysis
        
        return analysis
    
    def _generate_recommendations(self, issues_by_tool: Dict[str, List[Dict]]) -> List[Dict]:
        """生成解决建议"""
        recommendations = []
        
        for tool, issues in issues_by_tool.items():
            if tool == 'ruff':
                recommendations.extend(self._generate_ruff_recommendations(issues))
            elif tool == 'mypy':
                recommendations.extend(self._generate_mypy_recommendations(issues))
            elif tool == 'pytest':
                recommendations.extend(self._generate_pytest_recommendations(issues))
            elif tool == 'bandit':
                recommendations.extend(self._generate_bandit_recommendations(issues))
            elif tool == 'coverage':
                recommendations.extend(self._generate_coverage_recommendations(issues))
        
        return recommendations
    
    def _generate_ruff_recommendations(self, issues: List[Dict]) -> List[Dict]:
        """生成Ruff问题的解决建议"""
        recommendations = []
        
        # 按问题类型分组
        by_category = defaultdict(list)
        for issue in issues:
            by_category[issue.get('category', 'other')].append(issue)
        
        if 'style_error' in by_category:
            recommendations.append({
                'tool': 'ruff',
                'category': 'style_error',
                'priority': 'high',
                'action': 'auto_fix',
                'description': '运行 ruff --fix 自动修复代码风格问题',
                'command': 'ruff check --fix src/ tests/',
                'affected_count': len(by_category['style_error'])
            })
        
        if 'import_issue' in by_category:
            recommendations.append({
                'tool': 'ruff', 
                'category': 'import_issue',
                'priority': 'medium',
                'action': 'reorganize_imports',
                'description': '重新整理import语句的顺序和分组',
                'command': 'ruff check --select I --fix src/ tests/',
                'affected_count': len(by_category['import_issue'])
            })
        
        return recommendations
    
    def _generate_mypy_recommendations(self, issues: List[Dict]) -> List[Dict]:
        """生成MyPy问题的解决建议"""
        recommendations = []
        
        by_category = defaultdict(list)
        for issue in issues:
            by_category[issue.get('category', 'other')].append(issue)
        
        if 'missing_annotation' in by_category:
            recommendations.append({
                'tool': 'mypy',
                'category': 'missing_annotation',
                'priority': 'medium',
                'action': 'add_type_annotations',
                'description': '为缺少类型注解的函数和变量添加类型注解',
                'affected_count': len(by_category['missing_annotation']),
                'suggestion': '使用 typing 模块中的类型，如 Dict, List, Optional 等'
            })
        
        if 'type_mismatch' in by_category:
            recommendations.append({
                'tool': 'mypy',
                'category': 'type_mismatch', 
                'priority': 'high',
                'action': 'fix_type_errors',
                'description': '修复类型不匹配错误，确保变量类型一致',
                'affected_count': len(by_category['type_mismatch'])
            })
        
        return recommendations
    
    def _generate_pytest_recommendations(self, issues: List[Dict]) -> List[Dict]:
        """生成Pytest问题的解决建议"""
        recommendations = []
        
        by_category = defaultdict(list)
        for issue in issues:
            by_category[issue.get('category', 'other')].append(issue)
        
        if 'assertion_failure' in by_category:
            recommendations.append({
                'tool': 'pytest',
                'category': 'assertion_failure',
                'priority': 'high',
                'action': 'fix_test_logic',
                'description': '检查测试逻辑，确保断言条件正确',
                'affected_count': len(by_category['assertion_failure'])
            })
        
        if 'import_error' in by_category:
            recommendations.append({
                'tool': 'pytest',
                'category': 'import_error',
                'priority': 'high',
                'action': 'fix_imports',
                'description': '修复测试文件中的导入错误，检查模块路径',
                'affected_count': len(by_category['import_error'])
            })
        
        return recommendations
    
    def _generate_bandit_recommendations(self, issues: List[Dict]) -> List[Dict]:
        """生成Bandit问题的解决建议"""
        recommendations = []
        
        if issues:
            recommendations.append({
                'tool': 'bandit',
                'category': 'security_issue',
                'priority': 'high',
                'action': 'fix_security_issues',
                'description': '修复安全漏洞，避免使用不安全的函数和模式',
                'affected_count': len(issues),
                'suggestion': '检查硬编码密码、不安全的随机数生成、SQL注入风险等'
            })
        
        return recommendations
    
    def _generate_coverage_recommendations(self, issues: List[Dict]) -> List[Dict]:
        """生成Coverage问题的解决建议"""
        recommendations = []
        
        low_coverage_files = [issue for issue in issues if issue.get('category') == 'file_coverage_low']
        
        if low_coverage_files:
            recommendations.append({
                'tool': 'coverage',
                'category': 'coverage_low',
                'priority': 'medium',
                'action': 'increase_test_coverage',
                'description': '为覆盖率低的文件添加更多测试用例',
                'affected_count': len(low_coverage_files),
                'affected_files': [issue.get('file_path') for issue in low_coverage_files]
            })
        
        return recommendations


@click.command()
@click.option("--tool", "-t", help="分析特定工具的输出 (ruff, mypy, pytest, bandit, coverage)")
@click.option("--input-file", "-i", help="输入文件路径 (工具输出或日志文件)")
@click.option("--output", "-o", help="输出分析报告的文件路径")
@click.option("--log-file", "-l", help="质量检查日志文件路径")
@click.option("--summary", "-s", is_flag=True, help="显示分析摘要")
@click.option("--recommendations", "-r", is_flag=True, help="显示解决建议")
@click.option("--project-root", "-p", help="项目根目录路径")
def main(tool, input_file, output, log_file, summary, recommendations, project_root):
    """
    🔍 CI问题智能分析器
    
    深度分析CI工具输出，提供精确的问题分类和解决方案建议。
    
    Examples:
        ci_issue_analyzer.py -l logs/quality_check.json -s
        ci_issue_analyzer.py -t ruff -i ruff_output.txt -r
        ci_issue_analyzer.py -s -r -o analysis_report.json
    """
    
    project_path = Path(project_root) if project_root else Path.cwd()
    analyzer = CIAnalyzer(project_path)
    
    click.echo("🔍 CI问题智能分析器启动")
    
    if tool and input_file:
        # 分析特定工具的输出文件
        input_path = Path(input_file)
        if not input_path.exists():
            click.echo(f"❌ 输入文件不存在: {input_file}")
            return
        
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = analyzer.analyze_tool_output(tool, content)
        click.echo(f"📊 从 {tool} 输出中检测到 {len(issues)} 个问题")
        
        if summary:
            for issue in issues[:5]:  # 显示前5个问题
                click.echo(f"  - {issue.get('severity', 'unknown').upper()}: {issue.get('message', '')}")
        
        issues_by_tool = {tool: issues}
    
    elif log_file or Path(project_path / "logs" / "quality_check.json").exists():
        # 分析质量检查日志
        log_path = Path(log_file) if log_file else project_path / "logs" / "quality_check.json"
        issues_by_tool = analyzer.analyze_quality_check_log(log_path)
        
        total_issues = sum(len(issues) for issues in issues_by_tool.values())
        click.echo(f"📊 从日志中检测到 {total_issues} 个问题，涉及 {len(issues_by_tool)} 个工具")
    
    else:
        click.echo("❌ 请指定输入文件 (-i) 或日志文件 (-l)")
        return
    
    # 生成分析报告
    if issues_by_tool:
        report = analyzer.generate_problem_analysis_report(issues_by_tool)
        
        if summary:
            click.echo("\n📋 问题摘要:")
            click.echo(f"  总问题数: {report['summary']['total_issues']}")
            click.echo(f"  严重程度分布:")
            for severity, count in report['summary']['by_severity'].items():
                click.echo(f"    {severity}: {count}")
            click.echo(f"  工具分布:")
            for tool, count in report['summary']['by_tool'].items():
                click.echo(f"    {tool}: {count}")
        
        if recommendations:
            click.echo("\n💡 解决建议:")
            for rec in report['recommendations']:
                priority = rec.get('priority', 'medium')
                description = rec.get('description', '')
                click.echo(f"  [{priority.upper()}] {description}")
                if 'command' in rec:
                    click.echo(f"    命令: {rec['command']}")
                if 'affected_count' in rec:
                    click.echo(f"    影响: {rec['affected_count']} 个问题")
        
        # 保存报告
        if output:
            output_path = Path(output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            click.echo(f"💾 分析报告已保存到: {output_path}")
    
    else:
        click.echo("ℹ️ 没有检测到CI问题")


if __name__ == "__main__":
    main() 