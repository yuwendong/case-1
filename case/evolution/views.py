#-*- coding:utf-8 -*-

import os
import IP
import json
import time
import pymongo
from city_count import Pcount
from BeautifulSoup import BeautifulSoup
from case.extensions import db
from case.model import CityRepost
# 根据count不同，给不同的城市不同的颜色
from city_color import province_color_map
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
from city_map import partition_time, partition_count, map_circle_data, map_line_data, \
        statistics_data, work_in_out, select_groups

from case.dynamic_xapian_weibo import getXapianWeiboByTopic # 问题，待修改----应该在cron中完成
from xapian_case.xapian_backend import XapianSearch
from utils import weiboinfo2url

mod = Blueprint('evolution', __name__, url_prefix='/evolution')

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


def ts2date(ts):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))


def get_city_weibo(query, start_ts, end_ts):
    topic = query
    weibos = []
    query_dict = {
        '$or': [{'message_type': 1}, {'message_type': 3}],
        'timestamp':{'$gt': start_ts, '$lt': end_ts}
    }
    search_city_weibo = getXapianWeiboByTopic()
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
        city = geo2city(result['geo']).split('\t')[1]
        result['weibo_link'] = weiboinfo2url(result['user'], result['_id'])
        #print 'city:', city

        if city in province_list:
            try:
                city_dict[city].append(result)
            except:
                city_dict[city] = [result]
    return city_dict


def topSelect(total_count):
    total_count_list_reverse = []
    total_count_list_reverse = sorted(total_count.iteritems(), key = lambda (k, v):v, reverse = True)
    return total_count_list_reverse

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

def readPropagateSpatialAcum(stylenum, topic, start_ts, end_ts, during):
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

@mod.route('/city_map_view/')
def city_map_view():
    topic = request.args.get('topic', '')
    during = request.args.get('pointInterval', 60 * 60) # 默认查询时间粒度为3600秒
    during = int(during)
    end_ts = request.args.get('end_ts', '')
    end_ts = long(end_ts)
    start_ts = request.args.get('start_ts', '')
    start_ts = long(start_ts)
    ts_arr = []
    results = []

    top_city_weibo = get_city_weibo(topic, start_ts, end_ts)
    # top_city_weibo = {city:[weibo1,weibo2...],...}

    items = db.session.query(CityRepost).filter(CityRepost.topic == topic).all()
    if items:
        for item in items:
            r = {}
            r['original'] = item.original
            r['topic'] = item.topic
            r['mid'] = item.mid
            r['ts'] = item.ts
            r['origin_location'] = item.origin_location
            r['repost_location'] = item.repost_location

            ts_arr.append(r['ts'])
            ts_arr = sorted(list(set(ts_arr)))
            results.append(r)
        raw_ts_series, raw_groups = partition_time(ts_arr, results, during)
        ts_series, groups = select_groups(raw_ts_series, raw_groups, start_ts, end_ts)
        # draw_circle_data = map_circle_data(groups, True)
        max_repost_num, draw_line_data = map_line_data(groups, True)
        in_out_results = work_in_out(draw_line_data)
        repost_series, origin_series, post_series, statistic_data = statistics_data(groups, draw_line_data, True)
        return json.dumps({'draw_line_data': draw_line_data, 'in_out_results': in_out_results,'statistics_data': statistic_data, 'top_city_weibo': top_city_weibo})

        '''
        return json.dumps({'ts_arr':ts_arr, 'results':results, 'ts_series':ts_series, 'groups': groups, \
                'draw_circle_data':draw_circle_data, 'draw_line_data': draw_line_data, 'max_repost_num': max_repost_num, \
                'repost_series':repost_series, 'origin_series':origin_series, 'post_series':post_series, 'statistics_data':statistic_data})
        '''
    else:
        print 'no results'


