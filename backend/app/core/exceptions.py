"""
Global business exception system.
Aligned with: API_错误码对照表.md §2 (error code dictionary).
"""
from enum import Enum
from typing import Any, Optional

from fastapi import Request
from fastapi.responses import JSONResponse


class ErrorCode(str, Enum):
    """Business error codes per API_错误码对照表.md."""
    
    # Auth (§2.1) - 鉴权与账号模块
    AUTH_4000 = "AUTH_4000"  # Token 缺失或无效格式
    AUTH_4001 = "AUTH_4001"  # Access Token 已过期
    AUTH_4002 = "AUTH_4002"  # 账号异地登录踢出
    AUTH_4003 = "AUTH_4003"  # 验证码/凭证校验失败
    AUTH_4004 = "AUTH_4004"  # 验证码获取频率超限
    AUTH_4005 = "AUTH_4005"  # Refresh Token 过期/协议未接受
    AUTH_4006 = "AUTH_4006"  # 管理员 IP 白名单校验失败

    # User (§2.1) - 用户模块
    USER_4010 = "USER_4010"  # 账号已被封禁/安全锁定
    USER_4011 = "USER_4011"  # 账号长周期不活跃进入休眠期
    USER_4012 = "USER_4012"  # 用户信誉分低于操作红线阈值
    USER_4013 = "USER_4013"  # 用户当前层级不足以越权操作
    USER_4014 = "USER_4014"  # 专家资格认证申请被驳回

    # Economy (§2.2) - 经济模型模块
    ECON_4001 = "ECON_4001"  # 可可豆双资总余额不足以覆盖当期交易
    ECON_4002 = "ECON_4002"  # 跨池并发状态锁定产生隔离行锁冲突
    ECON_4004 = "ECON_4004"  # 订单涉金数额突破平台定义硬性上限
    ECON_4005 = "ECON_4005"  # 账户资产因严重风控处于冻结状态

    # Bounty (§2.2) - 悬赏流转模块
    BOUNTY_4001 = "BOUNTY_4001"  # 用户当前双豆总金额不足锁定该单悬赏
    BOUNTY_4002 = "BOUNTY_4002"  # 悬赏时效逾期已被底座自动核销失效
    BOUNTY_4003 = "BOUNTY_4003"  # 预备采纳发放时检测发榜者财产状态冻结

    # Resource (§2.3) - 资源处理与云文件模块
    RES_4001 = "RES_4001"  # 文件体积超过服务器分片组接限制
    RES_4002 = "RES_4002"  # 文件指纹或扩展提取未能与白名单安全库匹配
    RES_4005 = "RES_4005"  # AI特征向量判定新物料语义重复相像度>80%
    RES_4006 = "RES_4006"  # 文件经特征沙盒截获含有机考违禁元素
    RES_4007 = "RES_4007"  # 用户月度免费总量消耗殆尽再兼缺豆结账阻绝
    RES_4008 = "RES_4008"  # 所提取资源物理注销或 Lifecycle 为 DELETED
    RES_4009 = "RES_4009"  # OSS 在线解析非标准化文件/加密 PDF 打回失败

    # AI (§2.4) - AI 大语言模型引擎
    AI_4001 = "AI_4001"  # AI 免费额度（每日问答总轮次）已达上限
    AI_4002 = "AI_4002"  # Tokenizer 大幅越过大模型显存极值
    AI_4003 = "AI_4003"  # 连线大模型厂商中继层受高频请求堆积超时
    AI_4004 = "AI_4004"  # DPO提示预留机制捕获安全违则言论
    AI_4005 = "AI_4005"  # 后台底层统管的大模型底层 Token 预算告磬

    # Community (§2.5) - 社区互动与发帖模块
    COM_4001 = "COM_4001"  # 回复或发帖文理间遭遇系统黑名单屏蔽网
    COM_4002 = "COM_4002"  # 发帖水军防灌水阈值触界（频率限速）
    COM_4003 = "COM_4003"  # 向强制关闭锁定或终结的帖子回发增量
    COM_4004 = "COM_4004"  # 悬赏标的物尝试投向本人进行自我采纳
    COM_4005 = "COM_4005"  # 连续等幂冲按捕捉到的重复点赞干预
    COM_4007 = "COM_4007"  # 针对已经被打上最佳标识的话题重发悬赏令

    # System (§2.6) - 系统底层网关
    SYS_4290 = "SYS_4290"  # 应用层规则独立计数的阻击防刷限流
    SYS_5000 = "SYS_5000"  # 主线逻辑代码越界引发的逻辑性抛错
    SYS_5001 = "SYS_5001"  # 服务主动下线或实施定期维护升级
    SYS_5002 = "SYS_5002"  # 对外组件（支付/OSS）建立RPC时的通讯超时

    # Admin (管理后台)
    ADMIN_4001 = "ADMIN_4001"  # 管理员账号已被禁用
    ADMIN_4002 = "ADMIN_4002"  # 权限不足
    ADMIN_4003 = "ADMIN_4003"  # 管理员不存在
    ADMIN_4004 = "ADMIN_4004"  # 用户不存在
    ADMIN_4005 = "ADMIN_4005"  # 资源不存在
    ADMIN_4006 = "ADMIN_4006"  # 话题不存在
    ADMIN_4007 = "ADMIN_4007"  # 反馈不存在
    ADMIN_4008 = "ADMIN_4008"  # 配置项不存在
    ADMIN_4009 = "ADMIN_4009"  # 扩容包不存在


