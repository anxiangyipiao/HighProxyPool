import redis.asyncio as redis
import json
import asyncio
from typing import List, Optional, Dict, Any
from .storage_interface import StorageInterface
from config.settings import config_manager
from utils.logger import logger
from utils.exceptions import StorageError

class RedisStorage(StorageInterface):
    """Redis 存储实现"""
    
    def __init__(self):
        self.config = config_manager.config.redis
        self.pool_name = config_manager.config.scheduler.proxy_pool_name
        self._redis: Optional[redis.Redis] = None
    
    async def _get_connection(self) -> redis.Redis:
        """获取 Redis 连接"""
        if self._redis is None:
            try:
                self._redis = redis.Redis(
                    host=self.config.host,
                    port=self.config.port,
                    password=self.config.password,
                    db=self.config.db,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                # 测试连接
                await self._redis.ping()
                logger.info("Redis 连接成功")
            except Exception as e:
                logger.error(f"Redis 连接失败: {e}")
                raise StorageError(f"Redis 连接失败: {e}")
        return self._redis
    
    async def add_proxy(self, proxy: Dict[str, str]) -> bool:
        """添加代理"""
        try:
            redis_conn = await self._get_connection()
            proxy_str = json.dumps(proxy, ensure_ascii=False)
            result = await redis_conn.sadd(self.pool_name, proxy_str)
            if result == 1:
                logger.info(f"代理添加成功: {proxy}")
                return True
            else:
                logger.debug(f"代理已存在: {proxy}")
                return False
        except Exception as e:
            logger.error(f"添加代理失败: {e}")
            raise StorageError(f"添加代理失败: {e}")
    
    async def remove_proxy(self, proxy: Dict[str, str]) -> bool:
        """移除代理"""
        try:
            redis_conn = await self._get_connection()
            proxy_str = json.dumps(proxy, ensure_ascii=False)
            result = await redis_conn.srem(self.pool_name, proxy_str)
            if result > 0:
                logger.info(f"代理移除成功: {proxy}")
                return True
            return False
        except Exception as e:
            logger.error(f"移除代理失败: {e}")
            raise StorageError(f"移除代理失败: {e}")
    
    async def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """获取随机代理"""
        try:
            redis_conn = await self._get_connection()
            proxy_str = await redis_conn.srandmember(self.pool_name)
            if proxy_str:
                return json.loads(proxy_str)
            return None
        except Exception as e:
            logger.error(f"获取随机代理失败: {e}")
            raise StorageError(f"获取随机代理失败: {e}")
    
    async def get_all_proxies(self) -> List[Dict[str, str]]:
        """获取所有代理"""
        try:
            redis_conn = await self._get_connection()
            proxy_strs = await redis_conn.smembers(self.pool_name)
            return [json.loads(proxy_str) for proxy_str in proxy_strs]
        except Exception as e:
            logger.error(f"获取所有代理失败: {e}")
            raise StorageError(f"获取所有代理失败: {e}")
    
    async def get_proxy_count(self) -> int:
        """获取代理数量"""
        try:
            redis_conn = await self._get_connection()
            return await redis_conn.scard(self.pool_name)
        except Exception as e:
            logger.error(f"获取代理数量失败: {e}")
            raise StorageError(f"获取代理数量失败: {e}")
    
    async def clear_proxies(self) -> bool:
        """清空所有代理"""
        try:
            redis_conn = await self._get_connection()
            await redis_conn.delete(self.pool_name)
            logger.info("代理池已清空")
            return True
        except Exception as e:
            logger.error(f"清空代理池失败: {e}")
            raise StorageError(f"清空代理池失败: {e}")
    
    async def close(self):
        """关闭连接"""
        if self._redis:
            await self._redis.close()
            logger.info("Redis 连接已关闭")