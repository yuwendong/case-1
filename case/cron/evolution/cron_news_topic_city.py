# -*- coding: utf-8 -*-

import sys
import IP   #引入IP，对'geo'字段进行解析
import json
import datetime
import pymongo
import random
from topics import _all_topics
from config import MONGODB_HOST, MONGODB_PORT, db, mtype_kv_news
from time_utils import datetime2ts, ts2HourlyTime
from global_utils import getTopicByName
from dynamic_xapian_weibo import getXapianWeiboByTopic
from model import CityTopicCountNews, CityNews


Minute = 60
Fifteenminutes = 15 * 60
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24

TOP_NEWS_LIMIT = 50
fields_list=['_id', 'url', 'timestamp', 'content168', 'relative_news', 'transmit_name', 'user_name', 'source_from_name', 'title', 'showurl']
SORT_FIELD = 'timestamp'

conn = pymongo.Connection(host=MONGODB_HOST, port=MONGODB_PORT)
mongodb = conn['news']

PROVINCE_LIST = ['安徽','北京','重庆','福建','甘肃','山东','广东','贵州','河北','黑龙江']

def get_filter_dict():
    fields_dict = {}
    for field in fields_list:
        fields_dict[field] = 1
    return fields_dict

def media2city(geo): #将weibo中的'geo'字段解析为地址
    idx = random.randint(0,9)
    geo = '中国 ' + PROVINCE_LIST[idx]

    geo = '\t'.join(geo.split())
    return geo
    '''
    try:
        province, city = geo.split()
        if province in [u'内蒙古自治区', u'黑龙江省']:
            province = province[:3]
        else:
            province = province[:2]

        geo = province + ' ' + city
    except:
        pass

    if isinstance(geo, unicode):
        geo = geo.encode('utf-8')

    if geo.split()[0] not in ['海外', '其他']:
        geo = '中国 ' + geo

    geo = '\t'.join(geo.split())

    return geo
    '''


def save_rt_results(topic, mtype, results, during, first_item):
    ts, ccount = results
    item = CityTopicCountNews(topic, during, ts, mtype, json.dumps(ccount), json.dumps(first_item))
    item_exist = db.session.query(CityTopicCountNews).filter(CityTopicCountNews.topic==topic, \
                                                                    CityTopicCountNews.range==during, \
                                                                    CityTopicCountNews.end==ts, \
                                                                    CityTopicCountNews.mtype==mtype).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()

def save_ns_results(topic, ts, during, n_limit, news):
    item = CityNews(topic , ts, during, n_limit, json.dumps(news))
    item_exist = db.session.query(CityNews).filter(CityNews.topic==topic, \
                                                          CityNews.range==during, \
                                                          CityNews.end==ts, \
                                                          CityNews.limit==n_limit).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()

def cityCronTopicNews(topic, mongo_collection, start_ts, over_ts, during=Fifteenminutes, n_limit=TOP_NEWS_LIMIT):
    if topic and topic != '':
        start_ts = int(start_ts)
        over_ts = int(over_ts)

        over_ts = ts2HourlyTime(over_ts, during)
        interval = (over_ts - start_ts) / during

        topics = topic.strip().split(',')
        for i in range(interval, 0, -1):
            ccount_dict = {}
            for k, v in mtype_kv_news.iteritems():
                ccount_dict[k] = {}

            begin_ts = over_ts - during * i
            end_ts = begin_ts + during
            first_timestamp = end_ts
            first_item = {}
            news = []

            query_dict = {
                'timestamp': {'$gt': begin_ts, '$lt': end_ts},
            }
            fields_dict = get_filter_dict()

            results_list = mongo_collection.find(query_dict, fields_dict).sort([(SORT_FIELD,1)])

            for weibo_result in results_list:
                if (weibo_result['timestamp'] <= first_timestamp ):
                    first_timestamp = weibo_result['timestamp']
                    first_item = weibo_result

                if weibo_result['source_from_name'] and weibo_result['transmit_name']:
                    source = media2city(weibo_result['source_from_name'])
                    try:
                        ccount_dict['forward'][source] += 1
                    except KeyError:
                        ccount_dict['forward'][source] = 1
                    try:
                        ccount_dict['sum'][source] += 1
                    except KeyError:
                        ccount_dict['sum'][source] = 1
                elif weibo_result['source_from_name']:
                    source = media2city(weibo_result['source_from_name'])
                    try:
                        ccount_dict['origin'][source] += 1
                    except KeyError:
                        ccount_dict['origin'][source] = 1
                    try:
                        ccount_dict['sum'][source] += 1
                    except KeyError:
                        ccount_dict['sum'][source] = 1
                else:
                    continue

                weibo_result['source_from_area'] = source # 添加区域字段
                news.append(weibo_result)

            for k, v in mtype_kv_news.iteritems():
                results = [end_ts, ccount_dict[k]]
                save_rt_results(topic,v, results, during, first_item)

            sorted_news = sorted(news, key=lambda k: k[SORT_FIELD], reverse=True)
            sorted_news = sorted_news[:n_limit]
            save_ns_results(topic, end_ts, during, n_limit, sorted_news)

def get_dynamic_mongo(topic, start_ts, end_ts):
    topic_collection = mongodb.news_topic
    topic_news = topic_collection.find_one({'topic':topic, 'startts':{'$lte':start_ts}, 'endts':{'$gte':end_ts}})
    if not topic_news:
        print 'no this topic'
        return None
    else:
        print 'exists'
        topic_news_id = topic_news['_id']
        news_collection_name = 'post_' + str(topic_news_id)
        topic_news_collection = mongodb[news_collection_name]
    return topic_news_collection

if __name__ == '__main__':
    start_ts = 1415030400
    end_ts = 1415750400
    topic =  u'全军政治工作会议'# u"外滩踩踏"
    mongo_collection = get_dynamic_mongo(topic, start_ts, end_ts)

    print 'topic: ', topic.encode('utf8'), 'from %s to %s' % (start_ts, end_ts)
    cityCronTopicNews(topic, mongo_collection, start_ts=start_ts, over_ts=end_ts, during=Fifteenminutes)

