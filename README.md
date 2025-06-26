# HighProxyPool - 高效代理池系统

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

一个高效、稳定、功能丰富的代理池系统，支持多源代理获取、智能验证、性能监控和RESTful API服务。

## 🌟 功能特性

### 核心功能
- **多源代理获取**: 支持从多个免费代理网站获取代理IP
- **智能代理验证**: 异步批量验证代理可用性，自动清理无效代理
- **高性能存储**: 基于Redis的代理存储，支持缓存优化
- **任务调度**: 自动定时获取和验证代理，保持代理池活跃
- **RESTful API**: 提供完整的HTTP API接口，易于集成

### 高级特性
- **性能监控**: 实时监控系统资源使用情况和代理统计
- **健康检查**: 全面的系统健康状态检查
- **异步架构**: 全异步设计，支持高并发处理
- **容器化部署**: 支持Docker和Docker Compose部署
- **配置管理**: 灵活的YAML配置文件，支持环境变量覆盖

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Redis 5.0+
- 8GB+ 内存推荐

### 安装依赖

```bash
# 克隆项目
git clone <项目地址>
cd HighProxyPool

# 安装Python依赖
pip install -r requirements.txt
```

### 配置设置

编辑 `config.yaml` 文件：

```yaml
redis:
  host: "localhost"
  port: 6379
  password: ""
  db: 1

fastapi:
  host: "0.0.0.0"
  port: 8001

scheduler:
  verifier_interval: 900  # 15分钟验证一次
  fetch_interval: 3600    # 60分钟获取一次
  verifier_url: "http://www.baidu.com"
```

### 运行方式

#### 1. 命令行模式（推荐用于开发）
```bash
# 运行异步调度器（后台模式）
python main.py

# 运行API服务器
python app.py
```

#### 2. Docker部署（推荐用于生产）
```bash
# 使用Docker Compose一键部署
docker-compose up -d

# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

## 📡 API接口

### 基础接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API首页和文档 |
| `/api/get_proxy` | GET | 获取一个可用代理 |
| `/api/proxy_count` | GET | 获取代理池数量 |
| `/api/proxy_stats` | GET | 获取详细统计信息 |

### 管理接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/refresh_proxies` | POST | 手动触发代理获取 |
| `/api/clean_proxies` | POST | 手动触发代理清理 |
| `/api/health` | GET | 系统健康检查 |

### 使用示例

```python
import requests

# 获取代理
response = requests.get('http://localhost:8001/api/get_proxy')
if response.status_code == 200:
    proxy_data = response.json()
    proxy = proxy_data['proxy']['http']
    print(f"获取到代理: {proxy}")

# 获取代理数量
response = requests.get('http://localhost:8001/api/proxy_count')
count = response.json()['count']
print(f"代理池共有 {count} 个代理")
```

```bash
# 使用curl
curl http://localhost:8001/api/get_proxy
curl http://localhost:8001/api/proxy_count
curl -X POST http://localhost:8001/api/refresh_proxies
```

## 🏗️ 项目架构

```
HighProxyPool/
├── main.py                 # 异步调度器入口
├── app.py                  # FastAPI应用入口
├── config.yaml            # 配置文件
├── requirements.txt        # Python依赖
├── docker-compose.yml      # Docker部署配置
├── config/                 # 配置管理模块
│   └── settings.py        # 配置类定义
├── core/                   # 核心业务逻辑
│   ├── proxy_manager.py   # 代理管理器
│   ├── fetchers/          # 代理获取器
│   │   ├── bajiu_fetcher.py
│   │   ├── kuaidaili_fetcher.py
│   │   └── base_fetcher.py
│   ├── validators/        # 代理验证器
│   │   └── proxy_validator.py
│   └── interfaces/        # 接口定义
├── storage/               # 数据存储模块
│   ├── redis_storage.py   # Redis存储实现
│   └── cached_redis_storage.py  # 缓存优化存储
├── utils/                 # 工具模块
│   ├── logger.py         # 日志管理
│   ├── scheduler.py      # 异步调度器
│   ├── monitoring.py     # 性能监控
│   └── exceptions.py     # 异常定义
├── tests/                # 测试模块
├── logs/                 # 日志文件
└── README.md            # 项目文档
```

