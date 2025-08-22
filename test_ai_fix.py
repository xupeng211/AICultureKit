"""测试文件，包含各种可修复的问题"""


def test_function(param1, param2):
    """测试函数"""
    _unused_var = "这是未使用的变量"  # F841
    result = param1 + param2  # E225: 操作符周围缺少空格
    return result


class TestClass:
    """测试类"""

    def __init__(self):
        self.value = 42

    def method1(self):  # E302: 缺少空行
        """方法1"""
        return self.value

    def method2(self):  # E303: 过多空行
        """方法2"""
        items = [1, 2, 3, 4]  # E231: 逗号后缺少空格
        return items


def function_with_security_issues():
    """包含安全问题的函数"""
    # B101: assert语句
    assert True, "这是一个assert"

    # B311: 不安全的随机数
    import random

    return random.randint(1, 100)


# 文件末尾没有换行符
