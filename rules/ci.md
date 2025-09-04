# CI/CD校验规则 (ci.md)

## 🎯 CI/CD理念

### 1. **快速反馈**
- 每次代码变更都触发自动化检查
- 检查失败立即通知开发者
- 提供清晰的错误信息和修复建议

### 2. **质量门禁**
- 代码质量不达标禁止合并
- 测试覆盖率必须达到要求
- 安全扫描必须通过

### 3. **环境一致性**
- 开发、测试、生产环境保持一致
- 使用容器化保证环境统一
- 基础设施即代码(IaC)

---

## 🛠️ 本地CI模拟

### 完整CI流程
```bash
# 一键运行完整CI检查
make ci

# 等价于以下步骤：
make env-check      # 环境检查
make context        # 项目上下文加载
make quality        # 代码质量检查
make test           # 单元测试
make coverage       # 覆盖率测试
```

### 分步骤检查
```bash
# 1. 环境检查
make env-check
# 检查项：
# - 虚拟环境是否激活
# - 依赖是否完整安装
# - Git分支是否正确
# - 开发工具是否可用

# 2. 代码质量检查
make quality
# 检查项：
# - 代码格式化 (black)
# - 代码风格 (flake8)
# - 类型检查 (mypy)
# - 安全扫描 (bandit)
# - 复杂度分析 (radon)

# 3. 测试验证
make test
# 要求：
# - 所有单元测试通过
# - 集成测试通过
# - 性能测试在可接受范围内

# 4. 覆盖率验证
make coverage
# 要求：
# - 代码覆盖率 >= 80%
# - 分支覆盖率 >= 70%
# - 新代码覆盖率 >= 90%
```

---

## 🔍 质量门禁标准

### 代码质量指标
| 指标 | 最低要求 | 目标值 | 阻断条件 |
|------|---------|-------|----------|
| **代码覆盖率** | 80% | 90% | <80% |
| **分支覆盖率** | 70% | 85% | <70% |
| **圈复杂度** | ≤10 | ≤6 | >10 |
| **重复代码率** | ≤5% | ≤2% | >5% |
| **技术债务** | ≤2h | ≤30min | >4h |
| **安全漏洞** | 0 | 0 | >0 |

### 检查配置

#### 1. **代码格式检查**
```bash
# .flake8配置
[flake8]
max-line-length = 88
max-complexity = 10
ignore = 
    E203,  # whitespace before ':'
    W503,  # line break before binary operator
exclude = 
    .git,
    __pycache__,
    venv,
    .venv,
    migrations

# 检查命令
flake8 src/ tests/ scripts/
```

#### 2. **类型检查配置**
```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy-tests.*]
disallow_untyped_defs = False

# 检查命令
mypy src/
```

#### 3. **安全检查配置**
```yaml
# .bandit
exclude_dirs: ['tests', 'venv', '.venv']
tests: ['B101', 'B102', 'B103', 'B104', 'B105', 'B106', 'B107']
skips: ['B101']  # 如果需要跳过特定检查

# 检查命令
bandit -r src/ -f json
```

#### 4. **复杂度检查配置**
```bash
# 复杂度检查
radon cc src/ --min=B
radon mi src/ --min=B

# 圈复杂度等级
# A: 1-5 (低复杂度)
# B: 6-10 (中等复杂度)
# C: 11-20 (高复杂度)
# D: 21-30 (极高复杂度)
# E: 31-40 (无法维护)
# F: 41+ (极度危险)
```

---

## 🧪 测试策略

### 测试金字塔
```
     /\
    /  \     E2E Tests (10%)
   /____\    - 关键用户路径
  /      \   - 端到端业务流程
 /        \  
/__________\  Integration Tests (20%)
/          \  - 模块间交互
/            \ - 外部服务集成
/              \
/______________\ Unit Tests (70%)
                 - 单元逻辑验证
                 - 边界条件测试
```

