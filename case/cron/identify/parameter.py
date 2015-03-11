# -*- coding: utf-8 -*-
import pymongo
from config import MONGODB_HOST, MONGODB_PORT

conn = pymongo.Connection(host=MONGODB_HOST, port=MONGODB_PORT)

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 60 * Minute
sixHour = Hour * 6
Day = Hour * 24

#cron_topic_identify
MODULE_T_S = 'identify'
TOPIC = u'外滩踩踏'
START = '2014-12-31'
END = '2015-01-10'
MONGODB_WEIBO = '54api_weibo_v2'
MONGODB_WEIBO_TOPIC_COLLECTION = 'master_timeline_topic'
MAX_SIZE = 100000
TOPK = 100000
gexf_type = 1
ds_gexf_type = 2

# get_first_user
fields_list = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', \
               'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', \
               'comments_count', 'sentiment', 'topics', 'message_type', 'terms']

user_fields_list = ['_id', 'name', 'gender', 'profile_image_url', 'friends_count', \
                    'followers_count', 'location', 'created_at','statuses_count']
first_user_count = 20
domain_list = ['folk', 'media', 'opinion_leader', 'oversea', 'other']
domain_en2ch = {'folk': u'民众', 'media': u'媒体', 'opinion_leader': u'意见领袖', 'oversea': u'海外', 'other': u'其他'}
USER_DOMAIN = 'user_domain' # user domain hash
DOMAIN_LIST = ['folk', 'media', 'opinion_leader', 'oversea', 'other']
#area
DEFAULT_INTERVAL = Hour
network_type = 1
ds_network_type = 2
cut_degree = 1

#fu_tr
weibo_fields_list = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', \
               'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', \
               'comments_count', 'sentiment', 'topics', 'message_type']
field_list = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', \
                  'reposts_count','comments_count','terms']
USER_DOMAIN = 'user_domain'
MinInterval = Fifteenminutes
fu_tr_during = Day
trend_maker_count = 20
trend_pusher_count = 20
fu_tr_unit = 900
fu_tr_top_keyword = 50
p_during = Hour

# cron_news_identify
NEWS_MODULE = 'i_news'
NEWS_TOPIC = u'全军政治工作会议'
NEWS_START_TS = 1415030400
NEWS_END_TS = 1415808000
MONGODB_NEWS = 'news'
MONGODB_NEWS_TOPIC_COLLECTION = 'news_topic'

# early_join_news
all_fields = ['id', '_id', 'title', 'url', 'summary', 'timestamp', \
                   'datetime', 'date', 'thumbnail_url', 'user_id', 'user_url', \
                   'user_image_url', 'user_name', 'source_website', \
                   'category', 'same_news_num', 'more_same_link', \
                   'relative_news', 'key', 'key', 'tplid', 'classid', 'title1', \
                   'content168','isV', 'Pagesize', 'Showurl', 'source_from_name' ,\
                   'Replies', 'last_modify', 'first_in', 'news_author', 'transmit_name', 'weight']
filter_fields = ['user_id', 'user_url', 'user_image_url', 'user_name',\
                      'relative_news', 'key', 'tplid', 'classid', 'isV', 'Pagesize', 'Showurl' ,\
                      'Replies', 'last_modify', 'first_in','news_author']
first_news_count = 20

# trend_user_news
During = Day # 计算波峰波谷的时间粒度
pusher_during = Hour # 计算推动者的时间粒度
unit = 900
maker_news_count = 20
pusher_news_count = 20
interval_count_during = Day
title_term_weight = 5
content_term_weight = 1

# 通过mongo中topic_id， 获取对应xapian的名称
def weibo_topic2xapian(topic_name, start_ts, end_ts):
    mongodb = conn[MONGODB_WEIBO]
    topic_collection = mongodb[MONGODB_WEIBO_TOPIC_COLLECTION]
    topic_weibos = topic_collection.find_one({'name': topic_name})
    if not topic_weibos:
        print 'this topic is not exist in mongodb'
        return None
    else:
        topic_weibo_id = topic_weibos['_id']
        return topic_weibo_id

#通过topic, start_ts, end_ts获取news_topic中对应的object_id，然后找到对应的collection
def get_dynamic_mongo(topic, start_ts, end_ts):
    mongodb = conn[MONGODB_NEWS]
    topic_collection = mongodb[MONGODB_NEWS_TOPIC_COLLECTION] 
    '''
    topic_news = topic_collection.find_one({'topic':topic, 'startts':start_ts, 'endts':end_ts}) # 保证时间范围是在该数据
    '''
    topic_news = topic_collection.find_one({'topic':topic})
    if not topic_news:
        print 'this topic is not exist'
        return None
    else:
        topic_news_id = topic_news['_id']
        news_collection_name = 'post_' + str(topic_news_id) 
        topic_news_collection = mongodb[news_collection_name] # 这里的调用方法可能会有问题
        comment_collection_name = 'comment_' + str(topic_news_id)
        topic_comment_collection = mongodb[comment_collection_name]
    return topic_news_collection, topic_comment_collection


    
    
    
    
    
    


