# -*- coding:utf-8 -*-

import os
import types
import time
import datetime
import IP
from config import db
from utils import geo2city, IP2city
from model import CityRepost
from global_utils import getTopicByName
from dynamic_xapian_weibo import getXapianWeiboByTopic

RESP_ITER_KEYS = ['_id', 'retweeted_mid', 'timestamp', 'geo', 'message_type']
SORT_FIELD = '-timestamp'

SECOND = 1
TENSECONDS = 10 * SECOND
MINUTE = 60
FIFTEENMINUTES = 15 * MINUTE
HOUR = 3600
SIXHOURS = 6 * HOUR
DAY = 24 * HOUR

def datetime2ts(date):
    return int(time.mktime(time.strptime(date, '%Y-%m-%d')))


def repost_search(topic, startts, endts):
    repost_list = []
    ts_arr = []
    if topic and topic != '':
        query_dict = {
            "timestamp": {
                "$gte": startts,
                "$lte": endts
            }
        }

        count,results = xapian_search.search(query=query_dict, sort_by=[SORT_FIELD], fields=RESP_ITER_KEYS)
        print 'count',count

        for r in results():
            location_dict = results_gen(r, topic)
            if location_dict:
                repost_list.append(location_dict)
                ts_arr.append(r['timestamp'])

        print len(repost_list)

        save_rt_results(topic, repost_list)

    return sorted(list(set(ts_arr))), repost_list


def save_rt_results(topic, repost_list):

    for location in repost_list:
        item = CityRepost(location['original'], topic, location['mid'], location['ts'],\
                        location['origin_location'], location['repost_location'])
        item_exist = db.session.query(CityRepost).filter(CityRepost.topic == topic, CityRepost.mid == location['mid']).first()

        if item_exist:
            db.session.delete(item_exist)
        db.session.add(item)

    db.session.commit()
    print 'commited'



def check_location(locations):
    for location in locations:
        if location == '':
            return False
        try:
            tokens = location.split('\t')
            if tokens[0] == u'中国'.encode('utf-8'):
                if len(tokens) == 1:
                    return False

                elif len(tokens) == 2:
                    province, district = tokens[1], None

                elif len(tokens) == 3:
                    province, district = tokens[1], tokens[2]
            else:
                return False
        except:
            return False
    return True


def results_gen(r, topic):
    # {original:xx, mid:xx, topic:xx, ts:xx, origin_location:xx, repost_location:xx}
    location_dict = {}
    message_type = r['message_type']
    if message_type == 3: # 转发
        # print 'retweeted_mid', r['retweeted_mid']
        try:
            if (len(r['geo'].split('.')) == 4):
                repost_location = IP2city(r['geo'])
            else:
                repost_location = geo2city(r['geo'])
        except:
            return None
        if check_location([repost_location]): # 过滤不能解析的item
            if r['retweeted_mid']: # 过滤retweed_mid不完整的item
                item = xapian_search.search_by_id(r['retweeted_mid'], fields = ['geo','_id'])
                if item:
                    try:
                        if (len(item['geo'].split('.')) == 4):
                            origin_location = IP2city(item['geo'])
                        else:
                            origin_location = geo2city(item['geo'])
                    except:
                        return None
                    if check_location([origin_location]):
                        location_dict['original'] = 0
                        location_dict['mid'] = r['_id']
                        location_dict['topic'] = topic
                        location_dict['ts'] = r['timestamp']
                        location_dict['origin_location'] = origin_location.split('\t')[1]
                        location_dict['repost_location'] = repost_location.split('\t')[1]
                        return location_dict

    elif message_type == 1: # 原创
        try:
            if (len(r['geo'].split('.')) == 4):
                origin_location = IP2city(r['geo'])
            else:
                origin_location = geo2city(r['geo'])
        except:
            return None
        if check_location([origin_location]):
            location_dict['original'] = 1
            location_dict['mid'] = r['_id']
            location_dict['topic'] = topic
            location_dict['ts'] = r['timestamp']
            location_dict['origin_location'] = origin_location.split('\t')[1]
            location_dict['repost_location'] = None
            return location_dict

    return None

if __name__ == '__main__':
    START_TS = datetime2ts('2015-03-02')
    END_TS = datetime2ts('2015-03-15')

    topic = u'两会2015'
    topic_id = getTopicByName(topic)['_id']
    print 'topic: ', topic.encode('utf8')
    print topic_id, START_TS, END_TS

    xapian_search = getXapianWeiboByTopic(topic_id)
    repost_search(topic, START_TS, END_TS)
    """
    item_exist = db.session.query(CityRepost).filter(CityRepost.topic == topic).all()

    if item_exist:
        for item in item_exist:
            db.session.delete(item)
    db.session.commit()
    print 'commited'
    """
