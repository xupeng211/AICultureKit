# Git提交规范与分支策略 (git.md)

## 🎯 Git工作流原则

### 1. **分支策略清晰**
- 主分支保护，禁止直接推送
- 功能分支短命，及时合并
- 提交历史清晰，便于追溯

### 2. **提交规范统一**
- 使用语义化提交信息
- 原子性提交，一次解决一个问题
- 提交前必须通过所有检查

### 3. **代码审查必需**
- 所有代码变更都需要审查
- 自动化检查作为审查基础
- 人工审查关注业务逻辑和架构

---

## 🌳 分支策略

### 主分支结构
```
main/master     ← 生产环境代码，受保护
├── develop     ← 开发集成分支
├── feature/*   ← 功能开发分支
├── hotfix/*    ← 紧急修复分支
└── release/*   ← 发布准备分支
```

### 分支使用规范

#### 1. **主分支 (main/master)**
```bash
# 特点
- 始终保持可部署状态
- 受保护，禁止直接推送
- 只接受来自release或hotfix的合并

# 保护规则
- 要求PR审查
- 要求状态检查通过
- 要求分支更新
- 禁止强制推送
```

#### 2. **开发分支 (develop)**
```bash
# 特点
- 最新的开发代码
- 功能分支的合并目标
- 定期合并到release分支

# 使用场景
git checkout develop
git pull origin develop
# 确保develop分支是最新的
```

#### 3. **功能分支 (feature/***)**
```bash
# 命名规范
feature/user-authentication
feature/payment-integration
feature/issue-123-fix-login-bug

# 创建和使用
git checkout develop
git pull origin develop
git checkout -b feature/user-authentication

# 开发完成后
git checkout develop
git pull origin develop
git checkout feature/user-authentication
git rebase develop  # 或者 git merge develop
git push origin feature/user-authentication
# 创建PR到develop分支
```

#### 4. **发布分支 (release/***)**
```bash
# 命名规范
release/v1.2.0
release/2024-01-15

# 创建发布分支
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# 发布准备（版本号更新、文档更新等）
# 测试完成后合并到main和develop
git checkout main
git merge release/v1.2.0
git tag v1.2.0
git checkout develop
git merge release/v1.2.0
```

#### 5. **热修复分支 (hotfix/***)**
```bash
# 命名规范
hotfix/critical-security-fix
hotfix/issue-456-payment-bug

# 创建热修复分支
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# 修复完成后合并到main和develop
git checkout main
git merge hotfix/critical-security-fix
git tag v1.2.1
git checkout develop
git merge hotfix/critical-security-fix
```

---

## 📝 提交规范

### Conventional Commits格式
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### 提交类型 (type)
| 类型 | 描述 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(auth): 添加用户登录功能` |
| `fix` | Bug修复 | `fix(api): 修复用户数据查询错误` |
| `docs` | 文档更新 | `docs(readme): 更新安装指南` |
| `style` | 代码格式 | `style: 修复代码格式问题` |
| `refactor` | 代码重构 | `refactor(user): 重构用户服务模块` |
| `perf` | 性能优化 | `perf(db): 优化数据库查询性能` |
| `test` | 测试相关 | `test(auth): 添加登录功能测试` |
| `chore` | 构建/工具 | `chore: 更新依赖版本` |
| `ci` | CI/CD配置 | `ci: 添加自动化测试流程` |
| `build` | 构建系统 | `build: 更新webpack配置` |
| `revert` | 回退提交 | `revert: 回退用户认证功能` |

### 范围 (scope)
```bash
# 常用范围示例
(auth)      # 认证模块
(user)      # 用户模块
(api)       # API接口
(ui)        # 用户界面
(db)        # 数据库
(config)    # 配置
(test)      # 测试
(docs)      # 文档
(ci)        # 持续集成
```

### 描述 (description)
- 使用现在时态："添加功能"而不是"添加了功能"
- 使用命令式语气："修复bug"而不是"修复了bug"
- 首字母小写
- 末尾不加句号
- 限制在50个字符以内

### 提交示例

#### ✅ 好的提交示例
```bash
# 功能添加
feat(auth): 实现JWT认证机制

添加JWT token生成和验证功能
- 用户登录时生成token
- 中间件验证token有效性
- 支持token刷新机制

Closes #123

# Bug修复
fix(api): 修复用户查询接口返回null的问题

当用户ID不存在时，接口应该返回404错误而不是null
修改了UserController.getUserById方法的错误处理

# 文档更新
docs(api): 更新用户接口文档

- 添加认证参数说明
- 更新错误码说明
- 添加请求示例

# 重构
refactor(user): 重构用户服务层

- 拆分UserService为多个专门的服务类
- 改善代码可测试性
- 减少类之间的耦合

# 性能优化
perf(db): 优化用户查询性能

- 添加用户表索引
- 优化SQL查询语句
- 减少N+1查询问题

查询时间从500ms减少到50ms
```

#### ❌ 避免的提交示例
```bash
# 描述不清晰
fix: 修复bug
update: 更新代码
change: 改变了一些东西

# 一次提交包含多个不相关的更改
feat: 添加用户认证和修复支付bug和更新文档

# 使用错误的时态
fix: 修复了登录问题
feat: 添加了新功能

# 没有描述具体内容
chore: 更新
docs: 修改
test: 测试
```

---

## 🔧 自动化工具集成

### Pre-commit钩子
```bash
# 安装pre-commit
pip install pre-commit

# 配置 .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: make-format
        name: Code formatting
        entry: make format
        language: system
        pass_filenames: false
      
      - id: make-lint
        name: Code linting
        entry: make lint
        language: system
        pass_filenames: false
      
      - id: make-test
        name: Run tests
        entry: make test
        language: system
        pass_filenames: false

