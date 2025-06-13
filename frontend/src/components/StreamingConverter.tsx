'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Loader2, Play, Square, Download, Copy, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StreamEvent {
  type: 'start' | 'progress' | 'chunk' | 'quality' | 'complete' | 'error';
  data: any;
  timestamp: number;
}

interface ConversionState {
  isConnected: boolean;
  isConverting: boolean;
  progress: number;
  stage: string;
  message: string;
  partialContent: string;
  finalContent: string;
  qualityScore: number;
  conversationType: string;
  error: string | null;
}

interface StreamingConverterProps {
  className?: string;
}

export default function StreamingConverter({ className }: StreamingConverterProps) {
  const [inputText, setInputText] = useState('');
  const [copied, setCopied] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const [state, setState] = useState<ConversionState>({
    isConnected: false,
    isConverting: false,
    progress: 0,
    stage: '',
    message: '',
    partialContent: '',
    finalContent: '',
    qualityScore: 0,
    conversationType: '',
    error: null
  });

  // 打字机效果相关状态
  const [typewriterContent, setTypewriterContent] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const typewriterRef = useRef<{
    queue: string[];
    isRunning: boolean;
    timeoutId?: NodeJS.Timeout;
  }>({
    queue: [],
    isRunning: false
  });

  // 打字机效果函数
  const typeText = useCallback((text: string, speed: number = 30) => {
    const typewriter = typewriterRef.current;
    
    // 将新文本添加到队列
    typewriter.queue.push(text);
    
    // 如果已经在运行，不需要重新启动
    if (typewriter.isRunning) return;
    
    typewriter.isRunning = true;
    setIsTyping(true);
    
    const processQueue = () => {
      if (typewriter.queue.length === 0) {
        typewriter.isRunning = false;
        setIsTyping(false);
        return;
      }
      
      const currentText = typewriter.queue.shift()!;
      let index = 0;
      
      const typeChar = () => {
        if (index < currentText.length) {
          setTypewriterContent(prev => prev + currentText[index]);
          index++;
          typewriter.timeoutId = setTimeout(typeChar, speed);
        } else {
          // 当前文本打完，处理下一个
          processQueue();
        }
      };
      
      typeChar();
    };
    
    processQueue();
  }, []);

  // 重置状态
  const resetState = useCallback(() => {
    setState({
      isConnected: false,
      isConverting: false,
      progress: 0,
      stage: '',
      message: '',
      partialContent: '',
      finalContent: '',
      qualityScore: 0,
      conversationType: '',
      error: null
    });
    setTypewriterContent('');
    setIsTyping(false);
    
    // 清理打字机
    const typewriter = typewriterRef.current;
    typewriter.queue = [];
    typewriter.isRunning = false;
    if (typewriter.timeoutId) {
      clearTimeout(typewriter.timeoutId);
    }
  }, []);



  // 开始流式转换
  const startStreamConversion = useCallback(async () => {
    if (!inputText.trim() || state.isConverting) return;
    
    resetState();
    
    setState(prev => ({
      ...prev,
      isConverting: true,
      stage: '建立连接',
      message: '正在连接转换服务...'
    }));

    try {
      // 使用fetch进行流式POST请求
      const response = await fetch('/api/v1/v2/transcription/convert/stream-simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // 检查是否为流式响应
      if (!response.body) {
        throw new Error('响应不支持流式读取');
      }

      setState(prev => ({
        ...prev,
        isConnected: true,
        stage: '连接成功',
        message: '开始处理转换请求...'
      }));

      // 处理流式响应
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        // 解码数据
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          const trimmedLine = line.trim();
          
          if (trimmedLine.startsWith('event: ')) {
            const eventType = trimmedLine.substring(7);
            continue; // 事件类型行，继续处理下一行
          }
          
          if (trimmedLine.startsWith('data: ')) {
            const dataStr = trimmedLine.substring(6);
            
            try {
              const eventData = JSON.parse(dataStr);
              
              // 根据不同事件类型处理数据
              if (eventData.stage) {
                // progress 事件
                setState(prev => ({
                  ...prev,
                  progress: eventData.percentage || prev.progress,
                  stage: eventData.stage,
                  message: eventData.message
                }));
              } else if (eventData.content) {
                // chunk 事件 - 这里是关键的内容处理
                const content = eventData.content;
                
                // 确保内容有效且不为空
                if (content && typeof content === 'string' && content.trim()) {
                  // 添加到打字机队列
                  const typewriter = typewriterRef.current;
                  typewriter.queue.push(...content.split(''));
                  
                  // 如果打字机没有运行，启动它
                  if (!typewriter.isRunning) {
                    typewriter.isRunning = true;
                    processTypewriterQueue();
                  }
                }
              } else if (eventData.success !== undefined) {
                // complete 事件
                setState(prev => ({
                  ...prev,
                  isConverting: false,
                  isConnected: false,
                  stage: '转换完成',
                  message: '转换成功完成',
                  finalContent: eventData.final_content || prev.partialContent,
                  qualityScore: eventData.quality_score,
                  conversionSummary: eventData.conversion_summary
                }));
                
                // 确保打字机处理完所有内容
                const typewriter = typewriterRef.current;
                if (typewriter.queue.length === 0) {
                  setState(prev => ({ ...prev, partialContent: eventData.final_content || prev.partialContent }));
                }
              } else if (eventData.score !== undefined) {
                // quality 事件
                setState(prev => ({
                  ...prev,
                  qualityScore: eventData.score,
                  qualityMetrics: eventData.metrics
                }));
              } else if (eventData.message && eventData.conversation_type) {
                // start 事件
                setState(prev => ({
                  ...prev,
                  isConnected: true,
                  stage: '开始转换',
                  message: eventData.message,
                  conversationType: eventData.conversation_type
                }));
              }
            } catch (parseError) {
              console.warn('解析SSE数据失败:', dataStr, parseError);
            }
          }
        }
      }

    } catch (fetchError) {
      console.error('流式请求错误:', fetchError);
      setState(prev => ({
        ...prev,
        isConverting: false,
        isConnected: false,
        stage: '连接失败',
        message: `连接错误: ${fetchError.message}`,
        error: fetchError.message
      }));
    }
  }, [inputText, resetState, typeText]);

  const stopConversion = useCallback(() => {
    // 清理打字机
    const typewriter = typewriterRef.current;
    typewriter.queue = [];
    typewriter.isRunning = false;
    if (typewriter.timeoutId) {
      clearTimeout(typewriter.timeoutId);
    }
    
    setState(prev => ({
      ...prev,
      isConverting: false,
      isConnected: false,
      stage: '已停止',
      message: '转换已被用户停止'
    }));
  }, []);

  const copyResult = useCallback(async () => {
    const content = state.finalContent || typewriterContent;
    if (content) {
      try {
        await navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (error) {
        console.error('复制失败:', error);
      }
    }
  }, [state.finalContent, typewriterContent]);

  const downloadResult = useCallback(() => {
    const content = state.finalContent || typewriterContent;
    if (content) {
      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `转换结果_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  }, [state.finalContent, typewriterContent]);

  const getProgressColor = () => {
    if (state.error) return 'bg-red-500';
    if (state.progress === 100) return 'bg-green-500';
    return 'bg-blue-500';
  };

  const getStageColor = (stage: string) => {
    if (stage.includes('失败') || stage.includes('错误')) return 'destructive';
    if (stage.includes('完成')) return 'success';
    return 'default';
  };

  const getConversationTypeDisplay = (type: string) => {
    const typeMap: Record<string, string> = {
      'general': '一般对话',
      'interview': '面试对话',
      'meeting': '会议记录',
      'consultation': '咨询对话',
      'casual': '日常对话',
      'emotional': '情感对话'
    };
    return typeMap[type] || type;
  };

  // 示例文本
  const exampleTexts = [
    {
      title: '面试对话示例',
      content: '面试官: 你好，请简单介绍一下自己。\n我: 你好，我是张三，有三年的软件开发经验，熟悉React和Node.js。\n面试官: 你之前做过什么项目？\n我: 我主要负责过电商网站的前端开发，包括用户界面设计和交互功能实现。'
    },
    {
      title: '日常对话示例', 
      content: '医生: 你好，今天感觉怎么样？\n我: 还好，就是有点头痛。\n医生: 头痛多久了？\n我: 大概两天了，昨天开始的。\n医生: 有没有其他症状？\n我: 还有点发烧，体温大概37.8度。'
    },
    {
      title: '咨询对话示例',
      content: '律师: 请描述一下您遇到的法律问题。\n我: 我和房东因为租金问题产生了纠纷。\n律师: 具体是什么情况？\n我: 合同约定的租金是3000元，但房东突然要求涨到3500元。'
    }
  ];

  return (
    <div className={cn('max-w-7xl mx-auto space-y-6', className)}>
      {/* 输入区域 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Play className="h-5 w-5 text-blue-600" />
            <span>输入要转换的笔录</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="请输入对话式笔录内容，或选择下方示例..."
            className="min-h-[200px] text-sm leading-relaxed"
            disabled={state.isConverting}
          />
          
          {/* 示例文本按钮 */}
          <div className="space-y-2">
            <div className="text-sm font-medium text-slate-600">快速示例:</div>
            <div className="flex flex-wrap gap-2">
              {exampleTexts.map((example, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => setInputText(example.content)}
                  disabled={state.isConverting}
                  className="text-xs"
                >
                  {example.title}
                </Button>
              ))}
            </div>
          </div>

          {/* 控制按钮 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Button
                onClick={startStreamConversion}
                disabled={state.isConverting || !inputText.trim()}
                className="flex items-center space-x-2"
              >
                {state.isConverting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
                <span>{state.isConverting ? '转换中...' : '开始流式转换'}</span>
              </Button>
              
              {state.isConverting && (
                <Button
                  onClick={stopConversion}
                  variant="outline"
                  className="flex items-center space-x-2"
                >
                  <Square className="h-4 w-4" />
                  <span>停止</span>
                </Button>
              )}
            </div>
            
            <div className="text-sm text-slate-500">
              字数: {inputText.length}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 转换状态和进度 */}
      {(state.isConnected || state.error || state.isConverting) && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <div className={cn(
                  "h-3 w-3 rounded-full",
                  state.isConnected && !state.error ? "bg-green-500 animate-pulse" : 
                  state.error ? "bg-red-500" : "bg-yellow-500 animate-pulse"
                )} />
                <span>转换状态</span>
              </CardTitle>
              <div className="flex items-center space-x-2">
                {state.conversationType && (
                  <Badge variant="secondary">
                    {getConversationTypeDisplay(state.conversationType)}
                  </Badge>
                )}
                <Badge variant={getStageColor(state.stage)}>
                  {state.stage}
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">{state.message}</span>
                <span className="text-sm font-medium">{state.progress}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div 
                  className={cn("h-2 rounded-full transition-all duration-300", getProgressColor())}
                  style={{ width: `${state.progress}%` }}
                />
              </div>
              {state.qualityScore > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">质量评分:</span>
                  <span className="text-sm font-medium">{(state.qualityScore * 100).toFixed(1)}分</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 转换结果 */}
      {(typewriterContent || state.finalContent || isTyping) && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span>转换结果</span>
              </CardTitle>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={copyResult}
                  className="flex items-center space-x-1"
                >
                  <Copy className="h-4 w-4" />
                  <span>{copied ? '已复制' : '复制'}</span>
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={downloadResult}
                  className="flex items-center space-x-1"
                >
                  <Download className="h-4 w-4" />
                  <span>下载</span>
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="relative">
              <div className="bg-slate-50 p-4 rounded-lg min-h-[200px] text-sm leading-relaxed whitespace-pre-wrap">
                {typewriterContent || state.finalContent}
                {isTyping && (
                  <span className="inline-block w-2 h-5 bg-blue-500 ml-1 animate-pulse" />
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 