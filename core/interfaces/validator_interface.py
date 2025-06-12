from abc import ABC, abstractmethod
from typing import Dict, List

class ProxyValidatorInterface(ABC):
    """代理验证器接口"""
    
    @abstractmethod
    async def validate_proxy(self, proxy: Dict[str, str]) -> bool:
        """验证单个代理"""
        pass
    
    @abstractmethod
    async def validate_proxies(self, proxies: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """批量验证代理"""
        pass