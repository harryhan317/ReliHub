"""
日志配置模块
功能：
1. 区分开发和生产环境日志级别
2. 减少生产环境 DEBUG 日志
3. 关键操作使用 INFO 级别
4. 错误使用 ERROR 级别
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(environment: str = "development") -> None:
    """
    配置全局日志级别和格式
    
    Args:
        environment: 运行环境 ("development" 或 "production")
    """
    # 创建日志目录
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 根据环境设置日志级别
    if environment == "production":
        log_level = logging.INFO
        # 生产环境：INFO 级别，减少 DEBUG 日志
        console_level = logging.WARNING
        file_level = logging.INFO
    else:
        log_level = logging.DEBUG
        # 开发环境：DEBUG 级别，便于调试
        console_level = logging.DEBUG
        file_level = logging.DEBUG
    
    # 根日志配置
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（按大小轮转）
    file_handler = RotatingFileHandler(
        log_dir / f"{environment}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 设置第三方库日志级别（减少噪音）
    logging.getLogger("uvicorn").setLevel(logging.WARNING if environment == "production" else logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO if environment == "production" else logging.DEBUG)
    
    # 关键模块日志级别设置
    # 搜索服务：INFO 级别（关键操作需要记录）
    logging.getLogger("app.services.search_service").setLevel(logging.INFO)
    
    # 缓存服务：生产环境 WARNING，开发环境 DEBUG
    logging.getLogger("app.services.search_cache_service").setLevel(
        logging.WARNING if environment == "production" else logging.DEBUG
    )
    
    # 支付服务：INFO 级别（涉及资金操作）
    logging.getLogger("app.services.payment_service").setLevel(logging.INFO)
    
    # AI 服务：INFO 级别
    logging.getLogger("app.services.ai_service").setLevel(logging.INFO)
    
    # 敏感词服务：WARNING 级别（减少日志量）
    logging.getLogger("app.services.sensitive_word_service").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取命名日志器
    
    Args:
        name: 日志器名称，通常使用 __name__
    
    Returns:
        配置好的日志器实例
    """
    return logging.getLogger(name)
