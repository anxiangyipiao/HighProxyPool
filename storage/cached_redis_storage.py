import asyncio
import random
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from .storage_interface import StorageInterface
from config.settings import config_manager
from utils.logger import logger
from utils.exceptions import StorageError

class CachedRedisStorage(StorageInterface):
    """增强的Redis存储实现，带缓存和性能优化"""
    
    def __init__(self):
        self.config = config_manager.config.redis
        self.pool_name = config_manager.config.scheduler.proxy_pool_name
        self._redis = None
        
        # 本地缓存
        self._proxy_cache: Set[str] = set()
        self._cache_last_update = None
        self._cache_ttl = 300  # 5分钟缓存TTL
        
        # 性能统计
        self._stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'redis_operations': 0
        }
    
    async def _get_connection(self):
        """获取 Redis 连接池"""
        if self._redis is None:
            import redis.asyncio as redis
            try:
                # 使用连接池提高性能
                pool = redis.ConnectionPool(
                    host=self.config.host,
                    port=self.config.port,
                    password=self.config.password or None,
                    db=self.config.db,
                    max_connections=self.config.max_connections,
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout,
                    decode_responses=True
                )
                
                self._redis = redis.Redis(connection_pool=pool)
                # 测试连接
                await self._redis.ping()
                logger.info("Redis 连接池创建成功")
            except Exception as e:
                logger.error(f"Redis 连接失败: {e}")
                raise StorageError(f"Redis 连接失败: {e}")
        return self._redis
    
    async def _update_cache(self):
        """更新本地缓存"""
        if (self._cache_last_update is None or 
            datetime.now() - self._cache_last_update > timedelta(seconds=self._cache_ttl)):
            
            try:
                redis_conn = await self._get_connection()
                self._stats['redis_operations'] += 1
                proxy_strs = await redis_conn.smembers(self.pool_name)
                self._proxy_cache = set(proxy_strs)
                self._cache_last_update = datetime.now()
                logger.debug(f"缓存已更新，包含 {len(self._proxy_cache)} 个代理")
            except Exception as e:
                logger.error(f"更新缓存失败: {e}")
    
    async def add_proxy(self, proxy: Dict[str, str]) -> bool:
        """添加代理"""
        try:
            import json
            redis_conn = await self._get_connection()
            proxy_str = json.dumps(proxy, ensure_ascii=False, sort_keys=True)
            
            self._stats['redis_operations'] += 1
            result = await redis_conn.sadd(self.pool_name, proxy_str)
            
            if result == 1:
                # 更新本地缓存
                self._proxy_cache.add(proxy_str)
                logger.debug(f"代理添加成功: {proxy}")
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
            import json
            redis_conn = await self._get_connection()
            proxy_str = json.dumps(proxy, ensure_ascii=False, sort_keys=True)
            
            self._stats['redis_operations'] += 1
            result = await redis_conn.srem(self.pool_name, proxy_str)
            
            if result > 0:
                # 更新本地缓存
                self._proxy_cache.discard(proxy_str)
                logger.debug(f"代理移除成功: {proxy}")
                return True
            return False
        except Exception as e:
            logger.error(f"移除代理失败: {e}")
            raise StorageError(f"移除代理失败: {e}")
    
    async def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """获取随机代理（优先使用缓存）"""
        try:
            # 尝试从缓存获取
            await self._update_cache()
            
            if self._proxy_cache:
                self._stats['cache_hits'] += 1
                proxy_str = random.choice(list(self._proxy_cache))
                import json
                return json.loads(proxy_str)
            else:
                # 缓存为空，直接从Redis获取
                self._stats['cache_misses'] += 1
                redis_conn = await self._get_connection()
                self._stats['redis_operations'] += 1
                proxy_str = await redis_conn.srandmember(self.pool_name)
                if proxy_str:
                    import json
                    return json.loads(proxy_str)
            
            return None
        except Exception as e:
            logger.error(f"获取随机代理失败: {e}")
            raise StorageError(f"获取随机代理失败: {e}")
    
    async def get_all_proxies(self) -> List[Dict[str, str]]:
        """获取所有代理"""
        try:
            redis_conn = await self._get_connection()
            self._stats['redis_operations'] += 1
            proxy_strs = await redis_conn.smembers(self.pool_name)
            
            import json
            return [json.loads(proxy_str) for proxy_str in proxy_strs]
        except Exception as e:
            logger.error(f"获取所有代理失败: {e}")
            raise StorageError(f"获取所有代理失败: {e}")
    
    async def get_proxy_count(self) -> int:
        """获取代理数量（优先使用缓存）"""
        try:
            await self._update_cache()
            
            if self._cache_last_update:
                self._stats['cache_hits'] += 1
                return len(self._proxy_cache)
            else:
                self._stats['cache_misses'] += 1
                redis_conn = await self._get_connection()
                self._stats['redis_operations'] += 1
                return await redis_conn.scard(self.pool_name)
        except Exception as e:
            logger.error(f"获取代理数量失败: {e}")
            raise StorageError(f"获取代理数量失败: {e}")
    
    async def clear_proxies(self) -> bool:
        """清空所有代理"""
        try:
            redis_conn = await self._get_connection()
            self._stats['redis_operations'] += 1
            await redis_conn.delete(self.pool_name)
            
            # 清空缓存
            self._proxy_cache.clear()
            self._cache_last_update = None
            
            logger.info("代理池已清空")
            return True
        except Exception as e:
            logger.error(f"清空代理池失败: {e}")
            raise StorageError(f"清空代理池失败: {e}")
    
    async def batch_add_proxies(self, proxies: List[Dict[str, str]]) -> int:
        """批量添加代理（性能优化）"""
        try:
            import json
            redis_conn = await self._get_connection()
            
            proxy_strs = [json.dumps(proxy, ensure_ascii=False, sort_keys=True) for proxy in proxies]
            
            self._stats['redis_operations'] += 1
            added_count = await redis_conn.sadd(self.pool_name, *proxy_strs)
            
            # 更新缓存
            self._proxy_cache.update(proxy_strs)
            
            logger.info(f"批量添加 {added_count} 个新代理")
            return added_count
        except Exception as e:
            logger.error(f"批量添加代理失败: {e}")
            raise StorageError(f"批量添加代理失败: {e}")
    
    async def batch_remove_proxies(self, proxies: List[Dict[str, str]]) -> int:
        """批量移除代理（性能优化）"""
        try:
            import json
            redis_conn = await self._get_connection()
            
            proxy_strs = [json.dumps(proxy, ensure_ascii=False, sort_keys=True) for proxy in proxies]
            
            self._stats['redis_operations'] += 1
            removed_count = await redis_conn.srem(self.pool_name, *proxy_strs)
            
            # 更新缓存
            for proxy_str in proxy_strs:
                self._proxy_cache.discard(proxy_str)
            
            logger.info(f"批量移除 {removed_count} 个代理")
            return removed_count
        except Exception as e:
            logger.error(f"批量移除代理失败: {e}")
            raise StorageError(f"批量移除代理失败: {e}")
    
    def get_stats(self) -> Dict[str, any]:
        """获取存储统计信息"""
        cache_total = self._stats['cache_hits'] + self._stats['cache_misses']
        cache_hit_rate = (self._stats['cache_hits'] / cache_total * 100) if cache_total > 0 else 0
        
        return {
            'cache_size': len(self._proxy_cache),
            'cache_hit_rate': f"{cache_hit_rate:.2f}%",
            'cache_hits': self._stats['cache_hits'],
            'cache_misses': self._stats['cache_misses'],
            'redis_operations': self._stats['redis_operations'],
            'cache_last_update': self._cache_last_update.isoformat() if self._cache_last_update else None
        }
    
    async def close(self):
        """关闭连接"""
        if self._redis:
            await self._redis.close()
            logger.info("Redis 连接已关闭")