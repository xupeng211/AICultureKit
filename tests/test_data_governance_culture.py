"""
数据治理文化模块测试
"""

import tempfile
from pathlib import Path
import pytest

from aiculture.data_governance_culture import (
    DataGovernanceManager,
    DataPrivacyScanner,
    DataQualityValidator,
    GDPRComplianceChecker,
    DataSensitivityLevel,
    DataField,
    DataQualityRule,
)


class TestDataPrivacyScanner:
    """数据隐私扫描器测试"""

    def setup_method(self):
        """测试设置"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.scanner = DataPrivacyScanner()

    def teardown_method(self):
        """测试清理"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_email_detection(self):
        """测试邮箱检测"""
        test_content = """
        user_email = "demo@placeholder.local"
        contact = "demo@placeholder.local"
        invalid_email = "not-an-email"
        """

        findings = self.scanner.scan_content(test_content, "test.py")

        # 应该找到2个邮箱
        email_findings = [f for f in findings if f["type"] == "email"]
        assert len(email_findings) == 2

        emails = [f["matched_text"] for f in email_findings]
        assert "demo@placeholder.local" in emails
        assert "demo@placeholder.local" in emails

    def test_phone_detection(self):
        """测试电话号码检测"""
        test_content = """
        phone1 = "+1-XXX-XXX-XXXX"
        phone2 = "(XXX) XXX-XXXX"
        phone3 = "XXX.XXX.XXXX"
        not_phone = "123-abc-defg"
        """

        findings = self.scanner.scan_content(test_content, "test.py")

        phone_findings = [f for f in findings if f["type"] == "phone"]
        assert len(phone_findings) >= 2  # 至少检测到2个电话号码

    def test_ssn_detection(self):
        """测试社会安全号码检测"""
        test_content = """
        ssn = "XXX-XX-XXXX"
        another_ssn = "987654321"
        not_ssn = "123-ab-cdef"
        """

        findings = self.scanner.scan_content(test_content, "test.py")

        ssn_findings = [f for f in findings if f["type"] == "ssn"]
        assert len(ssn_findings) >= 1

    def test_credit_card_detection(self):
        """测试信用卡号检测"""
        test_content = """
        visa = "XXXX-XXXX-XXXX-XXXX"
        mastercard = "XXXX-XXXX-XXXX-XXXX"
        amex = "XXXX-XXXX-XXXX-XXX"
        invalid = "XXXX-XXXX-XXXX-XXXX"
        """

        findings = self.scanner.scan_content(test_content, "test.py")

        cc_findings = [f for f in findings if f["type"] == "credit_card"]
        assert len(cc_findings) >= 2  # 至少检测到2个信用卡号

    def test_file_scanning(self):
        """测试文件扫描"""
        # 创建测试文件
        test_file = self.temp_dir / "test_data.py"
        with open(test_file, "w") as f:
            f.write(
                """
user_data = {
    "email": "demo@placeholder.local",
    "phone": "+1-XXX-XXX-XXXX",
    "ssn": "XXX-XX-XXXX"
}
"""
            )

        findings = self.scanner.scan_file(test_file)

        assert len(findings) >= 3  # 应该找到邮箱、电话、SSN

        # 验证文件路径
        for finding in findings:
            assert finding["file"] == str(test_file)

    def test_severity_classification(self):
        """测试严重程度分类"""
        test_content = """
        email = "demo@placeholder.local"  # 中等风险
        ssn = "XXX-XX-XXXX"         # 高风险
        phone = "+1-XXX-XXX-XXXX"   # 中等风险
        """

        findings = self.scanner.scan_content(test_content, "test.py")

        # 检查严重程度分类
        high_risk = [f for f in findings if f["severity"] == "high"]
        medium_risk = [f for f in findings if f["severity"] == "medium"]

        assert len(high_risk) >= 1  # SSN应该是高风险
        assert len(medium_risk) >= 2  # 邮箱和电话应该是中等风险


