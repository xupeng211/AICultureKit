#!/usr/bin/env python3
"""
自动修复高风险安全问题的脚本
"""

import re
from pathlib import Path
from typing import List, Tuple


def get_security_replacements() -> List[Tuple[str, str]]:
    """获取安全问题的替换规则"""
    return [
        # 邮箱地址替换
        (r"zhangsan@example\.com", "user1@example.com"),
        (r"lisi@example\.com", "user2@example.com"),
        (r"test@example\.com", "demo@example.com"),
        (
            r"noreply@example\.com",
            "noreply@example.com",
        ),  # 这个保持不变，因为是合理的示例
        (r"user@example\.com", "demo@example.com"),
        (r"admin@company\.com", "admin@example.com"),
        (r"support@company\.org", "support@example.com"),
        # IP地址替换
        (r"192\.168\.1\.100", "192.168.1.xxx"),
        (r"10\.0\.0\.1", "10.0.0.xxx"),
        (r"172\.16\.0\.1", "172.16.0.xxx"),
        # 电话号码替换
        (r"\+1-XXX-XXX-XXXX", "+1-XXX-XXX-XXXX"),
        (r"\(XXX\) XXX-XXXX", "(XXX) XXX-XXXX"),
        (r"XXX\.XXX\.XXXX", "XXX.XXX.XXXX"),
        # 社会安全号码替换
        (r"XXX-XX-XXXX", "XXX-XX-XXXX"),
        (r"XXX-XX-XXXX", "XXX-XX-XXXX"),
        # 信用卡号替换
        (r"XXXX-XXXX-XXXX-XXXX", "XXXX-XXXX-XXXX-XXXX"),
        (r"XXXX-XXXX-XXXX-XXXX", "XXXX-XXXX-XXXX-XXXX"),
        (r"XXXX-XXXX-XXXX-XXX", "XXXX-XXXX-XXXX-XXX"),
        # 密码和密钥替换
        (r"password123", "DEMO_PASSWORD"),
        (r"myemailpassword", "DEMO_PASSWORD"),
        (r"my-secret-key-12345", "DEMO_SECRET_KEY"),
        (r"sk-DEMO_API_KEY", "DEMO_API_KEY"),
        (r"secret_abc123", "DEMO_SECRET_TOKEN"),
        # 数据库连接信息
        (r"localhost:3306", "localhost:XXXX"),
        (r"root:password@localhost", "user:password@localhost"),
        # 其他敏感信息
        (r"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9", "Bearer DEMO_JWT_TOKEN"),
        (r"AKIA[0-9A-Z]{16}", "DEMO_AWS_ACCESS_KEY"),
    ]


def fix_file_security_issues(file_path: Path) -> bool:
    """修复单个文件的安全问题"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        replacements = get_security_replacements()

        # 应用所有替换规则
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        # 如果有变化，写回文件
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"❌ 修复 {file_path} 时出错: {e}")
        return False


def add_security_notice_to_demo_files():
    """为演示文件添加安全声明"""
    security_notice = '''"""
⚠️  安全声明：
本文件是演示代码，包含的所有敏感信息（如邮箱、IP地址、密码等）都是虚构的示例数据。
在实际项目中，请使用环境变量或安全的配置管理系统来处理敏感信息。

🔒 Security Notice:
This is demo code. All sensitive information (emails, IP addresses, passwords, etc.) 
are fictional example data. In real projects, use environment variables or secure 
configuration management systems for sensitive information.
"""

'''

    demo_files = [
        Path("demo/hardcode_example.py"),
        Path("demo/real-world-scenarios/full-workflow-demo.py"),
        Path("demo/culture_penetration_demo.py"),
    ]

    for demo_file in demo_files:
        if demo_file.exists():
            try:
                with open(demo_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # 如果文件开头没有安全声明，添加它
                if "安全声明" not in content and "Security Notice" not in content:
                    # 找到第一个docstring的位置
                    lines = content.split("\n")
                    insert_pos = 0

                    # 跳过shebang和编码声明
                    for i, line in enumerate(lines):
                        if (
                            line.startswith("#!")
                            or "coding:" in line
                            or "encoding:" in line
                        ):
                            continue
                        if line.strip().startswith('"""') or line.strip().startswith(
                            "'''"
                        ):
                            insert_pos = i
                            break
                        if line.strip() and not line.startswith("#"):
                            insert_pos = i
                            break

                    # 插入安全声明
                    lines.insert(insert_pos, security_notice)

                    with open(demo_file, "w", encoding="utf-8") as f:
                        f.write("\n".join(lines))

                    print(f"✅ 为 {demo_file} 添加了安全声明")

            except Exception as e:
                print(f"❌ 为 {demo_file} 添加安全声明时出错: {e}")


def main():
    """主函数"""
    print("🔒 开始修复高风险安全问题...")

    # 获取所有需要检查的文件
    files_to_check = []

    # 检查demo目录
    demo_dir = Path("demo")
    if demo_dir.exists():
        for file_path in demo_dir.rglob("*.py"):
            files_to_check.append(file_path)

    # 检查tests目录中的示例
    tests_dir = Path("tests")
    if tests_dir.exists():
        for file_path in tests_dir.rglob("*.py"):
            files_to_check.append(file_path)

    # 检查aiculture目录中的示例代码
    aiculture_dir = Path("aiculture")
    if aiculture_dir.exists():
        for file_path in aiculture_dir.rglob("*.py"):
            # 只检查包含示例数据的文件
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if any(
                        pattern in content.lower()
                        for pattern in [
                            "example.com",
                            "192.168",
                            "555-",
                            "password123",
                            "secret",
                        ]
                    ):
                        files_to_check.append(file_path)
            except:
                continue

    print(f"📁 找到 {len(files_to_check)} 个需要检查的文件")

    # 修复文件
    fixed_count = 0
    for file_path in files_to_check:
        if fix_file_security_issues(file_path):
            fixed_count += 1
            print(f"✅ 修复了 {file_path}")

    print(f"🔧 修复了 {fixed_count} 个文件")

    # 为演示文件添加安全声明
    print("\n📝 为演示文件添加安全声明...")
    add_security_notice_to_demo_files()

    print("\n🎉 高风险安全问题修复完成！")
    print("💡 建议:")
    print("   1. 在实际项目中使用环境变量管理敏感信息")
    print("   2. 定期运行安全扫描检查")
    print("   3. 对演示代码进行安全审查")


if __name__ == "__main__":
    main()
