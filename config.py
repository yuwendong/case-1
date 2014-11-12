# -*- coding: utf-8 -*-

from case.global_config import MYSQL_HOST, MYSQL_USER, MYSQL_DB

# the debug toolbar is only enabled in debug mode
DEBUG = True

ADMINS = frozenset(['youremail@yourdomain.com'])
SECRET_KEY = 'SecretKeyForSessionSigning'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://%s:@%s/%s?charset=utf8' % (MYSQL_USER, MYSQL_HOST, MYSQL_DB)
SQLALCHEMY_ECHO = False
DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 8

CSRF_ENABLED = True
CSRF_SESSION_KEY= 'somethingimpossibletoguess'
