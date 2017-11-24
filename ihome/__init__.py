# coding:utf-8

from flask import Flask
from config import CONFIG_MAP
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect

import redis

db = SQLAlchemy()

# 创建redis连接对象
redis_store = None


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