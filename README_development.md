# 开发指南

## 💻 项目结构

### 前端项目结构
```
frontend/
├── app/                    # Next.js App Router 结构
│   ├── (auth)/            # 认证相关路由组
│   │   ├── login/
│   │   └── register/
│   ├── dashboard/         # 主应用界面
│   ├── rules/            # 规则配置界面
│   ├── result/           # 结果展示界面
│   ├── history/          # 历史记录界面
│   ├── profile/          # 用户个人中心
│   ├── globals.css       # 全局样式
│   ├── layout.tsx        # 根布局组件
│   └── page.tsx          # 首页组件
├── components/            # 可复用组件
│   ├── ui/               # 基础UI组件 (shadcn/ui)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   └── ...
│   ├── layout/           # 布局相关组件
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   └── navigation.tsx
│   ├── auth/             # 认证相关组件
│   │   ├── login-form.tsx
│   │   ├── register-form.tsx
│   │   ├── auth-provider.tsx
│   │   └── protected-route.tsx
│   ├── forms/            # 表单组件
│   │   ├── upload-form.tsx
│   │   ├── rule-config-form.tsx
│   │   └── batch-process-form.tsx
│   ├── features/         # 功能特定组件
│   │   ├── text-upload/
│   │   ├── rule-manager/
│   │   ├── result-viewer/
│   │   ├── history/
│   │   ├── batch-processor/
│   │   └── realtime-status/
│   └── common/           # 通用组件
│       ├── loading.tsx
│       ├── error-boundary.tsx
│       └── modal.tsx
├── lib/                  # 工具库和配置
│   ├── utils.ts          # 通用工具函数
│   ├── supabase/         # Supabase 相关配置
│   │   ├── client.ts     # 客户端配置
│   │   ├── server.ts     # 服务端配置
│   │   └── middleware.ts # 中间件配置
│   ├── api.ts            # API 客户端 (兼容 FastAPI)
│   ├── auth.ts           # 认证相关 (Supabase Auth)
│   ├── constants.ts      # 常量定义
│   └── types.ts          # TypeScript 类型定义
├── hooks/                # 自定义 React Hooks
│   ├── useAuth.ts        # Supabase Auth hooks
│   ├── useSupabase.ts    # Supabase 数据 hooks
│   ├── useRealtime.ts    # 实时功能 hooks
│   ├── useUpload.ts      # 文件上传 hooks
│   ├── useRules.ts       # 规则管理 hooks
│   └── useHistory.ts     # 历史记录 hooks
├── contexts/             # React Context
│   ├── AuthContext.tsx   # 认证上下文 (Supabase)
│   ├── RulesContext.tsx
│   └── ThemeContext.tsx
├── public/               # 静态资源
│   ├── images/
│   └── icons/
├── styles/               # 样式文件
│   └── components/       # 组件专用样式
├── __tests__/            # 测试文件
│   ├── components/
│   ├── pages/
│   └── utils/
├── .env.example          # 环境变量示例
├── .env.local.example    # 本地环境变量示例
├── next.config.js        # Next.js 配置
├── tailwind.config.js    # Tailwind CSS 配置
├── tsconfig.json         # TypeScript 配置
└── package.json          # 依赖管理
```

