# Phase2 技术架构

## 文档元信息

| 项目 | 内容 |
|------|------|
| 文档名称 | Phase2 技术架构 |
| 文档版本 | V1.0 |
| 创建日期 | 2026-04-23 |
| 作者 | 技术团队 |
| 适用范围 | ReliHub Phase2阶段技术实现方案 |
| 文档状态 | 草案 |

## 一、技术架构总览

### 1.1 架构设计原则

Phase2阶段技术架构设计遵循以下原则：

**1. 微信生态优先原则**
- 深度集成微信小程序生态能力
- 优先使用微信原生API和组件
- 遵循微信小程序开发规范

**2. 渐进式迁移原则**  
- 保持与Phase1 Web版本的兼容性
- 支持双平台并行运营
- 平滑迁移，最小化用户影响

**3. 性能优先原则**
- 小程序包体积控制在2MB以内
- 首屏加载时间优化到1.5秒内
- 接口响应时间控制在500ms内

**4. 安全可靠原则**
- 微信用户数据合规处理
- 支付交易数据安全加密
- 敏感操作多重验证

### 1.2 技术栈选择

| 层级 | 技术选型 | 版本 | 选择理由 |
|------|---------|------|---------|
| **前端框架** | Taro | 3.x | 支持React语法，跨端能力强 |
| **UI组件库** | Taro UI + 自定义 | - | 官方组件+业务定制 |
| **状态管理** | Zustand | 4.x | 轻量高效，与Web版本一致 |
| **路由管理** | 小程序原生路由 | - | 性能最优，兼容性好 |
| **后端框架** | FastAPI | 0.104+ | 高性能，异步支持好 |
| **数据库** | PostgreSQL | 14+ | 关系型数据，扩展性强 |
| **缓存** | Redis | 7.x | 高性能缓存，会话管理 |
| **消息队列** | Celery + Redis | - | 异步任务处理 |
| **对象存储** | 阿里云OSS | - | 文件存储，CDN加速 |

## 二、前端架构设计

### 2.1 小程序项目结构

```
frontend-miniprogram/
├── src/
│   ├── app.js                 # 小程序入口
│   ├── app.json               # 全局配置
│   ├── app.scss               # 全局样式
│   ├── pages/                 # 页面目录
│   │   ├── ask/               # 爱问模块
│   │   ├── resource/          # 资源模块
│   │   ├── community/         # 社区模块
│   │   └── my/                # 我的模块
│   ├── components/            # 公共组件
│   │   ├── common/            # 通用组件
│   │   ├── business/          # 业务组件
│   │   └── wechat/            # 微信特有组件
│   ├── services/              # 服务层
│   │   ├── api/               # API接口
│   │   ├── wechat/            # 微信服务
│   │   └── utils/             # 工具函数
│   ├── store/                 # 状态管理
│   │   ├── authStore.ts       # 认证状态
│   │   ├── userStore.ts       # 用户状态
│   │   └── ...                # 其他状态
│   └── assets/                # 静态资源
│       ├── images/            # 图片资源
│       └── styles/            # 样式文件
├── project.config.json        # 项目配置
└── package.json              # 依赖管理
```

### 2.2 组件架构设计

#### 2.2.1 组件分层架构

**基础组件层**
- 封装微信原生组件
- 提供统一的组件接口
- 处理平台差异

**业务组件层**
- 复用Web版本业务逻辑
- 适配小程序特有交互
- 保持功能一致性

**页面组件层**
- 页面级组件封装
- 路由跳转管理
- 页面生命周期管理

#### 2.2.2 关键组件设计

**微信授权组件**
```typescript
// components/wechat/AuthButton.tsx
interface AuthButtonProps {
  onSuccess: (userInfo: WechatUserInfo) => void;
  onError: (error: Error) => void;
}

const AuthButton: React.FC<AuthButtonProps> = ({ onSuccess, onError }) => {
  const handleAuth = async () => {
    try {
      const { code } = await Taro.login();
      const userInfo = await authService.wechatLogin(code);
      onSuccess(userInfo);
    } catch (error) {
      onError(error);
    }
  };
  
  return <Button onClick={handleAuth}>微信一键登录</Button>;
};
```

**支付组件**
```typescript
// components/wechat/PaymentButton.tsx
interface PaymentButtonProps {
  orderInfo: OrderInfo;
  onSuccess: (result: PaymentResult) => void;
  onError: (error: Error) => void;
}

const PaymentButton: React.FC<PaymentButtonProps> = ({ orderInfo, onSuccess, onError }) => {
  const handlePayment = async () => {
    try {
      const paymentParams = await paymentService.createWechatPayment(orderInfo);
      const result = await Taro.requestPayment(paymentParams);
      onSuccess(result);
    } catch (error) {
      onError(error);
    }
  };
  
  return <Button onClick={handlePayment}>立即支付</Button>;
};
```

