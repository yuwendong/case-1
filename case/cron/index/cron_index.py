#-*- coding:utf-8 -*

import time
import datetime
import IP
import json
from model import IndexTopic
from time_utils import ts2datetime_full
from xapian_case.xapian_backend import XapianSearch
from xapian_case.utils import top_keywords, gen_mset_iter
from consts import INDEX_PATH, db


PATH = INDEX_PATH
RESP_ITER_KEYS = ['_id','user','text','timestamp','geo','terms','reposts_count','source']
SORT_FIELD='-timestamp'
TOP_CITY = 10
K_LIMIT = 10

SECOND = 1
TENSECONDS = 10 * SECOND
MINUTE = 60
FIFTEENMINUTES = 15 * MINUTE
HOUR = 3600
SIXHOURS = 6 * HOUR
DAY = 24 * HOUR
INTERVAL = TENSECONDS

BEGIN_TS = time.mktime(datetime.datetime(2013, 9, 1, 0, 0, 0).timetuple())
END_TS = time.mktime(datetime.datetime(2013, 9, 1, 0, 1, 0).timetuple())


s = XapianSearch(stub = PATH, schema_version = '5')


def cron_index_topic(topic, begin_ts = BEGIN_TS, end_ts = END_TS):
    if topic and topic != '':
        topic = topic.strip()
        query_dict = {
                'timestamp':{'$gt':begin_ts,'$lt':end_ts},
                'topics':topic
                }

        count,results = s.search(query=query_dict, sort_by=[SORT_FIELD], fields=RESP_ITER_KEYS)
        count2,results2 = s.search(query=query_dict, sort_by=[SORT_FIELD], fields=RESP_ITER_KEYS)
        user_raw_list = []
        time_list = []
        sublist_by_time=[]
        city_dict = {}


        # 测试city_dict是否可用
        # city = geo2city('219.224.135.46')
        # print city,city_dict.setdefault(city,0)
        # city_dict[city] += 1
        # print 'city_dict[city]',city_dict[city]
        print 'count',count

        for r in results():
            user_raw_list.append(r['user']) # 原始用户列表

            time_list.append(r['timestamp']) # 时间列表

            sublist_by_time.append((r['timestamp'],r['reposts_count'],r['user'],r['source'],r['text'])) # 部分字段构成子列表

            city = geo2city(r['geo'])
            # print city
            city_dict.setdefault(city,0)
            city_dict[city] += 1 # 字典相应键值加1
            # print 'city_dict[city]',city_dict[city]
            # print '_id',r['_id']
            # print 'user',r['user']
            # print 'timestamp',ts2datetime_full(r['timestamp'])
            # print 'reposts_count',r['reposts_count']

        user_count = len(list(set(user_raw_list))) # 去重后的参与人数
        print 'user_count',user_count

        topic_begin_ts = ts2datetime_full(time_list[0])
        topic_end_ts = ts2datetime_full(time_list[-1])
        print 'topic_begin_ts',topic_begin_ts
        print 'topic_end_ts',topic_end_ts

        final_list_by_time = select_by_time(sublist_by_time,time_list[0],time_list[-1],INTERVAL)
        print 'final_list_by_time'
        for item in final_list_by_time:
            print 'timestamp', ts2datetime_full(item['timestamp'])
            print 'reposts_count',item['reposts_count']
            print 'user',item['user']
            print 'source',item['source']
            print 'text',item['text']

        top_city_list = top_city(city_dict)
        for city in top_city_list:
            print 'top_city_list',city

        print 'top_keywords'
        top_keywords_list = top_keywords(results2, top = K_LIMIT)
        for keyword in top_keywords_list:
            print 'keyword',keyword[0].decode('utf-8').encode('utf-8'),keyword[1]

        save_rt_results(topic, count, user_count, time_list,\
                top_city_list, top_keywords_list, final_list_by_time)



def save_rt_results(topic, count, user_count, time_list, top_city_list, top_keywords_list, final_list_by_time):
    area = top_city_list

    # 关键词列表转化成字典
    key_words_dict = {}
    for keyword in top_keywords_list:
        key_words_dict[keyword[0]] = keyword[1]

    opinion = final_list_by_time

    item = IndexTopic(topic, count, user_count, time_list[0], time_list[-1],\
            json.dumps(area), json.dumps(key_words_dict), json.dumps(opinion))

    item_exist = db.session.query(IndexTopic).filter(IndexTopic.topic == topic).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

    print 'commited'


def select_by_time(sublist_by_time, begin_ts, end_ts,during): # 挑选各时间段的代表微博
    m = (end_ts - begin_ts) % during
    if m:
        time_count = (end_ts - begin_ts) / during + 1
    else:
        time_count = (end_ts - begin_ts) / during
    final_list_by_time = []

    for t in range(time_count):
        ts1 = begin_ts + during * t
        ts2 = min(ts1 + during, end_ts)
        list1 = [(timestamp,reposts_count,user,source,text) for timestamp,reposts_count,user,source,text in sublist_by_time if ts1 < timestamp <= ts2]
        list2 = sorted(list1, key = lambda d:d[1], reverse = True) # 按转发量排序

        # 元组转化为字典
        final_dict = {}
        final_dict['timestamp'] = list2[0][0]
        final_dict['reposts_count'] = list2[0][1]
        final_dict['user'] = list2[0][2]
        final_dict['source'] = list2[0][3]
        final_dict['text'] = list2[0][4]

        final_list_by_time.append(final_dict)

    return final_list_by_time


def top_city(city_dict): # 返回出现次数最多的城市
    sorted_city_list = sorted(city_dict.iteritems(), key = lambda d:d[1])
    top_city_list = [city for city, count in sorted_city_list[len(sorted_city_list)-TOP_CITY:]]

    return top_city_list


def geo2city(geo): # 将geo字段解析为地址
    try:
        city = IP.find(str(geo))
        #print city
        if city:
            city = city.encode('utf-8')
        else:
            return None
    except Exception,e:
        print e
        return None

    return city


if __name__ == '__main__':
    topic = u'中国'
    cron_index_topic(topic)
    # print geo2city('219.224.135.46')

