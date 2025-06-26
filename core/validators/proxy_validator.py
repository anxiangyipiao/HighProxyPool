import aiohttp
import asyncio
from typing import Dict, List
from ..interfaces.validator_interface import ProxyValidatorInterface
from storage.storage_interface import StorageInterface
from utils.logger import logger
from utils.exceptions import ProxyValidationError

class ProxyValidator(ProxyValidatorInterface):
    """代理验证器"""
    
    def __init__(self, storage: StorageInterface, check_url: str, timeout: int = 10, max_concurrent: int = 50, delay: float = 0.5):
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
        """清理无效代理（优化版本，支持分批处理）"""
        logger.info("开始清理无效代理...")
        batch_size = 100  # 分批处理，每批100个代理
        max_retries = 3
        
        for retry in range(max_retries):
            try:
                # 先获取代理总数
                total_count = await self.storage.get_proxy_count()
                logger.info(f"当前代理总数: {total_count}")
                
                if total_count == 0:
                    logger.info("代理池为空，无需清理")
                    return
                
                # 如果代理数量较少，直接获取所有代理
                if total_count <= batch_size:
                    all_proxies = await self.storage.get_all_proxies()
                    valid_proxies = await self.validate_proxies(all_proxies)
                    
                    # 计算需要移除的代理
                    invalid_proxies = [proxy for proxy in all_proxies if proxy not in valid_proxies]
                    
                    if invalid_proxies:
                        # 批量移除无效代理
                        removed_count = await self.storage.batch_remove_proxies(invalid_proxies)
                        logger.info(f"清理完成，移除无效代理: {removed_count} 个，剩余有效代理: {len(valid_proxies)} 个")
                    else:
                        logger.info("所有代理都有效，无需清理")
                else:
                    # 大量代理时，采用随机抽样验证策略
                    logger.info(f"代理数量较多({total_count})，采用抽样验证策略")
                    await self._clean_by_sampling()
                
                return  # 成功完成，退出重试循环
                
            except Exception as e:
                logger.error(f"清理无效代理时发生错误 (尝试 {retry + 1}/{max_retries}): {e}")
                if retry == max_retries - 1:
                    # 最后一次重试失败，记录错误但不抛出异常
                    logger.error("清理无效代理多次尝试失败，请检查Redis连接状态")
                    return
                
                # 等待后重试
                await asyncio.sleep(5 * (retry + 1))
    
    async def _clean_by_sampling(self):
        """通过抽样方式清理代理（用于大量代理的情况）"""
        sample_size = 200  # 每次抽样验证200个代理
        invalid_count = 0
        total_validated = 0
        
        for batch_num in range(5):  # 最多进行5轮抽样
            try:
                # 随机获取一批代理进行验证
                sample_proxies = []
                for _ in range(sample_size):
                    proxy = await self.storage.get_random_proxy()
                    if proxy and proxy not in sample_proxies:
                        sample_proxies.append(proxy)
                    if len(sample_proxies) >= sample_size:
                        break
                
                if not sample_proxies:
                    break
                
                logger.info(f"第 {batch_num + 1} 轮抽样验证，验证 {len(sample_proxies)} 个代理")
                
                # 验证这批代理
                valid_proxies = await self.validate_proxies(sample_proxies)
                invalid_proxies = [proxy for proxy in sample_proxies if proxy not in valid_proxies]
                
                # 移除无效代理
                if invalid_proxies:
                    removed = await self.storage.batch_remove_proxies(invalid_proxies)
                    invalid_count += removed
                
                total_validated += len(sample_proxies)
                
                # 添加延迟避免频繁操作
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"第 {batch_num + 1} 轮抽样验证失败: {e}")
                break
        
        logger.info(f"抽样清理完成，共验证 {total_validated} 个代理，移除无效代理: {invalid_count} 个")

