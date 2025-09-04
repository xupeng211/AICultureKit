# 测试编写与覆盖率要求 (testing.md)

## 🎯 测试理念

### 1. **测试金字塔**
```
        /\     
       /  \    E2E测试 (10%)
      /____\   
     /      \  
    /        \  集成测试 (20%)
   /__________\
  /            \
 /              \ 单元测试 (70%)
/________________\
```

### 2. **测试驱动开发（TDD）**
- **Red**: 写一个失败的测试
- **Green**: 写最少的代码让测试通过
- **Refactor**: 重构代码，保持测试通过

### 3. **行为驱动开发（BDD）**
- 测试应该描述**行为**而不是实现
- 使用**Given-When-Then**模式
- 测试名称应该是可读的句子

---

## 🧪 测试分类与要求

### 单元测试 (Unit Tests)
**目标覆盖率: 90%+**

```python
# tests/test_user_service.py
import pytest
from unittest.mock import Mock, patch
from src.core.services import UserService
from src.core.exceptions import ValidationError

class TestUserService:
    """用户服务测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.email_service = Mock()
        self.user_service = UserService(self.email_service)
    
    def test_create_user_with_valid_data_should_return_user(self):
        """给定有效用户数据，当创建用户时，应该返回用户对象"""
        # Given
        user_data = {
            "name": "张三", 
            "email": "zhangsan@example.com",
            "age": 25
        }
        
        # When
        result = self.user_service.create_user(user_data)
        
        # Then
        assert result.name == "张三"
        assert result.email == "zhangsan@example.com"
        assert result.age == 25
        self.email_service.send_welcome_email.assert_called_once()
    
    def test_create_user_with_invalid_email_should_raise_validation_error(self):
        """给定无效邮箱，当创建用户时，应该抛出验证错误"""
        # Given
        user_data = {"name": "张三", "email": "invalid-email"}
        
        # When & Then
        with pytest.raises(ValidationError) as exc_info:
            self.user_service.create_user(user_data)
        
        assert "邮箱格式无效" in str(exc_info.value)
    
    @patch('src.core.services.datetime')
    def test_create_user_should_set_creation_time(self, mock_datetime):
        """创建用户时应该设置创建时间"""
        # Given
        mock_datetime.now.return_value = "2024-01-01 10:00:00"
        user_data = {"name": "张三", "email": "zhangsan@example.com"}
        
        # When
        result = self.user_service.create_user(user_data)
        
        # Then
        assert result.created_at == "2024-01-01 10:00:00"
```

### 集成测试 (Integration Tests)
**目标覆盖率: 80%+**

```python
# tests/integration/test_user_workflow.py
import pytest
from src.core.services import UserService
from src.interfaces.api import UserAPI
from tests.fixtures import real_database, real_email_service

class TestUserWorkflow:
    """用户完整工作流测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, real_database, real_email_service):
        """使用真实的数据库和邮件服务"""
        self.user_api = UserAPI(
            user_service=UserService(real_email_service),
            database=real_database
        )
    
    def test_complete_user_registration_workflow(self):
        """完整的用户注册流程测试"""
        # Given
        registration_data = {
            "name": "李四",
            "email": "lisi@example.com",
            "password": "SecurePass123!"
        }
        
        # When
        response = self.user_api.register(registration_data)
        
        # Then
        assert response.status_code == 201
        assert response.json()["user"]["name"] == "李四"
        
        # 验证数据库中确实创建了用户
        user = self.user_api.get_user_by_email("lisi@example.com")
        assert user is not None
        assert user.is_active is True
        
        # 验证发送了欢迎邮件
        # (通过邮件服务的日志或测试邮件系统验证)
```

### 端到端测试 (E2E Tests)
**目标覆盖率: 关键路径100%**

