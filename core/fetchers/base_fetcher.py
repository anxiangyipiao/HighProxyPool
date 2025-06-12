import aiohttp
import asyncio
from typing import Dict, Optional
from utils.logger import logger
from utils.exceptions import ProxyFetchError

class BaseFetcher:
    """基础获取器"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Connection": "close",
        }
    
    async def fetch_url(self, url: str, headers: Optional[Dict[str, str]] = None) -> str:
        """获取网页内容"""
        headers = headers or self.headers
        
        for attempt in range(self.max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            content = await response.text()
                            logger.debug(f"成功获取 {url} 内容")
                            return content
                        else:
                            logger.warning(f"获取 {url} 失败，状态码: {response.status}")
            except Exception as e:
                logger.warning(f"第 {attempt + 1} 次尝试获取 {url} 失败: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                else:
                    raise ProxyFetchError(f"获取 {url} 失败: {e}")
        
        raise ProxyFetchError(f"获取 {url} 失败，已重试 {self.max_retries} 次")