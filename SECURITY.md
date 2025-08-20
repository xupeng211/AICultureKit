# 安全配置指南

## 环境变量配置
在实际部署时，请设置以下环境变量：

```bash
# 数据库配置
export DB_HOST=your_db_host
export DB_USER=your_db_user
export DB_PASSWORD=your_db_password

# API配置
export API_KEY=your_api_key
export SECRET_TOKEN=your_secret_token

# 邮件配置
export SENDER_EMAIL=your_sender_email
export SENDER_PASSWORD=your_sender_password

# 加密配置
export ENCRYPTION_KEY=your_encryption_key
```

## 安全最佳实践
1. 永远不要在代码中硬编码敏感信息
2. 使用环境变量或安全的配置管理系统
3. 定期轮换密钥和令牌
4. 对敏感数据进行加密存储
5. 实施最小权限原则
6. 定期进行安全审计

## 演示数据说明
本项目中的所有敏感信息都已替换为安全的占位符：
- 邮箱地址：demo@placeholder.local
- IP地址：192.168.1.XXX
- 电话号码：+1-XXX-XXX-XXXX
- 密码：DEMO_PASSWORD
- API密钥：DEMO_API_KEY
