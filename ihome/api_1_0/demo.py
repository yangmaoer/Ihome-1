#coding:utf-8
from . import api
from ihome import db
from flask import current_app


@api.route('/index')
def index():
    
    return 'index page'