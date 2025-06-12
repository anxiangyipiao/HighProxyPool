# HighProxyPool - 高效代理池系统 (优化版本)

## 项目概述

HighProxyPool 是一个高效、可扩展的代理池管理系统，经过全面重构后，具有更好的架构设计、错误处理和扩展性。

## 🚀 主要特性

- **模块化架构**: 清晰的分层设计，易于维护和扩展
- **异步支持**: 全面的异步/await支持，提高性能
- **接口抽象**: 使用接口设计模式，便于添加新的代理源和存储后端
- **完善的错误处理**: 统一的异常处理机制
- **高级日志系统**: 支持文件轮转和多级别日志
- **配置管理**: 基于YAML的配置系统，支持环境变量
- **调度系统**: 增强的任务调度器，支持监控和错误恢复
- **RESTful API**: FastAPI驱动的现代API接口
- **类型提示**: 全面的类型注解，提高代码质量

## 📁 项目结构

```
HighProxyPool/
├── config/                 # 配置管理
│   ├── __init__.py
│   └── settings.py        # 配置类定义
├── core/                  # 核心业务逻辑
│   ├── interfaces/        # 接口定义
│   │   ├── fetcher_interface.py
│   │   └── validator_interface.py
│   ├── fetchers/          # 代理获取器
│   │   ├── base_fetcher.py
│   │   └── bajiu_fetcher.py
│   ├── validators/        # 代理验证器
│   │   └── proxy_validator.py
│   └── proxy_manager.py   # 代理管理器
├── storage/               # 数据存储
│   ├── storage_interface.py
│   └── redis_storage.py
├── utils/                 # 工具模块
│   ├── exceptions.py      # 异常定义
│   ├── logger.py         # 日志系统
│   └── scheduler.py      # 调度器
├── logs/                 # 日志文件目录
├── config.yaml           # 配置文件
├── main.py              # 主程序入口
├── app.py               # API服务入口
└── requirements.txt     # 依赖文件
```

## 🛠️ 安装与配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置Redis

确保Redis服务正在运行，默认配置：
- 主机: localhost
- 端口: 6379
- 数据库: 0

### 3. 修改配置

编辑 `config.yaml` 文件以适应您的环境：

```yaml
redis:
  host: "localhost"
  port: 6379
  password: ""
  db: 0

fastapi:
  host: "0.0.0.0"
  port: 8000

scheduler:
  verifier_interval: 300    # 代理验证间隔(秒)
  fetch_interval: 1800     # 代理获取间隔(秒)
  verifier_url: "http://httpbin.org/ip"
  proxy_pool_name: "proxy_pool"
  logger_name: "HighProxyPool"
```

## 🚀 使用方法

### 方式1: 启动主程序（定时任务模式）

```bash
python main.py
```

这将启动代理池的后台服务，自动执行代理获取和验证任务。

### 方式2: 启动API服务

```bash
python app.py
```

这将启动FastAPI服务器，提供HTTP API接口。

## 📡 API接口

### 获取代理
```
GET /api/get_proxy
```

### 获取代理数量
```
GET /api/proxy_count
```

### 手动刷新代理
```
POST /api/refresh_proxies
```

### 清理无效代理
```
POST /api/clean_proxies
```

### 系统状态
```
GET /api/status
```

### API文档
访问 `http://localhost:8000/docs` 查看完整的API文档。

## 🔧 扩展性

### 添加新的代理源

1. 在 `core/fetchers/` 目录下创建新的获取器
2. 继承 `BaseFetcher` 并实现 `ProxyFetcherInterface`
3. 在 `ProxyManager` 中注册新的获取器

示例：
```python
from .base_fetcher import BaseFetcher
from ..interfaces.fetcher_interface import ProxyFetcherInterface

class NewProxyFetcher(BaseFetcher, ProxyFetcherInterface):
    def get_name(self) -> str:
        return "新代理源"
    
    async def fetch_proxies(self) -> List[Dict[str, str]]:
        # 实现代理获取逻辑
        pass
```

### 添加新的存储后端

1. 在 `storage/` 目录下创建新的存储实现
2. 实现 `StorageInterface` 接口
3. 在配置中指定新的存储后端

## 🔍 架构优势

### 1. 清晰的分层架构
- **接口层**: 定义抽象接口
- **业务层**: 实现核心业务逻辑
- **存储层**: 处理数据持久化
- **工具层**: 提供通用工具功能

### 2. 设计模式应用
- **策略模式**: 代理获取器和验证器
- **单例模式**: 配置管理器和调度器
- **工厂模式**: 存储后端创建
- **依赖注入**: 组件间解耦

### 3. 异步编程优势
- 高并发代理验证
- 非阻塞网络请求
- 更好的资源利用率

### 4. 完善的错误处理
- 自定义异常体系
- 统一的错误日志
- 优雅的降级处理

## 📊 性能优化

1. **并发控制**: 限制同时验证的代理数量
2. **连接池**: 复用HTTP连接
3. **指数退避**: 智能重试机制
4. **批量操作**: 减少Redis交互次数

## 🐳 Docker支持

### 使用Docker Compose

```bash
docker-compose up -d
```

这将启动Redis和代理池服务。

## 📝 日志系统

- 支持控制台和文件输出
- 文件自动轮转 (10MB)
- 多级别日志记录
- 结构化日志格式

日志文件位置: `logs/app.log`

## 🔐 安全性

- 输入验证和清理
- 安全的异常处理
- 资源泄露防护
- 请求频率限制

## 📈 监控和诊断

- 系统状态API
- 任务执行监控
- 性能指标收集
- 健康检查端点

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 📞 支持

如有问题或建议，请提交Issue或联系维护者。
