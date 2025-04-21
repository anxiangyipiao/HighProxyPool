
from fastapi import FastAPI
from core.proxy_fetcher import Proxy
<<<<<<< HEAD
from fastapi.concurrency import run_in_threadpool
=======
>>>>>>> ae7311624accaeba06f05241f5a906e5476f90ca
from utils.config_reader import flask_config, scheduler_config  # 假设你用这个读取配置
import uvicorn  # 用于启动 FastAPI 应用

app = FastAPI(title="Proxy API", description="一个简单的代理服务 API", version="1.0.0")
p = Proxy(proxy_pool_name=scheduler_config['proxy_pool_name'])


@app.get("/api/get_proxy", summary="获取代理 IP", description="返回一个代理 IP")
<<<<<<< HEAD
async def get_ip():
    proxy = await run_in_threadpool(p.get_proxy)  # 将同步方法包装为异步调用
    return {"proxy": proxy}
=======
def get_ip():
    return {"proxy": p.get_proxy()}
>>>>>>> ae7311624accaeba06f05241f5a906e5476f90ca


if __name__ == "__main__":
    # 使用 uvicorn 启动 FastAPI 应用
    uvicorn.run(app, host=flask_config['host'], port=flask_config['port'])
