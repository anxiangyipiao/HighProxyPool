
import logging
import threading
from fastapi import FastAPI
from core.proxy_fetcher import Proxy
from fastapi.concurrency import run_in_threadpool
from utils.config_reader import flask_config, scheduler_config  # 假设你用这个读取配置
import uvicorn  # 用于启动 FastAPI 应用
from main import start_scheduler,close_scheduler  # 假设你有一个函数来启动调度器



app = FastAPI(title="Proxy API", description="一个简单的代理服务 API", version="1.0.0")
p = Proxy(proxy_pool_name=scheduler_config['proxy_pool_name'])


@app.get("/api/get_proxy", summary="获取代理 IP", description="返回一个代理 IP")
async def get_ip():
    proxy = await run_in_threadpool(p.get_proxy)  # 将同步方法包装为异步调用
    return {"proxy": proxy}




if __name__ == "__main__":
    try:
        # 启动调度器线程
        scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
        scheduler_thread.start()

        # 启动 FastAPI 应用
        uvicorn.run(app, host=flask_config['host'], port=flask_config['port'])
    except Exception as e:
        # 捕获异常并记录日志
        logging.error(f"发生异常: {e}")
    finally:
        logging.info("程序退出。")
        close_scheduler()  # 确保调度器关闭
