from typing import List, Dict
import re
from .base_fetcher import BaseFetcher
from ..interfaces.fetcher_interface import ProxyFetcherInterface
from utils.logger import logger
from utils.exceptions import ProxyFetchError

class KuaidailiFetcher(BaseFetcher, ProxyFetcherInterface):
    """快代理获取器"""
    
    def __init__(self):
        super().__init__()
        self.urls = [
            "https://www.kuaidaili.com/free/inha/",
            "https://www.kuaidaili.com/free/intr/"
        ]
    
    def get_name(self) -> str:
        return "快代理"
    
    async def fetch_proxies(self) -> List[Dict[str, str]]:
        """获取快代理"""
        all_proxies = []
        
        for url in self.urls:
            try:
                logger.info(f"从 {url} 获取代理")
                content = await self.fetch_url(url)
                proxies = self._parse_proxies(content)
                all_proxies.extend(proxies)
            except Exception as e:
                logger.error(f"获取 {url} 失败: {e}")
                continue
        
        logger.info(f"{self.get_name()} 总计获取 {len(all_proxies)} 个代理")
        return all_proxies
    
    def _parse_proxies(self, content: str) -> List[Dict[str, str]]:
        """解析代理"""
        proxies = []
        try:
            # 使用正则表达式匹配IP和端口
            pattern = r'(\d+\.\d+\.\d+\.\d+)\s*</td>\s*<td[^>]*>\s*(\d+)'
            matches = re.findall(pattern, content)
            
            for ip, port in matches:
                if ip and port:
                    proxy = {"http": f"http://{ip}:{port}"}
                    proxies.append(proxy)
                    logger.debug(f"解析到代理: {ip}:{port}")
            
            logger.info(f"成功解析 {len(proxies)} 个代理")
            return proxies
        except Exception as e:
            logger.error(f"解析代理失败: {e}")
            raise ProxyFetchError(f"解析代理失败: {e}")