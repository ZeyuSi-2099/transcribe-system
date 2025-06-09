# 部署指南

## ✅ 生产环境成功部署信息

### 🌐 当前生产环境配置
- **前端部署平台**: Vercel
- **后端部署平台**: Render
- **数据库**: SQLite (本地文件数据库)
- **域名**: transcribe.solutions
- **LLM服务**: Deepseek API

### 🔗 生产环境链接
- **主域名**: https://www.transcribe.solutions
- **前端仓库**: https://github.com/ZeyuSi-2099/transcribe-system (deploy-main 分支)
- **后端API**: https://transcribe-system.onrender.com
- **数据库**: SQLite文件 (存储在Render服务器本地)

### ⚙️ 关键配置文件
1. **Vercel配置** (`frontend/vercel.json`):
```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install"
}
```

2. **环境变量配置**:
   - Vercel: `NEXT_PUBLIC_API_URL` (Supabase相关变量已配置但未使用)
   - Render: `DEEPSEEK_API_KEY` (数据库使用SQLite文件，无需额外配置)

3. **部署分支**: `deploy-main`

### 🚀 部署成功关键步骤
1. **解决Root Directory配置**: 在Vercel中设置Root Directory为`frontend`
2. **删除冲突配置文件**: 移除项目根目录的vercel.json和next.config.ts
3. **添加框架识别配置**: 在frontend目录下创建vercel.json明确指定Next.js框架
4. **简化数据库配置**: 使用SQLite替代Supabase以避免部署时的依赖冲突
5. **环境变量配置**: 正确配置所有必要的环境变量

### 📊 数据库配置详情

#### 当前使用：SQLite
- **类型**: 本地文件数据库
- **位置**: Render服务器本地 (`./transcribe_system.db`)
- **优势**: 
  - 🚀 部署简单，无需外部数据库服务
  - 💰 无额外费用
  - ⚡ 快速启动和测试
- **限制**: 
  - 📊 数据存储在单个服务器实例
  - 🔄 服务重启时数据会重置 (Render的限制)
  - 📈 不适合大规模并发

#### 未来升级计划：迁移到Supabase
- **配置文件**: 已预留 `backend/app/core/supabase_client.py`
- **环境变量**: 前端已配置Supabase连接信息
- **迁移时机**: 当需要持久化数据存储和用户认证时

## 🚀 部署架构概览

### 生产环境推荐架构 (Supabase 集成)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx/CDN     │    │   前端 (Next.js) │    │   后端 (FastAPI) │
│   负载均衡/SSL   │────│   静态资源服务   │────│   API 服务       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                              │
                              ┌─────────────────────────────────────┐
                              │         Supabase Cloud              │
                              │  ┌─────────────┐ ┌─────────────────┐ │
                              │  │ PostgreSQL  │ │ Supabase Auth   │ │
                              │  │  数据库     │ │   认证服务      │ │
                              │  └─────────────┘ └─────────────────┘ │
                              │  ┌─────────────┐ ┌─────────────────┐ │
                              │  │ Storage     │ │ Realtime        │ │
                              │  │  文件存储   │ │   实时功能      │ │
                              │  └─────────────┘ └─────────────────┘ │
                              └─────────────────────────────────────┘
                                              │
                              ┌─────────────────┐    ┌─────────────────┐
                              │   LLM 服务      │    │   监控告警      │
                              │ Deepseek/Ollama │    │ Prometheus/等   │
                              └─────────────────┘    └─────────────────┘
```

### 本地开发架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │ Local Supabase  │
│   localhost:3000│────│   localhost:8000│────│ localhost:54321 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                              │
                              ┌─────────────────┐    ┌─────────────────┐
                              │   Ollama (可选)  │    │   Redis (可选)   │
                              │ localhost:11434 │    │ localhost:6379  │
                              └─────────────────┘    └─────────────────┘
```

## 🐳 Docker 部署

### Docker Compose 配置 (Supabase 云服务)
```yaml
# docker-compose.yml
version: '3.8'

services:
  # 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NODE_ENV=production
    depends_on:
      - backend

  # 后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - SUPABASE_JWT_SECRET=${SUPABASE_JWT_SECRET}
      - LLM_PROVIDER=${LLM_PROVIDER}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - OLLAMA_BASE_URL=http://ollama:11434
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - ollama
    volumes:
      - ./backend/uploads:/app/uploads

  # 缓存服务 (可选)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  # 本地 LLM 服务 (可选)
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    command: serve

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend

volumes:
  redis_data:
  ollama_data:
```

