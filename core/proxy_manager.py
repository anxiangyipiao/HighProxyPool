import asyncio
import threading
from typing import List, Dict, Optional
from .fetchers.bajiu_fetcher import BajiuFetcher
from .fetchers.kuaidaili_fetcher import KuaidailiFetcher
from .fetchers.proxylistplus_fetcher import ProxyListPlusFetcher
from .validators.proxy_validator import ProxyValidator
from storage.storage_interface import StorageInterface
from storage.redis_storage import RedisStorage
from storage.cached_redis_storage import CachedRedisStorage
from config.settings import config_manager
from utils.logger import logger
from utils.exceptions import ProxyFetchError, ProxyValidationError

class ProxyManager:
    """代理管理器 - 统一管理代理获取、验证和存储"""
    
    def __init__(self, storage: Optional[StorageInterface] = None):
        self.storage = storage or RedisStorage()
        self.config = config_manager.config
        
        # 初始化获取器 - 添加更多代理源
        self.fetchers = [
            BajiuFetcher(),
            # KuaidailiFetcher(),
            # ProxyListPlusFetcher(),
            # 可以轻松添加更多获取器
        ]
        
        # 初始化验证器
        self.validator = ProxyValidator(
            storage=self.storage,
            check_url=self.config.scheduler.verifier_url,
            timeout=10,
            max_concurrent=50
        )
    
    async def fetch_all_proxies(self) -> int:
        """从所有源获取代理"""
        total_added = 0
        
        # 顺序获取代理，避免事件循环冲突
        for fetcher in self.fetchers:
            try:
                added_count = await self._fetch_from_source(fetcher)
                total_added += added_count
            except Exception as e:
                logger.error(f"从 {fetcher.get_name()} 获取代理时发生异常: {e}")
        
        logger.info(f"本次获取总计添加 {total_added} 个有效代理")
        return total_added
    
    async def _fetch_from_source(self, fetcher) -> int:
        """从单个源获取代理"""
        added_count = 0
        try:
            logger.info(f"开始从 {fetcher.get_name()} 获取代理")
            proxies = await fetcher.fetch_proxies()
            
            # 验证并保存代理
            if proxies:
                valid_proxies = await self.validator.validate_proxies(proxies)
                for proxy in valid_proxies:
                    if await self.storage.add_proxy(proxy):
                        added_count += 1
                
                logger.info(f"从 {fetcher.get_name()} 成功添加 {len(valid_proxies)} 个有效代理")
            else:
                logger.warning(f"从 {fetcher.get_name()} 未获取到代理")
                
        except Exception as e:
            logger.error(f"从 {fetcher.get_name()} 获取代理失败: {e}")
        
        return added_count
    
    async def get_proxy(self) -> Optional[Dict[str, str]]:
        """获取一个可用代理"""
        try:
            proxy = await self.storage.get_random_proxy()
            if proxy:
                # 快速验证代理是否仍然有效
                if await self.validator.validate_proxy(proxy):
                    return proxy
                else:
                    # 代理无效，移除并重试
                    await self.storage.remove_proxy(proxy)
                    logger.warning(f"移除无效代理: {proxy}")
                    return await self.get_proxy()  # 递归重试
            return None
        except Exception as e:
            logger.error(f"获取代理失败: {e}")
            return None
    
    async def get_proxy_count(self) -> int:
        """获取代理池中的代理数量"""
        try:
            return await self.storage.get_proxy_count()
        except Exception as e:
            logger.error(f"获取代理数量失败: {e}")
            return 0
    
    async def clean_invalid_proxies(self):
        """清理无效代理"""
        try:
            await self.validator.clean_invalid_proxies()
        except Exception as e:
            logger.error(f"清理无效代理失败: {e}")
            raise ProxyValidationError(f"清理无效代理失败: {e}")
    
    async def get_proxy_statistics(self) -> Dict[str, any]:
        """获取代理统计信息"""
        try:
            total_count = await self.storage.get_proxy_count()
            all_proxies = await self.storage.get_all_proxies()
            
            # 统计不同类型的代理
            http_count = len([p for p in all_proxies if 'http' in p])
            
            return {
                'total_count': total_count,
                'http_count': http_count,
                'fetcher_count': len(self.fetchers),
                'fetcher_names': [f.get_name() for f in self.fetchers]
            }
        except Exception as e:
            logger.error(f"获取代理统计信息失败: {e}")
            return {}
    
    def run_fetch_proxies(self):
        """同步方法，用于在调度器中调用"""
        try:
            logger.info("开始执行代理获取任务...")
            result = self._run_async_task(self.fetch_all_proxies())
            logger.info(f"代理获取任务完成，添加了 {result} 个代理")
        except Exception as e:
            logger.error(f"执行代理获取任务时发生错误: {e}")
    
    def run_clean_proxies(self):
        """同步方法，用于在调度器中调用"""
        try:
            logger.info("开始执行代理清理任务...")
            self._run_async_task(self.clean_invalid_proxies())
            logger.info("代理清理任务完成")
        except Exception as e:
            logger.error(f"执行代理清理任务时发生错误: {e}")
    
    def _run_async_task(self, coro):
        """安全地运行异步任务的辅助方法"""
        try:
            # 尝试获取当前运行的事件循环
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # 如果已有运行中的循环，在新线程中创建新的事件循环
                import concurrent.futures
                import threading
                
                def run_in_new_loop():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(coro)
                    finally:
                        new_loop.close()
                        asyncio.set_event_loop(None)
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_new_loop)
                    return future.result()
            else:
                # 循环存在但未运行，直接运行
                return loop.run_until_complete(coro)
                
        except RuntimeError as e:
            if "no running event loop" in str(e).lower() or "no current event loop" in str(e).lower():
                # 没有事件循环，创建新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(coro)
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)
            else:
                # 其他 RuntimeError，可能是循环已关闭
                logger.warning(f"事件循环异常: {e}，创建新的事件循环")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(coro)
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)
    
    async def close(self):
        """关闭资源"""
        if hasattr(self.storage, 'close'):
            await self.storage.close()