import asyncio
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from core.proxy_manager import ProxyManager
from utils.logger import logger
from config.settings import config_manager
from utils.scheduler import scheduler
import uvicorn

# 全局代理管理器
proxy_manager = ProxyManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("FastAPI 应用启动中...")
    
    # 启动时的初始化
    try:
        # 启动调度器
        scheduler.start()
        
        # 添加定时任务
        config = config_manager.config
        scheduler.add_job(
            func=proxy_manager.run_fetch_proxies,
            trigger='interval',
            seconds=config.scheduler.fetch_interval,
            job_id='api_fetch_proxies'
        )
        
        scheduler.add_job(
            func=proxy_manager.run_clean_proxies,
            trigger='interval',
            seconds=config.scheduler.verifier_interval,
            job_id='api_clean_proxies'
        )
        
        logger.info("FastAPI 应用启动完成")
        yield
    except Exception as e:
        logger.error(f"启动 FastAPI 应用失败: {e}")
        raise
    finally:
        # 关闭时的清理
        logger.info("FastAPI 应用关闭中...")
        try:
            scheduler.stop()
            await proxy_manager.close()
            logger.info("FastAPI 应用关闭完成")
        except Exception as e:
            logger.error(f"关闭 FastAPI 应用时发生错误: {e}")

# 创建 FastAPI 应用
app = FastAPI(
    title="HighProxyPool API",
    description="高效的代理池服务API",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/api/get_proxy", summary="获取代理", description="获取一个可用的代理IP")
async def get_proxy():
    """获取代理API"""
    try:
        proxy = await proxy_manager.get_proxy()
        if proxy:
            return JSONResponse(
                status_code=200,
                content={"status": "success", "proxy": proxy}
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="暂无可用代理，请稍后重试"
            )
    except Exception as e:
        logger.error(f"获取代理API错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@app.get("/api/proxy_count", summary="获取代理数量", description="获取代理池中的代理总数")
async def get_proxy_count():
    """获取代理数量API"""
    try:
        count = await proxy_manager.get_proxy_count()
        return JSONResponse(
            status_code=200,
            content={"status": "success", "count": count}
        )
    except Exception as e:
        logger.error(f"获取代理数量API错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@app.post("/api/refresh_proxies", summary="刷新代理", description="手动触发代理获取任务")
async def refresh_proxies():
    """手动刷新代理API"""
    try:
        # 在后台线程中执行代理获取
        def fetch_in_background():
            proxy_manager.run_fetch_proxies()
        
        thread = threading.Thread(target=fetch_in_background)
        thread.start()
        
        return JSONResponse(
            status_code=200,
            content={"status": "success", "message": "代理刷新任务已启动"}
        )
    except Exception as e:
        logger.error(f"刷新代理API错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@app.post("/api/clean_proxies", summary="清理代理", description="手动触发代理清理任务")
async def clean_proxies():
    """手动清理代理API"""
    try:
        # 在后台线程中执行代理清理
        def clean_in_background():
            proxy_manager.run_clean_proxies()
        
        thread = threading.Thread(target=clean_in_background)
        thread.start()
        
        return JSONResponse(
            status_code=200,
            content={"status": "success", "message": "代理清理任务已启动"}
        )
    except Exception as e:
        logger.error(f"清理代理API错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@app.get("/api/status", summary="系统状态", description="获取系统运行状态")
async def get_status():
    """获取系统状态API"""
    try:
        proxy_count = await proxy_manager.get_proxy_count()
        job_info = scheduler.get_job_info()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": {
                    "proxy_count": proxy_count,
                    "scheduler_running": scheduler._is_started,
                    "jobs": job_info
                }
            }
        )
    except Exception as e:
        logger.error(f"获取状态API错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@app.get("/", summary="首页", description="API首页")
async def root():
    """API首页"""
    return JSONResponse(
        status_code=200,
        content={
            "message": "Welcome to HighProxyPool API",
            "version": "2.0.0",
            "endpoints": {
                "get_proxy": "/api/get_proxy",
                "proxy_count": "/api/proxy_count",
                "refresh_proxies": "/api/refresh_proxies",
                "clean_proxies": "/api/clean_proxies",
                "status": "/api/status"
            }
        }
    )

def run_api_server():
    """运行API服务器"""
    config = config_manager.config.fastapi
    logger.info(f"启动 API 服务器，地址: {config.host}:{config.port}")
    
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    run_api_server()
