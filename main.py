# FILE: main.py
import asyncio
import signal
import sys
from core.proxy_manager import ProxyManager
from utils.scheduler import async_scheduler
from utils.logger import logger
from config.settings import config_manager

class AsyncProxyPoolApp:
    """异步代理池应用主类"""
    
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.config = config_manager.config
        self._running = False
        self._shutdown_event = asyncio.Event()
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"收到信号 {signum}，准备关闭应用...")
            # 设置关闭事件
            asyncio.create_task(self._shutdown_event.set())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """启动异步应用"""
        logger.info("HighProxyPool 异步应用启动中...")
        
        try:
            # 设置信号处理
            self.setup_signal_handlers()
            
            # 启动异步调度器
            await async_scheduler.start()
            
            # 添加代理获取任务 - 直接使用异步方法
            async_scheduler.add_async_job(
                func=self.proxy_manager.fetch_all_proxies,
                trigger='interval',
                seconds=self.config.scheduler.fetch_interval,
                job_id='fetch_proxies'
            )
            
            # 添加代理验证任务
            async_scheduler.add_async_job(
                func=self.proxy_manager.clean_invalid_proxies,
                trigger='interval',
                seconds=self.config.scheduler.verifier_interval,
                job_id='clean_proxies'
            )
            
            self._running = True
            logger.info("异步代理池应用启动成功")
            
            # 立即执行一次代理获取
            logger.info("立即执行一次代理获取...")
            await self.proxy_manager.fetch_all_proxies()
            
            # 等待关闭信号
            await self._wait_for_shutdown()
            
        except Exception as e:
            logger.error(f"启动异步应用失败: {e}")
            await self.stop()
            sys.exit(1)
    
    async def _wait_for_shutdown(self):
        """等待关闭信号"""
        logger.info("异步调度器运行中，按 Ctrl+C 退出...")
        
        try:
            while self._running:
                # 检查是否收到关闭信号
                try:
                    await asyncio.wait_for(self._shutdown_event.wait(), timeout=60.0)
                    # 收到关闭信号
                    break
                except asyncio.TimeoutError:
                    # 定期检查调度器状态
                    if async_scheduler._is_started:
                        job_count = len(async_scheduler.get_jobs())
                        proxy_count = await self.proxy_manager.get_proxy_count()
                        logger.info(f"调度器运行中 - 任务数: {job_count}, 代理数: {proxy_count}")
                    
        except (KeyboardInterrupt, SystemExit):
            logger.info("收到退出信号...")
        finally:
            await self.stop()
    
    async def stop(self):
        """停止异步应用"""
        if self._running:
            logger.info("正在关闭异步代理池应用...")
            
            try:
                # 停止调度器
                await async_scheduler.stop()
                
                # 关闭代理管理器
                await self.proxy_manager.close()
                
                self._running = False
                logger.info("异步代理池应用已关闭")
                
            except Exception as e:
                logger.error(f"关闭异步应用时发生错误: {e}")

async def async_main():
    """异步主函数"""
    app = AsyncProxyPoolApp()
    await app.start()

def main():
    """主函数 - 运行异步应用"""
    try:
        # 运行异步应用
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("应用被用户中断")
    except Exception as e:
        logger.error(f"应用运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


