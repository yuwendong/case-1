# -*- coding: utf-8 -*-

import pymongo
from weibo import Client
from dogapi.utils import resp2item_search
from dogapi.pipelines.mongodbPipeline import MongodbPipeline
from global_config import API_HOST, API_PORT, MASTER_TIMELINE_54API_MONGOD_HOST, \
MASTER_TIMELINE_54API_MONGOD_PORT, MASTER_TIMELINE_54API_WEIBO_DB, \
MASTER_TIMELINE_54API_USER_COLLECTION, MASTER_TIMELINE_54API_WEIBO_DAILY_COLLECTION_PREFIX, \
MASTER_TIMELINE_54API_WEIBO_TOPIC_COLLECTION_PREFIX, MASTER_TIMELINE_54API_TOPIC_COLLECTION, \
MASTER_TIMELINE_54API_WEIBO_REPOST_COLLECTION


def get_client(api_host=API_HOST, api_port=API_PORT):
    return Client(api_host, api_port)


def _default_mongo(host=MASTER_TIMELINE_54API_MONGOD_HOST, \
	port=MASTER_TIMELINE_54API_MONGOD_PORT, usedb=MASTER_TIMELINE_54API_WEIBO_DB):
    # 强制写journal，并强制safe
    connection = pymongo.MongoClient(host=host, port=port, j=True, w=1)
    db = connection.admin
    # db.authenticate('root', 'root')
    db = getattr(connection, usedb)
    return db

mongo = _default_mongo()
weibo_client = get_client(API_HOST, API_PORT)

def items2mongo(items, weibo_mode='DAILY'):
    pipeline = MongodbPipeline(MASTER_TIMELINE_54API_WEIBO_DB, \
        MASTER_TIMELINE_54API_MONGOD_HOST, MASTER_TIMELINE_54API_MONGOD_PORT, \
        MASTER_TIMELINE_54API_USER_COLLECTION, MASTER_TIMELINE_54API_WEIBO_DAILY_COLLECTION_PREFIX, \
        MASTER_TIMELINE_54API_WEIBO_TOPIC_COLLECTION_PREFIX, weibo_mode, \
        MASTER_TIMELINE_54API_TOPIC_COLLECTION, MASTER_TIMELINE_54API_WEIBO_REPOST_COLLECTION)

    for item in items:
        pipeline.process_item_sync(item, spider=None)


def getWeiboById(mid):
    weibo = mongo.master_timeline_weibo_repost.find_one({'_id': int(mid)})
    if weibo:
        return weibo
    else:
        weibo = weibo_client.get('/showBatch', ids=int(mid))['statuses'][0]
        
        items = resp2item_search(weibo, 8)
        items2mongo(items, weibo_mode='REPOST')

        return weibo


def updateWeiboById(mid):
    weibo = weibo_client.get('/showBatch', ids=int(mid))['statuses'][0]
        
    items = resp2item_search(weibo, 8)
    items2mongo(items, weibo_mode='REPOST')

    return weibo


def getTopicByName(name):
    topic = mongo.master_timeline_topic.find_one({'name': name})
    if topic:
        return topic
    else:
        return None
