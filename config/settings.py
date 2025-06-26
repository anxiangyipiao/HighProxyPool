import yaml
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from utils.logger import logger

@dataclass
class RedisConfig:
    host: str
    port: int
    password: str
    db: int
    max_connections: int = 20
    socket_timeout: int = 30  # 更新默认值
    socket_connect_timeout: int = 15  # 更新默认值
    retry_on_timeout: bool = True  # 新增重试配置
    health_check_interval: int = 30  # 新增健康检查间隔

@dataclass
class FastAPIConfig:
    host: str
    port: int
    workers: int = 1
    reload: bool = False

@dataclass
class SchedulerConfig:
    verifier_interval: int
    fetch_interval: int
    verifier_url: str
    proxy_pool_name: str
    logger_name: str
    max_workers: int = 10
    max_concurrent_validations: int = 50

@dataclass
class ProxyConfig:
    timeout: int = 10
    max_retries: int = 3
    user_agents: list = None
    
    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ]

@dataclass
class AuthConfig:
    enabled: bool = False
    api_key: str = ""
    header_name: str = "X-API-Key"

@dataclass
class AppConfig:
    redis: RedisConfig
    fastapi: FastAPIConfig
    scheduler: SchedulerConfig
    proxy: ProxyConfig
    auth: AuthConfig

class ConfigManager:
    _instance = None
    _config: AppConfig = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._load_config()

    def _load_config(self):
        """加载配置文件"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)
        
        # 支持环境变量覆盖
        raw_config = self._apply_env_overrides(raw_config)
        
        # 验证配置
        self._validate_config(raw_config)
        
        self._config = AppConfig(
            redis=RedisConfig(**raw_config['redis']),
            fastapi=FastAPIConfig(**raw_config['fastapi']),
            scheduler=SchedulerConfig(**raw_config['scheduler']),
            proxy=ProxyConfig(**raw_config.get('proxy', {})),
            auth=AuthConfig(**raw_config.get('auth', {}))
        )
        
        logger.info("配置加载完成")

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境变量覆盖"""
        env_mappings = {
            'REDIS_HOST': ['redis', 'host'],
            'REDIS_PORT': ['redis', 'port'],
            'REDIS_PASSWORD': ['redis', 'password'],
            'REDIS_DB': ['redis', 'db'],
            'API_HOST': ['fastapi', 'host'],
            'API_PORT': ['fastapi', 'port'],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # 尝试转换类型
                if config_path[1] in ['port', 'db']:
                    value = int(value)
                
                # 设置配置值
                current = config
                for key in config_path[:-1]:
                    current = current.setdefault(key, {})
                current[config_path[-1]] = value
                
                logger.info(f"环境变量 {env_var} 覆盖配置: {'.'.join(config_path)} = {value}")
        
        return config

    def _validate_config(self, config: Dict[str, Any]):
        """验证配置有效性"""
        required_sections = ['redis', 'fastapi', 'scheduler']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"配置文件缺少必需的节: {section}")
        
        # 验证Redis配置
        redis_config = config['redis']
        if not isinstance(redis_config.get('port'), int) or redis_config['port'] <= 0:
            raise ValueError("Redis端口必须是正整数")
        
        # 验证API配置
        api_config = config['fastapi']
        if not isinstance(api_config.get('port'), int) or api_config['port'] <= 0:
            raise ValueError("API端口必须是正整数")
        
        # 验证调度器配置
        scheduler_config = config['scheduler']
        if scheduler_config.get('verifier_interval', 0) <= 0:
            raise ValueError("验证间隔必须是正整数")
        if scheduler_config.get('fetch_interval', 0) <= 0:
            raise ValueError("获取间隔必须是正整数")

    @property
    def config(self) -> AppConfig:
        return self._config
    
    def reload_config(self):
        """重新加载配置"""
        self._config = None
        self._load_config()
        logger.info("配置已重新加载")

# 全局配置实例
config_manager = ConfigManager()