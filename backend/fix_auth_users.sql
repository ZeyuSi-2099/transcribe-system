-- ===============================================
-- 修复数据库约束问题 - 创建系统用户
-- 解决外键约束导致转换历史无法保存的问题
-- 请在Supabase控制台的SQL编辑器中执行此脚本
-- ===============================================

-- 1. 在auth.users表中创建系统用户
INSERT INTO auth.users (
    id,
    instance_id,
    aud,
    role,
    email,
    encrypted_password,
    email_confirmed_at,
    invited_at,
    confirmation_token,
    confirmation_sent_at,
    recovery_token,
    recovery_sent_at,
    email_change_token_new,
    email_change,
    email_change_sent_at,
    last_sign_in_at,
    raw_app_meta_data,
    raw_user_meta_data,
    is_super_admin,
    created_at,
    updated_at,
    phone,
    phone_confirmed_at,
    phone_change,
    phone_change_token,
    phone_change_sent_at,
    email_change_token_current,
    email_change_confirm_status,
    banned_until,
    reauthentication_token,
    reauthentication_sent_at
) VALUES (
    '00000000-0000-0000-0000-000000000000',  -- 系统用户ID
    '00000000-0000-0000-0000-000000000000',
    'authenticated',
    'authenticated',
    'system@transcription-system.local',
    '',  -- 空密码，系统用户无法登录
    NOW(),
    NULL,
    '',
    NULL,
    '',
    NULL,
    '',
    '',
    NULL,
    NULL,
    '{"provider": "system", "providers": ["system"], "role": "system"}',
    '{"full_name": "系统用户", "avatar_url": "", "role": "system"}',
    false,
    NOW(),
    NOW(),
    NULL,
    NULL,
    '',
    '',
    NULL,
    '',
    0,
    NULL,
    '',
    NULL
) ON CONFLICT (id) DO NOTHING;

-- 2. 创建匿名用户
INSERT INTO auth.users (
    id,
    instance_id,
    aud,
    role,
    email,
    encrypted_password,
    email_confirmed_at,
    invited_at,
    confirmation_token,
    confirmation_sent_at,
    recovery_token,
    recovery_sent_at,
    email_change_token_new,
    email_change,
    email_change_sent_at,
    last_sign_in_at,
    raw_app_meta_data,
    raw_user_meta_data,
    is_super_admin,
    created_at,
    updated_at,
    phone,
    phone_confirmed_at,
    phone_change,
    phone_change_token,
    phone_change_sent_at,
    email_change_token_current,
    email_change_confirm_status,
    banned_until,
    reauthentication_token,
    reauthentication_sent_at
) VALUES (
    '00000000-0000-0000-0000-000000000001',  -- 匿名用户ID
    '00000000-0000-0000-0000-000000000000',
    'authenticated',
    'authenticated',
    'anonymous@transcription-system.local',
    '',  -- 空密码，匿名用户无法登录
    NOW(),
    NULL,
    '',
    NULL,
    '',
    NULL,
    '',
    '',
    NULL,
    NULL,
    '{"provider": "anonymous", "providers": ["anonymous"], "role": "anonymous"}',
    '{"full_name": "匿名用户", "avatar_url": "", "role": "anonymous"}',
    false,
    NOW(),
    NOW(),
    NULL,
    NULL,
    '',
    '',
    NULL,
    '',
    0,
    NULL,
    '',
    NULL
) ON CONFLICT (id) DO NOTHING;

-- 3. 验证插入结果
SELECT 
    id, 
    email, 
    role,
    raw_user_meta_data->>'role' as user_role,
    created_at
FROM auth.users 
WHERE id IN (
    '00000000-0000-0000-0000-000000000000',
    '00000000-0000-0000-0000-000000000001'
); 