### 后端项目结构
```
backend/
├── app/                  # FastAPI 应用主体
│   ├── api/             # API 路由
│   │   ├── v1/          # API 版本 1
│   │   │   ├── auth.py      # 认证相关API (Supabase Auth 集成)
│   │   │   ├── upload.py    # 文件上传API (Supabase Storage)
│   │   │   ├── rules.py     # 规则管理API
│   │   │   ├── transform.py # 转换处理API
│   │   │   ├── history.py   # 历史记录API
│   │   │   ├── batch.py     # 批量处理API
│   │   │   └── realtime.py  # 实时功能API
│   │   └── deps.py      # API 依赖项 (Supabase 客户端)
│   ├── core/            # 核心功能模块
│   │   ├── config.py    # 配置管理 (包含 Supabase 配置)
│   │   ├── security.py  # 安全相关 (Supabase Auth 集成)
│   │   ├── supabase.py  # Supabase 客户端配置
│   │   └── exceptions.py # 异常处理
│   ├── models/          # 数据模型 (Supabase Schema)
│   │   ├── user.py      # 用户模型
│   │   ├── rule.py      # 规则模型
│   │   ├── transform.py # 转换记录模型
│   │   ├── batch.py     # 批量任务模型
│   │   └── history.py   # 历史记录模型
│   ├── schemas/         # Pydantic 数据校验
│   │   ├── user.py      # 用户数据校验
│   │   ├── rule.py      # 规则数据校验
│   │   ├── transform.py # 转换数据校验
│   │   ├── batch.py     # 批量处理数据校验
│   │   └── common.py    # 通用数据校验
│   ├── services/        # 业务逻辑服务
│   │   ├── auth_service.py      # 认证服务 (Supabase Auth)
│   │   ├── file_service.py      # 文件服务 (Supabase Storage)
│   │   ├── rule_service.py      # 规则服务
│   │   ├── transform_service.py # 转换服务
│   │   ├── batch_service.py     # 批量处理服务
│   │   ├── realtime_service.py  # 实时服务
│   │   └── llm_service.py       # LLM 服务
│   ├── transformers/    # 转换引擎
│   │   ├── base.py      # 基础转换器
│   │   ├── rule_engine.py   # 规则引擎
│   │   ├── llm_engine.py    # LLM 处理引擎
│   │   ├── preprocessor.py  # 预处理器
│   │   └── postprocessor.py # 后处理器
│   ├── utils/           # 工具函数
│   │   ├── supabase.py  # Supabase 工具函数
│   │   ├── file_utils.py
│   │   ├── text_utils.py
│   │   ├── validation.py
│   │   └── metrics.py
│   └── main.py          # FastAPI 应用入口
├── supabase/            # Supabase 配置和迁移
│   ├── migrations/      # 数据库迁移文件
│   ├── functions/       # Edge Functions (可选)
│   ├── config.toml      # Supabase 项目配置
│   └── seed.sql         # 初始数据
├── tests/               # 测试文件
│   ├── api/
│   ├── services/
│   ├── transformers/
│   └── conftest.py
├── requirements.txt     # Python 依赖
├── pyproject.toml       # Poetry 配置
├── .env.example         # 环境变量示例
└── Dockerfile           # Docker 配置
```

## 🚀 开发环境设置

### 前端开发环境
```bash
# 1. 克隆项目
git clone <repository-url>
cd frontend

# 2. 安装依赖
npm install

# 3. 安装 Supabase 相关依赖
npm install @supabase/supabase-js @supabase/auth-helpers-nextjs @supabase/ssr

# 4. 配置环境变量
cp .env.example .env.local
# 编辑 .env.local 配置 Supabase 相关变量:
# NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
# NEXT_PUBLIC_API_URL=http://localhost:8000

# 5. 启动开发服务器
npm run dev

# 6. 构建生产版本
npm run build

# 7. 启动生产服务器
npm start
```

### 后端开发环境
```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt
# 或使用 Poetry
poetry install

# 4. 安装 Supabase Python 客户端
pip install supabase

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 配置 Supabase 和其他服务:
# SUPABASE_URL=your-supabase-url
# SUPABASE_KEY=your-supabase-service-role-key
# SUPABASE_JWT_SECRET=your-jwt-secret
# DATABASE_URL=postgresql://...  # Supabase 数据库连接
# LLM_PROVIDER=deepseek
# DEEPSEEK_API_KEY=your-deepseek-key

# 6. 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Supabase 环境设置

#### 1. 创建 Supabase 项目
```bash
# 安装 Supabase CLI
npm install -g @supabase/cli

# 登录 Supabase
supabase login

# 初始化项目
supabase init

# 启动本地开发环境
supabase start

# 链接到远程项目
supabase link --project-ref your-project-id
```

#### 2. 数据库初始化
```bash
# 创建数据库表结构
supabase migration new create_initial_schema

# 编辑迁移文件 (supabase/migrations/xxx_create_initial_schema.sql)
# 添加之前在架构文档中定义的表结构

# 应用迁移
supabase db push

