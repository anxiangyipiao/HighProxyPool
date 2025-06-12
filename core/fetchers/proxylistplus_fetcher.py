from typing import List, Dict
import json
from .base_fetcher import BaseFetcher
from ..interfaces.fetcher_interface import ProxyFetcherInterface
from utils.logger import logger
from utils.exceptions import ProxyFetchError

class ProxyListPlusFetcher(BaseFetcher, ProxyFetcherInterface):
    """ProxyList.plus 代理获取器"""
    
    def __init__(self):
        super().__init__()
        self.url = "https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1"
    
    def get_name(self) -> str:
        return "ProxyList.plus"
    
    async def fetch_proxies(self) -> List[Dict[str, str]]:
        """获取ProxyList.plus代理"""
        try:
            logger.info(f"开始获取 {self.get_name()} 代理")
            content = await self.fetch_url(self.url)
            return self._parse_proxies(content)
        except Exception as e:
            logger.error(f"获取 {self.get_name()} 代理失败: {e}")
            raise ProxyFetchError(f"获取 {self.get_name()} 代理失败: {e}")
    
    def _parse_proxies(self, content: str) -> List[Dict[str, str]]:
        """解析代理"""
        proxies = []
        try:
            # 简单的正则匹配IP:PORT格式
            import re
            pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})'
            matches = re.findall(pattern, content)
            
            for ip, port in matches:
                # 基本的IP有效性检查
                ip_parts = ip.split('.')
                if all(0 <= int(part) <= 255 for part in ip_parts):
                    proxy = {"http": f"http://{ip}:{port}"}
                    proxies.append(proxy)
                    logger.debug(f"解析到代理: {ip}:{port}")
            
            logger.info(f"成功解析 {len(proxies)} 个代理")
            return proxies
        except Exception as e:
            logger.error(f"解析代理失败: {e}")
            raise ProxyFetchError(f"解析代理失败: {e}")