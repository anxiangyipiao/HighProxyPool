import logging
import requests
from utils.redis_client import RedisObject
import ast


# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ProxyVerifier:
    
    def __init__(self, check_url: str = "https://www.kuaidaili.com/",proxy_pool_name: str = "proxy_pool"):
        self.conn = RedisObject().get_connection()
        self.proxy_pool_name = proxy_pool_name  # Redis 中存储代理的集合名称
        self.check_url = check_url
        

    def validate_proxy(self, ip: str) -> bool:
        """
        验证单个代理是否有效
        """
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            'Connection': 'close'
        }
        try:
            # {'http': 'http://114.232.110.39:8888'}
            # 使用 ast.literal_eval 替代 eval
            proxy = ast.literal_eval(ip)
            response = requests.get(self.check_url, proxies=proxy, headers=headers, timeout=5)
            logging.info(f"代理 {ip} 返回状态码: {response.status_code}")
            return response.status_code == 200
        except (ValueError, SyntaxError, requests.RequestException) as e:
            logging.error(f"验证代理失败: {ip}, 错误: {e}")
            return False

    def clean_invalid_proxies(self):
        """
        清理 Redis 中的无效代理
        """
        logging.info("开始清理无效代理...")
        try:
            ips = self.conn.smembers(self.proxy_pool_name)  # 获取 Redis 集合中的所有代理
            for ip in ips:
                ip = ip.decode('utf-8')  # 解码 Redis 中存储的字节数据
                if not self.validate_proxy(ip):
                    self.conn.srem(self.proxy_pool_name, ip)  # 删除无效代理
                    logging.warning(f"删除无效代理: {ip}")
            logging.info("无效代理清理完成")
        except Exception as e:
            logging.error(f"清理无效代理时发生错误: {e}")

   

