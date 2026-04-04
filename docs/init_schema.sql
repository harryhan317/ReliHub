-- ReliHub Database Initialization Script
-- Note: This is a reference schema. In production, we use Alembic for migrations.

-- 1. Enable vector extension for AI semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50),
    wechat_openid VARCHAR(100) UNIQUE,
    cocoa_beans INTEGER DEFAULT 0,
    reputation_points INTEGER DEFAULT 0,
    reputation_level VARCHAR(20) DEFAULT 'NEWBIE',
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_wechat_openid ON users(wechat_openid);

-- 3. Create Resources Table
CREATE TABLE IF NOT EXISTS resources (
    id VARCHAR(36) PRIMARY KEY,
    uploader_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    file_url VARCHAR(1024) NOT NULL,
    file_md5 VARCHAR(32) NOT NULL,
    embedding vector(1536), -- Assuming OpenAI ada-002 model dimensions
    price INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'SCANNING',
    is_elite BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_resource_uploader ON resources(uploader_id);
CREATE INDEX IF NOT EXISTS idx_resource_md5 ON resources(file_md5);
CREATE INDEX IF NOT EXISTS idx_resource_status ON resources(status);
-- HNSW index for vector similarity searches (better performance for large datasets)
CREATE INDEX ON resources USING hnsw (embedding vector_cosine_ops);

-- 4. Create Ledger Tables
CREATE TABLE IF NOT EXISTS cocoa_bean_ledger (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    order_type VARCHAR(50) NOT NULL,
    change_value INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    business_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_cbl_user ON cocoa_bean_ledger(user_id);
CREATE INDEX IF NOT EXISTS idx_cbl_created ON cocoa_bean_ledger(created_at);

CREATE TABLE IF NOT EXISTS reputation_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    action_type VARCHAR(50) NOT NULL,
    change_value INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    reason VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_repset_user ON reputation_logs(user_id);