### 测试执行策略
```bash
# 1. 快速测试（提交前）
pytest tests/unit/ -x --ff

# 2. 完整测试（CI中）
pytest tests/ --cov=src --cov-report=xml

# 3. 性能测试（夜间）
pytest tests/performance/ --benchmark-only

# 4. 集成测试（部署前）
pytest tests/integration/ --env=staging
```

### 测试环境隔离
```python
# conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture(scope="session")
def test_database():
    """测试数据库，每个测试会话创建一次"""
    db = create_test_database()
    yield db
    cleanup_test_database(db)

@pytest.fixture(autouse=True)
def isolate_tests(test_database):
    """自动隔离每个测试"""
    transaction = test_database.begin()
    yield
    transaction.rollback()

@pytest.fixture
def mock_external_service():
    """模拟外部服务"""
    with Mock() as mock:
        yield mock
```

---

## 🚀 CI流水线配置

### GitHub Actions配置
```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

env:
  PYTHON_VERSION: "3.11"

jobs:
  lint-and-format:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    
    - name: Install dependencies
      run: make install
    
    - name: Check code formatting
      run: |
        make format
        git diff --exit-code
    
    - name: Lint code
      run: make lint
    
    - name: Type check
      run: make typecheck

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: make install
    
    - name: Security scan
      run: make security
    
    - name: Complexity check
      run: make complexity

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-type: [unit, integration]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: make install
    
    - name: Run ${{ matrix.test-type }} tests
      run: |
        if [ "${{ matrix.test-type }}" = "unit" ]; then
          pytest tests/unit/ --cov=src --cov-report=xml
        else
          pytest tests/integration/
        fi
    
    - name: Upload coverage to Codecov
      if: matrix.test-type == 'unit'
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  build-and-package:
    needs: [lint-and-format, security-scan, test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Build package
      run: |
        pip install build
        python -m build
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: python-package
        path: dist/
```

### GitLab CI配置
```yaml
# .gitlab-ci.yml
stages:
  - validate
  - test
  - build
  - deploy

variables:
  PYTHON_VERSION: "3.11"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

before_script:
  - python3 -m venv venv
  - source venv/bin/activate
  - pip install --upgrade pip
  - make install

lint-and-format:
  stage: validate
  script:
    - make format
    - git diff --exit-code
    - make lint
    - make typecheck
  only:
    - merge_requests
    - main
    - develop

security-check:
  stage: validate
  script:
    - make security
    - make complexity
  only:
    - merge_requests
    - main
    - develop

unit-tests:
  stage: test
  script:
    - make coverage
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  only:
    - merge_requests
    - main
    - develop

integration-tests:
  stage: test
  services:
    - postgres:13
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_pass
  script:
    - pytest tests/integration/
  only:
    - merge_requests
    - main
    - develop

build-package:
  stage: build
  script:
    - python -m build
  artifacts:
    paths:
      - dist/
  only:
    - main
```

---

## 📊 CI监控与报告

### 关键指标监控
```bash
# CI执行时间监控
- 总执行时间 < 10分钟
- 单元测试 < 2分钟
- 集成测试 < 5分钟
- 安全扫描 < 1分钟

# CI成功率监控
- 主分支CI成功率 > 95%
- PR CI成功率 > 90%
- 夜间完整测试成功率 > 98%

# 质量趋势监控
- 代码覆盖率趋势
- 技术债务变化
- 漏洞数量趋势
- 性能指标变化
```

### 报告生成
```bash
# 生成CI报告
make ci-report

# 包含以下内容：
# - 测试执行摘要
# - 覆盖率报告
# - 质量门禁状态
# - 性能基准对比
# - 安全扫描结果
```

### 失败通知
```yaml
# 通知配置示例
notifications:
  slack:
    channels:
      - dev-team
      - ci-alerts
    conditions:
      - failure
      - recovery
  
  email:
    recipients:
      - tech-lead@company.com
    conditions:
      - failure
      - first_failure
```

---

## 🔧 环境管理

### 开发环境配置
```bash
# 开发环境检查清单
make env-check

# 包含检查项：
- Python版本兼容性
- 虚拟环境状态
- 必需依赖安装
- 环境变量配置
- 开发工具可用性
- Git配置正确性
```

