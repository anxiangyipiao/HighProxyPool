from abc import ABC, abstractmethod
from typing import List, Dict

class ProxyFetcherInterface(ABC):
    """代理获取器接口"""
    
    @abstractmethod
    async def fetch_proxies(self) -> List[Dict[str, str]]:
        """获取代理列表"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取获取器名称"""
        pass