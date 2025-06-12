import yaml
import os
from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class RedisConfig:
    host: str
    port: int
    password: str
    db: int

@dataclass
class FastAPIConfig:
    host: str
    port: int

@dataclass
class SchedulerConfig:
    verifier_interval: int
    fetch_interval: int
    verifier_url: str
    proxy_pool_name: str
    logger_name: str

@dataclass
class AppConfig:
    redis: RedisConfig
    fastapi: FastAPIConfig
    scheduler: SchedulerConfig

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
        
        self._config = AppConfig(
            redis=RedisConfig(**raw_config['redis']),
            fastapi=FastAPIConfig(**raw_config['fastapi']),
            scheduler=SchedulerConfig(**raw_config['scheduler'])
        )

    @property
    def config(self) -> AppConfig:
        return self._config

# 全局配置实例
config_manager = ConfigManager()