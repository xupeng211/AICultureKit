"""
CLI命令模块

将CLI命令拆分为多个模块以提高可维护性。
"""

from .project_commands import project_group
from .quality_commands import quality_group
from .culture_commands import culture_group
from .template_commands import template_group

__all__ = ["project_group", "quality_group", "culture_group", "template_group"]
