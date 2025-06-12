from typing import List, Dict
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher
from ..interfaces.fetcher_interface import ProxyFetcherInterface
from utils.logger import logger
from utils.exceptions import ProxyFetchError

class BajiuFetcher(BaseFetcher, ProxyFetcherInterface):
    """89免费代理获取器"""
    
    def __init__(self):
        super().__init__()
        self.url = "http://www.89ip.cn/"
    
    def get_name(self) -> str:
        return "89免费代理"
    
    async def fetch_proxies(self) -> List[Dict[str, str]]:
        """获取89免费代理"""
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
            soup = BeautifulSoup(content, "html.parser")
            table = soup.find("table", class_="layui-table")
            if not table:
                logger.warning("未找到代理表格")
                return proxies
            
            tbody = table.find("tbody")
            if not tbody:
                logger.warning("未找到代理表格主体")
                return proxies
            
            rows = tbody.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    host = cells[0].get_text().strip()
                    port = cells[1].get_text().strip()
                    if host and port:
                        proxy = {"http": f"http://{host}:{port}"}
                        proxies.append(proxy)
                        logger.debug(f"解析到代理: {host}:{port}")
            
            logger.info(f"成功解析 {len(proxies)} 个代理")
            return proxies
        except Exception as e:
            logger.error(f"解析代理失败: {e}")
            raise ProxyFetchError(f"解析代理失败: {e}")