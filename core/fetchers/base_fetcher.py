import aiohttp
import asyncio
from typing import Dict, Optional
from utils.logger import logger
from utils.exceptions import ProxyFetchError

try:
    from DrissionPage import WebPage
    DRISSION_AVAILABLE = True
except ImportError:
    DRISSION_AVAILABLE = False
    logger.warning("DrissionPage 未安装，浏览器获取功能不可用")

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
    
    def fetch_url_with_browser(self, url: str, wait_time: int = 3, headless: bool = True) -> str:
        """使用浏览器获取网页内容（适用于需要JS渲染的页面）
        
        Args:
            url: 目标网址
            wait_time: 页面加载等待时间（秒）
            headless: 是否使用无头模式
            
        Returns:
            网页内容
            
        Raises:
            ProxyFetchError: 获取失败时抛出
        """
        if not DRISSION_AVAILABLE:
            raise ProxyFetchError("DrissionPage 未安装，无法使用浏览器获取功能")
        
        page = None
        try:
            # 创建 WebPage 实例
            page = WebPage()
            
            # 设置用户代理
            page.set.user_agent(self.headers.get("User-Agent", ""))
            
            logger.debug(f"使用浏览器访问: {url}")
            
            # 访问页面
            page.get(url)
            
            # 等待页面加载完成
            if wait_time > 0:
                page.wait(wait_time)
            
            # 获取页面内容
            content = page.html
            
            if not content:
                raise ProxyFetchError(f"浏览器获取 {url} 返回空内容")
            
            logger.debug(f"成功使用浏览器获取 {url} 内容")
            return content
            
        except Exception as e:
            logger.error(f"浏览器获取 {url} 失败: {e}")
            raise ProxyFetchError(f"浏览器获取 {url} 失败: {e}")
        finally:
            # 确保关闭浏览器
            if page:
                try:
                    page.quit()
                except:
                    pass
    
    async def fetch_url_with_browser_async(self, url: str, wait_time: int = 3, headless: bool = True) -> str:
        """异步版本的浏览器获取方法
        
        Args:
            url: 目标网址
            wait_time: 页面加载等待时间（秒）
            headless: 是否使用无头模式
            
        Returns:
            网页内容
            
        Raises:
            ProxyFetchError: 获取失败时抛出
        """
        if not DRISSION_AVAILABLE:
            raise ProxyFetchError("DrissionPage 未安装，无法使用浏览器获取功能")
        
        # 直接复用同步方法的逻辑，避免代码重复
        return await asyncio.to_thread(
            self.fetch_url_with_browser, 
            url, 
            wait_time, 
            headless
        )