# 安装钩子
pre-commit install
```

### Commit消息模板
```bash
# 设置commit模板
git config commit.template .gitmessage

# .gitmessage内容
# <type>(<scope>): <description>
# 
# Explain why this change is being made
# 
# Provide links to any relevant tickets, articles or other resources
# 
# Use the imperative mood in the subject line
# Limit the first line to 72 characters
# Reference any ticket numbers in the footer
```

### 自动化检查
```bash
# Makefile中的Git相关检查
.PHONY: check-commit
check-commit:
	@echo "检查提交信息格式..."
	@git log --oneline -1 | grep -E "^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\(.+\))?: .+"

.PHONY: check-branch
check-branch:
	@echo "检查当前分支..."
	@branch=$$(git branch --show-current); \
	if [ "$$branch" = "main" ] || [ "$$branch" = "master" ]; then \
		echo "❌ 不能直接在主分支上开发"; \
		exit 1; \
	fi
```

---

## 🔄 工作流程

### 日常开发流程
```bash
# 1. 开始新功能
git checkout develop
git pull origin develop
git checkout -b feature/new-awesome-feature

# 2. 开发过程中
# 经常提交，保持提交原子性
git add .
git commit -m "feat(feature): 添加基础功能框架"

# 开发过程中定期同步
git fetch origin
git rebase origin/develop

# 3. 功能完成
# 运行完整检查
make prepush

# 推送功能分支
git push origin feature/new-awesome-feature

# 4. 创建Pull Request
# 在GitHub/Gitee上创建PR
# 等待代码审查和自动化检查
```

### 合并策略
```bash
# 1. Merge Commit (保留分支历史)
git checkout develop
git merge feature/new-feature

# 2. Rebase and Merge (线性历史)
git checkout feature/new-feature
git rebase develop
git checkout develop
git merge feature/new-feature --ff-only

# 3. Squash and Merge (压缩提交)
git checkout develop
git merge --squash feature/new-feature
git commit -m "feat(feature): 添加新功能"
```

---

## 🚨 错误处理和回滚

### 常见问题处理

#### 1. **提交信息错误**
```bash
# 修改最后一次提交信息
git commit --amend -m "正确的提交信息"

# 修改多个提交信息
git rebase -i HEAD~3  # 修改最近3个提交
```

#### 2. **错误的文件提交**
```bash
# 从暂存区移除文件
git reset HEAD <file>

# 从提交中移除文件但保留本地更改
git reset --soft HEAD~1
git reset HEAD <file>
git commit
```

#### 3. **分支操作错误**
```bash
# 切换到错误的分支
git checkout correct-branch
git cherry-pick <commit-hash>  # 转移提交

# 删除错误的分支
git branch -D wrong-branch
```

### 紧急回滚
```bash
# 1. 回滚到特定提交
git reset --hard <commit-hash>

# 2. 创建反向提交
git revert <commit-hash>

# 3. 紧急热修复
git checkout main
git checkout -b hotfix/emergency-fix
# 修复问题
git commit -m "fix: 紧急修复关键问题"
# 立即合并到main并部署
```

---

## 📊 Git最佳实践

### 分支管理
- ✅ 保持分支名称有意义且简洁
- ✅ 及时删除已合并的功能分支
- ✅ 定期同步主分支的更改
- ✅ 使用受保护分支保护重要分支

### 提交管理
- ✅ 提交前运行自动化检查
- ✅ 编写清晰的提交信息
- ✅ 保持提交的原子性
- ✅ 定期整理提交历史

### 协作管理
- ✅ 及时响应代码审查
- ✅ 解决合并冲突后进行测试
- ✅ 保持开放的沟通
- ✅ 分享最佳实践和经验

### 性能优化
```bash
# 清理本地仓库
git gc --prune=now
git remote prune origin

# 优化仓库大小
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 查看仓库状态
git status
git log --oneline --graph --decorate --all
```

---

## 🎯 代码审查清单

### 审查前准备
- [ ] 确保CI检查全部通过
- [ ] 本地运行完整测试套件
- [ ] 检查提交信息格式正确
- [ ] 确保分支同步最新代码

### 审查要点
- [ ] **功能性**: 代码是否实现了预期功能
- [ ] **可读性**: 代码逻辑清晰，命名合理
- [ ] **测试覆盖**: 新功能有相应测试
- [ ] **性能影响**: 是否有性能问题
- [ ] **安全性**: 是否引入安全风险
- [ ] **兼容性**: 是否破坏现有功能

### 审查反馈
```bash
# 建设性反馈示例
# ✅ 好的反馈
"建议将这个长函数拆分为几个小函数，提高可读性"
"这里可以考虑使用缓存来提高性能"
"测试用例中缺少边界条件的测试"

# ❌ 避免的反馈
"这段代码不好"
"改一下"
"有问题"
```

---

## 📈 Git度量指标

### 关键指标
- **提交频率**: 每天至少1次有意义的提交
- **分支生命周期**: 功能分支不超过1周
- **代码审查时间**: 24小时内响应
- **合并成功率**: 95%以上无冲突合并
- **回滚频率**: 月回滚次数<5%

### 监控工具
```bash
# 提交统计
git log --since="1 month ago" --pretty=format:"%h %an %s" --shortstat

# 贡献者统计
git shortlog -sn --since="1 month ago"

# 分支状态
git for-each-ref --format='%(refname:short) %(committerdate)' refs/heads

# 文件变更统计
git log --stat --since="1 month ago"
```

**记住：良好的Git实践是团队协作的基础，也是项目成功的保障！** 