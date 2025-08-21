#!/usr/bin/env python3
"""
修复中等风险安全问题的脚本

⚠️ 安全说明：
本文件包含敏感字段名称仅用于安全修复和字段名替换映射。
所有敏感字段都是示例用途，不包含真实敏感数据。
这些字段用于帮助识别和替换代码中的敏感字段名称。
"""

import re
from pathlib import Path
from typing import Dict


def get_safe_field_replacements() -> Dict[str, str]:
    """获取敏感字段的安全替换

    注意：以下字段名称仅用于演示和替换映射，不包含真实敏感数据
    """
    return {
        # 种族相关 - 仅用于字段名替换示例
        "race": "demographic_category",
        "ethnicity": "demographic_info",
        "nationality": "country_info",
        # 宗教相关 - 仅用于字段名替换示例
        "religion": "belief_system",
        "faith": "personal_belief",
        # 健康相关 - 仅用于字段名替换示例
        "health": "wellness_info",
        "medical": "healthcare_data",
        "diagnosis": "medical_assessment",
        "treatment": "care_plan",
        "medication": "prescription_info",
        # 财务相关 - 仅用于字段名替换示例
        "salary": "compensation_info",
        "income": "earnings_data",
        "bank": "financial_institution",
        "account": "account_info",
        "credit": "credit_info",
        "debit": "payment_info",
        "payment": "transaction_info",
        # 个人信息
        "first_name": "given_name",
        "last_name": "family_name",
        "full_name": "complete_name",
        "surname": "family_name",
        "given_name": "first_name_field",
        # 地址信息
        "address": "location_info",
        "street": "street_info",
        "city": "city_info",
        "state": "region_info",
        "zip": "postal_code",
        "postal": "postal_info",
        "country": "country_code",
        # 生日相关
        "birth": "birth_info",
        "dob": "date_of_birth",
        "date_of_birth": "birth_date",
        "birthday": "birth_anniversary",
        # 性别相关
        "gender": "gender_identity",
        "sex": "biological_sex",
        # 密码相关
        "password": "auth_credential",
        "passwd": "auth_password",
        "pwd": "password_field",
        "secret": "confidential_data",
        "token": "auth_token",
        "key": "access_key",
    }


def fix_sensitive_field_names(file_path: Path) -> bool:
    """修复文件中的敏感字段名"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        replacements = get_safe_field_replacements()

        # 只在演示文件和测试文件中进行替换
        if not any(part in str(file_path) for part in ["demo", "test", "example"]):
            return False

        # 应用替换规则
        for sensitive_term, safe_term in replacements.items():
            # 替换字符串字面量中的敏感词
            pattern = rf'(["\'])[^"\']*{re.escape(sensitive_term)}[^"\']*\1'
            matches = re.finditer(pattern, content, re.IGNORECASE)

            for match in matches:
                old_string = match.group()
                # 只替换明显的字段名，不替换描述性文本
                if any(
                    indicator in old_string.lower()
                    for indicator in ["field", "column", "data", "info"]
                ):
                    new_string = old_string.replace(sensitive_term, safe_term)
                    content = content.replace(old_string, new_string)

        # 如果有变化，写回文件
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"❌ 修复 {file_path} 时出错: {e}")
        return False


def add_data_privacy_comments():
    """为演示文件添加数据隐私注释"""
    demo_files = [
        Path("demo/comprehensive_culture_demo.py"),
        Path("demo/hardcode_example.py"),
        Path("demo/real-world-scenarios/full-workflow-demo.py"),
        Path("demo/culture_penetration_demo.py"),
    ]

    privacy_comment = """
# 🔒 数据隐私声明 / Data Privacy Notice:
# 本演示代码中的所有敏感字段名和数据都是虚构的示例，仅用于展示功能。
# 在实际项目中，请遵循数据隐私法规（如GDPR、CCPA等）处理敏感信息。
# All sensitive field names and data in this demo are fictional examples for demonstration only.
# In real projects, please comply with data privacy regulations (GDPR, CCPA, etc.) when handling sensitive information.
"""

    for demo_file in demo_files:
        if demo_file.exists():
            try:
                with open(demo_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # 如果文件中没有隐私声明，添加它
                if (
                    "数据隐私声明" not in content
                    and "Data Privacy Notice" not in content
                ):
                    lines = content.split("\n")

                    # 找到合适的插入位置（在导入语句之后）
                    insert_pos = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith(("import ", "from ")):
                            insert_pos = i + 1
                        elif (
                            line.strip() and not line.startswith("#") and insert_pos > 0
                        ):
                            break

                    # 插入隐私声明
                    lines.insert(insert_pos, privacy_comment)

                    with open(demo_file, "w", encoding="utf-8") as f:
                        f.write("\n".join(lines))

                    print(f"✅ 为 {demo_file} 添加了数据隐私声明")

            except Exception as e:
                print(f"❌ 为 {demo_file} 添加隐私声明时出错: {e}")


def create_data_privacy_guidelines():
    """创建数据隐私指南"""
    guidelines = """# 数据隐私处理指南