@mod.route("/topic_ajax_spatial/")
def ajax_spatial():
    """
    地域演化的页面,从database获取数据返回topic_spatial.html
    """

    stylenum = request.args.get('style', '') # stylenum表示返回count是origin：1,forward：2,comment：3,sum：4
    stylenum = int(stylenum)
    topic = request.args.get('topic', '')
    during = request.args.get('pointInterval', 60 * 60) # 默认查询时间粒度为3600秒
    during = int(during)
    end_ts = request.args.get('end_ts', '')
    end_ts = long(end_ts)
    start_ts = request.args.get('start_ts', '')
    start_ts = long(start_ts)
    incremental = request.args.get('incremental', 0)
    incremental = int(incremental)
    pointnum = (end_ts - start_ts) / during # 时间点数

    top_city_weibo = get_city_weibo(topic, start_ts, end_ts)
    # top_city_weibo = {city:[weibo1,weibo2...],...}

    spatial_dict = {}
    global_max_count = 0
    if incremental == 0:
        global_first_timestamp = end_ts
        global_first_city = ""
        for i in range(pointnum + 1): # 增长量
            end_ts = start_ts +  during * i
            max_count, topic_spatial_info, first_item = readPropagateSpatial(stylenum, topic, end_ts , during)  # 查询在一定时间范围内，某个topic的stylenum信息各个省市的数量

            if global_max_count < max_count:
                global_max_count = max_count
            try:
                if first_item['timestamp'] <= global_first_timestamp:
                    global_first_timestamp = first_item['timestamp']
                    global_first_city = geo2city(first_item['geo'])
            except KeyError:
                pass
            spatial_dict[str(end_ts)] = topic_spatial_info # spatial_dict = {end_ts:map_data}

    elif incremental == 1: # 累计量
        global_max_count, spatial_dict, global_first_city = readPropagateSpatialAcum(stylenum, topic, start_ts, end_ts , during)  # 查询在一定时间范围内，某个topic的stylenum信息各个省市的数量

    map_data = info2map(spatial_dict, incremental)
    map_data['max_count'] = global_max_count
    map_data['first_city'] = global_first_city
    map_data['top_city_weibo'] = top_city_weibo

    return json.dumps(map_data)



@mod.route('/in_out_map/')
def in_out_map():
    topic = request.args.get('topic', '')
    during = request.args.get('pointInterval', 60 * 60) # 默认查询时间粒度为3600秒
    during = int(during)
    end_ts = request.args.get('end_ts', '')
    end_ts = long(end_ts)
    start_ts = request.args.get('start_ts', '')
    start_ts = long(start_ts)
    ts_arr = []
    results = []

    top_city_weibo = get_city_weibo(topic, start_ts, end_ts)
    # top_city_weibo = {city:[weibo1,weibo2...],...}

    items = db.session.query(CityRepost).filter(CityRepost.topic == topic).all()
    if items:
        for item in items:
            r = {}
            r['original'] = item.original
            r['topic'] = item.topic
            r['mid'] = item.mid
            r['ts'] = item.ts
            r['origin_location'] = item.origin_location
            r['repost_location'] = item.repost_location

            ts_arr.append(r['ts'])
            ts_arr = sorted(list(set(ts_arr)))
            results.append(r)
        raw_ts_series, raw_groups = partition_time(ts_arr, results, during)
        ts_series, groups = select_groups(raw_ts_series, raw_groups, start_ts, end_ts)
        # draw_circle_data = map_circle_data(groups, True)
        max_repost_num, draw_line_data = map_line_data(groups, True)
        in_out_results = work_in_out(draw_line_data)
        repost_series, origin_series, post_series, statistic_data = statistics_data(groups, draw_line_data, True)
        return json.dumps({'draw_line_data': draw_line_data, 'in_out_results': in_out_results, 'statistics_data': statistic_data, 'top_city_weibo': top_city_weibo})

        '''
        return json.dumps({'ts_arr':ts_arr, 'results':results, 'ts_series':ts_series, 'groups': groups, \
                'draw_circle_data':draw_circle_data, 'draw_line_data': draw_line_data, 'max_repost_num': max_repost_num, \
                'repost_series':repost_series, 'origin_series':origin_series, 'post_series':post_series, 'statistics_data':statistic_data})
        '''
    else:
        print 'no results'
