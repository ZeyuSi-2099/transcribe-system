"use client"

import * as React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { supabase } from "@/lib/supabase"
import { Mail, Loader2, ArrowLeft, CheckCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import Link from "next/link"

interface PasswordResetFormProps {
  className?: string
}

export default function PasswordResetForm({ className }: PasswordResetFormProps) {
  const [email, setEmail] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)

  const handlePasswordReset = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError("")
    setLoading(true)

    if (!email) {
      setError("请输入邮箱地址")
      setLoading(false)
      return
    }

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      })

      if (error) {
        setError(error.message || "发送重置邮件失败")
      } else {
        setSuccess(true)
      }
    } catch (error) {
      setError("发送重置邮件时出现错误")
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <Card className={cn("w-full max-w-md mx-auto", className)}>
        <CardHeader className="space-y-1 text-center">
          <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <CheckCircle className="h-6 w-6 text-green-600" />
          </div>
          <CardTitle className="text-2xl font-bold">邮件已发送</CardTitle>
          <CardDescription>
            我们已向您的邮箱发送了密码重置链接
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center text-sm text-muted-foreground">
            <p>请检查您的邮箱（包括垃圾邮件文件夹）</p>
            <p>并点击邮件中的链接来重置密码</p>
          </div>
          
          <div className="flex flex-col space-y-2">
            <Button
              variant="outline"
              onClick={() => {
                setSuccess(false)
                setEmail("")
                setError("")
              }}
              className="w-full"
            >
              重新发送邮件
            </Button>
            
            <Link href="/auth/login" className="w-full">
              <Button variant="ghost" className="w-full">
                <ArrowLeft className="mr-2 h-4 w-4" />
                返回登录
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn("w-full max-w-md mx-auto", className)}>
      <CardHeader className="space-y-1 text-center">
        <CardTitle className="text-2xl font-bold">重置密码</CardTitle>
        <CardDescription>
          输入您的邮箱地址，我们将发送重置链接给您
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handlePasswordReset} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="reset-email">邮箱地址</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                id="reset-email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-10"
                required
              />
            </div>
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-3">
              {error}
            </div>
          )}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            发送重置邮件
          </Button>
        </form>

        <div className="mt-6 text-center">
          <Link 
            href="/auth/login" 
            className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-flex items-center"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回登录
          </Link>
        </div>
      </CardContent>
    </Card>
  )
} 