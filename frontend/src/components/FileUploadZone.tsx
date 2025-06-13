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
  inputText?: string;
  onInputChange?: (text: string) => void;
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
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
};

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export default function FileUploadZone({ 
  onUploadSuccess, 
  onUploadError, 
  className,
  inputText = '',
  onInputChange
}: FileUploadZoneProps) {
  const [uploadState, setUploadState] = useState<UploadState>({
    file: null,
    uploading: false,
    progress: 0,
    success: false,
    error: null,
    result: null,
  });
  const [title, setTitle] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const resetUpload = () => {
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
  };

  const validateFile = useCallback((file: File): string | null => {
    if (!Object.keys(ACCEPTED_FILE_TYPES).includes(file.type)) {
      return `不支持的文件类型。支持的格式：${Object.values(ACCEPTED_FILE_TYPES).join(', ')}`;
    }

    if (file.size > MAX_FILE_SIZE) {
      return `文件大小超过限制（最大 ${Math.round(MAX_FILE_SIZE / 1024 / 1024)}MB）`;
    }

    return null;
  }, []);

  const uploadFile = useCallback(async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setUploadState(prev => ({
        ...prev,
        error: validationError
      }));
      return;
    }

    setUploadState(prev => ({
      ...prev,
      file,
      uploading: true,
      progress: 0,
      error: null,
      success: false,
      result: null,
    }));

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', `文件转换-${file.name}`);
      formData.append('rule_config', '{}');

      const response = await fetch('/api/v1/transcription/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('上传失败');
      }

      const result = await response.json();
      
      // 上传成功，设置成功状态
      setUploadState(prev => ({
        ...prev,
        uploading: false,
        success: true,
        result
      }));
      
      // 通知父组件上传成功
      onUploadSuccess?.(result);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '上传失败';
      setUploadState(prev => ({
        ...prev,
        uploading: false,
        error: errorMessage
      }));
      onUploadError?.(errorMessage);
    }
  }, [validateFile, onUploadSuccess, onUploadError]);

  const handleFileSelect = (file: File) => {
    uploadFile(file);
  };

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
    <div className={cn("w-full h-full flex flex-col", className)}>
      {uploadState.success ? (
        // 上传成功后显示文本编辑界面
        <div className="h-full flex flex-col">
          <div className="relative border border-input bg-background rounded-lg focus-within:ring-1 focus-within:ring-ring h-full">
            <textarea
              value={inputText}
              onChange={(e) => onInputChange?.(e.target.value)}
              placeholder="请在此处粘贴或输入原始笔录内容..."
              className="h-full w-full min-h-[calc(100%-2px)] resize-none border-0 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 text-sm p-3"
            />
          </div>
        </div>
      ) : (
        // 文件上传区域 - 占满整个容器
        <div
          className={cn(
            "border-2 border-dashed rounded-lg p-6 text-center transition-colors h-full flex flex-col justify-center",
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
                    <span className="text-sm">上传中...</span>
                  </div>
                  <Progress value={uploadState.progress} className="w-full" />
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

              {/* 错误提示 - 内嵌在上传区域内 */}
              {uploadState.error && (
                <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md">
                  <div className="flex items-center gap-2 text-destructive text-sm">
                    <AlertCircle className="h-4 w-4" />
                    <span>{uploadState.error}</span>
                  </div>
                </div>
              )}
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
                支持 .txt、.docx 格式，最大 {Math.round(MAX_FILE_SIZE / 1024 / 1024)}MB
              </p>

              {/* 错误提示 - 内嵌在上传区域内 */}
              {uploadState.error && (
                <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md">
                  <div className="flex items-center gap-2 text-destructive text-sm">
                    <AlertCircle className="h-4 w-4" />
                    <span>{uploadState.error}</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* 隐藏的文件输入 */}
      <input
        type="file"
        ref={fileInputRef}
        className="hidden"
        accept={Object.values(ACCEPTED_FILE_TYPES).join(',')}
        onChange={handleFileInputChange}
      />
    </div>
  );
} 