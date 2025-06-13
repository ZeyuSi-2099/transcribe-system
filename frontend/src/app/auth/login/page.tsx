"use client"

import { Suspense } from "react"
import AuthForm from "@/components/auth/AuthForm"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

function AuthPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="absolute top-4 left-4">
        <Link 
          href="/" 
          className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          返回首页
        </Link>
      </div>
      
      <div className="w-full max-w-md">
        <AuthForm defaultTab="signin" />
      </div>
    </div>
  )
}

function PageLoading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
        <p className="text-gray-600">加载中...</p>
      </div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={<PageLoading />}>
      <AuthPage />
    </Suspense>
  )
} 