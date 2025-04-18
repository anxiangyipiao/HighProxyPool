import redis
import threading
from utils.config_reader import redis_config  


class RedisObject:
    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 从配置文件中读取 Redis 配置
        self.host = redis_config['host']
        self.port = redis_config['port']
        self.password = redis_config['password']
        self.db = redis_config['db']
        self.pool = None

    def get_connection(self) -> redis.StrictRedis:
        """获取 Redis 连接"""
        if not self.pool:
            try:
                self.pool = redis.ConnectionPool(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    db=self.db,
                    socket_timeout=5,
                    max_connections=469
                )
            except redis.ConnectionError as e:
                raise Exception(f"Redis 连接池创建失败: {e}")

        try:
            conn = redis.StrictRedis(connection_pool=self.pool, decode_responses=True)
            return conn
        except redis.ConnectionError as e:
            raise Exception(f"Redis 连接失败: {e}")
