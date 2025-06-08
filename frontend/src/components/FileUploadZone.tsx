"use client";

import * as React from "react";
import { useState, useRef, useCallback } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { 
  Upload, 
  File, 
  FileText, 
  X, 
  CheckCircle, 
  AlertCircle,
  Loader2 
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface FileUploadZoneProps {
  onUploadSuccess?: (result: any) => void;
  onUploadError?: (error: string) => void;
  className?: string;
}

interface UploadState {
  file: File | null;
  uploading: boolean;
  progress: number;
  success: boolean;
  error: string | null;
  result: any | null;
}

const ACCEPTED_FILE_TYPES = {
  'text/plain': '.txt',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
  'text/csv': '.csv'
};

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export default function FileUploadZone({ 
  onUploadSuccess, 
  onUploadError, 
  className 
}: FileUploadZoneProps) {
  const [uploadState, setUploadState] = useState<UploadState>({
    file: null,
    uploading: false,
    progress: 0,
    success: false,
    error: null,
    result: null
  });
  const [title, setTitle] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const resetUpload = useCallback(() => {
    setUploadState({
      file: null,
      uploading: false,
      progress: 0,
      success: false,
      error: null,
      result: null
    });
    setTitle("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, []);

  const validateFile = useCallback((file: File): string | null => {
    // 检查文件类型
    if (!Object.keys(ACCEPTED_FILE_TYPES).includes(file.type)) {
      return `不支持的文件类型。支持的格式：${Object.values(ACCEPTED_FILE_TYPES).join(', ')}`;
    }

    // 检查文件大小
    if (file.size > MAX_FILE_SIZE) {
      return `文件大小超过限制（最大 ${Math.round(MAX_FILE_SIZE / 1024 / 1024)}MB）`;
    }

    return null;
  }, []);

  const uploadFile = useCallback(async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setUploadState(prev => ({ ...prev, error: validationError }));
      onUploadError?.(validationError);
      return;
    }

    setUploadState(prev => ({
      ...prev,
      file,
      uploading: true,
      progress: 0,
      error: null,
      success: false
    }));

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title || `文件转换-${file.name}`);
      formData.append('rule_config', '{}');

      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadState(prev => {
          const newProgress = Math.min(prev.progress + 10, 90);
          return { ...prev, progress: newProgress };
        });
      }, 200);

      const response = await fetch('/api/v1/transcription/upload', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '上传失败');
      }

      const result = await response.json();

      setUploadState(prev => ({
        ...prev,
        uploading: false,
        progress: 100,
        success: true,
        result
      }));

      onUploadSuccess?.(result);

      // 开始轮询转换状态
      pollConversionStatus(result.id);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '上传失败';
      setUploadState(prev => ({
        ...prev,
        uploading: false,
        error: errorMessage
      }));
      onUploadError?.(errorMessage);
    }
  }, [title, validateFile, onUploadSuccess, onUploadError]);

  const pollConversionStatus = useCallback(async (transcriptionId: number) => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`/api/v1/transcription/${transcriptionId}`);
        if (response.ok) {
          const data = await response.json();
          
          if (data.status === 'completed') {
            setUploadState(prev => ({
              ...prev,
              result: { ...prev.result, ...data }
            }));
          } else if (data.status === 'failed') {
            setUploadState(prev => ({
              ...prev,
              error: data.error_message || '转换失败'
            }));
          } else {
            // 继续轮询
            setTimeout(checkStatus, 2000);
          }
        }
      } catch (error) {
        console.error('轮询状态失败:', error);
      }
    };

    checkStatus();
  }, []);

  const handleFileSelect = useCallback((file: File) => {
    uploadFile(file);
  }, [uploadFile]);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  }, [handleFileSelect]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const getFileIcon = (file: File) => {
    if (file.type === 'text/plain') {
      return <FileText className="h-8 w-8 text-blue-500" />;
    } else if (file.type.includes('wordprocessingml')) {
      return <File className="h-8 w-8 text-blue-600" />;
    }
    return <File className="h-8 w-8 text-gray-500" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          文件上传转换
        </CardTitle>
        <CardDescription>
          支持上传 .txt、.docx、.csv 格式文件进行笔录转换
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 标题输入 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">转换任务标题（可选）</label>
          <Input
            placeholder="输入转换任务的标题"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={uploadState.uploading}
          />
        </div>

        {/* 文件上传区域 */}
        <div
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
            isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25",
            uploadState.error ? "border-destructive bg-destructive/5" : "",
            "hover:border-primary/50 hover:bg-muted/50"
          )}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          {uploadState.file ? (
            // 文件已选择状态
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-3">
                {getFileIcon(uploadState.file)}
                <div className="text-left">
                  <p className="font-medium">{uploadState.file.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(uploadState.file.size)}
                  </p>
                </div>
              </div>

              {uploadState.uploading && (
                <div className="space-y-2">
                  <div className="flex items-center justify-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">
                      {uploadState.progress < 100 ? '上传中...' : '处理中...'}
                    </span>
                  </div>
                  <Progress value={uploadState.progress} className="w-full" />
                </div>
              )}

              {uploadState.success && !uploadState.uploading && (
                <div className="flex items-center justify-center gap-2 text-green-600">
                  <CheckCircle className="h-5 w-5" />
                  <span>上传成功，正在转换中...</span>
                </div>
              )}

              <div className="flex gap-2 justify-center">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={resetUpload}
                  disabled={uploadState.uploading}
                >
                  <X className="h-4 w-4 mr-1" />
                  重新选择
                </Button>
              </div>
            </div>
          ) : (
            // 文件选择状态
            <div className="space-y-4">
              <Upload className="h-12 w-12 mx-auto text-muted-foreground" />
              <div>
                <p className="text-lg font-medium">拖拽文件到这里</p>
                <p className="text-sm text-muted-foreground">
                  或者
                </p>
              </div>
              <Button
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadState.uploading}
              >
                选择文件
              </Button>
              <p className="text-xs text-muted-foreground">
                支持 .txt、.docx、.csv 格式，最大 {Math.round(MAX_FILE_SIZE / 1024 / 1024)}MB
              </p>
            </div>
          )}
        </div>

        {/* 错误提示 */}
        {uploadState.error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{uploadState.error}</AlertDescription>
          </Alert>
        )}

        {/* 转换结果预览 */}
        {uploadState.result && uploadState.result.status === 'completed' && (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              转换完成！任务ID: {uploadState.result.id}
            </AlertDescription>
          </Alert>
        )}

        {/* 隐藏的文件输入 */}
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept={Object.values(ACCEPTED_FILE_TYPES).join(',')}
          onChange={handleFileInputChange}
        />
      </CardContent>
    </Card>
  );
} 