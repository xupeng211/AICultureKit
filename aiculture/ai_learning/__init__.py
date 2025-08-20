"""
AI学习系统模块

提供智能项目分析和个性化规则生成功能。
"""

from .pattern_types import (
    ProjectPattern,
    LearningResult,
    PatternAnalyzer,
    NamingPatternAnalyzer,
    StructurePatternAnalyzer,
    StylePatternAnalyzer,
    DocumentationPatternAnalyzer
)

from .code_analyzer import CodeAnalyzer
from .learning_engine import LearningEngine

__all__ = [
    'ProjectPattern',
    'LearningResult',
    'PatternAnalyzer',
    'NamingPatternAnalyzer',
    'StructurePatternAnalyzer',
    'StylePatternAnalyzer',
    'DocumentationPatternAnalyzer',
    'CodeAnalyzer',
    'LearningEngine'
]
