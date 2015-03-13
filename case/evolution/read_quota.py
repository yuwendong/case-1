#-*- coding: utf-8 -*-
import IP
import time
import json
import math
from xapian_case.xapian_backend import XapianSearch

from case.extensions import db
from case.model import CityWeibos
from city_count import Pcount
# 根据count不同，给不同的城市不同的颜色
from city_color import province_color_map
from utils import weiboinfo2url

#mtype_kv={'original': 1, 'forward': 2, 'comment': 3,'sum':4}

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes

SORT_FIELD = ['reposts_count']

RESP_ITER_KEYS = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', \
'bmiddle_pic', 'geo', 'comments_count', 'sentiment']
TOP_WEIBOS_LIMIT = 50

province_list = [u'安徽', u'北京', u'重庆', u'福建', u'甘肃', u'广东', u'广西', u'贵州', u'海南', \
                 u'河北', u'黑龙江', u'河南', u'湖北', u'湖南', u'内蒙古', u'江苏', u'江西', u'吉林', \
                 u'辽宁', u'宁夏', u'青海', u'山西', u'山东', u'上海', u'四川', u'天津', u'西藏', u'新疆', \
                 u'云南', u'浙江', u'陕西', u'台湾', u'香港', u'澳门']

def _json_loads(weibos):
    try:
        return json.loads(weibos)
    except ValueError:
        if isinstance(weibos, unicode):
            return json.loads(json.dumps(weibos))
        else:
            return None

def acquire_user_by_id(uid):
    XAPIAN_USER_DATA_PATH = '/home/xapian/xapian_user/'
    user_search = XapianSearch(path=XAPIAN_USER_DATA_PATH, name='master_timeline_user', schema_version=1)
    result = user_search.search_by_id(int(uid), fields=['name', 'location', 'followers_count', 'friends_count'])
    user = {}
    if result:
        user['name'] = result['name']
        user['location'] = result['location']
        user['count1'] = result['followers_count']
        user['count2'] = result['friends_count']
    
    return user

def ts2date(ts):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))

def topSelect(total_count):
    total_count_list_reverse = []
    total_count_list_reverse = sorted(total_count.iteritems(), key = lambda (k, v):v, reverse = True)
    return total_count_list_reverse

def info2map(infos, incremental = 0): # infos = {end_ts:map_data}, map_data={'count':{}, 'color':{}, 'summary':{}}
    count = {}
    rank = {}
    ratio = {}
    top10 = {}
    total_count = {}

    for info in infos:
        map_dict = infos[info]
        count[info] = [0] * 34
        rank[info] = [0] * 34
        ratio[info] = [0] *34
        for p in range(34):
            try:
                pcount = map_dict['count'][province_list[p]][0]
                prank = map_dict['count'][province_list[p]][1]
                pratio = map_dict['count'][province_list[p]][2]
            except:
                continue
            count[info][p] = pcount
            rank[info][p] = prank
            ratio[info][p] = pratio

            if incremental == 0:
                try:
                    total_count[province_list[p]] += pcount
                except:
                    total_count[province_list[p]] = pcount  # total_count = {city:count}
            elif incremental == 1:
                try:
                    total_count[province_list[p]]
                except KeyError:
                    total_count[province_list[p]] = 0
                if total_count[province_list[p]] < pcount:
                    total_count[province_list[p]] = pcount

        top10[info] = map_dict['summary']

    total_count_list_reverse = []
    total_count_list_reverse = topSelect(total_count) # 整体所有数据的排序
    # print 'total_count_list_reverse:', total_count_list_reverse

    province_data = {}
    for p in province_list:
        province_data[p] = []

    ts_list = []
    sorted_count_by_ts = sorted(count.iteritems(), key=lambda (k, v) : k, reverse=False)
    for ts, pdata in sorted_count_by_ts:
        ts_list.append(ts)
        for idx, d in enumerate(pdata):
            province_data[province_list[idx]].append(d)


    data = {'count':count, 'rank':rank, 'ratio':ratio, 'top10':top10, 'province_data': province_data, 'ts_list': ts_list, \
            'total_count': total_count_list_reverse}

    return data

def geo2city(geo):
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
        city = IP.find(str(geo))
        if city:
            city = city.encode('utf-8')
        else:
            return None
    except Exception, e:
        print e
        return None
    return city
    """

def get_city_weibo(topic, start_ts, end_ts, unit=MinInterval, limit=TOP_WEIBOS_LIMIT):
    weibos = []
    if (end_ts - start_ts < unit):
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        item = db.session.query(CityWeibos).filter(CityWeibos.end==upbound, \
                                                       CityWeibos.topic==topic, \
                                                       CityWeibos.range==unit, \
                                                       CityWeibos.limit==limit).first()
        if item:
            news = _json_loads(item.weibos)
            for weibo_item in news:
                weibos.append((weibo_item['reposts_count'],weibo_item))
    else:
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        items = db.session.query(CityWeibos).filter(CityWeibos.end>lowbound, \
                                                         CityWeibos.end<=upbound, \
                                                         CityWeibos.topic==topic, \
                                                         CityWeibos.range==unit, \
                                                         CityWeibos.limit==limit).all()
        for item in items:
            news = _json_loads(item.weibos)
            for weibo_item in news:
                try:
                    weibos.append((weibo_item['reposts_count'],weibo_item))
                except:
                    continue
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
    return city_dict

def readPropagateSpatial(stylenum, topic, end_ts , during):
    """将从数据库中读取的数据转化为map_data
    """
    max_count = 0
    city_count = {}
    first_item = {}
    first_item, city_count = Pcount(end_ts, during, stylenum, topic) # PCount从db中计算各个省市地区的总数
    if city_count.values():
        max_count = max(city_count.values())
    map_data = province_color_map(city_count)
    return max_count, map_data, first_item

def readAcum(stylenum, topic, start_ts, end_ts, during):
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
        first_item, city_count = Pcount(end_ts, during, stylenum, topic)


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
                global_first_city = geo2city(first_item['geo'])
        except KeyError:
            pass
    return global_max_count, spatial_dict, global_first_city
