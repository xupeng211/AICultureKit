# AICultureKit API 参考文档

## 核心模块 (aiculture.core)

### CultureConfig

文化配置管理类，负责加载和管理项目的文化配置信息。

#### 构造函数

```python
CultureConfig(config_path: Optional[str] = None)
```

**参数:**
- `config_path`: 配置文件路径，默认为 "aiculture.yaml"

#### 方法

##### get_principle(key: str) -> Any

获取指定的文化原则。

**参数:**
- `key`: 原则键名

**返回:**
- 对应的原则值

**示例:**
```python
config = CultureConfig()
principle = config.get_principle("code_quality")
```

### QualityTools

代码质量工具管理类，提供统一的质量检查接口。

#### 构造函数

```python
QualityTools(project_path: str = ".")
```

**参数:**
- `project_path`: 项目根目录路径，默认为当前目录

#### 方法

##### run_flake8() -> Dict[str, Any]

运行flake8代码风格检查。

**返回:**
- 包含检查结果的字典

##### run_mypy() -> Dict[str, Any]

运行mypy类型检查。

**返回:**
- 包含类型检查结果的字典

##### run_pytest() -> Dict[str, Any]

运行pytest测试套件。

**返回:**
- 包含测试结果的字典

### ProjectTemplate

项目模板生成类，用于创建符合标准的项目结构。

#### 构造函数

```python
ProjectTemplate()
```

#### 方法

##### generate_project(name: str, template_type: str = "python") -> None

生成新项目。

**参数:**
- `name`: 项目名称
- `template_type`: 模板类型，支持 "python", "javascript"

**示例:**
```python
template = ProjectTemplate()
template.generate_project("my-project", "python")
```

## 数据治理模块 (aiculture.data_governance_culture)

### DataGovernanceManager

数据治理管理器，提供数据隐私、质量和合规检查功能。

#### 构造函数

```python
DataGovernanceManager(project_path: Path)
```

**参数:**
- `project_path`: 项目根目录路径

#### 方法

##### scan_project_for_privacy_issues() -> Dict[str, Any]

扫描项目中的隐私问题。

**返回:**
- 包含隐私问题详情的字典，按严重程度分类

##### validate_data_quality(data_path: Path) -> Dict[str, Any]

验证数据质量。

**参数:**
- `data_path`: 数据文件或目录路径

**返回:**
- 数据质量验证结果

## 可访问性模块 (aiculture.accessibility_culture)

### AccessibilityCultureManager

可访问性文化管理器，提供国际化和无障碍设计检查。

#### 构造函数

```python
AccessibilityCultureManager(project_path: Path)
```

**参数:**
- `project_path`: 项目根目录路径

#### 方法

##### check_project_accessibility() -> Dict[str, Any]

检查项目的可访问性问题。

**返回:**
- 包含可访问性问题的详细报告

##### generate_accessibility_report() -> Dict[str, Any]

生成可访问性报告。

**返回:**
- 格式化的可访问性报告

## 监控配置模块 (aiculture.monitoring_config)

### MonitoringConfigManager

监控配置管理器，用于配置项目的监控和告警。

#### 构造函数

```python
MonitoringConfigManager(project_path: Path)
```

**参数:**
- `project_path`: 项目根目录路径

#### 方法

##### add_metric(name: str, metric: MetricConfig) -> None

添加监控指标。

**参数:**
- `name`: 指标名称
- `metric`: 指标配置对象

##### generate_prometheus_config() -> Dict[str, Any]

生成Prometheus配置。

**返回:**
- Prometheus配置字典

##### generate_grafana_dashboard(title: str) -> Dict[str, Any]

生成Grafana仪表板配置。

**参数:**
- `title`: 仪表板标题

**返回:**
- Grafana仪表板配置

## 数据目录模块 (aiculture.data_catalog)

### DataCatalog

数据目录管理器，用于管理和追踪项目中的数据资产。

#### 构造函数

```python
DataCatalog(project_path: Path)
```

**参数:**
- `project_path`: 项目根目录路径

#### 方法

##### scan_data_files() -> None

扫描项目中的数据文件并添加到目录中。

##### add_asset(key: str, asset: DataAsset) -> None

添加数据资产。

**参数:**
- `key`: 资产键名
- `asset`: 数据资产对象

##### search_assets(**kwargs) -> List[DataAsset]

搜索数据资产。

**参数:**
- `**kwargs`: 搜索条件（如tags、file_type、name_pattern等）

**返回:**
- 匹配的数据资产列表

## 国际化模块 (aiculture.i18n)

### 函数

#### set_locale(locale: str) -> None

设置当前语言环境。

**参数:**
- `locale`: 语言代码（如 'en', 'zh'）

#### get_current_locale() -> str

获取当前语言环境。

**返回:**
- 当前语言代码

#### _(key: str, **kwargs) -> str

翻译函数，获取指定键的翻译文本。

**参数:**
- `key`: 翻译键
- `**kwargs`: 翻译参数

**返回:**
- 翻译后的文本

**示例:**
```python
from aiculture.i18n import _, set_locale

set_locale('zh')
message = _('welcome', name='用户')
```

## 使用示例

### 基本项目初始化

```python
from aiculture.core import ProjectTemplate, CultureConfig

# 创建新项目
template = ProjectTemplate()
template.generate_project("my-ai-project", "python")

# 加载配置
config = CultureConfig("my-ai-project/aiculture.yaml")
principles = config.get_principle("development_principles")
```

### 质量检查

```python
from aiculture.core import QualityTools

tools = QualityTools("./my-project")

# 运行所有质量检查
flake8_result = tools.run_flake8()
mypy_result = tools.run_mypy()
test_result = tools.run_pytest()

print(f"代码风格检查: {'通过' if flake8_result['success'] else '失败'}")
print(f"类型检查: {'通过' if mypy_result['success'] else '失败'}")
print(f"测试结果: {test_result['summary']}")
```

### 数据治理

```python
from pathlib import Path
from aiculture.data_governance_culture import DataGovernanceManager

manager = DataGovernanceManager(Path("./my-project"))

# 扫描隐私问题
privacy_issues = manager.scan_project_for_privacy_issues()
print(f"发现 {len(privacy_issues['issues'])} 个隐私问题")

# 按严重程度查看
high_risk = privacy_issues['by_severity']['high']
print(f"高风险问题: {len(high_risk)} 个")
```

## 错误处理

所有API方法都会抛出适当的异常：

- `FileNotFoundError`: 当指定的文件或目录不存在时
- `ValueError`: 当参数值无效时
- `PermissionError`: 当没有足够权限访问文件时
- `ConfigurationError`: 当配置文件格式错误时

建议在使用API时进行适当的异常处理：

```python
try:
    config = CultureConfig("invalid-path.yaml")
except FileNotFoundError:
    print("配置文件不存在，使用默认配置")
    config = CultureConfig()
```