## 🎯 核心组件

### 代理管理器 (ProxyManager)
- 统一管理代理的获取、验证和存储
- 支持多个代理源的并发获取
- 智能的代理验证和清理机制

### 代理获取器 (Fetchers)
- **89免费代理**: 支持浏览器渲染的JavaScript页面
- **快代理**: 支持多页面并发获取
- **扩展性**: 易于添加新的代理源

### 代理验证器 (Validator)
- 异步批量验证，提高效率
- 可配置的并发数和超时时间
- 智能重试机制

### 存储系统 (Storage)
- **Redis存储**: 高性能的内存数据库
- **缓存优化**: 本地缓存减少Redis访问
- **批量操作**: 提高数据操作效率

### 异步调度器 (Scheduler)
- 基于APScheduler的异步任务调度
- 支持定时任务和手动触发
- 完善的错误处理和日志记录

## 📊 性能特性

### 高并发处理
- 全异步架构，支持大量并发请求
- 连接池复用，减少资源开销
- 智能的限流和错误处理

### 内存优化
- 本地缓存减少Redis访问频率
- 定期清理过期数据
- 合理的数据结构设计

### 监控告警
- 实时系统资源监控
- 代理池状态监控
- 健康检查和异常告警

## 🔧 配置说明

### Redis配置
```yaml
redis:
  host: "localhost"          # Redis服务器地址
  port: 6379                # Redis端口
  password: ""              # Redis密码
  db: 1                     # 数据库编号
  max_connections: 20       # 最大连接数
  socket_timeout: 5         # 套接字超时
```

### API配置
```yaml
fastapi:
  host: "0.0.0.0"          # API服务地址
  port: 8001               # API服务端口
  workers: 1               # 工作进程数
  reload: false            # 是否自动重载
```

### 调度器配置
```yaml
scheduler:
  verifier_interval: 900   # 验证间隔(秒)
  fetch_interval: 3600     # 获取间隔(秒)
  verifier_url: "http://www.baidu.com"  # 验证URL
  max_concurrent_validations: 50        # 最大并发验证数
```

## 🔍 监控和日志

### 日志系统
- 分级日志记录（DEBUG, INFO, WARNING, ERROR）
- 文件滚动，避免日志文件过大
- 结构化日志，便于分析

### 性能监控
- CPU、内存、磁盘使用率监控
- 请求响应时间统计
- 错误率和成功率统计

### 健康检查
- Redis连接状态检查
- 代理池状态检查
- 系统资源状态检查

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_proxy_manager.py

# 运行测试并显示覆盖率
pytest --cov=core --cov=storage --cov=utils
```

## 🚀 部署建议

### 开发环境
- 使用 `python main.py` 运行调度器
- 使用 `python app.py` 运行API服务
- 本地Redis实例

### 生产环境
- 使用Docker Compose部署
- 配置Redis持久化
- 设置日志轮转
- 配置监控告警

### 性能优化
- 增加Redis内存
- 调整并发验证数量
- 优化获取和验证间隔
- 使用负载均衡

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 开发计划

- [ ] 支持更多代理源
- [ ] 添加代理质量评分
- [ ] 实现地理位置过滤
- [ ] 支持HTTPS代理
- [ ] 添加Web管理界面
- [ ] 实现分布式部署

## ❓ 常见问题

### Q: 代理获取失败怎么办？
A: 检查网络连接，确认代理源网站可访问，查看日志了解具体错误。

### Q: Redis连接失败？
A: 检查Redis服务状态，确认连接配置正确，检查防火墙设置。

### Q: 代理验证太慢？
A: 可以增加并发验证数量，调整超时时间，或更换验证URL。

### Q: 如何添加新的代理源？
A: 继承BaseFetcher类，实现fetch_proxies方法，在ProxyManager中注册。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- FastAPI - 现代高性能Web框架
- Redis - 高性能内存数据库
- APScheduler - 高级Python调度器
- 所有贡献者和用户的支持

---

**注意**: 请遵守相关网站的robots.txt和使用条款，合理使用代理服务。