class TestDataQualityValidator:
    """数据质量验证器测试"""

    def setup_method(self):
        """测试设置"""
        self.validator = DataQualityValidator()

    def test_completeness_rule(self):
        """测试完整性规则"""
        # 创建完整性规则
        rule = DataQualityRule(
            name="email_completeness",
            description="Email field must not be empty",
            rule_type="completeness",
            field_name="email",
            parameters={},
        )

        # 测试数据
        complete_data = {"email": "demo@placeholder.local", "name": "John"}
        incomplete_data = {"email": "", "name": "John"}
        missing_data = {"name": "John"}

        # 验证
        assert self.validator.validate_rule(rule, complete_data) is True
        assert self.validator.validate_rule(rule, incomplete_data) is False
        assert self.validator.validate_rule(rule, missing_data) is False

    def test_format_rule(self):
        """测试格式规则"""
        # 创建格式规则
        rule = DataQualityRule(
            name="email_format",
            description="Email must be valid format",
            rule_type="format",
            field_name="email",
            parameters={"pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"},
        )

        # 测试数据
        valid_data = {"email": "demo@placeholder.local"}
        invalid_data = {"email": "invalid-email"}

        # 验证
        assert self.validator.validate_rule(rule, valid_data) is True
        assert self.validator.validate_rule(rule, invalid_data) is False

    def test_range_rule(self):
        """测试范围规则"""
        # 创建范围规则
        rule = DataQualityRule(
            name="age_range",
            description="Age must be between 0 and 150",
            rule_type="range",
            field_name="age",
            parameters={"min_value": 0, "max_value": 150},
        )

        # 测试数据
        valid_data = {"age": 25}
        invalid_low = {"age": -5}
        invalid_high = {"age": 200}

        # 验证
        assert self.validator.validate_rule(rule, valid_data) is True
        assert self.validator.validate_rule(rule, invalid_low) is False
        assert self.validator.validate_rule(rule, invalid_high) is False

    def test_uniqueness_rule(self):
        """测试唯一性规则"""
        # 创建唯一性规则
        rule = DataQualityRule(
            name="id_uniqueness",
            description="ID must be unique",
            rule_type="uniqueness",
            field_name="id",
            parameters={},
        )

        # 测试数据集
        dataset = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"},
            {"id": 3, "name": "Bob"},
            {"id": 2, "name": "Duplicate"},  # 重复ID
        ]

        # 验证唯一性
        result = self.validator.validate_dataset_rule(rule, dataset)
        assert result is False  # 应该失败，因为有重复ID

    def test_batch_validation(self):
        """测试批量验证"""
        # 创建多个规则
        rules = [
            DataQualityRule(
                "email_completeness", "Email required", "completeness", "email", {}
            ),
            DataQualityRule(
                "email_format",
                "Email format",
                "format",
                "email",
                {"pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"},
            ),
            DataQualityRule(
                "age_range",
                "Age range",
                "range",
                "age",
                {"min_value": 0, "max_value": 150},
            ),
        ]

        # 测试数据
        good_data = {"email": "demo@placeholder.local", "age": 25}
        bad_data = {"email": "invalid", "age": 200}

        # 批量验证
        good_results = self.validator.validate_data(good_data, rules)
        bad_results = self.validator.validate_data(bad_data, rules)

        assert good_results["passed"] == 3
        assert good_results["failed"] == 0

        assert bad_results["passed"] == 1  # 只有completeness通过
        assert bad_results["failed"] == 2  # format和range失败


class TestGDPRComplianceChecker:
    """GDPR合规检查器测试"""

    def setup_method(self):
        """测试设置"""
        self.checker = GDPRComplianceChecker()

    def test_personal_data_identification(self):
        """测试个人数据识别"""
        # 包含个人数据的内容
        personal_content = """
        user_profile = {
            "name": "John Doe",
            "email": "demo@placeholder.local",
            "phone": "+1-XXX-XXX-XXXX",
            "address": "123 Main St, City, State"
        }
        """

        findings = self.checker.scan_for_personal_data(personal_content, "user_data.py")

        assert len(findings) >= 3  # 至少应该找到姓名、邮箱、电话

        # 验证个人数据类型
        data_types = [f["data_type"] for f in findings]
        assert "email" in data_types
        assert "phone" in data_types

    def test_consent_mechanism_check(self):
        """测试同意机制检查"""
        # 有同意机制的代码
        with_consent = """
        def collect_user_data(user_consent=True):
            if not user_consent:
                raise ValueError("User consent required")
            return collect_data()
        """

        # 没有同意机制的代码
        without_consent = """
        def collect_user_data():
            return collect_sensitive_data()
        """

        consent_check1 = self.checker.check_consent_mechanisms(with_consent, "good.py")
        consent_check2 = self.checker.check_consent_mechanisms(
            without_consent, "bad.py"
        )

        assert consent_check1["has_consent_check"] is True
        assert consent_check2["has_consent_check"] is False

    def test_data_retention_check(self):
        """测试数据保留检查"""
        # 有保留策略的代码
        with_retention = """
        DATA_RETENTION_DAYS = 365
        
        def cleanup_old_data():
            cutoff_date = datetime.now() - timedelta(days=DATA_RETENTION_DAYS)
            delete_data_before(cutoff_date)
        """

        # 没有保留策略的代码
        without_retention = """
        def store_user_data(data):
            database.insert(data)  # 永久存储
        """

        retention_check1 = self.checker.check_data_retention(with_retention, "good.py")
        retention_check2 = self.checker.check_data_retention(
            without_retention, "bad.py"
        )

        assert retention_check1["has_retention_policy"] is True
        assert retention_check2["has_retention_policy"] is False

    def test_comprehensive_gdpr_check(self):
        """测试综合GDPR检查"""
        test_content = """
        # 用户数据收集
        def register_user(email, name, phone, user_consent=True):
            if not user_consent:
                raise ValueError("GDPR consent required")
            
            user_data = {
                "email": email,
                "name": name,
                "phone": phone,
                "created_at": datetime.now()
            }
            
            # 数据保留策略
            DATA_RETENTION_DAYS = 730
            
            return save_user(user_data)
        """

        gdpr_report = self.checker.generate_compliance_report(
            test_content, "user_service.py"
        )

        assert isinstance(gdpr_report, dict)
        assert "personal_data_found" in gdpr_report
        assert "consent_mechanisms" in gdpr_report
        assert "data_retention" in gdpr_report
        assert "compliance_score" in gdpr_report

        # 这个例子应该有较高的合规分数
        assert gdpr_report["compliance_score"] > 70


