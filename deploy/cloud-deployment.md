# 🌩️ AICultureKit 云部署指南

## 支持的云平台

### 🔵 阿里云 (推荐)
- **容器服务ACK**: Kubernetes集群部署
- **函数计算FC**: Serverless部署
- **容器镜像服务**: 私有镜像仓库
- **云数据库**: RDS、Redis集成

### 🟢 腾讯云
- **容器服务TKE**: Kubernetes部署
- **云函数SCF**: 事件驱动部署
- **容器镜像服务**: TCR私有仓库

### 🟠 AWS
- **EKS**: Kubernetes服务
- **Lambda**: 无服务器部署
- **ECR**: 容器镜像仓库
- **ECS**: 容器服务

### 🔷 Azure
- **AKS**: Azure Kubernetes服务
- **Container Instances**: 容器实例
- **Functions**: 无服务器计算

## 一键部署脚本

### 阿里云ACK部署

```bash
#!/bin/bash
# deploy/aliyun-ack-deploy.sh

# 1. 构建和推送镜像
docker build -t registry.cn-hangzhou.aliyuncs.com/your-namespace/aiculture-kit:latest .
docker push registry.cn-hangzhou.aliyuncs.com/your-namespace/aiculture-kit:latest

# 2. 部署到K8s
kubectl apply -f deploy/k8s/

# 3. 检查部署状态
kubectl get pods -l app=aiculture-kit
kubectl get svc aiculture-kit-service
```

### Docker Compose云部署

```bash
#!/bin/bash
# deploy/docker-compose-deploy.sh

# 1. 拉取最新代码
git pull origin main

# 2. 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 3. 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 4. 健康检查
docker-compose -f docker-compose.prod.yml ps
```

## Kubernetes配置示例

### 部署配置
```yaml
# deploy/k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aiculture-kit
  labels:
    app: aiculture-kit
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aiculture-kit
  template:
    metadata:
      labels:
        app: aiculture-kit
    spec:
      containers:
      - name: aiculture-kit
        image: your-registry/aiculture-kit:latest
        ports:
        - containerPort: 8000
        env:
        - name: APP_ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 服务配置
```yaml
# deploy/k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: aiculture-kit-service
spec:
  selector:
    app: aiculture-kit
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### 配置管理
```yaml
# deploy/k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aiculture-config
data:
  APP_ENV: "production"
  LOG_LEVEL: "INFO"
  ENABLE_METRICS: "true"
---
apiVersion: v1
kind: Secret
metadata:
  name: aiculture-secrets
type: Opaque
data:
  database-url: <base64-encoded-value>
  api-key: <base64-encoded-value>
```

## 环境变量管理

### 生产环境配置
```bash
# .env.production
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# 数据库配置
DATABASE_URL=postgresql://user:pass@rds-instance:5432/db
REDIS_URL=redis://redis-cluster:6379/0

# 监控和日志
PROMETHEUS_ENDPOINT=http://prometheus:9090
ELASTICSEARCH_URL=http://elasticsearch:9200

# 安全配置
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
ENCRYPTION_KEY=your-encryption-key
```

## 监控和日志

### Prometheus监控
```yaml
# deploy/monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'aiculture-kit'
    static_configs:
      - targets: ['aiculture-kit-service:8000']
    metrics_path: '/metrics'
```

### ELK日志收集
```yaml
# deploy/logging/filebeat.yml
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  processors:
  - add_kubernetes_metadata:
      host: ${NODE_NAME}
      matchers:
      - logs_path:
          logs_path: "/var/lib/docker/containers/"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

## 自动化部署流程

### GitOps工作流
```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Configure cloud credentials
      uses: aliyun/configure-kubectl-action@v1
      with:
        access-key-id: ${{ secrets.ALIYUN_ACCESS_KEY_ID }}
        access-key-secret: ${{ secrets.ALIYUN_ACCESS_KEY_SECRET }}
        cluster-id: ${{ secrets.K8S_CLUSTER_ID }}

    - name: Build and push image
      run: |
        docker build -t ${{ secrets.REGISTRY_URL }}/aiculture-kit:${{ github.ref_name }} .
        docker push ${{ secrets.REGISTRY_URL }}/aiculture-kit:${{ github.ref_name }}

    - name: Deploy to Kubernetes
      run: |
        sed -i 's|IMAGE_TAG|${{ github.ref_name }}|g' deploy/k8s/deployment.yaml
        kubectl apply -f deploy/k8s/

    - name: Verify deployment
      run: |
        kubectl rollout status deployment/aiculture-kit
        kubectl get pods -l app=aiculture-kit
```

## 成本优化策略

### 1. 资源优化
- **水平扩展**: 根据负载自动调整Pod数量
- **垂直扩展**: 动态调整CPU/内存资源
- **预留实例**: 使用云服务商的预留实例降低成本

### 2. 存储优化
- **对象存储**: 静态文件使用OSS/S3
- **缓存层**: Redis集群减少数据库压力
- **CDN加速**: 全球内容分发网络

### 3. 网络优化
- **负载均衡**: ALB/CLB智能流量分发
- **内网通信**: 服务间通过内网通信降低费用

## 安全最佳实践

### 1. 网络安全
```yaml
# deploy/security/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: aiculture-network-policy
spec:
  podSelector:
    matchLabels:
      app: aiculture-kit
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8000
```

### 2. 密钥管理
- **Kubernetes Secrets**: 敏感信息加密存储
- **云密钥管理**: 使用KMS等服务管理密钥
- **定期轮换**: 自动化密钥轮换机制

## 灾难恢复

### 备份策略
```bash
#!/bin/bash
# scripts/backup.sh

# 1. 数据库备份
kubectl exec -it postgres-pod -- pg_dump dbname > backup-$(date +%Y%m%d).sql

# 2. 配置备份
kubectl get configmaps,secrets -o yaml > config-backup-$(date +%Y%m%d).yaml

# 3. 上传到云存储
aws s3 cp backup-$(date +%Y%m%d).sql s3://backup-bucket/
```

### 故障恢复
```bash
#!/bin/bash
# scripts/disaster-recovery.sh

# 1. 恢复数据库
kubectl exec -it postgres-pod -- psql dbname < backup-latest.sql

# 2. 重新部署应用
kubectl rollout restart deployment/aiculture-kit

# 3. 验证服务
kubectl get pods -l app=aiculture-kit
curl -f http://service-endpoint/health
```

## 总结

AICultureKit的云部署架构具备以下优势：

✅ **自动化程度高**: GitOps + CI/CD全自动部署
✅ **可靠性强**: 健康检查 + 自动恢复机制
✅ **可扩展性好**: 水平/垂直自动扩缩容
✅ **安全性高**: 网络隔离 + 密钥管理
✅ **可观测性**: 全链路监控 + 日志收集
✅ **成本可控**: 资源优化 + 预留实例

这套架构可以支撑从小型应用到大规模分布式系统的各种场景需求。
