

import requests
import logging
from w3lib.http import basic_auth_header



def process_request(url):
    """
    使用 requests 发送代理请求
    
    Args:
        url: 请求的目标URL
        
    Returns:
        requests.Response 对象或 None (出错时)
    """
    try:
        # 代理配置
        proxy = "h154.kdltps.com:15818"
        proxy_url = f"http://{proxy}"

     
        # 请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Connection": "close"
        }

        headers['Proxy-Authorization'] = basic_auth_header('t10902206553199', 'j6hbvavd')  # 白名单认证可注释此行
        
        # 发送请求
        response = requests.get(
            url,
            proxies={"http": proxy_url},
            headers=headers,
            timeout=30,
            verify=False  # 禁用 SSL 验证
        )
        
        # 检查响应状态
        response.raise_for_status()
        return response
        
    except requests.exceptions.RequestException as e:
        logging.error(f"请求失败: {url}, 错误: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"发生未知错误: {url}, 错误: {str(e)}")
        return None
    

response = process_request("http://www.baidu.com")
if response:
    print(response.text)