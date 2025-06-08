# 技术架构详细说明

## 🏗️ 详细技术架构

### 前端技术栈
- **核心框架**: React 18.2.0 + Next.js 15.0.3 (App Router)
- **开发语言**: TypeScript 5.0+
- **样式方案**: Tailwind CSS 3.4+
- **UI组件库**: Radix UI + shadcn/ui
- **状态管理**: React Context API + URL 搜索参数
- **认证**: Supabase Auth (@supabase/auth-helpers-nextjs)
- **数据获取**: Supabase Client (@supabase/supabase-js)
- **实时功能**: Supabase Realtime
- **图标库**: Lucide React
- **包管理**: npm
- **代码质量**: ESLint + Prettier

### 后端技术栈
- **编程语言**: Python 3.11.5
- **Web 框架**: FastAPI 0.104.1
- **数据库**: Supabase (PostgreSQL 15+)
- **认证**: Supabase Auth
- **ORM**: supabase-py + 原生 PostgreSQL 查询
- **文件存储**: Supabase Storage
- **实时通信**: Supabase Realtime WebSockets
- **LLM 集成**:
  - **云端方案**: Deepseek API
  - **本地方案**: Ollama + Qwen2.5-7B-Instruct (推荐配置)
  - **Hugging Face**: `transformers` 库支持
- **文档处理**: python-docx 1.1.0+ (Word文档读写)
- **依赖管理**: Poetry 1.6+
- **数据校验**: Pydantic 2.0+
- **异步处理**: asyncio + uvicorn 0.24+

### Supabase 架构集成

#### 核心服务
- **Supabase Database**: PostgreSQL 15+ 托管数据库
  - 行级安全策略 (Row Level Security, RLS)
  - 自动生成的 REST API
  - 实时数据同步
  - 自动备份和恢复

- **Supabase Auth**: 统一认证服务
  - JWT 令牌管理
  - 多种认证方式 (邮箱/密码、OAuth)
  - 用户会话管理
  - 密码重置和邮箱验证

- **Supabase Storage**: 文件存储服务
  - 上传文件的安全存储
  - CDN 加速分发
  - 自动图片优化和转换
  - 细粒度访问控制

- **Supabase Realtime**: 实时通信
  - WebSocket 连接管理
  - 数据库变更实时推送
  - 自定义事件广播
  - 用户在线状态同步

#### 数据库设计
```sql
-- 用户表 (由 Supabase Auth 管理)
-- auth.users 表自动创建，包含基础认证信息

-- 用户配置表
CREATE TABLE user_profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  username TEXT UNIQUE,
  display_name TEXT,
  avatar_url TEXT,
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 转换规则表
CREATE TABLE transformation_rules (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  name TEXT NOT NULL,
  description TEXT,
  rules JSONB NOT NULL,
  is_active BOOLEAN DEFAULT true,
  is_system BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 转换历史表
CREATE TABLE conversion_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  original_filename TEXT,
  original_content TEXT NOT NULL,
  converted_content TEXT NOT NULL,
  rule_id UUID REFERENCES transformation_rules(id),
  quality_score NUMERIC(5,2),
  quality_metrics JSONB,
  processing_time NUMERIC(8,3),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 批量处理任务表
CREATE TABLE batch_jobs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  name TEXT NOT NULL,
  status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
  total_files INTEGER NOT NULL,
  completed_files INTEGER DEFAULT 0,
  failed_files INTEGER DEFAULT 0,
  progress NUMERIC(5,2) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 行级安全策略
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE transformation_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversion_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_jobs ENABLE ROW LEVEL SECURITY;

-- RLS 策略示例
CREATE POLICY "Users can view own profile" ON user_profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
  FOR UPDATE USING (auth.uid() = id);
```

### 数据存储
- **主数据库**: Supabase PostgreSQL 15+
  - 高可用性托管数据库
  - 自动备份和恢复
  - 性能监控和优化
  - 连接池管理

- **文件存储**: Supabase Storage
  - 原始上传文件存储
  - 转换结果文件存储
  - CDN 加速访问
  - 安全访问控制

- **缓存层**: Redis 7+ (可选)
  - LLM 结果缓存
  - 会话数据缓存
  - 计算结果缓存

### 混合处理架构设计

#### 确定性规则引擎
- **发言人标记识别**: 正则表达式 + 启发式算法
- **格式化处理**: 标准化文本预处理管道
- **语法修正**: 基于规则的语法检查和修正
- **适用场景**: 简单重复、确定性强的转换任务

#### LLM 处理引擎
- **语言优化**: 基于上下文的语言流畅性改进
- **语气调整**: 保持口语化感觉的同时提升可读性
- **上下文理解**: 跨句子和段落的语义连贯性处理
- **视角转换**: 从对话式转换为第一人称叙述
- **适用场景**: 复杂语义理解和生成任务

#### 混合处理流程
```
输入文本 → 预处理 → 确定性规则处理 → LLM优化 → 后处理 → 输出文本
         ↓
    发言人识别
    格式标准化     → 语言优化 → 质量检验
    基础修正         语气调整    指标计算
                    视角转换
```

