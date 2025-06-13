'use client'

import React, { useState, useEffect, Suspense, useMemo } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useRuleSet, RuleSet } from '@/contexts/RuleSetContext'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Plus, 
  Search, 
  Star, 
  Info, 
  Edit, 
  Download, 
  Copy, 
  Trash2, 
  Filter, 
  ArrowUpDown,
  Settings,
  Play,
  TestTube,
  Save,
  HelpCircle,
  FileText,
  Sparkles,
  Check,
  Eye,
  Power,
  PowerOff,
  Package,
  RefreshCw,
  BookOpen,
  ChevronDown
} from 'lucide-react'
import Sidebar from '@/components/Sidebar'

// 规则数据结构
interface Rule {
  id: string
  name: string
  description: string
  category: string
  type: 'llm' | 'regex' | 'custom'
  enabled: boolean
  isOfficial: boolean
  config?: any
  example?: {
    before: string
    after: string
    description: string
  }
  testCases?: TestCase[]
}

interface TestCase {
  id: string
  input: string
  expectedOutput: string
  description: string
}

// 定义规则分类
const ruleCategories = [
  { id: 'all', name: '全部规则', icon: '📋' },
  { id: 'format', name: '格式转换', icon: '🔄' },
  { id: 'content', name: '内容整理', icon: '✂️' },
  { id: 'structure', name: '结构优化', icon: '🏗️' },
  { id: 'language', name: '语言规范', icon: '📝' },
  { id: 'dialogue', name: '对话处理', icon: '💬' },
  { id: 'classification', name: '主题分类', icon: '🏷️' }
]

