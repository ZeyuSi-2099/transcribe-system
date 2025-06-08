# 📝 笔录转换系统

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![React](https://img.shields.io/badge/React-18.2.0-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-15.0.3-black.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![Python](https://img.shields.io/badge/Python-3.11.5-yellow.svg)
![Supabase](https://img.shields.io/badge/Supabase-Backend-green.svg)

> 🎯 **智能化笔录转换工具** - 将访谈对话记录转换为高质量的第一人称叙述文档

## 📖 目录

- [🎯 项目概述](#-项目概述)
- [✨ 核心功能](#-核心功能)
- [🚀 快速开始](#-快速开始)
- [🛠️ 技术栈](#️-技术栈)
- [📊 项目状态](#-项目状态)
- [📚 文档导航](#-文档导航)
- [🤝 贡献指南](#-贡献指南)
- [📄 许可证](#-许可证)

## 🎯 项目概述

本系统是一个专为访谈记录转换设计的智能化工具，结合传统规则引擎与先进的大语言模型(LLM)技术，将访谈对话式笔录高效转换为流畅的第一人称叙述文档。

### 🌟 核心价值
- **智能转换**: 混合处理架构，确保转换准确性和流畅性
- **灵活配置**: 支持自定义规则集和个性化转换策略
- **质量保证**: 完整的检验指标体系和可视化对比
- **用户友好**: 直观的Web界面和完整的操作流程
- **企业级架构**: 基于 Supabase 的现代化后端基础设施

## ✨ 核心功能

### 📁 多格式输入支持
- **文本输入**: 直接粘贴或输入笔录内容
- **文件上传**: 支持 `.txt` 和 `.docx` 格式
- **格式保持**: 严格保持原始文档的换行和格式

### ⚙️ 智能转换引擎
- **混合处理**: 规则引擎 + LLM 双重处理
- **规则配置**: 三级规则结构，灵活配置转换策略
- **实时预览**: 规则配置即时测试和效果预览
- **定制规则**: 基于训练数据生成专属转换规则

### 📊 质量检验体系
- **定量指标**: 字数保留率、原文引用率、实质保持率
- **定性评估**: 视角一致性、主题分类、语义连贯性
- **可视化对比**: 左右对比视图，差异高亮显示
- **指标自定义**: 可调整阈值和权重配置

### 💾 结果管理
- **多格式导出**: 支持 `.txt`、`.docx`格式
- **历史记录**: 完整的转换历史和操作记录
- **批量处理**: 支持多文件同时处理(规划中)

## 🚀 快速开始

### 📋 环境要求
- **Node.js**: 18.0+ 
- **Python**: 3.11+
- **Docker**: 20.10+ (推荐)
- **内存**: 4GB+ (本地LLM需要8GB+)

### 🐳 Docker 快速部署 (推荐)

```bash
# 1. 克隆项目
git clone <repository-url>
cd 笔录转换系统

# 2. 启动所有服务
docker-compose up -d

# 3. 初始化LLM模型 (可选-本地模式)
docker-compose exec ollama ollama pull qwen2.5:7b-instruct

# 4. 访问应用
open http://localhost:3000
```

### 🔧 本地开发环境

**前端启动**:
```bash
cd frontend
npm install
npm run dev
# 访问: http://localhost:3000
```

**后端启动**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# API文档: http://localhost:8000/docs
```

### 🎮 使用步骤

1. **上传笔录**: 选择文本输入或文件上传
2. **配置规则**: 选择或定制转换规则集
3. **开始转换**: 点击转换按钮，等待处理完成
4. **查看结果**: 对比原文和转换结果，查看质量指标
5. **导出文档**: 选择格式下载转换后的文档

## 🛠️ 技术栈

### 前端技术
- **框架**: React 18.2.0 + Next.js 15.0.3 (App Router)
- **语言**: TypeScript 5.0+
- **样式**: Tailwind CSS 3.4+ + shadcn/ui
- **状态管理**: React Context API
- **认证**: Supabase Auth

### 后端技术
- **框架**: FastAPI 0.104.1
- **语言**: Python 3.11.5
- **数据库**: Supabase (PostgreSQL)
- **认证**: Supabase Auth
- **实时功能**: Supabase Realtime
- **文件存储**: Supabase Storage
- **缓存**: Redis 7+ (可选)
- **ORM**: supabase-py

### AI & LLM 集成
- **云端方案**: Deepseek API (推荐)
- **本地方案**: Ollama + Qwen2.5-7B-Instruct
- **备选**: OpenAI GPT系列、Hugging Face Transformers

### 开发工具
- **BaaS平台**: Supabase (数据库、认证、存储、实时功能)
- **容器化**: Docker + Docker Compose
- **代码质量**: ESLint + Prettier (前端) + Ruff (后端)
- **测试**: Jest + Playwright (E2E)
- **版本控制**: Git + 传统分支策略

## 🚀 开发计划

### 📋 总体规划
项目采用敏捷开发模式，分为5个主要阶段，预计总开发周期 **3-4个月**，每个阶段都有明确的交付目标和可演示功能。

---

### 🎯 阶段一：基础架构搭建 (2-3周)
**版本目标**: `v0.1.0-alpha` - MVP核心功能

#### 📌 主要任务
- **前端基础**: Next.js项目初始化，基础路由和布局设计
- **后端基础**: FastAPI项目初始化，基础API架构搭建
- **数据库**: SQLite开发环境配置，核心数据模型设计
- **LLM集成**: Deepseek API集成，基础调用接口实现
- **基础UI**: 文本输入区域、转换按钮、结果显示界面

#### ✅ 交付标准
- [ ] 能够进行基础的文本输入和转换
- [ ] 有简洁可用的Web界面
- [ ] LLM调用功能正常
- [ ] 基础的前后端通信建立

---

### ⚙️ 阶段二：核心转换功能 (3-4周)
**版本目标**: `v0.2.0-alpha` - 完整转换流程

#### 📌 主要任务
- **文件处理**: 支持 `.txt` 和 `.docx` 格式文件上传
- **规则引擎**: 设计和实现转换规则配置系统
- **混合处理**: 规则引擎 + LLM 的混合处理架构
- **API完善**: 完整的文件上传、转换、下载API接口
- **前端集成**: 文件上传UI、转换进度显示、结果预览

#### ✅ 交付标准
- [ ] 支持多种格式文件上传和处理
- [ ] 规则配置功能可用
- [ ] 转换质量达到基本要求
- [ ] 完整的转换工作流程

---

### 📊 阶段三：质量检验系统 (2-3周)
**版本目标**: `v0.3.0-beta` - 质量保证体系

#### 📌 主要任务
- **检验指标**: 实现字数保留率、原文引用率、实质保持率计算
- **对比界面**: 左右对比视图，差异高亮显示功能
- **可视化**: 转换质量指标的图表和统计展示
- **用户反馈**: 转换结果评价和改进建议机制
- **界面优化**: 用户体验改进和交互流程优化

#### ✅ 交付标准
- [ ] 完整的质量评估指标体系
- [ ] 直观的转换结果对比界面
- [ ] 用户友好的操作体验
- [ ] 转换质量可量化评估

---

### 🔧 阶段四：高级功能完善 (3-4周)
**版本目标**: `v1.0.0-rc` - 功能完整版本

#### 📌 主要任务
- **用户系统**: 基于 Supabase Auth 的用户注册、登录、个人中心功能
- **历史记录**: 使用 Supabase 数据库的转换历史存储、查询、管理功能
- **批量处理**: 利用 Supabase Realtime 的多文件同时处理和批量转换
- **性能优化**: Supabase 缓存机制、异步处理、响应速度优化
- **数据管理**: 基于 Supabase Storage 的个人数据导入导出、设置同步
- **实时体验**: Supabase Realtime 实现转换进度实时更新

#### ✅ 交付标准
- [ ] 基于 Supabase Auth 的完整用户认证和授权系统
- [ ] 使用 PostgreSQL 的转换历史记录功能完善
- [ ] 支持批量文件处理和实时进度显示
- [ ] 系统性能满足生产要求
- [ ] Supabase 集成完成，提供企业级稳定性

#### 🔄 Supabase 迁移计划
1. **环境设置** (1-2天): 创建 Supabase 项目，配置环境变量
2. **数据库迁移** (2-3天): 设计 schema，迁移现有数据，配置 RLS
3. **后端集成** (3-4天): 集成 supabase-py，替换现有数据库操作
4. **前端集成** (2-3天): 集成 Supabase Auth 和 Realtime
5. **高级功能** (剩余时间): 批量处理、性能优化、数据管理

---

### 🚀 阶段五：部署运维 (1-2周)
**版本目标**: `v1.0.0` - 生产就绪版本

#### 📌 主要任务
- **容器化**: 完整的Docker化部署方案
- **生产环境**: PostgreSQL、Redis等生产级服务配置
- **监控系统**: 应用监控、日志收集、性能追踪
- **安全加固**: 数据加密、访问控制、安全审计
- **文档完善**: 用户手册、API文档、运维指南

#### ✅ 交付标准
- [ ] 生产环境稳定部署
- [ ] 完整的监控和日志系统
- [ ] 安全性达到生产标准
- [ ] 文档齐全，用户可自助使用

---

### 📈 里程碑时间线

```
Week 1-3    │ 阶段一：基础架构搭建 ✅
Week 4-7    │ 阶段二：核心转换功能 ✅
Week 8-10   │ 阶段三：质量检验系统 ✅
Week 11-14  │ 阶段四：高级功能完善 + Supabase集成 🔄
Week 15-16  │ 阶段五：部署运维
```

### 🎯 当前状态
- **当前阶段**: 阶段四进行中 🔄 - Supabase 集成开发
- **下一里程碑**: v1.0.0-rc (预计3周后)
- **项目进度**: 75% (前三阶段完成，正在进行 Supabase 集成)

## 📚 文档导航

### 📖 详细文档
- **[🏗️ 技术架构](README_architecture.md)** - 详细技术栈、架构设计、安全策略
- **[👤 用户指南](README_user_guide.md)** - 完整用户流程、界面设计、功能说明
- **[💻 开发指南](README_development.md)** - 项目结构、开发环境、代码规范、测试策略
- **[🚀 部署指南](README_deployment.md)** - Docker部署、云服务部署、监控配置

---

## 🙏 致谢

感谢以下开源项目和社区的支持：
- [React](https://reactjs.org/) & [Next.js](https://nextjs.org/) - 现代化前端框架
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Python Web框架
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的CSS框架
- [shadcn/ui](https://ui.shadcn.com/) - 精美的React组件库
- [Ollama](https://ollama.ai/) - 本地LLM运行平台

---

<div align="center">

**Made with ❤️ for better interview transcription**

[![Stars](https://img.shields.io/github/stars/your-repo/transcribe-system?style=social)](https://github.com/your-repo/transcribe-system)
[![Forks](https://img.shields.io/github/forks/your-repo/transcribe-system?style=social)](https://github.com/your-repo/transcribe-system)
[![Contributors](https://img.shields.io/github/contributors/your-repo/transcribe-system)](https://github.com/your-repo/transcribe-system/graphs/contributors)

</div>