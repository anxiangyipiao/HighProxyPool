# HighProxyPool - 高效代理池系统

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

一个高效、稳定的代理池系统，支持多源获取、智能验证和RESTful API服务。

## ✨ 核心特性

- **多源代理获取**: 支持89代理、快代理等多个免费代理网站
- **智能验证**: 异步批量验证代理可用性，自动清理无效代理
- **高性能存储**: 基于Redis的代理存储，支持本地缓存优化
- **自动调度**: 定时获取和验证代理，保持代理池活跃
- **RESTful API**: 提供完整的HTTP API接口
- **容器化部署**: 支持Docker一键部署
- **实时监控**: 系统健康检查和性能监控

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Redis 5.0+

### 本地部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置Redis (修改 config.yaml)
redis:
  host: "localhost"
  port: 6379

# 3. 启动服务
python main.py    # 启动调度器(后台)
python app.py     # 启动API服务
```

### Docker部署 (推荐)

```bash
# 一键启动
docker-compose up -d

# 查看状态
docker-compose ps
docker-compose logs -f app
```

## 📡 API接口

**基础URL**: `http://localhost:8001`

| 接口 | 方法 | 描述 | 示例 |
|------|------|------|------|
| `/api/get_proxy` | GET | 获取一个可用代理 | `{"proxy":{"http":"1.2.3.4:8080"}}` |
| `/api/proxy_count` | GET | 获取代理池数量 | `{"count":1234}` |
| `/api/proxy_stats` | GET | 获取详细统计 | 包含总数、验证成功率等 |
| `/api/refresh_proxies` | POST | 手动获取代理 | `{"message":"started"}` |
| `/api/clean_proxies` | POST | 手动清理无效代理 | `{"message":"started"}` |
| `/api/health` | GET | 系统健康检查 | 系统状态信息 |

### 使用示例

```python
import requests

# 获取代理
response = requests.get('http://localhost:8001/api/get_proxy')
proxy_data = response.json()
proxy = proxy_data['proxy']['http']

# 使用代理
proxies = {'http': proxy, 'https': proxy}
requests.get('https://httpbin.org/ip', proxies=proxies)
```

## 🏗️ 项目结构

```
HighProxyPool/
├── main.py                 # 调度器入口
├── app.py                  # API服务入口
├── config.yaml            # 配置文件
├── core/                   # 核心模块
│   ├── proxy_manager.py   # 代理管理器
│   ├── fetchers/          # 代理获取器
│   └── validators/        # 代理验证器
├── storage/               # 存储模块
│   ├── redis_storage.py   # Redis存储
│   └── cached_redis_storage.py  # 缓存存储
├── utils/                 # 工具模块
│   ├── scheduler.py       # 异步调度
│   ├── logger.py         # 日志管理
│   └── monitoring.py     # 性能监控
└── tests/                # 测试模块
```

## ⚙️ 配置说明

**config.yaml** 主要配置项：

```yaml
# Redis配置
redis:
  host: "localhost"
  port: 6379
  password: ""
  db: 1

# API服务配置
fastapi:
  host: "0.0.0.0"
  port: 8001

# 调度器配置
scheduler:
  verifier_interval: 900    # 验证间隔(15分钟)
  fetch_interval: 3600      # 获取间隔(60分钟)
  verifier_url: "http://www.baidu.com"
  max_concurrent_validations: 50
```

## 🔧 扩展开发

### 添加新的代理源

1. 继承 `BaseFetcher` 类
2. 实现 `fetch_proxies` 方法
3. 在 `ProxyManager` 中注册

```python
from core.fetchers.base_fetcher import BaseFetcher

class NewSiteFetcher(BaseFetcher):
    async def fetch_proxies(self) -> List[Dict]:
        # 实现获取逻辑
        pass
```

### 自定义验证器

```python
from core.interfaces.validator_interface import ValidatorInterface

class CustomValidator(ValidatorInterface):
    async def validate_proxy(self, proxy_info: Dict) -> bool:
        # 实现验证逻辑
        pass
```

## 🧪 测试

```bash
# 运行测试
pytest

# 测试覆盖率
pytest --cov=core --cov=storage --cov=utils
```

## 📊 性能优化

- **并发调优**: 调整 `max_concurrent_validations` 参数
- **缓存优化**: 使用 `CachedRedisStorage` 减少Redis访问
- **间隔调整**: 根据需求调整获取和验证间隔
- **资源监控**: 通过 `/api/health` 监控系统状态

## 🐛 故障排除

| 问题 | 解决方案 |
|------|----------|
| Redis连接失败 | 检查Redis服务状态和配置 |
| 代理获取失败 | 检查网络连接和目标网站状态 |
| 验证速度慢 | 增加并发数或更换验证URL |
| 内存占用高 | 调整缓存大小和清理间隔 |

## 📝 开发计划

- [ ] 支持更多代理源
- [ ] 添加代理质量评分


## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 了解详情

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。

---

**注意**: 请遵守目标网站的使用条款，合理使用代理服务。