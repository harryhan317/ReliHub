-- ReliHub 测试数据初始化脚本 (PostgreSQL 15+)
-- 适用范围：MVP 基础冒烟测试、UAT 验收、压力测试基准
-- 注意：执行前请确保数据库架构 (Migrations) 已完成部署

BEGIN;

/* ==========================================
   1. 基础字典表 (Categories & Metadata)
   ========================================== */
INSERT INTO categories (id, name, type, description) VALUES
(1, '可靠性标准', 'RESOURCE', 'HALT/HASS、MIL-STD 等行业标准'),
(2, '失效分析', 'RESOURCE', '案例研究、工具方法'),
(3, '行业软件', 'RESOURCE', 'ReliaSoft, Sherlock 等工具教程'),
(4, '技术求助', 'COMMUNITY', '社区技术问答'),
(5, '经验分享', 'COMMUNITY', '行业心得、职业规划');

/* ==========================================
   2. 用户体系 (Users & Experts)
   ========================================== */
-- 系统账号 (用于通缩账户与匿名化)
INSERT INTO users (id, business_id, nick_name, reputation_points, is_deleted) VALUES
('00000000-0000-0000-0000-000000000000', 'USER000000', '匿名用户', 0, true),
('ffffffff-ffff-ffff-ffff-ffffffffffff', 'USER_BURN', 'SYSTEM_BURN', 0, false); -- 通缩账户

-- 管理员
INSERT INTO users (id, business_id, nick_name, reputation_status) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'ADM2026001', '超级管理员', 'NORMAL');

-- 专家用户 (UUID: 1001)
INSERT INTO users (id, business_id, nick_name, reputation_points, reputation_level) VALUES
('11111111-1111-1111-1111-111111111111', 'EXP1001', '可靠性老王', 150, 'EXPERT');

-- 普通用户 (UUID: 2001)
INSERT INTO users (id, business_id, nick_name, reputation_points, reputation_level) VALUES
('22222222-2222-2222-2222-222222222222', 'USR2001', '新人小白', 50, 'NOVICE');

/* ==========================================
   3. 资源模块 (Resources)
   ========================================== */
-- 已通过的基础资源
INSERT INTO resources (id, uploader_id, title, category_id, price, is_seed, status) VALUES
('r001', '11111111-1111-1111-1111-111111111111', 'GJB 899A-2009 可靠性鉴定及验收试验', 1, 10, true, 'APPROVED');

-- 待审核资源
INSERT INTO resources (id, uploader_id, title, category_id, price, is_seed, status) VALUES
('r002', '22222222-2222-2222-2222-222222222222', 'FMEA 案例分析 PPT', 2, 5, false, 'PENDING_REVIEW');

-- 被拒绝资源
INSERT INTO resources (id, uploader_id, title, category_id, price, is_seed, status) VALUES
('r003', '22222222-2222-2222-2222-222222222222', '违规盗版资料.pdf', 3, 10, false, 'REJECTED');

/* ==========================================
   4. 社区模块 (Topics & Posts)
   ========================================== */
-- 活动中的悬赏话题 (Bounty = 100)
INSERT INTO topics (id, author_id, title, content, bounty_amount, bounty_status) VALUES
('t001', '22222222-2222-2222-2222-222222222222', '如何建立 HALT 试验剖面？', '急求航天级 HALT 试验的典型应力步进值...', 100, 'ACTIVE');

-- 普通话题
INSERT INTO topics (id, author_id, title, content) VALUES
('t002', '11111111-1111-1111-1111-111111111111', 'ReliaSoft 版本更新内容讨论', '大家觉得 2026 版好用吗？');

-- 已解决的悬赏
INSERT INTO topics (id, author_id, title, content, bounty_amount, bounty_status) VALUES
('t003', '11111111-1111-1111-1111-111111111111', '某机电系统 MTBF 计算求助', '求助详细步骤...', 50, 'RESOLVED');

-- 已过期的悬赏
INSERT INTO topics (id, author_id, title, content, bounty_amount, bounty_status) VALUES
('t004', '22222222-2222-2222-2222-222222222222', '寻失效分析相关外文文献', '寻找几篇经典文献...', 200, 'REFUNDED');

/* ==========================================
   5. 经济系统预设 (Initial Ledgers)
   ========================================== */
-- 为新人小白预充值 100 资产豆
INSERT INTO point_ledger (id, transaction_uuid, user_id, amount, point_type, order_type, balance_after) VALUES
(gen_random_uuid(), gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 100, 'GOLD_BEAN', 'RECHARGE', 100);

-- 签到奖励测试数据
INSERT INTO point_ledger (id, transaction_uuid, user_id, amount, point_type, order_type, balance_after) VALUES
(gen_random_uuid(), gen_random_uuid(), '22222222-2222-2222-2222-222222222222', 2, 'BONUS_BEAN', 'SIGN_IN', 2);

/* ==========================================
   6. 意见反馈 (Feedbacks)
   ========================================== */
INSERT INTO feedbacks (id, business_id, user_id, type, content_body, status) VALUES
(gen_random_uuid(), 'FB20260402000001', '22222222-2222-2222-2222-222222222222', 1, '社区搜索功能偶发性 502', 'PENDING');

COMMIT;
