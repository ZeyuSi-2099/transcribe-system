"use client"

import { useAuth } from "@/contexts/AuthContext"
import { AuthState } from "@/lib/supabase"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { Loader2 } from "lucide-react"

interface ProtectedRouteProps {
  children: React.ReactNode
  redirectTo?: string
  requireAuth?: boolean
}

export default function ProtectedRoute({ 
  children, 
  redirectTo = "/auth/login",
  requireAuth = true 
}: ProtectedRouteProps) {
  const { authState, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (loading) return

    if (requireAuth && authState === AuthState.UNAUTHENTICATED) {
      router.push(redirectTo)
    } else if (!requireAuth && authState === AuthState.AUTHENTICATED) {
      router.push("/dashboard")
    }
  }, [authState, loading, router, redirectTo, requireAuth])

  // 显示加载状态
  if (loading || authState === AuthState.LOADING) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
          <p className="mt-2 text-sm text-muted-foreground">加载中...</p>
        </div>
      </div>
    )
  }

  // 如果需要认证但用户未认证，显示加载状态（即将重定向）
  if (requireAuth && authState === AuthState.UNAUTHENTICATED) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
          <p className="mt-2 text-sm text-muted-foreground">重定向到登录页面...</p>
        </div>
      </div>
    )
  }

  // 如果不需要认证但用户已认证，显示加载状态（即将重定向）
  if (!requireAuth && authState === AuthState.AUTHENTICATED) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
          <p className="mt-2 text-sm text-muted-foreground">重定向到仪表板...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
} 