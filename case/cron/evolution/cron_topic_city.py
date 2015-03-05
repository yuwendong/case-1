# -*- coding: utf-8 -*-

import sys
import IP   #引入IP，对'geo'字段进行解析
import json
import datetime
from topics import _all_topics

from time_utils import datetime2ts, ts2HourlyTime
from global_utils import getTopicByName
from dynamic_xapian_weibo import getXapianWeiboByTopic
from config import mtype_kv, db
from model import CityTopicCount


Minute = 60
Fifteenminutes = 15 * 60
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24


RESP_ITER_KEYS = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'bmiddle_pic', 'geo', 'comments_count', 'sentiment', 'terms']
fields_list=['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', 'comments_count', 'sentiment', 'topics', 'message_type', 'terms']


def geo2city(geo): #将weibo中的'geo'字段解析为地址
    try:
        province, city = geo.split()
        if province in [u'内蒙古自治区', u'黑龙江省']:
            province = province[:3]
        else:
            province = province[:2]

        city = city.strip(u'市').strip(u'区')

        geo = province + ' ' + city
    except:
        pass

    if isinstance(geo, unicode):
        geo = geo.encode('utf-8')

    if geo.split()[0] not in ['海外', '其他']:
        geo = '中国 ' + geo

    geo = '\t'.join(geo.split())

    return geo
    """
    try:
        city=IP.find(str(geo))
        #print city
        if city:
            city=city.encode('utf-8')
        else:
            return None
    except Exception,e:
        print e
        return None

    return city
    """


def save_rt_results(topic, mtype, results, during, first_item):
    ts, ccount = results
    item = CityTopicCount(topic, during, ts, mtype, json.dumps(ccount), json.dumps(first_item))
    item_exist = db.session.query(CityTopicCount).filter(CityTopicCount.topic==topic, \
                                                                        CityTopicCount.range==during, \
                                                                        CityTopicCount.end==ts, \
                                                                        CityTopicCount.mtype==mtype).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()


def cityCronTopic(topic, xapian_search_weibo, start_ts, over_ts, during=Fifteenminutes):
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

                    if geo2city(weibo_result['geo']):
                        try:
                            ccount[geo2city(weibo_result['geo'])] += 1   
                        except KeyError:
                            ccount[geo2city(weibo_result['geo'])] = 1    
                    else:
                        continue
                mtype_ccount[v] = [end_ts, ccount]

                save_rt_results(topic,v, mtype_ccount[v], during, first_item)


if __name__ == '__main__':
    # START_TS = datetime2ts('2013-09-02')
    START_TS = datetime2ts('2015-01-23')
    # END_TS = datetime2ts('2013-09-08')
    END_TS = datetime2ts('2015-02-03')

    topic = u'张灵甫遗骨疑似被埋羊圈' # u'东盟,博览会'
    # topic_id = getTopicByName(topic)['_id']
    topic_id = '54cf5ad9e8d7ce533b1160ec'   #'54ccbfab5a220134d9fc1b37'# 54cc9616a41513bb4fa6e262

    xapian_search_weibo = getXapianWeiboByTopic(topic_id)
    print 'topic: ', topic.encode('utf8')
    cityCronTopic(topic, xapian_search_weibo, start_ts=START_TS, over_ts=END_TS, during=Fifteenminutes)

