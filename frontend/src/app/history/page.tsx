"use client";

import * as React from "react";
import { useState, useEffect } from "react";
import { format } from "date-fns";
import { zhCN } from "date-fns/locale";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { 
  History, 
  Eye, 
  Trash2, 
  Download, 
  Search,
  Filter,
  Calendar,
  Clock,
  FileText,
  MoreVertical,
  RefreshCw,
  CheckCircle,
  XCircle,
  Loader
} from "lucide-react";
import Sidebar from '@/components/Sidebar';
import { useRouter } from 'next/navigation';

interface TranscriptionSummary {
  id: number;
  title: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  processing_time?: number;
}

interface TranscriptionDetail {
  id: number;
  title: string;
  original_text: string;
  converted_text: string;
  status: string;
  created_at: string;
  completed_at?: string;
  processing_time?: number;
  quality_metrics?: any;
  file_name?: string;
  file_type?: string;
  error_message?: string;
}

interface HistoryItem {
  id: number;
  title: string;
  original_text: string;
  converted_text: string;
  status: 'completed' | 'failed' | 'processing';
  createdAt: string;
  processing_time?: number;
  rule_set_name: string;
  file_type: 'text' | 'file';
  quality_score?: number;
}

export default function HistoryPage() {
  const router = useRouter();
  const [transcriptions, setTranscriptions] = useState<TranscriptionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<TranscriptionDetail | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("newest");

  useEffect(() => {
    fetchTranscriptions();
  }, []);

  const fetchTranscriptions = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/transcription/');
      if (response.ok) {
        const data = await response.json();
        setTranscriptions(data);
      }
    } catch (error) {
      console.error('获取历史记录失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTranscriptionDetail = async (id: number) => {
    try {
      const response = await fetch(`/api/v1/transcription/${id}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedItem(data);
      }
    } catch (error) {
      console.error('获取详情失败:', error);
    }
  };

  const deleteTranscription = async (id: number) => {
    try {
      const response = await fetch(`/api/v1/transcription/${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setTranscriptions(prev => prev.filter(item => item.id !== id));
        if (selectedItem?.id === id) {
          setSelectedItem(null);
        }
      }
    } catch (error) {
      console.error('删除失败:', error);
    }
  };

  const exportResult = (item: TranscriptionDetail) => {
    const content = `
原始笔录：
${item.original_text}

转换结果：
${item.converted_text}

转换信息：
- 任务标题：${item.title}
- 转换时间：${format(new Date(item.created_at), 'yyyy-MM-dd HH:mm:ss', { locale: zhCN })}
- 处理耗时：${item.processing_time ? `${item.processing_time.toFixed(2)}秒` : '未知'}
- 质量评分：${item.quality_metrics?.overall_score ? `${Math.round(item.quality_metrics.overall_score)}%` : '未评分'}
`;

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${item.title}_转换结果.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getStatusBadge = (status: string) => {
    const statusMap = {
      pending: { label: '等待中', variant: 'secondary' as const },
      processing: { label: '处理中', variant: 'default' as const },
      completed: { label: '已完成', variant: 'default' as const },
      failed: { label: '失败', variant: 'destructive' as const },
    };
    
    const statusInfo = statusMap[status as keyof typeof statusMap] || { label: status, variant: 'secondary' as const };
    return <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>;
  };

  const filteredTranscriptions = transcriptions.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const filteredAndSortedItems = filteredTranscriptions
    .sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case 'oldest':
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        case 'title':
          return a.title.localeCompare(b.title);
        case 'quality':
          return (b.quality_metrics?.overall_score || 0) - (a.quality_metrics?.overall_score || 0);
        default:
          return 0;
      }
    });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'processing':
        return <Loader className="w-4 h-4 text-yellow-600 animate-spin" />;
      default:
        return null;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'failed':
        return '失败';
      case 'processing':
        return '处理中';
      default:
        return '未知';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleViewDetails = (id: number) => {
    router.push(`/results/${id}`);
  };

  const handleDownload = (item: TranscriptionDetail) => {
    if (item.status !== 'completed') return;
    
    const blob = new Blob([item.converted_text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${item.title}_转换结果.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 侧边栏 */}
      <Sidebar />
      
      {/* 主内容区域 */}
      <div className="flex-1 overflow-hidden ml-14">
        <div className="h-full p-6 overflow-y-auto">
          {/* 页面标题 */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <History className="h-6 w-6" />
              转换历史
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              查看和管理所有的笔录转换记录
            </p>
        </div>
        
          {/* 搜索和过滤区域 */}
          <Card className="mb-6">
            <CardContent className="p-4">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
                      placeholder="搜索标题或内容..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
                </div>
                <div className="flex gap-2">
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">全部状态</SelectItem>
                      <SelectItem value="completed">已完成</SelectItem>
                      <SelectItem value="processing">处理中</SelectItem>
                      <SelectItem value="failed">失败</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={sortBy} onValueChange={setSortBy}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="newest">最新优先</SelectItem>
                      <SelectItem value="oldest">最旧优先</SelectItem>
                      <SelectItem value="title">按标题</SelectItem>
                      <SelectItem value="quality">按质量</SelectItem>
                    </SelectContent>
                  </Select>
        </div>
      </div>
            </CardContent>
          </Card>

          {/* 历史记录列表 */}
          <div className="space-y-4">
            {filteredAndSortedItems.length === 0 ? (
        <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <History className="w-12 h-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">暂无转换记录</h3>
                  <p className="text-gray-600 text-center">
              {searchTerm || statusFilter !== 'all' 
                      ? '没有找到匹配的记录，请尝试调整搜索条件'
                : '开始您的第一次笔录转换吧'
              }
            </p>
          </CardContent>
        </Card>
      ) : (
              filteredAndSortedItems.map(item => (
            <Card key={item.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold">{item.title}</h3>
                          <Badge 
                            variant="secondary" 
                            className={getStatusColor(item.status)}
                          >
                            <div className="flex items-center gap-1">
                              {getStatusIcon(item.status)}
                              {getStatusText(item.status)}
                            </div>
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {item.file_type === 'file' ? '文件上传' : '文本输入'}
                          </Badge>
                        </div>
                        
                        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                          {item.original_text.substring(0, 150)}
                          {item.original_text.length > 150 ? '...' : ''}
                        </p>
                        
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                        {format(new Date(item.created_at), 'yyyy-MM-dd HH:mm', { locale: zhCN })}
                          </div>
                          <div>规则集：{item.quality_metrics?.rule_set_name}</div>
                      {item.processing_time && (
                            <div>处理时间：{item.processing_time.toFixed(2)}s</div>
                          )}
                          {item.quality_metrics?.overall_score && (
                            <div>质量评分：{Math.round(item.quality_metrics.overall_score)}%</div>
                      )}
                        </div>
                  </div>
                  
                      <div className="flex items-center gap-2 ml-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleViewDetails(item.id)}
                          className="gap-1"
                        >
                          <Eye className="w-4 h-4" />
                          查看
                        </Button>
                        {item.status === 'completed' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDownload(item)}
                            className="gap-1"
                          >
                            <Download className="w-4 h-4" />
                            下载
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
                    )}
                  </div>
                </div>
              </div>
    </div>
  );
} 