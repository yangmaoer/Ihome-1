# coding:utf-8

from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants
from flask import current_app, jsonify, make_response
from ihome.utils.response_code import RET


@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id: 图片验证码编号
    :return: 正常情况：验证码图片 异常情况：返回json
    """
    # 业务逻辑处理
    # 生成验证码图片
    # 名字，真实文本，图片数据
    name, text, image_data = captcha.generate_captcha()
    # 将验证码真实值与编号保存到redis
    try:
        redis_store.setex('image_code_%s' % image_code_id, constants.IMAGE_REDIS_EXPIRES, text)
    except Exception as e:
        # 把错误信息记录到日志中
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errormsg='save image code failed')
    # 返回图片
    resp = make_response(image_data)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp
