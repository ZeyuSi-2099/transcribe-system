/**
 * Supabase客户端配置
 * 用于前端连接Supabase数据库和认证服务
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://ghbtjyetllhcdddhjygi.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdoYnRqeWV0bGxoY2RkZGhqeWdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxODk2OTMsImV4cCI6MjA2NDc2NTY5M30.9z608olZIwPpjNpcWJ_qgiJwAWHrctnLoSRE32mB47s'

// 在开发环境中警告，但不阻止构建
if ((!supabaseUrl || !supabaseAnonKey) && process.env.NODE_ENV === 'development') {
  console.warn('Warning: Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    flowType: 'pkce'
  }
})

// 数据库类型定义
export interface UserProfile {
  id: string
  username?: string
  email: string
  full_name?: string
  avatar_url?: string
  preferences: Record<string, any>
  created_at: string
  updated_at: string
}

export interface TransformationRule {
  id: string
  user_id: string
  name: string
  description?: string
  rule_type: string
  rule_config: Record<string, any>
  is_active: boolean
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface ConversionHistory {
  id: string
  user_id: string
  original_text: string
  converted_text: string
  rule_id?: string
  quality_score?: number
  processing_time?: number
  file_name?: string
  file_size?: number
  metadata: Record<string, any>
  created_at: string
}

export interface BatchJob {
  id: string
  user_id: string
  job_name: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  total_files: number
  processed_files: number
  failed_files: number
  rule_id?: string
  results: any[]
  error_log?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

// 认证相关的类型定义
export interface User {
  id: string
  email: string
  user_metadata?: {
    full_name?: string
    avatar_url?: string
  }
}

export interface Session {
  access_token: string
  refresh_token: string
  user: User
}

// 认证状态枚举
export enum AuthState {
  LOADING = 'loading',
  AUTHENTICATED = 'authenticated',
  UNAUTHENTICATED = 'unauthenticated'
} 