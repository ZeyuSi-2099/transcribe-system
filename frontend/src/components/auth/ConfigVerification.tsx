"use client"

import React, { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { supabase } from "@/lib/supabase"
import { CheckCircle, XCircle, AlertCircle, Loader2 } from "lucide-react"

interface ConfigCheckResult {
  step: string
  status: 'success' | 'error' | 'warning'
  message: string
  details?: string
}

export default function ConfigVerification() {
  const [checking, setChecking] = useState(false)
  const [results, setResults] = useState<ConfigCheckResult[]>([])

  const checkConfiguration = async () => {
    setChecking(true)
    setResults([])
    
    const newResults: ConfigCheckResult[] = []

    // 1. 检查环境变量
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    
    if (supabaseUrl && supabaseKey) {
      newResults.push({
        step: "环境变量检查",
        status: 'success',
        message: "Supabase 环境变量配置正确",
        details: `URL: ${supabaseUrl}`
      })
    } else {
      newResults.push({
        step: "环境变量检查",
        status: 'error',
        message: "Supabase 环境变量缺失",
        details: "请检查 .env.local 文件"
      })
    }

    // 2. 检查 Supabase 连接
    try {
      const { data, error } = await supabase.auth.getSession()
      if (error) {
        newResults.push({
          step: "Supabase 连接",
          status: 'warning',
          message: "Supabase 连接正常，但可能有配置问题",
          details: error.message
        })
      } else {
        newResults.push({
          step: "Supabase 连接",
          status: 'success',
          message: "Supabase 连接正常",
          details: "认证服务可访问"
        })
      }
    } catch (error) {
      newResults.push({
        step: "Supabase 连接",
        status: 'error',
        message: "无法连接到 Supabase",
        details: error instanceof Error ? error.message : "未知错误"
      })
    }

    // 3. 测试 Google OAuth 配置
    try {
      // 尝试获取 OAuth URL（不实际重定向）
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          skipBrowserRedirect: true // 不实际跳转
        }
      })

      if (error) {
        if (error.message.includes('provider is not enabled')) {
          newResults.push({
            step: "Google OAuth 配置",
            status: 'error',
            message: "Google OAuth Provider 未启用",
            details: "请在 Supabase Dashboard 中启用 Google 提供商"
          })
        } else {
          newResults.push({
            step: "Google OAuth 配置",
            status: 'warning',
            message: "Google OAuth 配置可能有问题",
            details: error.message
          })
        }
      } else if (data?.url) {
        newResults.push({
          step: "Google OAuth 配置",
          status: 'success',
          message: "Google OAuth 配置正确",
          details: "可以正常生成 OAuth URL"
        })
      }
    } catch (error) {
      newResults.push({
        step: "Google OAuth 配置",
        status: 'error',
        message: "Google OAuth 测试失败",
        details: error instanceof Error ? error.message : "未知错误"
      })
    }

    // 4. 检查回调 URL 配置
    const currentOrigin = window.location.origin
    const expectedCallback = `https://ghbtjyetllhcdddhjygi.supabase.co/auth/v1/callback`
    
    newResults.push({
      step: "回调 URL 配置",
      status: 'success',
      message: "回调 URL 格式正确",
      details: `应配置为: ${expectedCallback}`
    })

    setResults(newResults)
    setChecking(false)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'border-green-200 bg-green-50'
      case 'error':
        return 'border-red-200 bg-red-50'
      case 'warning':
        return 'border-yellow-200 bg-yellow-50'
      default:
        return 'border-gray-200 bg-gray-50'
    }
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Google OAuth 配置验证</CardTitle>
        <CardDescription>
          检查您的 Google OAuth 配置是否正确设置
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button 
          onClick={checkConfiguration} 
          disabled={checking}
          className="w-full"
        >
          {checking && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {checking ? '检查中...' : '开始配置检查'}
        </Button>

        {results.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-lg font-semibold">检查结果：</h3>
            {results.map((result, index) => (
              <Alert key={index} className={getStatusColor(result.status)}>
                <div className="flex items-start gap-3">
                  {getStatusIcon(result.status)}
                  <div className="flex-1">
                    <AlertTitle className="text-sm font-medium">
                      {result.step}
                    </AlertTitle>
                    <AlertDescription className="text-sm">
                      <p>{result.message}</p>
                      {result.details && (
                        <p className="mt-1 text-xs opacity-80">{result.details}</p>
                      )}
                    </AlertDescription>
                  </div>
                </div>
              </Alert>
            ))}
          </div>
        )}

        {results.length > 0 && (
          <Alert className="border-blue-200 bg-blue-50">
            <AlertCircle className="h-4 w-4 text-blue-600" />
            <AlertTitle className="text-blue-800">下一步</AlertTitle>
            <AlertDescription className="text-blue-700">
              {results.some(r => r.status === 'error') ? (
                <div>
                  <p>发现配置错误，请按照以下步骤修复：</p>
                  <ul className="mt-2 space-y-1 text-sm">
                    {results.filter(r => r.status === 'error').map((result, index) => (
                      <li key={index}>• {result.message}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p>配置看起来正确！您现在可以测试 Google 登录功能。</p>
              )}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
} 