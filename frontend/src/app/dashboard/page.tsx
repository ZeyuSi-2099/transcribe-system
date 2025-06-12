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
import { Pagination, PaginationContent, PaginationEllipsis, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination"
import { ArrowUp, Square, Wand2, Upload, FileText, Eye, BarChart3, Settings, Sliders, Download, ChevronLeft, ChevronRight, TrendingUp, FileCheck, Target, MoreHorizontal } from "lucide-react"
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

interface ParagraphPair {
  original: string
  converted: string
  index: number
}

interface KeyMetric {
  name: string
  value: string
  definition: string
  variables: { [key: string]: string | number }
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
  const [currentParagraphIndex, setCurrentParagraphIndex] = useState(0)
  const [paragraphs, setParagraphs] = useState<ParagraphPair[]>([])
  
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

  // 段落拆分函数
  const splitIntoParagraphs = (originalText: string, convertedText: string): ParagraphPair[] => {
    // 更智能的段落拆分：将连续的对话轮次合并为更大的段落
    const originalLines = originalText.split('\n').filter(line => line.trim().length > 0)
    const convertedSentences = convertedText.split(/[。！？\n]+/).filter(s => s.trim().length > 0)
    
    // 提取原始文本中的对话轮次
    const dialogueTurns: string[] = []
    let currentTurn = ''
    
    for (const line of originalLines) {
      const trimmedLine = line.trim()
      // 检查是否是新的对话轮次（以M:或I:开头）
      if (/^[MI]:\s*/.test(trimmedLine)) {
        if (currentTurn) {
          dialogueTurns.push(currentTurn.trim())
        }
        currentTurn = trimmedLine
      } else if (currentTurn) {
        // 继续当前对话轮次
        currentTurn += '\n' + trimmedLine
      } else {
        // 如果没有对话标识，直接作为一个段落
        dialogueTurns.push(trimmedLine)
      }
    }
    
    // 添加最后一个对话轮次
    if (currentTurn) {
      dialogueTurns.push(currentTurn.trim())
    }
    
    // 将对话轮次合并为更大的段落（每3-4个轮次为一个段落）
    const mergedParagraphs: string[] = []
    const turnsPerParagraph = 4 // 每个段落包含4个对话轮次
    
    if (dialogueTurns.length > 0) {
      for (let i = 0; i < dialogueTurns.length; i += turnsPerParagraph) {
        const paragraphTurns = dialogueTurns.slice(i, i + turnsPerParagraph)
        mergedParagraphs.push(paragraphTurns.join('\n\n'))
      }
    } else {
      // 如果没有找到对话格式，按照句子数量拆分
      const sentences = originalText.split(/[。！？]+/).filter(s => s.trim().length > 0)
      const sentencesPerParagraph = 3
      for (let i = 0; i < sentences.length; i += sentencesPerParagraph) {
        const paragraphSentences = sentences.slice(i, i + sentencesPerParagraph)
        mergedParagraphs.push(paragraphSentences.join('。') + '。')
      }
    }
    
    // 对转换后的文本也进行类似的拆分
    const convertedParagraphs: string[] = []
    const convertedSentencesPerParagraph = Math.max(1, Math.floor(convertedSentences.length / mergedParagraphs.length))
    
    for (let i = 0; i < convertedSentences.length; i += convertedSentencesPerParagraph) {
      const paragraphSentences = convertedSentences.slice(i, i + convertedSentencesPerParagraph)
      convertedParagraphs.push(paragraphSentences.join('。') + '。')
    }
    
    // 创建段落对
    const pairs: ParagraphPair[] = []
    const maxLength = Math.max(mergedParagraphs.length, convertedParagraphs.length)
    
    for (let i = 0; i < maxLength; i++) {
      pairs.push({
        original: mergedParagraphs[i] || '',
        converted: convertedParagraphs[i] || '',
        index: i
      })
    }
    
    return pairs
  }

  // 计算关键指标
  const calculateKeyMetrics = (original: string, converted: string): KeyMetric[] => {
    const originalLength = original.length
    const convertedLength = converted.length

    // 严格保留率计算（简化版本）
    const strictRetentionRate = originalLength > 0 ? ((convertedLength / originalLength) * 100) : 0
    
    // 广义保留率计算（假设去除了一些口语词）
    const oralWordsRemoved = Math.max(0, originalLength - convertedLength)
    const broadRetained = convertedLength + Math.floor(oralWordsRemoved * 0.5) // 假设50%的删除是口语词/语气词
    const broadRetentionRate = originalLength > 0 ? Math.min(100, (broadRetained / originalLength) * 100) : 0

    return [
      {
        name: "文本长度",
        value: `${originalLength} → ${convertedLength}`,
        definition: "衡量文本转换前后的长度变化，反映内容压缩程度",
        variables: {
          "原始笔录字数": originalLength,
          "转换后字数": convertedLength
        }
      },
      {
        name: "文字保留率（严格）",
        value: `${strictRetentionRate.toFixed(1)}%`,
        definition: "保留字数 ÷ 原始笔录字数 × 100%",
        variables: {
          "原始笔录字数": originalLength,
          "被保留的字数（严格一致）": convertedLength
        }
      },
      {
        name: "文字保留率（宽泛）",
        value: `${broadRetentionRate.toFixed(1)}%`,
        definition: "在严格指标基础上，纳入口语词、语气词去除的保留率，但不包含改写",
        variables: {
          "原始笔录字数": originalLength,
          "被保留的字数（允许口语词/语气词去除）": broadRetained
        }
      }
    ]
  }

  // 当转换结果更新时，重新计算段落和指标
  useEffect(() => {
    if (conversionResult && conversionResult.original_text && conversionResult.converted_text) {
      const newParagraphs = splitIntoParagraphs(conversionResult.original_text, conversionResult.converted_text)
      setParagraphs(newParagraphs)
      setCurrentParagraphIndex(0)
    }
  }, [conversionResult])

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

      {/* 优化后的结果分析浮窗 */}
      <Dialog open={showAnalysisModal} onOpenChange={setShowAnalysisModal}>
        <DialogContent 
          className="max-w-none p-4"
          style={{
            width: '95vw',
            height: '90vh',
            maxWidth: 'none',
            maxHeight: 'none'
          }}
        >
          <DialogHeader className="pb-1">
            <DialogTitle className="text-lg text-black">转换结果分析</DialogTitle>
          </DialogHeader>
          
          {conversionResult && (
            <div className="flex flex-col h-full space-y-2 overflow-hidden">
              {/* 上部：关键指标区域 */}
              <div className="flex gap-4">
                {/* 左侧：关键指标标题（竖排） */}
                <div className="flex items-center justify-center w-12">
                  <div className="flex flex-col items-center gap-1">
                    <Target className="h-5 w-5 text-black" />
                    <div className="flex flex-col items-center text-lg font-semibold text-black">
                      <span>关</span>
                      <span>键</span>
                      <span>指</span>
                      <span>标</span>
                    </div>
                  </div>
                </div>
                
                {/* 右侧：三个指标卡片 */}
                <div className="flex-1 grid grid-cols-3 gap-4">
                  {calculateKeyMetrics(conversionResult.original_text, conversionResult.converted_text).map((metric, index) => (
                    <Card key={index} className="border-black hover:shadow-md transition-shadow">
                      <CardHeader className="pb-1 pt-2 px-3">
                        <div className="flex items-center gap-2 mb-1">
                          {index === 0 && <TrendingUp className="h-3 w-3 text-black" />}
                          {index === 1 && <FileCheck className="h-3 w-3 text-black" />}
                          {index === 2 && <Target className="h-3 w-3 text-black" />}
                          <CardTitle className="text-xs text-black">{metric.name}</CardTitle>
                        </div>
                        <div className="text-xs text-gray-600 leading-tight mb-1">
                          {metric.definition}
                        </div>
                        <div className="text-xl font-bold text-black">
                          {metric.value}
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0 pb-2 px-3">
                        <div className="space-y-0.5">
                          {Object.entries(metric.variables).map(([key, value]) => (
                            <div key={key} className="flex justify-between text-xs">
                              <span className="text-gray-600">{key}:</span>
                              <span className="font-medium text-black">{value}</span>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              {/* 分割线 */}
              <div className="border-t border-black"></div>

              {/* 下部：段落分析 */}
              <div className="flex-1 flex gap-4 overflow-hidden min-h-0">
                {/* 左侧：段落分析标题（竖排） */}
                <div className="flex items-center justify-center w-12">
                  <div className="flex flex-col items-center gap-1">
                    <FileText className="h-5 w-5 text-black" />
                    <div className="flex flex-col items-center text-lg font-semibold text-black">
                      <span>段</span>
                      <span>落</span>
                      <span>分</span>
                      <span>析</span>
                    </div>
                  </div>
                </div>

                {/* 右侧：段落内容区域 */}
                <div className="flex-1 flex flex-col space-y-3 overflow-hidden min-h-0">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-black">
                      第 {currentParagraphIndex + 1} 段 / 共 {paragraphs.length} 段
                    </div>
                  </div>

                  {paragraphs.length > 0 && (
                    <>
                      {/* 段落内容显示 - 使用dashboard页面的文字区域样式 */}
                      <div className="flex-1 grid grid-cols-2 gap-4 overflow-hidden min-h-0">
                        <Card className="flex flex-col">
                          <CardHeader className="pb-1 pt-2">
                            <CardTitle className="text-sm text-black">原始段落</CardTitle>
                          </CardHeader>
                          <CardContent className="flex-1 pb-2">
                            <div className="relative border border-input bg-background rounded-lg focus-within:ring-1 focus-within:ring-ring h-full">
                              <Textarea
                                value={paragraphs[currentParagraphIndex]?.original || '无内容'}
                                readOnly
                                placeholder="无内容"
                                className="h-full min-h-[calc(100%-2px)] resize-none border-0 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 text-sm text-black"
                              />
                            </div>
                          </CardContent>
                        </Card>

                        <Card className="flex flex-col">
                          <CardHeader className="pb-1 pt-2">
                            <CardTitle className="text-sm text-black">转换后段落</CardTitle>
                          </CardHeader>
                          <CardContent className="flex-1 pb-2">
                            <div className="relative border border-input bg-background rounded-lg focus-within:ring-1 focus-within:ring-ring h-full">
                              <Textarea
                                value={paragraphs[currentParagraphIndex]?.converted || '无内容'}
                                readOnly
                                placeholder="无内容"
                                className="h-full min-h-[calc(100%-2px)] resize-none border-0 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 text-sm text-black"
                              />
                            </div>
                          </CardContent>
                        </Card>
                      </div>

                      {/* 段落导航 - 使用21st-dev分页组件，增加底部内边距 */}
                      <div className="pt-4 pb-6">
                        <Pagination>
                          <PaginationContent>
                            <PaginationItem>
                              <PaginationPrevious 
                                href="#"
                                onClick={(e) => {
                                  e.preventDefault()
                                  if (currentParagraphIndex > 0) {
                                    setCurrentParagraphIndex(currentParagraphIndex - 1)
                                  }
                                }}
                                className={cn(
                                  "border-black text-black hover:bg-gray-100",
                                  currentParagraphIndex === 0 && "opacity-50 cursor-not-allowed"
                                )}
                              />
                            </PaginationItem>
                            
                            {/* 显示当前页和相邻页 - 修改为显示5个按钮 */}
                            {(() => {
                              const totalPages = paragraphs.length
                              const current = currentParagraphIndex
                              const pages = []
                              
                              if (totalPages <= 7) {
                                // 如果总页数小于等于7，显示所有页码
                                for (let i = 0; i < totalPages; i++) {
                                  pages.push(
                                    <PaginationItem key={i}>
                                      <PaginationLink
                                        href="#"
                                        onClick={(e) => {
                                          e.preventDefault()
                                          setCurrentParagraphIndex(i)
                                        }}
                                        isActive={current === i}
                                        className={cn(
                                          "border-black text-black hover:bg-gray-100",
                                          current === i && "bg-black text-white"
                                        )}
                                      >
                                        {i + 1}
                                      </PaginationLink>
                                    </PaginationItem>
                                  )
                                }
                              } else {
                                // 总页数大于7时，使用省略号逻辑
                                // 总是显示第一页
                                pages.push(
                                  <PaginationItem key={0}>
                                    <PaginationLink
                                      href="#"
                                      onClick={(e) => {
                                        e.preventDefault()
                                        setCurrentParagraphIndex(0)
                                      }}
                                      isActive={current === 0}
                                      className={cn(
                                        "border-black text-black hover:bg-gray-100",
                                        current === 0 && "bg-black text-white"
                                      )}
                                    >
                                      1
                                    </PaginationLink>
                                  </PaginationItem>
                                )
                                
                                // 如果当前页离第一页很远，显示省略号
                                if (current > 3) {
                                  pages.push(
                                    <PaginationItem key="ellipsis1">
                                      <PaginationEllipsis />
                                    </PaginationItem>
                                  )
                                }
                                
                                // 显示当前页附近的页码（显示5个按钮）
                                let start = Math.max(1, current - 2)
                                let end = Math.min(totalPages - 2, current + 2)
                                
                                // 确保显示5个按钮
                                if (end - start < 4) {
                                  if (start === 1) {
                                    end = Math.min(totalPages - 2, start + 4)
                                  } else if (end === totalPages - 2) {
                                    start = Math.max(1, end - 4)
                                  }
                                }
                                
                                for (let i = start; i <= end; i++) {
                                  if (i !== 0 && i !== totalPages - 1) {
                                    pages.push(
                                      <PaginationItem key={i}>
                                        <PaginationLink
                                          href="#"
                                          onClick={(e) => {
                                            e.preventDefault()
                                            setCurrentParagraphIndex(i)
                                          }}
                                          isActive={current === i}
                                          className={cn(
                                            "border-black text-black hover:bg-gray-100",
                                            current === i && "bg-black text-white"
                                          )}
                                        >
                                          {i + 1}
                                        </PaginationLink>
                                      </PaginationItem>
                                    )
                                  }
                                }
                                
                                // 如果当前页离最后一页很远，显示省略号
                                if (current < totalPages - 4) {
                                  pages.push(
                                    <PaginationItem key="ellipsis2">
                                      <PaginationEllipsis />
                                    </PaginationItem>
                                  )
                                }
                                
                                // 总是显示最后一页
                                pages.push(
                                  <PaginationItem key={totalPages - 1}>
                                    <PaginationLink
                                      href="#"
                                      onClick={(e) => {
                                        e.preventDefault()
                                        setCurrentParagraphIndex(totalPages - 1)
                                      }}
                                      isActive={current === totalPages - 1}
                                      className={cn(
                                        "border-black text-black hover:bg-gray-100",
                                        current === totalPages - 1 && "bg-black text-white"
                                      )}
                                    >
                                      {totalPages}
                                    </PaginationLink>
                                  </PaginationItem>
                                )
                              }
                              
                              return pages
                            })()}
                            
                            <PaginationItem>
                              <PaginationNext 
                                href="#"
                                onClick={(e) => {
                                  e.preventDefault()
                                  if (currentParagraphIndex < paragraphs.length - 1) {
                                    setCurrentParagraphIndex(currentParagraphIndex + 1)
                                  }
                                }}
                                className={cn(
                                  "border-black text-black hover:bg-gray-100",
                                  currentParagraphIndex === paragraphs.length - 1 && "opacity-50 cursor-not-allowed"
                                )}
                              />
                            </PaginationItem>
                          </PaginationContent>
                        </Pagination>
                      </div>
                    </>
                  )}

                  {paragraphs.length === 0 && (
                    <div className="flex-1 flex items-center justify-center text-black">
                      暂无段落数据
                    </div>
                  )}
                </div>
              </div>
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