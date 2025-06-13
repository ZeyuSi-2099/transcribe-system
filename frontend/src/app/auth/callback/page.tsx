"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { supabase } from "@/lib/supabase"
import { Loader2 } from "lucide-react"

export default function AuthCallback() {
  const router = useRouter()

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // 处理OAuth回调
        const { data, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('认证回调错误:', error)
          router.push('/auth/login?error=oauth_callback_error')
          return
        }

        if (data.session) {
          console.log('OAuth认证成功:', data.session.user.email)
          // 重定向到仪表板
          router.push('/dashboard')
        } else {
          // 没有会话，重定向到登录页
          router.push('/auth/login')
        }
      } catch (error) {
        console.error('处理认证回调时出错:', error)
        router.push('/auth/login?error=callback_error')
      }
    }

    handleAuthCallback()
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
        <p className="mt-2 text-sm text-muted-foreground">正在完成登录...</p>
      </div>
    </div>
  )
} 