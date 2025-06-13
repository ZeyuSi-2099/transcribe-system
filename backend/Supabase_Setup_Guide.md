# 📚 Supabase数据库设置指南

## 📋 目录
- [方案概述](#方案概述)
- [方案一：自动化设置（推荐）](#方案一自动化设置推荐)
- [方案二：手动设置（适合小白）](#方案二手动设置适合小白)
- [验证设置](#验证设置)
- [常见问题](#常见问题)

## 🎯 方案概述

我们提供了**三种方案**来创建Supabase数据库表结构：

| 方案 | 适用人群 | 推荐度 | 说明 |
|------|----------|--------|------|
| **自动化设置** | 有技术基础 | ⭐⭐⭐⭐⭐ | 一键运行脚本，全自动设置 |
| **手动设置** | 完全小白 | ⭐⭐⭐⭐ | 在Supabase控制台复制粘贴SQL |
| **混合方案** | 部分失败时 | ⭐⭐⭐ | 自动+手动结合 |

---

## 🚀 方案一：自动化设置（推荐）

### 🔧 前置准备

1. **确保环境变量已设置**：
   ```bash
   # 检查.env文件
   cat .env
   ```
   
   应该包含：
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```

2. **确保依赖已安装**：
   ```bash
   pip install psycopg2-binary python-dotenv
   ```

### ⚡ 一键运行

```bash
# 运行自动化设置脚本
python3 setup_supabase_simple.py
```

### 📊 预期输出

```
🚀 开始自动化设置Supabase数据库...
📝 这将创建表结构、索引、安全策略和默认数据

🔗 连接到数据库: xxx.pooler.supabase.com:6543
✅ 数据库连接成功

🔧 创建数据表...
✅ 创建数据表 - 成功

🔧 创建索引...
✅ 创建索引 - 成功

🔧 启用行级安全策略...
✅ 启用行级安全策略 - 成功

🔧 创建触发器...
✅ 创建触发器 - 成功

🔧 插入默认规则...
✅ 插入默认规则 - 成功

🔍 验证数据库设置...
✅ 表 user_profiles - 验证成功 (记录数: 0)
✅ 表 transformation_rules - 验证成功 (记录数: 3)
✅ 表 conversion_history - 验证成功 (记录数: 0)
✅ 表 batch_jobs - 验证成功 (记录数: 0)

📊 设置结果: 5/5 步骤成功
🎉 数据库设置完成！

🎯 下一步:
1. 运行测试: python3 test_supabase_integration.py
2. 启动后端: uvicorn app.main:app --reload
3. 启动前端: cd ../frontend && npm run dev
```

---

## 👥 方案二：手动设置（适合小白）

### 📝 详细步骤

#### 1️⃣ 打开Supabase控制台

1. 访问 [Supabase控制台](https://app.supabase.com)
2. 登录您的账户
3. 选择您的项目

#### 2️⃣ 进入SQL编辑器

1. 在左侧菜单中点击 **"SQL Editor"**（SQL编辑器）
2. 点击 **"New query"**（新建查询）

#### 3️⃣ 复制SQL脚本

打开文件 `backend/supabase_manual_setup.sql`，复制**所有内容**到SQL编辑器中。

#### 4️⃣ 执行SQL脚本

1. 确保所有SQL内容都在编辑器中
2. 点击右下角的 **"Run"**（运行）按钮
3. 等待执行完成

#### 5️⃣ 查看执行结果

执行成功后，您应该看到类似的输出：
```
NOTICE: 🎉 数据库设置完成！
NOTICE: ✅ 已创建 4 个数据表
NOTICE: ✅ 已创建索引和触发器
NOTICE: ✅ 已启用行级安全策略
NOTICE: ✅ 已设置存储桶
NOTICE: ✅ 已插入默认规则
```

#### 6️⃣ 验证表创建

1. 在左侧菜单点击 **"Table Editor"**（表编辑器）
2. 您应该看到以下4个表：
   - `user_profiles` - 用户配置表
   - `transformation_rules` - 转换规则表
   - `conversion_history` - 转换历史表
   - `batch_jobs` - 批量任务表

---

## ✅ 验证设置

### 🔍 运行测试脚本

```bash
python3 test_supabase_integration.py
```

### 📊 预期结果

```
🚀 开始测试Supabase集成...

🔗 测试数据库连接...
✅ Supabase连接成功

🔍 验证表结构...
✅ 表 user_profiles 存在
✅ 表 transformation_rules 存在 (3 条记录)
✅ 表 conversion_history 存在
✅ 表 batch_jobs 存在

📊 测试摘要:
✅ 所有测试通过
🎉 Supabase集成配置正确！

🎯 下一步:
1. 启动后端服务: uvicorn app.main:app --reload
2. 启动前端服务: cd ../frontend && npm run dev
3. 访问应用: http://localhost:3000
```

---

## 🛠️ 常见问题

### ❌ 问题1：连接失败

**症状**：
```
❌ 连接失败，尝试备用方法...
❌ 备用连接也失败: connection failed
```

**解决方案**：
1. 检查环境变量是否正确设置
2. 确认Supabase项目状态正常
3. 尝试方案二（手动设置）

### ❌ 问题2：权限不足

**症状**：
```
❌ 创建数据表 - 失败: permission denied
```

**解决方案**：
1. 确保使用的是 `SUPABASE_SERVICE_ROLE_KEY`（不是 `SUPABASE_ANON_KEY`）
2. 检查Service Role Key是否有效
3. 在Supabase控制台重新生成Key

### ❌ 问题3：表已存在

**症状**：
```
❌ 创建数据表 - 失败: relation already exists
```

**解决方案**：
这通常不是问题，脚本使用 `CREATE TABLE IF NOT EXISTS`，应该会跳过已存在的表。如果仍有问题：
1. 在Supabase控制台删除冲突的表
2. 重新运行脚本

### ❌ 问题4：部分步骤失败

**症状**：
```
📊 设置结果: 3/5 步骤成功
⚠️ 部分设置失败，请检查错误信息
```

**解决方案**：
1. 查看具体错误信息
2. 可以手动在Supabase控制台执行失败的SQL部分
3. 或者使用方案二完全手动设置

---

## 🎯 下一步操作

设置完成后，请按以下顺序进行：

1. **验证设置**：
   ```bash
   python3 test_supabase_integration.py
   ```

2. **启动后端服务**：
   ```bash
   uvicorn app.main:app --reload
   ```

3. **启动前端服务**：
   ```bash
   cd ../frontend
   npm run dev
   ```

4. **访问应用**：
   打开浏览器访问 `http://localhost:3000`

---

## 📞 获取帮助

如果遇到问题，可以：

1. **查看错误日志**：仔细阅读终端输出的错误信息
2. **检查环境变量**：确保所有必要的变量都已正确设置
3. **尝试替代方案**：如果自动化失败，可以使用手动方案
4. **重新开始**：删除表后重新运行设置脚本

---

## 📋 快速检查清单

- [ ] ✅ Supabase项目已创建
- [ ] ✅ 环境变量已正确设置
- [ ] ✅ 依赖包已安装
- [ ] ✅ 数据库表已创建
- [ ] ✅ 测试脚本运行成功
- [ ] ✅ 后端服务可以启动
- [ ] ✅ 前端服务可以启动 