```python
# tests/e2e/test_system_workflow.py
import pytest
from selenium import webdriver
from tests.fixtures import test_server

class TestSystemWorkflow:
    """系统端到端测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_server):
        """启动测试服务器"""
        self.driver = webdriver.Chrome()
        self.base_url = test_server.url
        
    def teardown_method(self):
        """清理资源"""
        self.driver.quit()
    
    def test_user_can_complete_full_registration_and_login(self):
        """用户可以完成完整的注册和登录流程"""
        # 访问注册页面
        self.driver.get(f"{self.base_url}/register")
        
        # 填写注册表单
        self.driver.find_element("name", "name").send_keys("王五")
        self.driver.find_element("name", "email").send_keys("wangwu@example.com")
        self.driver.find_element("name", "password").send_keys("SecurePass123!")
        
        # 提交注册
        self.driver.find_element("type", "submit").click()
        
        # 验证注册成功
        success_message = self.driver.find_element("class", "success-message")
        assert "注册成功" in success_message.text
        
        # 登录验证
        self.driver.get(f"{self.base_url}/login")
        self.driver.find_element("name", "email").send_keys("wangwu@example.com")
        self.driver.find_element("name", "password").send_keys("SecurePass123!")
        self.driver.find_element("type", "submit").click()
        
        # 验证登录成功
        assert "dashboard" in self.driver.current_url
```

---

## 📊 覆盖率要求

### 覆盖率目标
| 测试类型 | 最低要求 | 目标 | 关键模块 |
|---------|---------|------|----------|
| **单元测试** | 80% | 90%+ | 95%+ |
| **集成测试** | 60% | 80%+ | 90%+ |
| **分支覆盖** | 70% | 85%+ | 90%+ |
| **函数覆盖** | 90% | 95%+ | 100% |

### 覆盖率检查
```bash
# 运行覆盖率测试
make coverage

# 生成HTML报告
make coverage-html

# 检查具体文件覆盖率
coverage report --show-missing

# 失败阈值设置
coverage report --fail-under=80
```

### 覆盖率配置
```ini
# .coveragerc
[run]
source = src
omit = 
    */tests/*
    */venv/*
    */migrations/*
    */settings/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = htmlcov
```

---

## 🛠️ 测试工具与框架

### 核心测试工具
```python
# requirements.txt 中的测试依赖
pytest==7.4.4           # 测试框架
pytest-cov==4.1.0       # 覆盖率插件
pytest-mock==3.12.0     # Mock插件
pytest-asyncio==0.21.1  # 异步测试
pytest-xdist==3.5.0     # 并行测试
factory-boy==3.3.0      # 测试数据工厂
```

### Pytest配置
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --strict-config
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80

markers =
    unit: 单元测试
    integration: 集成测试
    e2e: 端到端测试
    slow: 运行时间较长的测试
    database: 需要数据库的测试
```

---

## 🏭 测试数据管理

### 测试数据工厂
```python
# tests/factories.py
import factory
from src.core.models import User, Project

class UserFactory(factory.Factory):
    """用户测试数据工厂"""
    class Meta:
        model = User
    
    name = factory.Sequence(lambda n: f"用户{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.name}@example.com")
    age = factory.Faker('random_int', min=18, max=80)
    is_active = True
    created_at = factory.Faker('date_time')

class ProjectFactory(factory.Factory):
    """项目测试数据工厂"""
    class Meta:
        model = Project
    
    title = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=200)
    owner = factory.SubFactory(UserFactory)
    status = factory.Faker('random_element', elements=['active', 'inactive', 'pending'])

# 使用示例
def test_user_creation():
    user = UserFactory()
    assert user.name.startswith("用户")
    assert "@example.com" in user.email
    
def test_project_with_specific_owner():
    specific_user = UserFactory(name="特定用户")
    project = ProjectFactory(owner=specific_user)
    assert project.owner.name == "特定用户"
```

### 测试夹具（Fixtures）
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock
from src.core.services import UserService, EmailService
from src.config.settings import settings

@pytest.fixture
def mock_email_service():
    """模拟邮件服务"""
    service = Mock(spec=EmailService)
    service.send_email.return_value = True
    return service

@pytest.fixture
def user_service(mock_email_service):
    """用户服务夹具"""
    return UserService(email_service=mock_email_service)

@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "name": "测试用户",
        "email": "test@example.com",
        "age": 25
    }

@pytest.fixture(scope="session")
def test_database():
    """测试数据库"""
    # 创建临时测试数据库
    test_db = create_test_database()
    
    yield test_db
    
    # 清理
    cleanup_test_database(test_db)

@pytest.fixture(autouse=True)
def reset_database(test_database):
    """每个测试后重置数据库"""
    yield
    test_database.reset()
```

---

## 📝 测试编写指南

