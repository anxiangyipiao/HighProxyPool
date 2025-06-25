import asyncio
import atexit
from typing import Optional, Callable, Any, Union
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from utils.logger import logger
from utils.exceptions import SchedulerError

class AsyncEnhancedScheduler:
    """异步增强调度器，支持异步任务调度"""
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_workers: int = 10):
        if self._initialized:
            return
        
        # 配置异步执行器
        executors = {
            'default': AsyncIOExecutor(),
        }
        
        # 任务默认配置
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'misfire_grace_time': 30
        }
        
        self.scheduler = AsyncIOScheduler(
            executors=executors,
            job_defaults=job_defaults
        )
        self._is_started = False
        self._initialized = True
        
        # 注册退出处理
        atexit.register(self._cleanup)

    async def start(self):
        """启动异步调度器"""
        if not self._is_started:
            try:
                self.scheduler.start()
                self._is_started = True
                logger.info("异步增强调度器已启动")
            except Exception as e:
                logger.error(f"启动异步调度器失败: {e}")
                raise SchedulerError(f"启动异步调度器失败: {e}")
        else:
            logger.warning("异步调度器已在运行")

    async def stop(self):
        """停止异步调度器"""
        if self._is_started:
            try:
                self.scheduler.shutdown(wait=False)
                self._is_started = False
                logger.info("异步调度器已停止")
            except Exception as e:
                logger.error(f"停止异步调度器失败: {e}")
                raise SchedulerError(f"停止异步调度器失败: {e}")

    def add_async_job(
        self, 
        func: Union[Callable, Callable[..., Any]], 
        trigger: str, 
        job_id: Optional[str] = None,
        replace_existing: bool = True,
        **kwargs
    ) -> str:
        """添加异步任务到调度器"""
        try:
            # 包装异步函数以添加错误处理
            async def wrapped_async_func():
                try:
                    logger.info(f"开始执行异步任务: {func.__name__}")
                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()
                    logger.info(f"异步任务执行完成: {func.__name__}")
                except Exception as e:
                    logger.error(f"异步任务执行失败 {func.__name__}: {e}")
            
            job = self.scheduler.add_job(
                wrapped_async_func,
                trigger,
                id=job_id,
                replace_existing=replace_existing,
                **kwargs
            )
            
            logger.info(f"异步任务已添加: {func.__name__} (ID: {job.id}), 触发器: {trigger}")
            return job.id
            
        except Exception as e:
            logger.error(f"添加异步任务失败: {e}")
            raise SchedulerError(f"添加异步任务失败: {e}")

    def remove_job(self, job_id: str):
        """移除任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"任务已移除: {job_id}")
        except Exception as e:
            logger.error(f"移除任务失败: {e}")
            raise SchedulerError(f"移除任务失败: {e}")

    def get_jobs(self):
        """获取所有任务"""
        return self.scheduler.get_jobs()

    def get_job_info(self):
        """获取任务信息"""
        jobs = self.get_jobs()
        job_info = []
        for job in jobs:
            info = {
                'id': job.id,
                'name': job.name,
                'func': job.func.__name__ if hasattr(job.func, '__name__') else str(job.func),
                'trigger': str(job.trigger),
                'next_run': job.next_run_time
            }
            job_info.append(info)
        return job_info

    def _cleanup(self):
        """清理资源"""
        if self._is_started:
            try:
                asyncio.run(self.stop())
            except Exception as e:
                logger.error(f"清理调度器失败: {e}")

# 全局异步调度器实例
async_scheduler = AsyncEnhancedScheduler()
