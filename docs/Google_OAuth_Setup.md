# Google OAuth 配置指南

## 概述

本文档将指导您完成在Supabase项目中配置Google OAuth的完整过程，使用户能够通过Google账户进行登录和注册。

## 前提条件

1. 已创建的Supabase项目
2. Google Cloud Platform账户
3. 前端应用程序已部署或有固定的回调URL

## 步骤 1: Google Cloud Platform 配置

### 1.1 创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 点击项目选择器，然后点击"新项目"
3. 输入项目名称（例如："笔录转换系统"）
4. 点击"创建"

### 1.2 启用 Google+ API

1. 在Google Cloud Console中，转到"API和服务" > "库"
2. 搜索"Google+ API"
3. 点击"Google+ API"
4. 点击"启用"

### 1.3 创建 OAuth 2.0 凭据

1. 转到"API和服务" > "凭据"
2. 点击"创建凭据" > "OAuth 客户端ID"
3. 选择应用类型："Web应用程序"
4. 输入名称（例如："笔录转换系统Web客户端"）
5. 在"已授权的JavaScript来源"中添加：
   - `http://localhost:3000` (开发环境)
   - `https://transcribe.solutions` (生产环境)
6. 在"已授权的重定向URI"中添加：
   - `https://ghbtjyetllhcdddhjygi.supabase.co/auth/v1/callback`
   - 注意：将URL中的项目ID替换为您的实际Supabase项目ID

### 1.4 获取客户端凭据

1. 创建完成后，复制"客户端ID"和"客户端密钥"
2. 安全保存这些凭据

## 步骤 2: Supabase 配置

### 2.1 配置Google OAuth提供商

1. 登录您的 [Supabase Dashboard](https://app.supabase.com/)
2. 选择您的项目
3. 转到"Authentication" > "Providers"
4. 找到"Google"提供商
5. 启用"Enable Google provider"
6. 输入从Google Cloud Console获取的：
   - **Client ID**：您的Google客户端ID
   - **Client Secret**：您的Google客户端密钥
7. 点击"Save"

### 2.2 配置重定向URL（可选）

在"Authentication" > "URL Configuration"中：
- **Site URL**: `http://localhost:3000` (开发) 或 `https://transcribe.solutions` (生产)
- **Redirect URLs**: 添加您的应用程序允许的重定向URL

## 步骤 3: 前端代码配置

### 3.1 环境变量

确保您的 `frontend/.env.local` 文件包含正确的Supabase配置：

```env
NEXT_PUBLIC_SUPABASE_URL=https://ghbtjyetllhcdddhjygi.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3.2 Supabase客户端配置

确保您的 `src/lib/supabase.ts` 包含OAuth配置：

```typescript
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    flowType: 'pkce'
  }
})
```

## 步骤 4: 测试配置

### 4.1 开发环境测试

1. 启动前端开发服务器：
   ```bash
   cd frontend && npm run dev
   ```

2. 访问 `http://localhost:3000/auth/login`

3. 点击"使用Google登录"按钮

4. 验证是否正确重定向到Google登录页面

### 4.2 生产环境配置

对于生产环境，需要：

1. 更新Google Cloud Console中的已授权来源和重定向URI
2. 更新Supabase中的Site URL
3. 确保HTTPS配置正确

## 故障排除

### 常见错误

1. **"Unsupported provider: provider is not enabled"**
   - 检查Supabase Dashboard中是否启用了Google提供商
   - 验证客户端ID和密钥是否正确输入

2. **"redirect_uri_mismatch"**
   - 检查Google Cloud Console中的重定向URI配置
   - 确保Supabase回调URL正确添加

3. **"origin_mismatch"**
   - 检查Google Cloud Console中的已授权JavaScript来源
   - 确保包含正确的域名和端口

### 调试步骤

1. 检查浏览器开发者工具的控制台错误
2. 验证网络请求是否正确发送到Supabase
3. 检查Supabase项目的身份验证日志

## 安全注意事项

1. **客户端密钥安全**：
   - 永远不要在前端代码中暴露Google客户端密钥
   - 客户端密钥应该只在Supabase Dashboard中配置

2. **域名验证**：
   - 只在Google Cloud Console中添加受信任的域名
   - 定期审查已授权的重定向URI

3. **用户数据处理**：
   - 了解Google OAuth返回的用户数据
   - 根据隐私政策处理用户信息

## 总结

完成以上配置后，您的应用程序将支持：

- Google账户登录和注册
- 自动的用户会话管理
- 与现有邮箱/密码认证的无缝集成
- 安全的OAuth流程处理

如果遇到问题，请检查Supabase项目的身份验证日志和浏览器开发者工具中的错误信息。 