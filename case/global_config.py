# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from xapian_case.xapian_backend import XapianSearch

emotions_kv = {'happy': 1, 'angry': 2, 'sad': 3, 'news': 4}
emotions_zh_kv = {'happy': '高兴', 'angry': '愤怒', 'sad': '悲伤', 'news': '新闻'}
#这里的domainlist仅作为测试时使用，后面会通过对话题内的微博分类，获取其对应的领域domain_list
DOMAIN_LIST = ['culture', 'education', 'entertainment', 'fashion', 'finance', 'media', 'sports', 'technology', 'oversea', \
               'university', 'homeadmin', 'abroadadmin', 'homemedia', 'abroadmedia', 'folkorg', \
               'lawyer', 'politician', 'mediaworker', 'activer', 'grassroot', 'other']
DOMAIN_ZH_LIST = [u'文化', u'教育', u'娱乐', u'时尚', u'财经', u'媒体', u'体育', u'科技', u'境外', \
                  u'高校微博', u'境内机构', u'境外机构', u'境内媒体', u'境外媒体', u'民间组织', u'律师', \
                  u'政府官员', u'媒体人士', u'活跃人士', u'草根', u'其它']

IS_PROD = 0

if IS_PROD == 1:
    # 219.224.135.60
    MYSQL_HOST = '219.224.135.46'
    MYSQL_USER = 'root'
    MYSQL_DB = 'weibocase'
    SSDB_PORT = 8888
    SSDB_HOST = '219.224.135.47' # SSDB服务器在47
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:@219.224.135.46/weibocase?charset=utf8'
    XAPIAN_USER_DATA_PATH = '/home/ubuntu/dev/data/user-datapath/'
else:
    # 219.224.135.47
    MYSQL_HOST = '219.224.135.46'
    MYSQL_USER = 'root'
    MYSQL_DB = 'weibocase'
    SSDB_PORT = 8888
    SSDB_HOST = '219.224.135.47' # SSDB服务器在47
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:@219.224.135.46/weibocase?charset=utf8'
    XAPIAN_USER_DATA_PATH = '/home/ubuntu3/huxiaoqian/case_test/data/user-datapath/'

xapian_search_user = XapianSearch(path=XAPIAN_USER_DATA_PATH, name='master_timeline_user', schema_version=1)

# Create application
app = Flask('xxx')

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# Create database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)
