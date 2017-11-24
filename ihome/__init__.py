# coding:utf-8

from flask import Flask
from config import CONFIG_MAP
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect

import redis
import logging
from logging.handlers import RotatingFileHandler


db = SQLAlchemy()

# 创建redis连接对象
redis_store = None


# 配置日志信息
# 创建日志记录器，指明保存路径，日志大小及个数
file_log_handler=RotatingFileHandler('logs/log',maxBytes=1024*1024*100,backupCount=10)
# 创建日志记录的格式
formatter=logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# w为刚创建的日志记录设置格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象添加日志记录器
logging.getLogger().addHandler(file_log_handler)
# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)


# 工厂模式
def create_app(config_name):
    """
    创建flask的应用对象
    :param config_name:     配置模式的模式的名字
    :return:
    """
    app = Flask(__name__)

    # 根据配置模式的名字获取配置参数的类
    config_class = CONFIG_MAP.get(config_name)
    app.config.from_object(config_class)

    # 使用app初始化db
    db.init_app(app)

    # 初始化redis工具
    global redis_store
    redis_store=redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 用flask-session，将session数据保存到redis中
    Session(app)

    # 为flask补充csrf防护
    CSRFProtect(app)

    # 注册蓝图
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix="/api_1")

    return app