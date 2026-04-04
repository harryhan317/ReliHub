# 集成方案 - RAG 知识库方案 (集成_RAG知识库方案)

## 1. 业务背景 (Phase 3 预留)
为了提高 AI 对电子产品可靠性专业知识的回答准确度，需构建本地专家知识库。

## 2. 技术栈
- **向量数据库**: PostgreSQL + `pgvector`。
- **Embedding 模型**: `text-embedding-3-small` (OpenAI) 或国产高性能模型。
- **分块策略**: 采用固定长度 + 重叠 (Chunking with Overlap) 策略，确保上下文不丢失。

## 3. 处理流程
1. **注入**: PDF/Docx 转文本 -> 分块 -> 生成 Embedding -> 存入数据库。
2. **检索**: 用户提问 -> 生成 Embedding -> Top-K 检索 -> 召回背景知识。
3. **生成**: 系统 Prompt + 召回知识 + 用户问题 -> LLM 生成回答。

---
- [x] 对齐 PRD 总体演进计划：Phase 2/3 RAG 落地准备。
- [x] 架构与 `pgvector` 方案同步。
