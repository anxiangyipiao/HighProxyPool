# HighProxyPool - 高效代理池系统

一个基于 Python 的高性能代理池管理系统，支持多源代理获取、智能验证、性能监控和 RESTful API 服务。

## 📋 项目特性

### 🔧 核心功能
- **多源代理获取**: 支持89免费代理、快代理等多个代理源
- **智能代理验证**: 异步批量验证，自动清理无效代理
- **高效缓存存储**: Redis + 本地缓存双重优化
- **异步任务调度**: 定时获取和验证代理
- **RESTful API**: 完整的HTTP API接口

### 🚀 性能优化
- **异步IO**: 全异步架构，支持高并发
- **连接池管理**: Redis连接池优化
- **批量操作**: 支持代理的批量添加/删除
- **智能重试**: 自动重试机制和故障恢复
- **本地缓存**: 减少Redis访问频率

### 📊 监控运维
- **健康检查**: 系统和组件状态监控
- **性能指标**: CPU、内存、响应时间等监控
- **详细日志**: 分级日志记录和轮转
- **统计分析**: 代理池使用统计

## 🏗️ 系统架构

```
HighProxyPool/
├── app.py                 # FastAPI应用入口
├── main.py               # 异步调度器入口
├── config.yaml           # 配置文件
├── requirements.txt      # 依赖包
├── core/                 # 核心业务逻辑
│   ├── proxy_manager.py  # 代理管理器
│   ├── fetchers/         # 代理获取器
│   │   ├── base_fetcher.py
│   │   ├── bajiu_fetcher.py
│   │   └── kuaidaili_fetcher.py
│   ├── validators/       # 代理验证器
│   │   └── proxy_validator.py
│   └── interfaces/       # 接口定义
├── storage/              # 存储层
│   ├── redis_storage.py
│   └── cached_redis_storage.py
├── utils/                # 工具模块
│   ├── logger.py         # 日志管理
│   ├── scheduler.py      # 任务调度
│   ├── monitoring.py     # 性能监控
│   └── exceptions.py     # 异常定义
└── config/               # 配置管理
    └── settings.py
```

## 🛠️ 安装部署

### 环境要求
- Python 3.9+
- Redis 5.0+
- Chrome浏览器 (用于DrissionPage)

### 1. 克隆项目
```bash
git clone <repository-url>
cd HighProxyPool
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置文件
修改 `config.yaml` 中的配置：
```yaml
redis:
  host: "your-redis-host"
  port: 6379
  password: "your-password"
  db: 1

fastapi:
  host: "0.0.0.0"
  port: 8001

auth:
  enabled: true
  api_key: "your-secret-api-key"
```

### 4. 启动服务

#### 方式一：直接运行
```bash
# 启动异步调度器
python main.py

# 启动API服务（另开终端）
python app.py
```

#### 方式二：Docker部署
```bash
# 构建并启动服务
docker-compose up -d
```

## 📚 API接口

### 基础接口
| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 首页和接口概览 |
| `/api/get_proxy` | GET | 获取一个可用代理 |
| `/api/proxy_count` | GET | 获取代理池数量 |
| `/api/proxy_stats` | GET | 获取代理统计信息 |

### 管理接口
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/refresh_proxies` | POST | 手动刷新代理 |
| `/api/clean_proxies` | POST | 手动清理无效代理 |
| `/api/health` | GET | 系统健康检查 |

### API认证
所有API接口都支持API Key认证，在请求头中添加：
```
X-API-Key: your-secret-api-key
```

### 使用示例
```python
import requests

# 获取代理
response = requests.get(
    "http://localhost:8001/api/get_proxy",
    headers={"X-API-Key": "your-secret-api-key"}
)
proxy = response.json()["proxy"]
print(f"获取到代理: {proxy}")

# 获取代理数量
response = requests.get(
    "http://localhost:8001/api/proxy_count",
    headers={"X-API-Key": "your-secret-api-key"}
)
count = response.json()["count"]
print(f"代理池数量: {count}")
```

## ⚙️ 配置说明

### Redis配置
```yaml
redis:
  host: "127.0.0.1"           # Redis主机
  port: 6379                  # Redis端口
  password: ""                # Redis密码
  db: 1                       # Redis数据库
  max_connections: 20         # 最大连接数
  socket_timeout: 30          # 连接超时
```

### 调度器配置
```yaml
scheduler:
  fetch_interval: 360         # 获取间隔(秒)
  verifier_interval: 90       # 验证间隔(秒)
  verifier_url: "http://www.baidu.com"  # 验证URL
  max_concurrent_validations: 50        # 最大并发验证数
```

### API配置
```yaml
fastapi:
  host: "0.0.0.0"            # 监听地址
  port: 8001                 # 监听端口
  workers: 1                 # 工作进程数

auth:
  enabled: true              # 是否启用认证
  api_key: "your-key"        # API密钥
  header_name: "X-API-Key"   # 认证头名称
```

## 🔍 监控指标

### 系统健康检查
- Redis连接状态
- 代理池数量状态
- 系统资源使用率

### 性能指标
- CPU使用率
- 内存使用率
- 请求响应时间
- 错误率统计

## 🚀 扩展功能

### 添加新的代理源
1. 在 `core/fetchers/` 目录下创建新的获取器
2. 继承 `BaseFetcher` 和实现 `ProxyFetcherInterface`
3. 在 `ProxyManager` 中注册新的获取器

### 自定义验证逻辑
修改 `ProxyValidator` 类中的验证方法，支持自定义验证URL和规则。

## 📝 日志管理

日志文件位置：`logs/app.log`

日志级别：
- INFO: 常规信息
- WARNING: 警告信息
- ERROR: 错误信息
- DEBUG: 调试信息

## 🔧 故障排除

### 常见问题
1. **Redis连接失败**: 检查Redis服务状态和配置
2. **代理获取失败**: 检查网络连接和目标网站状态
3. **浏览器相关错误**: 确保Chrome浏览器已安装

### 性能调优
- 调整Redis连接池大小
- 优化并发验证数量
- 合理设置获取和验证间隔

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

---

**HighProxyPool** - 让代理管理更简单高效！