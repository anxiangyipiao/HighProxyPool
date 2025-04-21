# HighProxyPool


## 简介 (Introduction)

HighProxyPool 是一个高效的代理池项目，旨在为用户提供稳定、快速的代理服务。 基于fastapi、redis、apscheduler等包。
HighProxyPool is an efficient proxy pool project designed to provide users with stable and fast proxy services.

---

## 功能 (Features)

1. **高效抓取代理**: 自动抓取多个代理网站上的免费代理。  
   **Efficient Proxy Scraping**: Automatically scrape free proxies from multiple proxy websites.

2. **代理验证**: 验证代理的可用性和速度，筛选出高质量的代理。  
   **Proxy Validation**: Validate proxies for availability and speed to filter high-quality proxies.

3. **API 接口**: 提供便捷的 API 接口，方便用户获取代理。  
   **API Interface**: Provide a convenient API interface for users to fetch proxies.

4. **定时任务**: 支持定时抓取和更新代理池。  
   **Scheduled Tasks**: Support scheduled scraping and updating of the proxy pool.


### 启动项目 (Start the Project)

运行以下命令启动项目：  
Run the following command to start the project:

```bash
python main.py
python app.py
```

---

## API 示例 (API Examples)

1. **获取代理 (Fetch Proxies)**  
   请求方式 (Request Method): `GET`  
   URL: `/api/get_proxy`  
   示例返回 (Example Response):
   ```json
   {
       "proxy": "192.168.1.1:8080",

   }
   ```

```

这段 `README.md` 包含双语说明，详细描述了项目功能、使用到的包及如何使用。如果有更多具体要求，请告诉我！
