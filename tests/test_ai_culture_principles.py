"""
测试aiculture.ai_culture_principles模块
"""

from aiculture.ai_culture_principles import (
    AICulturePrinciples,
    DevelopmentPrinciple,
    PrincipleCategory,
)


class TestDevelopmentPrinciple:
    """测试DevelopmentPrinciple类"""

    def test_principle_creation(self) -> None:
        """测试原则创建"""
        principle = DevelopmentPrinciple(
            name="Test Principle",
            category=PrincipleCategory.CODE_QUALITY,
            description="A test principle",
            rules=["Rule 1", "Rule 2"],
            ai_instructions=["Instruction 1", "Instruction 2"],
            enforcement_level="strict",
        )

        assert principle.name == "Test Principle"
        assert principle.category == PrincipleCategory.CODE_QUALITY
        assert principle.description == "A test principle"
        assert principle.enforcement_level == "strict"
        assert len(principle.rules) == 2
        assert len(principle.ai_instructions) == 2
        assert isinstance(principle.tools, list)
        assert isinstance(principle.examples, dict)


class TestAICulturePrinciples:
    """测试AICulturePrinciples类"""

    def test_ai_culture_principles_creation(self) -> None:
        """测试AI文化原则管理器创建"""
        principles = AICulturePrinciples()
        assert hasattr(principles, "principles")
        assert isinstance(principles.principles, dict)
        assert len(principles.principles) > 0

    def test_get_principles_by_category(self) -> None:
        """测试按类别获取原则"""
        principles = AICulturePrinciples()

        # 测试获取代码质量类别的原则
        code_quality_principles = principles.get_by_category(PrincipleCategory.CODE_QUALITY)
        assert isinstance(code_quality_principles, list)

        # 验证返回的都是正确类别的原则
        for principle in code_quality_principles:
            assert principle.category == PrincipleCategory.CODE_QUALITY

    def test_get_principle_by_name(self) -> None:
        """测试按名称获取原则"""
        principles = AICulturePrinciples()

        # 获取第一个原则的名称进行测试
        if principles.principles:
            first_principle_name = list(principles.principles.keys())[0]
            found_principle = principles.get_principle(first_principle_name)
            assert found_principle is not None
            assert found_principle.name == principles.principles[first_principle_name].name

        # 测试获取不存在的原则
        found_principle = principles.get_principle("nonexistent_principle")
        assert found_principle is None

    def test_get_all_categories(self) -> None:
        """测试获取所有类别"""
        principles = AICulturePrinciples()
        # 从原则中提取所有类别
        categories = set(p.category for p in principles.principles.values())

        assert isinstance(categories, set)
        assert len(categories) > 0

        # 验证返回的都是PrincipleCategory实例
        for category in categories:
            assert isinstance(category, PrincipleCategory)

    def test_get_ai_instructions(self) -> None:
        """测试获取AI指令"""
        principles = AICulturePrinciples()
        instructions = principles.get_ai_instructions()

        assert isinstance(instructions, dict)
        # 指令应该包含各个原则的AI指令
        assert len(instructions) > 0

    def test_principles_have_required_fields(self) -> None:
        """测试原则包含必需字段"""
        principles = AICulturePrinciples()

        for principle in principles.principles.values():
            assert hasattr(principle, "name")
            assert hasattr(principle, "category")
            assert hasattr(principle, "description")
            assert hasattr(principle, "rules")
            assert hasattr(principle, "ai_instructions")
            assert hasattr(principle, "enforcement_level")
            assert hasattr(principle, "tools")
            assert hasattr(principle, "examples")

            # 验证字段类型
            assert isinstance(principle.name, str)
            assert isinstance(principle.category, PrincipleCategory)
            assert isinstance(principle.description, str)
            assert isinstance(principle.rules, list)
            assert isinstance(principle.ai_instructions, list)
            assert isinstance(principle.enforcement_level, str)
            assert isinstance(principle.tools, list)
            assert isinstance(principle.examples, dict)
