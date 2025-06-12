import time
import psutil
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from utils.logger import logger

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    proxy_count: int
    request_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics_history = []
        self.max_history_size = 100
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
    
    def record_request(self, response_time: float, is_error: bool = False):
        """记录请求信息"""
        self.request_count += 1
        if is_error:
            self.error_count += 1
        self.response_times.append(response_time)
        
        # 保持响应时间列表在合理大小
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-500:]
    
    async def collect_metrics(self, proxy_count: int = 0) -> PerformanceMetrics:
        """收集系统性能指标"""
        try:
            # 系统资源使用情况
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 计算平均响应时间
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                disk_usage_percent=disk.percent,
                proxy_count=proxy_count,
                request_count=self.request_count,
                error_count=self.error_count,
                avg_response_time=avg_response_time
            )
            
            # 添加到历史记录
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"收集性能指标失败: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                disk_usage_percent=0.0,
                proxy_count=proxy_count
            )
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            uptime = time.time() - self.start_time
            
            return {
                'system': {
                    'platform': psutil.platform,
                    'python_version': f"{psutil.version_info}",
                    'cpu_count': psutil.cpu_count(),
                    'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                },
                'runtime': {
                    'uptime_seconds': uptime,
                    'uptime_formatted': str(timedelta(seconds=int(uptime))),
                    'total_requests': self.request_count,
                    'total_errors': self.error_count,
                    'error_rate': self.error_count / self.request_count if self.request_count > 0 else 0,
                }
            }
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {}
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        if not self.metrics_history:
            return {}
        
        try:
            recent_metrics = self.metrics_history[-10:]  # 最近10条记录
            
            return {
                'current': asdict(self.metrics_history[-1]),
                'averages': {
                    'cpu_percent': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
                    'memory_percent': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
                    'avg_response_time': sum(m.avg_response_time for m in recent_metrics) / len(recent_metrics),
                },
                'history_count': len(self.metrics_history)
            }
        except Exception as e:
            logger.error(f"获取指标摘要失败: {e}")
            return {}

class HealthChecker:
    """健康检查器"""
    
    def __init__(self, proxy_manager, storage):
        self.proxy_manager = proxy_manager
        self.storage = storage
        self.last_check_time = None
        self.health_status = {}
    
    async def check_health(self) -> Dict[str, Any]:
        """执行健康检查"""
        self.last_check_time = datetime.now()
        
        checks = {
            'redis_connection': await self._check_redis(),
            'proxy_pool': await self._check_proxy_pool(),
            'system_resources': await self._check_system_resources(),
        }
        
        # 计算整体健康状态
        all_healthy = all(check['healthy'] for check in checks.values())
        
        self.health_status = {
            'timestamp': self.last_check_time.isoformat(),
            'overall_healthy': all_healthy,
            'checks': checks
        }
        
        if not all_healthy:
            logger.warning(f"健康检查发现问题: {self.health_status}")
        
        return self.health_status
    
    async def _check_redis(self) -> Dict[str, Any]:
        """检查Redis连接"""
        try:
            redis_conn = await self.storage._get_connection()
            await redis_conn.ping()
            return {
                'healthy': True,
                'message': 'Redis连接正常'
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Redis连接失败: {e}'
            }
    
    async def _check_proxy_pool(self) -> Dict[str, Any]:
        """检查代理池状态"""
        try:
            proxy_count = await self.proxy_manager.get_proxy_count()
            
            if proxy_count == 0:
                return {
                    'healthy': False,
                    'message': '代理池为空',
                    'proxy_count': proxy_count
                }
            elif proxy_count < 10:
                return {
                    'healthy': True,
                    'message': f'代理数量较少: {proxy_count}',
                    'proxy_count': proxy_count,
                    'warning': True
                }
            else:
                return {
                    'healthy': True,
                    'message': f'代理池状态正常: {proxy_count}个代理',
                    'proxy_count': proxy_count
                }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'检查代理池失败: {e}'
            }
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            issues = []
            
            if cpu_percent > 90:
                issues.append(f'CPU使用率过高: {cpu_percent}%')
            
            if memory.percent > 90:
                issues.append(f'内存使用率过高: {memory.percent}%')
            
            if disk.percent > 90:
                issues.append(f'磁盘使用率过高: {disk.percent}%')
            
            if issues:
                return {
                    'healthy': False,
                    'message': '; '.join(issues),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent
                }
            else:
                return {
                    'healthy': True,
                    'message': '系统资源状态正常',
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent
                }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'检查系统资源失败: {e}'
            }

# 全局实例
performance_monitor = PerformanceMonitor()