# 生成 TypeScript 类型
supabase gen types typescript --local > types/supabase.ts
```

#### 3. 认证配置
```bash
# 在 Supabase Dashboard 中配置:
# 1. 启用邮箱认证
# 2. 配置 OAuth 提供商 (可选)
# 3. 设置认证重定向 URL
# 4. 配置邮件模板
```

#### 4. 存储配置
```bash
# 在 Supabase Dashboard 中创建存储桶:
# 1. 创建 "uploads" 桶用于原始文件
# 2. 创建 "results" 桶用于转换结果
# 3. 配置访问策略
```

#### 5. 实时功能配置
```bash
# 在 Supabase Dashboard 中:
# 1. 启用 Realtime
# 2. 配置表级实时订阅
# 3. 设置 RLS 策略
```

### 环境变量配置

#### 前端环境变量 (.env.local)
```bash
# Supabase 配置
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key

# 后端 API
NEXT_PUBLIC_API_URL=http://localhost:8000

# 应用配置
NEXT_PUBLIC_APP_NAME=笔录转换系统
NEXT_PUBLIC_APP_VERSION=1.0.0
```

#### 后端环境变量 (.env)
```bash
# Supabase 配置
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# 数据库配置 (可选，直接使用 Supabase)
DATABASE_URL=postgresql://postgres:[password]@[host]:5432/[database]

# LLM 配置
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 本地 LLM 配置 (可选)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct

# Redis 配置 (可选)
REDIS_URL=redis://localhost:6379

# 应用配置
APP_NAME=笔录转换系统
APP_VERSION=1.0.0
DEBUG=true
```

### 本地 LLM 环境设置 (可选)
```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. 下载推荐模型
ollama pull qwen2.5:7b-instruct

# 3. 启动 Ollama 服务
ollama serve

# 4. 在后端配置中启用本地模式
# .env 文件中设置:
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b-instruct
OLLAMA_BASE_URL=http://localhost:11434
```

### 开发工作流程

#### 1. 数据库开发
```bash
# 修改数据库结构
supabase migration new your_migration_name

# 编辑迁移文件
# supabase/migrations/xxx_your_migration_name.sql

# 本地测试迁移
supabase db push

# 生成新的类型定义
supabase gen types typescript --local > types/supabase.ts
```

#### 2. 前端开发
```bash
# 启动开发服务器
npm run dev

# 类型检查
npm run type-check

# 代码格式化
npm run format

# 运行测试
npm run test
```

#### 3. 后端开发
```bash
# 启动开发服务器
uvicorn app.main:app --reload

# 运行测试
pytest

# 代码格式化
ruff format .

# 类型检查
mypy .
```

### 调试和测试

#### 前端调试
```bash
# 启动开发服务器
npm run dev

# 在浏览器中访问 http://localhost:3000
# 使用浏览器开发者工具进行调试

# Supabase 客户端调试
console.log(supabase.auth.getUser())
console.log(supabase.from('conversion_history').select('*'))
```

#### 后端调试
```bash
# 启动开发服务器 (带调试)
uvicorn app.main:app --reload --log-level debug

# 访问 API 文档
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)

# Supabase 连接测试
python -c "
from app.core.supabase import get_supabase_client
client = get_supabase_client()
result = client.table('user_profiles').select('*').execute()
print(result.data)
"
```

#### 数据库调试
```bash
# 连接到本地 Supabase 数据库
supabase db connect

# 或者直接使用 psql
psql postgresql://postgres:postgres@localhost:54322/postgres

# 查看表结构
\dt
\d conversion_history
```

### 常见问题解决

#### Supabase 连接问题
```bash
# 检查 Supabase 项目状态
supabase status

# 重新启动本地 Supabase
supabase stop
supabase start

# 检查环境变量
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

#### 认证问题
```bash
# 检查 JWT 配置
# 确保前后端使用相同的 JWT 密钥

# 检查 RLS 策略
# 在 Supabase Dashboard 中查看行级安全策略

# 调试认证流程
# 在浏览器开发者工具中查看网络请求
```

#### 实时功能问题
```bash
# 检查 WebSocket 连接
# 在浏览器开发者工具的网络面板中查看 WS 连接

# 检查实时订阅
# 确保表启用了 Realtime
# 检查 RLS 策略是否影响实时更新
```

## 📋 代码规范

### TypeScript/JavaScript 规范 (前端)
```json
// .eslintrc.json
{
  "extends": [
    "next/core-web-vitals",
    "@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "prefer-const": "error",
    "no-var": "error"
  }
}
```

