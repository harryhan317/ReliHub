# API 接口 - 意见反馈模块
 
 ## 1. 模块概述
 提供用户提交建议、故障反馈及查看反馈进度的接口。
 
 ## 2. 接口列表
 
 ### 2.1 提交反馈
 - **Endpoint**: `POST /api/v1/feedback`
 - **参数**:
   - `type`: 功能异常 / 体验建议 / 内容纠错 / 其他
   - `content`: 描述文本
   - `images`: 图片附件 (URLs)
   - `contact`: 选填联系方式
 
 ### 2.2 获取我的反馈列表
 - **Endpoint**: `GET /api/v1/feedback/my`
 
 ### 2.3 获取反馈详情
 - **Endpoint**: `GET /api/v1/feedback/{id}`
 - **说明**: 包含管理员的回包/回复。
 
 ### 2.4 管理员回复反馈
 - **Endpoint**: `POST /api/v1/admin/feedbacks/{id}/reply`
 - **说明**: 管理员审查工单并填写回复内容，该操作会将反馈状态流转至 RESOLVED。

 ### 2.5 反馈处理规则 (对齐 PRD_MVP_意见反馈 §2.1)
 - **完整状态机**: 待处理 (PENDING) -> 处理中 (PROCESSING) -> 已解决 (RESOLVED) / 已驳回 (REJECTED)。
 - **状态流转**:
   - PENDING: 用户提交后初始状态
   - PROCESSING: 管理员领用后进入，锁定工单
   - RESOLVED: 管理员确认解决（必填回复内容）
   - REJECTED: 管理员驳回（必填回复内容）
 - **超级管理员权限**: 可强行将孤儿工单（处理中超时无人响应）重置回 PENDING 或指派给其他管理员。
 
 ---
 
 ## 3. 模块联动与奖励 (Phase 2)
 - **奖励触发器**: 当管理员将状态变更为“已解决”且标记为“采纳”时，系统自动调用 `PointService.award` 接口。
 - **入账规则**: `amount` = 20, `point_type` = BONUS_BEAN, `order_type` = FEEDBACK_AWARD。
