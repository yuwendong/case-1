# -*- coding:utf-8 -*-

import os
import time
import datetime
import IP
from config import db
from model import CityRepost
from dynamic_xapian_weibo import getXapianWeiboByDate

RESP_ITER_KEYS = ['_id', 'retweeted_mid', 'timestamp', 'geo', 'message_type']
SORT_FIELD = '-timestamp'

SECOND = 1
TENSECONDS = 10 * SECOND
MINUTE = 60
FIFTEENMINUTES = 15 * MINUTE
HOUR = 3600
SIXHOURS = 6 * HOUR
DAY = 24 * HOUR


s = getXapianWeiboByDate('20130919')
l = getXapianWeiboByDuration(['20130919', '20130920'])

BEGIN_TS = time.mktime(datetime.datetime(2013, 9, 19, 16, 0, 0).timetuple())
END_TS = time.mktime(datetime.datetime(2013, 9, 19, 16, 1, 0).timetuple())


def repost_search(topic, begin_ts = BEGIN_TS, end_ts = END_TS):
    if topic and topic != '':
        topic = topic.strip()
        query_dict = {
                'timestamp':{'$gt':begin_ts, '$lt':end_ts},
                'topics':topic
                }

        count,results = s.search(query = query_dict, sort_by = [SORT_FIELD], fields = RESP_ITER_KEYS)

        for r in results():
            results_gen(r)


def geo2city(geo):
    try:
        city = IP.find(str(geo))
        if city:
            city = city.encode('utf-8')
        else:
            return None
    except Exception, e:
        print e
        return None

    return city

def check_location(locations):


def save_rt_results():


def results_gen(r):
    # {message_type:xx, mid:xx, topic:xx, ts:xx, origin_location:xx, repost_location:xx}
    message_type = r['message_type']
        if message_type != 1: # 转发或评论
            print 'retweeted_mid', r['retweeted_mid']
            repost_location = geo2city(r['geo'])
            item = l.search_by_id(r['retweeted_mid'], fields = ['geo','_id'])
                if item:
                    origin_location = geo2city(item['geo'])
                    if check_location([origin_location, repost_location]):
                        save_rt_results()
                    else:
                        pass
                else:
                    pass





if __name__ == '__main__':
    topic = u'中国'
#    repost_search(topic)

    item = s.search_by_id('3617746241890522', fields = ['geo','_id'])
    if item:
        print 'exits', item['_id'], item['geo']
    else:
        print 'nothing'