**命名规范**:
- **组件**: PascalCase (例: `UploadForm.tsx`)
- **函数/变量**: camelCase (例: `getUserData`)
- **常量**: SCREAMING_SNAKE_CASE (例: `API_BASE_URL`)
- **文件**: kebab-case 或 camelCase
- **类型/接口**: PascalCase (例: `UserProfile`)

**组件编写规范**:
```typescript
// 优秀的组件结构示例
interface Props {
  title: string;
  onSubmit: (data: FormData) => void;
  isLoading?: boolean;
}

export const UploadForm: React.FC<Props> = ({ 
  title, 
  onSubmit, 
  isLoading = false 
}) => {
  // Hooks 声明
  const [file, setFile] = useState<File | null>(null);
  
  // 事件处理函数
  const handleSubmit = useCallback((e: FormEvent) => {
    e.preventDefault();
    if (file) {
      onSubmit(new FormData());
    }
  }, [file, onSubmit]);

  // 渲染
  return (
    <form onSubmit={handleSubmit}>
      {/* JSX 内容 */}
    </form>
  );
};
```

### Python 代码规范 (后端)
```toml
# pyproject.toml - Ruff 配置
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "C90", "I", "N", "D", "UP", "B", "A", "S", "T20", "Q"]
ignore = ["D100", "D101", "D102", "D103", "D104", "D105"]

[tool.ruff.lint.pydocstyle]
convention = "google"
```

**命名规范**:
- **函数/变量**: snake_case (例: `get_user_data`)
- **类**: PascalCase (例: `UserService`)
- **常量**: SCREAMING_SNAKE_CASE (例: `API_KEY`)
- **私有方法**: 前缀下划线 (例: `_validate_input`)
- **模块**: snake_case (例: `user_service.py`)

**函数编写规范**:
```python
from typing import Optional, List
from pydantic import BaseModel

async def transform_text(
    text: str,
    rules: List[str],
    llm_provider: Optional[str] = None
) -> dict[str, any]:
    """
    转换文本内容基于指定规则.
    
    Args:
        text: 待转换的文本内容
        rules: 应用的规则列表
        llm_provider: LLM提供商，None时使用默认配置
        
    Returns:
        包含转换结果和元数据的字典
        
    Raises:
        ValidationError: 当输入参数无效时
        TransformError: 当转换过程失败时
    """
    # 实现逻辑...
    pass
```

## 🧪 测试策略

### 前端测试
```bash
# 安装测试依赖
npm install --save-dev @testing-library/react @testing-library/jest-dom jest-environment-jsdom

# 运行测试
npm run test        # 单次运行
npm run test:watch  # 监听模式
npm run test:coverage  # 覆盖率报告
```

**组件测试示例**:
```typescript
// __tests__/components/UploadForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { UploadForm } from '@/components/forms/UploadForm';

describe('UploadForm', () => {
  it('应该正确渲染上传表单', () => {
    const mockOnSubmit = jest.fn();
    
    render(
      <UploadForm 
        title="测试标题" 
        onSubmit={mockOnSubmit} 
      />
    );
    
    expect(screen.getByText('测试标题')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /上传/i })).toBeInTheDocument();
  });

  it('应该在文件选择后启用提交按钮', async () => {
    const mockOnSubmit = jest.fn();
    
    render(
      <UploadForm 
        title="测试标题" 
        onSubmit={mockOnSubmit} 
      />
    );
    
    const fileInput = screen.getByRole('input', { hidden: true });
    const file = new File(['测试内容'], 'test.txt', { type: 'text/plain' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    const submitButton = screen.getByRole('button', { name: /上传/i });
    expect(submitButton).not.toBeDisabled();
  });
});
```

### 后端测试
```bash
# 运行测试
pytest                    # 运行所有测试
pytest --cov=app         # 生成覆盖率报告
pytest -v tests/api/     # 运行特定目录测试
pytest -k "test_upload"  # 运行特定测试
```

