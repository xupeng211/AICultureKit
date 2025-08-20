"""
增量覆盖率适配器 - 使用diff-cover检查变更行覆盖率
"""

import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class DiffCoverageAdapter:
    """增量覆盖率适配器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
    
    def check_diff_coverage(self, 
                          base_branch: str = "origin/main",
                          changed_lines_threshold: float = 80.0,
                          new_files_threshold: float = 70.0) -> List[Dict[str, Any]]:
        """检查增量覆盖率"""
        
        problems = []
        
        # 1. 运行测试并生成覆盖率报告
        coverage_xml = self._generate_coverage_report()
        if not coverage_xml:
            problems.append({
                'tool': 'diff-cover',
                'type': 'coverage_setup',
                'severity': 'error',
                'message': '无法生成覆盖率报告',
                'fix_suggestion': '确保安装了pytest-cov并且测试可以运行',
                'blocking': True
            })
            return problems
        
        # 2. 运行diff-cover检查变更行覆盖率
        diff_problems = self._run_diff_cover(coverage_xml, base_branch, changed_lines_threshold)
        problems.extend(diff_problems)
        
        # 3. 检查新文件覆盖率
        new_file_problems = self._check_new_files_coverage(coverage_xml, base_branch, new_files_threshold)
        problems.extend(new_file_problems)
        
        return problems
    
    def _generate_coverage_report(self) -> Optional[Path]:
        """生成覆盖率XML报告"""
        
        try:
            # 运行pytest生成覆盖率报告
            cmd = [
                "python", "-m", "pytest", 
                "-q", "--maxfail=1", "--disable-warnings",
                "--cov=aiculture", "--cov=tools",
                "--cov-report=xml:coverage.xml",
                "--cov-report=term-missing"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            coverage_xml = self.project_root / "coverage.xml"
            if coverage_xml.exists():
                return coverage_xml
            else:
                print(f"覆盖率报告生成失败: {result.stderr}")
                return None
        
        except subprocess.TimeoutExpired:
            print("覆盖率报告生成超时")
            return None
        except Exception as e:
            print(f"覆盖率报告生成异常: {e}")
            return None
    
    def _run_diff_cover(self, coverage_xml: Path, base_branch: str, threshold: float) -> List[Dict[str, Any]]:
        """运行diff-cover检查"""
        
        problems = []
        
        try:
            cmd = [
                "diff-cover", str(coverage_xml),
                f"--compare-branch={base_branch}",
                f"--fail-under={threshold}",
                "--json-report", "diff_coverage_report.json"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # 解析diff-cover输出
            if result.returncode != 0:
                # diff-cover失败，解析详细信息
                problems.extend(self._parse_diff_cover_output(result.stdout, result.stderr, threshold))
            
            # 尝试读取JSON报告
            json_report = self.project_root / "diff_coverage_report.json"
            if json_report.exists():
                try:
                    with open(json_report, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                    problems.extend(self._parse_diff_cover_json(report_data, threshold))
                except Exception as e:
                    print(f"解析diff-cover JSON报告失败: {e}")
        
        except subprocess.TimeoutExpired:
            problems.append({
                'tool': 'diff-cover',
                'type': 'coverage_timeout',
                'severity': 'error',
                'message': 'diff-cover检查超时',
                'blocking': False
            })
        except Exception as e:
            problems.append({
                'tool': 'diff-cover',
                'type': 'coverage_error',
                'severity': 'warning',
                'message': f'diff-cover检查失败: {e}',
                'blocking': False
            })
        
        return problems
    
    def _parse_diff_cover_output(self, stdout: str, stderr: str, threshold: float) -> List[Dict[str, Any]]:
        """解析diff-cover文本输出"""
        
        problems = []
        
        # 解析覆盖率信息
        lines = stdout.split('\n') + stderr.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 查找覆盖率不足的信息
            if 'Diff Coverage:' in line:
                # 提取覆盖率百分比
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.endswith('%'):
                            coverage_str = part.rstrip('%')
                            current_coverage = float(coverage_str)
                            
                            if current_coverage < threshold:
                                problems.append({
                                    'tool': 'diff-cover',
                                    'type': 'diff_coverage',
                                    'severity': 'error',
                                    'message': f'变更行覆盖率不足: {current_coverage:.1f}% < {threshold}%',
                                    'fix_suggestion': f'需要为变更的代码添加测试，提升覆盖率到{threshold}%以上',
                                    'blocking': True,
                                    'metadata': {
                                        'current_coverage': current_coverage,
                                        'required_coverage': threshold,
                                        'coverage_gap': threshold - current_coverage
                                    }
                                })
                            break
                except (ValueError, IndexError):
                    continue
            
            # 查找未覆盖的文件
            elif line.startswith('Missing coverage') or 'not covered' in line.lower():
                problems.append({
                    'tool': 'diff-cover',
                    'type': 'missing_coverage',
                    'severity': 'warning',
                    'message': f'发现未覆盖的变更: {line}',
                    'fix_suggestion': '为变更的代码添加相应的测试用例',
                    'blocking': False
                })
        
        return problems
    
    def _parse_diff_cover_json(self, report_data: Dict[str, Any], threshold: float) -> List[Dict[str, Any]]:
        """解析diff-cover JSON报告"""
        
        problems = []
        
        try:
            # 获取总体覆盖率
            diff_coverage = report_data.get('diff_coverage_percent', 0)
            
            if diff_coverage < threshold:
                problems.append({
                    'tool': 'diff-cover',
                    'type': 'diff_coverage',
                    'severity': 'error',
                    'message': f'变更行覆盖率不足: {diff_coverage:.1f}% < {threshold}%',
                    'fix_suggestion': f'需要为变更的代码添加测试，提升覆盖率到{threshold}%以上',
                    'blocking': True,
                    'metadata': {
                        'current_coverage': diff_coverage,
                        'required_coverage': threshold,
                        'coverage_gap': threshold - diff_coverage
                    }
                })
            
            # 解析文件级别的覆盖率
            files_data = report_data.get('src_stats', {})
            for file_path, file_stats in files_data.items():
                file_coverage = file_stats.get('percent_covered', 0)
                
                if file_coverage < threshold * 0.8:  # 文件覆盖率低于80%阈值
                    problems.append({
                        'tool': 'diff-cover',
                        'type': 'file_diff_coverage',
                        'severity': 'warning',
                        'file': file_path,
                        'message': f'文件变更覆盖率过低: {file_coverage:.1f}%',
                        'fix_suggestion': '为此文件的变更添加更多测试用例',
                        'blocking': False,
                        'metadata': {
                            'file_coverage': file_coverage,
                            'num_statements': file_stats.get('num_statements', 0),
                            'missing_lines': file_stats.get('missing_lines', [])
                        }
                    })
        
        except Exception as e:
            problems.append({
                'tool': 'diff-cover',
                'type': 'report_parsing',
                'severity': 'warning',
                'message': f'解析diff-cover报告失败: {e}',
                'blocking': False
            })
        
        return problems
    
    def _check_new_files_coverage(self, coverage_xml: Path, base_branch: str, threshold: float) -> List[Dict[str, Any]]:
        """检查新文件的覆盖率"""
        
        problems = []
        
        try:
            # 获取新增文件列表
            new_files = self._get_new_files(base_branch)
            
            if not new_files:
                return problems
            
            # 解析覆盖率XML
            tree = ET.parse(coverage_xml)
            root = tree.getroot()
            
            for new_file in new_files:
                if not new_file.endswith('.py'):
                    continue
                
                # 查找文件的覆盖率信息
                file_coverage = self._get_file_coverage_from_xml(root, new_file)
                
                if file_coverage is not None and file_coverage < threshold:
                    problems.append({
                        'tool': 'diff-cover',
                        'type': 'new_file_coverage',
                        'severity': 'error',
                        'file': new_file,
                        'message': f'新文件覆盖率不足: {file_coverage:.1f}% < {threshold}%',
                        'fix_suggestion': f'为新文件添加测试，提升覆盖率到{threshold}%以上',
                        'blocking': True,
                        'metadata': {
                            'file_coverage': file_coverage,
                            'required_coverage': threshold,
                            'is_new_file': True
                        }
                    })
        
        except Exception as e:
            problems.append({
                'tool': 'diff-cover',
                'type': 'new_file_check',
                'severity': 'warning',
                'message': f'新文件覆盖率检查失败: {e}',
                'blocking': False
            })
        
        return problems
    
    def _get_new_files(self, base_branch: str) -> List[str]:
        """获取相对于基准分支的新增文件"""
        
        try:
            cmd = ["git", "diff", "--name-only", "--diff-filter=A", base_branch]
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.split('\n') if f.strip()]
            else:
                return []
        
        except Exception:
            return []
    
    def _get_file_coverage_from_xml(self, root: ET.Element, file_path: str) -> Optional[float]:
        """从XML中获取文件覆盖率"""
        
        try:
            # 查找匹配的文件
            for package in root.findall('.//package'):
                for class_elem in package.findall('.//class'):
                    filename = class_elem.get('filename', '')
                    
                    # 匹配文件路径
                    if filename.endswith(file_path) or file_path.endswith(filename):
                        line_rate = float(class_elem.get('line-rate', 0))
                        return line_rate * 100
            
            return None
        
        except Exception:
            return None
    
    def generate_coverage_improvement_guide(self, problems: List[Dict[str, Any]]) -> str:
        """生成覆盖率改进指南"""
        
        guide = []
        guide.append("# 增量覆盖率改进指南\n")
        
        # 按问题类型分组
        diff_coverage_problems = [p for p in problems if p.get('type') == 'diff_coverage']
        file_problems = [p for p in problems if p.get('type') in ['file_diff_coverage', 'new_file_coverage']]
        
        if diff_coverage_problems:
            guide.append("## 🎯 变更行覆盖率不足\n")
            
            for problem in diff_coverage_problems:
                metadata = problem.get('metadata', {})
                current = metadata.get('current_coverage', 0)
                required = metadata.get('required_coverage', 80)
                gap = metadata.get('coverage_gap', 0)
                
                guide.append(f"**当前覆盖率**: {current:.1f}%")
                guide.append(f"**要求覆盖率**: {required}%")
                guide.append(f"**覆盖率缺口**: {gap:.1f}%")
                guide.append("")
                guide.append("**改进建议**:")
                guide.append("1. 运行 `diff-cover coverage.xml --compare-branch=origin/main --html-report diff_coverage.html`")
                guide.append("2. 打开 diff_coverage.html 查看具体未覆盖的行")
                guide.append("3. 为未覆盖的变更行添加测试用例")
                guide.append("4. 重新运行测试验证覆盖率提升")
                guide.append("")
        
        if file_problems:
            guide.append("## 📁 文件级覆盖率问题\n")
            
            for problem in file_problems:
                file_path = problem.get('file', 'unknown')
                metadata = problem.get('metadata', {})
                file_coverage = metadata.get('file_coverage', 0)
                
                guide.append(f"### {file_path}")
                guide.append(f"- **当前覆盖率**: {file_coverage:.1f}%")
                
                if problem.get('type') == 'new_file_coverage':
                    guide.append("- **文件类型**: 新增文件")
                    guide.append("- **建议**: 为新文件创建完整的测试套件")
                else:
                    guide.append("- **文件类型**: 变更文件")
                    guide.append("- **建议**: 为变更的代码路径添加测试")
                
                missing_lines = metadata.get('missing_lines', [])
                if missing_lines:
                    guide.append(f"- **未覆盖行数**: {len(missing_lines)}")
                
                guide.append("")
        
        # 通用改进建议
        guide.append("## 🛠️ 通用改进策略\n")
        guide.append("### 1. 识别未覆盖代码")
        guide.append("```bash")
        guide.append("# 生成详细的覆盖率报告")
        guide.append("pytest --cov=aiculture --cov=tools --cov-report=html:htmlcov")
        guide.append("# 打开 htmlcov/index.html 查看详细报告")
        guide.append("```")
        guide.append("")
        guide.append("### 2. 针对性添加测试")
        guide.append("- **单元测试**: 测试单个函数/方法")
        guide.append("- **集成测试**: 测试组件间交互")
        guide.append("- **边界测试**: 测试边界条件和异常情况")
        guide.append("")
        guide.append("### 3. 使用测试脚手架")
        guide.append("```bash")
        guide.append("# 使用AI生成测试脚手架")
        guide.append("python -m tools.ai_fix_agent.agent --in artifacts/problems.json --out artifacts/ai_fixes")
        guide.append("# 应用测试脚手架补丁")
        guide.append("git apply artifacts/ai_fixes/test_scaffold.patch")
        guide.append("```")
        guide.append("")
        
        return '\n'.join(guide)


def main():
    """测试函数"""
    adapter = DiffCoverageAdapter()
    
    print("检查增量覆盖率...")
    problems = adapter.check_diff_coverage(
        base_branch="origin/main",
        changed_lines_threshold=80.0,
        new_files_threshold=70.0
    )
    
    print(f"发现 {len(problems)} 个覆盖率问题")
    for problem in problems:
        print(f"  {problem['severity']}: {problem['message']}")
    
    if problems:
        guide = adapter.generate_coverage_improvement_guide(problems)
        print(f"\n改进指南:\n{guide}")


if __name__ == "__main__":
    main()
