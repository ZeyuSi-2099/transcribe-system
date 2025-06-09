"use client";

import * as React from "react";
import { useState, useCallback, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { AlertCircle, Check, Code, FileText, Hash, Info, List, Play, Plus, Save, Settings, Trash2, X } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface RuleType {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
}

const RULE_TYPES: RuleType[] = [
  {
    id: "preprocessing",
    name: "预处理规则",
    description: "文本预处理阶段的规则",
    icon: <FileText className="h-4 w-4" />,
  },
  {
    id: "dialogue_structure",
    name: "对话结构规则",
    description: "对话结构转换规则",
    icon: <Code className="h-4 w-4" />,
  },
  {
    id: "language_style",
    name: "语言风格规则",
    description: "语言风格优化规则",
    icon: <List className="h-4 w-4" />,
  },
  {
    id: "content_filter",
    name: "内容过滤规则",
    description: "内容过滤和筛选规则",
    icon: <Hash className="h-4 w-4" />,
  },
  {
    id: "postprocessing",
    name: "后处理规则",
    description: "文本后处理阶段的规则",
    icon: <Settings className="h-4 w-4" />,
  },
];

interface RuleConfig {
  id?: number;
  name: string;
  description: string;
  rule_type: string;
  scope: string;
  priority: number;
  is_active: boolean;
  pattern?: string;
  replacement?: string;
  conditions?: Record<string, any>;
  parameters?: Record<string, any>;
  examples?: Array<{ input: string; output: string; }>;
  tags?: string[];
}

const useAutoResizeTextarea = ({
  minHeight,
  maxHeight,
}: {
  minHeight: number;
  maxHeight?: number;
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(
    (reset?: boolean) => {
      const textarea = textareaRef.current;
      if (!textarea) return;

      if (reset) {
        textarea.style.height = `${minHeight}px`;
        return;
      }

      textarea.style.height = `${minHeight}px`;
      const newHeight = Math.max(
        minHeight,
        Math.min(textarea.scrollHeight, maxHeight ?? Number.POSITIVE_INFINITY)
      );
      textarea.style.height = `${newHeight}px`;
    },
    [minHeight, maxHeight]
  );

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = `${minHeight}px`;
    }
  }, [minHeight]);

  useEffect(() => {
    const handleResize = () => adjustHeight();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [adjustHeight]);

  return { textareaRef, adjustHeight };
};

