"use client"

import * as React from "react"
import { useState, useRef, useEffect, useCallback, Suspense } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ArrowUp, Square, Wand2, Upload, FileText, Eye, BarChart3, Settings, Sliders, Download } from "lucide-react"
import { cn } from "@/lib/utils"
import FileUploadZone from "@/components/FileUploadZone"
import { useRouter, useSearchParams } from "next/navigation"
import Sidebar from '@/components/Sidebar'
import ProtectedRoute from '@/components/auth/ProtectedRoute'

interface TranscriptionConverterProps {
  className?: string
}

interface UseAutoResizeTextareaProps {
  minHeight: number
  maxHeight?: number
}

interface ConversionResult {
  id: number
  original_text: string
  converted_text: string
  quality_metrics?: any
  processing_stages?: any
  status: string
  processing_time?: number
}

interface RuleConfig {
  ruleSetId: string
  ruleSetName: string
  enabledRules: Array<{
    categoryId: string
    primaryRuleId: string
    secondaryRuleId?: string
  }>
}

interface RuleSet {
  id: string
  name: string
  description: string
  isDefault: boolean
  enabledRulesCount: number
}

function useAutoResizeTextarea({
  minHeight,
  maxHeight,
}: UseAutoResizeTextareaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const adjustHeight = useCallback(
    (reset?: boolean) => {
      const textarea = textareaRef.current
      if (!textarea) return

      if (reset) {
        textarea.style.height = `${minHeight}px`
        return
      }

      // Temporarily shrink to get the right scrollHeight
      textarea.style.height = `${minHeight}px`

      // Calculate new height
      const newHeight = Math.max(
        minHeight,
        Math.min(
          textarea.scrollHeight,
          maxHeight ?? Number.POSITIVE_INFINITY
        )
      )

      textarea.style.height = `${newHeight}px`
    },
    [minHeight, maxHeight]
  )

  useEffect(() => {
    // Set initial height
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = `${minHeight}px`
    }
  }, [minHeight])

  // Adjust height on window resize
  useEffect(() => {
    const handleResize = () => adjustHeight()
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [adjustHeight])

  return { textareaRef, adjustHeight }
}