### 2.3 状态管理架构

#### 2.3.1 状态分层设计

**全局状态**
- 用户认证信息
- 应用配置信息
- 全局加载状态

**模块状态**
- 各模块的业务状态
- 页面级数据缓存
- 用户操作状态

**临时状态**
- 表单输入状态
- 页面交互状态
- 异步操作状态

#### 2.3.2 Zustand状态管理

```typescript
// store/authStore.ts
interface AuthState {
  user: User | null;
  isLoggedIn: boolean;
  wechatInfo: WechatUserInfo | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoggedIn: false,
  wechatInfo: null,
  
  login: async (credentials) => {
    const user = await authService.login(credentials);
    set({ user, isLoggedIn: true });
  },
  
  logout: () => {
    authService.logout();
    set({ user: null, isLoggedIn: false, wechatInfo: null });
  },
  
  refreshToken: async () => {
    const newToken = await authService.refreshToken();
    // 更新token逻辑
  }
}));
```

## 三、后端架构设计

### 3.1 微信生态适配层

#### 3.1.1 微信API统一封装

```python
# backend/app/services/wechat_service.py
class WechatService:
    def __init__(self):
        self.app_id = settings.WECHAT_APP_ID
        self.app_secret = settings.WECHAT_APP_SECRET
    
    async def get_access_token(self) -> str:
        """获取微信access_token"""
        cache_key = f"wechat_access_token:{self.app_id}"
        access_token = await redis_client.get(cache_key)
        
        if not access_token:
            url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
            response = await self._request(url)
            access_token = response["access_token"]
            await redis_client.setex(cache_key, 7000, access_token)  # 缓存2小时
        
        return access_token
    
    async def code_to_session(self, code: str) -> WechatSession:
        """code换session"""
        url = f"https://api.weixin.qq.com/sns/jscode2session?appid={self.app_id}&secret={self.app_secret}&js_code={code}&grant_type=authorization_code"
        response = await self._request(url)
        return WechatSession(**response)
```

#### 3.1.2 支付服务封装

```python
# backend/app/services/wechat_pay_service.py
class WechatPayService:
    def __init__(self):
        self.mch_id = settings.WECHAT_MCH_ID
        self.api_key = settings.WECHAT_API_KEY
        self.notify_url = settings.WECHAT_PAY_NOTIFY_URL
    
    async def create_jsapi_payment(self, order: Order, openid: str) -> JsapiPaymentParams:
        """创建JSAPI支付参数"""
        # 统一下单
        unified_order = await self._unified_order(order, openid)
        
        # 生成支付参数
        params = {
            "appId": self.app_id,
            "timeStamp": str(int(time.time())),
            "nonceStr": self._generate_nonce_str(),
            "package": f"prepay_id={unified_order.prepay_id}",
            "signType": "RSA",
        }
        
        # 签名
        params["paySign"] = self._sign_params(params)
        
        return JsapiPaymentParams(**params)
```

### 3.2 数据库架构扩展

#### 3.2.1 新增数据表设计

**微信用户关联表**
```sql
CREATE TABLE wechat_user (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    openid VARCHAR(128) UNIQUE NOT NULL,
    unionid VARCHAR(128),
    session_key VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_wechat_user_openid ON wechat_user(openid);
CREATE INDEX idx_wechat_user_user_id ON wechat_user(user_id);
```

**支付订单表**
```sql
CREATE TABLE payment_orders (
    id BIGSERIAL PRIMARY KEY,
    order_no VARCHAR(64) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    subject VARCHAR(255) NOT NULL,
    body TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    wechat_prepay_id VARCHAR(64),
    wechat_transaction_id VARCHAR(64),
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payment_orders_user_id ON payment_orders(user_id);
CREATE INDEX idx_payment_orders_status ON payment_orders(status);
CREATE INDEX idx_payment_orders_created_at ON payment_orders(created_at);
```

#### 3.2.2 数据迁移策略

**用户数据迁移**
```python
# backend/scripts/migrate_users.py
async def migrate_users_to_wechat():
    """将现有用户迁移到微信体系"""
    users = await User.all().filter(is_active=True)
    
    for user in users:
        # 检查是否已关联微信
        wechat_user = await WechatUser.filter(user_id=user.id).first()
        if not wechat_user:
            # 生成虚拟openid用于过渡
            virtual_openid = f"virtual_{user.id}_{int(time.time())}"
            await WechatUser.create(
                user_id=user.id,
                openid=virtual_openid,
                session_key=""
            )
```

