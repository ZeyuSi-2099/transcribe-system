-- ===============================================
-- 手动修复数据库约束问题
-- 在 Supabase 控制台的 SQL 编辑器中执行此脚本
-- ===============================================

-- 步骤1: 在 auth.users 表中创建系统用户
-- 注意：需要使用 Supabase 控制台的 SQL 编辑器执行，因为有Service Role权限

DO $$
BEGIN
    -- 检查并插入系统用户
    IF NOT EXISTS (SELECT 1 FROM auth.users WHERE id = '00000000-0000-0000-0000-000000000000') THEN
        INSERT INTO auth.users (
            id,
            instance_id,
            aud,
            role,
            email,
            encrypted_password,
            email_confirmed_at,
            recovery_sent_at,
            last_sign_in_at,
            raw_app_meta_data,
            raw_user_meta_data,
            created_at,
            updated_at,
            confirmation_token,
            email_change,
            email_change_token_new,
            recovery_token
        ) VALUES (
            '00000000-0000-0000-0000-000000000000',
            '00000000-0000-0000-0000-000000000000',
            'authenticated',
            'authenticated',
            'system@transcription-system.local',
            '',
            NOW(),
            NULL,
            NULL,
            '{"provider": "system", "providers": ["system"], "role": "system"}'::jsonb,
            '{"full_name": "系统用户", "role": "system"}'::jsonb,
            NOW(),
            NOW(),
            '',
            '',
            '',
            ''
        );
        RAISE NOTICE '系统用户已创建';
    ELSE
        RAISE NOTICE '系统用户已存在';
    END IF;

    -- 检查并插入匿名用户
    IF NOT EXISTS (SELECT 1 FROM auth.users WHERE id = '00000000-0000-0000-0000-000000000001') THEN
        INSERT INTO auth.users (
            id,
            instance_id,
            aud,
            role,
            email,
            encrypted_password,
            email_confirmed_at,
            recovery_sent_at,
            last_sign_in_at,
            raw_app_meta_data,
            raw_user_meta_data,
            created_at,
            updated_at,
            confirmation_token,
            email_change,
            email_change_token_new,
            recovery_token
        ) VALUES (
            '00000000-0000-0000-0000-000000000001',
            '00000000-0000-0000-0000-000000000000',
            'authenticated',
            'authenticated',
            'anonymous@transcription-system.local',
            '',
            NOW(),
            NULL,
            NULL,
            '{"provider": "anonymous", "providers": ["anonymous"], "role": "anonymous"}'::jsonb,
            '{"full_name": "匿名用户", "role": "anonymous"}'::jsonb,
            NOW(),
            NOW(),
            '',
            '',
            '',
            ''
        );
        RAISE NOTICE '匿名用户已创建';
    ELSE
        RAISE NOTICE '匿名用户已存在';
    END IF;
END $$;

-- 步骤2: 创建对应的用户配置
INSERT INTO user_profiles (
    id,
    username,
    email,
    full_name,
    preferences,
    created_at,
    updated_at
) VALUES 
(
    '00000000-0000-0000-0000-000000000000',
    'system',
    'system@transcription-system.local',
    '系统用户',
    '{"role": "system", "created_by": "manual_fix"}'::jsonb,
    NOW(),
    NOW()
),
(
    '00000000-0000-0000-0000-000000000001',
    'anonymous',
    'anonymous@transcription-system.local',
    '匿名用户',
    '{"role": "anonymous", "created_by": "manual_fix"}'::jsonb,
    NOW(),
    NOW()
)
ON CONFLICT (id) DO UPDATE SET
    updated_at = NOW(),
    preferences = EXCLUDED.preferences;

-- 步骤3: 验证创建结果
SELECT 
    'auth.users' as table_name,
    id, 
    email, 
    role,
    raw_user_meta_data->>'role' as user_role,
    created_at
FROM auth.users 
WHERE id IN (
    '00000000-0000-0000-0000-000000000000',
    '00000000-0000-0000-0000-000000000001'
)

UNION ALL

SELECT 
    'user_profiles' as table_name,
    id,
    email,
    NULL as role,
    preferences->>'role' as user_role,
    created_at
FROM user_profiles
WHERE id IN (
    '00000000-0000-0000-0000-000000000000',
    '00000000-0000-0000-0000-000000000001'
);

-- 步骤4: 测试转换历史插入
DO $$
DECLARE
    test_rule_id UUID;
    test_conversion_id UUID := gen_random_uuid();
BEGIN
    -- 获取一个系统规则ID
    SELECT id INTO test_rule_id 
    FROM transformation_rules 
    WHERE rule_type = 'system' 
    LIMIT 1;

    -- 测试插入转换历史
    INSERT INTO conversion_history (
        id,
        user_id,
        original_text,
        converted_text,
        rule_id,
        file_name,
        metadata,
        created_at
    ) VALUES (
        test_conversion_id,
        '00000000-0000-0000-0000-000000000000',
        '测试原始文本 - 约束修复验证',
        '测试转换文本 - 约束修复验证',
        test_rule_id,
        'constraint_fix_test.txt',
        '{"test": true, "fix_verification": true}'::jsonb,
        NOW()
    );

    RAISE NOTICE '转换历史插入测试成功，记录ID: %', test_conversion_id;

    -- 立即删除测试数据
    DELETE FROM conversion_history WHERE id = test_conversion_id;
    RAISE NOTICE '测试数据已清理';

EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '转换历史插入测试失败: %', SQLERRM;
END $$;

-- 步骤5: 最终检查
SELECT 
    '数据库约束修复完成' as status,
    COUNT(*) as system_users_count
FROM user_profiles 
WHERE id IN (
    '00000000-0000-0000-0000-000000000000',
    '00000000-0000-0000-0000-000000000001'
); 