_HTTP_STATUS_MAP = {
    ErrorCode.AUTH_4000: 401,
    ErrorCode.AUTH_4001: 401,
    ErrorCode.AUTH_4002: 401,
    ErrorCode.AUTH_4003: 400,
    ErrorCode.AUTH_4004: 429,
    ErrorCode.AUTH_4005: 400,
    ErrorCode.AUTH_4006: 403,
    ErrorCode.USER_4010: 403,
    ErrorCode.USER_4011: 403,
    ErrorCode.USER_4012: 403,
    ErrorCode.USER_4013: 403,
    ErrorCode.USER_4014: 400,
    ErrorCode.ECON_4001: 400,
    ErrorCode.ECON_4002: 409,
    ErrorCode.ECON_4004: 400,
    ErrorCode.ECON_4005: 403,
    ErrorCode.BOUNTY_4001: 400,
    ErrorCode.BOUNTY_4002: 400,
    ErrorCode.BOUNTY_4003: 403,
    ErrorCode.RES_4001: 400,
    ErrorCode.RES_4002: 400,
    ErrorCode.RES_4005: 400,
    ErrorCode.RES_4006: 400,
    ErrorCode.RES_4007: 403,
    ErrorCode.RES_4008: 404,
    ErrorCode.RES_4009: 400,
    ErrorCode.AI_4001: 403,
    ErrorCode.AI_4002: 400,
    ErrorCode.AI_4003: 503,
    ErrorCode.AI_4004: 400,
    ErrorCode.AI_4005: 503,
    ErrorCode.COM_4001: 400,
    ErrorCode.COM_4002: 429,
    ErrorCode.COM_4003: 403,
    ErrorCode.COM_4004: 403,
    ErrorCode.COM_4005: 400,
    ErrorCode.COM_4007: 400,
    ErrorCode.SYS_4290: 429,
    ErrorCode.SYS_5000: 500,
    ErrorCode.SYS_5001: 503,
    ErrorCode.SYS_5002: 502,
    ErrorCode.ADMIN_4001: 403,
    ErrorCode.ADMIN_4002: 403,
    ErrorCode.ADMIN_4003: 404,
    ErrorCode.ADMIN_4004: 404,
    ErrorCode.ADMIN_4005: 404,
    ErrorCode.ADMIN_4006: 404,
    ErrorCode.ADMIN_4007: 404,
    ErrorCode.ADMIN_4008: 404,
    ErrorCode.ADMIN_4009: 404,
}


