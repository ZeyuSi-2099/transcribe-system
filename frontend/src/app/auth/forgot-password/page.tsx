"use client"

import { Suspense } from "react"
import PasswordResetForm from "@/components/auth/PasswordResetForm"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

function ForgotPasswordPage() {
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
        <PasswordResetForm />
      </div>
    </div>
  )
}

export default function Page() {
  return (
    <Suspense fallback={<div>加载中...</div>}>
      <ForgotPasswordPage />
    </Suspense>
  )
} 