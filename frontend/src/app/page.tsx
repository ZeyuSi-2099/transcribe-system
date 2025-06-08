"use client"

import * as React from "react"
import { useState, useRef, useEffect, useCallback } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowUp, Square, Wand2, Upload, FileText, Eye, BarChart3, Settings } from "lucide-react"
import { cn } from "@/lib/utils"
import FileUploadZone from "@/components/FileUploadZone"
import { useRouter, useSearchParams } from "next/navigation"
import Sidebar from '@/components/Sidebar'

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

  // 模拟规则集数据
  const [availableRuleSets] = useState<RuleSet[]>([
    { id: 'default', name: '通用规则集', description: '适用于大多数笔录转换场景', isDefault: true, enabledRulesCount: 8 },
    { id: 'meeting', name: '会议专用规则', description: '针对会议记录优化的规则集', isDefault: false, enabledRulesCount: 6 },
    { id: 'interview', name: '访谈优化规则', description: '专门用于访谈笔录的规则集', isDefault: false, enabledRulesCount: 7 },
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
        ruleSetName: selectedRuleSet?.name || '通用规则集',
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

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 侧边栏 */}
      <Sidebar />
      
      {/* 主内容区域 */}
      <div className="flex-1 overflow-hidden ml-14">
        <div className={cn("h-full p-6 overflow-y-auto", className)}>
          <div className="w-full max-w-6xl mx-auto">
      <div className="flex flex-col space-y-6">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-foreground">笔录转换工具</h1>
          <p className="text-muted-foreground">支持文本输入和文件上传两种方式，自动转换对话式笔录为叙述式笔录</p>
        </div>

              {/* 规则选择区域 */}
              <Card className="border-blue-200 bg-blue-50">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    规则配置
                  </CardTitle>
                  <CardDescription>
                    选择适合的规则集来优化转换效果
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">规则集：</span>
                        <Select value={selectedRuleSetId} onValueChange={setSelectedRuleSetId}>
                          <SelectTrigger className="w-64">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {availableRuleSets.map(ruleSet => (
                              <SelectItem key={ruleSet.id} value={ruleSet.id}>
                                <div className="flex items-center gap-2">
                                  <span>{ruleSet.name}</span>
                                  {ruleSet.isDefault && (
                                    <Badge variant="secondary" className="text-xs">默认</Badge>
                                  )}
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      {selectedRuleSet && (
                        <div className="text-sm text-gray-600">
                          <span>{selectedRuleSet.description}</span>
                          <span className="ml-2">• 已启用 {selectedRuleSet.enabledRulesCount} 个规则</span>
                        </div>
                      )}
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => router.push(`/rules?set=${selectedRuleSetId}`)}
                      className="gap-2"
                    >
                      <Settings className="h-4 w-4" />
                      配置规则
                    </Button>
                  </div>
                </CardContent>
              </Card>

        <Tabs defaultValue="text" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="text" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              文本输入
            </TabsTrigger>
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              文件上传
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="text" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium">原始笔录</h3>
                  {inputText && (
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={handleClearInput}
                    >
                      清空
                    </Button>
                  )}
                </div>
                <div className="relative border border-input bg-background rounded-lg focus-within:ring-1 focus-within:ring-ring">
                  <Textarea
                    ref={inputRef}
                    value={inputText}
                    onChange={handleInputChange}
                    placeholder="请在此处粘贴或输入原始笔录内容..."
                          className="min-h-[300px] resize-none border-0 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium">转换结果</h3>
                  {conversionResult && (
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={handleClearResult}
                    >
                      清空
                    </Button>
                  )}
                </div>
                <div className="relative border border-input bg-background rounded-lg">
                  <Textarea
                    ref={outputRef}
                    value={conversionResult?.converted_text || ''}
                    readOnly
                    placeholder="转换后的内容将显示在这里..."
                          className="min-h-[300px] resize-none border-0 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0"
                  />
                </div>
              </div>
            </div>

                  <div className="flex justify-center gap-4">
              <Button
                onClick={handleConvert}
                disabled={!inputText.trim() || isConverting}
                      className="gap-2"
              >
                {isConverting ? (
                  <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          转换中...
                  </>
                ) : (
                  <>
                    <Wand2 className="size-4" />
                    开始转换
                  </>
                )}
              </Button>
            </div>
          </TabsContent>
          
          <TabsContent value="upload" className="space-y-6">
            <FileUploadZone 
              onUploadSuccess={handleFileUploadSuccess}
              onUploadError={(error) => console.error('Upload error:', error)}
            />
          </TabsContent>
        </Tabs>

        {/* 转换结果详情 */}
        {conversionResult && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                转换结果详情
              </CardTitle>
              <CardDescription>
                查看详细的转换信息和质量评估
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="space-y-1">
                  <p className="text-sm font-medium">任务ID</p>
                  <p className="text-2xl font-bold">{conversionResult.id}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium">状态</p>
                  <Badge variant={conversionResult.status === 'completed' ? 'default' : 'destructive'}>
                    {conversionResult.status === 'completed' ? '已完成' : '失败'}
                  </Badge>
                </div>
                {conversionResult.processing_time && (
                  <div className="space-y-1">
                    <p className="text-sm font-medium">处理时间</p>
                    <p className="text-2xl font-bold">{conversionResult.processing_time.toFixed(2)}s</p>
                  </div>
                )}
                {conversionResult.quality_metrics?.overall_score && (
                  <div className="space-y-1">
                    <p className="text-sm font-medium">质量评分</p>
                    <div className="flex items-center gap-2">
                      <Progress value={conversionResult.quality_metrics.overall_score} className="flex-1" />
                      <span className="text-sm font-medium">
                        {Math.round(conversionResult.quality_metrics.overall_score)}%
                      </span>
                    </div>
                  </div>
                )}
              </div>
              
              {/* 质量指标详情 */}
              {conversionResult.quality_metrics && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium flex items-center gap-2">
                    <BarChart3 className="h-4 w-4" />
                    质量指标
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    {Object.entries(conversionResult.quality_metrics).map(([key, value]) => {
                      if (key === 'overall_score') return null
                            
                            // 处理嵌套对象
                            const formatValue = (val: any): string => {
                              if (typeof val === 'number') {
                                return `${val.toFixed(2)}${key.includes('score') || key.includes('rate') ? '%' : ''}`
                              } else if (typeof val === 'object' && val !== null) {
                                // 如果是对象，显示其主要属性
                                if (val.score !== undefined) return `${val.score.toFixed(2)}%`
                                if (val.rate !== undefined) return `${(val.rate * 100).toFixed(2)}%`
                                if (val.count !== undefined) return `${val.count}`
                                // 对于复杂对象，显示关键信息
                                const entries = Object.entries(val)
                                if (entries.length > 0) {
                                  const [firstKey, firstValue] = entries[0]
                                  if (typeof firstValue === 'number') {
                                    return `${firstValue.toFixed(2)}`
                                  }
                                }
                                return '已计算'
                              } else {
                                return String(val)
                              }
                            }
                            
                            // 格式化键名显示
                            const formatKey = (k: string): string => {
                              const keyMap: { [key: string]: string } = {
                                'character_count': '字符统计',
                                'word_count': '词汇统计', 
                                'compression_ratio': '压缩比例',
                                'content_preservation': '内容保留',
                                'language_quality': '语言质量',
                                'structure_metrics': '结构指标',
                                'rule_application': '规则应用',
                                'conversion_summary': '转换摘要',
                                'processing_stages': '处理阶段'
                              }
                              return keyMap[k] || k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                            }
                            
                      return (
                        <div key={key} className="flex justify-between">
                                <span className="text-muted-foreground">{formatKey(key)}:</span>
                          <span className="font-medium">
                                  {formatValue(value)}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {conversionResult.status === 'completed' && (
                <div className="flex justify-center pt-4">
                  <Button
                    onClick={() => window.open(`/results/${conversionResult.id}`, '_blank')}
                    className="w-full max-w-xs gap-2"
                  >
                    <Eye className="size-4" />
                    查看详细结果和对比
                  </Button>
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

export default function TranscriptionConverterDemo() {
  return <TranscriptionConverter />
}
