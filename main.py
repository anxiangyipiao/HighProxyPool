# FILE: main.py
import asyncio
import signal
import sys
from core.proxy_manager import ProxyManager
from utils.scheduler import scheduler
from utils.logger import logger
from config.settings import config_manager

class ProxyPoolApp:
    """代理池应用主类"""
    
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.config = config_manager.config
        self._running = False
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"收到信号 {signum}，准备关闭应用...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start(self):
        """启动应用"""
        logger.info("HighProxyPool 应用启动中...")
        
        try:
            # 设置信号处理
            self.setup_signal_handlers()
            
            # 启动调度器
            scheduler.start()
            
            # 添加代理获取任务
            scheduler.add_job(
                func=self.proxy_manager.run_fetch_proxies,
                trigger='interval',
                seconds=self.config.scheduler.fetch_interval,
                job_id='fetch_proxies'
            )
            
            # 添加代理验证任务
            scheduler.add_job(
                func=self.proxy_manager.run_clean_proxies,
                trigger='interval',
                seconds=self.config.scheduler.verifier_interval,
                job_id='clean_proxies'
            )
            
            self._running = True
            logger.info("代理池应用启动成功")
            
            # 保持运行
            scheduler.keep_alive()
            
        except Exception as e:
            logger.error(f"启动应用失败: {e}")
            self.stop()
            sys.exit(1)
    
    def stop(self):
        """停止应用"""
        if self._running:
            logger.info("正在关闭代理池应用...")
            
            try:
                # 停止调度器
                scheduler.stop()
                
                # 关闭代理管理器
                asyncio.run(self.proxy_manager.close())
                
                self._running = False
                logger.info("代理池应用已关闭")
                
            except Exception as e:
                logger.error(f"关闭应用时发生错误: {e}")

def main():
    """主函数"""
    app = ProxyPoolApp()
    app.start()

if __name__ == "__main__":
    main()


