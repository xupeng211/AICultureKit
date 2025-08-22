"""
安全问题修复策略
"""

import re
from pathlib import Path
from typing import Any


class SecurityFixStrategy:
    """安全问题修复策略"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    def can_fix(self, problem: dict[str, Any]) -> bool:
        """判断是否可以修复此问题"""
        if problem.get("tool") not in ["bandit", "detect-secrets"]:
            return False

        # 只修复高置信度的安全问题
        if problem.get("tool") == "bandit":
            confidence = problem.get("confidence", "LOW")
            severity = problem.get("severity", "info")
            return confidence in ["HIGH", "MEDIUM"] and severity in ["error", "warning"]

        # detect-secrets的问题通常需要人工审查
        if problem.get("tool") == "detect-secrets":
            return False  # 暂时不自动修复密钥问题

        return False

    def generate_fix(self, problems: list[dict[str, Any]]) -> tuple[str, str, float]:
        """
        生成安全修复补丁

        Returns:
            (patch_content, explanation, confidence)
        """

        # 按文件分组问题
        problems_by_file = {}
        for problem in problems:
            if not self.can_fix(problem):
                continue

            file_path = problem.get("file", "")
            if not file_path:
                continue

            if file_path not in problems_by_file:
                problems_by_file[file_path] = []
            problems_by_file[file_path].append(problem)

        if not problems_by_file:
            return "", "没有可自动修复的安全问题", 0.0

        # 生成修复
        patch_parts = []
        explanations = []
        total_confidence = 0.0
        fix_count = 0

        for file_path, file_problems in problems_by_file.items():
            file_patch, file_explanation, file_confidence = self._fix_file_problems(
                file_path, file_problems
            )

            if file_patch:
                patch_parts.append(file_patch)
                explanations.append(f"**{file_path}**: {file_explanation}")
                total_confidence += file_confidence
                fix_count += 1

        if not patch_parts:
            return "", "无法生成有效的安全修复补丁", 0.0

        # 合并补丁
        patch_content = "\n".join(patch_parts)
        explanation = "## 安全问题自动修复\n\n" + "\n".join(explanations)
        avg_confidence = total_confidence / fix_count if fix_count > 0 else 0.0

        return patch_content, explanation, avg_confidence

    def _fix_file_problems(
        self, file_path: str, problems: list[dict[str, Any]]
    ) -> tuple[str, str, float]:
        """修复单个文件的安全问题"""

        full_path = self.project_root / file_path
        if not full_path.exists():
            return "", f"文件不存在: {file_path}", 0.0

        try:
            with open(full_path, encoding="utf-8") as f:
                original_content = f.read()
        except Exception as e:
            return "", f"读取文件失败: {e}", 0.0

        # 应用修复
        fixed_content = original_content
        applied_fixes = []

        # 按行号排序，从后往前修复避免行号偏移
        sorted_problems = sorted(problems, key=lambda p: p.get("line", 0), reverse=True)

        for problem in sorted_problems:
            fix_result = self._apply_security_fix(fixed_content, problem)
            if fix_result:
                fixed_content, fix_description = fix_result
                applied_fixes.append(fix_description)

        if fixed_content == original_content:
            return "", "没有应用任何安全修复", 0.0

        # 生成patch
        patch_content = self._generate_patch(file_path, original_content, fixed_content)
        explanation = f"修复了 {len(applied_fixes)} 个安全问题: {', '.join(applied_fixes)}"
        confidence = 0.6  # 安全修复的置信度相对较低，需要人工审查

        return patch_content, explanation, confidence

    def _apply_security_fix(self, content: str, problem: dict[str, Any]) -> tuple[str, str] | None:
        """应用单个安全修复"""

        if problem.get("tool") != "bandit":
            return None

        test_id = problem.get("code", "")
        line_num = problem.get("line", 0)

        lines = content.split("\n")
        if line_num <= 0 or line_num > len(lines):
            return None

        line_idx = line_num - 1
        original_line = lines[line_idx]

        # 根据bandit测试ID应用修复
        if test_id == "B101":  # assert语句
            # 将assert替换为适当的异常或logging
            if "assert " in original_line:
                indent = len(original_line) - len(original_line.lstrip())
                indent_str = " " * indent

                # 提取assert条件
                assert_match = re.search(r"assert\s+(.+?)(?:\s*,\s*(.+))?$", original_line.strip())
                if assert_match:
                    condition = assert_match.group(1)
                    message = assert_match.group(2) or f'"{condition} failed"'

                    # 替换为if语句和异常
                    new_lines = [
                        f"{indent_str}if not ({condition}):",
                        f"{indent_str}    raise ValueError({message})",
                    ]

                    lines[line_idx : line_idx + 1] = new_lines
                    return "\n".join(lines), "B101: 将assert替换为异常检查"

        elif test_id == "B102":  # exec使用
            if "exec(" in original_line:
                # 添加警告注释
                indent = len(original_line) - len(original_line.lstrip())
                indent_str = " " * indent

                warning_comment = (
                    f"{indent_str}# WARNING: exec() usage detected - consider safer alternatives"
                )
                lines.insert(line_idx, warning_comment)
                return "\n".join(lines), "B102: 为exec()使用添加安全警告"

        elif test_id == "B108":  # 临时文件创建不安全
            if "tempfile.mktemp" in original_line:
                # 替换为更安全的tempfile.mkstemp
                new_line = original_line.replace("tempfile.mktemp", "tempfile.mkstemp")
                lines[line_idx] = new_line
                return "\n".join(lines), "B108: 使用更安全的tempfile.mkstemp"

        elif test_id == "B311":  # 不安全的随机数
            if "random." in original_line and any(
                func in original_line for func in ["random()", "randint(", "choice("]
            ):
                # 添加导入secrets模块的建议注释
                indent = len(original_line) - len(original_line.lstrip())
                indent_str = " " * indent

                warning_comment = f"{indent_str}# SECURITY: Consider using 'secrets' module for cryptographic randomness"
                lines.insert(line_idx, warning_comment)
                return "\n".join(lines), "B311: 添加安全随机数使用建议"

        elif test_id == "B324":  # 不安全的哈希算法
            if any(hash_func in original_line for hash_func in ["md5()", "sha1()"]):
                # 建议使用更安全的哈希算法
                indent = len(original_line) - len(original_line.lstrip())
                indent_str = " " * indent

                warning_comment = (
                    f"{indent_str}# SECURITY: Consider using SHA-256 or stronger hash algorithms"
                )
                lines.insert(line_idx, warning_comment)
                return "\n".join(lines), "B324: 添加安全哈希算法建议"

        elif test_id == "B501":  # 未验证SSL证书
            if "verify=False" in original_line or "ssl._create_unverified_context" in original_line:
                # 添加SSL验证警告
                indent = len(original_line) - len(original_line.lstrip())
                indent_str = " " * indent

                warning_comment = f"{indent_str}# SECURITY: SSL certificate verification disabled - ensure this is intentional"
                lines.insert(line_idx, warning_comment)
                return "\n".join(lines), "B501: 添加SSL验证警告"

        elif test_id == "B601" or test_id == "B602":  # shell注入风险
            if "shell=True" in original_line:
                # 建议使用shell=False
                indent = len(original_line) - len(original_line.lstrip())
                indent_str = " " * indent

                warning_comment = f"{indent_str}# SECURITY: shell=True may be vulnerable to injection - validate inputs"
                lines.insert(line_idx, warning_comment)
                return "\n".join(lines), f"{test_id}: 添加shell注入风险警告"

        return None

    def _generate_patch(self, file_path: str, original: str, fixed: str) -> str:
        """生成Git patch格式"""

        # 使用简单的diff格式
        orig_lines = original.split("\n")
        fixed_lines = fixed.split("\n")

        patch_lines = [
            f"--- a/{file_path}",
            f"+++ b/{file_path}",
            f"@@ -1,{len(orig_lines)} +1,{len(fixed_lines)} @@",
        ]

        # 简单的逐行比较
        max_lines = max(len(orig_lines), len(fixed_lines))

        for i in range(max_lines):
            orig_line = orig_lines[i] if i < len(orig_lines) else None
            fixed_line = fixed_lines[i] if i < len(fixed_lines) else None

            if orig_line is None:
                patch_lines.append(f"+{fixed_line}")
            elif fixed_line is None:
                patch_lines.append(f"-{orig_line}")
            elif orig_line != fixed_line:
                patch_lines.append(f"-{orig_line}")
                patch_lines.append(f"+{fixed_line}")
            else:
                patch_lines.append(f" {orig_line}")

        return "\n".join(patch_lines)

    def generate_manual_guide(self, problems: list[dict[str, Any]]) -> str:
        """为无法自动修复的问题生成手工修复指南"""

        guides = []
        guides.append("# 安全问题手工修复指南\n")

        # 按问题类型分组
        problems_by_type = {}
        for problem in problems:
            if problem.get("tool") == "detect-secrets":
                problem_type = "secrets"
            elif problem.get("tool") == "bandit":
                problem_type = problem.get("code", "unknown")
            else:
                continue

            if problem_type not in problems_by_type:
                problems_by_type[problem_type] = []
            problems_by_type[problem_type].append(problem)

        # 生成各类型的修复指南
        for problem_type, type_problems in problems_by_type.items():
            if problem_type == "secrets":
                guides.append(self._generate_secrets_guide(type_problems))
            else:
                guides.append(self._generate_bandit_guide(problem_type, type_problems))

        return "\n".join(guides)

    def _generate_secrets_guide(self, problems: list[dict[str, Any]]) -> str:
        """生成密钥问题修复指南"""

        guide = ["## 🔑 密钥泄漏修复指南\n"]

        for i, problem in enumerate(problems, 1):
            file_path = problem.get("file", "unknown")
            line_num = problem.get("line", 0)
            secret_type = problem.get("code", "unknown")

            guide.append(f"### {i}. {file_path}:{line_num} - {secret_type}")
            guide.append("")
            guide.append("**修复步骤:**")
            guide.append("1. 确认是否为真实密钥（可能是误报）")
            guide.append("2. 如果是真实密钥：")
            guide.append("   - 立即撤销/更换密钥")
            guide.append("   - 将密钥移至环境变量或配置文件")
            guide.append("   - 添加配置文件到.gitignore")
            guide.append("3. 如果是误报：")
            guide.append("   - 添加到.secrets.baseline文件")
            guide.append("   - 或修改代码避免触发检测")
            guide.append("")
            guide.append("**示例代码:**")
            guide.append("```python")
            guide.append("# 不安全的做法")
            guide.append("API_KEY = 'sk-1234567890abcdef'")
            guide.append("")
            guide.append("# 安全的做法")
            guide.append("import os")
            guide.append("API_KEY = os.getenv('API_KEY')")
            guide.append("```")
            guide.append("")

        return "\n".join(guide)

    def _generate_bandit_guide(self, test_id: str, problems: list[dict[str, Any]]) -> str:
        """生成bandit问题修复指南"""

        guide = [f"## 🛡️ {test_id} 安全问题修复指南\n"]

        # 根据测试ID提供具体指导
        if test_id == "B105" or test_id == "B106" or test_id == "B107":
            guide.append("**问题**: 硬编码密码")
            guide.append("**修复方法**: 使用环境变量或配置文件存储密码")
        elif test_id == "B301":
            guide.append("**问题**: 使用pickle模块存在安全风险")
            guide.append("**修复方法**: 考虑使用JSON或其他安全的序列化方式")
        elif test_id == "B601" or test_id == "B602":
            guide.append("**问题**: shell注入风险")
            guide.append("**修复方法**: 避免使用shell=True，或严格验证输入")
        else:
            guide.append(f"**问题**: {test_id} 安全风险")
            guide.append("**修复方法**: 请参考bandit文档获取具体修复建议")

        guide.append("")
        guide.append("**受影响的文件:**")

        for problem in problems:
            file_path = problem.get("file", "unknown")
            line_num = problem.get("line", 0)
            message = problem.get("message", "")
            guide.append(f"- {file_path}:{line_num} - {message}")

        guide.append("")

        return "\n".join(guide)


def main():
    """测试函数"""
    strategy = SecurityFixStrategy()

    # 测试问题
    test_problems = [
        {
            "tool": "bandit",
            "code": "B101",
            "file": "test.py",
            "line": 10,
            "message": "Use of assert detected",
            "confidence": "HIGH",
            "severity": "warning",
        }
    ]

    patch, explanation, confidence = strategy.generate_fix(test_problems)
    print(f"Patch:\n{patch}")
    print(f"Explanation: {explanation}")
    print(f"Confidence: {confidence}")

    # 测试手工指南
    guide = strategy.generate_manual_guide(test_problems)
    print(f"\nManual Guide:\n{guide}")


if __name__ == "__main__":
    main()
