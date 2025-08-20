"""
AI学习系统 - 智能分析项目特征并生成个性化开发文化规则。

这个系统能够：
1. 分析项目代码模式和风格
2. 学习团队编码习惯
3. 生成个性化的质量检查规则
4. 自适应调整严格度

注意：此模块已重构为模块化结构，主要功能已迁移到ai_learning子包中。
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ai_learning import CodeAnalyzer, LearningEngine, LearningResult, ProjectPattern


class ProjectAnalyzer:
    """项目分析器 - 向后兼容接口"""

    def __init__(self, project_path: Path) -> None:
        """初始化项目分析器"""
        self.project_path = project_path
        self.patterns: List[ProjectPattern] = []
        self.logger = logging.getLogger(__name__)
        self._analyzer = CodeAnalyzer(project_path)

    def analyze_project(self) -> Dict[str, Any]:
        """分析整个项目，返回项目特征"""
        return self._analyzer.analyze_project()


class AILearningEngine:
    """AI学习引擎 - 向后兼容接口"""

    def __init__(self, project_path: Path) -> None:
        """初始化AI学习引擎"""
        self.project_path = project_path
        self.analyzer = ProjectAnalyzer(project_path)
        self.logger = logging.getLogger(__name__)
        self._engine = LearningEngine(project_path)

        # 配置
        self.config = {
            'min_confidence': 0.7,
            'pattern_threshold': 0.6,
            'adaptation_rate': 0.1,
        }

    def learn_project_patterns(self) -> LearningResult:
        """学习项目模式并生成个性化规则"""
        return self._engine.learn_project_patterns()


class AdaptiveStrictnessManager:
    """自适应严格度管理器 - 向后兼容接口"""

    def __init__(self, project_path: Path) -> None:
        """初始化严格度管理器"""
        self.project_path = project_path
        self.logger = logging.getLogger(__name__)
        self._engine = LearningEngine(project_path)

    def calculate_strictness(self, learning_result: LearningResult) -> float:
        """计算适应性严格度"""
        return learning_result.recommended_strictness

    def adjust_strictness_based_on_feedback(
        self, current_strictness: float, feedback: Dict[str, Any]
    ) -> float:
        """根据反馈调整严格度"""
        # 简化实现
        if feedback.get('too_strict', False):
            return max(0.1, current_strictness - 0.1)
        elif feedback.get('too_lenient', False):
            return min(1.0, current_strictness + 0.1)
        return current_strictness


def save_learning_result(learning_result: LearningResult, project_path: Path) -> None:
    """保存学习结果到文件"""
    engine = LearningEngine(project_path)
    engine.save_learning_result(learning_result)


def load_learning_result(project_path: Path) -> Optional[LearningResult]:
    """从文件加载学习结果"""
    try:
        engine = LearningEngine(project_path)
        return engine.load_learning_result()
    except (FileNotFoundError, ValueError):
        return None


# 向后兼容的别名
AILearningSystem = AILearningEngine  # 兼容旧的类名


# 文件已重构为模块化结构，主要功能已迁移到ai_learning子包中
