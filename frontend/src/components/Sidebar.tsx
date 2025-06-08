'use client'

import { useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { 
  Plus, 
  History, 
  Settings, 
  FileText, 
  ChevronDown, 
  ChevronRight,
  Clock,
  Wand2,
  Home
} from 'lucide-react'
import { cn } from "@/lib/utils"

interface HistoryItem {
  id: number
  title: string
  createdAt: string
  status: 'completed' | 'failed' | 'processing'
}

interface RuleSetItem {
  id: string
  name: string
  updatedAt: string
  isDefault: boolean
}

const sidebarVariants = {
  open: {
    width: "16rem",
  },
  closed: {
    width: "3.5rem",
  },
}

const contentVariants = {
  open: { display: "block", opacity: 1 },
  closed: { display: "block", opacity: 1 },
}

const variants = {
  open: {
    x: 0,
    opacity: 1,
    transition: {
      x: { stiffness: 1000, velocity: -100 },
    },
  },
  closed: {
    x: -20,
    opacity: 0,
    transition: {
      x: { stiffness: 100 },
    },
  },
}

const transitionProps = {
  type: "tween" as const,
  ease: "easeOut",
  duration: 0.2,
  staggerChildren: 0.1,
}

const staggerVariants = {
  open: {
    transition: { staggerChildren: 0.03, delayChildren: 0.02 },
  },
}

export default function Sidebar() {
  const router = useRouter()
  const pathname = usePathname()
  const [isCollapsed, setIsCollapsed] = useState(true)
  const [isHistoryExpanded, setIsHistoryExpanded] = useState(true)
  const [isRulesExpanded, setIsRulesExpanded] = useState(true)
  
  // 模拟数据
  const [recentHistory, setRecentHistory] = useState<HistoryItem[]>([
    { id: 1, title: '会议记录转换', createdAt: '2024-06-04 20:30', status: 'completed' },
    { id: 2, title: '访谈笔录整理', createdAt: '2024-06-04 19:45', status: 'completed' },
    { id: 3, title: '客户沟通记录', createdAt: '2024-06-04 18:20', status: 'failed' },
    { id: 4, title: '项目讨论纪要', createdAt: '2024-06-04 17:15', status: 'completed' },
    { id: 5, title: '培训课程笔记', createdAt: '2024-06-04 16:30', status: 'completed' }
  ])
  
  const [recentRuleSets, setRecentRuleSets] = useState<RuleSetItem[]>([
    { id: 'default', name: '通用规则集', updatedAt: '2024-06-04 20:00', isDefault: true },
    { id: 'custom_1', name: '会议专用规则', updatedAt: '2024-06-04 19:30', isDefault: false },
    { id: 'custom_2', name: '访谈优化规则', updatedAt: '2024-06-04 18:45', isDefault: false }
  ])

  const handleNewConversion = () => {
    router.push('/')
  }

  const handleViewHistory = (id?: number) => {
    if (id) {
      router.push(`/results/${id}`)
    } else {
      router.push('/history')
    }
  }

  const handleRuleConfig = (id?: string) => {
    if (id) {
      router.push(`/rules?set=${id}`)
    } else {
      router.push('/rules')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'processing': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return '已完成'
      case 'failed': return '失败'
      case 'processing': return '处理中'
      default: return '未知'
    }
  }

  return (
    <motion.div
      className={cn(
        "sidebar fixed left-0 z-40 h-full shrink-0 border-r bg-white dark:bg-black",
      )}
      initial={isCollapsed ? "closed" : "open"}
      animate={isCollapsed ? "closed" : "open"}
      variants={sidebarVariants}
      transition={transitionProps}
      onMouseEnter={() => setIsCollapsed(false)}
      onMouseLeave={() => setIsCollapsed(true)}
    >
      <motion.div
        className="relative z-40 flex text-muted-foreground h-full shrink-0 flex-col bg-white dark:bg-black transition-all"
        variants={contentVariants}
      >
        <motion.ul variants={staggerVariants} className="flex h-full flex-col">
          <div className="flex grow flex-col items-center">
            {/* 主导航区域 */}
            <div className="flex h-full w-full flex-col">
              <div className="flex grow flex-col gap-2 p-2">
                <ScrollArea className="h-16 grow">
                  <div className={cn("flex w-full flex-col gap-1")}>
                    {/* 新转换 */}
                    <div
                      onClick={handleNewConversion}
                      className={cn(
                        "flex h-10 w-full flex-row items-center rounded-md px-2 py-1.5 cursor-pointer transition hover:bg-muted hover:text-primary",
                        pathname === '/' && "bg-muted text-blue-600",
                      )}
                    >
                      <Plus className="h-4 w-4" />
                      <motion.li variants={variants}>
                        {!isCollapsed && (
                          <p className="ml-2 text-sm font-medium">新转换</p>
                        )}
                      </motion.li>
                    </div>

                    {/* 转换历史 */}
                    <div
                      onClick={() => setIsHistoryExpanded(!isHistoryExpanded)}
                      className={cn(
                        "flex h-10 w-full flex-row items-center rounded-md px-2 py-1.5 cursor-pointer transition hover:bg-muted hover:text-primary",
                        pathname?.includes("history") && "bg-muted text-blue-600",
                      )}
                    >
                      <History className="h-4 w-4" />
                      <motion.li variants={variants}>
                        {!isCollapsed && (
                          <div className="flex items-center justify-between w-full ml-2">
                            <p className="text-sm font-medium">转换历史</p>
                            {isHistoryExpanded ? (
                              <ChevronDown className="w-4 h-4" />
                            ) : (
                              <ChevronRight className="w-4 h-4" />
                            )}
                          </div>
                        )}
                      </motion.li>
                    </div>

                    {/* 历史记录子项 */}
                    {!isCollapsed && isHistoryExpanded && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="ml-6 space-y-1"
                      >
                        {recentHistory.slice(0, 3).map(item => (
                          <div
                            key={item.id}
                            className="p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                            onClick={() => handleViewHistory(item.id)}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs font-medium truncate flex-1">
                                {item.title}
                              </span>
                              <Badge 
                                variant="secondary" 
                                className={cn("text-xs", getStatusColor(item.status))}
                              >
                                {getStatusText(item.status)}
                              </Badge>
                            </div>
                            <div className="flex items-center gap-1 text-xs text-gray-500">
                              <Clock className="w-3 h-3" />
                              {item.createdAt}
                            </div>
                          </div>
                        ))}
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="w-full text-xs"
                          onClick={() => handleViewHistory()}
                        >
                          查看全部历史
                        </Button>
                      </motion.div>
                    )}

                    <Separator className="w-full my-2" />

                    {/* 规则配置 */}
                    <div
                      onClick={() => setIsRulesExpanded(!isRulesExpanded)}
                      className={cn(
                        "flex h-10 w-full flex-row items-center rounded-md px-2 py-1.5 cursor-pointer transition hover:bg-muted hover:text-primary",
                        pathname?.includes("rules") && "bg-muted text-blue-600",
                      )}
                    >
                      <Settings className="h-4 w-4" />
                      <motion.li variants={variants}>
                        {!isCollapsed && (
                          <div className="flex items-center justify-between w-full ml-2">
                            <p className="text-sm font-medium">规则配置</p>
                            {isRulesExpanded ? (
                              <ChevronDown className="w-4 h-4" />
                            ) : (
                              <ChevronRight className="w-4 h-4" />
                            )}
                          </div>
                        )}
                      </motion.li>
                    </div>

                    {/* 规则配置子项 */}
                    {!isCollapsed && isRulesExpanded && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="ml-6 space-y-1"
                      >
                        {recentRuleSets.map(item => (
                          <div
                            key={item.id}
                            className="p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                            onClick={() => handleRuleConfig(item.id)}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs font-medium truncate flex-1">
                                {item.name}
                              </span>
                              {item.isDefault && (
                                <Badge variant="secondary" className="text-xs">
                                  默认
                                </Badge>
                              )}
                            </div>
                            <div className="flex items-center gap-1 text-xs text-gray-500">
                              <Clock className="w-3 h-3" />
                              {item.updatedAt}
                            </div>
                          </div>
                        ))}
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="w-full text-xs"
                          onClick={() => handleRuleConfig()}
                        >
                          管理所有规则集
                        </Button>
                      </motion.div>
                    )}
                  </div>
                </ScrollArea>
              </div>
            </div>
          </div>
        </motion.ul>
      </motion.div>
    </motion.div>
  )
} 