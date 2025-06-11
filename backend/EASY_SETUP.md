# 🚀 5分钟完成数据库设置

## 📋 超简单3步法

### 第1步：打开Supabase控制台
- 访问：https://app.supabase.com
- 登录你的账户
- 点击项目（应该能看到项目ID: ghbtjyetllhcdddhjygi）

### 第2步：进入SQL编辑器
- 点击左侧菜单的 **"SQL Editor"**（或 **"SQL编辑器"**）
- 点击 **"New query"**（或 **"新建查询"**）

### 第3步：复制粘贴运行
复制下面的SQL，粘贴到编辑器，点击 **"Run"**：

```sql
-- 🚀 笔录转换系统 - 一键创建所有表

-- 1. 用户配置表
CREATE TABLE user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 转换规则表
CREATE TABLE transformation_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rule_type VARCHAR(50) NOT NULL DEFAULT 'custom',
    rule_config JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 转换历史表
CREATE TABLE conversion_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    converted_text TEXT NOT NULL,
    rule_id UUID REFERENCES transformation_rules(id) ON DELETE SET NULL,
    quality_score DECIMAL(5,2),
    processing_time DECIMAL(8,3),
    file_name VARCHAR(255),
    file_size INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 批量任务表
CREATE TABLE batch_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_files INTEGER DEFAULT 0,
    processed_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    rule_id UUID REFERENCES transformation_rules(id) ON DELETE SET NULL,
    results JSONB DEFAULT '[]',
    error_log TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 插入默认规则
INSERT INTO transformation_rules (user_id, name, description, rule_type, rule_config, is_default) VALUES
(NULL, '标准问答转换', '将问答式对话转换为第一人称叙述', 'system', '{"style": "first_person", "format": "narrative"}', true),
(NULL, '正式文档转换', '转换为正式的文档格式', 'system', '{"style": "formal", "format": "document"}', false),
(NULL, '简洁摘要转换', '生成简洁的摘要版本', 'system', '{"style": "summary", "format": "brief"}', false);

-- 完成提示
SELECT '🎉 数据库设置完成！' as message;
```

## ✅ 验证成功

执行成功后你会看到：
- 显示 "🎉 数据库设置完成！"
- 左侧 Table Editor 中有4个新表

## 🎯 设置完成后

在终端运行验证：
```bash
python3 test_supabase_integration.py
```

应该看到所有测试通过！

---

**预计耗时：3-5分钟** ⏱️ 