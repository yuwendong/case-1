#-*- coding: utf-8 -*-
import IP
import time
from xapian_case.xapian_backend import XapianSearch
from case.global_utils import getTopicByName
from case.dynamic_xapian_weibo import getXapianWeiboByTopic # 问题，待修改----应该在cron中完成

from city_count import Pcount, PcountNews
# 根据count不同，给不同的城市不同的颜色
from city_color import province_color_map
from utils import weiboinfo2url
from read_quota import geo2city, ts2date, acquire_user_by_id

#mtype_kv={'original': 1, 'forward': 2, 'comment': 3,'sum':4}

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes

DB_NAME = '54api_weibo_v2' 
TB_NAME = 'master_timeline_weibo' 

#mongoclient =  pymongo.MongoClient('219.224.135.46')
#mongodb = mongoclient[DB_NAME] 
#mongotable = mongodb[TB_NAME]

SORT_FIELD = ['reposts_count']

RESP_ITER_KEYS = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', \
'bmiddle_pic', 'geo', 'comments_count', 'sentiment']

province_list = [u'安徽', u'北京', u'重庆', u'福建', u'甘肃', u'广东', u'广西', u'贵州', u'海南', \
                 u'河北', u'黑龙江', u'河南', u'湖北', u'湖南', u'内蒙古', u'江苏', u'江西', u'吉林', \
                 u'辽宁', u'宁夏', u'青海', u'山西', u'山东', u'上海', u'四川', u'天津', u'西藏', u'新疆', \
                 u'云南', u'浙江', u'陕西', u'台湾', u'香港', u'澳门']


def get_city_news(query, start_ts, end_ts):
    """
    topic = query
    topicid = str(getTopicByName(topic)['_id'])
    weibos = []
    query_dict = {
        '$or': [{'message_type': 1}, {'message_type': 3}],
        'timestamp':{'$gt': start_ts, '$lt': end_ts}
    }
    search_city_weibo = getXapianWeiboByTopic(topicid)
    count, get_results = search_city_weibo.search(query=query_dict, fields=RESP_ITER_KEYS)
    for r in get_results():
        #weibo = mongotable.find_one({'_id': int(r['_id'])})
        weibo = None
        if weibo:
            r['reposts_count'] = int(weibo['reposts_count'])
            r['comments_count'] = int(weibo['comments_count'])

        weibos.append((r['reposts_count'], r))

    sorted_weibos = sorted(weibos, key=lambda k: k[0], reverse=True)

    city_dict = {}
    k = 0
    for reposts_count, result in sorted_weibos:
        k += 1
        if k > 1000:
            break

        uid = result['user']
        user_info = acquire_user_by_id(uid)
        if user_info:
            result['username'] = user_info['name']
        else:
            result['username'] = '未知'
        time = ts2date(result['timestamp'])
        result['time'] = time
        try:
            city = geo2city(result['geo']).split('\t')[1]
        except:
            city = ''
        result['weibo_link'] = weiboinfo2url(result['user'], result['_id'])
        #print 'city:', city

        if city in province_list:
            try:
                city_dict[city].append(result)
            except:
                city_dict[city] = [result]
    """
    city_dict = {}
    return city_dict

def readNews(stylenum, topic, end_ts , during):
    """将从数据库中读取的数据转化为map_data
    """
    max_count = 0
    city_count = {}
    first_item = {}
    first_item, city_count = PcountNews(end_ts, during, stylenum, topic) # PCount从db中计算各个省市地区的总数
    if city_count.values():
        max_count = max(city_count.values())
    map_data = province_color_map(city_count)
    return max_count, map_data, first_item

def readAcumNews(stylenum, topic, start_ts, end_ts, during):
    pointnum = (end_ts - start_ts) / during # 时间点数
    spatial_dict = {}
    spatial_info_list = []
    global_max_count = 0
    global_first_timestamp = end_ts
    global_first_city = ""

    for i in range(pointnum + 1):
        end_ts = start_ts +  during * i
        max_count = 0
        first_item = {}
        city_count = {}
        first_item, city_count = PcountNews(end_ts, during, stylenum, topic)


        for city in city_count:
            j = i
            while j > 0:
                previous_data = spatial_info_list[j-1]
                if city in previous_data:
                    city_count[city] += previous_data[city]
                    break
                else:
                    j -= 1
        if i > 0:
            previous_data = spatial_info_list[i-1]
            for city in previous_data:
                try:
                    city_count[city]
                except KeyError:
                    city_count[city] = previous_data[city]
                    continue

        if city_count.values():
            max_count = max(city_count.values())

        if global_max_count < max_count:
            global_max_count = max_count
        spatial_info_list.append(city_count)
        topic_spatial_info = province_color_map(city_count)
        spatial_dict[str(end_ts)] = topic_spatial_info # spatial_dict = {end_ts:map_data}
        try:
            if first_item['timestamp'] <= global_first_timestamp:
                global_first_timestamp = first_item['timestamp']
                global_first_city = ''
        except KeyError:
            pass
    return global_max_count, spatial_dict, global_first_city
