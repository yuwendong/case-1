# -*- coding:utf-8 -*-

import os
import types
import time
import datetime
import IP
from config import db
from model import CityRepost
from dynamic_xapian_weibo import getXapianWeiboByDate, getXapianWeiboByDuration, getXapianWeiboByTopic

RESP_ITER_KEYS = ['_id', 'retweeted_mid', 'timestamp', 'geo', 'message_type']
SORT_FIELD = '-timestamp'

SECOND = 1
TENSECONDS = 10 * SECOND
MINUTE = 60
FIFTEENMINUTES = 15 * MINUTE
HOUR = 3600
SIXHOURS = 6 * HOUR
DAY = 24 * HOUR


s = getXapianWeiboByTopic(u'东盟,博览会')
l = getXapianWeiboByTopic(u'东盟,博览会')

BEGIN_TS = time.mktime(datetime.datetime(2013, 9, 1, 16, 0, 0).timetuple())
END_TS = time.mktime(datetime.datetime(2013, 9, 1, 16, 1, 0).timetuple())


def repost_search(topic):
    repost_list = []
    ts_arr = []
    if topic and topic != '':
        topics = topic.strip().split(',')

        query_dict = {
                # 'timestamp':{'$gt':BEGIN_TS, '$lt':END_TS},
                '$or': [],
                }
        for topic_a in topics:
            query_dict['$or'].append({'topics': topic_a})

        count,results = s.search(query = query_dict, sort_by = [SORT_FIELD], fields = RESP_ITER_KEYS)
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
        repost_location = geo2city(r['geo'])
        if r['retweeted_mid']: # 过滤retweed_mid不完整的item
            item = l.search_by_id(r['retweeted_mid'], fields = ['geo','_id'])
            if item:
                origin_location = geo2city(item['geo'])
                if check_location([origin_location, repost_location]):
                    location_dict['original'] = 0
                    location_dict['mid'] = r['_id']
                    location_dict['topic'] = topic
                    location_dict['ts'] = r['timestamp']
                    location_dict['origin_location'] = origin_location.split('\t')[1]
                    location_dict['repost_location'] = repost_location.split('\t')[1]
                    return location_dict

    elif message_type == 1: # 原创
        origin_location = geo2city(r['geo'])
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
    topic = u'东盟,博览会'
    repost_search(topic)
