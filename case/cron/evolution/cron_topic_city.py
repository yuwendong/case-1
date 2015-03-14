# -*- coding: utf-8 -*-

import sys
import json
import datetime
from topics import _all_topics

from time_utils import datetime2ts, ts2HourlyTime
from global_utils import getTopicByName
from dynamic_xapian_weibo import getXapianWeiboByTopic
from config import mtype_kv, db
from model import CityTopicCount, CityWeibos
from utils import geo2city, IP2city

Minute = 60
Fifteenminutes = 15 * 60
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24


TOP_WEIBOS_LIMIT = 50
RESP_ITER_KEYS = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'bmiddle_pic', 'geo', 'comments_count', 'sentiment', 'terms']
fields_list=['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', 'comments_count', 'sentiment', 'topics', 'message_type', 'terms']
SORT_FIELD = 'timestamp'


def save_rt_results(topic, results, during, first_item):
    for k, v in results.iteritems():
        mtype = k
        ts, ccount = v
        item = CityTopicCount(topic, during, ts, mtype, json.dumps(ccount), json.dumps(first_item))
        item_exist = db.session.query(CityTopicCount).filter(CityTopicCount.topic==topic, \
                                                                            CityTopicCount.range==during, \
                                                                            CityTopicCount.end==ts, \
                                                                            CityTopicCount.mtype==mtype).first()
        if item_exist:
            db.session.delete(item_exist)
        db.session.add(item)
    db.session.commit()

def save_ws_results(topic, ts, during, n_limit, weibos):
    item = CityWeibos(topic , ts, during, n_limit, json.dumps(weibos))
    item_exist = db.session.query(CityWeibos).filter(CityWeibos.topic==topic, \
                                                          CityWeibos.range==during, \
                                                          CityWeibos.end==ts, \
                                                          CityWeibos.limit==n_limit).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()

def cityCronTopic(topic, xapian_search_weibo, start_ts, over_ts, during=Fifteenminutes, n_limit=TOP_WEIBOS_LIMIT):
    if topic and topic != '':
        start_ts = int(start_ts)
        over_ts = int(over_ts)

        over_ts = ts2HourlyTime(over_ts, during)
        interval = (over_ts - start_ts) / during

        topics = topic.strip().split(',')
        for i in range(interval, 0, -1):
            mtype_ccount = {}  # mtype为message_type，ccount为{city：count}

            begin_ts = over_ts - during * i
            end_ts = begin_ts + during
            weibos = []

            query_dict = {
                'timestamp': {'$gt': begin_ts, '$lt': end_ts},
            }

            for k, v in mtype_kv.iteritems():
                ccount={}
                first_timestamp = end_ts
                first_item = {}
                query_dict['message_type'] = v
                count,weibo_results = xapian_search_weibo.search(query=query_dict, fields=fields_list)# weibo_results是在指定时间段、topic、message_type的微博匹配集
                for weibo_result in weibo_results():
                    if (weibo_result['timestamp'] <= first_timestamp ):
                        first_timestamp = weibo_result['timestamp']
                        first_item = weibo_result
                    try:
                        if (len(weibo_result['geo'].split('.')) == 4):
                            city = IP2city(weibo_result['geo'])
                            if city:
                                try:
                                    ccount[city] += 1   
                                except KeyError:
                                    ccount[city] = 1    
                            else:
                                continue
                        else:
                            city = geo2city(weibo_result['geo'])
                            if city:
                                try:
                                    ccount[city] += 1   
                                except KeyError:
                                    ccount[city] = 1    
                            else:
                                continue
                    except:
                        continue

                    if (v == 1) or (v == 3): # 只存储原创和转发
                        weibos.append(weibo_result)

                mtype_ccount[v] = [end_ts, ccount]
            save_rt_results(topic, mtype_ccount, during, first_item)

            sorted_weibos = sorted(weibos, key=lambda k: k[SORT_FIELD], reverse=True)
            sorted_weibos = sorted_weibos[:n_limit]
            save_ws_results(topic, end_ts, during, n_limit, sorted_weibos)

if __name__ == '__main__':
    START_TS = datetime2ts('2014-10-31')
    END_TS = datetime2ts('2014-11-15')

    topic = u'全军政治工作会议'
    topic_id = getTopicByName(topic)['_id']
    print topic_id, START_TS, END_TS
    xapian_search_weibo = getXapianWeiboByTopic(topic_id)
    print 'topic: ', topic.encode('utf8')
    cityCronTopic(topic, xapian_search_weibo, start_ts=START_TS, over_ts=END_TS, during=Fifteenminutes)
    """
    item_exist = db.session.query(CityWeibos).filter(CityWeibos.topic==topic).all()
    if item_exist:
        for item in item_exist:
            db.session.delete(item)
    db.session.commit()
    """

