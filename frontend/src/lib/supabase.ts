/**
 * Supabase客户端配置
 * 用于前端连接Supabase数据库和认证服务
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
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