
import requests


def get_proxy():

    url = 'http://121.37.171.89:8001/api/get_proxy'

    try:
        # 发送请求
        res = requests.get(url, timeout=5)
        res.raise_for_status()  # 检查 HTTP 状态码是否为 200

        # 解析响应数据
        proxy_data = res.json().get('proxy', {})
        if not proxy_data:
            raise ValueError("响应中未找到代理数据")

        # 构建代理字典
        proxies = {key: proxy_data[key] for key in ['http', 'https'] if key in proxy_data}
        return proxies

    except requests.RequestException as e:
        # 捕获请求异常
        print(f"请求失败: {e}")
    except ValueError as e:
        # 捕获数据解析异常
        print(f"数据解析失败: {e}")

    # 如果发生异常，返回空字典
    return {}
    

def test_proxy(proxies):

    url = 'https://www.bilibili.com/'

    try:
        res = requests.get(url, proxies=proxies, timeout=5)
        if res.status_code == 200:
            print('Proxy is working')
            return True
        else:
            print('Proxy is not working')
            return False
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        return False
    

if __name__ == '__main__':

    ip = get_proxy()
    print(ip)
    if ip:
        test_proxy(ip)
    else:
        print('No proxy found')