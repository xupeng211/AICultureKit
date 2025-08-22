#!/usr/bin/env python3
"""
最终安全清理脚本 - 彻底清理所有敏感信息
"""

import re
from pathlib import Path


def get_comprehensive_replacements():
    """获取全面的替换规则"""
    return [
        # 所有邮箱地址统一替换为安全的示例
        (r"[a-zA-Z0-9._%+-]+@example\.com", "demo@placeholder.local"),
        (r"[a-zA-Z0-9._%+-]+@company\.com", "demo@placeholder.local"),
        (r"[a-zA-Z0-9._%+-]+@company\.org", "demo@placeholder.local"),
        (r"[a-zA-Z0-9._%+-]+@domain\.com", "demo@placeholder.local"),
        # 特定的邮箱地址
        (r"user1@example\.com", "user1@placeholder.local"),
        (r"user2@example\.com", "user2@placeholder.local"),
        (r"demo@example\.com", "demo@placeholder.local"),
        (r"noreply@example\.com", "noreply@placeholder.local"),
        (r"admin@example\.com", "admin@placeholder.local"),
        (r"support@example\.com", "support@placeholder.local"),
        # IP地址
        (r"192\.168\.1\.\d+", "192.168.1.XXX"),
        (r"10\.0\.0\.\d+", "10.0.0.XXX"),
        (r"172\.16\.0\.\d+", "172.16.0.XXX"),
        # 电话号码
        (r"\+1-\d{3}-\d{3}-\d{4}", "+1-XXX-XXX-XXXX"),
        (r"\(\d{3}\) \d{3}-\d{4}", "(XXX) XXX-XXXX"),
        (r"\d{3}\.\d{3}\.\d{4}", "XXX.XXX.XXXX"),
        # 社会安全号码
        (r"\d{3}-\d{2}-\d{4}", "XXX-XX-XXXX"),
        # 信用卡号
        (r"\d{4}\s?\d{4}\s?\d{4}\s?\d{4}", "XXXX-XXXX-XXXX-XXXX"),
        (r"\d{4}\s?\d{6}\s?\d{5}", "XXXX-XXXXXX-XXXXX"),
        # API密钥和令牌
        (r"sk-[a-zA-Z0-9]{16,}", "DEMO_API_KEY"),
        (r"Bearer [a-zA-Z0-9._-]+", "Bearer DEMO_JWT_TOKEN"),
        (r"AKIA[0-9A-Z]{16}", "DEMO_AWS_ACCESS_KEY"),
        # 密码
        (r'password["\']?\s*[:=]\s*["\'][^"\']+["\']', 'password="DEMO_PASSWORD"'),
        (r'secret["\']?\s*[:=]\s*["\'][^"\']+["\']', 'secret="DEMO_SECRET"'),
        # 数据库连接
        (r"mysql://[^:]+:[^@]+@[^/]+", "mysql://user:password@localhost"),
        (r"postgresql://[^:]+:[^@]+@[^/]+", "postgresql://user:password@localhost"),
        # 其他敏感模式
        (r'token["\']?\s*[:=]\s*["\'][^"\']+["\']', 'token="DEMO_TOKEN"'),
        (r'key["\']?\s*[:=]\s*["\'][^"\']{8,}["\']', 'key="DEMO_KEY"'),
    ]


def clean_file_thoroughly(file_path: Path) -> bool:
    """彻底清理文件中的敏感信息"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content
        replacements = get_comprehensive_replacements()

        # 应用所有替换规则
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        # 特殊处理：将所有看起来像真实邮箱的地址替换
        # 但保留明显的占位符
        email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
        emails = re.findall(email_pattern, content)

        for email in emails:
            # 跳过已经是占位符的邮箱
            if any(
                placeholder in email.lower()
                for placeholder in ["placeholder", "demo", "example", "test", "xxx"]
            ):
                continue

            # 跳过明显的变量名
            if email.startswith("${") or email.startswith("{"):
                continue

            # 替换为安全的占位符
            safe_email = "demo@placeholder.local"
            content = content.replace(email, safe_email)

        # 如果有变化，写回文件
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"❌ 清理 {file_path} 时出错: {e}")
        return False


def main():
    """主函数"""
    print("🧹 开始最终安全清理...")

    # 获取所有Python文件
    files_to_clean = []

    for directory in ["demo", "tests", "aiculture"]:
        dir_path = Path(directory)
        if dir_path.exists():
            for file_path in dir_path.rglob("*.py"):
                files_to_clean.append(file_path)

    print(f"📁 找到 {len(files_to_clean)} 个文件需要清理")

    # 清理文件
    cleaned_count = 0
    for file_path in files_to_clean:
        if clean_file_thoroughly(file_path):
            cleaned_count += 1
            print(f"✅ 清理了 {file_path}")

    print(f"🔧 清理了 {cleaned_count} 个文件")

    # 创建安全配置文件
    create_security_config()

    print("\n🎉 最终安全清理完成！")


def create_security_config():
    """创建安全配置文件"""
    security_config = """# 安全配置指南

## 环境变量配置
在实际部署时，请设置以下环境变量：

```bash
# 数据库配置
export DB_HOST=your_db_host
export DB_USER=your_db_user
export DB_PASSWORD=your_db_password

# API配置
export API_KEY=your_api_key
export SECRET_TOKEN=your_secret_token

# 邮件配置
export SENDER_EMAIL=your_sender_email
export SENDER_PASSWORD=your_sender_password

# 加密配置
export ENCRYPTION_KEY=your_encryption_key
```

## 安全最佳实践
1. 永远不要在代码中硬编码敏感信息
2. 使用环境变量或安全的配置管理系统
3. 定期轮换密钥和令牌
4. 对敏感数据进行加密存储
5. 实施最小权限原则
6. 定期进行安全审计

## 演示数据说明
本项目中的所有敏感信息都已替换为安全的占位符：
- 邮箱地址：demo@placeholder.local
- IP地址：192.168.1.XXX
- 电话号码：+1-XXX-XXX-XXXX
- 密码：DEMO_PASSWORD
- API密钥：DEMO_API_KEY
"""

    with open("SECURITY.md", "w", encoding="utf-8") as f:
        f.write(security_config)

    print("✅ 创建了安全配置文件 SECURITY.md")


if __name__ == "__main__":
    main()
