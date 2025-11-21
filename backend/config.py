"""
應用配置
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """基礎配置"""
    DEBUG = False
    TESTING = False
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False

class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    DEVELOPMENT = True
    PORT = int(os.getenv('PORT', 5000))

class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    DEVELOPMENT = False
    PORT = int(os.getenv('PORT', 5000))

class TestingConfig(Config):
    """測試環境配置"""
    TESTING = True
    DEBUG = True

# 獲取當前配置
def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
