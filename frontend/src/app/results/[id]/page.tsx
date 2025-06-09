'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { Progress } from "@/components/ui/progress"
import { ArrowLeft, Download, Share2, BarChart3, FileText, Clock, User, Eye, TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface TranscriptionRecord {
  id: number
  title: string
  original_text: string
  converted_text: string
  status: string
  quality_metrics: any
  processing_time: number
  created_at: string
  completed_at: string
  file_name?: string
}

interface QualityMetrics {
  overall_score: number
  quality_report: {
    grade: string
    grade_color: string
    score: number
    suggestions: string[]
    summary: string
  }
  basic_metrics: any
  content_preservation: any
  language_quality: any
  structure_metrics: any
}

// 差异类型枚举
enum DiffType {
  UNCHANGED = 'unchanged',
  ADDED = 'added',
  REMOVED = 'removed',
  MODIFIED = 'modified'
}

interface DiffSegment {
  type: DiffType
  text: string
  originalIndex?: number
  convertedIndex?: number
}

export default function ResultsPage() {
  const params = useParams()
  const router = useRouter()
  const [record, setRecord] = useState<TranscriptionRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showDiff, setShowDiff] = useState(true)
  
  // 同步滚动的refs
  const originalScrollRef = useRef<HTMLDivElement>(null)
  const convertedScrollRef = useRef<HTMLDivElement>(null)
  const isScrolling = useRef(false)

  useEffect(() => {
    const fetchRecord = async () => {
      try {
        const response = await fetch(`/api/v1/transcription/${params.id}`)
        if (response.ok) {
          const data = await response.json()
          setRecord(data)
        } else {
          setError('转换记录未找到')
        }
      } catch (err) {
        setError('加载转换记录失败')
      } finally {
        setLoading(false)
      }
    }

    if (params.id) {
      fetchRecord()
    }
  }, [params.id])

  // 同步滚动处理
  const handleScroll = (source: 'original' | 'converted') => (e: React.UIEvent<HTMLDivElement>) => {
    if (isScrolling.current) return
    
    isScrolling.current = true
    const sourceElement = e.currentTarget
    const targetElement = source === 'original' ? convertedScrollRef.current : originalScrollRef.current
    
    if (targetElement) {
      const scrollPercentage = sourceElement.scrollTop / (sourceElement.scrollHeight - sourceElement.clientHeight)
      targetElement.scrollTop = scrollPercentage * (targetElement.scrollHeight - targetElement.clientHeight)
    }
    
    setTimeout(() => {
      isScrolling.current = false
    }, 50)
  }

  // 简单的文本差异分析
  const analyzeDifferences = (original: string, converted: string): DiffSegment[] => {
    const originalSentences = original.split(/[。！？\n]/).filter(s => s.trim())
    const convertedSentences = converted.split(/[。！？\n]/).filter(s => s.trim())
    
    const segments: DiffSegment[] = []
    
    // 简化的差异分析 - 实际项目中可以使用更复杂的diff算法
    const maxLength = Math.max(originalSentences.length, convertedSentences.length)
    
    for (let i = 0; i < maxLength; i++) {
      const originalSent = originalSentences[i]
      const convertedSent = convertedSentences[i]
      
      if (originalSent && convertedSent) {
        if (originalSent.trim() === convertedSent.trim()) {
          segments.push({ type: DiffType.UNCHANGED, text: originalSent })
        } else {
          segments.push({ type: DiffType.MODIFIED, text: convertedSent, originalIndex: i })
        }
      } else if (originalSent && !convertedSent) {
        segments.push({ type: DiffType.REMOVED, text: originalSent })
      } else if (!originalSent && convertedSent) {
        segments.push({ type: DiffType.ADDED, text: convertedSent })
      }
    }
    
    return segments
  }

  // 计算定量指标
  const calculateMetrics = (original: string, converted: string) => {
    const originalLength = original.length
    const convertedLength = converted.length
    const retentionRate = (convertedLength / originalLength) * 100
    
    // 简单的相似度计算
    const originalWords = original.split(/\s+/)
    const convertedWords = converted.split(/\s+/)
    const commonWords = originalWords.filter(word => convertedWords.includes(word))
    const preservationRate = (commonWords.length / originalWords.length) * 100
    
    return {
      retentionRate,
      preservationRate,
      originalLength,
      convertedLength,
      originalWords: originalWords.length,
      convertedWords: convertedWords.length
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'bg-green-100 text-green-800'
      case 'PROCESSING': return 'bg-blue-100 text-blue-800'
      case 'FAILED': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getMetricColor = (value: number, type: 'retention' | 'preservation') => {
    if (type === 'retention') {
      if (value >= 60 && value <= 80) return 'text-green-600'
      if ((value >= 50 && value < 60) || (value > 80 && value <= 90)) return 'text-yellow-600'
      return 'text-red-600'
    } else {
      if (value > 75) return 'text-green-600'
      if (value >= 60) return 'text-yellow-600'
      return 'text-red-600'
    }
  }

  const downloadResult = () => {
    if (!record) return
    
    const content = `转换结果报告\n\n原始文本：\n${record.original_text}\n\n转换结果：\n${record.converted_text}\n\n质量评分：${record.quality_metrics?.overall_score || 0}分`
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `转换结果_${record.id}_${new Date().toISOString().split('T')[0]}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载转换结果中...</p>
        </div>
      </div>
    )
  }

  if (error || !record) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || '转换记录未找到'}</p>
          <Button onClick={() => router.push('/')} variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            返回首页
          </Button>
        </div>
      </div>
    )
  }

  const qualityMetrics = record.quality_metrics as QualityMetrics || {}
  const metrics = calculateMetrics(record.original_text, record.converted_text)
  const diffSegments = analyzeDifferences(record.original_text, record.converted_text)

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* 头部 */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <Button 
              onClick={() => router.push('/history')} 
              variant="outline" 
              size="sm"
              className="mr-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              返回历史
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {record.title || `转换结果 #${record.id}`}
              </h1>
              <p className="text-gray-600">
                {record.file_name || '文本输入'} • 创建于 {new Date(record.created_at).toLocaleString()}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button 
              onClick={() => setShowDiff(!showDiff)} 
              variant={showDiff ? "default" : "outline"} 
              size="sm"
            >
              <Eye className="w-4 h-4 mr-2" />
              {showDiff ? '隐藏差异' : '显示差异'}
            </Button>
            <Button onClick={downloadResult} variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              下载结果
            </Button>
          </div>
        </div>

        {/* 定量指标卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">字数保留率</p>
                  <p className={`text-2xl font-bold ${getMetricColor(metrics.retentionRate, 'retention')}`}>
                    {metrics.retentionRate.toFixed(1)}%
                  </p>
                  <p className="text-xs text-gray-500">
                    {metrics.convertedLength} / {metrics.originalLength} 字符
                  </p>
                </div>
                <div className="text-right">
                  {metrics.retentionRate >= 60 && metrics.retentionRate <= 80 ? (
                    <TrendingUp className="w-6 h-6 text-green-600" />
                  ) : (
                    <TrendingDown className="w-6 h-6 text-red-600" />
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">内容保持率</p>
                  <p className={`text-2xl font-bold ${getMetricColor(metrics.preservationRate, 'preservation')}`}>
                    {metrics.preservationRate.toFixed(1)}%
                  </p>
                  <p className="text-xs text-gray-500">
                    词汇相似度分析
                  </p>
                </div>
                <div className="text-right">
                  {metrics.preservationRate > 75 ? (
                    <TrendingUp className="w-6 h-6 text-green-600" />
                  ) : (
                    <TrendingDown className="w-6 h-6 text-red-600" />
                    )}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">处理时间</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {record.processing_time?.toFixed(2) || 0}s
                  </p>
                  <p className="text-xs text-gray-500">
                    转换耗时
                  </p>
                </div>
                <Clock className="w-6 h-6 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">质量评分</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {qualityMetrics.overall_score || 0}分
                  </p>
                  <p className="text-xs text-gray-500">
                    综合评估
                  </p>
                </div>
                <BarChart3 className="w-6 h-6 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 左右对比视图 */}
              <Card>
                <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              转换对比分析
            </CardTitle>
                  <CardDescription>
              左侧为原始笔录，右侧为转换结果。{showDiff && '差异部分已高亮显示：🟢新增 🔴删除 🟡修改 ⚪未变化'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* 原始笔录 */}
              <div className="space-y-2">
                <h3 className="text-lg font-medium text-gray-900">原始笔录</h3>
                <div 
                  ref={originalScrollRef}
                  onScroll={handleScroll('original')}
                  className="h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 bg-gray-50"
                >
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {showDiff ? (
                      diffSegments.map((segment, index) => (
                        <span
                          key={index}
                          className={
                            segment.type === DiffType.REMOVED ? 'bg-red-100 text-red-800 line-through' :
                            segment.type === DiffType.MODIFIED ? 'bg-yellow-100 text-yellow-800' :
                            segment.type === DiffType.UNCHANGED ? 'bg-white' :
                            'hidden'
                          }
                        >
                          {segment.text}
                        </span>
                      ))
                    ) : (
                      record.original_text
                    )}
                  </div>
                  </div>
                <div className="text-xs text-gray-500">
                  {metrics.originalLength} 字符 • {metrics.originalWords} 词
            </div>
                      </div>

              {/* 转换结果 */}
              <div className="space-y-2">
                <h3 className="text-lg font-medium text-gray-900">转换结果</h3>
                <div 
                  ref={convertedScrollRef}
                  onScroll={handleScroll('converted')}
                  className="h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 bg-white"
                >
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {showDiff ? (
                      diffSegments.map((segment, index) => (
                        <span
                          key={index}
                          className={
                            segment.type === DiffType.ADDED ? 'bg-green-100 text-green-800' :
                            segment.type === DiffType.MODIFIED ? 'bg-yellow-100 text-yellow-800' :
                            segment.type === DiffType.UNCHANGED ? 'bg-white' :
                            'hidden'
                          }
                        >
                          {segment.text}
                        </span>
                      ))
                    ) : (
                      record.converted_text
                    )}
                      </div>
                    </div>
                <div className="text-xs text-gray-500">
                  {metrics.convertedLength} 字符 • {metrics.convertedWords} 词
                      </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

        {/* 详细质量分析 */}
        {qualityMetrics.quality_report && (
          <Card className="mt-6">
              <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                详细质量分析
              </CardTitle>
              </CardHeader>
              <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <Badge className={`${qualityMetrics.quality_report.grade_color === 'green' ? 'bg-green-100 text-green-800' : 
                                     qualityMetrics.quality_report.grade_color === 'yellow' ? 'bg-yellow-100 text-yellow-800' : 
                                     'bg-red-100 text-red-800'}`}>
                    {qualityMetrics.quality_report.grade}
                  </Badge>
                  <Progress value={qualityMetrics.overall_score} className="flex-1" />
                  <span className="text-sm font-medium">{qualityMetrics.overall_score}分</span>
                    </div>
                
                {qualityMetrics.quality_report.summary && (
                  <p className="text-gray-700">{qualityMetrics.quality_report.summary}</p>
                )}
                
                {qualityMetrics.quality_report.suggestions && qualityMetrics.quality_report.suggestions.length > 0 && (
                    <div>
                    <h4 className="font-medium mb-2">改进建议：</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                      {qualityMetrics.quality_report.suggestions.map((suggestion: string, index: number) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
                </div>
              </CardContent>
            </Card>
        )}
      </div>
    </div>
  )
} 