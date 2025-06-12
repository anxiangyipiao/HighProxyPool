"""
测试代理管理器功能
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from core.proxy_manager import ProxyManager
from storage.redis_storage import RedisStorage
from core.validators.proxy_validator import ProxyValidator

class TestProxyManager:
    """代理管理器测试类"""
    
    @pytest.fixture
    async def mock_storage(self):
        """模拟存储"""
        storage = Mock(spec=RedisStorage)
        storage.add_proxy = AsyncMock(return_value=True)
        storage.get_random_proxy = AsyncMock(return_value={"http": "http://127.0.0.1:8080"})
        storage.get_proxy_count = AsyncMock(return_value=10)
        storage.get_all_proxies = AsyncMock(return_value=[])
        storage.remove_proxy = AsyncMock(return_value=True)
        return storage
    
    @pytest.fixture
    async def proxy_manager(self, mock_storage):
        """创建代理管理器实例"""
        return ProxyManager(storage=mock_storage)
    
    @pytest.mark.asyncio
    async def test_get_proxy_count(self, proxy_manager):
        """测试获取代理数量"""
        count = await proxy_manager.get_proxy_count()
        assert count == 10
    
    @pytest.mark.asyncio
    async def test_get_proxy_statistics(self, proxy_manager):
        """测试获取代理统计信息"""
        stats = await proxy_manager.get_proxy_statistics()
        assert isinstance(stats, dict)
        assert 'total_count' in stats
        assert 'fetcher_count' in stats
        assert 'fetcher_names' in stats
    
    @pytest.mark.asyncio
    async def test_fetch_from_source(self, proxy_manager):
        """测试从单个源获取代理"""
        # 模拟获取器
        mock_fetcher = Mock()
        mock_fetcher.get_name.return_value = "测试获取器"
        mock_fetcher.fetch_proxies = AsyncMock(return_value=[
            {"http": "http://127.0.0.1:8080"},
            {"http": "http://127.0.0.1:8081"}
        ])
        
        # 模拟验证器
        proxy_manager.validator.validate_proxies = AsyncMock(return_value=[
            {"http": "http://127.0.0.1:8080"}
        ])
        
        result = await proxy_manager._fetch_from_source(mock_fetcher)
        assert result == 1  # 一个代理被成功添加