## 四、性能优化方案

### 4.1 小程序性能优化

#### 4.1.1 包体积优化

**代码分割策略**
```javascript
// 按页面分包
{
  "subPackages": [
    {
      "root": "pages/ask",
      "pages": ["index", "chat", "history"]
    },
    {
      "root": "pages/resource", 
      "pages": ["index", "detail", "upload"]
    }
  ]
}
```

**资源优化策略**
- 图片压缩：使用WebP格式，控制图片尺寸
- 字体优化：使用系统字体，减少自定义字体
- 代码压缩：Taro构建时自动压缩

#### 4.1.2 运行时优化

**数据缓存策略**
```typescript
// services/cacheService.ts
class CacheService {
  private static instance: CacheService;
  
  async getWithCache<T>(key: string, fetcher: () => Promise<T>, ttl: number = 300): Promise<T> {
    const cached = await Taro.getStorage({ key });
    if (cached && Date.now() - cached.timestamp < ttl * 1000) {
      return cached.data;
    }
    
    const data = await fetcher();
    await Taro.setStorage({
      key,
      data: { data, timestamp: Date.now() }
    });
    
    return data;
  }
}
```

**接口请求优化**
- 请求合并：相同接口合并请求
- 数据分页：大数据量分页加载
- 懒加载：非关键数据延迟加载

### 4.2 后端性能优化

#### 4.2.1 接口性能优化

**缓存策略**
```python
# backend/app/core/cache.py
class RedisCache:
    async def get_or_set(self, key: str, fetcher: Callable, ttl: int = 300):
        """缓存获取或设置"""
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        data = await fetcher()
        await self.redis.setex(key, ttl, json.dumps(data))
        return data
```

**数据库优化**
- 索引优化：关键查询字段添加索引
- 查询优化：避免N+1查询问题
- 连接池：数据库连接池配置

#### 4.2.2 异步处理

**Celery异步任务**
```python
# backend/app/tasks/wechat_tasks.py
@celery.task
async def send_wechat_template_message(user_id: int, template_id: str, data: dict):
    """发送微信模板消息"""
    user = await User.get(id=user_id)
    wechat_user = await WechatUser.filter(user_id=user_id).first()
    
    if wechat_user:
        await wechat_service.send_template_message(
            openid=wechat_user.openid,
            template_id=template_id,
            data=data
        )
```

## 五、安全架构设计

### 5.1 数据安全

**敏感数据加密**
```python
# backend/app/core/security.py
class DataEncryption:
    def __init__(self):
        self.key = settings.ENCRYPTION_KEY
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """加密敏感数据"""
        cipher = Fernet(self.key)
        return cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """解密敏感数据"""
        cipher = Fernet(self.key)
        return cipher.decrypt(encrypted_data.encode()).decode()
```

**支付安全**
- 支付签名验证
- 金额校验
- 防重放攻击

### 5.2 接口安全

**接口权限控制**
```python
# backend/app/api/deps.py
async def get_current_wechat_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> WechatUser:
    """获取当前微信用户"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    wechat_user = await db.query(WechatUser).filter(WechatUser.user_id == user_id).first()
    return wechat_user
```

## 六、部署架构

### 6.1 小程序部署

**开发环境**
- Taro开发服务器
- 微信开发者工具
- 本地API服务

**生产环境**
- 微信小程序平台
- CDN静态资源分发
- 生产API服务

### 6.2 后端部署

**容器化部署**
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/relihub
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=relihub
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
  
  redis:
    image: redis:7-alpine
```

## 七、监控与运维

### 7.1 监控指标

**性能监控**
- 小程序启动时间
- 页面加载时间
- 接口响应时间
- 错误率统计

**业务监控**
- 用户活跃度
- 支付成功率
- 功能使用率
- 用户留存率

### 7.2 日志系统

**结构化日志**
```python
# backend/app/core/logging.py
import structlog

logger = structlog.get_logger()

async def api_logger(request: Request, call_next):
    """API请求日志中间件"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    logger.info(
        "api_request",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time,
        user_agent=request.headers.get("user-agent")
    )
    
    return response
```

## 八、总结

Phase2技术架构在保持与Phase1技术栈一致性的基础上，重点解决了微信小程序生态集成、性能优化和安全保障等关键问题。通过渐进式迁移策略和模块化架构设计，确保Phase2阶段的顺利实施和长期可维护性。