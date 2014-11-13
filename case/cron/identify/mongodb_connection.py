# -*- coding: utf-8 -*-
import pymongo
from config import MONGODB_HOST, MONGODB_PORT

conn = pymongo.Connection(host=MONGODB_HOST, port=MONGODB_PORT)
mongodb = conn['54api_weibo_v2']
collection = mongodb.master_timeline_user
