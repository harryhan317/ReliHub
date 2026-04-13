# ReliHub - 电子产品可靠性领域专业 AI 社区

ReliHub 是一个面向电子产品可靠性技术人员的一站式解决方案平台。它结合了先进的 LLM 技术 (ReliBot) 与社区共享生态，旨在提升行业问题的解决效率。

---

## 🚀 快速导航

- **📄 [项目文档 (docs)](./docs/)**：包含全量 PRD、技术架构方案、测试文档。
- **📌 [需求输入基线 (V2.2)](./docs/01_产品需求/ReliHub%20产品需求输入文件%20V2.2.md)**：项目原始需求输入文件。
- **⚙️ [后端代码 (backend)](./backend/)**：基于 FastAPI 的高性能异步 API。
- **📱 [前端代码](./docs/06_前端UI设计/)**：UI/UX 设计文档（前端代码开发中）。

---

## 🏗️ 项目架构简介

- **Web 前端**: React 18 + Vite + TypeScript + Tailwind CSS (开发中)
- **API 后端**: FastAPI (Python 3.10+) + SQLAlchemy
- **数据库**: PostgreSQL 15+ (Full Text Search + pgvector)
- **缓存**: Redis 7.2+
- **任务队列**: Celery 5.3+
- **AI 核心**: System Prompt 驱动的多轮会话模型

---

## 🛠️ 开发起步 (Getting Started)

> 请参考 [backend/START_LOCAL.md](./backend/START_LOCAL.md)

### 后端开发

```bash
# 1. 进入后端目录
cd backend

# 2. 一键部署（自动完成环境检查、依赖安装、数据库迁移、启动服务）
./deploy.sh

# 或手动分步执行：
# - 初始化数据库：docker-compose up -d db
# - 启动后端：uvicorn app.main:app --reload
```

### 访问服务

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

---

## 📂 项目目录结构

```
ReliHub/
├── README.md              # 本文件
├── backend/               # 后端代码
│   ├── app/              # FastAPI 应用代码
│   ├── tests/            # 测试代码
│   ├── alembic/          # 数据库迁移脚本
│   ├── START_LOCAL.md    # 本地开发指南
│   └── deploy.sh          # 部署脚本
├── docs/                  # 项目文档
│   ├── 01_产品需求/       # PRD 文档
│   ├── 02_技术设计/       # 技术设计文档
│   ├── 03_测试文档/       # 测试用例文档
│   ├── 04_开发计划/       # Sprint 计划
│   ├── 05_审查报告/       # 审查报告
│   └── 06_前端UI设计/     # 前端 UI/UX 设计文档
├── design_assets/         # Figma 设计资源
└── .github/               # GitHub 配置 (CI/CD)
```

---

## 🏷️ 版本信息

- **文档版本**: V1.5 (Audit Aligned)
- **项目状态**: MVP 开发 Sprint D 阶段
- **技术栈**: PostgreSQL + FastAPI + React
