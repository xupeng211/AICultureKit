"""
Security adapter for bandit and detect-secrets
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional


class SecurityAdapter:
    """安全检查适配器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
    
    def run_bandit(self, files: List[str] = None) -> List[Dict[str, Any]]:
        """运行bandit安全检查"""
        problems = []
        
        try:
            cmd = ["python", "-m", "bandit", "-f", "json", "-r"]
            if files:
                cmd.extend(files)
            else:
                cmd.append(".")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.stdout:
                try:
                    bandit_report = json.loads(result.stdout)
                    results = bandit_report.get('results', [])
                    
                    for issue in results:
                        problems.append({
                            'tool': 'bandit',
                            'type': 'security',
                            'severity': self._map_bandit_severity(issue.get('issue_severity', 'LOW')),
                            'file': issue.get('filename', ''),
                            'line': issue.get('line_number', 0),
                            'column': 0,
                            'code': issue.get('test_id', ''),
                            'message': issue.get('issue_text', ''),
                            'confidence': issue.get('issue_confidence', 'UNDEFINED'),
                            'fix_suggestion': self._get_bandit_fix_suggestion(issue),
                            'blocking': self._is_blocking_security_issue(issue)
                        })
                
                except json.JSONDecodeError:
                    # bandit可能输出非JSON格式的错误信息
                    if result.stderr:
                        problems.append({
                            'tool': 'bandit',
                            'type': 'system',
                            'severity': 'warning',
                            'message': f'Bandit输出解析失败: {result.stderr[:200]}',
                            'blocking': False
                        })
        
        except subprocess.TimeoutExpired:
            problems.append({
                'tool': 'bandit',
                'type': 'system',
                'severity': 'error',
                'message': 'Bandit检查超时',
                'blocking': False
            })
        except FileNotFoundError:
            problems.append({
                'tool': 'bandit',
                'type': 'system',
                'severity': 'info',
                'message': 'Bandit未安装，跳过安全检查',
                'blocking': False
            })
        except Exception as e:
            problems.append({
                'tool': 'bandit',
                'type': 'system',
                'severity': 'warning',
                'message': f'Bandit检查失败: {e}',
                'blocking': False
            })
        
        return problems
    
    def run_detect_secrets(self, files: List[str] = None) -> List[Dict[str, Any]]:
        """运行detect-secrets检查"""
        problems = []
        
        try:
            # 首先尝试扫描
            cmd = ["detect-secrets", "scan", "--all-files"]
            if files:
                for file in files:
                    cmd.extend(["--files", file])
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                try:
                    secrets_report = json.loads(result.stdout)
                    results = secrets_report.get('results', {})
                    
                    for filename, secrets in results.items():
                        for secret in secrets:
                            problems.append({
                                'tool': 'detect-secrets',
                                'type': 'security',
                                'severity': 'high',
                                'file': filename,
                                'line': secret.get('line_number', 0),
                                'column': 0,
                                'code': secret.get('type', 'SECRET'),
                                'message': f'检测到潜在密钥: {secret.get("type", "未知类型")}',
                                'fix_suggestion': '移除硬编码密钥，使用环境变量或配置文件',
                                'blocking': True
                            })
                
                except json.JSONDecodeError:
                    if "No secrets were detected" not in result.stdout:
                        problems.append({
                            'tool': 'detect-secrets',
                            'type': 'system',
                            'severity': 'warning',
                            'message': 'Detect-secrets输出解析失败',
                            'blocking': False
                        })
        
        except FileNotFoundError:
            problems.append({
                'tool': 'detect-secrets',
                'type': 'system',
                'severity': 'info',
                'message': 'Detect-secrets未安装，跳过密钥检查',
                'blocking': False
            })
        except Exception as e:
            problems.append({
                'tool': 'detect-secrets',
                'type': 'system',
                'severity': 'warning',
                'message': f'Detect-secrets检查失败: {e}',
                'blocking': False
            })
        
        return problems
    
    def _map_bandit_severity(self, severity: str) -> str:
        """映射bandit严重度"""
        mapping = {
            'HIGH': 'error',
            'MEDIUM': 'warning',
            'LOW': 'info'
        }
        return mapping.get(severity.upper(), 'warning')
    
    def _get_bandit_fix_suggestion(self, issue: Dict[str, Any]) -> str:
        """获取bandit修复建议"""
        test_id = issue.get('test_id', '')
        
        suggestions = {
            'B101': '移除assert语句或使用logging',
            'B102': '避免使用exec()函数',
            'B103': '设置适当的文件权限',
            'B104': '绑定到所有接口存在安全风险',
            'B105': '硬编码密码存在安全风险',
            'B106': '硬编码密码存在安全风险',
            'B107': '硬编码密码存在安全风险',
            'B108': '临时文件创建不安全',
            'B110': 'try-except-pass可能隐藏错误',
            'B112': 'try-except-continue可能隐藏错误',
            'B201': 'Flask debug模式不应在生产环境使用',
            'B301': 'pickle模块存在安全风险',
            'B302': 'marshal模块存在安全风险',
            'B303': 'MD5哈希算法不安全',
            'B304': 'DES加密算法不安全',
            'B305': 'RC4加密算法不安全',
            'B306': 'mktemp函数不安全',
            'B307': 'eval()函数存在安全风险',
            'B308': 'mark_safe()可能导致XSS',
            'B309': 'HTTPSConnection未验证证书',
            'B310': 'urllib.urlopen存在安全风险',
            'B311': '使用random模块生成密码不安全',
            'B312': 'telnetlib模块不安全',
            'B313': 'xml.etree.ElementTree易受XXE攻击',
            'B314': 'xml.etree.cElementTree易受XXE攻击',
            'B315': 'xml.expat易受XXE攻击',
            'B316': 'xml.sax易受XXE攻击',
            'B317': 'xml.dom.minidom易受XXE攻击',
            'B318': 'xml.dom.pulldom易受XXE攻击',
            'B319': 'lxml易受XXE攻击',
            'B320': 'xmlrpclib易受XXE攻击',
            'B321': 'ftplib.FTP不安全',
            'B322': 'input()函数在Python2中不安全',
            'B323': 'unverified HTTPS请求',
            'B324': 'hashlib.new()使用不安全算法',
            'B325': 'tempfile.mktemp()不安全',
            'B501': '请求未验证SSL证书',
            'B502': 'SSL/TLS配置不安全',
            'B503': 'SSL/TLS配置不安全',
            'B504': 'SSL/TLS配置不安全',
            'B505': 'SSL/TLS配置不安全',
            'B506': 'YAML load()不安全',
            'B507': 'SSH主机密钥未验证',
            'B601': 'shell注入风险',
            'B602': 'subprocess shell注入风险',
            'B603': 'subprocess未验证输入',
            'B604': '函数调用存在shell注入风险',
            'B605': '启动进程存在shell注入风险',
            'B606': '启动进程未验证输入',
            'B607': '启动进程存在部分路径遍历风险',
            'B608': 'SQL注入风险',
            'B609': 'Linux命令通配符注入',
            'B610': 'Django SQL注入风险',
            'B611': 'Django SQL注入风险',
            'B701': 'jinja2模板自动转义关闭',
            'B702': 'Mako模板默认过滤器关闭',
            'B703': 'Django标记为安全但可能不安全'
        }
        
        return suggestions.get(test_id, f'参考bandit文档修复安全问题: {test_id}')
    
    def _is_blocking_security_issue(self, issue: Dict[str, Any]) -> bool:
        """判断是否为阻塞性安全问题"""
        severity = issue.get('issue_severity', 'LOW')
        confidence = issue.get('issue_confidence', 'LOW')
        test_id = issue.get('test_id', '')
        
        # 高严重度且高置信度的问题阻塞
        if severity == 'HIGH' and confidence in ['HIGH', 'MEDIUM']:
            return True
        
        # 特定的严重安全问题
        critical_tests = [
            'B105', 'B106', 'B107',  # 硬编码密码
            'B102',  # exec使用
            'B301',  # pickle使用
            'B501',  # 未验证SSL
            'B601', 'B602',  # shell注入
            'B608',  # SQL注入
        ]
        
        return test_id in critical_tests


def main():
    """测试函数"""
    adapter = SecurityAdapter()
    
    print("运行bandit检查...")
    bandit_problems = adapter.run_bandit()
    print(f"发现 {len(bandit_problems)} 个bandit问题")
    
    print("运行detect-secrets检查...")
    secrets_problems = adapter.run_detect_secrets()
    print(f"发现 {len(secrets_problems)} 个密钥问题")
    
    all_problems = bandit_problems + secrets_problems
    blocking_problems = [p for p in all_problems if p.get('blocking', False)]
    
    print(f"总计: {len(all_problems)} 个安全问题，其中 {len(blocking_problems)} 个阻塞性问题")


if __name__ == "__main__":
    main()
