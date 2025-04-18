# FILE: main.py
import logging
from core.proxy_fetcher import Proxy
from core.proxy_verifier import ProxyVerifier
from utils.global_scheduler import GlobalScheduler
from utils.config_reader import scheduler_config,flask_config # 假设你用这个读取配置
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



if __name__ == "__main__":


    logging.info("应用程序启动...")

    # 获取全局调度器实例 (只需要获取一次)
    scheduler = GlobalScheduler()

    proxy_pool_name = scheduler_config.get('proxy_pool_name', 'proxy_pool') # 提供默认值

    # --- 初始化和调度 Proxy (抓取器) ---
    try:

        proxy_instance = Proxy(proxy_pool_name=proxy_pool_name)
        fetch_interval = int(scheduler_config.get('fetch_interval', 8)) # 假设单位是小时
        # 直接使用全局 scheduler 添加任务，而不是调用 proxy_instance.start_scheduler
        scheduler.add_job(proxy_instance.fetch_bajiu_daili, 'interval', hours=fetch_interval)
        logging.info(f"代理抓取任务已添加，每 {fetch_interval} 小时执行一次。")
    except Exception as e:
        logging.error(f"初始化或调度 Proxy 失败: {e}")
        # 根据需要决定是否退出
        exit(1)

    # --- 初始化和调度 ProxyVerifier (验证器) ---
    try:
        verifier_instance = ProxyVerifier(
                check_url=scheduler_config.get('verifier_url', 'http://httpbin.org/get'),
                proxy_pool_name=proxy_pool_name
        )
        verifier_interval = int(scheduler_config.get('verifier_interval', 30)) # 假设单位是分钟
        scheduler.add_job(verifier_instance.clean_invalid_proxies, 'interval', seconds=verifier_interval)
        logging.info(f"代理验证任务已添加，每 {verifier_interval} 分钟执行一次。")
    except Exception as e:
        logging.error(f"初始化或调度 ProxyVerifier 失败: {e}")
        # 根据需要决定是否退出
        exit(1)

    # --- 启动调度器 ---
    # 只需要启动一次
    scheduler.start()

    # --- 保持主线程活动 ---
    # 调用全局调度器的 keep_alive 方法
    scheduler.keep_alive()

    # 当 keep_alive 结束时 (例如收到 Ctrl+C)，程序会继续执行到这里
    logging.info("应用程序即将退出。")