**API测试示例**:
```python
# tests/api/test_upload.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestUploadAPI:
    """文件上传API测试"""
    
    def test_upload_text_file_success(self):
        """测试文本文件上传成功"""
        test_content = "测试用户: 这是一段测试对话\n访谈者: 好的，继续"
        
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.txt", test_content, "text/plain")},
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "file_id" in data
        assert data["content_preview"].startswith("测试用户:")

    def test_upload_invalid_file_format(self):
        """测试无效文件格式上传"""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.pdf", b"invalid content", "application/pdf")},
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 400
        assert "不支持的文件格式" in response.json()["detail"]
        
    def test_upload_without_auth(self):
        """测试未认证上传"""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.txt", "content", "text/plain")}
        )
        
        assert response.status_code == 401
```

**服务层测试示例**:
```python
# tests/services/test_transform_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.transform_service import TransformService

class TestTransformService:
    """转换服务测试"""
    
    @pytest.fixture
    def transform_service(self):
        return TransformService()
    
    @patch('app.services.transform_service.LLMService')
    async def test_transform_text_with_llm(self, mock_llm, transform_service):
        """测试使用LLM的文本转换"""
        # 模拟LLM响应
        mock_llm.return_value.process_text.return_value = "转换后的文本"
        
        result = await transform_service.transform_text(
            text="原始文本",
            rules=["rule1", "rule2"],
            use_llm=True
        )
        
        assert result["transformed_text"] == "转换后的文本"
        assert result["rules_applied"] == ["rule1", "rule2"]
        mock_llm.return_value.process_text.assert_called_once()
```

### E2E 测试 (Playwright)
```bash
# 安装 Playwright
npm install --save-dev @playwright/test

# 安装浏览器
npx playwright install

# 运行 E2E 测试
npm run test:e2e
npx playwright test --ui  # 带UI的测试运行器
```

**E2E测试示例**:
```typescript
// tests/e2e/upload-workflow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('文件上传工作流', () => {
  test('完整的文件上传和转换流程', async ({ page }) => {
    // 1. 登录
    await page.goto('/login');
    await page.fill('[data-testid=email]', 'test@example.com');
    await page.fill('[data-testid=password]', 'password');
    await page.click('[data-testid=login-button]');
    
    // 2. 上传文件
    await page.goto('/dashboard');
    await page.setInputFiles('[data-testid=file-input]', 'test-data/sample.txt');
    
    // 3. 等待文件处理
    await expect(page.locator('[data-testid=file-preview]')).toBeVisible();
    
    // 4. 配置规则
    await page.click('[data-testid=rules-tab]');
    await page.check('[data-testid=rule-language-optimization]');
    
    // 5. 开始转换
    await page.click('[data-testid=transform-button]');
    
    // 6. 验证结果
    await expect(page.locator('[data-testid=transform-result]')).toBeVisible();
    await expect(page.locator('[data-testid=metrics-card]')).toBeVisible();
    
    // 7. 下载结果
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid=download-button]');
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/^转换后笔录_\d+\.txt$/);
  });
});
```

## 🛠️ 开发工具配置

### VS Code 推荐设置
```json
// .vscode/settings.json
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "files.associations": {
    "*.css": "tailwindcss"
  },
  "tailwindCSS.includeLanguages": {
    "typescript": "javascript",
    "typescriptreact": "javascript"
  }
}
```

### Git 钩子配置
```bash
# 安装 husky
npm install --save-dev husky lint-staged

# 配置 pre-commit 钩子
npx husky add .husky/pre-commit "npx lint-staged"
```

```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{py}": [
      "ruff format",
      "ruff check --fix"
    ]
  }
}
```

## 📅 开发计划

我们的开发工作将分为以下几个阶段进行：

### 阶段一（已完成 ✅）：基础架构搭建

**目标版本**: v0.1.0-alpha

**时间安排**: 预计 2-3 周

**任务清单**:

- [x] 后端：FastAPI 应用骨架搭建
- [x] 后端：SQLModel 集成和基本数据模型 (Transcription)
- [x] 后端：数据库连接配置 (SQLite for dev)
- [x] 后端：Deepseek API 集成服务封装
- [x] 后端：实现基本的笔录创建和存储 API 端点
- [x] 前端：Next.js 项目初始化 (TypeScript, Tailwind CSS)
- [x] 前端：集成 shadcn/ui 组件库
- [x] 前端：搭建基础转换界面 (输入框, 输出框, 按钮)
- [x] 前端：实现前端与后端 API 的基本通信
- [x] 前端：实现基本的转换触发和结果显示逻辑
- [x] 环境：Python 虚拟环境设置和依赖管理
- [x] 环境：API 密钥等环境变量配置 (.env)
- [x] 验证：基本功能端到端测试（前端 -> 后端 -> LLM -> 后端 -> 前端）
- [x] 文档：更新开发指南中项目结构、环境设置部分

