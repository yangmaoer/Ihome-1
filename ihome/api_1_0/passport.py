# coding:utf-8

from . import api
from flask import request, jsonify, current_app,session
from ihome.utils.response_code import RET
import re
from ihome import redis_store, db
from ihome.models import User
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


# @api.route('/users', methods=['POST'])
@api.route("/users", methods=["POST"])
def register():
    """参数：手机号，短信验证码，密码"""
    # 获取请求的json数据，返回字典
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    smscode = req_dict.get('smscode')
    passwd = req_dict.get('passwd')
    passwd2 = req_dict.get('passwd2')

    # 校验参数
    if not all([mobile, smscode, passwd, passwd2]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 判断手机号格式
    if not re.match(r'1[34578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    if passwd2 != passwd:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码不一致")

    # 从redis中取出短信验证码,若过期为None，而不是抛出异常
    try:
        real_smscode = redis_store.get('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="读取真实短信验证码异常")

    # 判断短信验证码是否过期
    if real_smscode is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")

    # 删除redis中的短信验证码，防止重复使用校验
    try:
        redis_store.delete('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 判断用户填写短信验证码的正确性
    if real_smscode != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    # 在用户访问时，瓶颈是对数据库的访问，因此尽量减少对数据库的访问量，由于采用了unique方式，在插入重复数据时数据库会自动抛出异常
    # 保存用户到数据库中
    user=User(name=mobile,mobile=mobile)

    # 密码管理
    user.password=passwd

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库回滚
        db.session.rollback()
        # 记录日志信息
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")
    except Exception as e:
        # 数据库回滚
        db.session.rollback()
        # 记录日志信息
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")

    # 保存登录状态到session中
    session['name']=mobile
    session['mobile']=mobile
    session['user_id']=user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")