from locust import HttpUser, task, between

class ProxyAPITestUser(HttpUser):
    wait_time = between(1, 5)  # 每个用户请求之间的等待时间（秒）

    @task
    def get_proxy(self):
        self.client.get("/api/get_proxy")  # 测试你的 `/api/get_proxy` 路由