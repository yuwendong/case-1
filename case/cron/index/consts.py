# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:@219.224.135.46/weibocase?charset=utf8'
INDEX_PATH = '/home/ubuntu3/huxiaoqian/case_test/data/stubpath/master_timeline_weibo_20130901'
# Create application
app = Flask(__name__)


# Create dummy secret key so we can use sessions
app.config['SECRET_KEY'] = 'A0Zr98j/3yX R~XHH!jmNJLWX/,?RT'


# Create database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)
