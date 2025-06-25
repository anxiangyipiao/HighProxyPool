import asyncio
import threading
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.proxy_manager import ProxyManager
from utils.logger import logger
from utils.monitoring import performance_monitor, HealthChecker
from config.settings import config_manager
from utils.scheduler import async_scheduler
import uvicorn

# 全局代理管理器
proxy_manager = ProxyManager()
health_checker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global health_checker
    logger.info("FastAPI 应用启动中...")
    
    # 启动时的初始化
    try:
        # 初始化健康检查器
        health_checker = HealthChecker(proxy_manager, proxy_manager.storage)
        
        # 启动异步调度器
        await async_scheduler.start()
        
        # 添加定时任务 - 使用异步方法
        config = config_manager.config
        async_scheduler.add_async_job(
            func=proxy_manager.fetch_all_proxies,
            trigger='interval',
            seconds=config.scheduler.fetch_interval,
            job_id='api_fetch_proxies'
        )
        
        async_scheduler.add_async_job(
            func=proxy_manager.clean_invalid_proxies,
            trigger='interval',
            seconds=config.scheduler.verifier_interval,
            job_id='api_clean_proxies'
        )
        
        # 添加性能监控任务
        async def collect_performance_metrics():
            proxy_count = await proxy_manager.get_proxy_count()
            await performance_monitor.collect_metrics(proxy_count)
        
        async_scheduler.add_async_job(
            func=collect_performance_metrics,
            trigger='interval',
            seconds=60,  # 每分钟收集一次指标
            job_id='collect_metrics'
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
            await async_scheduler.stop()
            await proxy_manager.close()
            logger.info("FastAPI 应用关闭完成")
        except Exception as e:
            logger.error(f"关闭 FastAPI 应用时发生错误: {e}")

# 创建 FastAPI 应用
app = FastAPI(
    title="HighProxyPool API",
    description="高效的代理池服务API",
    version="2.1.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求中间件：记录性能指标
@app.middleware("http")
async def add_performance_monitoring(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        performance_monitor.record_request(process_time, False)
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        process_time = time.time() - start_time
        performance_monitor.record_request(process_time, True)
        raise e

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

@app.get("/api/proxy_stats", summary="获取代理统计", description="获取详细的代理统计信息")
async def get_proxy_stats():
    """获取代理统计信息API"""
    try:
        stats = await proxy_manager.get_proxy_statistics()
        return JSONResponse(
            status_code=200,
            content={"status": "success", "data": stats}
        )
    except Exception as e:
        logger.error(f"获取代理统计API错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@app.post("/api/refresh_proxies", summary="刷新代理", description="手动触发代理获取任务")
async def refresh_proxies():
    """手动刷新代理API"""
    try:
        # 直接调用异步方法
        asyncio.create_task(proxy_manager.fetch_all_proxies())
        
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
        # 直接调用异步方法
        asyncio.create_task(proxy_manager.clean_invalid_proxies())
        
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

@app.get("/api/health", summary="健康检查", description="获取系统健康状态")
async def health_check():
    """健康检查API"""
    try:
        if health_checker:
            health_status = await health_checker.check_health()
            status_code = 200 if health_status['overall_healthy'] else 503
            return JSONResponse(
                status_code=status_code,
                content={"status": "success", "data": health_status}
            )
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "error", "message": "健康检查器未初始化"}
            )
    except Exception as e:
        logger.error(f"健康检查API错误: {e}")
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
            "version": "2.1.0",
            "features": [
                "多源代理获取",
                "智能代理验证",
                "性能监控",
                "健康检查",
                "统计分析"
            ],
            "endpoints": {
                "get_proxy": "/api/get_proxy",
                "proxy_count": "/api/proxy_count", 
                "proxy_stats": "/api/proxy_stats",
                "refresh_proxies": "/api/refresh_proxies",
                "clean_proxies": "/api/clean_proxies",
                "status": "/api/status",
                "health": "/api/health",
                "metrics": "/api/metrics"
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
        workers=config.workers,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    run_api_server()
