"use client"

import React from "react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-lg text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          🎉 笔录转换工具
        </h1>
        <p className="text-gray-600 mb-6">
          欢迎使用基于LLM和规则引擎的智能笔录转换系统
        </p>
        <div className="space-y-3">
          <p className="text-sm text-green-600">✅ 前端部署成功</p>
          <p className="text-sm text-blue-600">🚀 Vercel 运行正常</p>
          <p className="text-sm text-purple-600">🔗 域名解析正确</p>
        </div>
        <p className="text-xs text-gray-500 mt-6">
          部署时间: {new Date().toLocaleString('zh-CN')}
        </p>
      </div>
    </div>
  )
}