_ERROR_MESSAGES = {
    ErrorCode.AUTH_4000: "Token 缺失或无效格式",
    ErrorCode.AUTH_4001: "Access Token 已过期",
    ErrorCode.AUTH_4002: "您的账号已在其他设备登录，如非本人操作请立即修改密码",
    ErrorCode.AUTH_4003: "验证码错误，请重新输入",
    ErrorCode.AUTH_4004: "验证码发送过于频繁，请稍后重试",
    ErrorCode.AUTH_4005: "登录凭证已过期，请重新登录",
    ErrorCode.AUTH_4006: "当前网络环境受限，请联系运维确认",
    ErrorCode.USER_4010: "您的账号已被安全锁定",
    ErrorCode.USER_4011: "您的账号已进入休眠状态，请重新激活",
    ErrorCode.USER_4012: "您的信誉分不够，无法执行该项操作",
    ErrorCode.USER_4013: "当前操作需要更高级别的账号权限，请查看等级晋升指南",
    ErrorCode.USER_4014: "您的专家申请未通过",
    ErrorCode.ECON_4001: "可可豆余额不足以覆盖本次交易",
    ErrorCode.ECON_4002: "系统正在处理您的同类扣费订单，请勿重复操作",
    ErrorCode.ECON_4004: "单次悬赏金额不可超过平台规定的单笔最高额度",
    ErrorCode.ECON_4005: "您的账户资产已被冻结，无法执行资金操作，请联系管理员",
    ErrorCode.BOUNTY_4001: "您的可可豆余额不足以锁定该悬赏金，请降低金额或获取更多可可豆",
    ErrorCode.BOUNTY_4002: "该悬赏已逾期（默认30天），系统已自动关闭并退款至发布者账户",
    ErrorCode.BOUNTY_4003: "执行悬赏采纳时，检测到悬赏发布者账户已冻结，无法完成悬赏金发放",
    ErrorCode.RES_4001: "单文件体积超标，请压缩至规约限制内后重试",
    ErrorCode.RES_4002: "系统暂不支持该文件格式，请上传标准格式文件",
    ErrorCode.RES_4005: "检测到平台包含高度相似的语义内容，是否强制提交进入人工审核？",
    ErrorCode.RES_4006: "文件未通过安全校验，存在病毒或违规内容风险",
    ErrorCode.RES_4007: "免费额度已耗尽，请兑换或购买流量包",
    ErrorCode.RES_4008: "对不起，该资源已被删除或原始链接失效",
    ErrorCode.RES_4009: "该文件格式不支持在线预览，请下载后查看",
    ErrorCode.AI_4001: "您当前的 AI 免费额度已耗尽，请使用可可豆兑换 AI 扩充包补充额度",
    ErrorCode.AI_4002: "会话上下文超出模型长度限制，请开启新会话继续",
    ErrorCode.AI_4003: "AI 服务暂时繁忙，请稍后重试",
    ErrorCode.AI_4004: "您的提问内容包含敏感违规词汇，请修改后重新提问",
    ErrorCode.AI_4005: "AI 服务暂时不可用，技术人员正在紧急处理中，请稍后再试",
    ErrorCode.COM_4001: "您的内容包含系统违禁词汇，请检查并修改后再提交",
    ErrorCode.COM_4002: "您发文过于频繁，请稍后再试",
    ErrorCode.COM_4003: "该话题已关闭，请选择其他话题参与讨论",
    ErrorCode.COM_4004: "系统规则不允许采纳本人发布的回复作为最佳答案",
    ErrorCode.COM_4005: "您已点赞过该内容，请勿重复操作",
    ErrorCode.COM_4007: "该话题已有最佳答案，不可重复采纳",
    ErrorCode.SYS_4290: "操作过于频繁，请稍后重试",
    ErrorCode.SYS_5000: "服务器处理异常，请稍后重试",
    ErrorCode.SYS_5001: "系统升级维护中",
    ErrorCode.SYS_5002: "第三方服务通信超时，请稍后重试",
    ErrorCode.ADMIN_4001: "管理员账号已被禁用",
    ErrorCode.ADMIN_4002: "权限不足",
    ErrorCode.ADMIN_4003: "管理员不存在",
    ErrorCode.ADMIN_4004: "用户不存在",
    ErrorCode.ADMIN_4005: "资源不存在",
    ErrorCode.ADMIN_4006: "话题不存在",
    ErrorCode.ADMIN_4007: "反馈不存在",
    ErrorCode.ADMIN_4008: "配置项不存在",
    ErrorCode.ADMIN_4009: "扩容包不存在",
}


class BusinessException(Exception):
    """Raise to return structured error response."""

    def __init__(
        self,
        code: ErrorCode,
        msg: Optional[str] = None,
        data: Optional[dict[str, Any]] = None,
        http_status: Optional[int] = None,
    ):
        self.code = code
        self.msg = msg or _ERROR_MESSAGES.get(code, "未知错误")
        self.data = data or {}
        self.http_status = http_status or _HTTP_STATUS_MAP.get(code, 400)


async def business_exception_handler(_request: Request, exc: BusinessException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status,
        content={"code": exc.code.value, "msg": exc.msg, "data": exc.data},
    )


async def generic_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"code": "SYS_5000", "msg": "服务器处理异常，请稍后重试", "data": {}},
    )
