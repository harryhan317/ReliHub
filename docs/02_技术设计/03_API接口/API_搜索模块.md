# API 接口 - 搜索模块 (API_搜索模块)

## 1. 全局检索
- **Endpoint**: `GET /api/v1/search`
- **参数**: `q` (关键词), `type` (ALL/RESOURCE/COMMUNITY/AI)
- **实现**: 基于 `tsvector` 的全文检索 + 复合热度衰减评分。当 `type=AI` 时，强制按 `updated_at DESC` 排序，不参与热度衰减评分。
- **最新查询限制**: 若指定 `sort_by=latest`，强制执行硬性时间窗隔离过滤：RESOURCE 仅拉取 `created_at` 距今 7 天内数据，COMMUNITY 仅拉取距今 3 天内数据，杜绝长尾污染（详见方案《集成_全文检索算法方案.md》）。

## 2. 搜索建议 (Autocomplete)
- **Endpoint**: `GET /api/v1/search/suggestions`
- **逻辑**: 基于 Redis ZSET 的前缀匹配，响应时间 ≤ 300ms。

---
- [x] 对齐 PRD §4.2 搜索系统目标。
- [x] 技术方案对齐《集成_全文检索算法方案.md》。
