# coding:utf-8

from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
import re
from ihome import redis_store, db, constants
from ihome.models import User
from sqlalchemy.exc import IntegrityError
from ihome.utils.commons import login_required
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
    user = User(name=mobile, mobile=mobile)

    # 密码管理
    user.password = passwd

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
    session['name'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")


@api.route("/sessions", methods=["POST"])
def login():
    """用户登录
    参数： 手机号、密码， json
    """
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    passwd = req_dict.get("passwd")

    # 校验参数
    # 参数完整的校验
    if not all([mobile, passwd]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 手机号的格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    # 判断错误次数是否超过限制，如果超过限制，则返回
    # redis记录： "access_nums_请求的ip": "次数"
    user_ip = request.remote_addr  # 用户的ip地址
    try:
        access_nums = redis_store.get("access_num_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="错误次数过多，请稍后重试")

    # 从数据库中根据手机号查询用户的数据对象
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    # 用数据库的密码与用户填写的密码进行对比验证
    if user is None or not user.check_passwd(passwd):
        # 如果验证失败，记录错误次数，返回信息
        try:
            # redis的incr可以对字符串类型的数字数据进行加一操作，如果数据一开始不存在，则会初始化为1
            redis_store.incr("access_num_%s" % user_ip)
            redis_store.expire("access_num_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")

    # 如果验证相同成功，保存登录状态， 在session中
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="登录成功")


# @api.route('/users/login', methods=['POST'])
# def login():
#     req_dict = request.get_json()
#     mobile = req_dict.get('mobile')
#     passwd = req_dict.get('passwd')
#
#     # 检查参数
#     if not req_dict:
#         return jsonify(errno=RET.PARAMERR, errmsg="未接收到参数")
#
#     if not all([mobile, passwd]):
#         return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
#
#     # 手机号格式校验
#     if not re.match(r"^1[34578]\d{9}$", mobile):
#         return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")
#
#     # 判断用户名是否已注册
#     try:
#         user = User.query.filter_by(mobile=mobile).first()
#     except Exception as e:
#         current_app.logger.error(e)
#     else:
#         if user is None:
#             # 表示未注册
#             return jsonify(errno=RET.NODATA, errmsg="当前用户未注册")
#         elif user.check_passwd(passwd):
#             return jsonify(errno=0, errmsg="登陆成功")
#         else:
#             return jsonify(errno=RET.DATAERR, errmsg="登陆失败")
#
#     # 判断用户名是否已登陆
#     try:
#         user = session.get('name')
#     except Exception as e:
#         current_app.logger.error(e)
#     else:
#         if user is not None:
#             # 表明当前用户已登陆
#             return jsonify(errno=RET.DATAEXIST, errmsg='当前用户已登陆')


@api.route("/session", methods=["GET"])
def check_login():
    """
    检查登陆状态
    """
    # 尝试从session中获取用户的名字
    name = session.get("name")
    # 如果session中数据name名字存在，则表示用户已登录，否则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/session", methods=["DELETE"])
@login_required
def logout():
    """
    登出
    """
    # 清除session数据
    csrf_token = session.get("csrf_token")
    session.clear()
    session["csrf_token"] = csrf_token
    return jsonify(errno=RET.OK, errmsg="OK")