### 开发工具与 MCP 集成

#### MCP (Model Context Protocol) 集成说明
- **21st-dev/magic MCP**: UI 组件快速生成和优化
  - 使用场景: 快速构建React组件和界面
  - 集成方式: VS Code + Cursor 扩展
  
- **Sequential-Thinking MCP**: 复杂问题分析和方案设计
  - 使用场景: 架构设计、问题诊断、方案评估
  - 集成方式: 开发过程中的决策支持工具
  
- **Playwright MCP**: 自动化测试执行和反馈
  - 使用场景: E2E测试、回归测试、用户流程验证
  - 集成方式: CI/CD 管道中的自动化测试
  
- **Context-7 MCP**: 文档查询和代码生成辅助
  - 使用场景: 技术文档查询、API使用指导
  - 集成方式: 开发环境中的实时文档助手

### 安全与质量保证

#### 认证与授权 (Supabase Auth)
- **认证方式**: 
  - 邮箱/密码认证
  - OAuth 提供商 (Google, GitHub 等)
  - 魔法链接登录
  - 手机号验证 (可选)
- **会话管理**: JWT 令牌 + 刷新令牌机制
- **密码安全**: Supabase 内置的 bcrypt 哈希处理
- **权限控制**: 基于行级安全策略 (RLS) 的数据访问控制

#### 数据安全 (Supabase 内置)
- **传输安全**: 强制 HTTPS/WSS 连接
- **存储安全**: 数据库级别的加密存储
- **访问控制**: 细粒度的 RLS 策略
- **备份恢复**: 自动备份和点击恢复功能
- **审计日志**: 完整的操作日志记录

#### 输入验证与安全
- **文件格式验证**: 严格的MIME类型检查和文件头验证
- **内容大小限制**: 防止DoS攻击的文件大小和处理时间限制
- **Prompt 注入防护**: LLM输入的清理、转义和模板化处理
- **XSS防护**: 前端输入输出的严格转义和CSP策略
- **SQL注入防护**: Supabase 自动防护 + 参数化查询

#### API 安全
- **Rate Limiting**: Supabase 内置的请求频率限制
- **CORS 配置**: 严格的跨域资源共享配置
- **API 密钥管理**: 环境变量管理，不同环境不同密钥
- **请求验证**: 基于 JWT 的请求认证和授权

#### 实时功能安全
- **连接认证**: WebSocket 连接的 JWT 验证
- **频道授权**: 基于用户权限的频道访问控制
- **消息过滤**: 基于 RLS 的实时消息过滤
- **连接限制**: 单用户连接数量限制

#### 用户认证与授权
- **认证方式**: JWT (JSON Web Token) 基于的无状态认证
- **密码安全**: bcrypt哈希 + 盐值处理
- **会话管理**: 访问令牌 + 刷新令牌机制
- **权限控制**: 基于角色的访问控制 (RBAC)
  - **管理员**: 完整系统管理权限
  - **普通用户**: 个人数据和功能访问权限

#### 用户数据隐私
- **数据加密**: 敏感数据字段级加密存储
- **数据最小化**: 只收集和存储必要的用户数据
- **访问日志**: 详细的数据访问和操作日志记录
- **数据删除**: 用户数据删除和匿名化机制
- **隐私合规**: 遵循GDPR和相关隐私法规要求

### 性能优化策略

#### 前端性能
- **代码分割**: Next.js自动代码分割和懒加载
- **图片优化**: Next.js Image组件优化和WebP支持
- **缓存策略**: 浏览器缓存 + Supabase CDN缓存优化
- **Bundle优化**: Tree shaking和无用代码移除
- **实时优化**: 智能的 WebSocket 连接管理和重连机制

#### 后端性能
- **异步处理**: FastAPI异步支持 + supabase-py 异步操作
- **连接池**: Supabase 自动连接池管理
- **缓存层**: Redis缓存热点数据和计算结果 (可选)
- **负载均衡**: Supabase 内置负载均衡和高可用

#### 数据库性能
- **索引优化**: 基于查询模式的智能索引设计
- **查询优化**: 使用 Supabase 的查询计划分析
- **连接池**: Supabase 自动管理的连接池
- **读写分离**: Supabase 内置的读写分离机制

#### LLM处理优化
- **请求批处理**: 多个请求的批量处理优化
- **结果缓存**: 相似输入的结果缓存机制 (Redis)
- **模型选择**: 根据任务复杂度选择合适的模型
- **流式响应**: 支持流式输出提升用户体验

#### 实时功能优化
- **连接复用**: 智能的 WebSocket 连接池管理
- **消息批处理**: 批量发送实时更新减少网络开销
- **频道管理**: 动态频道订阅和取消订阅
- **心跳机制**: 智能的连接保活和故障检测

---

更多信息请参考：
- [用户指南](README_user_guide.md)
- [开发指南](README_development.md)
- [部署指南](README_deployment.md) 