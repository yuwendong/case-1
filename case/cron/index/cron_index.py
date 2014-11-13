#-*- coding:utf-8 -*

import sys
import time
import datetime
import IP
import json
import redis
from model import IndexTopic
sys.path.append('../')
from time_utils import ts2datetime_full
from xapian_case.xapian_backend import XapianSearch
from xapian_case.utils import top_keywords, gen_mset_iter
from config import xapian_search_user as user_search
from consts import INDEX_PATH, db


PATH = INDEX_PATH
RESP_ITER_KEYS = ['_id','user','text','timestamp','geo','terms','reposts_count','source','comments_count']
SORT_FIELD='-timestamp'
TOP_CITY = 10
K_LIMIT = 10
O_LIMIT = 100
M_LIMIT = 10

SECOND = 1
TENSECONDS = 10 * SECOND
MINUTE = 60
FIFTEENMINUTES = 15 * MINUTE
HOUR = 3600
SIXHOURS = 6 * HOUR
DAY = 24 * HOUR
INTERVAL = TENSECONDS

REDIS_HOST = '219.224.135.48'
REDIS_PORT = 6379
USER_DOMAIN = 'user_domain' # user domain hash

BEGIN_TS = time.mktime(datetime.datetime(2013, 9, 1, 0, 0, 0).timetuple())
END_TS = time.mktime(datetime.datetime(2013, 9, 1, 0, 1, 0).timetuple())


s = XapianSearch(stub = PATH, schema_version = '5')

def _default_redis(host = REDIS_HOST, port = REDIS_PORT, db = 0):
    return redis.StrictRedis(host, port, db)
r = _default_redis()


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

            sublist_by_time.append((r['timestamp'],r['reposts_count'],r['user'],r['source'],r['text'],r['comments_count'],r['geo'])) # 部分字段构成子列表

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

        final_list_by_time = select_by_time(sublist_by_time,O_LIMIT)
        final_list_by_media =select_by_media(sublist_by_time, M_LIMIT)
        print 'final_list_by_media'
        for item in final_list_by_media:
            print 'timestamp', ts2datetime_full(item['timestamp'])
            print 'reposts_count',item['reposts_count']
            print 'user',item['user']
            print 'domain',uid2domain(item['user'])
            print 'source',item['source']
            print 'text',item['text']
            print 'comments_count', item['comments_count']
            print 'geo', item['geo']
            print 'username', item['username']
            print 'profile_image_url', item['profile_image_url']

        print 'final_list_by_time'
        for item in final_list_by_time:
            print 'timestamp', ts2datetime_full(item['timestamp'])
            print 'reposts_count',item['reposts_count']
            print 'user',item['user']
            print 'source',item['source']
            print 'text',item['text']
            print 'comments_count', item['comments_count']
            print 'geo', item['geo']
            print 'username', item['username']
            print 'profile_image_url', item['profile_image_url']

        top_city_list = top_city(city_dict)
        '''
        for city in top_city_list:
            print 'top_city_list',city
        '''

        top_keywords_list = top_keywords(results2, top = K_LIMIT)
        '''
        print 'top_keywords'
        for keyword in top_keywords_list:
            print 'keyword',keyword[0].decode('utf-8').encode('utf-8'),keyword[1]
        '''
        save_rt_results(topic, count, user_count, time_list,\
                top_city_list, top_keywords_list, final_list_by_time, final_list_by_media)



def save_rt_results(topic, count, user_count, time_list, top_city_list, top_keywords_list, final_list_by_time, final_list_by_media):
    area = top_city_list

    # 关键词列表转化成字典
    key_words_dict = {}
    for keyword in top_keywords_list:
        key_words_dict[keyword[0]] = keyword[1]

    opinion = final_list_by_time
    media_opinion = final_list_by_media

    item = IndexTopic(topic, count, user_count, time_list[0], time_list[-1],\
            json.dumps(area), json.dumps(key_words_dict), json.dumps(opinion), json.dumps(media_opinion))

    item_exist = db.session.query(IndexTopic).filter(IndexTopic.topic == topic).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

    print 'commited'


def getuserinfo(uid):
    user = acquire_user_by_id(uid)
    if not user:
        username = 'Unknown'
        profileimage = ''
    else:
        username = user['name']
        profileimage = user['image']
    return username, profileimage

def acquire_user_by_id(uid):
    user_result = user_search.search_by_id(uid, fields=['name', 'profile_image_url'])
    user = {}
    if user_result:
        user['name'] = user_result['name']
        user['image'] = user_result['profile_image_url']

    return user



def uid2domain(user): # 将用户转化为对应的领域
    # DOMAIN_V3_LIST = ['folks','media','opinion_leader','oversea','other']
    # DOMAIN_V3_ZH_LIST = [u'民众', u'媒体', u'意见领袖', u'境外', u'其他']

    domain_str = r.hget(USER_DOMAIN, str(user))
    if not domain_str:
        return 'other'

    domain_dict = json.loads(domain_str)
    domain = domain_dict['v3']

    return domain

def is_media(user):
    domain = uid2domain(user)
    if domain == 'media':
        return True
    else:
        return False

def select_by_media(sublist_by_time, limit): # 媒体代表性观点

    media_opinion_list = filter(lambda x:is_media(x[2]), sublist_by_time)

    m = len(media_opinion_list) % limit
    if m:
        count = len(media_opinion_list) / limit + 1
    else:
        count = len(media_opinion_list) / limit
    final_list_by_media = []

    for t in range(count):
        a = limit * t
        b = limit * (t + 1)
        if b >= len(media_opinion_list):
            list1 = media_opinion_list[a:]
        else:
            list1 = media_opinion_list[a:b]
        list2 = sorted(list1, key = lambda d:d[1], reverse = True)

        username,profileimage = getuserinfo(list2[0][2])
        # 元组转化为字典
        final_dict = {}
        final_dict['timestamp'] = list2[0][0]
        final_dict['reposts_count'] = list2[0][1]
        final_dict['user'] = list2[0][2]
        final_dict['source'] = list2[0][3]
        final_dict['text'] = list2[0][4]
        final_dict['comments_count'] = list2[0][5]
        final_dict['geo'] = list2[0][6]
        final_dict['username'] = username
        final_dict['profile_image_url'] = profileimage

        final_list_by_media.append(final_dict)

    return final_list_by_media


def select_by_time(sublist_by_time, limit): # 挑选代表微博

    m = len(sublist_by_time) % limit
    if m:
        count = len(sublist_by_time) / limit + 1
    else:
        count = len(sublist_by_time) / limit

    final_list_by_time = []

    for t in range(limit):
        a = count * t
        b = count * (t + 1)
        if b >= len(sublist_by_time):
            list1 = sublist_by_time[a:]
        else:
            list1 = sublist_by_time[a:b]
        list2 = sorted(list1, key = lambda d:d[1], reverse = True)

        username, profileimage = getuserinfo(list2[0][2])
        # 元组转化为字典
        final_dict = {}
        final_dict['timestamp'] = list2[0][0]
        final_dict['reposts_count'] = list2[0][1]
        final_dict['user'] = list2[0][2]
        final_dict['source'] = list2[0][3]
        final_dict['text'] = list2[0][4]
        final_dict['comments_count'] = list2[0][5]
        final_dict['geo'] = list2[0][6]
        final_dict['username'] = username
        final_dict['profile_image_url'] = profileimage

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

