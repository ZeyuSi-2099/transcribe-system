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
import { ArrowUp, Square, Wand2, Upload, FileText, Eye, BarChart3, Settings, Sliders } from "lucide-react"
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
  const [inputText, setInputText] = useState("")
  const [isConverting, setIsConverting] = useState(false)
  const [conversionResult, setConversionResult] = useState<ConversionResult | null>(null)
  const [selectedRuleSetId, setSelectedRuleSetId] = useState<string>('default')
  
  const searchParams = useSearchParams()
  const router = useRouter()
  
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
    { id: 'default', name: '官方-通用规则集', description: '适用于大多数笔录转换场景', isDefault: false, enabledRulesCount: 8 }
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
    // 文件上传成功后，轮询检查转换状态
    const checkStatus = async (id: number) => {
      const statusResponse = await fetch(`/api/v1/transcription/${id}`)
      const statusData = await statusResponse.json()
      
      if (statusData.status === 'completed') {
        setConversionResult(statusData)
        adjustOutputHeight()
      } else if (statusData.status === 'failed') {
        setConversionResult({
          id: statusData.id,
          original_text: statusData.original_text || '',
          converted_text: '转换失败：' + (statusData.error_message || '未知错误'),
          status: 'failed'
        })
      } else {
        setTimeout(() => checkStatus(id), 2000)
      }
    }
    
    checkStatus(result.id)
  }

  const navigateToRuleManagement = () => {
    router.push('/rules')
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
                  <Tabs defaultValue="text" className="w-full flex-1 flex flex-col">
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
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-sm">原始笔录</CardTitle>
                            {inputText && (
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={handleClearInput}
                                className="text-xs h-6"
                              >
                                清空
                              </Button>
                            )}
                          </div>
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
                          <CardTitle className="text-sm">文件上传</CardTitle>
                        </CardHeader>
                        <CardContent className="flex-1 pb-2">
                          <FileUploadZone 
                            onUploadSuccess={handleFileUploadSuccess}
                            onUploadError={(error) => console.error('Upload error:', error)}
                          />
                        </CardContent>
                      </Card>
                    </TabsContent>
                  </Tabs>
                </div>

                {/* 右侧：转换结果 */}
                <div className="flex flex-col h-full">
                  <Card className="flex-1 flex flex-col">
                    <CardHeader className="pb-1 pt-2">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm">转换结果</CardTitle>
                        {conversionResult && (
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={handleClearResult}
                            className="text-xs h-6"
                          >
                            清空
                          </Button>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent className="flex-1 pb-2">
                      <div className="relative border border-input bg-background rounded-lg h-full">
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

              {/* 转换结果详情 - 仅在有结果时显示 */}
              {conversionResult && (
                <Card className="mb-1">
                  <CardHeader className="py-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Eye className="h-4 w-4" />
                      转换结果详情
                    </CardTitle>
                    <CardDescription className="text-xs">
                      查看详细的转换信息和质量评估
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2 pb-2">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div className="space-y-1">
                        <p className="text-xs font-medium">任务ID</p>
                        <p className="text-lg font-bold">{conversionResult.id}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-xs font-medium">状态</p>
                        <Badge variant={conversionResult.status === 'completed' ? 'default' : 'destructive'} className="text-xs">
                          {conversionResult.status === 'completed' ? '已完成' : '失败'}
                        </Badge>
                      </div>
                      {conversionResult.processing_time && (
                        <div className="space-y-1">
                          <p className="text-xs font-medium">处理时间</p>
                          <p className="text-lg font-bold">{conversionResult.processing_time.toFixed(2)}s</p>
                        </div>
                      )}
                      {conversionResult.quality_metrics?.overall_score && (
                        <div className="space-y-1">
                          <p className="text-xs font-medium">质量评分</p>
                          <div className="flex items-center gap-2">
                            <Progress value={conversionResult.quality_metrics.overall_score} className="flex-1 h-2" />
                            <span className="text-xs font-medium">
                              {Math.round(conversionResult.quality_metrics.overall_score)}%
                            </span>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* 质量指标详情 */}
                    {conversionResult.quality_metrics && Object.keys(conversionResult.quality_metrics).length > 1 && (
                      <div className="space-y-1">
                        <h4 className="font-medium text-sm">详细指标</h4>
                        <div className="grid grid-cols-2 gap-1 text-xs">
                          {Object.entries(conversionResult.quality_metrics).map(([key, value]) => {
                            if (key === 'overall_score') return null
                            
                            const formatValue = (val: any): string => {
                              if (typeof val === 'number') {
                                return val < 1 ? `${(val * 100).toFixed(1)}%` : val.toFixed(2)
                              }
                              return String(val)
                            }
                            
                            const formatKey = (k: string): string => {
                              const keyMap: { [key: string]: string } = {
                                'word_count_retention': '字数保留率',
                                'semantic_similarity': '语义相似度',
                                'readability_score': '可读性评分',
                                'length_ratio': '长度比率'
                              }
                              return keyMap[k] || k
                            }
                            
                            return (
                              <div key={key} className="flex justify-between">
                                <span className="text-muted-foreground">{formatKey(key)}:</span>
                                <span className="font-medium">{formatValue(value)}</span>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
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