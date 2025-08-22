"""
安全代码修改策略
处理常见的安全问题：subprocess shell=True、hashlib.md5、requests verify=False等
"""

import re
from typing import Any, Dict, List

from ..utils import create_patch


class SecurityCodeModStrategy:
    """安全代码修改策略"""

    def __init__(self):
        self.name = "security_codemods"
        self.description = "修复常见安全问题"

        # 安全修复规则
        self.rules = [
            {
                "name": "subprocess_shell_true",
                "pattern": r"subprocess\.(run|call|check_call|check_output|Popen)\([^)]*shell\s*=\s*True",
                "confidence": "medium",
                "description": "subprocess调用使用shell=True存在安全风险",
            },
            {
                "name": "hashlib_md5",
                "pattern": r"hashlib\.md5\(",
                "confidence": "high",
                "description": "MD5哈希算法不安全，建议使用SHA-256",
            },
            {
                "name": "requests_verify_false",
                "pattern": r"requests\.(get|post|put|delete|patch|head|options)\([^)]*verify\s*=\s*False",
                "confidence": "high",
                "description": "requests禁用SSL验证存在安全风险",
            },
            {
                "name": "eval_usage",
                "pattern": r"\beval\s*\(",
                "confidence": "high",
                "description": "eval()函数存在代码注入风险",
            },
            {
                "name": "exec_usage",
                "pattern": r"\bexec\s*\(",
                "confidence": "high",
                "description": "exec()函数存在代码注入风险",
            },
            {
                "name": "pickle_load",
                "pattern": r"pickle\.loads?\(",
                "confidence": "medium",
                "description": "pickle反序列化存在安全风险",
            },
        ]

    def can_fix(self, file_path: str, content: str) -> bool:
        """判断是否可以修复该文件"""
        return file_path.endswith(".py") and content.strip()

    def analyze_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """分析文件中的安全问题"""

        issues = []
        lines = content.split("\n")

        for rule in self.rules:
            pattern = re.compile(rule["pattern"])

            for line_num, line in enumerate(lines, 1):
                matches = pattern.finditer(line)
                for match in matches:
                    issues.append(
                        {
                            "rule": rule["name"],
                            "line_num": line_num,
                            "line_content": line.strip(),
                            "match_text": match.group(),
                            "confidence": rule["confidence"],
                            "description": rule["description"],
                            "start_pos": match.start(),
                            "end_pos": match.end(),
                        }
                    )

        return issues

    def fix_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """修复单个文件的安全问题"""

        result = {
            "success": False,
            "original_content": content,
            "fixed_content": content,
            "changes": [],
            "todos": [],
            "errors": [],
        }

        try:
            issues = self.analyze_file(file_path, content)
            if not issues:
                result["success"] = True
                result["changes"].append("无安全问题需要修复")
                return result

            fixed_content = content
            changes_made = []
            todos_added = []

            # 按行号倒序处理，避免位置偏移
            issues.sort(key=lambda x: x["line_num"], reverse=True)

            for issue in issues:
                fix_result = self._apply_fix(fixed_content, issue)
                if fix_result["applied"]:
                    fixed_content = fix_result["content"]
                    changes_made.append(fix_result["description"])
                else:
                    todos_added.append(fix_result["todo"])

            if changes_made or todos_added:
                result["fixed_content"] = fixed_content
                result["changes"] = changes_made
                result["todos"] = todos_added
                result["success"] = True
            else:
                result["success"] = True
                result["changes"].append("发现安全问题但无法自动修复")

        except Exception as e:
            result["errors"].append(f"处理文件时出错: {str(e)}")

        return result

    def _apply_fix(self, content: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """应用具体的安全修复"""

        lines = content.split("\n")
        line_idx = issue["line_num"] - 1

        if line_idx >= len(lines):
            return {
                "applied": False,
                "content": content,
                "todo": f"行号超出范围: {issue['line_num']}",
            }

        original_line = lines[line_idx]

        # 根据规则类型应用修复
        if issue["rule"] == "hashlib_md5":
            return self._fix_hashlib_md5(content, lines, line_idx, issue)
        elif issue["rule"] == "requests_verify_false":
            return self._fix_requests_verify(content, lines, line_idx, issue)
        elif issue["rule"] == "subprocess_shell_true":
            return self._fix_subprocess_shell(content, lines, line_idx, issue)
        else:
            # 低置信度或复杂问题，添加TODO
            return self._add_security_todo(content, lines, line_idx, issue)

    def _fix_hashlib_md5(
        self, content: str, lines: List[str], line_idx: int, issue: Dict[str, Any]
    ) -> Dict[str, Any]:
        """修复hashlib.md5使用"""

        if issue["confidence"] == "high":
            # 高置信度：直接替换为sha256
            new_line = lines[line_idx].replace("hashlib.md5(", "hashlib.sha256(")
            lines[line_idx] = new_line

            return {
                "applied": True,
                "content": "\n".join(lines),
                "description": f"第{issue['line_num']}行: 将MD5替换为SHA-256",
            }
        else:
            return self._add_security_todo(content, lines, line_idx, issue)

    def _fix_requests_verify(
        self, content: str, lines: List[str], line_idx: int, issue: Dict[str, Any]
    ) -> Dict[str, Any]:
        """修复requests verify=False"""

        if issue["confidence"] == "high":
            # 高置信度：移除verify=False参数
            new_line = re.sub(r",?\s*verify\s*=\s*False", "", lines[line_idx])
            lines[line_idx] = new_line

            return {
                "applied": True,
                "content": "\n".join(lines),
                "description": f"第{issue['line_num']}行: 移除verify=False参数",
            }
        else:
            return self._add_security_todo(content, lines, line_idx, issue)

    def _fix_subprocess_shell(
        self, content: str, lines: List[str], line_idx: int, issue: Dict[str, Any]
    ) -> Dict[str, Any]:
        """修复subprocess shell=True"""

        # subprocess shell=True比较复杂，通常需要手工处理
        return self._add_security_todo(content, lines, line_idx, issue)

    def _add_security_todo(
        self, content: str, lines: List[str], line_idx: int, issue: Dict[str, Any]
    ) -> Dict[str, Any]:
        """添加安全TODO注释"""

        todo_comment = f"# TODO: SECURITY - {issue['description']}"

        # 在问题行上方添加TODO注释
        lines.insert(line_idx, todo_comment)

        return {
            "applied": True,
            "content": "\n".join(lines),
            "todo": f"第{issue['line_num']}行: 添加安全TODO - {issue['description']}",
        }

    def generate_patches(self, files: List[str]) -> List[Dict[str, Any]]:
        """为文件列表生成安全修复补丁"""

        from ..utils import get_file_content

        patches = []

        for file_path in files:
            content = get_file_content(file_path)
            if not self.can_fix(file_path, content):
                continue

            fix_result = self.fix_file(file_path, content)

            if (
                fix_result["success"]
                and fix_result["fixed_content"] != fix_result["original_content"]
            ):
                patch_content = create_patch(
                    fix_result["original_content"],
                    fix_result["fixed_content"],
                    file_path,
                )

                if patch_content:
                    patches.append(
                        {
                            "file_path": file_path,
                            "patch_content": patch_content,
                            "changes": fix_result["changes"],
                            "todos": fix_result["todos"],
                            "errors": fix_result["errors"],
                        }
                    )

        return patches

    def create_changelog_entry(self, patches: List[Dict[str, Any]]) -> str:
        """创建变更日志条目"""

        if not patches:
            return "## 安全代码修改\n\n无安全问题需要修复。\n"

        lines = ["## 安全代码修改", ""]
        lines.append(f"修复了 {len(patches)} 个文件的安全问题：")
        lines.append("")

        for patch in patches:
            lines.append(f"### {patch['file_path']}")
            lines.append("")

            if patch["changes"]:
                lines.append("**自动修复：**")
                for change in patch["changes"]:
                    lines.append(f"- {change}")
                lines.append("")

            if patch["todos"]:
                lines.append("**需要人工处理（已添加TODO）：**")
                for todo in patch["todos"]:
                    lines.append(f"- {todo}")
                lines.append("")

            if patch["errors"]:
                lines.append("**错误：**")
                for error in patch["errors"]:
                    lines.append(f"- {error}")
                lines.append("")

        lines.append("**风险评估：** 中等风险 - 安全相关修改，请仔细审查")
        lines.append("")
        lines.append("**应用方法：**")
        lines.append("```bash")
        lines.append("git apply artifacts/ai_fixes/security_*.patch --index")
        lines.append("```")
        lines.append("")

        return "\n".join(lines)


def create_security_patches(files: List[str]) -> Dict[str, Any]:
    """创建安全修复补丁的便捷函数"""

    strategy = SecurityCodeModStrategy()
    patches = strategy.generate_patches(files)

    return {
        "strategy": strategy.name,
        "patches": patches,
        "changelog": strategy.create_changelog_entry(patches),
        "total_files": len(patches),
    }
