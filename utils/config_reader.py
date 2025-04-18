

import yaml

class ConfigReader:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    def get_redis_config(self):
        return {
            'host': self.config['redis']['host'],
            'port': self.config['redis']['port'],
            'password': self.config['redis']['password'],
            'db': self.config['redis']['db']
        }

    def get_flask_config(self):
        return {
            'host': self.config['fastapi']['host'],
            'port': self.config['fastapi']['port'],
        }
    
    def get_scheduler_config(self):
        return {
            'verifier_interval': self.config['scheduler']['verifier_interval'],
            'fetch_interval': self.config['scheduler']['fetch_interval'],
            'verifier_url': self.config['scheduler']['verifier_url'],
            'proxy_pool_name': self.config['scheduler']['proxy_pool_name'],
            'logger_name': self.config['scheduler']['logger_name'],
        }
    



# 全局实例
config_reader = ConfigReader('config.yaml')

redis_config = config_reader.get_redis_config()

flask_config = config_reader.get_flask_config()

scheduler_config = config_reader.get_scheduler_config()