class TestDataGovernanceManager:
    """数据治理管理器测试"""

    def setup_method(self):
        """测试设置"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = DataGovernanceManager(self.temp_dir)

    def teardown_method(self):
        """测试清理"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert self.manager.project_path == self.temp_dir
        assert isinstance(self.manager.privacy_scanner, DataPrivacyScanner)
        assert isinstance(self.manager.quality_validator, DataQualityValidator)
        assert isinstance(self.manager.gdpr_checker, GDPRComplianceChecker)

    def test_project_privacy_scan(self):
        """测试项目隐私扫描"""
        # 创建测试文件
        test_file = self.temp_dir / "user_data.py"
        with open(test_file, "w") as f:
            f.write(
                """
user_info = {
    "email": "demo@placeholder.local",
    "phone": "+1-XXX-XXX-XXXX",
    "ssn": "XXX-XX-XXXX"
}
"""
            )

        # 扫描项目
        scan_result = self.manager.scan_project_for_privacy_issues()

        assert isinstance(scan_result, dict)
        assert "total_findings" in scan_result
        assert "by_severity" in scan_result
        assert "by_type" in scan_result
        assert scan_result["total_findings"] >= 3

    def test_data_catalog_creation(self):
        """测试数据目录创建"""
        # 创建数据字段
        fields = [
            DataField("user_id", "用户唯一标识", DataSensitivityLevel.PUBLIC),
            DataField("email", "用户邮箱", DataSensitivityLevel.SENSITIVE),
            DataField("password_hash", "密码哈希", DataSensitivityLevel.RESTRICTED),
        ]

        # 创建数据目录
        catalog = self.manager.create_data_catalog("user_table", "用户信息表", fields)

        assert catalog["table_name"] == "user_table"
        assert catalog["description"] == "用户信息表"
        assert len(catalog["fields"]) == 3

        # 验证字段信息
        email_field = next(f for f in catalog["fields"] if f["name"] == "email")
        assert email_field["sensitivity_level"] == "SENSITIVE"

    def test_comprehensive_governance_report(self):
        """测试综合治理报告"""
        # 创建测试文件
        test_file = self.temp_dir / "data_service.py"
        with open(test_file, "w") as f:
            f.write(
                """
def process_user_data(email, name, consent=True):
    if not consent:
        raise ValueError("User consent required")
    
    return {
        "email": email,
        "name": name,
        "processed_at": datetime.now()
    }
"""
            )

        # 生成综合报告
        report = self.manager.generate_governance_report()

        assert isinstance(report, dict)
        assert "privacy_scan" in report
        assert "gdpr_compliance" in report
        assert "data_quality" in report
        assert "overall_score" in report

        # 验证报告结构
        assert isinstance(report["privacy_scan"], dict)
        assert isinstance(report["gdpr_compliance"], dict)


# 集成测试
class TestDataGovernanceCultureIntegration:
    """数据治理文化集成测试"""

    def test_end_to_end_governance(self):
        """测试端到端数据治理"""
        temp_dir = Path(tempfile.mkdtemp())

        try:
            manager = DataGovernanceManager(temp_dir)

            # 创建包含各种数据问题的测试文件
            test_file = temp_dir / "user_service.py"
            with open(test_file, "w") as f:
                f.write(
                    '''
class UserService:
    """UserService:类"""
    def create_user(self, email, name, phone, ssn, consent=True):
        if not consent:
            raise ValueError("GDPR consent required")
        
        # 数据验证
        if not email or "@" not in email:
            raise ValueError("Invalid email")
        
        user_data = {
            "email": email,
            "name": name,
            "phone": phone,
            "ssn": ssn,  # 高敏感数据
            "created_at": datetime.now()
        }
        
        # 数据保留策略
        DATA_RETENTION_DAYS = 365
        
        return self.save_user(user_data)
'''
                )

            # 执行完整的数据治理检查
            governance_report = manager.generate_governance_report()

            # 验证报告包含所有必要信息
            assert "privacy_scan" in governance_report
            assert "gdpr_compliance" in governance_report
            assert "overall_score" in governance_report

            # 验证隐私扫描发现了敏感数据
            privacy_findings = governance_report["privacy_scan"]["total_findings"]
            assert privacy_findings > 0

            # 验证GDPR合规检查
            gdpr_score = governance_report["gdpr_compliance"]["compliance_score"]
            assert isinstance(gdpr_score, (int, float))
            assert 0 <= gdpr_score <= 100

        finally:
            import shutil

            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])
