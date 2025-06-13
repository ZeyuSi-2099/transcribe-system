'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export interface Rule {
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

export interface RuleSet {
  id: string
  name: string
  description: string
  isDefault: boolean
  isOfficial: boolean
  enabledRules: string[]
  enabledRulesCount: number
  rules?: Rule[]
  createdAt: string
  updatedAt: string
}

interface RuleSetContextType {
  ruleSets: RuleSet[]
  currentRuleSetId: string
  addRuleSet: (ruleSet: Omit<RuleSet, 'id' | 'createdAt' | 'updatedAt'>) => void
  updateRuleSet: (id: string, updates: Partial<RuleSet>) => void
  deleteRuleSet: (id: string) => void
  setCurrentRuleSet: (id: string) => void
  getCurrentRuleSet: () => RuleSet | undefined
  getRuleSetById: (id: string) => RuleSet | undefined
  addRule: (ruleSetId: string, rule: Omit<Rule, 'id'>) => void
  updateRule: (ruleSetId: string, ruleId: string, updates: Partial<Rule>) => void
  deleteRule: (ruleSetId: string, ruleId: string) => void
  toggleRule: (ruleSetId: string, ruleId: string) => void
}

const RuleSetContext = createContext<RuleSetContextType | undefined>(undefined)

// 示例规则数据
const sampleRules: Rule[] = [
  {
    id: 'basic_1',
    name: '去除重复词汇',
    description: '去除句子中的重复词汇和冗余表达',
    category: 'basic',
    type: 'llm',
    enabled: true,
    isOfficial: true,
    example: {
      before: '然后然后，我就我就去了去了那里',
      after: '然后，我就去了那里',
      description: '识别并去除重复的词汇和短语'
    }
  },
  {
    id: 'basic_2',
    name: '标点符号规范',
    description: '规范标点符号的使用，确保语法正确',
    category: 'format',
    type: 'regex',
    enabled: true,
    isOfficial: true,
    example: {
      before: '我说,你好吗?',
      after: '我说："你好吗？"',
      description: '修正标点符号的使用和位置'
    }
  },
  {
    id: 'format_1',
    name: '第一人称转换',
    description: '将对话转换为第一人称叙述',
    category: 'content',
    type: 'llm',
    enabled: true,
    isOfficial: true,
    example: {
      before: '问：你今天做了什么？答：我去了商店。',
      after: '今天我去了商店。',
      description: '将问答格式转换为第一人称叙述'
    }
  }
]

// 初始规则集数据
const initialRuleSets: RuleSet[] = [
  {
    id: 'default',
    name: '官方-通用规则集',
    description: '适用于大多数笔录转换场景',
    isDefault: true,
    isOfficial: true,
    enabledRules: ['basic_1', 'basic_2', 'format_1'],
    enabledRulesCount: 3,
    rules: sampleRules,
    createdAt: '2024-06-01T00:00:00Z',
    updatedAt: '2024-06-01T00:00:00Z'
  },
  {
    id: 'official_meeting',
    name: '官方-会议记录规则集',
    description: '专门针对会议记录优化的规则集',
    isDefault: false,
    isOfficial: true,
    enabledRules: ['basic_1', 'format_1'],
    enabledRulesCount: 2,
    rules: sampleRules.filter(rule => ['basic_1', 'format_1'].includes(rule.id)),
    createdAt: '2024-06-01T00:00:00Z',
    updatedAt: '2024-06-01T00:00:00Z'
  }
]