### 依赖管理
```txt
# requirements.txt
# 生产依赖
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23

# requirements-dev.txt  
# 开发依赖
black==23.12.1
flake8==7.0.0
mypy==1.8.0
pytest==7.4.4
pytest-cov==4.1.0
bandit==1.7.5
radon==6.0.1

# 依赖更新策略
- 定期更新补丁版本
- 谨慎更新次要版本
- 重大版本升级需要完整测试
```

### 环境变量管理
```bash
# .env.example
# 复制到.env并填写实际值
DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key
API_KEY=your-api-key

# 环境变量验证
make validate-env
```

---

## 🚨 故障处理

### CI失败处理流程
```bash
# 1. 快速识别问题
make ci-debug

# 2. 本地复现问题
make clean
make ci

# 3. 修复问题
make fix      # 自动修复格式问题
make test     # 运行相关测试

# 4. 验证修复
make ci

# 5. 重新提交
git add .
git commit --amend
git push --force-with-lease
```

### 常见CI失败及解决方案

#### 1. **代码格式问题**
```bash
# 错误：Black格式化检查失败
# 解决：
make format
git add .
git commit --amend --no-edit
```

#### 2. **测试失败**
```bash
# 错误：单元测试失败
# 解决：
# 1. 查看测试失败详情
pytest tests/ -v --tb=short

# 2. 修复失败的测试
# 3. 确保新代码有测试覆盖
```

#### 3. **覆盖率不足**
```bash
# 错误：代码覆盖率低于80%
# 解决：
# 1. 查看覆盖率报告
coverage html
open htmlcov/index.html

# 2. 为未覆盖代码添加测试
# 3. 验证覆盖率提升
make coverage
```

#### 4. **安全漏洞**
```bash
# 错误：Bandit发现安全问题
# 解决：
# 1. 查看详细安全报告
bandit -r src/ -f txt

# 2. 修复安全问题或添加忽略注释
# 3. 重新验证
make security
```

### 紧急绕过机制
```bash
# 仅在紧急情况下使用
# 需要团队负责人批准

# 临时跳过CI检查（不推荐）
git commit -m "fix: emergency fix" --no-verify

# 创建hotfix分支绕过PR流程
git checkout -b hotfix/emergency
# 修复完成后直接合并到main
```

---

## 📈 CI优化策略

### 执行时间优化
```bash
# 1. 并行执行
pytest tests/ -n auto  # 并行运行测试

# 2. 缓存依赖
# GitHub Actions中使用cache action
# 本地使用pip缓存

# 3. 增量检查
# 只对变更文件运行检查
git diff --name-only HEAD~1 | grep '\.py$' | xargs flake8

# 4. 分层检查
# 快速检查优先，慢速检查放到夜间
```

### 资源优化
```yaml
# 合理配置CI资源
jobs:
  test:
    runs-on: ubuntu-latest
    # 使用合适的机器配置
    # 避免过度配置浪费资源
```

### 成本优化
```bash
# 1. 按需触发
# 只在必要时运行完整CI
# 草稿PR跳过某些检查

# 2. 复用构建产物
# 缓存依赖安装结果
# 复用构建镜像

# 3. 智能调度
# 夜间运行重型测试
# 工作时间优先快速反馈
```

---

## 🎯 CI最佳实践

### 设计原则
- ✅ **快速反馈**: CI应该在5-10分钟内完成
- ✅ **可靠稳定**: CI结果应该一致可重复
- ✅ **易于调试**: 失败信息应该清晰明确
- ✅ **安全可控**: 敏感信息应该妥善保护

### 流程优化
- ✅ 分层执行，快速检查优先
- ✅ 并行运行，提高执行效率
- ✅ 缓存机制，减少重复工作
- ✅ 增量检查，只检查变更部分

### 团队协作
- ✅ CI失败及时修复，不能累积
- ✅ 共享CI配置知识，避免单点依赖
- ✅ 定期review CI流程，持续改进
- ✅ 文档化CI故障处理流程

**记住：良好的CI/CD是软件质量的基石，也是团队效率的倍增器！** 