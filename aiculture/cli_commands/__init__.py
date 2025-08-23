"""
CLI命令模块

包含所有的命令行接口实现，按功能分组
"""

from .project_commands import project_group
from .quality_commands import quality_group  
from .culture_commands import culture_group
from .template_commands import template_group
from .ai_commands import ai_group, ai_context  # 新增AI协作命令

__all__ = [
    'project_group',
    'quality_group', 
    'culture_group',
    'template_group',
    'ai_group',      # AI协作命令组
    'ai_context'     # 快捷上下文命令
]
