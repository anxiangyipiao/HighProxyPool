import logging
import atexit
import threading
import time
from typing import Optional, Callable, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from utils.logger import logger
from utils.exceptions import SchedulerError

class EnhancedScheduler:
    """增强的调度器，支持更好的错误处理和监控"""
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_workers: int = 10):
        if self._initialized:
            return
        
        # 配置执行器
        executors = {
            'default': ThreadPoolExecutor(max_workers),
        }
        
        # 任务默认配置
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'misfire_grace_time': 30
        }
        
        self.scheduler = BackgroundScheduler(
            executors=executors,
            job_defaults=job_defaults
        )
        self._is_started = False
        self._initialized = True
        
        # 注册退出处理
        atexit.register(self._cleanup)

    def start(self):
        """启动调度器"""
        if not self._is_started:
            try:
                self.scheduler.start()
                self._is_started = True
                logger.info("增强调度器已启动")
            except Exception as e:
                logger.error(f"启动调度器失败: {e}")
                raise SchedulerError(f"启动调度器失败: {e}")
        else:
            logger.warning("调度器已在运行")

    def stop(self):
        """停止调度器"""
        if self._is_started:
            try:
                self.scheduler.shutdown(wait=False)
                self._is_started = False
                logger.info("调度器已停止")
            except Exception as e:
                logger.error(f"停止调度器失败: {e}")
                raise SchedulerError(f"停止调度器失败: {e}")

    def add_job(
        self, 
        func: Callable, 
        trigger: str, 
        job_id: Optional[str] = None,
        replace_existing: bool = True,
        **kwargs
    ) -> str:
        """
        添加任务到调度器
        
        Args:
            func: 要执行的函数
            trigger: 触发器类型
            job_id: 任务ID
            replace_existing: 是否替换现有任务
            **kwargs: 触发器参数
        
        Returns:
            任务ID
        """
        try:
            # 包装函数以添加错误处理
            def wrapped_func():
                try:
                    logger.info(f"开始执行任务: {func.__name__}")
                    func()
                    logger.info(f"任务执行完成: {func.__name__}")
                except Exception as e:
                    logger.error(f"任务执行失败 {func.__name__}: {e}")
            
            job = self.scheduler.add_job(
                wrapped_func,
                trigger,
                id=job_id,
                replace_existing=replace_existing,
                **kwargs
            )
            
            logger.info(f"任务已添加: {func.__name__} (ID: {job.id}), 触发器: {trigger}, 参数: {kwargs}")
            return job.id
            
        except Exception as e:
            logger.error(f"添加任务失败: {e}")
            raise SchedulerError(f"添加任务失败: {e}")

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

    def keep_alive(self):
        """保持主线程活动"""
        logger.info("主线程进入 keep_alive 模式。按 Ctrl+C 退出。")
        try:
            while True:
                # 定期检查调度器状态
                if self._is_started:
                    job_count = len(self.get_jobs())
                    logger.debug(f"调度器运行中，当前任务数: {job_count}")
                time.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            logger.info("收到退出信号，准备关闭...")
            self.stop()

    def _cleanup(self):
        """清理资源"""
        if self._is_started:
            self.stop()

# 全局调度器实例
scheduler = EnhancedScheduler()