### Docker Compose 配置 (完全本地开发)
```yaml
# docker-compose.local.yml
version: '3.8'

services:
  # 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${LOCAL_SUPABASE_ANON_KEY}
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NODE_ENV=development
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
      - supabase

  # 后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=http://supabase:8000
      - SUPABASE_KEY=${LOCAL_SUPABASE_SERVICE_KEY}
      - SUPABASE_JWT_SECRET=${LOCAL_SUPABASE_JWT_SECRET}
      - LLM_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./backend:/app
      - ./backend/uploads:/app/uploads
    depends_on:
      - supabase
      - redis
      - ollama

  # 本地 Supabase
  supabase:
    image: supabase/supabase:latest
    ports:
      - "54321:8000"
      - "54322:5432"  # PostgreSQL
      - "54323:3000"  # Dashboard
    environment:
      - POSTGRES_PASSWORD=postgres
      - JWT_SECRET=${LOCAL_SUPABASE_JWT_SECRET}
      - ANON_KEY=${LOCAL_SUPABASE_ANON_KEY}
      - SERVICE_ROLE_KEY=${LOCAL_SUPABASE_SERVICE_KEY}
    volumes:
      - supabase_data:/var/lib/postgresql/data
      - ./supabase:/docker-entrypoint-initdb.d

  # Redis 缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Ollama LLM
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  supabase_data:
  redis_data:
  ollama_data:
```

### 环境变量配置 (.env)
```bash
# Supabase 云服务配置
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# 本地 Supabase 配置 (可选)
LOCAL_SUPABASE_ANON_KEY=your-local-anon-key
LOCAL_SUPABASE_SERVICE_KEY=your-local-service-key
LOCAL_SUPABASE_JWT_SECRET=your-local-jwt-secret

# LLM 配置
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-key

# 应用配置
APP_NAME=笔录转换系统
APP_VERSION=1.0.0
NODE_ENV=production
```

### 前端 Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS base

# 安装依赖
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# 构建应用
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# 配置 Supabase 构建时环境变量
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ARG NEXT_PUBLIC_API_URL

ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

# 运行时镜像
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### 后端 Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Supabase 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🌐 云部署方案

### Vercel + Supabase 部署 (推荐)

#### 1. 前端部署到 Vercel
```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录 Vercel
vercel login

# 部署前端
cd frontend
vercel

# 配置环境变量 (在 Vercel Dashboard)
# NEXT_PUBLIC_SUPABASE_URL
# NEXT_PUBLIC_SUPABASE_ANON_KEY
# NEXT_PUBLIC_API_URL
```

#### 2. 后端部署到云服务器
```bash
# 部署到 AWS/GCP/Azure/DigitalOcean
# 1. 创建云服务器实例
# 2. 安装 Docker 和 Docker Compose
# 3. 克隆代码库
# 4. 配置环境变量
# 5. 运行部署脚本

./deploy.sh production
```

#### 3. Supabase 云服务配置
```bash
# 1. 在 Supabase Dashboard 创建项目
# 2. 配置数据库 Schema
# 3. 设置认证策略
# 4. 配置存储桶
# 5. 启用实时功能
# 6. 获取 API 密钥和连接信息
```

### Railway + Supabase 部署

#### railway.json 配置
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepThreshold": 0,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### 部署步骤
```bash
# 1. 安装 Railway CLI
npm install -g @railway/cli

# 2. 登录 Railway
railway login

# 3. 创建项目
railway init

# 4. 配置环境变量
railway variables set SUPABASE_URL=your-url
railway variables set SUPABASE_KEY=your-key

# 5. 部署
railway up
```

### Docker Swarm 集群部署

#### docker-stack.yml
```yaml
version: '3.8'

services:
  frontend:
    image: your-registry/transcribe-frontend:latest
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure

  backend:
    image: your-registry/transcribe-backend:latest
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    configs:
      - source: nginx_config
        target: /etc/nginx/nginx.conf
    deploy:
      replicas: 2

configs:
  nginx_config:
    external: true
```

## 🔧 部署脚本