function RuleConfigManager() {
  const [rules, setRules] = useState<RuleConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeRule, setActiveRule] = useState<RuleConfig | null>(null);
  const [testInput, setTestInput] = useState("");
  const [testResult, setTestResult] = useState<{
    matched: boolean;
    details: string;
  } | null>(null);
  
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 100,
    maxHeight: 200,
  });

  // 获取规则列表
  const fetchRules = async () => {
    try {
      const response = await fetch('/api/v1/rules/rules');
      if (response.ok) {
        const data = await response.json();
        setRules(data);
      } else {
        // 如果API失败，获取默认规则
        const defaultResponse = await fetch('/api/v1/rules/default-rules');
        if (defaultResponse.ok) {
          const defaultData = await defaultResponse.json();
          setRules(defaultData.map((rule: any) => ({
            ...rule,
            scope: 'global',
            is_active: true,
            tags: []
          })));
        }
      }
    } catch (error) {
      console.error('获取规则失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleAddRule = () => {
    const newRule: RuleConfig = {
      name: "新规则",
      description: "",
      rule_type: "preprocessing",
      scope: "global",
      priority: 5,
      is_active: true,
      pattern: "",
      replacement: "",
      conditions: {},
      parameters: {},
      examples: [],
      tags: [],
    };
    setActiveRule(newRule);
  };

  const handleDeleteRule = async (id: number) => {
    try {
      const response = await fetch(`/api/v1/rules/rules/${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setRules(rules.filter((rule) => rule.id !== id));
        if (activeRule && activeRule.id === id) {
          setActiveRule(null);
        }
      }
    } catch (error) {
      console.error('删除规则失败:', error);
    }
  };

  const handleSaveRule = async (ruleData: RuleConfig) => {
    try {
      const isUpdate = !!ruleData.id;
      const url = isUpdate 
        ? `/api/v1/rules/rules/${ruleData.id}`
        : '/api/v1/rules/rules';
      
      const response = await fetch(url, {
        method: isUpdate ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(ruleData),
      });

      if (response.ok) {
        const savedRule = await response.json();
        if (isUpdate) {
          setRules(rules.map((rule) => (rule.id === savedRule.id ? savedRule : rule)));
        } else {
          setRules([...rules, savedRule]);
        }
        setActiveRule(savedRule);
      }
    } catch (error) {
      console.error('保存规则失败:', error);
    }
  };

  const handleTestRule = async () => {
    if (!activeRule) return;

    try {
      const response = await fetch(`/api/v1/rules/rules/${activeRule.id}/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: testInput }),
      });

      if (response.ok) {
        const result = await response.json();
        setTestResult({
          matched: result.applied,
          details: result.applied 
            ? `规则应用成功：${result.result_text}`
            : '规则未匹配到输入文本'
        });
      }
    } catch (error) {
      setTestResult({
        matched: false,
        details: `测试失败: ${error}`,
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">加载中...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-4 w-full max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">规则配置管理</h1>
        <Button onClick={handleAddRule}>
          <Plus className="mr-2 h-4 w-4" />
          添加规则
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>规则列表</CardTitle>
              <CardDescription>管理所有规则配置</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {rules.map((rule) => (
                  <div
                    key={rule.id || rule.name}
                    className={cn(
                      "flex items-center justify-between p-3 rounded-md cursor-pointer",
                      activeRule?.id === rule.id
                        ? "bg-accent text-accent-foreground"
                        : "hover:bg-muted"
                    )}
                    onClick={() => setActiveRule(rule)}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        {RULE_TYPES.find((t) => t.id === rule.rule_type)?.icon}
                      </div>
                      <div>
                        <div className="font-medium">{rule.name}</div>
                        <div className="text-xs text-muted-foreground">
                          优先级: {rule.priority}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge
                        variant={rule.is_active ? "default" : "outline"}
                        className="text-xs"
                      >
                        {rule.is_active ? "启用" : "禁用"}
                      </Badge>
                      {rule.id && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteRule(rule.id!);
                          }}
                        >
                          <Trash2 className="h-4 w-4 text-muted-foreground" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
                {rules.length === 0 && (
                  <div className="text-center py-4 text-muted-foreground">
                    暂无规则，请添加新规则
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2">
          {activeRule ? (
            <Tabs defaultValue="config">
              <TabsList className="grid grid-cols-2">
                <TabsTrigger value="config">
                  <Settings className="mr-2 h-4 w-4" />
                  规则配置
                </TabsTrigger>
                <TabsTrigger value="test">
                  <Play className="mr-2 h-4 w-4" />
                  规则测试
                </TabsTrigger>
              </TabsList>
              <TabsContent value="config">
                <Card>
                  <CardHeader>
                    <CardTitle>编辑规则</CardTitle>
                    <CardDescription>
                      配置规则的详细参数和匹配条件
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium">规则名称</label>
                        <Input
                          value={activeRule.name}
                          onChange={(e) =>
                            setActiveRule({
                              ...activeRule,
                              name: e.target.value,
                            })
                          }
                        />
                      </div>

                      <div>
                        <label className="text-sm font-medium">规则类型</label>
                        <Select
                          value={activeRule.rule_type}
                          onValueChange={(value) =>
                            setActiveRule({
                              ...activeRule,
                              rule_type: value,
                            })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="选择规则类型" />
                          </SelectTrigger>
                          <SelectContent>
                            {RULE_TYPES.map((type) => (
                              <SelectItem key={type.id} value={type.id}>
                                <div className="flex items-center">
                                  <span className="mr-2">{type.icon}</span>
                                  <span>{type.name}</span>
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <p className="text-xs text-muted-foreground mt-1">
                          {RULE_TYPES.find((t) => t.id === activeRule.rule_type)?.description}
                        </p>
                      </div>

                      <div>
                        <label className="text-sm font-medium">
                          优先级: {activeRule.priority}
                        </label>
                        <Slider
                          value={[activeRule.priority]}
                          min={1}
                          max={10}
                          step={1}
                          onValueChange={(value) =>
                            setActiveRule({
                              ...activeRule,
                              priority: value[0],
                            })
                          }
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                          优先级越高，规则越先被执行（1-10）
                        </p>
                      </div>

                      <div>
                        <label className="text-sm font-medium">匹配模式（正则表达式）</label>
                        <Textarea
                          value={activeRule.pattern || ""}
                          onChange={(e) =>
                            setActiveRule({
                              ...activeRule,
                              pattern: e.target.value,
                            })
                          }
                          placeholder="输入正则表达式，如: \\b(问：|答：)\\b"
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                          使用标准正则表达式语法进行匹配
                        </p>
                      </div>

                      <div>
                        <label className="text-sm font-medium">替换模板</label>
                        <Textarea
                          value={activeRule.replacement || ""}
                          onChange={(e) =>
                            setActiveRule({
                              ...activeRule,
                              replacement: e.target.value,
                            })
                          }
                          placeholder="输入替换模板，如: 空字符串删除匹配内容"
                        />
                      </div>

                      <div>
                        <label className="text-sm font-medium">规则描述</label>
                        <Textarea
                          value={activeRule.description}
                          onChange={(e) =>
                            setActiveRule({
                              ...activeRule,
                              description: e.target.value,
                            })
                          }
                          placeholder="输入规则的详细描述和用途"
                        />
                      </div>

                      <div className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                        <div className="space-y-0.5">
                          <label className="text-sm font-medium">启用规则</label>
                          <p className="text-xs text-muted-foreground">
                            切换此规则的启用状态
                          </p>
                        </div>
                        <Switch
                          checked={activeRule.is_active}
                          onCheckedChange={(checked) =>
                            setActiveRule({
                              ...activeRule,
                              is_active: checked,
                            })
                          }
                        />
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter className="flex justify-between">
                    <Button
                      variant="outline"
                      onClick={() => setActiveRule(null)}
                    >
                      取消
                    </Button>
                    <Button onClick={() => handleSaveRule(activeRule)}>
                      <Save className="mr-2 h-4 w-4" />
                      保存规则
                    </Button>
                  </CardFooter>
                </Card>
              </TabsContent>
              <TabsContent value="test">
                <Card>
                  <CardHeader>
                    <CardTitle>测试规则</CardTitle>
                    <CardDescription>
                      测试当前规则是否能正确匹配输入内容
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium">测试输入</label>
                        <Textarea
                          ref={textareaRef}
                          value={testInput}
                          onChange={(e) => {
                            setTestInput(e.target.value);
                            adjustHeight();
                          }}
                          placeholder="输入要测试的文本内容"
                          className="min-h-[100px]"
                        />
                      </div>

                      <div className="flex items-center space-x-2">
                        <Button onClick={handleTestRule}>
                          <Play className="mr-2 h-4 w-4" />
                          运行测试
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => {
                            setTestInput("");
                            setTestResult(null);
                            adjustHeight(true);
                          }}
                        >
                          <X className="mr-2 h-4 w-4" />
                          清除
                        </Button>
                      </div>

                      {testResult && (
                        <Alert
                          variant={testResult.matched ? "default" : "destructive"}
                        >
                          <div className="flex items-center">
                            {testResult.matched ? (
                              <Check className="h-4 w-4 mr-2" />
                            ) : (
                              <AlertCircle className="h-4 w-4 mr-2" />
                            )}
                            <AlertTitle>
                              {testResult.matched ? "匹配成功" : "匹配失败"}
                            </AlertTitle>
                          </div>
                          <AlertDescription>
                            {testResult.details}
                          </AlertDescription>
                        </Alert>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          ) : (
            <Card className="h-full flex items-center justify-center p-6">
              <div className="text-center">
                <Info className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">未选择规则</h3>
                <p className="text-muted-foreground mb-4">
                  请从左侧列表选择一个规则进行编辑，或创建一个新规则
                </p>
                <Button onClick={handleAddRule}>
                  <Plus className="mr-2 h-4 w-4" />
                  创建新规则
                </Button>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

export default RuleConfigManager; 