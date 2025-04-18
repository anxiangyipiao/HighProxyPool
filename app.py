
from fastapi import FastAPI
from core.proxy_fetcher import Proxy
from utils.config_reader import flask_config, scheduler_config  # 假设你用这个读取配置
import uvicorn  # 用于启动 FastAPI 应用

app = FastAPI(title="Proxy API", description="一个简单的代理服务 API", version="1.0.0")
p = Proxy(proxy_pool_name=scheduler_config['proxy_pool_name'])


@app.get("/api/get_proxy", summary="获取代理 IP", description="返回一个代理 IP")
def get_ip():
    return {"proxy": p.get_proxy()}


if __name__ == "__main__":
    # 使用 uvicorn 启动 FastAPI 应用
    uvicorn.run(app, host=flask_config['host'], port=flask_config['port'])