### 自动化部署脚本
```bash
#!/bin/bash
# deploy.sh

set -e

ENVIRONMENT=${1:-production}
VERSION=${2:-latest}

echo "🚀 开始部署笔录转换系统 (环境: $ENVIRONMENT, 版本: $VERSION)"

# 检查必要的文件和配置
check_prerequisites() {
    echo "📋 检查部署前置条件..."
    
    if [ ! -f "docker-compose.yml" ]; then
        echo "❌ docker-compose.yml 文件不存在"
        exit 1
    fi
    
    if [ ! -f ".env" ]; then
        echo "❌ .env 文件不存在，请从 .env.example 复制并配置"
        exit 1
    fi
    
    # 检查 Supabase 配置
    if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
        echo "❌ Supabase 配置不完整，请检查环境变量"
        exit 1
    fi
    
    echo "✅ 前置条件检查通过"
}

# 构建镜像
build_images() {
    echo "🔨 构建 Docker 镜像..."
    
    # 构建前端镜像
    echo "构建前端镜像..."
    docker build -t transcribe-frontend:$VERSION ./frontend
    
    # 构建后端镜像
    echo "构建后端镜像..."
    docker build -t transcribe-backend:$VERSION ./backend
    
    echo "✅ 镜像构建完成"
}

# 部署服务
deploy_services() {
    echo "🚀 部署服务..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        # 生产环境部署
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    else
        # 开发环境部署
        docker-compose up -d
    fi
    
    echo "✅ 服务部署完成"
}

# 检查服务健康状态
check_health() {
    echo "🏥 检查服务健康状态..."
    
    # 等待服务启动
    sleep 30
    
    # 检查前端服务
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ 前端服务正常"
    else
        echo "❌ 前端服务异常"
        exit 1
    fi
    
    # 检查后端服务
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 后端服务正常"
    else
        echo "❌ 后端服务异常"
        exit 1
    fi
    
    # 检查 Supabase 连接
    if curl -f "$SUPABASE_URL/rest/v1/" \
         -H "apikey: $SUPABASE_ANON_KEY" > /dev/null 2>&1; then
        echo "✅ Supabase 连接正常"
    else
        echo "❌ Supabase 连接异常"
        exit 1
    fi
}

# 数据库迁移 (如果需要)
migrate_database() {
    echo "📊 执行数据库迁移..."
    
    # 使用 Supabase CLI 执行迁移
    if command -v supabase >/dev/null 2>&1; then
        supabase db push
        echo "✅ 数据库迁移完成"
    else
        echo "⚠️ Supabase CLI 未安装，跳过数据库迁移"
    fi
}

# 清理旧版本
cleanup() {
    echo "🧹 清理旧版本..."
    
    # 删除未使用的镜像
    docker image prune -f
    
    # 删除未使用的容器
    docker container prune -f
    
    echo "✅ 清理完成"
}

# 主执行流程
main() {
    check_prerequisites
    build_images
    migrate_database
    deploy_services
    check_health
    cleanup
    
    echo "🎉 部署完成！"
    echo "前端地址: http://localhost:3000"
    echo "后端地址: http://localhost:8000"
    echo "API 文档: http://localhost:8000/docs"
}

# 执行主流程
main "$@"
```

### Supabase 数据库迁移脚本
```bash
#!/bin/bash
# migrate-supabase.sh

set -e

echo "📊 执行 Supabase 数据库迁移..."

# 检查 Supabase CLI
if ! command -v supabase >/dev/null 2>&1; then
    echo "❌ Supabase CLI 未安装"
    echo "请运行: npm install -g @supabase/cli"
    exit 1
fi

# 登录 Supabase (如果需要)
if [ ! -f ~/.config/supabase/access-token ]; then
    echo "🔑 请先登录 Supabase:"
    supabase login
fi

# 检查项目链接
if [ ! -f ".supabase/config.toml" ]; then
    echo "❌ 项目未链接到 Supabase"
    echo "请运行: supabase link --project-ref your-project-id"
    exit 1
fi

# 生成新迁移 (如果有本地更改)
echo "🔄 检查数据库变更..."
supabase db diff --use-migra > temp_migration.sql

if [ -s temp_migration.sql ]; then
    echo "📝 发现数据库变更，生成迁移文件..."
    MIGRATION_NAME="migration_$(date +%Y%m%d_%H%M%S)"
    mv temp_migration.sql "supabase/migrations/${MIGRATION_NAME}.sql"
    echo "✅ 迁移文件已生成: ${MIGRATION_NAME}.sql"
else
    echo "✅ 数据库无变更"
    rm temp_migration.sql
fi

# 应用迁移
echo "🚀 应用数据库迁移..."
supabase db push

# 生成类型定义
echo "📝 生成 TypeScript 类型定义..."
supabase gen types typescript --linked > types/supabase.ts

echo "✅ Supabase 数据库迁移完成"
```

## 📊 监控和日志

### 应用监控配置
```yaml
# monitoring/docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki.yml:/etc/loki/local-config.yaml
      - loki_data:/tmp/loki

volumes:
  prometheus_data:
  grafana_data:
  loki_data:
```

### 日志收集配置
```yaml
# 在主 docker-compose.yml 中添加日志配置
services:
  frontend:
    # ... 其他配置
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  backend:
    # ... 其他配置
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

更多信息请参考：
- [技术架构](README_architecture.md)
- [用户指南](README_user_guide.md)
- [开发指南](README_development.md) 