// 基于训练数据生成的完整转换规则
const trainingBasedRules: Rule[] = [
  // 格式转换类规则
  {
    id: 'remove-dialogue-markers',
    name: '去除对话标识符',
    description: '自动去除"M："、"1："等对话标识符，保留纯净的对话内容',
    type: 'regex',
    category: 'format',
    enabled: true,
    isOfficial: true,
    config: {
      pattern: '^[M1]：',
      replacement: '',
      flags: 'gm'
    },
    example: {
      before: 'M：您好，请问...\n1：我们使用华为...',
      after: '您好，请问...\n我们使用华为...',
      description: '去除对话开头的标识符'
    },
    testCases: [
      { id: '1', input: 'M：您好，请问...', expectedOutput: '您好，请问...', description: '去除M标识符' },
      { id: '2', input: '1：我们使用华为...', expectedOutput: '我们使用华为...', description: '去除1标识符' }
    ]
  },
  {
    id: 'add-topic-labels',
    name: '添加主题分类标签',
    description: '为不同主题的内容添加【】格式的分类标签，如【产品】、【服务】等',
    type: 'llm',
    category: 'format',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '为以下内容添加合适的主题分类标签，使用【】格式，常见分类包括：【整体合作情况】、【产品】、【服务】、【售前支持】、【售后支持】、【未来期望和建议】等'
    },
    example: {
      before: '顾问：您与华为的合作情况是怎样的？\n我们和华为合作得有XX年的时间...',
      after: '【整体合作情况】顾问：您与华为的合作情况是怎样的？\n我们和华为合作得有XX年的时间...',
      description: '为对话内容添加主题分类标签'
    },
    testCases: []
  },
  {
    id: 'convert-m-to-consultant',
    name: '称谓统一转换',
    description: '将对话中的"M"统一转换为"顾问"，保持称谓一致性',
    type: 'regex',
    category: 'format',
    enabled: true,
    isOfficial: true,
    config: {
      pattern: '\\bM\\b',
      replacement: '顾问',
      flags: 'g'
    },
    example: {
      before: 'M说了很多问题',
      after: '顾问说了很多问题',
      description: '将M替换为顾问'
    },
    testCases: []
  },

  // 内容整理类规则
  {
    id: 'remove-duplicate-words',
    name: '去除重复词汇',
    description: '智能识别并去除句子中的重复词汇和冗余表达，保持语言简洁',
    type: 'llm',
    category: 'content',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '去除以下文本中的重复词汇和冗余表达，保持核心意思不变，使语言更加简洁流畅'
    },
    example: {
      before: '我觉得我觉得华为的产品很好很好，质量质量确实不错',
      after: '我觉得华为的产品很好，质量确实不错',
      description: '去除重复的词汇和表达'
    },
    testCases: []
  },
  {
    id: 'remove-filler-words',
    name: '去除口语化表达',
    description: '去除"嗯"、"啊"、"那个"等口语化词汇，提升文本正式度',
    type: 'regex',
    category: 'content',
    enabled: true,
    isOfficial: true,
    config: {
      pattern: '\\b(嗯|啊|呃|那个|这个|就是说|然后呢|对吧|是吧|怎么说呢)\\b',
      replacement: '',
      flags: 'g'
    },
    example: {
      before: '嗯，怎么说呢，华为的产品，怎么说呢，确实不错',
      after: '我觉得华为的产品确实不错',
      description: '去除口语化填充词'
    },
    testCases: []
  },
  {
    id: 'merge-fragmented-sentences',
    name: '合并碎片化句子',
    description: '将意思相关的碎片化句子合并，形成完整连贯的表达',
    type: 'llm',
    category: 'content',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '将以下碎片化的句子合并成完整连贯的表达，保持原意不变'
    },
    example: {
      before: '华为的产品。很好用。我们很满意。',
      after: '华为的产品很好用，我们很满意。',
      description: '合并碎片化的短句'
    },
    testCases: []
  },
  {
    id: 'extract-key-information',
    name: '提取关键信息',
    description: '从冗长的对话中提取关键信息点，去除无关的闲聊内容',
    type: 'llm',
    category: 'content',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '从以下对话中提取关键信息，去除无关的闲聊和重复内容，保留核心观点和事实'
    },
    example: {
      before: '嗯，怎么说呢，华为的产品，我觉得吧，总的来说还是不错的，当然了，也有一些小问题...',
      after: '华为的产品总的来说不错，但也有一些小问题...',
      description: '提取核心信息，去除冗余表达'
    },
    testCases: []
  },

  // 结构优化类规则
  {
    id: 'organize-by-topic',
    name: '按主题重新组织',
    description: '将散乱的对话内容按主题重新组织，形成结构化的叙述',
    type: 'llm',
    category: 'structure',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '将以下对话内容按主题重新组织，常见主题包括：产品体验、服务评价、价格感受、技术支持、未来期望等'
    },
    example: {
      before: '华为产品不错，价格有点贵，服务很好，技术支持及时...',
      after: '【产品体验】华为产品不错\n【价格感受】价格有点贵\n【服务评价】服务很好，技术支持及时',
      description: '按主题重新组织内容'
    },
    testCases: []
  },
  {
    id: 'create-logical-flow',
    name: '创建逻辑流程',
    description: '为内容创建清晰的逻辑流程，使叙述更加条理化',
    type: 'llm',
    category: 'structure',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '为以下内容创建清晰的逻辑流程，使用"首先"、"其次"、"最后"等连接词'
    },
    example: {
      before: '华为产品好用，价格贵，服务不错',
      after: '首先，华为产品好用；其次，价格相对较贵；最后，服务质量不错',
      description: '创建逻辑清晰的表达流程'
    },
    testCases: []
  },
  {
    id: 'add-paragraph-structure',
    name: '添加段落结构',
    description: '为长文本添加合理的段落分割，提升可读性',
    type: 'llm',
    category: 'structure',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '为以下长文本添加合理的段落分割，每个段落围绕一个主要观点'
    },
    example: {
      before: '华为产品很好用我们用了很多年服务也不错价格有点贵但是质量确实好...',
      after: '华为产品很好用，我们用了很多年。\n\n服务也不错，价格有点贵，但是质量确实好...',
      description: '添加段落分割提升可读性'
    },
    testCases: []
  },

  // 语言规范类规则
  {
    id: 'standardize-punctuation',
    name: '标点符号规范',
    description: '规范标点符号的使用，确保语法正确',
    type: 'regex',
    category: 'language',
    enabled: true,
    isOfficial: true,
    config: {
      pattern: '([。！？])([^"』」】\\s])',
      replacement: '$1 $2',
      flags: 'g'
    },
    example: {
      before: '华为产品很好。我们很满意。价格有点贵。',
      after: '华为产品很好。我们很满意。价格有点贵。',
      description: '规范标点符号使用'
    },
    testCases: []
  },
  {
    id: 'convert-to-formal-language',
    name: '转换为正式语言',
    description: '将口语化表达转换为更正式的书面语言',
    type: 'llm',
    category: 'language',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '将以下口语化表达转换为正式的书面语言，保持原意不变'
    },
    example: {
      before: '华为的东西挺不错的，就是有点贵',
      after: '华为的产品质量较好，但价格相对较高',
      description: '转换为正式的书面表达'
    },
    testCases: []
  },
  {
    id: 'unify-terminology',
    name: '统一专业术语',
    description: '统一文档中的专业术语表达，保持一致性',
    type: 'llm',
    category: 'language',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '统一以下文本中的专业术语，确保同一概念使用相同的表达方式'
    },
    example: {
      before: '服务器、主机、计算设备在不同地方指代同一设备',
      after: '统一使用"服务器"来指代计算设备',
      description: '统一专业术语的表达'
    },
    testCases: []
  },

  // 对话处理类规则
  {
    id: 'convert-to-first-person',
    name: '转换为第一人称叙述',
    description: '将对话形式转换为第一人称的连贯叙述',
    type: 'llm',
    category: 'dialogue',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '将以下对话转换为第一人称的连贯叙述，保持所有关键信息'
    },
    example: {
      before: '顾问：您觉得华为产品怎么样？\n我觉得华为产品很好用。',
      after: '关于华为产品的评价，我觉得华为产品很好用。',
      description: '将问答对话转换为第一人称叙述'
    },
    testCases: []
  },
  {
    id: 'merge-qa-pairs',
    name: '合并问答对',
    description: '将相关的问答对合并成完整的主题段落',
    type: 'llm',
    category: 'dialogue',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '将相关的问答对合并成完整的主题段落，形成连贯的叙述'
    },
    example: {
      before: 'Q: 产品如何？A: 很好。Q: 价格呢？A: 有点贵。',
      after: '关于华为产品，我认为产品质量很好，但价格有点贵。',
      description: '合并相关问答形成完整段落'
    },
    testCases: []
  },
  {
    id: 'extract-interviewee-views',
    name: '提取被访者观点',
    description: '从对话中提取被访者的核心观点和态度',
    type: 'llm',
    category: 'dialogue',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '从以下对话中提取被访者的核心观点和态度，忽略访问者的问题'
    },
    example: {
      before: '顾问：您觉得如何？\n我觉得很好。顾问：有什么建议？\n希望价格更优惠。',
      after: '我觉得很好，希望价格更优惠。',
      description: '提取被访者的核心观点'
    },
    testCases: []
  },

  // 主题分类类规则
  {
    id: 'classify-product-feedback',
    name: '产品反馈分类',
    description: '将产品相关的反馈按功能、性能、质量等维度分类',
    type: 'llm',
    category: 'classification',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '将以下产品反馈按功能、性能、质量、易用性等维度进行分类整理'
    },
    example: {
      before: '华为产品功能强大，性能不错，但操作有点复杂',
      after: '【功能】功能强大\n【性能】性能不错\n【易用性】操作有点复杂',
      description: '按维度分类产品反馈'
    },
    testCases: []
  },
  {
    id: 'classify-service-feedback',
    name: '服务反馈分类',
    description: '将服务相关的反馈按售前、售后、技术支持等分类',
    type: 'llm',
    category: 'classification',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '将以下服务反馈按售前支持、售后服务、技术支持等类别进行分类'
    },
    example: {
      before: '售前很专业，售后响应及时，技术支持到位',
      after: '【售前支持】很专业\n【售后服务】响应及时\n【技术支持】到位',
      description: '按服务类型分类反馈'
    },
    testCases: []
  },
  {
    id: 'extract-improvement-suggestions',
    name: '提取改进建议',
    description: '从反馈中提取具体的改进建议和期望',
    type: 'llm',
    category: 'classification',
    enabled: true,
    isOfficial: true,
    config: {
      prompt: '从以下反馈中提取具体的改进建议和期望，分类整理'
    },
    example: {
      before: '希望价格更优惠，界面更友好，响应更快',
      after: '【价格建议】希望更优惠\n【界面建议】希望更友好\n【性能建议】希望响应更快',
      description: '提取并分类改进建议'
    },
    testCases: []
  }
]