**交付标准**:

- 项目基础结构搭建完成
- 前后端服务可独立或协同启动运行
- 用户界面可以输入文本并触发转换请求
- 后端能接收请求、调用 LLM 服务（Deepseek API）、存储记录，并返回结果
- 经过手动测试验证核心转换流程的可用性

### 阶段二（预计 3-4 周）：核心转换功能深化

**目标版本**: v0.2.0-alpha

**任务清单**:

- [ ] 后端：优化 LLM 提示词和转换逻辑
- [ ] 后端：实现更复杂的规则处理引擎
- [ ] 后端：引入更多可配置的转换规则选项
- [ ] 后端：实现质量检验指标计算
- [ ] 后端：增加批量转换 API 支持
- [ ] 后端：完善错误处理和日志记录
- [ ] 前端：优化用户界面，提升交互体验
- [ ] 前端：添加规则配置界面和功能
- [ ] 前端：优化转换结果展示和格式化
- [ ] 前端：实现历史记录查看功能
- [ ] 测试：编写自动化单元测试和集成测试
- [ ] 文档：更新转换规则、质量指标、API 文档

**交付标准**:

- 转换准确性和鲁棒性显著提升
- 支持多种转换规则配置
- 能够计算并展示转换质量指标
- 支持批量上传和处理笔录
- 核心业务逻辑有测试覆盖

### 阶段三（预计 2-3 周）：质量检验与优化

**目标版本**: v0.3.0-beta

**任务清单**:

- [ ] 后端：完善质量检验指标体系和计算方法
- [ ] 后端：实现人工校对结果的反馈机制
- [ ] 后端：优化 LLM 微调或 Re-ranking 策略
- [ ] 前端：开发质量检验结果展示界面
- [ ] 前端：实现人工校对和编辑功能
- [ ] 前端：增加用户反馈渠道
- [ ] 测试：增加性能测试和稳定性测试
- [ ] 文档：编写质量检验流程和标准文档

**交付标准**:

- 转换质量达到可接受水平 (基于质量指标)
- 用户可以方便地查看和修改转换结果
- 建立数据反馈循环以持续优化模型
- 系统性能和稳定性满足基本要求

### 阶段四（预计 3-4 周）：高级功能与用户体验完善

**目标版本**: v1.0.0-rc

**任务清单**:

- [ ] 后端：实现用户认证和授权
- [ ] 后端：支持多用户、多规则集管理
- [ ] 后端：集成其他 LLM 提供商 (可选)
- [ ] 前端：实现用户注册、登录、个人中心
- [ ] 前端：完善规则管理界面，支持导入导出
- [ ] 前端：优化整体 UI/UX 设计，提升用户体验
- [ ] 前端：添加引导教程和帮助文档入口
- [ ] 测试：进行全面的端到端用户场景测试
- [ ] 文档：完善用户指南和部署手册

**交付标准**:

- 支持用户管理和数据隔离
- 功能完善，满足大部分用户需求
- 用户界面友好，操作流畅
- 系统具备生产环境运行的基本条件

### 阶段五（预计 1-2 周）：部署与运维准备

**目标版本**: v1.0.0 正式发布

**任务清单**:

- [ ] 后端：编写 Dockerfile 和容器化配置
- [ ] 后端：准备生产环境数据库迁移脚本
- [ ] 后端：设置日志监控和报警
- [ ] 环境：编写部署指南 (Docker, Kubernetes 或云服务)
- [ ] 环境：准备生产环境配置模板
- [ ] 环境：安全加固和性能调优
- [ ] 测试：进行生产环境模拟测试

**交付标准**:

- 项目可在生产环境中稳定可靠运行
- 具备基本的运维和监控能力
- 发布 v1.0.0 正式版本

---

更多信息请参考：
- [技术架构](README_architecture.md)
- [用户指南](README_user_guide.md)
- [部署指南](README_deployment.md) 