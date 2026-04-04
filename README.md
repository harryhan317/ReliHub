# ReliHub - 电子产品可靠性领域专业 AI 社区
 
 ReliHub 是一个面向电子产品可靠性技术人员的一站式解决方案平台。它结合了先进的 LLM 技术 (ReliBot) 与社区共享生态，旨在提升行业问题的解决效率。
 
 ---
 
 ## 🚀 快速导航
 
 - **📄 [项目文档 (docs)](./docs/)**：包含全量 PRD 与技术架构方案。
 - **📌 [需求输入基线 (V2.2)](./docs/01_产品需求/ReliHub%20产品需求输入文件%20V2.2.md)**：项目原始需求输入文件。
 - **💻 [前端代码 (src/reliHub-web)](./src/reliHub-web/)**：基于 React 18 的移动端 Web 应用。
 - **⚙️ [后端代码 (src/reliHub-api)](./src/reliHub-api/)**：基于 FastAPI 的高性能异步 API。
 
 ---
 
 ## 🏗️ 项目架构简介
 - **Web 前端**: React 18 + Vite + TypeScript + Tailwind CSS
 - **API 后端**: FastAPI (Python 3.10+) + SQLAlchemy
 - **数据库**: PostgreSQL (Full Text Search)
 - **AI 核心**: System Prompt 驱动的多轮会话模型
 
 ---
 
 ## 🛠️ 开发起步 (Getting Started)
 > 请参考 [运维文档/配置_开发环境.md](./docs/04_运维文档/03_环境配置/配置_开发环境.md) (待创建)
 
 1. 初始化数据库：`docker-compose up -d db`
 2. 启动后端：`cd src/reliHub-api && uvicorn app.main:app --reload`
 3. 启动前端：`cd src/reliHub-web && npm run dev`
 
 ---
 
 ## 🏷️ 版本信息
 - **文档版本**: V1.5 (Audit Aligned)
 - **项目状态**: MVP 开发准备阶段
