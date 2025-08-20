#!/usr/bin/env python3
"""
Problem Aggregator - 前置问题聚合器

在提交前本地就给出"这次提交会被拦截的所有问题清单"
"""

import argparse
import json
import subprocess
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

from .adapters.lint import LintAdapter
from .adapters.security import SecurityAdapter
from .adapters.tests import TestsAdapter


class ProblemAggregator:
    """问题聚合器主类"""
    
    def __init__(self, project_root: str = ".", config_path: Optional[str] = None):
        self.project_root = Path(project_root)
        self.config = self._load_config(config_path)
        
        # 初始化适配器
        self.lint_adapter = LintAdapter(str(self.project_root))
        self.security_adapter = SecurityAdapter(str(self.project_root))
        self.tests_adapter = TestsAdapter(str(self.project_root))
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            'culture': {
                'min_test_coverage': 80.0,
                'forbid_skipping_tests': True,
                'forbid_disabling_hooks': True,
                'forbid_debug_prints': True
            },
            'quality': {
                'max_complexity': 10,
                'max_function_length': 50
            },
            'security': {
                'forbid_hardcoded_passwords': True,
                'forbid_hardcoded_api_keys': True
            }
        }
        
        if config_path:
            config_file = Path(config_path)
        else:
            # 尝试找到配置文件
            possible_configs = [
                self.project_root / "tools" / "problem_aggregator" / "rulesets" / "culture.yml",
                self.project_root / ".aiculture" / "config.yml",
                self.project_root / "aiculture.yml"
            ]
            
            config_file = None
            for config in possible_configs:
                if config.exists():
                    config_file = config
                    break
        
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    # 合并配置
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"警告: 配置文件加载失败 {config_file}: {e}")
        
        return default_config
    
    def get_changed_files(self, base: str = "HEAD") -> List[str]:
        """获取变更的文件列表"""
        try:
            if base == "HEAD":
                # 获取暂存区的文件
                cmd = ["git", "diff", "--cached", "--name-only"]
            else:
                # 获取与指定base的差异
                cmd = ["git", "diff", base, "--name-only"]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
                # 只返回Python文件
                python_files = [f for f in files if f.endswith('.py')]
                return python_files
            else:
                print(f"警告: 获取变更文件失败: {result.stderr}")
                return []
        
        except Exception as e:
            print(f"警告: 获取变更文件失败: {e}")
            return []
    
    def aggregate_problems(self, 
                          base: str = "HEAD", 
                          files: Optional[List[str]] = None,
                          strict: bool = False) -> Dict[str, Any]:
        """聚合所有问题"""
        
        print(f"🔍 开始聚合问题检查...")
        
        # 获取要检查的文件
        if files is None:
            files = self.get_changed_files(base)
            if not files:
                print("ℹ️  没有发现变更的Python文件，检查整个项目")
                files = []
        
        all_problems = []
        
        # 1. Lint检查
        print("  📝 运行代码风格检查...")
        try:
            lint_problems = self.lint_adapter.run_ruff(files if files else None)
            all_problems.extend(lint_problems)
            print(f"     发现 {len(lint_problems)} 个代码风格问题")
        except Exception as e:
            print(f"     代码风格检查失败: {e}")
        
        # 2. 安全检查
        print("  🔒 运行安全检查...")
        try:
            security_problems = []
            bandit_problems = self.security_adapter.run_bandit(files if files else None)
            secrets_problems = self.security_adapter.run_detect_secrets(files if files else None)
            security_problems.extend(bandit_problems)
            security_problems.extend(secrets_problems)
            all_problems.extend(security_problems)
            print(f"     发现 {len(security_problems)} 个安全问题")
        except Exception as e:
            print(f"     安全检查失败: {e}")
        
        # 3. 测试检查
        print("  🧪 运行测试检查...")
        try:
            test_problems = []
            collection_problems = self.tests_adapter.collect_tests()
            coverage_problems = self.tests_adapter.get_coverage_info(
                self.config.get('culture', {}).get('min_test_coverage', 80.0)
            )
            pattern_problems = self.tests_adapter.check_test_patterns()
            
            test_problems.extend(collection_problems)
            test_problems.extend(coverage_problems)
            test_problems.extend(pattern_problems)
            all_problems.extend(test_problems)
            print(f"     发现 {len(test_problems)} 个测试问题")
        except Exception as e:
            print(f"     测试检查失败: {e}")
        
        # 4. 自定义文化规则检查
        print("  🎯 运行文化规则检查...")
        try:
            culture_problems = self._check_culture_rules(files)
            all_problems.extend(culture_problems)
            print(f"     发现 {len(culture_problems)} 个文化规则问题")
        except Exception as e:
            print(f"     文化规则检查失败: {e}")
        
        # 统计和分类
        result = self._categorize_problems(all_problems)
        result['metadata'] = {
            'base': base,
            'files_checked': len(files) if files else 'all',
            'strict_mode': strict,
            'config': self.config
        }
        
        print(f"✅ 问题聚合完成: 总计 {len(all_problems)} 个问题")
        
        return result
    
    def _check_culture_rules(self, files: List[str]) -> List[Dict[str, Any]]:
        """检查自定义文化规则"""
        problems = []
        culture_config = self.config.get('culture', {})
        
        # 检查所有Python文件（如果没有指定文件）
        if not files:
            files = list(self.project_root.rglob("*.py"))
            files = [str(f.relative_to(self.project_root)) for f in files]
        
        for file_path in files:
            full_path = self.project_root / file_path
            if not full_path.exists() or not full_path.suffix == '.py':
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                # 检查调试print语句
                if culture_config.get('forbid_debug_prints', True):
                    for i, line in enumerate(lines, 1):
                        if 'print(' in line and not line.strip().startswith('#'):
                            # 简单启发式：如果不在字符串中且不是注释
                            if not self._is_in_string_or_comment(line, 'print('):
                                problems.append({
                                    'tool': 'culture',
                                    'type': 'debug_code',
                                    'severity': 'warning',
                                    'file': file_path,
                                    'line': i,
                                    'message': '发现调试print语句',
                                    'fix_suggestion': '移除print语句或使用logging',
                                    'blocking': False
                                })
                
                # 检查跳过的测试
                if culture_config.get('forbid_skipping_tests', True) and 'test_' in file_path:
                    for i, line in enumerate(lines, 1):
                        if '@pytest.mark.skip' in line or '@unittest.skip' in line:
                            problems.append({
                                'tool': 'culture',
                                'type': 'test_quality',
                                'severity': 'warning',
                                'file': file_path,
                                'line': i,
                                'message': '发现跳过的测试',
                                'fix_suggestion': '修复测试或提供跳过原因',
                                'blocking': False
                            })
                
                # 检查TODO/FIXME
                if culture_config.get('forbid_todo_fixme', False):
                    for i, line in enumerate(lines, 1):
                        if 'TODO' in line.upper() or 'FIXME' in line.upper():
                            problems.append({
                                'tool': 'culture',
                                'type': 'code_quality',
                                'severity': 'info',
                                'file': file_path,
                                'line': i,
                                'message': '发现TODO/FIXME注释',
                                'fix_suggestion': '完成TODO项目或创建issue跟踪',
                                'blocking': False
                            })
            
            except Exception as e:
                problems.append({
                    'tool': 'culture',
                    'type': 'system',
                    'severity': 'warning',
                    'file': file_path,
                    'message': f'文件检查失败: {e}',
                    'blocking': False
                })
        
        return problems
    
    def _is_in_string_or_comment(self, line: str, target: str) -> bool:
        """简单检查目标字符串是否在字符串字面量或注释中"""
        # 这是一个简化的实现，实际应该使用AST解析
        stripped = line.strip()
        if stripped.startswith('#'):
            return True
        
        # 简单检查是否在字符串中
        in_string = False
        quote_char = None
        i = 0
        while i < len(line):
            char = line[i]
            if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char:
                    in_string = False
                    quote_char = None
            elif not in_string and line[i:i+len(target)] == target:
                return False
            i += 1
        
        return in_string
    
    def _categorize_problems(self, problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分类和统计问题"""
        categories = {
            'security': [],
            'behavior_violations': [],
            'build_blocking': [],
            'quality': [],
            'style': [],
            'system': []
        }
        
        severity_counts = {'error': 0, 'warning': 0, 'info': 0}
        blocking_count = 0
        
        for problem in problems:
            severity = problem.get('severity', 'info')
            problem_type = problem.get('type', 'unknown')
            is_blocking = problem.get('blocking', False)
            
            # 统计
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            if is_blocking:
                blocking_count += 1
            
            # 分类
            if problem_type in ['security', 'secrets']:
                categories['security'].append(problem)
            elif problem_type in ['test_failure', 'test_collection']:
                categories['build_blocking'].append(problem)
            elif problem_type in ['debug_code', 'test_quality']:
                categories['behavior_violations'].append(problem)
            elif problem_type in ['lint', 'complexity']:
                categories['quality'].append(problem)
            elif problem_type in ['style', 'formatting']:
                categories['style'].append(problem)
            else:
                categories['system'].append(problem)
        
        return {
            'problems': problems,
            'categories': categories,
            'summary': {
                'total': len(problems),
                'blocking': blocking_count,
                'by_severity': severity_counts
            }
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AICultureKit Problem Aggregator')
    parser.add_argument('--base', default='HEAD', help='Git base for diff (default: HEAD)')
    parser.add_argument('--out', help='Output JSON file path')
    parser.add_argument('--md', help='Output Markdown report path')
    parser.add_argument('--strict', action='store_true', help='Strict mode: exit with error if problems found')
    parser.add_argument('--config', help='Config file path')
    parser.add_argument('--files', nargs='*', help='Specific files to check')
    
    args = parser.parse_args()
    
    # 创建输出目录
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    if args.md:
        Path(args.md).parent.mkdir(parents=True, exist_ok=True)
    
    # 运行聚合
    aggregator = ProblemAggregator(config_path=args.config)
    result = aggregator.aggregate_problems(
        base=args.base,
        files=args.files,
        strict=args.strict
    )
    
    # 输出JSON
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"📄 JSON报告已保存到: {args.out}")
    
    # 输出Markdown
    if args.md:
        from .reporters import MarkdownReporter
        reporter = MarkdownReporter()
        markdown_content = reporter.generate_report(result)
        
        with open(args.md, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"📋 Markdown报告已保存到: {args.md}")
    
    # 显示摘要
    summary = result['summary']
    print(f"\n📊 问题摘要:")
    print(f"   总计: {summary['total']} 个问题")
    print(f"   阻塞性: {summary['blocking']} 个")
    print(f"   错误: {summary['by_severity'].get('error', 0)} 个")
    print(f"   警告: {summary['by_severity'].get('warning', 0)} 个")
    print(f"   信息: {summary['by_severity'].get('info', 0)} 个")
    
    # 退出码
    if args.strict and (summary['blocking'] > 0 or summary['by_severity'].get('error', 0) > 0):
        print("\n❌ 严格模式：发现阻塞性问题或错误")
        sys.exit(1)
    else:
        print("\n✅ 问题聚合完成")
        sys.exit(0)


if __name__ == "__main__":
    main()
