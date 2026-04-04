# 🚀 Sprint C 开发准备清单

**创建日期**: 2026-04-04  
**状态**: 🔄 准备中

---

## ✅ 已完成

### 1. 部署环境准备
- [x] PostgreSQL 数据库已安装并运行
- [x] Python 3.9.6 环境已配置
- [x] 虚拟环境已创建 (.venv)
- [x] 依赖包已安装
- [x] 数据库迁移成功（17 个表）
- [x] 应用成功启动（http://localhost:8000）
- [x] Swagger UI 可访问
- [x] API 验证脚本已创建

### 2. 技术文档
- [x] Sprint C 技术方案设计
- [x] Sprint C 任务清单
- [x] Sprint C 启动会议程
- [x] 部署指南
- [x] 本地开发启动指南

---

## 🔄 进行中

### 1. LLM API 准备
- [ ] **DeepSeek API**
  - [ ] 注册 DeepSeek 账号
  - [ ] 获取 API Key
  - [ ] 测试 API 连接
  - [ ] 了解计费模式
  
- [ ] **阿里百炼 API**（备选）
  - [ ] 注册阿里云账号
  - [ ] 开通百炼服务
  - [ ] 获取 API Key
  - [ ] 测试 API 连接

### 2. 支付网关准备
- [ ] **微信支付**
  - [ ] 注册微信商户平台
  - [ ] 完成企业认证
  - [ ] 获取商户号 (MCHID)
  - [ ] 配置 API 密钥
  - [ ] 下载 API 证书
  - [ ] 配置回调 URL
  
- [ ] **支付宝**
  - [ ] 注册支付宝开放平台
  - [ ] 创建应用
  - [ ] 获取 APPID
  - [ ] 配置 RSA 密钥
  - [ ] 配置回调 URL

### 3. 敏感词过滤准备
- [ ] **敏感词库**
  - [ ] 收集基础敏感词库
  - [ ] 分类整理（政治、色情、暴力等）
  - [ ] 导入数据库
  - [ ] 建立更新机制

### 4. OSS 存储准备
- [ ] **阿里云 OSS**
  - [ ] 开通 OSS 服务
  - [ ] 创建 Bucket
  - [ ] 配置访问密钥
  - [ ] 配置 CORS
  - [ ] 配置 CDN（可选）

---

## 📋 开发环境配置

### 1. 环境变量配置

创建 `.env.local` 文件（不要提交到 Git）：

```bash
# LLM API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# ALIYUN_BAILIAN_API_KEY=your_aliyun_key  # 备选

# Payment Gateway Configuration
WECHAT_MCHID=your_wechat_merchant_id
WECHAT_API_V3_KEY=your_wechat_api_v3_key
WECHAT_SERIAL_NO=your_wechat_cert_serial
WECHAT_PRIVATE_KEY_PATH=./certs/wechat/apiclient_key.pem

ALIPAY_APPID=your_alipay_appid
ALIPAY_PRIVATE_KEY_PATH=./certs/alipay/app_private_key.pem
ALIPAY_ALIPAY_PUBLIC_KEY_PATH=./certs/alipay/alipay_public_key.pem

# OSS Configuration
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OSS_BUCKET=relihub-files
ALIYUN_ACCESS_KEY_ID=your_oss_access_key
ALIYUN_ACCESS_KEY_SECRET=your_oss_secret

# Sensitive Word Filter
SENSITIVE_WORD_DB_PATH=./data/sensitive_words.json
SENSITIVE_WORD_ENABLED=true
```

### 2. 证书目录结构

```
backend/
├── certs/
│   ├── wechat/
│   │   ├── apiclient_cert.pem      # 微信支付 API 证书
│   │   └── apiclient_key.pem       # 微信支付 API 私钥
│   └── alipay/
│       ├── app_private_key.pem     # 支付宝应用私钥
│       └── alipay_public_key.pem   # 支付宝公钥
└── data/
    └── sensitive_words.json        # 敏感词库
```

---

## 🧪 测试计划

### 1. LLM API 测试
```bash
# 测试 DeepSeek API 连接
curl -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### 2. 支付网关测试
- [ ] 微信支付沙箱测试
- [ ] 支付宝沙箱测试
- [ ] 回调接口测试

### 3. 敏感词过滤测试
```python
# 测试 AC 自动机
from app.services.sensitive_word_service import SensitiveWordService

service = SensitiveWordService()
service.load_words(["敏感词 1", "敏感词 2"])
result = service.filter("这段文字包含敏感词 1")
print(result)  # 这段文字包含***
```

---

## 📅 时间表

| 任务 | 预计时间 | 状态 |
|------|---------|------|
| LLM API 申请 | 1-2 天 | 🔄 |
| 支付网关申请 | 3-5 天 | ⏳ |
| 敏感词库收集 | 1 天 | ⏳ |
| OSS 配置 | 0.5 天 | ⏳ |
| 开发环境配置 | 0.5 天 | ⏳ |

---

## 🔗 参考文档

1. [DeepSeek API 文档](https://platform.deepseek.com/api-docs/)
2. [微信支付 API v3 文档](https://pay.weixin.qq.com/wiki/doc/apiv3/index.shtml)
3. [支付宝开放平台](https://opendocs.alipay.com/)
4. [阿里云 OSS 文档](https://help.aliyun.com/product/31815.html)
5. [Sprint C 技术方案设计](../docs/06_Sprint_C 规划/Sprint_C_技术方案设计.md)

---

## 📞 联系方式

如有问题，请联系：
- 技术负责人：developer@relihub.com
- Slack: #sprint-c-dev

---

**准备中 - 预计完成时间：2026-04-09** 🚧
