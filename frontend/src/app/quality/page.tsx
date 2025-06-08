"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  BarChart3, 
  TrendingUp, 
  Target, 
  Zap, 
  FileText, 
  Activity,
  CheckCircle,
  AlertCircle,
  Clock
} from "lucide-react";
import { toast } from "sonner";

interface QualityStatistics {
  total_analyzed_records: number;
  basic_quality_stats: {
    count: number;
    average: number;
    median: number;
    min: number;
    max: number;
    std_dev: number;
  };
  advanced_quality_stats: {
    count: number;
    average: number;
    median: number;
    min: number;
    max: number;
    std_dev: number;
  };
  quality_distribution: {
    excellent: number;
    good: number;
    fair: number;
    poor: number;
  };
  advanced_distribution: {
    excellent: number;
    good: number;
    fair: number;
    poor: number;
  };
}

interface TrendData {
  trends: Array<{
    record_id: number;
    created_at: string;
    quality_score: number;
    file_name: string;
  }>;
  summary: {
    total_records: number;
    analyzed_records: number;
    average_score: number;
    trend_analysis: {
      trend: string;
      change_magnitude: number;
      analysis: string;
    };
  };
}

export default function QualityDashboard() {
  const [statistics, setStatistics] = useState<QualityStatistics | null>(null);
  const [trends, setTrends] = useState<TrendData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState("overview");

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // 并行加载统计数据和趋势数据
      const [statsResponse, trendsResponse] = await Promise.all([
        fetch('/api/v1/quality/statistics'),
        fetch('/api/v1/quality/trends/')
      ]);

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStatistics(statsData.data.statistics);
      }

      if (trendsResponse.ok) {
        const trendsData = await trendsResponse.json();
        setTrends(trendsData.data);
      }

    } catch (error) {
      console.error('加载仪表板数据失败:', error);
      toast.error('加载数据失败，请刷新重试');
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'declining':
        return <Activity className="h-4 w-4 text-red-600" />;
      default:
        return <Target className="h-4 w-4 text-blue-600" />;
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2">加载质量分析数据中...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">质量分析仪表板</h1>
          <p className="text-gray-600 mt-1">深度质量分析与趋势监控</p>
        </div>
        <Button onClick={loadDashboardData} variant="outline">
          <Activity className="mr-2 h-4 w-4" />
          刷新数据
        </Button>
      </div>

      {/* 概览卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总分析记录</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics?.total_analyzed_records || 0}</div>
            <p className="text-xs text-muted-foreground">已完成质量分析</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">平均质量评分</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statistics?.basic_quality_stats?.average?.toFixed(1) || '0.0'}
            </div>
            <p className="text-xs text-muted-foreground">基础质量评分</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">高级分析评分</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {statistics?.advanced_quality_stats?.average?.toFixed(1) || '0.0'}
            </div>
            <p className="text-xs text-muted-foreground">深度分析评分</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">质量趋势</CardTitle>
            {trends && getTrendIcon(trends.summary.trend_analysis.trend)}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {trends?.summary.trend_analysis.trend === 'improving' ? '上升' :
               trends?.summary.trend_analysis.trend === 'declining' ? '下降' : '稳定'}
            </div>
            <p className="text-xs text-muted-foreground">
              变化幅度: {trends?.summary.trend_analysis.change_magnitude?.toFixed(1) || '0.0'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 主要内容区域 */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">概览</TabsTrigger>
          <TabsTrigger value="distribution">分布分析</TabsTrigger>
          <TabsTrigger value="trends">趋势分析</TabsTrigger>
        </TabsList>

        {/* 概览标签页 */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 基础质量统计 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="mr-2 h-5 w-5" />
                  基础质量统计
                </CardTitle>
                <CardDescription>转换质量的基本统计信息</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {statistics?.basic_quality_stats ? (
                  <>
                    <div className="flex justify-between">
                      <span>记录数量:</span>
                      <span className="font-medium">{statistics.basic_quality_stats.count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>平均分:</span>
                      <span className="font-medium">{statistics.basic_quality_stats.average.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>中位数:</span>
                      <span className="font-medium">{statistics.basic_quality_stats.median.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>最高分:</span>
                      <span className="font-medium text-green-600">{statistics.basic_quality_stats.max.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>最低分:</span>
                      <span className="font-medium text-red-600">{statistics.basic_quality_stats.min.toFixed(1)}</span>
                    </div>
                  </>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    <Clock className="mx-auto h-12 w-12 text-gray-300 mb-4" />
                    <p>暂无统计数据</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 高级质量统计 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Zap className="mr-2 h-5 w-5" />
                  深度分析统计
                </CardTitle>
                <CardDescription>深度质量分析的统计信息</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {statistics?.advanced_quality_stats && statistics.advanced_quality_stats.count > 0 ? (
                  <>
                    <div className="flex justify-between">
                      <span>分析记录:</span>
                      <span className="font-medium">{statistics.advanced_quality_stats.count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>平均分:</span>
                      <span className="font-medium">{statistics.advanced_quality_stats.average.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>最高分:</span>
                      <span className="font-medium text-green-600">{statistics.advanced_quality_stats.max.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>最低分:</span>
                      <span className="font-medium text-red-600">{statistics.advanced_quality_stats.min.toFixed(1)}</span>
                    </div>
                  </>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    <Clock className="mx-auto h-12 w-12 text-gray-300 mb-4" />
                    <p>暂无深度分析数据</p>
                    <p className="text-sm">请先进行深度质量分析</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 分布分析标签页 */}
        <TabsContent value="distribution" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 基础质量分布 */}
            <Card>
              <CardHeader>
                <CardTitle>基础质量分布</CardTitle>
                <CardDescription>转换质量等级分布统计</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {statistics?.quality_distribution ? (
                  <>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
                          <span>优秀 (90-100分)</span>
                        </div>
                        <span className="font-medium">{statistics.quality_distribution.excellent}</span>
                      </div>
                      <Progress 
                        value={(statistics.quality_distribution.excellent / statistics.total_analyzed_records) * 100} 
                        className="h-2"
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
                          <span>良好 (80-89分)</span>
                        </div>
                        <span className="font-medium">{statistics.quality_distribution.good}</span>
                      </div>
                      <Progress 
                        value={(statistics.quality_distribution.good / statistics.total_analyzed_records) * 100} 
                        className="h-2"
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-orange-500 rounded mr-2"></div>
                          <span>中等 (70-79分)</span>
                        </div>
                        <span className="font-medium">{statistics.quality_distribution.fair}</span>
                      </div>
                      <Progress 
                        value={(statistics.quality_distribution.fair / statistics.total_analyzed_records) * 100} 
                        className="h-2"
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-red-500 rounded mr-2"></div>
                          <span>需要改进 (&lt;70分)</span>
                        </div>
                        <span className="font-medium">{statistics.quality_distribution.poor}</span>
                      </div>
                      <Progress 
                        value={(statistics.quality_distribution.poor / statistics.total_analyzed_records) * 100} 
                        className="h-2"
                      />
                    </div>
                  </>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    <BarChart3 className="mx-auto h-12 w-12 text-gray-300 mb-4" />
                    <p>暂无分布数据</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 深度分析分布 */}
            <Card>
              <CardHeader>
                <CardTitle>深度分析分布</CardTitle>
                <CardDescription>深度质量分析等级分布</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {statistics?.advanced_distribution && statistics.advanced_quality_stats.count > 0 ? (
                  <>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
                          <span>优秀 (90-100分)</span>
                        </div>
                        <span className="font-medium">{statistics.advanced_distribution.excellent}</span>
                      </div>
                      <Progress 
                        value={(statistics.advanced_distribution.excellent / statistics.advanced_quality_stats.count) * 100} 
                        className="h-2"
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
                          <span>良好 (80-89分)</span>
                        </div>
                        <span className="font-medium">{statistics.advanced_distribution.good}</span>
                      </div>
                      <Progress 
                        value={(statistics.advanced_distribution.good / statistics.advanced_quality_stats.count) * 100} 
                        className="h-2"
                      />
                    </div>
                  </>
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    <BarChart3 className="mx-auto h-12 w-12 text-gray-300 mb-4" />
                    <p>暂无深度分析分布数据</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 趋势分析标签页 */}
        <TabsContent value="trends" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="mr-2 h-5 w-5" />
                质量趋势分析
              </CardTitle>
              <CardDescription>
                最近 {trends?.summary.total_records || 0} 条转换记录的质量变化趋势
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {trends && trends.trends.length > 0 ? (
                <>
                  {/* 趋势总结 */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="flex items-center mb-2">
                      {getTrendIcon(trends.summary.trend_analysis.trend)}
                      <span className="ml-2 font-medium">
                        {trends.summary.trend_analysis.trend === 'improving' ? '质量提升趋势' :
                         trends.summary.trend_analysis.trend === 'declining' ? '质量下降趋势' : '质量稳定趋势'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">
                      {trends.summary.trend_analysis.analysis}
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
                      <div>
                        <div className="text-sm text-gray-500">分析记录</div>
                        <div className="font-medium">{trends.summary.analyzed_records}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-500">平均评分</div>
                        <div className="font-medium">{trends.summary.average_score.toFixed(1)}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-500">变化幅度</div>
                        <div className="font-medium">{trends.summary.trend_analysis.change_magnitude.toFixed(1)}</div>
                      </div>
                    </div>
                  </div>

                  {/* 最近记录列表 */}
                  <div className="space-y-2">
                    <h4 className="font-medium text-gray-900">最近转换记录</h4>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {trends.trends.slice(0, 10).map((record) => (
                        <div key={record.record_id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                          <div className="flex-1">
                            <div className="font-medium text-sm">{record.file_name}</div>
                            <div className="text-xs text-gray-500">
                              {new Date(record.created_at).toLocaleString('zh-CN')}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge 
                              variant={record.quality_score >= 90 ? "default" : 
                                     record.quality_score >= 80 ? "secondary" : 
                                     record.quality_score >= 70 ? "outline" : "destructive"}
                            >
                              {record.quality_score.toFixed(1)}分
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <TrendingUp className="mx-auto h-12 w-12 text-gray-300 mb-4" />
                  <p>暂无趋势数据</p>
                  <p className="text-sm">至少需要2条转换记录才能分析趋势</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 