function TranscriptionConverter({ className }: TranscriptionConverterProps) {
  const router = useRouter()
  const [inputText, setInputText] = useState('')
  const [conversionResult, setConversionResult] = useState<ConversionResult | null>(null)
  const [isConverting, setIsConverting] = useState(false)
  const [selectedRuleSetId, setSelectedRuleSetId] = useState('default')
  const [activeTab, setActiveTab] = useState('text')
  const [uploadedFileInfo, setUploadedFileInfo] = useState<{name: string, type: string} | null>(null)
  const [showAnalysisModal, setShowAnalysisModal] = useState(false)
  
  const searchParams = useSearchParams()
  
  const { textareaRef: inputRef, adjustHeight: adjustInputHeight } = useAutoResizeTextarea({
    minHeight: 120,
    maxHeight: 300,
  })
  
  const { textareaRef: outputRef, adjustHeight: adjustOutputHeight } = useAutoResizeTextarea({
    minHeight: 120,
    maxHeight: 300,
  })

  // 更新规则集数据 - 只保留一个官方规则集
  const [availableRuleSets] = useState<RuleSet[]>([
    { id: 'default', name: '官方-通用规则集', description: '适用于大多数笔录转换场景', isDefault: true, enabledRulesCount: 8 }
  ])

  const selectedRuleSet = availableRuleSets.find(rs => rs.id === selectedRuleSetId)

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value)
    adjustInputHeight()
  }

  const handleConvert = async () => {
    if (!inputText.trim()) return
    
    setIsConverting(true)
    setConversionResult(null)
    
    try {
      // 构建规则配置
      const ruleConfig = {
        ruleSetId: selectedRuleSetId,
        ruleSetName: selectedRuleSet?.name || '官方-通用规则集',
        enabledRules: [] // 这里应该根据选中的规则集获取启用的规则
      }

      // 调用后端API进行转换，包含规则配置
      const response = await fetch('/api/v1/transcription/convert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: '文本转换',
          original_text: inputText,
          file_name: null,
          file_type: 'text',
          rule_config: ruleConfig
        }),
      })
      
      if (!response.ok) {
        throw new Error('转换失败')
      }
      
      const result = await response.json()
      
      // 轮询检查转换状态
      const checkStatus = async (id: number) => {
        const statusResponse = await fetch(`/api/v1/transcription/${id}`)
        const statusData = await statusResponse.json()
        
        if (statusData.status === 'completed') {
          setConversionResult(statusData)
          setIsConverting(false)
          adjustOutputHeight()
        } else if (statusData.status === 'failed') {
          setConversionResult({
            id: statusData.id,
            original_text: inputText,
            converted_text: '转换失败：' + (statusData.error_message || '未知错误'),
            status: 'failed'
          })
          setIsConverting(false)
          adjustOutputHeight()
        } else {
          // 继续轮询
          setTimeout(() => checkStatus(id), 1000)
        }
      }
      
      // 开始轮询
      checkStatus(result.id)
      
    } catch (error) {
      console.error('转换错误:', error)
      setConversionResult({
        id: 0,
        original_text: inputText,
        converted_text: '转换失败，请检查网络连接或稍后重试',
        status: 'failed'
      })
      setIsConverting(false)
      adjustOutputHeight()
    }
  }

  const handleClearInput = () => {
    setInputText("")
    adjustInputHeight(true)
  }

  const handleClearResult = () => {
    setConversionResult(null)
    adjustOutputHeight(true)
  }

  const handleFileUploadSuccess = (result: any) => {
    // 文件上传成功后，设置输入文本但不切换标签页
    setInputText(result.original_text || '')
    // 保存上传文件信息
    setUploadedFileInfo({
      name: result.file_name || '',
      type: result.file_type || 'text/plain'
    })
    // 调整输入框高度
    adjustInputHeight()
  }

  const navigateToRuleManagement = () => {
    router.push('/rules')
  }

  const handleDownloadResult = () => {
    if (!conversionResult?.converted_text) return
    
    const content = conversionResult.converted_text
    const originalFileName = uploadedFileInfo?.name || '转换结果'
    const fileType = uploadedFileInfo?.type || 'text/plain'
    
    // 生成文件名：在原文件名基础上添加"转换后"后缀
    let fileName = originalFileName
    if (fileName.includes('.')) {
      const lastDotIndex = fileName.lastIndexOf('.')
      const nameWithoutExt = fileName.substring(0, lastDotIndex)
      const extension = fileName.substring(lastDotIndex)
      fileName = `${nameWithoutExt}_转换后${extension}`
    } else {
      fileName = `${fileName}_转换后.txt`
    }
    
    // 创建并下载文件
    const blob = new Blob([content], { type: fileType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const handleTabChange = (value: string) => {
    // 如果从文件上传切换到文本输入，清空输入文本
    if (activeTab === 'upload' && value === 'text') {
      setInputText('')
      setUploadedFileInfo(null)
      // 清空转换结果
      setConversionResult(null)
    }
    setActiveTab(value)
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 侧边栏 */}
      <Sidebar />
      
      {/* 主内容区域 */}
      <div className="flex-1 overflow-hidden ml-14">
        <div className={cn("h-full p-3 overflow-auto", className)}>
          <div className="w-full max-w-7xl mx-auto">
            <div className="flex flex-col space-y-3">
              {/* 页面标题和描述 */}
              <div className="space-y-1">
                <h1 className="text-xl font-bold text-foreground">笔录转换工具</h1>
                <p className="text-xs text-muted-foreground">当前为内测版本，支持通用转换规则与自定义转换规则</p>
              </div>

              {/* 规则配置区域 - 深色样式 */}
              <Card className="border-gray-800 bg-gray-900 text-white">
                <CardHeader className="pb-2 pt-2">
                  <CardTitle className="text-base flex items-center gap-2 text-white">
                    <Settings className="h-4 w-4" />
                    规则配置
                  </CardTitle>
                  <CardDescription className="text-gray-300 text-xs">
                    选择适合的规则集来优化转换效果
                  </CardDescription>
                </CardHeader>
                <CardContent className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-white">规则集：</span>
                        <Select value={selectedRuleSetId} onValueChange={setSelectedRuleSetId}>
                          <SelectTrigger className="w-52 bg-gray-800 border-gray-700 text-white text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent className="bg-gray-800 border-gray-700">
                            {availableRuleSets.map(ruleSet => (
                              <SelectItem key={ruleSet.id} value={ruleSet.id} className="text-white hover:bg-gray-700 text-xs">
                                <span>{ruleSet.name}</span>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      {selectedRuleSet && (
                        <div className="text-xs text-gray-300">
                          <span>{selectedRuleSet.description}</span>
                          <span className="ml-1">• 已启用 {selectedRuleSet.enabledRulesCount} 个规则</span>
                        </div>
                      )}
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="bg-gray-800 border-gray-700 text-white hover:bg-gray-700 hover:text-white text-xs"
                      onClick={navigateToRuleManagement}
                    >
                      <Sliders className="mr-1 h-3 w-3" />
                      规则配置与管理
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* 主要工作区 - 左右两列布局 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 h-[calc(100vh-320px)]">
                {/* 左侧：输入区域 */}
                <div className="flex flex-col h-full">
                  <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full flex-1 flex flex-col">
                    <TabsList className="grid w-full grid-cols-2 h-8">
                      <TabsTrigger value="text" className="flex items-center gap-1 text-xs">
                        <FileText className="h-3 w-3" />
                        文本输入
                      </TabsTrigger>
                      <TabsTrigger value="upload" className="flex items-center gap-1 text-xs">
                        <Upload className="h-3 w-3" />
                        文件上传
                      </TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="text" className="flex-1 mt-1 flex flex-col">
                      <Card className="flex-1 flex flex-col">
                        <CardHeader className="pb-1 pt-2">
                          <CardTitle className="text-sm">原始笔录</CardTitle>
                        </CardHeader>
                        <CardContent className="flex-1 pb-2">
                          <div className="relative border border-input bg-background rounded-lg focus-within:ring-1 focus-within:ring-ring h-full">
                            <Textarea
                              ref={inputRef}
                              value={inputText}
                              onChange={handleInputChange}
                              placeholder="请在此处粘贴或输入原始笔录内容..."
                              className="h-full min-h-[calc(100%-2px)] resize-none border-0 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 text-sm"
                            />
                          </div>
                        </CardContent>
                      </Card>
                    </TabsContent>
                    
                    <TabsContent value="upload" className="flex-1 mt-1 flex flex-col">
                      <Card className="flex-1 flex flex-col">
                        <CardHeader className="pb-1 pt-2">
                          <CardTitle className="text-sm">原始笔录</CardTitle>
                        </CardHeader>
                        <CardContent className="flex-1 pb-2">
                          <FileUploadZone 
                            onUploadSuccess={handleFileUploadSuccess}
                            onUploadError={(error) => console.error('Upload error:', error)}
                            inputText={inputText}
                            onInputChange={(text) => {
                              setInputText(text)
                              adjustInputHeight()
                            }}
                          />
                        </CardContent>
                      </Card>
                    </TabsContent>
                  </Tabs>
                </div>

                {/* 右侧：按钮区域和转换结果 */}
                <div className="flex flex-col h-full space-y-3">
                  {/* 右上角独立按钮区域 */}
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowAnalysisModal(true)}
                      disabled={!conversionResult}
                      className={cn(
                        "text-xs",
                        !conversionResult && "text-muted-foreground cursor-not-allowed"
                      )}
                    >
                      <BarChart3 className="h-3 w-3 mr-1" />
                      结果分析
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleDownloadResult}
                      disabled={!conversionResult}
                      className={cn(
                        "text-xs",
                        !conversionResult && "text-muted-foreground cursor-not-allowed"
                      )}
                    >
                      <Download className="h-3 w-3 mr-1" />
                      结果下载
                    </Button>
                  </div>

                  {/* 转换结果区域 - 与左侧对齐 */}
                  <Card className="flex-1 flex flex-col">
                    <CardHeader className="pb-1 pt-2">
                      <CardTitle className="text-sm">转换结果</CardTitle>
                    </CardHeader>
                    <CardContent className="flex-1 pb-2">
                      <div className="relative border border-input bg-background rounded-lg focus-within:ring-1 focus-within:ring-ring h-full">
                        <Textarea
                          ref={outputRef}
                          value={conversionResult?.converted_text || ''}
                          readOnly
                          placeholder="转换后的内容将显示在这里..."
                          className="h-full min-h-[calc(100%-2px)] resize-none border-0 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 text-sm"
                        />
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* 转换按钮 */}
              <div className="flex justify-center py-1">
                <Button
                  onClick={handleConvert}
                  disabled={!inputText.trim() || isConverting}
                  size="default"
                  className="gap-2 px-6 h-8 text-sm"
                >
                  {isConverting ? (
                    <>
                      <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      转换中...
                    </>
                  ) : (
                    <>
                      <Wand2 className="size-3" />
                      开始转换
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 结果分析浮窗 */}
      <Dialog open={showAnalysisModal} onOpenChange={setShowAnalysisModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>转换结果分析</DialogTitle>
          </DialogHeader>
          
          {conversionResult && (
            <div className="space-y-6">
              {/* 质量评分 */}
              <div className="bg-muted/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium">综合质量评分</h3>
                  <span className="text-2xl font-bold text-primary">
                    {conversionResult.quality_score?.toFixed(1) || 'N/A'}
                  </span>
                </div>
                <Progress 
                  value={conversionResult.quality_score || 0} 
                  className="h-2"
                />
              </div>

              {/* 质量指标详情 */}
              {conversionResult.quality_metrics && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* 字符统计 */}
                  <div className="bg-card border rounded-lg p-4">
                    <h4 className="font-medium mb-3 flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      字符统计
                    </h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">原始字符数:</span>
                        <span>{conversionResult.quality_metrics.character_count?.original || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">转换后字符数:</span>
                        <span>{conversionResult.quality_metrics.character_count?.converted || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">保留率:</span>
                        <span>{((conversionResult.quality_metrics.character_count?.retention_rate || 0) * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>

                  {/* 词汇统计 */}
                  <div className="bg-card border rounded-lg p-4">
                    <h4 className="font-medium mb-3 flex items-center gap-2">
                      <BarChart3 className="h-4 w-4" />
                      词汇统计
                    </h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">原始词数:</span>
                        <span>{conversionResult.quality_metrics.word_count?.original || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">转换后词数:</span>
                        <span>{conversionResult.quality_metrics.word_count?.converted || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">保留率:</span>
                        <span>{((conversionResult.quality_metrics.word_count?.retention_rate || 0) * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>

                  {/* 压缩比 */}
                  <div className="bg-card border rounded-lg p-4">
                    <h4 className="font-medium mb-3">压缩比</h4>
                    <div className="text-2xl font-bold text-primary">
                      {((conversionResult.quality_metrics.compression_ratio || 0) * 100).toFixed(1)}%
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      转换后文本相对原文的长度比例
                    </p>
                  </div>

                  {/* 语言质量 */}
                  <div className="bg-card border rounded-lg p-4">
                    <h4 className="font-medium mb-3">语言质量</h4>
                    <div className="text-2xl font-bold text-primary">
                      {(conversionResult.quality_metrics.language_quality?.overall_score || 0).toFixed(1)}
                    </div>
                    <div className="space-y-1 text-xs text-muted-foreground mt-2">
                      <div>流畅度: {(conversionResult.quality_metrics.language_quality?.fluency || 0).toFixed(1)}</div>
                      <div>连贯性: {(conversionResult.quality_metrics.language_quality?.coherence || 0).toFixed(1)}</div>
                      <div>语法正确性: {(conversionResult.quality_metrics.language_quality?.grammar || 0).toFixed(1)}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* 应用的规则 */}
              {conversionResult.applied_rules && conversionResult.applied_rules.length > 0 && (
                <div className="bg-card border rounded-lg p-4">
                  <h4 className="font-medium mb-3">应用的转换规则</h4>
                  <div className="space-y-2">
                    {conversionResult.applied_rules.map((rule: any, index: number) => (
                      <div key={index} className="flex items-center justify-between text-sm">
                        <span>{rule.rule_name}</span>
                        <span className="text-xs text-muted-foreground px-2 py-1 bg-muted rounded">
                          {rule.rule_type}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

// 创建一个包装的加载组件
function PageLoading() {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
        <p className="text-gray-600">加载中...</p>
      </div>
    </div>
  )
}

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <Suspense fallback={<PageLoading />}>
        <TranscriptionConverter />
      </Suspense>
    </ProtectedRoute>
  )
} 