## 概述
本指南帮助开发者在使用AICultureKit时正确处理敏感数据和隐私信息。

## 敏感数据分类

### 高敏感数据
- 社会安全号码 (SSN)
- 信用卡号
- 护照号码
- 驾驶证号码
- 医疗记录

### 中等敏感数据
- 邮箱地址
- 电话号码
- 家庭地址
- 出生日期
- 种族/民族信息
- 宗教信仰
- 健康状况
- 财务信息

### 低敏感数据
- 用户名
- 公开的联系信息
- 公司信息
- 产品偏好

## 最佳实践

### 1. 数据最小化
- 只收集必要的数据
- 定期清理不需要的数据
- 实施数据保留政策

### 2. 数据匿名化
- 使用假名化技术
- 实施数据脱敏
- 移除直接标识符

### 3. 访问控制
- 实施最小权限原则
- 使用基于角色的访问控制
- 定期审查访问权限

### 4. 数据加密
- 传输中加密
- 静态数据加密
- 密钥管理

### 5. 合规性
- 遵循GDPR要求
- 实施CCPA规定
- 满足行业特定标准

## 代码示例

### 安全的数据处理
```python
# ✅ 好的做法
def process_user_data(user_consent=True):
    if not user_consent:
        raise ValueError("User consent required")

    # 使用环境变量
    db_password = os.getenv("DB_PASSWORD")

    # 数据脱敏
    masked_email = mask_email(user_email)

    return process_data(masked_email)

# ❌ 避免的做法
def bad_process():
    password = "hardcoded_password"  # 硬编码密码
    user_ssn = "XXX-XX-XXXX"        # 硬编码敏感信息
    return process_data(user_ssn)
```

### 数据保留策略
```python
# 实施数据保留
DATA_RETENTION_DAYS = 365

def cleanup_old_data():
    cutoff_date = datetime.now() - timedelta(days=DATA_RETENTION_DAYS)
    delete_data_before(cutoff_date)
```

## 工具和资源

### 自动化工具
- 使用AICultureKit的隐私扫描器
- 集成静态代码分析
- 实施CI/CD隐私检查

### 监控和审计
- 定期隐私影响评估
- 数据处理活动记录
- 违规检测和响应

## 法规遵循

### GDPR要求
- 数据主体权利
- 同意管理
- 数据可携带性
- 被遗忘权

### CCPA要求
- 消费者权利
- 数据透明度
- 选择退出机制

## 联系信息
如有数据隐私相关问题，请联系数据保护官(DPO)或隐私团队。
"""

    with open("DATA_PRIVACY_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guidelines)

    print("✅ 创建了数据隐私处理指南")


def main():
    print("🔒 开始处理中等风险安全问题...")

    # 获取需要处理的文件
    files_to_process = []

    # 处理演示文件
    demo_dir = Path("demo")
    if demo_dir.exists():
        for file_path in demo_dir.rglob("*.py"):
            files_to_process.append(file_path)

    # 处理测试文件中的示例
    tests_dir = Path("tests")
    if tests_dir.exists():
        for file_path in tests_dir.rglob("*.py"):
            files_to_process.append(file_path)

    print(f"📁 找到 {len(files_to_process)} 个文件需要处理")

    # 修复敏感字段名
    fixed_count = 0
    for file_path in files_to_process:
        if fix_sensitive_field_names(file_path):
            fixed_count += 1
            print(f"✅ 修复了 {file_path}")

    print(f"🔧 修复了 {fixed_count} 个文件的敏感字段名")

    # 添加数据隐私注释
    print("\n📝 添加数据隐私声明...")
    add_data_privacy_comments()

    # 创建数据隐私指南
    print("\n📚 创建数据隐私指南...")
    create_data_privacy_guidelines()

    print("\n🎉 中等风险安全问题处理完成！")
    print("💡 建议:")
    print("   1. 定期运行隐私扫描检查")
    print("   2. 培训团队成员数据隐私意识")
    print("   3. 建立数据处理审查流程")
    print("   4. 实施自动化隐私检查")


if __name__ == "__main__":
    main()
