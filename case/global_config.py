# -*- coding: utf-8 -*-

import os

emotions_kv = {'happy': 1, 'angry': 2, 'sad': 3}
emotions_zh_kv = {'happy': '高兴', 'angry': '愤怒', 'sad': '悲伤'}

IS_PROD = 0

if IS_PROD == 1:
    pass
else:
    # 219.224.135.60
    MYSQL_HOST = '219.224.135.60'
    MYSQL_USER = 'root'
    MYSQL_DB = 'weibo'
