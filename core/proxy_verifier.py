import logging
import sys
import requests
from utils.redis_client import RedisObject
import ast


logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format="%(asctime)s - %(levelname)s - %(message)s",  # 日志格式
    stream=sys.stdout  # 输出到标准输出
)


# class ProxyVerifier:
    
#     def __init__(self, check_url: str = "https://www.kuaidaili.com/",proxy_pool_name: str = "proxy_pool"):
#         self.conn = RedisObject().get_connection()
#         self.proxy_pool_name = proxy_pool_name  # Redis 中存储代理的集合名称
#         self.check_url = check_url
        

#     def validate_proxy(self, ip: str) -> bool:
#         """
#         验证单个代理是否有效
#         """
#         headers = {
#             'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
#             'Connection': 'close'
#         }
#         try:
#             # {'http': 'http://114.232.110.39:8888'}
#             # 使用 ast.literal_eval 替代 eval
#             proxy = ast.literal_eval(ip)
#             response = requests.get(self.check_url, proxies=proxy, headers=headers, timeout=5)
#             logging.info(f"代理 {ip} 返回状态码: {response.status_code}")
#             return response.status_code == 200
#         except (ValueError, SyntaxError, requests.RequestException) as e:
#             logging.error(f"验证代理失败: {ip}, 错误: {e}")
#             return False

#     def clean_invalid_proxies(self):
#         """
#         清理 Redis 中的无效代理
#         """
#         logging.info("开始清理无效代理...")
#         try:
#             ips = self.conn.smembers(self.proxy_pool_name)  # 获取 Redis 集合中的所有代理
#             for ip in ips:
#                 ip = ip.decode('utf-8')  # 解码 Redis 中存储的字节数据
#                 if not self.validate_proxy(ip):
#                     self.conn.srem(self.proxy_pool_name, ip)  # 删除无效代理
#                     logging.warning(f"删除无效代理: {ip}")
#             logging.info("无效代理清理完成")
#         except Exception as e:
#             logging.error(f"清理无效代理时发生错误: {e}")

   

import asyncio
import aiohttp
import logging
import ast

class ProxyValidator:
    def __init__(self, check_url: str, proxy_pool_name: str):
        self.check_url = check_url  # 验证代理的 URL
        self.conn = RedisObject().get_connection()
        self.proxy_pool_name = proxy_pool_name  # Redis 中存储代理的集合名称

    async def validate_proxy(self, ip: str) -> bool:
        """
        异步验证单个代理是否有效
        """
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            'Connection': 'close'
        }
        try:
            # 使用 ast.literal_eval 替代 eval 解析字符串为字典
            proxy = ast.literal_eval(ip)
            async with aiohttp.ClientSession() as session:
                async with session.get(self.check_url, proxy=proxy['http'], headers=headers, timeout=20) as response:
                    logging.info(f"代理 {ip} 返回状态码: {response.status}")
                    return response.status == 200
        except (ValueError, SyntaxError, aiohttp.ClientError, asyncio.TimeoutError) as e:
            logging.error(f"验证代理失败: {ip}, 错误: {e}")
            return False

    async def clean_invalid_proxies(self):
        """
        异步清理 Redis 中的无效代理
        """
        logging.info("开始清理无效代理...")
        try:
            # 获取 Redis 集合中的所有代理
            ips = await asyncio.to_thread(self.conn.smembers, self.proxy_pool_name)
            tasks = []
            for ip in ips:
                ip = ip.decode('utf-8')  # 解码 Redis 中存储的字节数据
                tasks.append(self.validate_and_remove(ip))  # 创建异步任务
            await asyncio.gather(*tasks)  # 并发执行所有任务
            logging.info("无效代理清理完成")
        except Exception as e:
            logging.error(f"清理无效代理时发生错误: {e}")

    async def validate_and_remove(self, ip: str):
        """
        验证代理并删除无效代理
        """
        if not await self.validate_proxy(ip):
            await asyncio.to_thread(self.conn.srem, self.proxy_pool_name, ip)  # 删除无效代理
            logging.warning(f"删除无效代理: {ip}")

    def run_clean_invalid_proxies(self):
        """
        同步方法,用于在调度器中调用
        """
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # 运行异步清理方法
            loop.run_until_complete(self.clean_invalid_proxies())
            # 关闭事件循环
            loop.close()
        except Exception as e:
            logging.error(f"执行代理清理任务时发生错误: {e}")