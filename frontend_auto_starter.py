#!/usr/bin/env python3
"""
前端服务自动启动器
功能：检测到用户访问请求时自动启动前端服务，提供状态监控和错误处理
"""

import asyncio
import aiohttp
import subprocess
import time
import os
import signal
import psutil
from aiohttp import web
from typing import Dict, Optional
import json
import logging

# 配置参数
CONFIG = {
    "FRONTEND_PORT": 3000,
    "PROXY_PORT": 8080,
    "MAX_STARTUP_TIME": 30,  # 最大启动时间（秒）
    "HEALTH_CHECK_INTERVAL": 5,  # 健康检查间隔（秒）
    "FRONTEND_DIR": "/Users/harryhan/Desktop/ReliHub/frontend",
    "SUPPORTED_BROWSERS": ["Chrome", "Firefox", "Safari", "Edge"],
    "CLIENT_DEVICES": ["Desktop", "Mobile", "Tablet"]
}

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceStatus:
    """服务状态管理"""
    def __init__(self):
        self.is_running = False
        self.is_starting = False
        self.start_time = None
        self.process = None
        self.last_health_check = 0
        self.error_count = 0
        self.max_errors = 3

    def set_starting(self):
        """标记服务正在启动"""
        self.is_starting = True
        self.start_time = time.time()
        self.error_count = 0

    def set_running(self, process):
        """标记服务运行中"""
        self.is_running = True
        self.is_starting = False
        self.process = process
        self.last_health_check = time.time()

    def set_stopped(self):
        """标记服务停止"""
        self.is_running = False
        self.is_starting = False
        self.process = None

    def record_error(self):
        """记录错误"""
        self.error_count += 1

    def should_retry(self) -> bool:
        """判断是否应该重试"""
        return self.error_count < self.max_errors

    def is_startup_timeout(self) -> bool:
        """判断启动是否超时"""
        if not self.is_starting or not self.start_time:
            return False
        return time.time() - self.start_time > CONFIG["MAX_STARTUP_TIME"]

