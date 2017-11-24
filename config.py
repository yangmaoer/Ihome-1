# coding:utf-8
import redis


class Config(object):
    SECRET_KEY = 'RENfnrwnbfNFN44RMRJWfror'

    # 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # flask-session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对cookie中的session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400  # SESSION数据有效期，单位s


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


CONFIG_MAP = {
    'develop': DevelopmentConfig,
    'product': ProductionConfig
}
