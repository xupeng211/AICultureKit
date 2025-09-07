"""核心功能模块"""


class ProjectCore:
    """项目核心类"""

    def __init__(self):
        self.name = "{{PROJECT_NAME}}"
        self.version = "0.1.0"

    def get_info(self) -> dict:
        """获取项目信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "{{PROJECT_DESCRIPTION}}",
        }
