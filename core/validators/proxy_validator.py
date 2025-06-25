import aiohttp
import asyncio
from typing import Dict, List
from ..interfaces.validator_interface import ProxyValidatorInterface
from storage.storage_interface import StorageInterface
from utils.logger import logger
from utils.exceptions import ProxyValidationError

class ProxyValidator(ProxyValidatorInterface):
    """代理验证器"""
    
    def __init__(self, storage: StorageInterface, check_url: str, timeout: int = 10, max_concurrent: int = 50, delay: float = 1):
        self.storage = storage
        self.check_url = check_url
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.delay = delay  # 添加延迟参数，单位为秒
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    async def validate_proxy(self, proxy: Dict[str, str]) -> bool:
        """验证单个代理"""
        try:
            proxy_url = proxy.get('http', '')
            if not proxy_url:
                return False
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    self.check_url, 
                    proxy=proxy_url, 
                    headers=self.headers
                ) as response:
                    is_valid = response.status == 200
                    if is_valid:
                        logger.debug(f"代理验证成功: {proxy}")
                    else:
                        logger.debug(f"代理验证失败: {proxy}, 状态码: {response.status}")
                    return is_valid
        except Exception as e:
            logger.debug(f"代理验证异常: {proxy}, 错误: {e}")
            return False
    
    async def validate_proxies(self, proxies: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """批量验证代理"""
        valid_proxies = []
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def validate_single(proxy):
            async with semaphore:
                if await self.validate_proxy(proxy):
                    valid_proxies.append(proxy)
                await asyncio.sleep(self.delay)  # 添加延迟
        
        tasks = [validate_single(proxy) for proxy in proxies]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"批量验证完成，有效代理: {len(valid_proxies)}/{len(proxies)}")
        return valid_proxies
    
    async def clean_invalid_proxies(self):
        """清理无效代理"""
        logger.info("开始清理无效代理...")
        try:
            all_proxies = await self.storage.get_all_proxies()
            logger.info(f"当前代理总数: {len(all_proxies)}")
            
            if not all_proxies:
                logger.info("代理池为空，无需清理")
                return
            
            # 批量验证
            valid_proxies = await self.validate_proxies(all_proxies)
            
            # 移除无效代理
            invalid_count = 0
            for proxy in all_proxies:
                if proxy not in valid_proxies:
                    await self.storage.remove_proxy(proxy)
                    invalid_count += 1
            
            logger.info(f"清理完成，移除无效代理: {invalid_count} 个，剩余有效代理: {len(valid_proxies)} 个")
            
        except Exception as e:
            logger.error(f"清理无效代理时发生错误: {e}")
            raise ProxyValidationError(f"清理无效代理失败: {e}")

