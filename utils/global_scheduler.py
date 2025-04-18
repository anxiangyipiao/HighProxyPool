import logging
import atexit
import threading
import time
from apscheduler.schedulers.background import BackgroundScheduler

class GlobalScheduler:
    _instance = None  # 单例实例
    _lock = threading.Lock()  # 用于线程安全

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:  # 双重检查锁
                    cls._instance = super(GlobalScheduler, cls).__new__(cls, *args, **kwargs)
                    cls._instance.scheduler = BackgroundScheduler()
                    cls._instance._is_started = False
                    atexit.register(lambda: cls._instance.scheduler.shutdown(wait=False))
        return cls._instance

    def start(self):
        """
        启动全局调度器
        """
        if not self._is_started:
            self.scheduler.start()
            self._is_started = True
            logging.info("全局调度器已启动")
        else:
            logging.warning("全局调度器已在运行")

    def stop(self):
        """
        停止全局调度器
        """
        if self._is_started:
            self.scheduler.shutdown(wait=False)
            self._is_started = False
            logging.info("全局调度器已停止")
        else:
            logging.warning("全局调度器未运行")

    def add_job(self, func, trigger, **kwargs):
        """
        添加任务到调度器
        :param func: 要执行的函数
        :param trigger: 触发器类型，例如 'interval', 'cron'
        :param kwargs: 触发器参数，例如 seconds=60
        """
        job = self.scheduler.add_job(func, trigger, **kwargs)
        logging.info(f"任务 {func.__name__} 已添加到调度器，任务ID: {job.id}, 触发器: {trigger}, 参数: {kwargs}")

    def get_jobs(self):
        """
        获取当前调度器中的所有任务
        """
        return self.scheduler.get_jobs()

    def remove_job(self, job_id):
        """
        根据任务ID移除任务
        :param job_id: 任务ID
        """
        self.scheduler.remove_job(job_id)
        logging.info(f"任务 {job_id} 已从调度器中移除")

    def keep_alive(self):
        """
        保持主线程活动，以允许后台调度器运行。
        按 Ctrl+C 退出。
        """
        logging.info("主线程进入 keep_alive 模式。按 Ctrl+C 退出。")
        try:
            while True:
                time.sleep(60)  # 休眠以减少 CPU 占用
        except (KeyboardInterrupt, SystemExit):
            logging.info("收到退出信号，准备关闭...")
            # atexit 会处理关闭，这里可以不调用 self.stop()
            # self.stop() # 如果希望在这里显式停止也可以