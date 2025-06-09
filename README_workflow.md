# 开发和部署工作流程

## 🔄 日常开发工作流程

### 1. 本地开发环境启动

#### 前端开发
```bash
# 进入前端目录
cd frontend

# 安装依赖（仅首次或package.json更新时）
npm install

# 启动开发服务器
npm run dev

# 浏览器访问: http://localhost:3000
```

#### 后端开发
```bash
# 进入后端目录
cd backend

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖（仅首次或requirements.txt更新时）
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API访问: http://localhost:8000
```

### 2. 代码修改和测试

#### 修改代码
- 在相应的目录中修改代码（frontend/ 或 backend/）
- 开发服务器会自动重载变更

#### 本地测试
- 确保前后端服务都正常运行
- 测试所有修改的功能
- 检查控制台是否有错误

### 3. 提交代码到GitHub

#### 检查代码状态
```bash
# 查看修改的文件
git status

# 查看具体修改内容
git diff
```

#### 提交到本地仓库
```bash
# 添加修改的文件
git add .

# 或者选择性添加文件
git add frontend/src/components/NewComponent.tsx
git add backend/app/api/new_endpoint.py

# 提交修改（使用有意义的提交信息）
git commit -m "feat: 添加新功能 - 具体描述"
# 或
git commit -m "fix: 修复XX问题"
# 或  
git commit -m "docs: 更新文档"
```

#### 推送到GitHub
```bash
# 推送到部署分支
git push origin deploy-main
```

## 🚀 自动部署流程

### 当您推送代码到GitHub后，自动发生：

#### 1. Vercel前端自动部署
- **触发条件**: 推送到 `deploy-main` 分支
- **部署流程**:
  1. Vercel检测到代码变更
  2. 自动拉取最新代码
  3. 安装依赖 (`npm install`)
  4. 构建项目 (`npm run build`)  
  5. 部署到生产环境
  6. 更新域名 https://www.transcribe.solutions

#### 2. Render后端自动部署
- **触发条件**: 推送到 `deploy-main` 分支
- **部署流程**:
  1. Render检测到代码变更
  2. 自动拉取最新代码
  3. 安装依赖 (`pip install -r requirements.txt`)
  4. 启动新的服务实例
  5. 更新API服务 https://transcribe-system.onrender.com

### 部署状态监控

#### Vercel部署状态
1. 访问: https://vercel.com/zeyusis-projects-5051a650/transcribe-solution-app
2. 点击 "Deployments" 标签
3. 查看最新部署状态:
   - 🟡 "Building" - 正在构建
   - 🟢 "Ready" - 部署成功
   - 🔴 "Failed" - 部署失败

#### Render部署状态
1. 访问Render控制台
2. 查看服务状态和部署日志

## 🛠️ 常见问题处理

### 前端部署失败
```bash
# 1. 检查本地构建是否成功
cd frontend
npm run build

# 2. 检查ESLint错误
npm run lint

# 3. 如果有TypeScript错误
npm run type-check  # 如果有这个脚本
```

### 后端部署失败
```bash
# 1. 检查依赖是否正确
cd backend
pip install -r requirements.txt

# 2. 本地测试启动
uvicorn app.main:app --reload

# 3. 检查环境变量配置
```

### 部署成功但功能异常
1. **检查环境变量**: 确保Vercel和Render中的环境变量配置正确
2. **检查API连接**: 确保前端的 `NEXT_PUBLIC_API_URL` 指向正确的后端地址
3. **查看日志**: 在Vercel和Render控制台查看运行时日志

## 📝 提交信息规范

### 提交类型
- `feat`: 新功能
- `fix`: 修复bug  
- `docs`: 文档修改
- `style`: 代码格式修改
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建或工具修改

### 提交信息格式
```
<类型>: <简短描述>

[可选的详细描述]

[可选的相关issue]
```

### 示例
```bash
git commit -m "feat: 添加文件上传进度显示功能"

git commit -m "fix: 修复规则配置保存失败的问题

- 修复了API调用时的参数格式错误
- 添加了错误处理和用户提示
- 相关issue: #123"
```

## 🔄 完整的开发到部署流程示例

### 场景：添加新功能

```bash
# 1. 本地开发
cd frontend
npm run dev  # 启动前端

# 新开终端
cd backend  
uvicorn app.main:app --reload  # 启动后端

# 2. 修改代码
# 编辑相关文件...

# 3. 本地测试
# 在浏览器中测试新功能

# 4. 提交代码
git add .
git commit -m "feat: 添加新的转换规则选项"
git push origin deploy-main

# 5. 监控部署
# 查看Vercel和Render的部署状态

# 6. 验证生产环境
# 访问 https://www.transcribe.solutions 测试新功能
```

### 场景：修复bug

```bash
# 1. 本地复现问题
# 在本地环境重现bug

# 2. 修复代码
# 编辑相关文件修复问题

# 3. 本地验证修复
# 确保问题已解决

# 4. 提交修复
git add .
git commit -m "fix: 修复文件上传时的编码问题"
git push origin deploy-main

# 5. 生产环境验证
# 部署完成后在生产环境验证修复
```

## 💡 最佳实践

### 开发建议
1. **小步提交**: 频繁提交小的、逻辑完整的修改
2. **测试驱动**: 修改后先在本地充分测试
3. **代码审查**: 重要修改可以创建Pull Request进行代码审查
4. **备份重要修改**: 重大修改前创建分支备份

### 部署建议
1. **监控部署状态**: 每次推送后检查部署是否成功
2. **生产环境验证**: 部署成功后立即测试关键功能
3. **回滚准备**: 如有问题，准备快速回滚到上一个稳定版本

### 环境变量管理
1. **敏感信息安全**: 不要在代码中硬编码API密钥等敏感信息
2. **环境一致性**: 确保各环境的配置正确对应
3. **定期检查**: 定期检查环境变量是否过期或需要更新 