"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { RiGoogleFill } from "@remixicon/react";
import { LoaderCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";

interface GoogleSignInButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Text to display on the button
   */
  text?: string;
  /**
   * Additional CSS classes
   */
  className?: string;
}

const GoogleSignInButton = React.forwardRef<HTMLButtonElement, GoogleSignInButtonProps>(
  ({ className, text = "使用Google登录", ...props }, ref) => {
    const { signInWithGoogle, loading } = useAuth();
    const [error, setError] = React.useState<string>("");

    const handleGoogleSignIn = async () => {
      setError("");
      
      const { error } = await signInWithGoogle();
      if (error) {
        // 检查是否是OAuth提供商未启用的错误
        if (error.message?.includes('provider is not enabled') || 
            error.message?.includes('validation_failed')) {
          setError("Google登录功能尚未配置，请联系管理员或使用邮箱登录");
        } else {
          setError(error.message || "Google登录失败");
        }
      }
    };

    return (
      <div className="w-full">
        <Button
          ref={ref}
          onClick={handleGoogleSignIn}
          disabled={loading}
          variant="outline"
          className={cn(
            "w-full relative flex items-center justify-center gap-2",
            "border-gray-300 hover:border-gray-400 hover:bg-gray-50",
            "text-gray-700 font-medium",
            "transition-all duration-200",
            className
          )}
          {...props}
        >
          {loading ? (
            <LoaderCircle
              aria-label="Loading"
              className="h-4 w-4 animate-spin"
            />
          ) : (
            <RiGoogleFill className="h-4 w-4" aria-hidden="true" />
          )}
          <span>{loading ? "登录中..." : text}</span>
        </Button>
        
        {error && (
          <div className="mt-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-2">
            {error}
          </div>
        )}
      </div>
    );
  }
);

GoogleSignInButton.displayName = "GoogleSignInButton";

export default GoogleSignInButton; 