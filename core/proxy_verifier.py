import asyncio
import logging
import sys
import time
import aiohttp
from utils.redis_client import RedisObject
import ast


logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format="%(asctime)s - %(levelname)s - %(message)s",  # 日志格式
    stream=sys.stdout  # 输出到标准输出
)


class ProxyVerifier:
    
    def __init__(self, check_url: str = "https://www.kuaidaili.com/",proxy_pool_name: str = "proxypool",max_concurrent_validations: int = 10):
        self.conn = RedisObject().get_connection()
        self.proxy_pool_name = proxy_pool_name  # Redis 中存储代理的集合名称
        self.check_url = check_url
        self.max_concurrent_validations = max_concurrent_validations
       
    async def _async_validate_proxy(self, ip_str):
        """
        测试单个代理
        :param ip:
        :return:
        """

        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            'Connection': 'close'
        }

        try:
            # 解析存储的字符串获取代理字典
            proxy_dict = ast.literal_eval(ip_str)
            proxy_url = None
            if isinstance(proxy_dict, dict):
                if 'http' in proxy_dict:
                    proxy_url = proxy_dict['http']
                elif 'https' in proxy_dict:
                     proxy_url = proxy_dict['https'] # 优先使用 http，如果没有则用 https

            if proxy_url:

                # 使用 aiohttp 测试代理
                conn = aiohttp.TCPConnector(verify_ssl=False)
                async with aiohttp.ClientSession(connector=conn) as session:
                    try:
                        async with session.get(self.check_url, proxy=proxy_url, timeout=5,headers=headers) as response:
                            if response.status == 200:
                                logging.info(f"代理 {proxy_url} 可用")

                            else:
                                logging.info(f"代理 {proxy_url} 不可用 (状态码: {response.status})")
                                # 删除无效代理
                                self.conn.srem(self.proxy_pool_name, ip_str)
                    except Exception as e:
                        logging.warning(f"代理 {proxy_url} 测试异常: {e}")
                        self.conn.srem(self.proxy_pool_name, ip_str)
        except Exception as e:
            logging.warning(f"解析代理字符串 {ip_str} 时发生异常: {e}")
            # 删除无效代理
            self.conn.srem(self.proxy_pool_name, ip_str)




    def clean_invalid_proxies(self):
        """
        (异步) 清理无效代理的主方法
        """
        logging.info(f"开始异步执行代理清理任务 (池: {self.proxy_pool_name})...")

        try:
            
            ips = list(self.conn.smembers(self.proxy_pool_name))
            
            if not ips:
                logging.info("没有可用的代理 IP")
                return
            

            for i in range(0, len(ips), self.max_concurrent_validations):
                # 分批处理代理 IP 字符串
                ip_strings = ips[i:i + self.max_concurrent_validations]
                # 将字节字符串解码为普通字符串
                ip_strings = [ip.decode('utf-8') for ip in ip_strings]

                loop = asyncio.get_event_loop()

                tasks = [self._async_validate_proxy(ip_str) for ip_str in ip_strings]
            
                loop.run_until_complete(asyncio.wait(tasks))

                sys.stdout.flush()

                time.sleep(5)

            logging.info(f"代理清理任务完成 (池: {self.proxy_pool_name})")

        except Exception as e:
            print('测试器发生错误', e.args)
        

   
    