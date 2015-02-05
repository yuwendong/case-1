# -*- coding: utf-8 -*-
import pymongo

# first_user
domain_dict = {'folk':u'民众', 'media':u'媒体', 'opinion_leader':u'意见领袖', 'other':u'其他', 'oversea':u'海外'}
domain_list = ['folk', 'media', 'opinion_leader','oversea', 'other']

# community_util
weibo_fields_list = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', \
               'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', \
               'comments_count', 'sentiment', 'topics', 'message_type', 'terms']
user_fields_list = ['_id', 'name', 'gender', 'profile_image_url', 'friends_count', \
                            'followers_count', 'location', 'created_at','statuses_count']
emotions_kv = {0:u'无倾向', 1:u'高兴', 2:u'愤怒', 3:u'悲伤', 4:u'新闻'}
REDIS_HOST = '219.224.135.48'
REDIS_PORT = 6379
USER_DOMAIN = 'user_domain' # user domain hash
DOMAIN_LIST = ['folk', 'media', 'opinion_leader', 'oversea', 'other']

# community_information
MONGODB_HOST = '219.224.135.46'
MONGODB_PORT = 27019
conn = pymongo.Connection(host=MONGODB_HOST, port=MONGODB_PORT)
MONGODB_WEIBO = '54api_weibo_v2'
MONGODB_WEIBO_TOPIC_COLLECTION = 'master_timeline_topic'

def topic2xapian(topic, start_ts, end_ts):
    mongodb = conn[MONGODB_WEIBO]
    topic_collection = mongodb[MONGODB_WEIBO_TOPIC_COLLECTION]
    topic_weibos = topic_collection.find({'name':topic})
    if not topic_weibos:
        print 'this topic is not exist'
        return None
    else:
        topic_weibo_id = topic_weibos['_id']
        return topic_weibo_id

def getXapianWeiboByTopic(topic, start_ts, end_ts):
    topic_id  = topic2xapian(topic, start_ts, end_ts)
    XAPIAN_WEIBO_TOPIC_DATA_PATH = '/home/xapian/xapian_weibo_topic/'
    stub_file = XAPIAN_WEIBO_TOPIC_DATA_PATH + 'stub/xapian_weibo_topic_stub_' + str(topic_id)
    if os.path.exists(stub_file):
        print 'stub exist'
        xapian_search_weibo = XapianSearch(stub=stub_file, schema_version='5')
        return xapian_search_weibo
    else:
        print 'stub not exist'
        return None
