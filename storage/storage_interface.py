from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class StorageInterface(ABC):
    """存储接口"""
    
    @abstractmethod
    async def add_proxy(self, proxy: Dict[str, str]) -> bool:
        """添加代理"""
        pass
    
    @abstractmethod
    async def remove_proxy(self, proxy: Dict[str, str]) -> bool:
        """移除代理"""
        pass
    
    @abstractmethod
    async def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """获取随机代理"""
        pass
    
    @abstractmethod
    async def get_all_proxies(self) -> List[Dict[str, str]]:
        """获取所有代理"""
        pass
    
    @abstractmethod
    async def get_proxy_count(self) -> int:
        """获取代理数量"""
        pass
    
    @abstractmethod
    async def clear_proxies(self) -> bool:
        """清空所有代理"""
        pass