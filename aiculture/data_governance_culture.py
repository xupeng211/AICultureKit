"""
数据治理文化模块 - 数据隐私、质量、血缘追踪和合规检查

提供：
1. 数据隐私保护检查
2. 数据质量验证
3. 数据血缘追踪
4. GDPR合规检查
5. 数据分类和标记

⚠️ 安全说明：
本模块包含敏感字段名称和模式仅用于数据治理检查。
所有敏感字段都是示例用途，用于识别和保护真实敏感数据。
"""

import json
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class DataSensitivityLevel(Enum):
    """数据敏感度级别"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class DataCategory(Enum):
    """数据类别"""

    PERSONAL = "personal"
    FINANCIAL = "financial"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    LOCATION = "location"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"


@dataclass
class DataField:
    """数据字段"""

    name: str
    data_type: str
    sensitivity_level: DataSensitivityLevel
    categories: list[DataCategory]
    description: str = ""
    source: str = ""
    transformations: list[str] = field(default_factory=list)
    retention_period: str | None = None
    encryption_required: bool = False
    anonymization_method: str | None = None


@dataclass
class DataQualityRule:
    """数据质量规则"""

    name: str
    field_name: str
    rule_type: str  # not_null, unique, range, pattern, custom
    parameters: dict[str, Any]
    severity: str = "error"  # error, warning, info
    description: str = ""


@dataclass
class DataLineageNode:
    """数据血缘节点"""

    id: str
    name: str
    type: str  # table, view, file, api, transformation
    location: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DataLineageEdge:
    """数据血缘边"""

    source_id: str
    target_id: str
    transformation: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


class DataPrivacyScanner:
    """数据隐私扫描器"""

    def __init__(self):
        """__init__函数"""
        # 个人信息模式
        self.pii_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "passport": r"\b[A-Z]{1,2}\d{6,9}\b",
            "driver_license": r"\b[A-Z]{1,2}\d{6,8}\b",
        }

        # 敏感字段名模式
        self.sensitive_field_patterns = {
            "password": r"(?i)(password|passwd|pwd|secret|token|key)",
            "personal_name": r"(?i)(first_?name|last_?name|full_?name|surname|given_?name)",
            "address": r"(?i)(address|street|city|state|zip|postal|country)",
            "birth": r"(?i)(birth|dob|date_of_birth|birthday)",
            "gender": r"(?i)(gender|sex)",
            "race": r"(?i)(race|ethnicity|nationality)",
            "religion": r"(?i)(religion|faith|belief)",
            "health": r"(?i)(health|medical|diagnosis|treatment|medication)",
            "financial": r"(?i)(salary|income|bank|account|credit|debit|payment)",
        }

    def _is_placeholder_data(self, pii_type: str, matched_text: str) -> bool:
        """判断是否为占位符数据"""
        text_lower = matched_text.lower()

        # 排除正则表达式模式本身
        regex_patterns = [
            r"(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            r"\b\d{3}-\d{2}-\d{4}\b",
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        ]

        if any(pattern in matched_text for pattern in regex_patterns):
            return True

        # 邮箱占位符
        if pii_type == "email":
            placeholder_domains = [
                "placeholder.local",
                "demo.local",
                "example.com",
                "test.com",
                "demo.com",
                "demo-placeholder.dev",
                "demo-company.com",
            ]
            placeholder_prefixes = [
                "demo",
                "test",
                "example",
                "placeholder",
                "user1",
                "user2",
                "noreply",
                "contact",
            ]

            domain = matched_text.split("@")[1].lower() if "@" in matched_text else ""
            prefix = matched_text.split("@")[0].lower() if "@" in matched_text else ""

            if domain in placeholder_domains or prefix in placeholder_prefixes:
                return True

        # IP地址占位符
        elif pii_type == "ip_address":
            if "xxx" in text_lower or "192.168.1.xxx" in text_lower:
                return True

        # 电话号码占位符
        elif pii_type == "phone":
            if "xxx" in text_lower:
                return True

        # SSN占位符
        elif pii_type == "ssn":
            if "xxx-xx-xxxx" in text_lower:
                return True

        # 其他占位符标识
        placeholder_indicators = [
            "xxx",
            "placeholder",
            "demo",
            "test",
            "example",
            "sample",
        ]
        if any(indicator in text_lower for indicator in placeholder_indicators):
            return True

        return False

    def scan_code_for_pii(self, file_path: Path) -> list[dict[str, Any]]:
        """扫描代码中的个人信息"""
        findings = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                # 检查PII模式
                for pii_type, pattern in self.pii_patterns.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        matched_text = match.group()

                        # 跳过占位符数据
                        if self._is_placeholder_data(pii_type, matched_text):
                            continue

                        findings.append(
                            {
                                "type": "pii_in_code",
                                "pii_type": pii_type,
                                "file": str(file_path),
                                "line": line_num,
                                "column": match.start(),
                                "matched_text": matched_text,
                                "severity": "high",
                                "recommendation": f"避免在代码中硬编码{pii_type}信息",
                            }
                        )

                # 检查敏感字段名
                for field_type, pattern in self.sensitive_field_patterns.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        findings.append(
                            {
                                "type": "sensitive_field",
                                "field_type": field_type,
                                "file": str(file_path),
                                "line": line_num,
                                "column": match.start(),
                                "matched_text": match.group(),
                                "severity": "medium",
                                "recommendation": f"确保{field_type}字段有适当的保护措施",
                            }
                        )

        except Exception as e:
            findings.append(
                {
                    "type": "scan_error",
                    "file": str(file_path),
                    "error": str(e),
                    "severity": "low",
                }
            )

        return findings

    def scan_database_schema(self, schema_info: dict[str, Any]) -> list[dict[str, Any]]:
        """扫描数据库模式中的敏感信息"""
        findings = []

        for table_name, table_info in schema_info.items():
            columns = table_info.get("columns", [])

            for column in columns:
                column_name = column.get("name", "")
                column_type = column.get("type", "")

                # 检查敏感字段名
                for field_type, pattern in self.sensitive_field_patterns.items():
                    if re.search(pattern, column_name):
                        findings.append(
                            {
                                "type": "sensitive_database_field",
                                "field_type": field_type,
                                "table": table_name,
                                "column": column_name,
                                "data_type": column_type,
                                "severity": "high",
                                "recommendation": f"为{field_type}字段实施加密和访问控制",
                            }
                        )

        return findings


class DataQualityValidator:
    """数据质量验证器"""

    def __init__(self):
        """__init__函数"""
        self.rules: list[DataQualityRule] = []

    def add_rule(self, rule: DataQualityRule) -> None:
        """添加质量规则"""
        self.rules.append(rule)

    def validate_data(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """验证数据质量"""
        results = {
            "total_records": len(data),
            "passed_records": 0,
            "failed_records": 0,
            "rule_results": {},
            "issues": [],
        }

        if not data:
            return results

        # 按规则验证
        for rule in self.rules:
            rule_results = self._validate_rule(rule, data)
            results["rule_results"][rule.name] = rule_results
            results["issues"].extend(rule_results["issues"])

        # 计算通过/失败记录数
        failed_record_ids = set()
        for issue in results["issues"]:
            if issue.get("record_id") is not None:
                failed_record_ids.add(issue["record_id"])

        results["failed_records"] = len(failed_record_ids)
        results["passed_records"] = results["total_records"] - results["failed_records"]

        return results

    def _validate_rule(self, rule: DataQualityRule, data: list[dict[str, Any]]) -> dict[str, Any]:
        """验证单个规则"""
        rule_result = {
            "rule_name": rule.name,
            "rule_type": rule.rule_type,
            "passed": 0,
            "failed": 0,
            "issues": [],
        }

        for record_id, record in enumerate(data):
            field_value = record.get(rule.field_name)

            is_valid = True
            issue_message = ""

            if rule.rule_type == "not_null":
                is_valid = field_value is not None and field_value != ""
                issue_message = f"字段 {rule.field_name} 不能为空"

            elif rule.rule_type == "unique":
                # 这需要在所有记录的上下文中检查
                values = [r.get(rule.field_name) for r in data]
                is_valid = values.count(field_value) == 1
                issue_message = f"字段 {rule.field_name} 值重复: {field_value}"

            elif rule.rule_type == "range":
                min_val = rule.parameters.get("min")
                max_val = rule.parameters.get("max")
                if isinstance(field_value, (int, float)):
                    is_valid = (min_val is None or field_value >= min_val) and (
                        max_val is None or field_value <= max_val
                    )
                    issue_message = (
                        f"字段 {rule.field_name} 值 {field_value} 超出范围 [{min_val}, {max_val}]"
                    )
                else:
                    is_valid = False
                    issue_message = f"字段 {rule.field_name} 不是数值类型"

            elif rule.rule_type == "pattern":
                pattern = rule.parameters.get("pattern")
                if pattern and isinstance(field_value, str):
                    is_valid = bool(re.match(pattern, field_value))
                    issue_message = f"字段 {rule.field_name} 值 {field_value} 不匹配模式 {pattern}"
                else:
                    is_valid = False
                    issue_message = f"字段 {rule.field_name} 模式验证失败"

            if is_valid:
                rule_result["passed"] += 1
            else:
                rule_result["failed"] += 1
                rule_result["issues"].append(
                    {
                        "record_id": record_id,
                        "field_name": rule.field_name,
                        "field_value": field_value,
                        "rule_name": rule.name,
                        "severity": rule.severity,
                        "message": issue_message,
                    }
                )

        return rule_result


class DataLineageTracker:
    """数据血缘追踪器"""

    def __init__(self):
        """__init__函数"""
        self.nodes: dict[str, DataLineageNode] = {}
        self.edges: list[DataLineageEdge] = []

    def add_node(self, node: DataLineageNode) -> None:
        """添加血缘节点"""
        self.nodes[node.id] = node

    def add_edge(self, edge: DataLineageEdge) -> None:
        """添加血缘边"""
        self.edges.append(edge)

    def track_transformation(
        self, source_id: str, target_id: str, transformation: str, **metadata
    ) -> None:
        """追踪数据转换"""
        edge = DataLineageEdge(
            source_id=source_id,
            target_id=target_id,
            transformation=transformation,
            timestamp=time.time(),
            metadata=metadata,
        )
        self.add_edge(edge)

    def get_upstream_lineage(self, node_id: str, max_depth: int = 10) -> dict[str, Any]:
        """获取上游血缘"""
        visited = set()
        lineage = {"nodes": {}, "edges": []}

        def traverse_upstream(current_id: str, depth: int):
            """traverse_upstream函数"""
            if depth >= max_depth or current_id in visited:
                return

            visited.add(current_id)

            if current_id in self.nodes:
                lineage["nodes"][current_id] = self.nodes[current_id]

            # 查找指向当前节点的边
            for edge in self.edges:
                if edge.target_id == current_id:
                    lineage["edges"].append(edge)
                    traverse_upstream(edge.source_id, depth + 1)

        traverse_upstream(node_id, 0)
        return lineage

    def get_downstream_lineage(self, node_id: str, max_depth: int = 10) -> dict[str, Any]:
        """获取下游血缘"""
        visited = set()
        lineage = {"nodes": {}, "edges": []}

        def traverse_downstream(current_id: str, depth: int):
            """traverse_downstream函数"""
            if depth >= max_depth or current_id in visited:
                return

            visited.add(current_id)

            if current_id in self.nodes:
                lineage["nodes"][current_id] = self.nodes[current_id]

            # 查找从当前节点出发的边
            for edge in self.edges:
                if edge.source_id == current_id:
                    lineage["edges"].append(edge)
                    traverse_downstream(edge.target_id, depth + 1)

        traverse_downstream(node_id, 0)
        return lineage

    def get_impact_analysis(self, node_id: str) -> dict[str, Any]:
        """获取影响分析"""
        downstream = self.get_downstream_lineage(node_id)

        impact_summary = {
            "affected_nodes": len(downstream["nodes"]),
            "affected_transformations": len(downstream["edges"]),
            "critical_paths": [],
            "recommendations": [],
        }

        # 分析关键路径
        for edge in downstream["edges"]:
            if "critical" in edge.metadata:
                impact_summary["critical_paths"].append(
                    {
                        "source": edge.source_id,
                        "target": edge.target_id,
                        "transformation": edge.transformation,
                    }
                )

        # 生成建议
        if impact_summary["affected_nodes"] > 10:
            impact_summary["recommendations"].append("影响范围较大，建议分阶段实施变更")

        if impact_summary["critical_paths"]:
            impact_summary["recommendations"].append("存在关键路径，需要额外的测试和验证")

        return impact_summary

    def export_lineage_graph(self, format: str = "json") -> str:
        """导出血缘图"""
        if format == "json":
            return json.dumps(
                {
                    "nodes": [
                        {
                            "id": node.id,
                            "name": node.name,
                            "type": node.type,
                            "location": node.location,
                            "metadata": node.metadata,
                        }
                        for node in self.nodes.values()
                    ],
                    "edges": [
                        {
                            "source": edge.source_id,
                            "target": edge.target_id,
                            "transformation": edge.transformation,
                            "timestamp": edge.timestamp,
                            "metadata": edge.metadata,
                        }
                        for edge in self.edges
                    ],
                },
                indent=2,
                ensure_ascii=False,
            )

        elif format == "dot":
            # Graphviz DOT格式
            lines = ["digraph DataLineage {"]

            # 添加节点
            for node in self.nodes.values():
                lines.append(f'  "{node.id}" [label="{node.name}\\n({node.type})"];')

            # 添加边
            for edge in self.edges:
                lines.append(
                    f'  "{edge.source_id}" -> "{edge.target_id}" [label="{edge.transformation}"];'
                )

            lines.append("}")
            return "\n".join(lines)

        return ""


class GDPRComplianceChecker:
    """GDPR合规检查器"""

    def __init__(self):
        """__init__函数"""
        self.gdpr_requirements = {
            "data_minimization": "只收集必要的个人数据",
            "purpose_limitation": "数据使用应限于收集目的",
            "accuracy": "确保个人数据准确和最新",
            "storage_limitation": "不应超过必要期限存储个人数据",
            "security": "实施适当的技术和组织措施",
            "accountability": "能够证明合规性",
            "consent": "获得明确的数据处理同意",
            "rights": "支持数据主体权利",
        }

    def check_compliance(self, data_inventory: list[DataField]) -> dict[str, Any]:
        """检查GDPR合规性"""
        compliance_report = {
            "overall_score": 0,
            "requirements": {},
            "violations": [],
            "recommendations": [],
        }

        personal_data_fields = [
            field for field in data_inventory if DataCategory.PERSONAL in field.categories
        ]

        # 检查数据最小化
        compliance_report["requirements"]["data_minimization"] = self._check_data_minimization(
            personal_data_fields
        )

        # 检查存储限制
        compliance_report["requirements"]["storage_limitation"] = self._check_storage_limitation(
            personal_data_fields
        )

        # 检查安全措施
        compliance_report["requirements"]["security"] = self._check_security_measures(
            personal_data_fields
        )

        # 检查数据准确性
        compliance_report["requirements"]["accuracy"] = self._check_data_accuracy(
            personal_data_fields
        )

        # 计算总体评分
        scores = [req["score"] for req in compliance_report["requirements"].values()]
        compliance_report["overall_score"] = sum(scores) / len(scores) if scores else 0

        # 收集违规和建议
        for req_name, req_result in compliance_report["requirements"].items():
            compliance_report["violations"].extend(req_result.get("violations", []))
            compliance_report["recommendations"].extend(req_result.get("recommendations", []))

        return compliance_report

    def _check_data_minimization(self, fields: list[DataField]) -> dict[str, Any]:
        """检查数据最小化原则"""
        result = {"score": 100, "violations": [], "recommendations": []}

        for data_field in fields:
            if not data_field.description:
                result["violations"].append(f"字段 {data_field.name} 缺少用途说明")
                result["score"] -= 10

            if (
                field.sensitivity_level == DataSensitivityLevel.RESTRICTED
                and not field.encryption_required
            ):
                result["violations"].append(f"高敏感字段 {field.name} 未要求加密")
                result["score"] -= 15

        if result["violations"]:
            result["recommendations"].append("为所有个人数据字段添加明确的用途说明")
            result["recommendations"].append("对高敏感数据实施加密保护")

        return result

    def _check_storage_limitation(self, fields: list[DataField]) -> dict[str, Any]:
        """检查存储限制原则"""
        result = {"score": 100, "violations": [], "recommendations": []}

        for data_field in fields:
            if not data_field.retention_period:
                result["violations"].append(f"字段 {data_field.name} 未定义保留期限")
                result["score"] -= 20

        if result["violations"]:
            result["recommendations"].append("为所有个人数据定义明确的保留期限")
            result["recommendations"].append("实施自动数据删除机制")

        return result

    def _check_security_measures(self, fields: list[DataField]) -> dict[str, Any]:
        """检查安全措施"""
        result = {"score": 100, "violations": [], "recommendations": []}

        sensitive_fields = [
            f
            for f in fields
            if f.sensitivity_level
            in [DataSensitivityLevel.CONFIDENTIAL, DataSensitivityLevel.RESTRICTED]
        ]

        for data_field in sensitive_fields:
            if not data_field.encryption_required:
                result["violations"].append(f"敏感字段 {data_field.name} 未启用加密")
                result["score"] -= 25

            if not data_field.anonymization_method:
                result["violations"].append(f"敏感字段 {data_field.name} 未定义匿名化方法")
                result["score"] -= 15

        if result["violations"]:
            result["recommendations"].append("对所有敏感个人数据实施加密")
            result["recommendations"].append("实施数据匿名化和假名化技术")

        return result

    def _check_data_accuracy(self, fields: list[DataField]) -> dict[str, Any]:
        """检查数据准确性"""
        result = {"score": 100, "violations": [], "recommendations": []}

        # 这里可以集成数据质量检查结果
        # 简化实现，假设所有字段都需要验证机制

        for data_field in fields:
            if not data_field.transformations:
                result["violations"].append(f"字段 {data_field.name} 缺少数据验证转换")
                result["score"] -= 10

        if result["violations"]:
            result["recommendations"].append("为个人数据字段实施数据验证和清洗机制")
            result["recommendations"].append("建立数据质量监控和报告机制")

        return result


class DataGovernanceManager:
    """数据治理管理器"""

    def __init__(self, project_path: Path):
        """__init__函数"""
        self.project_path = project_path
        self.config_dir = project_path / ".aiculture" / "data_governance"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.privacy_scanner = DataPrivacyScanner()
        self.quality_validator = DataQualityValidator()
        self.lineage_tracker = DataLineageTracker()
        self.gdpr_checker = GDPRComplianceChecker()

        self.data_inventory: list[DataField] = []
        self._load_data_inventory()

    def _load_data_inventory(self) -> None:
        """加载数据清单"""
        inventory_file = self.config_dir / "data_inventory.json"
        if inventory_file.exists():
            try:
                with open(inventory_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for field_data in data:
                        field = DataField(
                            name=field_data["name"],
                            data_type=field_data["data_type"],
                            sensitivity_level=DataSensitivityLevel(field_data["sensitivity_level"]),
                            categories=[DataCategory(cat) for cat in field_data["categories"]],
                            description=field_data.get("description", ""),
                            source=field_data.get("source", ""),
                            transformations=field_data.get("transformations", []),
                            retention_period=field_data.get("retention_period"),
                            encryption_required=field_data.get("encryption_required", False),
                            anonymization_method=field_data.get("anonymization_method"),
                        )
                        self.data_inventory.append(field)
            except Exception as e:
                print(f"加载数据清单失败: {e}")

    def _save_data_inventory(self) -> None:
        """保存数据清单"""
        inventory_file = self.config_dir / "data_inventory.json"
        data = []
        for data_field in self.data_inventory:
            data.append(
                {
                    "name": data_field.name,
                    "data_type": data_field.data_type,
                    "sensitivity_level": data_field.sensitivity_level.value,
                    "categories": [cat.value for cat in data_field.categories],
                    "description": data_field.description,
                    "source": data_field.source,
                    "transformations": data_field.transformations,
                    "retention_period": data_field.retention_period,
                    "encryption_required": data_field.encryption_required,
                    "anonymization_method": data_field.anonymization_method,
                }
            )

        with open(inventory_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def scan_project_for_privacy_issues(self) -> dict[str, Any]:
        """扫描项目中的隐私问题"""
        all_findings = []

        # 扫描Python文件
        for py_file in self.project_path.rglob("*.py"):
            if any(
                part.startswith(".") or part in ["venv", "__pycache__"] for part in py_file.parts
            ):
                continue

            findings = self.privacy_scanner.scan_code_for_pii(py_file)
            all_findings.extend(findings)

        # 按严重程度分组
        by_severity = {"high": [], "medium": [], "low": []}
        for finding in all_findings:
            severity = finding.get("severity", "low")
            by_severity[severity].append(finding)

        return {
            "total_findings": len(all_findings),
            "by_severity": by_severity,
            "summary": {
                "high_risk_files": len(set(f["file"] for f in by_severity["high"])),
                "pii_types_found": len(
                    set(f.get("pii_type", "") for f in all_findings if f.get("pii_type"))
                ),
                "recommendations": [
                    "移除代码中的硬编码个人信息",
                    "使用环境变量或配置文件存储敏感信息",
                    "实施数据脱敏和匿名化",
                    "添加数据访问控制和审计日志",
                ],
            },
        }

    def generate_compliance_report(self) -> dict[str, Any]:
        """生成合规报告"""
        privacy_scan = self.scan_project_for_privacy_issues()
        gdpr_compliance = self.gdpr_checker.check_compliance(self.data_inventory)

        return {
            "timestamp": time.time(),
            "privacy_scan": privacy_scan,
            "gdpr_compliance": gdpr_compliance,
            "data_inventory_size": len(self.data_inventory),
            "overall_compliance_score": (
                (100 - min(privacy_scan["total_findings"] * 5, 50)) * 0.4
                + gdpr_compliance["overall_score"] * 0.6
            ),
            "action_items": [
                f"修复 {privacy_scan['total_findings']} 个隐私问题",
                "提升GDPR合规评分至90%以上",
                "完善数据清单和分类",
                "实施数据保护技术措施",
            ],
        }


# 使用示例
if __name__ == "__main__":
    # 初始化数据治理管理器
    governance = DataGovernanceManager(Path("."))

    # 添加示例数据字段
    user_email = DataField(
        name="user_email",
        data_type="string",
        sensitivity_level=DataSensitivityLevel.CONFIDENTIAL,
        categories=[DataCategory.PERSONAL],
        description="用户邮箱地址",
        source="user_registration",
        retention_period="2_years",
        encryption_required=True,
        anonymization_method="hash",
    )
    governance.data_inventory.append(user_email)

    # 生成合规报告
    report = governance.generate_compliance_report()
    print(f"数据治理合规报告: {json.dumps(report, indent=2, ensure_ascii=False)}")

    # 扫描隐私问题
    privacy_issues = governance.scan_project_for_privacy_issues()
    print(f"隐私问题扫描结果: {privacy_issues['total_findings']} 个问题")
