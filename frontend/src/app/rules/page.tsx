'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { 
  ChevronDown, 
  ChevronRight, 
  Save, 
  HelpCircle, 
  TestTube, 
  Play,
  Settings,
  Plus,
  Upload,
  FileText,
  Sparkles
} from 'lucide-react'
import Sidebar from '@/components/Sidebar'

// 重新设计的数据结构
interface RuleCategory {
  id: string
  name: string
  description: string
  icon: string
  expanded: boolean
  primaryRules: PrimaryRule[]
}

interface PrimaryRule {
  id: string
  name: string
  description: string
  expanded: boolean
  enabled?: boolean  // 如果没有二级规则，开关在这里
  secondaryRules?: SecondaryRule[]  // 可选的二级规则
  example?: {
    before: string
    after: string
  }
}

interface SecondaryRule {
  id: string
  name: string
  description: string
  enabled: boolean  // 如果有二级规则，开关在这里
  type: 'llm' | 'rule'
  example?: {
    before: string
    after: string
  }
}

interface RuleSet {
  id: string
  name: string
  description: string
  isDefault: boolean
  categories: RuleCategory[]
  createdAt: string
}

function RulesPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [selectedRuleSetId, setSelectedRuleSetId] = useState<string>('default')
  const [testText, setTestText] = useState('')
  const [testResult, setTestResult] = useState('')
  const [isTestLoading, setIsTestLoading] = useState(false)
  const [isTestDialogOpen, setIsTestDialogOpen] = useState(false)
  const [currentTestRule, setCurrentTestRule] = useState<{categoryId: string, primaryRuleId: string, secondaryRuleId?: string} | null>(null)
  const [isSaveDialogOpen, setIsSaveDialogOpen] = useState(false)
  const [newRuleSetName, setNewRuleSetName] = useState('')
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  
  // 新增状态
  const [isCreateRuleDialogOpen, setIsCreateRuleDialogOpen] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [ruleCreationStep, setRuleCreationStep] = useState<'upload' | 'confirm' | 'generating'>('upload')
  const [identifiedRules, setIdentifiedRules] = useState<any[]>([])
  const [newRuleSetNameForCreation, setNewRuleSetNameForCreation] = useState('')

  // 模拟规则集数据
  const [ruleSets, setRuleSets] = useState<RuleSet[]>([
    {
      id: 'default',
      name: '通用规则集',
      description: '适用于大多数笔录转换场景的标准规则',
      isDefault: true,
      createdAt: '2024-01-01',
      categories: [
        {
          id: 'language_processing',
          name: '语言处理',
          description: '处理语言风格和表达方式',
          icon: '🗣️',
          expanded: true,
          primaryRules: [
            {
              id: 'tone_adjustment',
              name: '语气调整',
              description: '调整语气，使其更适合叙述文体',
              expanded: true,
              secondaryRules: [
                {
                  id: 'remove_colloquial',
                  name: '去除口语词',
                  description: '移除"嗯"、"啊"等口语化表达',
                  enabled: true,
                  type: 'rule',
                  example: {
                    before: '嗯，我觉得这个项目还是挺好的。',
                    after: '我觉得这个项目还是挺好的。'
                  }
                },
                {
                  id: 'unify_tone',
                  name: '语调统一',
                  description: '统一语调风格，保持一致性',
                  enabled: true,
                  type: 'llm',
                  example: {
                    before: '我觉得这个想法不错，应该可以试试。',
                    after: '我认为这个想法很好，值得尝试。'
                  }
                }
              ]
            },
            {
              id: 'perspective_conversion',
              name: '视角转换',
              description: '将对话转换为第一人称叙述',
              expanded: false,
              secondaryRules: [
                {
                  id: 'first_person_conversion',
                  name: '第一人称转换',
                  description: '将"他说"转换为"我说"的形式',
                  enabled: true,
                  type: 'llm',
                  example: {
                    before: '问：你的工作是什么？答：我是工程师。',
                    after: '我是工程师。'
                  }
                },
                {
                  id: 'remove_interviewer',
                  name: '去除访谈者发言',
                  description: '移除访谈者的问题和引导语',
                  enabled: true,
                  type: 'rule',
                  example: {
                    before: '访谈者：请介绍一下自己。被访者：我叫张三。',
                    after: '我叫张三。'
                  }
                }
              ]
            },
            {
              id: 'grammar_correction',
              name: '语法纠正',
              description: '自动纠正语法错误和不规范表达',
              expanded: false,
              enabled: true,
              example: {
                before: '我们公司的产品做的很好。',
                after: '我们公司的产品做得很好。'
              }
            }
          ]
        },
        {
          id: 'content_organization',
          name: '内容整理',
          description: '整理和优化内容结构',
          icon: '📝',
          expanded: false,
          primaryRules: [
            {
              id: 'paragraph_merge',
              name: '段落合并',
              description: '合并相关内容，形成连贯段落',
              expanded: false,
              secondaryRules: [
                {
                  id: 'topic_grouping',
                  name: '主题分组',
                  description: '按主题将相关内容分组',
                  enabled: true,
                  type: 'llm',
                  example: {
                    before: '我喜欢编程。我也喜欢设计。编程很有趣。设计很创新。',
                    after: '我喜欢编程，编程很有趣。我也喜欢设计，设计很创新。'
                  }
                },
                {
                  id: 'logical_connection',
                  name: '逻辑连接',
                  description: '添加逻辑连接词，增强连贯性',
                  enabled: true,
                  type: 'llm',
                  example: {
                    before: '我喜欢编程。编程很有趣。我每天都编程。',
                    after: '我喜欢编程，因为编程很有趣，所以我每天都会编程。'
                  }
                }
              ]
            },
            {
              id: 'redundancy_removal',
              name: '冗余去除',
              description: '去除重复和冗余的表达',
              expanded: false,
              enabled: false,
              example: {
                before: '我觉得，我认为这个想法很好，我觉得很不错。',
                after: '我认为这个想法很好。'
              }
            }
          ]
        },
        {
          id: 'format_optimization',
          name: '格式优化',
          description: '优化文本格式和结构',
          icon: '📋',
          expanded: false,
          primaryRules: [
            {
              id: 'punctuation_standardization',
              name: '标点规范化',
              description: '统一标点符号使用规范',
              expanded: false,
              enabled: true,
              example: {
                before: '这是一个例子,很好的例子。',
                after: '这是一个例子，很好的例子。'
              }
            },
            {
              id: 'paragraph_formatting',
              name: '段落格式化',
              description: '优化段落结构和换行',
              expanded: false,
              enabled: true,
              example: {
                before: '第一点内容第二点内容第三点内容',
                after: '第一点内容\n\n第二点内容\n\n第三点内容'
              }
            }
          ]
        }
      ]
    }
  ])

  const currentRuleSet = ruleSets.find(rs => rs.id === selectedRuleSetId)

  // 从URL参数初始化规则集
  useEffect(() => {
    const setParam = searchParams.get('set')
    if (setParam) {
      setSelectedRuleSetId(setParam)
    }
  }, [searchParams])

  // 切换分类展开状态
  const toggleCategoryExpanded = (categoryId: string) => {
    setRuleSets(prev => prev.map(ruleSet => {
      if (ruleSet.id !== selectedRuleSetId) return ruleSet
      
      return {
        ...ruleSet,
        categories: ruleSet.categories.map(category => 
          category.id === categoryId 
            ? { ...category, expanded: !category.expanded }
            : category
        )
      }
    }))
  }

  // 切换一级规则展开状态
  const togglePrimaryRuleExpanded = (categoryId: string, primaryRuleId: string) => {
    setRuleSets(prev => prev.map(ruleSet => {
      if (ruleSet.id !== selectedRuleSetId) return ruleSet
      
      return {
        ...ruleSet,
        categories: ruleSet.categories.map(category => {
          if (category.id !== categoryId) return category
          
          return {
            ...category,
            primaryRules: category.primaryRules.map(primaryRule => 
              primaryRule.id === primaryRuleId 
                ? { ...primaryRule, expanded: !primaryRule.expanded }
                : primaryRule
            )
          }
        })
      }
    }))
  }

  // 切换规则开关
  const toggleRule = (categoryId: string, primaryRuleId: string, secondaryRuleId?: string) => {
    setHasUnsavedChanges(true)
    setRuleSets(prev => prev.map(ruleSet => {
      if (ruleSet.id !== selectedRuleSetId) return ruleSet
      
      return {
        ...ruleSet,
        categories: ruleSet.categories.map(category => {
          if (category.id !== categoryId) return category
          
          return {
            ...category,
            primaryRules: category.primaryRules.map(primaryRule => {
              if (primaryRule.id !== primaryRuleId) return primaryRule
              
              if (secondaryRuleId) {
                // 切换二级规则
                return {
                  ...primaryRule,
                  secondaryRules: primaryRule.secondaryRules?.map(secondaryRule => 
                    secondaryRule.id === secondaryRuleId 
                      ? { ...secondaryRule, enabled: !secondaryRule.enabled }
                      : secondaryRule
                  )
                }
              } else {
                // 切换一级规则（没有二级规则的情况）
                return {
                  ...primaryRule,
                  enabled: !primaryRule.enabled
                }
              }
            })
          }
        })
      }
    }))
  }

  // 测试规则功能
  const handleTestRule = async () => {
    if (!testText.trim() || !currentTestRule) return
    
    setIsTestLoading(true)
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // 根据规则类型模拟不同的处理结果
      let processedText = testText
      if (currentTestRule.secondaryRuleId === 'remove_colloquial') {
        processedText = testText.replace(/嗯|啊|那个/g, '')
      } else if (currentTestRule.primaryRuleId === 'grammar_correction') {
        processedText = testText.replace(/做的/g, '做得')
      }
      
      setTestResult(`经过规则处理后的文本：\n\n${processedText}`)
    } catch (error) {
      setTestResult('测试失败，请重试')
    } finally {
      setIsTestLoading(false)
    }
  }

  // 打开测试对话框
  const openTestDialog = (categoryId: string, primaryRuleId: string, secondaryRuleId?: string) => {
    setCurrentTestRule({ categoryId, primaryRuleId, secondaryRuleId })
    setTestText('')
    setTestResult('')
    setIsTestDialogOpen(true)
  }

  // 保存规则集
  const handleSaveRuleSet = () => {
    if (!newRuleSetName.trim()) return
    
    const newRuleSet: RuleSet = {
      id: `custom_${Date.now()}`,
      name: newRuleSetName,
      description: `基于${currentRuleSet?.name}的自定义规则集`,
      isDefault: false,
      createdAt: new Date().toISOString(),
      categories: currentRuleSet?.categories || []
    }
    
    setRuleSets(prev => [...prev, newRuleSet])
    setSelectedRuleSetId(newRuleSet.id)
    setHasUnsavedChanges(false)
    setIsSaveDialogOpen(false)
    setNewRuleSetName('')
  }

  // 新增：处理文件上传
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    setUploadedFiles(files)
  }

  // 新增：分析上传的文件并识别规则
  const analyzeFilesAndCreateRules = async () => {
    if (uploadedFiles.length === 0 || !newRuleSetNameForCreation.trim()) return
    
    setRuleCreationStep('generating')
    
    try {
      // 模拟文件分析和规则识别过程
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      // 模拟识别出的规则结构
      const mockIdentifiedRules = [
        {
          categoryId: 'language_processing',
          categoryName: '语言处理',
          primaryRules: [
            {
              id: 'custom_tone_adjustment',
              name: '自定义语气调整',
              description: '基于上传文件识别的语气调整规则',
              secondaryRules: [
                {
                  id: 'remove_specific_words',
                  name: '移除特定词汇',
                  description: '移除文件中识别的特定口语词汇',
                  enabled: true,
                  type: 'rule'
                },
                {
                  id: 'formal_expression',
                  name: '正式表达转换',
                  description: '将口语表达转换为正式书面语',
                  enabled: true,
                  type: 'llm'
                }
              ]
            }
          ]
        },
        {
          categoryId: 'content_structure',
          categoryName: '内容结构',
          primaryRules: [
            {
              id: 'custom_paragraph_organization',
              name: '自定义段落组织',
              description: '基于文件特征的段落组织规则',
              enabled: true
            }
          ]
        }
      ]
      
      setIdentifiedRules(mockIdentifiedRules)
      setRuleCreationStep('confirm')
    } catch (error) {
      console.error('规则识别失败:', error)
      setRuleCreationStep('upload')
    }
  }

  // 新增：确认创建规则集
  const confirmCreateRuleSet = () => {
    // 这里应该调用后端API创建新的规则集
    console.log('创建新规则集:', newRuleSetNameForCreation, identifiedRules)
    
    // 重置状态
    setIsCreateRuleDialogOpen(false)
    setUploadedFiles([])
    setRuleCreationStep('upload')
    setIdentifiedRules([])
    setNewRuleSetNameForCreation('')
    
    // 显示成功消息（这里可以添加toast通知）
    alert('规则集创建成功！')
  }

  // 渲染二级规则
  const renderSecondaryRule = (categoryId: string, primaryRuleId: string, secondaryRule: SecondaryRule) => (
    <div key={secondaryRule.id} className="ml-8 p-3 border-l-2 border-gray-200 bg-gray-50 rounded-r-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 flex-1">
          <span className="font-medium text-sm">{secondaryRule.name}</span>
          <Badge variant={secondaryRule.type === 'llm' ? 'default' : 'secondary'} className="text-xs">
            {secondaryRule.type === 'llm' ? 'LLM' : '规则'}
          </Badge>
          {secondaryRule.example && (
            <Tooltip>
              <TooltipTrigger>
                <HelpCircle className="w-4 h-4 text-gray-400 hover:text-gray-600" />
              </TooltipTrigger>
              <TooltipContent side="right" className="max-w-sm">
                <div className="space-y-2">
                  <div>
                    <p className="font-medium text-xs">转换前：</p>
                    <p className="text-xs text-red-600">{secondaryRule.example.before}</p>
                  </div>
                  <div>
                    <p className="font-medium text-xs">转换后：</p>
                    <p className="text-xs text-green-600">{secondaryRule.example.after}</p>
                  </div>
                </div>
              </TooltipContent>
            </Tooltip>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-6 px-2 text-xs"
            onClick={() => openTestDialog(categoryId, primaryRuleId, secondaryRule.id)}
          >
            <TestTube className="w-3 h-3 mr-1" />
            测试
          </Button>
        </div>
        <Switch 
          checked={secondaryRule.enabled}
          onCheckedChange={() => toggleRule(categoryId, primaryRuleId, secondaryRule.id)}
        />
      </div>
      <p className="text-xs text-gray-600 mt-1">{secondaryRule.description}</p>
    </div>
  )

  // 渲染一级规则
  const renderPrimaryRule = (categoryId: string, primaryRule: PrimaryRule) => (
    <div key={primaryRule.id} className="ml-6 border-l-2 border-blue-200">
      <div className="p-3 bg-blue-50 rounded-r-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 flex-1">
            {primaryRule.secondaryRules && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
                onClick={() => togglePrimaryRuleExpanded(categoryId, primaryRule.id)}
              >
                {primaryRule.expanded ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
              </Button>
            )}
            <span className="font-medium">{primaryRule.name}</span>
            {primaryRule.example && (
              <Tooltip>
                <TooltipTrigger>
                  <HelpCircle className="w-4 h-4 text-gray-400 hover:text-gray-600" />
                </TooltipTrigger>
                <TooltipContent side="right" className="max-w-sm">
                  <div className="space-y-2">
                    <div>
                      <p className="font-medium text-xs">转换前：</p>
                      <p className="text-xs text-red-600">{primaryRule.example.before}</p>
                    </div>
                    <div>
                      <p className="font-medium text-xs">转换后：</p>
                      <p className="text-xs text-green-600">{primaryRule.example.after}</p>
                    </div>
                  </div>
                </TooltipContent>
              </Tooltip>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="h-6 px-2 text-xs"
              onClick={() => openTestDialog(categoryId, primaryRule.id)}
            >
              <TestTube className="w-3 h-3 mr-1" />
              测试
            </Button>
          </div>
          {/* 如果没有二级规则，开关放在这里 */}
          {!primaryRule.secondaryRules && (
            <Switch 
              checked={primaryRule.enabled || false}
              onCheckedChange={() => toggleRule(categoryId, primaryRule.id)}
            />
          )}
        </div>
        <p className="text-sm text-gray-600 mt-1">{primaryRule.description}</p>
      </div>
      
      {/* 二级规则 */}
      {primaryRule.secondaryRules && primaryRule.expanded && (
        <div className="mt-2 space-y-2">
          {primaryRule.secondaryRules.map(secondaryRule => 
            renderSecondaryRule(categoryId, primaryRule.id, secondaryRule)
          )}
        </div>
      )}
    </div>
  )

  return (
    <TooltipProvider>
      <div className="flex h-screen bg-gray-50">
        {/* 侧边栏 */}
        <Sidebar />
        
        {/* 主内容区域 */}
        <div className="flex-1 overflow-hidden ml-14">
          <div className="h-full p-6 overflow-y-auto">
            {/* 顶部区域 */}
            <div className="flex items-center justify-between mb-6 bg-white rounded-lg p-4 shadow-sm">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">规则配置与管理</h1>
                <p className="text-sm text-gray-600">配置转换规则，优化笔录转换效果</p>
              </div>
              
              <div className="flex items-center gap-3">
                {/* 创建新规则按钮 */}
                <Dialog open={isCreateRuleDialogOpen} onOpenChange={setIsCreateRuleDialogOpen}>
                  <DialogTrigger asChild>
                    <Button className="gap-2">
                      <Plus className="h-4 w-4" />
                      创建新规则
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle className="flex items-center gap-2">
                        <Sparkles className="h-5 w-5" />
                        智能规则创建
                      </DialogTitle>
                      <DialogDescription>
                        上传训练文件，我们将自动识别并生成适合的转换规则
                      </DialogDescription>
                    </DialogHeader>
                    
                    {ruleCreationStep === 'upload' && (
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium text-gray-700 mb-2 block">
                            规则集名称
                          </label>
                          <Input
                            value={newRuleSetNameForCreation}
                            onChange={(e) => setNewRuleSetNameForCreation(e.target.value)}
                            placeholder="请输入新规则集的名称..."
                          />
                        </div>
                        
                        <div>
                          <label className="text-sm font-medium text-gray-700 mb-2 block">
                            上传训练文件
                          </label>
                          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                            <div className="space-y-2">
                              <p className="text-sm text-gray-600">
                                拖拽文件到这里，或点击选择文件
                              </p>
                              <p className="text-xs text-gray-500">
                                支持 .txt, .docx, .csv 格式，最大 10MB
                              </p>
                            </div>
                            <input
                              type="file"
                              multiple
                              accept=".txt,.docx,.csv"
                              onChange={handleFileUpload}
                              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            />
                          </div>
                          
                          {uploadedFiles.length > 0 && (
                            <div className="mt-3 space-y-2">
                              <p className="text-sm font-medium text-gray-700">已选择文件：</p>
                              {uploadedFiles.map((file, index) => (
                                <div key={index} className="flex items-center gap-2 text-sm text-gray-600">
                                  <FileText className="h-4 w-4" />
                                  {file.name} ({(file.size / 1024).toFixed(1)} KB)
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                        
                        <Button 
                          onClick={analyzeFilesAndCreateRules}
                          disabled={uploadedFiles.length === 0 || !newRuleSetNameForCreation.trim()}
                          className="w-full gap-2"
                        >
                          <Sparkles className="h-4 w-4" />
                          开始分析并生成规则
                        </Button>
                      </div>
                    )}
                    
                    {ruleCreationStep === 'generating' && (
                      <div className="text-center py-8">
                        <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
                        <h3 className="text-lg font-medium text-gray-900 mb-2">正在分析文件...</h3>
                        <p className="text-sm text-gray-600">
                          我们正在分析您上传的文件，识别转换模式并生成相应的规则
                        </p>
                      </div>
                    )}
                    
                    {ruleCreationStep === 'confirm' && (
                      <div className="space-y-4">
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                          <h3 className="text-lg font-medium text-green-900 mb-2">
                            规则识别完成！
                          </h3>
                          <p className="text-sm text-green-700">
                            基于您上传的 {uploadedFiles.length} 个文件，我们识别出了以下规则：
                          </p>
                        </div>
                        
                        <div className="space-y-3 max-h-60 overflow-y-auto">
                          {identifiedRules.map((category, categoryIndex) => (
                            <div key={categoryIndex} className="border rounded-lg p-3">
                              <h4 className="font-medium text-gray-900 mb-2">
                                {category.categoryName}
                              </h4>
                              {category.primaryRules.map((rule: any, ruleIndex: number) => (
                                <div key={ruleIndex} className="ml-4 mb-2">
                                  <div className="flex items-center gap-2">
                                    <span className="text-sm font-medium">{rule.name}</span>
                                    <Badge variant="secondary" className="text-xs">
                                      {rule.secondaryRules ? `${rule.secondaryRules.length} 个子规则` : '单一规则'}
                                    </Badge>
                                  </div>
                                  <p className="text-xs text-gray-600 mt-1">{rule.description}</p>
                                </div>
                              ))}
                            </div>
                          ))}
                        </div>
                        
                        <div className="flex gap-3">
                          <Button 
                            variant="outline" 
                            onClick={() => setRuleCreationStep('upload')}
                            className="flex-1"
                          >
                            重新上传
                          </Button>
                          <Button 
                            onClick={confirmCreateRuleSet}
                            className="flex-1 gap-2"
                          >
                            <Save className="h-4 w-4" />
                            确认创建规则集
                          </Button>
                        </div>
                      </div>
                    )}
                  </DialogContent>
                </Dialog>

                {/* 当前规则集选择 */}
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">当前规则集：</span>
                  <Select value={selectedRuleSetId} onValueChange={setSelectedRuleSetId}>
                    <SelectTrigger className="w-48">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ruleSets.map(ruleSet => (
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

                {/* 保存规则更改按钮 */}
                {hasUnsavedChanges && (
                  <Dialog open={isSaveDialogOpen} onOpenChange={setIsSaveDialogOpen}>
                    <DialogTrigger asChild>
                      <Button variant="default" className="gap-2">
                        <Save className="h-4 w-4" />
                        保存更改
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>保存规则更改</DialogTitle>
                        <DialogDescription>
                          将当前的规则配置保存为新的规则集
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium text-gray-700 mb-2 block">
                            规则集名称
                          </label>
                          <Input
                            value={newRuleSetName}
                            onChange={(e) => setNewRuleSetName(e.target.value)}
                            placeholder="请输入规则集名称..."
                          />
                        </div>
                        <div className="flex gap-3">
                          <Button 
                            variant="outline" 
                            onClick={() => setIsSaveDialogOpen(false)}
                            className="flex-1"
                          >
                            取消
                          </Button>
                          <Button 
                            onClick={handleSaveRuleSet}
                            disabled={!newRuleSetName.trim()}
                            className="flex-1 gap-2"
                          >
                            <Save className="h-4 w-4" />
                            保存规则集
                          </Button>
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>
                )}
              </div>
            </div>

            {/* 规则树形结构 */}
            <Card>
              <CardHeader>
                <CardTitle>规则配置</CardTitle>
                <CardDescription>
                  点击展开/折叠规则分类和具体规则，使用开关控制规则启用状态
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {currentRuleSet?.categories.map(category => (
                  <div key={category.id} className="border rounded-lg p-4">
                    {/* 分类标题 */}
                    <div 
                      className="flex items-center gap-3 cursor-pointer hover:bg-gray-50 p-2 rounded-lg transition-colors"
                      onClick={() => toggleCategoryExpanded(category.id)}
                    >
                      <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                        {category.expanded ? (
                          <ChevronDown className="w-4 h-4" />
                        ) : (
                          <ChevronRight className="w-4 h-4" />
                        )}
                      </Button>
                      <span className="text-lg">{category.icon}</span>
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">{category.name}</h3>
                        <p className="text-sm text-gray-600">{category.description}</p>
                      </div>
                    </div>
                    
                    {/* 一级规则 */}
                    {category.expanded && (
                      <div className="mt-4 space-y-3">
                        {category.primaryRules.map(primaryRule => 
                          renderPrimaryRule(category.id, primaryRule)
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* 测试对话框 */}
            <Dialog open={isTestDialogOpen} onOpenChange={setIsTestDialogOpen}>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>规则测试</DialogTitle>
                  <DialogDescription>
                    输入测试文本，查看当前规则的转换效果
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">测试文本</label>
                    <Textarea
                      value={testText}
                      onChange={(e) => setTestText(e.target.value)}
                      placeholder="请输入要测试的文本..."
                      className="min-h-[100px]"
                    />
                  </div>
                  
                  <Button 
                    onClick={handleTestRule} 
                    disabled={!testText.trim() || isTestLoading}
                    className="w-full gap-2"
                  >
                    {isTestLoading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        测试中...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        测试规则
                      </>
                    )}
                  </Button>

                  {testResult && (
                    <div>
                      <label className="text-sm font-medium text-gray-700 mb-2 block">测试结果</label>
                      <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm whitespace-pre-wrap">
                        {testResult}
                      </div>
                    </div>
                  )}
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>
    </div>
    </TooltipProvider>
  )
}

// 创建加载组件
function RulesPageLoading() {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
        <p className="text-gray-600">加载规则配置...</p>
      </div>
    </div>
  )
}

// 默认导出使用 Suspense 包装
export default function RulesPage() {
  return (
    <Suspense fallback={<RulesPageLoading />}>
      <RulesPageContent />
    </Suspense>
  )
} 