// 现代化的规则集选择器组件
function RuleSetSelector({ ruleSets, currentRuleSetId, onRuleSetChange }: {
  ruleSets: RuleSet[]
  currentRuleSetId: string | null
  onRuleSetChange: (ruleSetId: string) => void
}) {
  const [isOpen, setIsOpen] = useState(false)
  const currentRuleSet = ruleSets.find(rs => rs.id === currentRuleSetId)

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between min-w-[200px] bg-white border border-gray-300 rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:border-gray-400 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all duration-200 shadow-sm"
      >
        <span className="truncate">
          {currentRuleSet?.name || '选择规则集'}
        </span>
        <ChevronDown 
          className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`} 
        />
      </button>

      {isOpen && (
        <>
          {/* 背景遮罩 */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* 下拉菜单 */}
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-20 py-1 max-h-60 overflow-y-auto">
            {ruleSets.map((ruleSet) => (
              <button
                key={ruleSet.id}
                onClick={() => {
                  onRuleSetChange(ruleSet.id)
                  setIsOpen(false)
                }}
                className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors ${
                  currentRuleSetId === ruleSet.id 
                    ? 'bg-gray-100 text-black font-medium' 
                    : 'text-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="truncate">{ruleSet.name}</span>
                  {currentRuleSetId === ruleSet.id && (
                    <Check className="w-4 h-4 text-black flex-shrink-0 ml-2" />
                  )}
                </div>
                {ruleSet.description && (
                  <div className="text-xs text-gray-500 mt-1 truncate">
                    {ruleSet.description}
                  </div>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

// 规则卡片组件
function RuleCard({ rule, onToggle, onViewDetails }: {
  rule: Rule
  onToggle: (ruleId: string) => void
  onViewDetails: (rule: Rule) => void
}) {
  return (
    <Card className={`relative overflow-hidden transition-all duration-200 hover:shadow-md cursor-pointer border-black min-h-[200px] ${
      rule.enabled ? 'ring-1 ring-black bg-gray-50' : ''
    }`}>
      <CardContent className="p-4 h-full flex flex-col">
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-sm font-semibold text-black truncate">{rule.name}</h3>
              {rule.isOfficial && (
                <Badge variant="outline" className="text-xs border-black text-black flex-shrink-0">
                  官方
                </Badge>
              )}
            </div>
            <p className="text-xs text-gray-600 line-clamp-2 mb-3">
              {rule.description}
            </p>
          </div>
          
          <div className="flex items-center gap-2 ml-3 flex-shrink-0">
            <Switch
              checked={rule.enabled}
              onCheckedChange={() => onToggle(rule.id)}
              className="data-[state=checked]:bg-black"
            />
            {rule.enabled ? (
              <Power className="h-3 w-3 text-black" />
            ) : (
              <PowerOff className="h-3 w-3 text-gray-400" />
            )}
          </div>
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-500 mb-4 flex-grow">
          <Badge variant="secondary" className="text-xs border-black text-black">
            {rule.type === 'llm' ? 'LLM规则' : rule.type === 'regex' ? '正则规则' : '自定义规则'}
          </Badge>
          <span className="truncate">分类: {rule.category}</span>
        </div>
        
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full text-xs border-black text-black hover:bg-gray-100 mt-auto"
          onClick={(e) => {
            e.stopPropagation()
            onViewDetails(rule)
          }}
        >
          <Eye className="h-3 w-3 mr-1" />
          查看详情
        </Button>
      </CardContent>
    </Card>
  )
}

// 规则集卡片组件
function RuleSetCard({ ruleSet, isActive, onSelect, onEdit }: {
  ruleSet: RuleSet
  isActive: boolean
  onSelect: (ruleSetId: string) => void
  onEdit?: (ruleSet: RuleSet) => void
}) {
  return (
    <Card className={`relative overflow-hidden transition-all duration-200 hover:shadow-md cursor-pointer border-black ${
      isActive ? 'ring-2 ring-black bg-blue-50' : ''
    }`} onClick={() => onSelect(ruleSet.id)}>
      <CardContent className="p-3">
        <div className="flex justify-between items-start mb-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="text-sm font-semibold text-black truncate">{ruleSet.name}</h4>
              {ruleSet.isOfficial && (
                <Badge variant="outline" className="text-xs border-black text-black flex-shrink-0">
                  官方
                </Badge>
              )}
              {isActive && (
                <Badge className="text-xs bg-black text-white flex-shrink-0">
                  使用中
                </Badge>
              )}
            </div>
            <p className="text-xs text-gray-600 line-clamp-1 mb-2">
              {ruleSet.description}
            </p>
          </div>
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{ruleSet.enabledRules.length} 个规则</span>
          <span>{new Date(ruleSet.createdAt).toLocaleDateString()}</span>
        </div>
      </CardContent>
    </Card>
  )
}

// 规则详情浮窗组件 - 使用21st-dev组件重新设计
function RuleDetailsModal({ rule, isOpen, onClose, onTest }: {
  rule: Rule | null
  isOpen: boolean
  onClose: () => void
  onTest: (rule: Rule, input: string) => Promise<string>
}) {
  const [testInput, setTestInput] = useState('')
  const [testOutput, setTestOutput] = useState('')
  const [isTestLoading, setIsTestLoading] = useState(false)

  if (!rule) return null

  const handleTest = async () => {
    if (!testInput.trim()) return
    
    setIsTestLoading(true)
    try {
      const result = await onTest(rule, testInput)
      setTestOutput(result)
    } catch (error) {
      setTestOutput('测试失败: ' + (error as Error).message)
    } finally {
      setIsTestLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-[95vw] w-[95vw] max-h-[95vh] overflow-hidden p-0 sm:max-w-[95vw]">
        {/* 头部区域 */}
        <div className="border-b px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <DialogTitle className="text-2xl font-bold">
                {rule.name}
              </DialogTitle>
              {rule.isOfficial && (
                <Badge variant="outline" className="text-sm">
                  官方
                </Badge>
              )}
              <Badge variant="outline" className={`text-sm ${rule.enabled ? '' : 'opacity-50'}`}>
                {rule.enabled ? '已启用' : '未启用'}
              </Badge>
            </div>
          </div>
          <DialogDescription className="text-base mt-3">
            {rule.description}
          </DialogDescription>
        </div>
        
        {/* 内容区域 */}
        <ScrollArea className="flex-1 px-8 py-6 max-h-[calc(95vh-200px)] overflow-y-auto overflow-x-hidden">
          <div className="space-y-8">
            {/* 规则基本信息卡片 */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold">规则信息</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="p-6">
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-muted-foreground">规则类型</h4>
                    <p className="text-base font-medium">
                      {rule.type === 'llm' ? 'LLM智能规则' : rule.type === 'regex' ? '正则表达式规则' : '自定义规则'}
                    </p>
                  </div>
                </Card>
                
                <Card className="p-6">
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-muted-foreground">规则分类</h4>
                    <p className="text-base font-medium">
                      {rule.category === 'format' ? '格式转换' : 
                       rule.category === 'content' ? '内容整理' :
                       rule.category === 'structure' ? '结构优化' :
                       rule.category === 'language' ? '语言规范' :
                       rule.category === 'dialogue' ? '对话处理' :
                       rule.category === 'classification' ? '主题分类' : '自定义'}
                    </p>
                  </div>
                </Card>
                
                <Card className="p-6">
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-muted-foreground">运行状态</h4>
                    <p className="text-base font-medium">
                      {rule.enabled ? '已启用' : '未启用'}
                    </p>
                  </div>
                </Card>
                
                <Card className="p-6">
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-muted-foreground">规则来源</h4>
                    <p className="text-base font-medium">
                      {rule.isOfficial ? '官方规则' : '自定义规则'}
                    </p>
                  </div>
                </Card>
              </div>
              
              <Card className="p-6">
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-muted-foreground">详细说明</h4>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {rule.description}
                  </p>
                </div>
              </Card>
            </div>

            {/* 转换示例卡片 */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold">转换示例</h3>
              
              {rule.example ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card className="p-6">
                      <div className="space-y-3">
                        <h4 className="text-sm font-medium text-muted-foreground">转换前</h4>
                        <div className="bg-muted p-4 rounded-md min-h-[150px]">
                          <pre className="text-sm font-mono whitespace-pre-wrap break-words">
                            {rule.example.before}
                          </pre>
                        </div>
                      </div>
                    </Card>
                    
                    <Card className="p-6">
                      <div className="space-y-3">
                        <h4 className="text-sm font-medium text-muted-foreground">转换后</h4>
                        <div className="bg-muted p-4 rounded-md min-h-[150px]">
                          <pre className="text-sm font-mono whitespace-pre-wrap break-words">
                            {rule.example.after}
                          </pre>
                        </div>
                      </div>
                    </Card>
                  </div>
                </div>
              ) : (
                <Card className="p-12 text-center">
                  <p className="text-muted-foreground">暂无转换示例</p>
                </Card>
              )}
            </div>

            {/* 规则测试卡片 */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold">规则测试</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="p-6">
                  <div className="space-y-4">
                    <h4 className="text-sm font-medium text-muted-foreground">测试输入</h4>
                    <Textarea
                      value={testInput}
                      onChange={(e) => setTestInput(e.target.value)}
                      placeholder="在此输入要测试的文本内容..."
                      className="min-h-[200px] text-sm font-mono resize-none"
                    />
                    
                    <Button
                      onClick={handleTest}
                      disabled={!testInput.trim() || isTestLoading}
                      className="w-full"
                    >
                      <TestTube className="h-4 w-4 mr-2" />
                      {isTestLoading ? (
                        <>
                          <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                          测试中...
                        </>
                      ) : (
                        '运行测试'
                      )}
                    </Button>
                  </div>
                </Card>
                
                <Card className="p-6">
                  <div className="space-y-4">
                    <h4 className="text-sm font-medium text-muted-foreground">测试结果</h4>
                    <div className="bg-muted p-4 rounded-md min-h-[200px] max-h-[250px] overflow-y-auto">
                      {testOutput ? (
                        <pre className="text-sm font-mono whitespace-pre-wrap break-words">
                          {testOutput}
                        </pre>
                      ) : (
                        <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                          <TestTube className="h-8 w-8 mb-2" />
                          <p className="text-sm">点击"运行测试"查看结果</p>
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}

// 保存规则集浮窗组件
function SaveRuleSetModal({ isOpen, onClose, onSave, enabledRules, currentRuleSet }: {
  isOpen: boolean
  onClose: () => void
  onSave: (name: string, description: string) => void
  enabledRules: Rule[]
  currentRuleSet?: RuleSet | null
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  useEffect(() => {
    if (isOpen) {
      if (currentRuleSet && !currentRuleSet.isOfficial) {
        setName(currentRuleSet.name)
        setDescription(currentRuleSet.description)
      } else {
        setName('')
        setDescription('')
      }
    }
  }, [isOpen, currentRuleSet])

  const handleSave = () => {
    if (!name.trim()) return
    onSave(name.trim(), description.trim())
    setName('')
    setDescription('')
    onClose()
  }

  const isUpdate = currentRuleSet && !currentRuleSet.isOfficial

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md border-black">
        <DialogHeader>
          <DialogTitle className="text-lg text-black">
            {isUpdate ? '更新规则集' : '保存规则集'}
          </DialogTitle>
          <DialogDescription className="text-sm text-gray-600">
            {isUpdate 
              ? `更新规则集"${currentRuleSet?.name}"的配置`
              : `将当前选中的 ${enabledRules.length} 个规则保存为规则集`
            }
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 mt-4">
          <div>
            <label className="text-xs font-medium text-black">规则集名称</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="输入规则集名称..."
              className="mt-1 text-xs border-black"
            />
          </div>
          
          <div>
            <label className="text-xs font-medium text-black">描述（可选）</label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="输入规则集描述..."
              className="mt-1 text-xs border-black min-h-[60px]"
            />
          </div>

          <div>
            <label className="text-xs font-medium text-black">包含的规则</label>
            <div className="mt-1 max-h-32 overflow-y-auto space-y-1">
              {enabledRules.map((rule) => (
                <div key={rule.id} className="flex items-center gap-2 text-xs">
                  <Check className="h-3 w-3 text-black" />
                  <span>{rule.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex gap-2 mt-6">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1 text-xs border-black text-black hover:bg-gray-100"
          >
            取消
          </Button>
          <Button
            onClick={handleSave}
            disabled={!name.trim()}
            className="flex-1 text-xs bg-black text-white hover:bg-gray-800"
          >
            <Save className="h-3 w-3 mr-1" />
            {isUpdate ? '更新' : '保存'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// 新增规则弹窗组件
function AddRuleModal({ isOpen, onClose, onSave, categories }: {
  isOpen: boolean
  onClose: () => void
  onSave: (rule: Omit<Rule, 'id'>) => void
  categories: { id: string; name: string }[]
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState<string>('format')
  const [type, setType] = useState<'llm' | 'regex' | 'custom'>('llm')
  const [isGenerating, setIsGenerating] = useState(false)

  const handleGenerate = async () => {
    if (!name.trim() || !description.trim()) return
    
    setIsGenerating(true)
    try {
      // 模拟生成规则
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const newRule: Omit<Rule, 'id'> = {
        name: name.trim(),
        description: description.trim(),
        category: category,
        type: type,
        enabled: true,
        isOfficial: false,
        example: {
          before: '示例输入文本',
          after: '转换后的输出文本',
          description: `${name.trim()}的转换效果展示`
        }
      }
      
      onSave(newRule)
      handleClose()
    } catch (error) {
      console.error('生成规则失败:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleClose = () => {
    setName('')
    setDescription('')
    setCategory('format')
    setType('llm')
    setIsGenerating(false)
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-bold">新增自定义规则</h2>
            <p className="text-muted-foreground mt-2">
              创建您的专属转换规则，精确控制文本转换逻辑
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                规则名称 <span className="text-red-500">*</span>
              </label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="输入规则名称，如：去除重复词汇"
                disabled={isGenerating}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                规则类型
              </label>
              <Select value={type} onValueChange={(value: 'llm' | 'regex' | 'custom') => setType(value)}>
                <SelectTrigger disabled={isGenerating}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="llm">LLM规则</SelectItem>
                  <SelectItem value="regex">正则表达式</SelectItem>
                  <SelectItem value="custom">自定义规则</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              规则分类
            </label>
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger disabled={isGenerating}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {categories.map((category) => (
                  <SelectItem key={category.id} value={category.id}>
                    {category.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              规则描述 <span className="text-red-500">*</span>
            </label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="详细描述这个规则的功能和效果，例如：将文本中所有的'您'替换为'你'，使语言更加亲切自然"
              className="h-32 resize-none"
              disabled={isGenerating}
            />
          </div>
          
          <div className="flex justify-end space-x-3">
            <Button variant="outline" onClick={handleClose} disabled={isGenerating}>
              取消
            </Button>
            <Button 
              onClick={handleGenerate}
              disabled={!name.trim() || !description.trim() || isGenerating}
              className="bg-black text-white hover:bg-gray-800"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  创建中...
                </>
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  创建规则
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// 获取类别标签的辅助函数
function getCategoryLabel(category: Rule['category']): string {
  const labels = {
    format: '格式规范',
    content: '内容转换', 
    style: '风格调整',
    correction: '错误纠正'
  }
  return labels[category] || category
}

function RulesPageContent() {
  const { 
    ruleSets, 
    currentRuleSetId, 
    setCurrentRuleSet, 
    getCurrentRuleSet, 
    addRule, 
    toggleRule 
  } = useRuleSet()
  const [selectedRule, setSelectedRule] = useState<Rule | null>(null)
  const [isRuleDetailsOpen, setIsRuleDetailsOpen] = useState(false)
  const [isAddRuleOpen, setIsAddRuleOpen] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState('all')

  const currentRuleSet = getCurrentRuleSet()

  // 合并官方规则和训练数据规则
  const allRules = useMemo(() => {
    const existingRules = currentRuleSet?.rules || []
    const existingIds = new Set(existingRules.map(rule => rule.id))
    const newRules = trainingBasedRules.filter(rule => !existingIds.has(rule.id))
    return [...existingRules, ...newRules]
  }, [currentRuleSet])

  // 根据分类筛选规则
  const filteredRules = useMemo(() => {
    if (selectedCategory === 'all') {
      return allRules
    }
    return allRules.filter(rule => rule.category === selectedCategory)
  }, [allRules, selectedCategory])

  // 计算每个分类的规则数量
  const categoryStats = useMemo(() => {
    const stats = ruleCategories.map(category => ({
      ...category,
      count: category.id === 'all' ? allRules.length : allRules.filter(rule => rule.category === category.id).length
    }))
    return stats
  }, [allRules])

  const handleRuleClick = (rule: Rule) => {
    setSelectedRule(rule)
    setIsRuleDetailsOpen(true)
  }

  const handleRuleSetChange = (ruleSetId: string) => {
    setCurrentRuleSet(ruleSetId)
  }

  const handleAddRule = (newRule: Omit<Rule, 'id'>) => {
    if (currentRuleSet) {
      addRule(currentRuleSet.id, newRule)
    }
  }

  const handleToggleRule = (ruleId: string) => {
    if (currentRuleSet) {
      toggleRule(currentRuleSet.id, ruleId)
    }
  }

  const handleTestRule = async (rule: Rule, input: string): Promise<string> => {
    // 模拟规则测试
    await new Promise(resolve => setTimeout(resolve, 1000))
    return `测试结果：应用"${rule.name}"规则后的输出`
  }

  return (
    <div className="flex h-screen bg-white">
      {/* 恢复原来dashboard界面的左侧边栏 */}
      <Sidebar />
      
      {/* 主内容区 */}
      <div className="flex-1 overflow-hidden ml-14 bg-gray-50">
                <div className="h-full p-6">
          <div className="max-w-7xl mx-auto">
            {/* 顶部标题和操作区 */}
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold text-black">规则配置</h2>
                <p className="text-gray-600 mt-1">
                  配置和管理转换规则，创建自定义规则集
                </p>
              </div>
              
              <div className="flex items-center gap-3">
                {/* 现代化的规则集选择器 */}
                <RuleSetSelector 
                  ruleSets={ruleSets}
                  currentRuleSetId={currentRuleSetId}
                  onRuleSetChange={handleRuleSetChange}
                />
                
                <Button 
                  onClick={() => setIsAddRuleOpen(true)}
                  className="bg-black text-white hover:bg-gray-800"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  新增规则
                </Button>
              </div>
            </div>

            {/* 主要内容区域 */}
            <div className="flex gap-6">
              {/* 优化后的规则分类区域 */}
              <div className="w-64 flex-shrink-0">
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="space-y-2">
                    {categoryStats.map((category) => (
                      <button
                        key={category.id}
                        onClick={() => setSelectedCategory(category.id)}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                          selectedCategory === category.id
                            ? 'bg-black text-white'
                            : 'text-gray-700 hover:bg-gray-100'
                        }`}
                      >
                        <span>{category.name}</span>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          selectedCategory === category.id
                            ? 'bg-white/20 text-white'
                            : 'bg-gray-200 text-gray-600'
                        }`}>
                          {category.count}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* 右侧：规则卡片网格 - 一行显示三个卡片 */}
              <div className="flex-1">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredRules.map((rule) => (
                    <RuleCard
                      key={rule.id}
                      rule={rule}
                      onToggle={handleToggleRule}
                      onViewDetails={handleRuleClick}
                    />
                  ))}
                                </div>
                
                {filteredRules.length === 0 && (
                  <div className="text-center py-12">
                    <div className="text-gray-400 text-lg mb-2">暂无规则</div>
                    <p className="text-gray-500 text-sm">
                      {selectedCategory === 'all' ? '当前规则集中没有规则' : '当前分类下没有规则'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 规则详情弹窗 */}
      <RuleDetailsModal
        rule={selectedRule}
        isOpen={isRuleDetailsOpen}
        onClose={() => setIsRuleDetailsOpen(false)}
        onTest={handleTestRule}
      />

      {/* 新增规则弹窗 */}
      <AddRuleModal
        isOpen={isAddRuleOpen}
        onClose={() => setIsAddRuleOpen(false)}
        onSave={handleAddRule}
        categories={ruleCategories.filter(c => c.id !== 'all')}
      />
    </div>
  )
}

function RulesPageLoading() {
  return (
    <div className="flex h-screen bg-white">
      <Sidebar />
      <div className="flex-1 overflow-hidden ml-14">
        <div className="h-full p-4 flex items-center justify-center">
          <div className="text-sm text-gray-500">加载中...</div>
        </div>
      </div>
    </div>
  )
}

export default function RulesPage() {
  return (
    <Suspense fallback={<RulesPageLoading />}>
      <RulesPageContent />
    </Suspense>
  )
} 