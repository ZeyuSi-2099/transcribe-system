"use client"

import React from 'react'
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, CheckCircle, Info } from "lucide-react"
import Link from "next/link"

interface OAuthStatusProps {
  error?: string | null
  isConfigured?: boolean
  showConfigGuide?: boolean
}

export default function OAuthStatus({ 
  error, 
  isConfigured = false, 
  showConfigGuide = true 
}: OAuthStatusProps) {
  
  // 处理URL参数中的错误
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search)
      const urlError = urlParams.get('error')
      if (urlError && !error) {
        // 可以通过props或状态管理来处理URL错误
      }
    }
  }, [error])

  if (error === 'validation_failed' || error === 'oauth_callback_error') {
    return (
      <Alert className="mb-4 border-orange-200 bg-orange-50">
        <AlertCircle className="h-4 w-4 text-orange-600" />
        <AlertTitle className="text-orange-800">Google 登录未配置</AlertTitle>
        <AlertDescription className="text-orange-700">
          <p className="mb-2">
            Supabase项目中尚未启用Google OAuth提供商。要启用Google登录功能，请按照以下步骤：
          </p>
          {showConfigGuide && (
            <div className="space-y-1 text-sm">
              <p>1. 访问 <a href="https://app.supabase.com/" target="_blank" rel="noopener noreferrer" className="underline font-medium">Supabase Dashboard</a></p>
              <p>2. 选择您的项目</p>
              <p>3. 转到 Authentication → Providers</p>
              <p>4. 启用 Google 提供商并配置客户端凭据</p>
              <div className="mt-3 flex flex-col space-y-2">
                <Link href="/docs/Google_OAuth_Setup.md" className="underline font-medium text-orange-700 hover:text-orange-800">
                  📖 查看详细配置指南 →
                </Link>
                <Link href="/auth/config-check" className="underline font-medium text-blue-700 hover:text-blue-800">
                  🔧 使用配置验证工具 →
                </Link>
              </div>
            </div>
          )}
        </AlertDescription>
      </Alert>
    )
  }

  if (error === 'callback_error') {
    return (
      <Alert className="mb-4 border-red-200 bg-red-50">
        <AlertCircle className="h-4 w-4 text-red-600" />
        <AlertTitle className="text-red-800">登录回调错误</AlertTitle>
        <AlertDescription className="text-red-700">
          Google登录过程中出现错误，请重试或使用邮箱登录。
        </AlertDescription>
      </Alert>
    )
  }

  if (isConfigured) {
    return (
      <Alert className="mb-4 border-green-200 bg-green-50">
        <CheckCircle className="h-4 w-4 text-green-600" />
        <AlertTitle className="text-green-800">Google 登录已配置</AlertTitle>
        <AlertDescription className="text-green-700">
          您可以使用Google账户进行登录和注册。
        </AlertDescription>
      </Alert>
    )
  }

  return null
} 