class FrontendServiceManager:
    """前端服务管理器"""
    
    def __init__(self):
        self.status = ServiceStatus()
        self.session: Optional[aiohttp.ClientSession] = None

    async def init_session(self):
        """初始化HTTP会话"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def check_service_health(self) -> bool:
        """检查前端服务健康状态"""
        try:
            if not self.session:
                await self.init_session()
            
            async with self.session.get(f"http://localhost:{CONFIG['FRONTEND_PORT']}", timeout=5) as response:
                self.status.last_health_check = time.time()
                return response.status == 200
        except Exception as e:
            logger.warning(f"健康检查失败: {e}")
            return False

    async def start_frontend_service(self) -> bool:
        """启动前端服务"""
        if self.status.is_running or self.status.is_starting:
            logger.info("服务已在运行或启动中，跳过启动")
            return True

        logger.info("开始启动前端服务...")
        self.status.set_starting()

        try:
            # 检查是否已有进程在运行
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and 'vite' in ' '.join(proc.info['cmdline']):
                        logger.info("发现已存在的Vite进程，尝试终止")
                        proc.terminate()
                        proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    continue

            # 启动新进程
            env = os.environ.copy()
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=CONFIG["FRONTEND_DIR"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.status.set_running(process)
            
            # 等待服务启动
            startup_timeout = CONFIG["MAX_STARTUP_TIME"]
            start_time = time.time()
            
            while time.time() - start_time < startup_timeout:
                if await self.check_service_health():
                    logger.info("前端服务启动成功")
                    return True
                
                # 检查进程是否存活
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    logger.error(f"前端服务进程异常退出: stdout={stdout}, stderr={stderr}")
                    self.status.record_error()
                    self.status.set_stopped()
                    return False
                
                await asyncio.sleep(2)
            
            # 启动超时
            logger.error("前端服务启动超时")
            self.status.record_error()
            self.status.set_stopped()
            return False
            
        except Exception as e:
            logger.error(f"启动前端服务失败: {e}")
            self.status.record_error()
            self.status.set_stopped()
            return False

    async def stop_frontend_service(self):
        """停止前端服务"""
        if self.status.process:
            try:
                self.status.process.terminate()
                self.status.process.wait(timeout=10)
                logger.info("前端服务已停止")
            except subprocess.TimeoutExpired:
                self.status.process.kill()
                logger.warning("强制终止前端服务")
            except Exception as e:
                logger.error(f"停止前端服务失败: {e}")
        
        self.status.set_stopped()

    async def handle_request(self, request: web.Request) -> web.Response:
        """处理HTTP请求"""
        user_agent = request.headers.get('User-Agent', '')
        client_ip = request.remote
        
        logger.info(f"收到请求: {request.method} {request.path} from {client_ip} ({user_agent[:50]})")
        
        # 检查浏览器兼容性
        if not self._is_browser_supported(user_agent):
            return web.Response(
                text=json.dumps({
                    "error": "不支持的浏览器",
                    "supported_browsers": CONFIG["SUPPORTED_BROWSERS"]
                }),
                content_type='application/json',
                status=400
            )

        # 检查服务状态
        if not self.status.is_running:
            if self.status.is_starting:
                # 服务正在启动中
                return web.Response(
                    text=json.dumps({
                        "status": "starting",
                        "message": "前端服务正在启动，请稍候...",
                        "estimated_time": CONFIG["MAX_STARTUP_TIME"] - int(time.time() - self.status.start_time)
                    }),
                    content_type='application/json',
                    status=202
                )
            
            # 尝试启动服务
            if not self.status.should_retry():
                return web.Response(
                    text=json.dumps({
                        "error": "服务启动失败",
                        "message": "前端服务多次启动失败，请联系管理员",
                        "error_count": self.status.error_count
                    }),
                    content_type='application/json',
                    status=503
                )
            
            # 启动服务
            success = await self.start_frontend_service()
            if not success:
                return web.Response(
                    text=json.dumps({
                        "error": "服务启动失败",
                        "message": "前端服务启动失败，请稍后重试",
                        "error_count": self.status.error_count
                    }),
                    content_type='application/json',
                    status=503
                )

        # 服务运行中，重定向到实际服务
        target_url = f"http://localhost:{CONFIG['FRONTEND_PORT']}{request.path}"
        
        # 如果是HTML请求，返回重定向页面
        if 'text/html' in request.headers.get('Accept', ''):
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta http-equiv="refresh" content="0;url={target_url}">
                <title>重定向中...</title>
            </head>
            <body>
                <p>正在重定向到前端服务...</p>
                <script>window.location.href = '{target_url}';</script>
            </body>
            </html>
            """
            return web.Response(text=html_content, content_type='text/html')
        
        # 其他请求返回重定向信息
        return web.Response(
            text=json.dumps({
                "redirect": target_url,
                "status": "running"
            }),
            content_type='application/json',
            status=307
        )

    def _is_browser_supported(self, user_agent: str) -> bool:
        """检查浏览器是否支持"""
        user_agent_lower = user_agent.lower()
        
        for browser in CONFIG["SUPPORTED_BROWSERS"]:
            if browser.lower() in user_agent_lower:
                return True
        
        # 允许其他浏览器但记录警告
        if user_agent:
            logger.warning(f"不常见的浏览器: {user_agent}")
        
        return True  # 默认允许所有浏览器

    async def health_check_task(self):
        """健康检查任务"""
        while True:
            try:
                if self.status.is_running:
                    # 检查服务是否仍然健康
                    if not await self.check_service_health():
                        logger.warning("前端服务健康检查失败，标记为停止")
                        self.status.set_stopped()
                
                await asyncio.sleep(CONFIG["HEALTH_CHECK_INTERVAL"])
            except Exception as e:
                logger.error(f"健康检查任务异常: {e}")
                await asyncio.sleep(CONFIG["HEALTH_CHECK_INTERVAL"])

    async def cleanup(self):
        """清理资源"""
        await self.stop_frontend_service()
        if self.session:
            await self.session.close()

async def create_app():
    """创建应用"""
    app = web.Application()
    manager = FrontendServiceManager()
    
    # 添加路由
    app.router.add_route('*', '/{path:.*}', manager.handle_request)
    
    # 启动健康检查任务
    app['manager'] = manager
    app.on_startup.append(lambda app: asyncio.create_task(manager.health_check_task()))
    app.on_cleanup.append(lambda app: asyncio.create_task(manager.cleanup()))
    
    return app

def main():
    """主函数"""
    logger.info("启动前端服务自动启动器...")
    logger.info(f"配置: 前端端口={CONFIG['FRONTEND_PORT']}, 代理端口={CONFIG['PROXY_PORT']}")
    
    # 设置信号处理
    def signal_handler(signum, frame):
        logger.info("收到终止信号，优雅关闭...")
        asyncio.get_event_loop().stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动应用
    web.run_app(create_app(), port=CONFIG['PROXY_PORT'], host='0.0.0.0')

if __name__ == "__main__":
    main()