import time
import logging
import requests
from bs4 import BeautifulSoup
from utils.redis_client import RedisObject
from typing import Optional, Dict


# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Proxy:

    def __init__(self,proxy_pool_name: str = "proxypool"):
        self.conn = RedisObject().get_connection()
        self.PROXY_POOL_NAME = proxy_pool_name

    def fetch_bajiu_daili(self) -> None:
        """
        抓取 89 免费代理并存入 Redis
        """
        url = "http://www.89ip.cn/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            "Connection": "close",
        }
        try:
            result = self.request_proxy("GET", url, headers=headers)
            soup = BeautifulSoup(result.text, "html.parser")
            ips = soup.find("table", class_="layui-table").find("tbody").find_all("tr")
            for ip in ips:
                td = ip.find_all("td")
                host = td[0].get_text().strip()
                port = td[1].get_text().strip()
                self._save_proxy({"http": f"http://{host}:{port}"})
                logging.info(f"抓取到代理: {host}:{port}")
        except Exception as e:
            logging.error(f"抓取 89 免费代理失败: {e}")

    def _save_proxy(self, proxy: Dict[str, str]) -> None:
        """
        保存代理到 Redis 集合
        :param proxy: 代理字典，例如 {"http": "http://111.222.33.123:8080"}
        """
        result = self.conn.sadd(self.PROXY_POOL_NAME, str(proxy))
        if result == 1:
            logging.info(f"代理 {proxy} 添加成功")
        elif result == 0:
            logging.info(f"代理 {proxy} 已存在")
        else:
            logging.warning(f"代理 {proxy} 添加失败，返回值: {result}")

    def request_proxy(self, method: str, url: str, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        使用代理发送 HTTP 请求
        :param method: HTTP 方法，例如 "GET" 或 "POST"
        :param url: 请求的 URL
        :param headers: 请求头
        :return: HTTP 响应对象
        """
        proxy = self._get_random_proxy()
        try:
            if proxy:
                logging.info(f"使用代理 {proxy} 发送请求")
                return requests.request(method, url, proxies=proxy, headers=headers, timeout=10)
            else:
                logging.info("未使用代理发送请求")
                return requests.request(method, url, headers=headers, timeout=10)
        except requests.RequestException as e:
            logging.error(f"请求失败: {e}")
            raise

    def _get_random_proxy(self) -> Optional[Dict[str, str]]:
        """
        从 Redis 中随机获取一个代理
        :return: 代理字典，例如 {"http": "http://111.222.33.123:8080"}，如果代理池为空则返回 None
        """
        proxy = self.conn.srandmember(self.PROXY_POOL_NAME)
        if proxy:
            return eval(proxy.decode("utf-8"))
        logging.warning("代理池为空")
        return None

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        获取一个代理 IP
        :return: 代理字典，例如 {"http": "http://111.222.33.123:8080"}，如果代理池为空则返回 None
        """
        proxy = self._get_random_proxy()
        if proxy:
            return proxy
        logging.warning("代理池为空，无法获取代理")
        return None


