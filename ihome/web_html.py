# coding:utf-8

from flask import Blueprint, current_app, make_response
from flask_wtf import csrf

# 静态文件蓝图
html = Blueprint('web_html', __name__)


@html.route('/<re(r".*"):file_name>')  # 注意这个地方的引号的嵌套
def get_html(file_name):
    # 提供html文件
    if not file_name:
        file_name = 'index.html'
    if file_name != 'favicon.ico':
        file_name = 'html/' + file_name

    # 生成csrf_token值
    csrf_token = csrf.generate_csrf()
    resp = make_response(current_app.send_static_file(file_name))
    # 设置cookie
    resp.set_cookie('csrf_token', csrf_token)
    return resp
