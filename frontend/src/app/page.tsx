"use client"

import * as React from "react"
import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  ArrowRight, 
  Zap, 
  Shield, 
  BarChart3, 
  FileText, 
  Settings, 
  Upload,
  Download,
  CheckCircle,
  Github,
  ExternalLink
} from "lucide-react"

interface FeatureCardProps {
  icon: React.ReactNode
  title: string
  description: string
  badge?: string
}

function FeatureCard({ icon, title, description, badge }: FeatureCardProps) {
  return (
    <Card className="relative overflow-hidden transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
              {icon}
            </div>
            <CardTitle className="text-lg">{title}</CardTitle>
          </div>
          {badge && (
            <Badge variant="secondary" className="text-xs">
              {badge}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-sm leading-relaxed">
          {description}
        </CardDescription>
      </CardContent>
    </Card>
  )
}

interface StepCardProps {
  step: number
  title: string
  description: string
  icon: React.ReactNode
}

function StepCard({ step, title, description, icon }: StepCardProps) {
  return (
    <div className="relative">
      <div className="flex items-center space-x-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground font-semibold">
          {step}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-lg mb-1">{title}</h3>
          <p className="text-muted-foreground text-sm leading-relaxed">
            {description}
          </p>
        </div>
        <div className="hidden md:block text-muted-foreground">
          {icon}
        </div>
      </div>
    </div>
  )
}

export default function LandingPage() {
  const [isLoading, setIsLoading] = useState(false)

  const features = [
    {
      icon: <Zap className="h-5 w-5" />,
      title: "智能转换引擎",
      description: "结合确定性规则与大语言模型，确保转换的准确性和流畅性。支持多种LLM后端。",
      badge: "核心功能"
    },
    {
      icon: <Settings className="h-5 w-5" />,
      title: "灵活规则配置",
      description: "三级规则结构设计，支持通用规则集和个性化定制规则，满足不同场景需求。",
    },
    {
      icon: <BarChart3 className="h-5 w-5" />,
      title: "质量检验体系",
      description: "完整的定量和定性指标评估，包含字数保留率、语义连贯性等多维度分析。",
    },
    {
      icon: <FileText className="h-5 w-5" />,
      title: "多格式支持",
      description: "支持文本直接输入、.txt和.docx文件上传，以及多格式结果导出。",
    },
    {
      icon: <Shield className="h-5 w-5" />,
      title: "数据安全保护",
      description: "完整的用户认证体系，数据加密存储，确保笔录内容的隐私安全。",
    },
    {
      icon: <Upload className="h-5 w-5" />,
      title: "批量处理能力",
      description: "支持多文件同时处理，提高工作效率，适合大规模笔录转换需求。",
      badge: "规划中"
    }
  ]

  const steps = [
    {
      step: 1,
      title: "上传笔录",
      description: "支持文本直接输入或文件上传(.txt, .docx)，自动识别格式并预览内容。",
      icon: <Upload className="h-5 w-5" />
    },
    {
      step: 2,
      title: "配置规则",
      description: "选择通用规则集或定制专属规则，实时预览转换效果，确保符合需求。",
      icon: <Settings className="h-5 w-5" />
    },
    {
      step: 3,
      title: "智能转换",
      description: "混合处理引擎自动执行转换，实时显示进度，确保高质量输出结果。",
      icon: <Zap className="h-5 w-5" />
    },
    {
      step: 4,
      title: "查看结果",
      description: "对比原文和转换结果，查看详细的质量指标，支持多格式下载。",
      icon: <Download className="h-5 w-5" />
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] dark:bg-grid-slate-700/25 dark:[mask-image:linear-gradient(0deg,rgba(255,255,255,0.1),rgba(255,255,255,0.5))]" />
        <div className="relative">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24">
            <div className="text-center">
              <h1 className="text-4xl sm:text-6xl font-bold text-slate-900 dark:text-white mb-6">
                智能笔录
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                  转换系统
                </span>
              </h1>
              <p className="text-xl text-slate-600 dark:text-slate-300 mb-8 max-w-3xl mx-auto leading-relaxed">
                基于大语言模型与确定性规则的混合处理架构，将访谈对话记录转换为高质量的第一人称叙述文档。
                支持自定义规则配置，提供完整的质量检验体系。
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link href="/dashboard">
                  <Button size="lg" className="w-full sm:w-auto" disabled={isLoading}>
                    开始使用
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/rules">
                  <Button variant="outline" size="lg" className="w-full sm:w-auto">
                    查看规则配置
                    <ExternalLink className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-white dark:bg-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
              强大功能特性
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
              集成先进的AI技术与灵活的规则引擎，为您提供专业级的笔录转换解决方案
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <FeatureCard key={index} {...feature} />
            ))}
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="py-24 bg-slate-50 dark:bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
              使用流程
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
              简单四步，完成从原始笔录到高质量第一人称叙述的智能转换
            </p>
          </div>
          <div className="space-y-8">
            {steps.map((step, index) => (
              <StepCard key={index} {...step} />
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-24 bg-white dark:bg-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary mb-2">95%+</div>
              <div className="text-slate-600 dark:text-slate-300">转换准确率</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">3s</div>
              <div className="text-slate-600 dark:text-slate-300">平均处理时间</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">10+</div>
              <div className="text-slate-600 dark:text-slate-300">支持文件格式</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            立即开始您的笔录转换之旅
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            体验AI驱动的智能转换，提升您的工作效率
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg" variant="secondary" className="w-full sm:w-auto">
                免费开始使用
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="w-full sm:w-auto border-white text-white hover:bg-white hover:text-blue-600">
              <Github className="mr-2 h-4 w-4" />
              查看源码
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-slate-900 text-slate-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-sm">
              © 2024 笔录转换系统. 基于现代Web技术构建，为高效文档处理而设计。
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
