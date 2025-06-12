class ProxyPoolException(Exception):
    """代理池基础异常"""
    pass

class ProxyFetchError(ProxyPoolException):
    """代理获取异常"""
    pass

class ProxyValidationError(ProxyPoolException):
    """代理验证异常"""
    pass

class StorageError(ProxyPoolException):
    """存储异常"""
    pass

class ConfigError(ProxyPoolException):
    """配置异常"""
    pass

class SchedulerError(ProxyPoolException):
    """调度器异常"""
    pass