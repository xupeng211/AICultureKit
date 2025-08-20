"""
AICultureKit - 标准化AI主导开发的文化和最佳实践工具包

这个包提供了：
- 项目模板和脚手架功能
- 代码质量和CI/CD配置
- AI协作指南和最佳实践
- 开发文化标准化工具
"""

__version__ = "0.1.0"
__author__ = "AICultureKit Contributors"
__email__ = "contact@aiculture.dev"

from .core import ProjectTemplate, QualityTools, CultureConfig
from .cli import main

__all__ = [
    "ProjectTemplate",
    "QualityTools", 
    "CultureConfig",
    "main",
] 