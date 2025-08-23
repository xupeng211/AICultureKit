"""
AI协作增效模块

解决AI开发中的4大核心痛点：
1. 上下文传递 - 自动生成项目摘要给AI
2. 代码一致性 - 检测和修复AI生成代码的风格问题
3. 增量迭代 - 维护AI协作的历史上下文
4. 质量把控 - 智能代码审查和改进建议
"""

from .context_generator import ProjectContextGenerator
from .consistency_checker import AICodeConsistencyChecker
from .session_manager import AISessionManager
from .quality_reviewer import AIQualityReviewer

__all__ = [
    'ProjectContextGenerator',
    'AICodeConsistencyChecker', 
    'AISessionManager',
    'AIQualityReviewer'
] 