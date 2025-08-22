"""
模式学习集成系统 - 结合AI学习系统和多语言分析，提供综合的项目模式学习。

这个模块将:
1. 整合Python和其他语言的分析结果
2. 识别跨语言的一致性模式
3. 生成针对多语言项目的个性化规则
4. 提供语言间的最佳实践建议
"""

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .ai_learning_system import AILearningEngine, LearningResult
from .multi_language_analyzer import LanguageMetrics, MultiLanguageManager


@dataclass
class CrossLanguagePattern:
    """跨语言模式"""

    pattern_name: str
    languages: list[str]
    pattern_values: dict[str, Any]
    consistency_score: float
    recommendation: str


@dataclass
class IntegratedLearningResult:
    """集成学习结果"""

    python_learning: LearningResult | None
    multi_language_analysis: dict[str, LanguageMetrics]
    cross_language_patterns: list[CrossLanguagePattern]
    unified_recommendations: list[str]
    overall_maturity: str
    recommended_strictness: float
    language_specific_rules: dict[str, dict[str, Any]]
    generated_at: float


class PatternLearningIntegrator:
    """模式学习集成器"""

    def __init__(self, project_path: Path) -> None:
        """初始化模式学习集成器"""
        self.project_path = project_path
        self.ai_learning_engine = AILearningEngine(project_path)
        self.multi_language_manager = MultiLanguageManager(project_path)

    def perform_comprehensive_learning(self) -> IntegratedLearningResult:
        """执行综合学习分析"""
        # 1. 执行Python AI学习
        try:
            python_learning = self.ai_learning_engine.learn_project_patterns()
        except Exception:
            python_learning = None

        # 2. 执行多语言分析
        multi_language_analysis = self.multi_language_manager.analyze_all_languages()

        # 3. 分析跨语言模式
        cross_language_patterns = self._analyze_cross_language_patterns(
            python_learning, multi_language_analysis
        )

        # 4. 评估整体项目成熟度
        overall_maturity = self._assess_overall_maturity(python_learning, multi_language_analysis)

        # 5. 计算推荐严格度
        recommended_strictness = self._calculate_unified_strictness(
            python_learning, multi_language_analysis, overall_maturity
        )

        # 6. 生成语言特定规则
        language_specific_rules = self._generate_language_specific_rules(
            multi_language_analysis, cross_language_patterns
        )

        # 7. 生成统一建议
        unified_recommendations = self._generate_unified_recommendations(
            python_learning, multi_language_analysis, cross_language_patterns
        )

        return IntegratedLearningResult(
            python_learning=python_learning,
            multi_language_analysis=multi_language_analysis,
            cross_language_patterns=cross_language_patterns,
            unified_recommendations=unified_recommendations,
            overall_maturity=overall_maturity,
            recommended_strictness=recommended_strictness,
            language_specific_rules=language_specific_rules,
            generated_at=time.time(),
        )

    def _analyze_cross_language_patterns(
        self,
        python_learning: LearningResult | None,
        multi_lang_analysis: dict[str, LanguageMetrics],
    ) -> list[CrossLanguagePattern]:
        """分析跨语言模式"""
        patterns = []

        # 收集所有语言的模式
        all_patterns = {}

        # 添加Python模式
        if python_learning:
            for pattern in python_learning.patterns:
                pattern_key = pattern.pattern_name
                if pattern_key not in all_patterns:
                    all_patterns[pattern_key] = {}
                all_patterns[pattern_key]["python"] = pattern.pattern_value

        # 添加其他语言模式
        for lang_name, metrics in multi_lang_analysis.items():
            for pattern in metrics.patterns:
                pattern_key = pattern.pattern_name
                if pattern_key not in all_patterns:
                    all_patterns[pattern_key] = {}
                all_patterns[pattern_key][lang_name] = pattern.pattern_value

        # 分析模式一致性
        for pattern_name, language_values in all_patterns.items():
            if len(language_values) > 1:  # 多种语言都有这个模式
                consistency_score = self._calculate_pattern_consistency(language_values)

                # 生成建议
                recommendation = self._generate_pattern_recommendation(
                    pattern_name, language_values, consistency_score
                )

                patterns.append(
                    CrossLanguagePattern(
                        pattern_name=pattern_name,
                        languages=list(language_values.keys()),
                        pattern_values=language_values,
                        consistency_score=consistency_score,
                        recommendation=recommendation,
                    )
                )

        # 分析特殊的跨语言模式
        patterns.extend(self._analyze_special_cross_patterns(python_learning, multi_lang_analysis))

        return patterns

    def _calculate_pattern_consistency(self, language_values: dict[str, Any]) -> float:
        """计算模式一致性分数"""
        if len(language_values) <= 1:
            return 1.0

        # 对于命名风格等分类值
        if all(isinstance(v, str) for v in language_values.values()):
            unique_values = set(language_values.values())
            return 1.0 if len(unique_values) == 1 else 0.5

        # 对于数值类型
        if all(isinstance(v, (int, float)) for v in language_values.values()):
            values = list(language_values.values())
            if not values:
                return 0.0

            mean_val = sum(values) / len(values)
            if mean_val == 0:
                return 1.0 if all(v == 0 for v in values) else 0.0

            # 计算相对标准差
            variance = sum((v - mean_val) ** 2 for v in values) / len(values)
            std_dev = variance**0.5
            relative_std = std_dev / abs(mean_val) if mean_val != 0 else 0

            # 转换为一致性分数 (0-1)
            consistency = max(0, 1 - relative_std)
            return consistency

        # 对于布尔值
        if all(isinstance(v, bool) for v in language_values.values()):
            unique_values = set(language_values.values())
            return 1.0 if len(unique_values) == 1 else 0.0

        # 默认情况
        return 0.5

    def _generate_pattern_recommendation(
        self,
        pattern_name: str,
        language_values: dict[str, Any],
        consistency_score: float,
    ) -> str:
        """生成模式建议"""
        if consistency_score >= 0.8:
            return f"✅ {pattern_name}在所有语言中保持良好一致性，继续维持当前标准"
        elif consistency_score >= 0.5:
            return f"⚠️ {pattern_name}在不同语言间存在轻微差异，建议统一标准"
        else:
            return f"❌ {pattern_name}在不同语言间差异较大，需要制定统一的跨语言规范"

    def _analyze_special_cross_patterns(
        self,
        python_learning: LearningResult | None,
        multi_lang_analysis: dict[str, LanguageMetrics],
    ) -> list[CrossLanguagePattern]:
        """分析特殊的跨语言模式"""
        patterns = []

        # 复杂度对比模式
        complexity_values = {}
        if python_learning:
            # 从Python学习结果中获取复杂度信息
            for pattern in python_learning.patterns:
                if pattern.pattern_type == "complexity":
                    complexity_values["python"] = pattern.pattern_value

        for lang_name, metrics in multi_lang_analysis.items():
            complexity_values[lang_name] = metrics.avg_complexity

        if len(complexity_values) > 1:
            consistency = self._calculate_pattern_consistency(complexity_values)
            patterns.append(
                CrossLanguagePattern(
                    pattern_name="complexity_consistency",
                    languages=list(complexity_values.keys()),
                    pattern_values=complexity_values,
                    consistency_score=consistency,
                    recommendation=self._generate_complexity_recommendation(
                        complexity_values, consistency
                    ),
                )
            )

        # 函数大小对比模式
        function_size_values = {}
        for lang_name, metrics in multi_lang_analysis.items():
            function_size_values[lang_name] = metrics.avg_function_size

        if function_size_values:
            consistency = self._calculate_pattern_consistency(function_size_values)
            patterns.append(
                CrossLanguagePattern(
                    pattern_name="function_size_consistency",
                    languages=list(function_size_values.keys()),
                    pattern_values=function_size_values,
                    consistency_score=consistency,
                    recommendation=self._generate_function_size_recommendation(
                        function_size_values, consistency
                    ),
                )
            )

        return patterns

    def _generate_complexity_recommendation(
        self, complexity_values: dict[str, float], consistency: float
    ) -> str:
        """生成复杂度建议"""
        avg_complexity = sum(complexity_values.values()) / len(complexity_values)

        if consistency >= 0.8:
            if avg_complexity <= 5:
                return "✅ 所有语言的复杂度都保持在理想范围内且一致"
            else:
                return "⚠️ 所有语言的复杂度都偏高，建议整体简化逻辑"
        else:
            max_lang = max(complexity_values.items(), key=lambda x: x[1])
            min_lang = min(complexity_values.items(), key=lambda x: x[1])
            return f"❌ 复杂度不一致：{max_lang[0]}({max_lang[1]:.1f}) vs {min_lang[0]}({min_lang[1]:.1f})，需要平衡各语言的实现复杂度"

    def _generate_function_size_recommendation(
        self, size_values: dict[str, float], consistency: float
    ) -> str:
        """生成函数大小建议"""
        avg_size = sum(size_values.values()) / len(size_values)

        if consistency >= 0.8:
            if avg_size <= 20:
                return "✅ 所有语言的函数大小都保持在合理范围内且一致"
            else:
                return "⚠️ 所有语言的函数都偏大，建议拆分长函数"
        else:
            max_lang = max(size_values.items(), key=lambda x: x[1])
            min_lang = min(size_values.items(), key=lambda x: x[1])
            return f"❌ 函数大小不一致：{max_lang[0]}({max_lang[1]:.1f}行) vs {min_lang[0]}({min_lang[1]:.1f}行)，建议统一函数长度标准"

    def _assess_overall_maturity(
        self,
        python_learning: LearningResult | None,
        multi_lang_analysis: dict[str, LanguageMetrics],
    ) -> str:
        """评估整体项目成熟度"""
        maturity_scores = []

        # Python成熟度
        if python_learning:
            python_score = self._maturity_to_score(python_learning.project_maturity)
            maturity_scores.append(python_score)

        # 其他语言成熟度评估
        for lang_name, metrics in multi_lang_analysis.items():
            lang_score = self._calculate_language_maturity_score(metrics)
            maturity_scores.append(lang_score)

        if not maturity_scores:
            return "beginner"

        avg_score = sum(maturity_scores) / len(maturity_scores)

        if avg_score >= 0.8:
            return "expert"
        elif avg_score >= 0.6:
            return "intermediate"
        else:
            return "beginner"

    def _maturity_to_score(self, maturity: str) -> float:
        """将成熟度等级转换为分数"""
        mapping = {"beginner": 0.3, "intermediate": 0.6, "expert": 0.9}
        return mapping.get(maturity, 0.3)

    def _calculate_language_maturity_score(self, metrics: LanguageMetrics) -> float:
        """计算语言特定的成熟度分数"""
        score = 0.0
        weight_sum = 0.0

        # 命名一致性 (权重: 0.3)
        score += metrics.naming_consistency * 0.3
        weight_sum += 0.3

        # 风格一致性 (权重: 0.2)
        score += metrics.style_consistency * 0.2
        weight_sum += 0.2

        # 复杂度评分 (权重: 0.3)
        complexity_score = (
            1.0 if metrics.avg_complexity <= 5 else max(0, 1 - (metrics.avg_complexity - 5) / 10)
        )
        score += complexity_score * 0.3
        weight_sum += 0.3

        # 函数大小评分 (权重: 0.2)
        size_score = (
            1.0
            if metrics.avg_function_size <= 20
            else max(0, 1 - (metrics.avg_function_size - 20) / 30)
        )
        score += size_score * 0.2
        weight_sum += 0.2

        return score / weight_sum if weight_sum > 0 else 0.0

    def _calculate_unified_strictness(
        self,
        python_learning: LearningResult | None,
        multi_lang_analysis: dict[str, LanguageMetrics],
        overall_maturity: str,
    ) -> float:
        """计算统一的严格度"""
        base_strictness = {"beginner": 0.6, "intermediate": 0.75, "expert": 0.9}

        strictness = base_strictness.get(overall_maturity, 0.7)

        # 根据跨语言一致性调整
        if len(multi_lang_analysis) > 1:
            consistency_scores = []

            # 计算命名一致性
            naming_styles = []
            for metrics in multi_lang_analysis.values():
                naming_patterns = [p for p in metrics.patterns if "naming" in p.pattern_name]
                if naming_patterns:
                    naming_styles.extend([p.pattern_value for p in naming_patterns])

            if naming_styles:
                unique_styles = set(naming_styles)
                naming_consistency = 1.0 if len(unique_styles) == 1 else 0.5
                consistency_scores.append(naming_consistency)

            # 如果有一致性数据，调整严格度
            if consistency_scores:
                avg_consistency = sum(consistency_scores) / len(consistency_scores)
                if avg_consistency >= 0.8:
                    strictness += 0.05  # 高一致性，可以提高严格度
                elif avg_consistency < 0.5:
                    strictness -= 0.1  # 低一致性，降低严格度避免过度限制

        return max(0.3, min(1.0, strictness))

    def _generate_language_specific_rules(
        self,
        multi_lang_analysis: dict[str, LanguageMetrics],
        cross_patterns: list[CrossLanguagePattern],
    ) -> dict[str, dict[str, Any]]:
        """生成语言特定的规则"""
        language_rules = {}

        for lang_name, metrics in multi_lang_analysis.items():
            rules = {}

            # 基于语言特定模式生成规则
            for pattern in metrics.patterns:
                if pattern.confidence > 0.7:
                    if pattern.pattern_type == "naming":
                        rules[f"enforce_{pattern.pattern_name}"] = {
                            "enabled": True,
                            "style": pattern.pattern_value,
                            "severity": "warning",
                        }
                    elif pattern.pattern_type == "style":
                        rules[f"style_{pattern.pattern_name}"] = {
                            "enabled": True,
                            "preference": pattern.pattern_value,
                            "severity": "info",
                        }

            # 基于复杂度生成规则
            if metrics.avg_complexity > 0:
                rules["complexity_threshold"] = {
                    "enabled": True,
                    "max_complexity": max(5, int(metrics.avg_complexity * 1.2)),
                    "severity": "warning",
                }

            # 基于函数大小生成规则
            if metrics.avg_function_size > 0:
                rules["function_length_threshold"] = {
                    "enabled": True,
                    "max_lines": max(20, int(metrics.avg_function_size * 1.5)),
                    "severity": "info",
                }

            language_rules[lang_name] = rules

        return language_rules

    def _generate_python_recommendations(self, python_learning: LearningResult) -> list[str]:
        """生成Python相关建议"""
        recommendations = []

        if python_learning.confidence > 0.8:
            recommendations.append("Python代码质量很高，建议保持当前标准")
        elif python_learning.confidence > 0.6:
            recommendations.append("Python代码质量良好，可进一步优化")
        else:
            recommendations.append("Python代码需要重点改进")

        # 基于学习到的模式添加具体建议
        for pattern in python_learning.patterns[:3]:  # 只取前3个最重要的模式
            if pattern.confidence > 0.7:
                recommendations.append(f"建议在项目中推广 {pattern.pattern_type} 模式")

        return recommendations

    def _generate_multilang_recommendations(
        self, multi_lang_analysis: dict[str, LanguageMetrics]
    ) -> list[str]:
        """生成多语言相关建议"""
        recommendations = []
        total_languages = len(multi_lang_analysis)

        if total_languages > 3:
            recommendations.append("项目使用多种编程语言，建议建立统一的代码规范")

        # 分析各语言的质量
        high_quality_langs = []
        low_quality_langs = []

        for lang, metrics in multi_lang_analysis.items():
            if metrics.quality_score > 0.8:
                high_quality_langs.append(lang)
            elif metrics.quality_score < 0.5:
                low_quality_langs.append(lang)

        if high_quality_langs:
            recommendations.append(f"以下语言代码质量较高: {', '.join(high_quality_langs)}")

        if low_quality_langs:
            recommendations.append(f"以下语言需要重点改进: {', '.join(low_quality_langs)}")

        return recommendations

    def _generate_cross_pattern_recommendations(
        self, cross_patterns: list[CrossLanguagePattern]
    ) -> list[str]:
        """生成跨语言模式建议"""
        recommendations = []

        if not cross_patterns:
            recommendations.append("建议建立跨语言的统一开发模式")
            return recommendations

        # 分析跨语言模式
        strong_patterns = [p for p in cross_patterns if p.strength > 0.7]
        weak_patterns = [p for p in cross_patterns if p.strength < 0.4]

        if strong_patterns:
            recommendations.append(f"发现 {len(strong_patterns)} 个强跨语言模式，建议继续强化")

        if weak_patterns:
            recommendations.append(f"发现 {len(weak_patterns)} 个弱跨语言模式，建议改进一致性")

        return recommendations

    def _generate_unified_recommendations(
        self,
        python_learning: LearningResult | None,
        multi_lang_analysis: dict[str, LanguageMetrics],
        cross_patterns: list[CrossLanguagePattern],
    ) -> list[str]:
        """生成统一建议"""
        recommendations = []

        # 基于Python学习结果的建议
        if python_learning:
            recommendations.extend(self._generate_python_recommendations(python_learning))

        # 基于多语言分析的建议
        recommendations.extend(self._generate_multilang_recommendations(multi_lang_analysis))

        # 基于跨语言模式的建议
        recommendations.extend(self._generate_cross_pattern_recommendations(cross_patterns))

        # 基于复杂度的建议
        complexity_pattern = next(
            (p for p in cross_patterns if p.pattern_name == "complexity_consistency"),
            None,
        )
        if complexity_pattern and complexity_pattern.consistency_score < 0.6:
            recommendations.append("🔄 不同语言间的复杂度差异较大，建议平衡实现复杂度")

        # 基于语言特定特征的建议
        for lang_name, metrics in multi_lang_analysis.items():
            if lang_name == "javascript":
                # JavaScript特定建议
                ts_patterns = [p for p in metrics.patterns if "typescript" in p.pattern_name]
                if ts_patterns and any(p.pattern_value < 0.5 for p in ts_patterns):
                    recommendations.append("📝 考虑增加TypeScript使用比例，提升类型安全性")

        # 基于整体质量的建议
        avg_naming_consistency = sum(
            m.naming_consistency for m in multi_lang_analysis.values()
        ) / len(multi_lang_analysis)
        if avg_naming_consistency < 0.8:
            recommendations.append("📝 命名规范不够一致，建议为每种语言制定明确的命名标准")

        avg_style_consistency = sum(
            m.style_consistency for m in multi_lang_analysis.values()
        ) / len(multi_lang_analysis)
        if avg_style_consistency < 0.8:
            recommendations.append("🎨 代码风格不够统一，建议为每种语言配置代码格式化工具")

        return recommendations


def save_integrated_learning_result(result: IntegratedLearningResult, project_path: Path) -> None:
    """保存集成学习结果"""
    result_file = project_path / ".aiculture" / "integrated_learning_result.json"
    result_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # 转换为可序列化的格式
        serializable_result = asdict(result)

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(serializable_result, f, indent=2, default=str)
    except (OSError, TypeError):
        pass


def load_integrated_learning_result(
    project_path: Path,
) -> IntegratedLearningResult | None:
    """加载集成学习结果"""
    result_file = project_path / ".aiculture" / "integrated_learning_result.json"

    try:
        if result_file.exists():
            with open(result_file, encoding="utf-8") as f:
                data = json.load(f)
                # 这里需要复杂的反序列化逻辑，简化处理
                return data  # 返回字典格式
    except (OSError, json.JSONDecodeError):
        pass

    return None