### 测试命名规范
```python
# ✅ 好的测试名称
def test_create_user_with_valid_data_should_return_user():
    """使用有效数据创建用户应该返回用户对象"""
    pass

def test_login_with_wrong_password_should_raise_authentication_error():
    """使用错误密码登录应该抛出认证错误"""
    pass

def test_calculate_discount_for_vip_user_should_apply_20_percent_discount():
    """为VIP用户计算折扣应该应用20%折扣"""
    pass

# ❌ 避免的命名
def test_user():
    pass

def test_login_fail():
    pass

def test_1():
    pass
```

### AAA模式（Arrange-Act-Assert）
```python
def test_user_service_creates_user_with_correct_attributes():
    """用户服务使用正确属性创建用户"""
    # Arrange (准备)
    user_data = {
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 30
    }
    email_service = Mock()
    user_service = UserService(email_service)
    
    # Act (执行)
    result = user_service.create_user(user_data)
    
    # Assert (断言)
    assert result.name == "张三"
    assert result.email == "zhangsan@example.com"
    assert result.age == 30
    assert result.created_at is not None
    email_service.send_welcome_email.assert_called_once_with("zhangsan@example.com")
```

### 参数化测试
```python
@pytest.mark.parametrize("email,expected", [
    ("valid@example.com", True),
    ("another.valid@test.org", True),
    ("invalid-email", False),
    ("@invalid.com", False),
    ("invalid@", False),
    ("", False),
])
def test_email_validation(email, expected):
    """测试邮箱验证的各种情况"""
    result = validate_email(email)
    assert result == expected
```

### 异常测试
```python
def test_divide_by_zero_should_raise_value_error():
    """除以零应该抛出ValueError"""
    with pytest.raises(ValueError) as exc_info:
        divide(10, 0)
    
    assert "不能除以零" in str(exc_info.value)

def test_invalid_user_data_should_raise_validation_error():
    """无效用户数据应该抛出验证错误"""
    invalid_data = {"name": "", "email": "invalid"}
    
    with pytest.raises(ValidationError) as exc_info:
        create_user(invalid_data)
    
    # 验证错误消息包含具体信息
    error_message = str(exc_info.value)
    assert "姓名不能为空" in error_message
    assert "邮箱格式无效" in error_message
```

---

## 🚀 CI/CD集成

### 测试在CI中的执行
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: make install
    
    - name: Run tests with coverage
      run: make coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

### 本地CI模拟
```bash
# 完整的本地CI检查
make ci

# 等价于
make env-check
make context
make quality
make test
make coverage
```

---

## 📊 测试监控与报告

### 测试报告生成
```bash
# 生成详细的测试报告
pytest --html=reports/pytest_report.html --self-contained-html

# 生成覆盖率报告
coverage html --directory=reports/coverage

# 生成性能报告
pytest --benchmark-only --benchmark-html=reports/benchmark.html
```

### 测试指标监控
- **测试通过率**: 目标100%
- **测试覆盖率**: 目标90%+
- **测试执行时间**: 单元测试<1s，集成测试<10s
- **测试维护性**: 定期审查和重构测试代码

---

## 🔄 测试维护

### 定期清理
- **移除过时测试**: 删除不再相关的测试
- **重构重复代码**: 提取公共测试工具
- **更新测试数据**: 保持测试数据的相关性
- **优化测试性能**: 减少不必要的资源消耗

### 测试债务管理
```bash
# 识别未测试的代码
coverage report --show-missing

# 识别脆弱的测试
pytest --lf  # 只运行上次失败的测试

# 识别慢测试
pytest --durations=10
```

---

## 🎯 测试最佳实践

### DO's (应该做的)
- ✅ 编写清晰、可读的测试名称
- ✅ 使用AAA模式组织测试
- ✅ 保持测试的独立性
- ✅ 优先测试公共接口而不是内部实现
- ✅ 使用适当的断言消息
- ✅ 保持测试的快速执行
- ✅ 定期重构和维护测试代码

### DON'Ts (不应该做的)
- ❌ 不要测试第三方库的功能
- ❌ 不要在测试中使用生产数据
- ❌ 不要编写依赖执行顺序的测试
- ❌ 不要忽略失败的测试
- ❌ 不要为了覆盖率而编写无意义的测试
- ❌ 不要在测试中使用随机数据（除非必要）

**记住：好的测试是代码质量的保证，也是重构的安全网！** 