export function RuleSetProvider({ children }: { children: ReactNode }) {
  const [ruleSets, setRuleSets] = useState<RuleSet[]>(initialRuleSets)
  const [currentRuleSetId, setCurrentRuleSetId] = useState('default')

  // 从localStorage加载数据
  useEffect(() => {
    const savedRuleSets = localStorage.getItem('ruleSets')
    const savedCurrentRuleSetId = localStorage.getItem('currentRuleSetId')
    
    if (savedRuleSets) {
      try {
        const parsed = JSON.parse(savedRuleSets)
        setRuleSets(parsed)
      } catch (error) {
        console.error('Failed to parse saved rule sets:', error)
      }
    }
    
    if (savedCurrentRuleSetId) {
      setCurrentRuleSetId(savedCurrentRuleSetId)
    }
  }, [])

  // 保存到localStorage
  useEffect(() => {
    localStorage.setItem('ruleSets', JSON.stringify(ruleSets))
  }, [ruleSets])

  useEffect(() => {
    localStorage.setItem('currentRuleSetId', currentRuleSetId)
  }, [currentRuleSetId])

  const addRuleSet = (ruleSet: Omit<RuleSet, 'id' | 'createdAt' | 'updatedAt'>) => {
    const now = new Date().toISOString()
    const newRuleSet: RuleSet = {
      ...ruleSet,
      id: `custom_${Date.now()}`,
      createdAt: now,
      updatedAt: now
    }
    setRuleSets(prev => [...prev, newRuleSet])
  }

  const updateRuleSet = (id: string, updates: Partial<RuleSet>) => {
    setRuleSets(prev => prev.map(ruleSet => 
      ruleSet.id === id 
        ? { ...ruleSet, ...updates, updatedAt: new Date().toISOString() }
        : ruleSet
    ))
  }

  const deleteRuleSet = (id: string) => {
    setRuleSets(prev => prev.filter(ruleSet => ruleSet.id !== id))
    if (currentRuleSetId === id) {
      setCurrentRuleSetId('default')
    }
  }

  const setCurrentRuleSet = (id: string) => {
    setCurrentRuleSetId(id)
  }

  const getCurrentRuleSet = () => {
    return ruleSets.find(ruleSet => ruleSet.id === currentRuleSetId)
  }

  const getRuleSetById = (id: string) => {
    return ruleSets.find(ruleSet => ruleSet.id === id)
  }

  const addRule = (ruleSetId: string, rule: Omit<Rule, 'id'>) => {
    const newRule: Rule = {
      ...rule,
      id: `rule_${Date.now()}`
    }
    
    setRuleSets(prev => prev.map(ruleSet => 
      ruleSet.id === ruleSetId 
        ? { 
            ...ruleSet, 
            rules: [...(ruleSet.rules || []), newRule],
            enabledRules: rule.enabled 
              ? [...ruleSet.enabledRules, newRule.id]
              : ruleSet.enabledRules,
            enabledRulesCount: rule.enabled 
              ? ruleSet.enabledRulesCount + 1
              : ruleSet.enabledRulesCount,
            updatedAt: new Date().toISOString()
          }
        : ruleSet
    ))
  }

  const updateRule = (ruleSetId: string, ruleId: string, updates: Partial<Rule>) => {
    setRuleSets(prev => prev.map(ruleSet => 
      ruleSet.id === ruleSetId 
        ? { 
            ...ruleSet, 
            rules: ruleSet.rules?.map(rule => 
              rule.id === ruleId ? { ...rule, ...updates } : rule
            ),
            updatedAt: new Date().toISOString()
          }
        : ruleSet
    ))
  }

  const deleteRule = (ruleSetId: string, ruleId: string) => {
    setRuleSets(prev => prev.map(ruleSet => 
      ruleSet.id === ruleSetId 
        ? { 
            ...ruleSet, 
            rules: ruleSet.rules?.filter(rule => rule.id !== ruleId),
            enabledRules: ruleSet.enabledRules.filter(id => id !== ruleId),
            enabledRulesCount: ruleSet.enabledRules.includes(ruleId) 
              ? ruleSet.enabledRulesCount - 1
              : ruleSet.enabledRulesCount,
            updatedAt: new Date().toISOString()
          }
        : ruleSet
    ))
  }

  const toggleRule = (ruleSetId: string, ruleId: string) => {
    setRuleSets(prev => prev.map(ruleSet => 
      ruleSet.id === ruleSetId 
        ? { 
            ...ruleSet, 
            rules: ruleSet.rules?.map(rule => 
              rule.id === ruleId 
                ? { ...rule, enabled: !rule.enabled }
                : rule
            ),
            enabledRules: ruleSet.enabledRules.includes(ruleId)
              ? ruleSet.enabledRules.filter(id => id !== ruleId)
              : [...ruleSet.enabledRules, ruleId],
            enabledRulesCount: ruleSet.enabledRules.includes(ruleId)
              ? ruleSet.enabledRulesCount - 1
              : ruleSet.enabledRulesCount + 1,
            updatedAt: new Date().toISOString()
          }
        : ruleSet
    ))
  }

  const value: RuleSetContextType = {
    ruleSets,
    currentRuleSetId,
    addRuleSet,
    updateRuleSet,
    deleteRuleSet,
    setCurrentRuleSet,
    getCurrentRuleSet,
    getRuleSetById,
    addRule,
    updateRule,
    deleteRule,
    toggleRule
  }

  return (
    <RuleSetContext.Provider value={value}>
      {children}
    </RuleSetContext.Provider>
  )
}

export function useRuleSet() {
  const context = useContext(RuleSetContext)
  if (context === undefined) {
    throw new Error('useRuleSet must be used within a RuleSetProvider')
  }
  return context
} 