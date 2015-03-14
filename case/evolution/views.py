#-*- coding:utf-8 -*-

import os
import IP
import time
import json
import pymongo
from BeautifulSoup import BeautifulSoup
from case.extensions import db
from case.model import CityRepost, CityRepostNews
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect
from city_map import partition_time, partition_count, map_circle_data, map_line_data, \
        statistics_data, work_in_out, select_groups

from read_quota import get_city_weibo, readPropagateSpatial, \
        readAcum, geo2city, info2map
from read_quota_news import get_city_news, readNews,\
        readAcumNews

mod = Blueprint('evolution', __name__, url_prefix='/evolution')

Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes

#mtype_kv={'original': 1, 'forward': 2, 'comment': 3,'sum':4}

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
    print time.time(), topic.encode('utf-8'), during, end_ts, start_ts
    top_city_weibo = get_city_weibo(topic, start_ts, end_ts)
    # top_city_weibo = {city:[weibo1,weibo2...],...}
    print time.time(), 'get weibo done'
    items = db.session.query(CityRepost).filter(CityRepost.topic == topic).all()
    print time.time(), 'get repost done'
    """
    if (topic == u'张灵甫遗骨疑似被埋羊圈'):
        tempfile = open('zhanglingfu.txt', 'r')
        items = json.loads(tempfile.read())
        tempfile.close()
        print time.time(), 'read done'
    """

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
        if (topic == u'张灵甫遗骨疑似被埋羊圈'):
            tempfile = open('zhanglingfu.txt', 'w')
            tempfile.write(json.dumps(results))
            tempfile.close()
            print time.time(), 'write done'
        print time.time(), 'endfor'
        raw_ts_series, raw_groups = partition_time(ts_arr, results, during)
        print time.time(), 'step 1 done'
        ts_series, groups = select_groups(raw_ts_series, raw_groups, start_ts, end_ts)
        print time.time(), 'step 2 done'
        # draw_circle_data = map_circle_data(groups, True)
        max_repost_num, draw_line_data = map_line_data(groups, True)
        print time.time(), 'step 3 done'
        in_out_results = work_in_out(draw_line_data)
        print time.time(), 'step 4 done'
        repost_series, origin_series, post_series, statistic_data = statistics_data(groups, draw_line_data, True)
        print time.time(), 'step 5 done'
        return json.dumps({'draw_line_data': draw_line_data, 'in_out_results': in_out_results,'statistics_data': statistic_data, 'top_city_weibo': top_city_weibo})

        '''
        return json.dumps({'ts_arr':ts_arr, 'results':results, 'ts_series':ts_series, 'groups': groups, \
                'draw_circle_data':draw_circle_data, 'draw_line_data': draw_line_data, 'max_repost_num': max_repost_num, \
                'repost_series':repost_series, 'origin_series':origin_series, 'post_series':post_series, 'statistics_data':statistic_data})
        '''
    else:
        return json.dumps({'draw_line_data': [], 'in_out_results': [],'statistics_data': [], 'top_city_weibo': top_city_weibo})


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
        global_max_count, spatial_dict, global_first_city = readAcum(stylenum, topic, start_ts, end_ts , during)  # 查询在一定时间范围内，某个topic的stylenum信息各个省市的数量

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
        return json.dumps({'draw_line_data': [], 'in_out_results': [],'statistics_data': [], 'top_city_weibo': top_city_weibo})


@mod.route('/city_map_view_news/')
def city_map_view_news():
    topic = request.args.get('topic', '')
    during = request.args.get('pointInterval', 60 * 60) # 默认查询时间粒度为3600秒
    during = int(during)
    end_ts = request.args.get('end_ts', '')
    end_ts = long(end_ts)
    start_ts = request.args.get('start_ts', '')
    start_ts = long(start_ts)
    ts_arr = []
    results = []
    print topic.encode('utf-8'), during, end_ts, start_ts
    top_city_news = get_city_news(topic, start_ts, end_ts) #{}
    # top_city_news = {city:[weibo1,weibo2...],...}

    items = db.session.query(CityRepostNews).filter(CityRepostNews.topic == topic).all()
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
        return json.dumps({'draw_line_data': draw_line_data, 'in_out_results': in_out_results,'statistics_data': statistic_data, 'top_city_news': top_city_news})

        '''
        return json.dumps({'ts_arr':ts_arr, 'results':results, 'ts_series':ts_series, 'groups': groups, \
                'draw_circle_data':draw_circle_data, 'draw_line_data': draw_line_data, 'max_repost_num': max_repost_num, \
                'repost_series':repost_series, 'origin_series':origin_series, 'post_series':post_series, 'statistics_data':statistic_data})
        '''
    else:
        return json.dumps({'draw_line_data': [], 'in_out_results': [],'statistics_data': [], 'top_city_news': top_city_news})

@mod.route("/topic_ajax_spatial_news/")
def ajax_spatial_news():
    """
    地域演化的页面,从database获取数据返回topic_spatial.html
    """

    stylenum = request.args.get('style', '') # stylenum表示返回count是origin：1,forward：2, sum：3
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

    top_city_news = get_city_news(topic, start_ts, end_ts) #{}
    # top_city_news = {city:[weibo1,weibo2...],...}

    spatial_dict = {}
    global_max_count = 0
    if incremental == 0:
        global_first_timestamp = end_ts
        global_first_city = ""
        for i in range(pointnum + 1): # 增长量
            end_ts = start_ts +  during * i
            max_count, topic_spatial_info, first_item = readNews(stylenum, topic, end_ts , during)  # 查询在一定时间范围内，某个topic的stylenum信息各个省市的数量

            if global_max_count < max_count:
                global_max_count = max_count
            try:
                if first_item['timestamp'] <= global_first_timestamp:
                    global_first_timestamp = first_item['timestamp']
                    global_first_city = ''
            except KeyError:
                pass
            spatial_dict[str(end_ts)] = topic_spatial_info # spatial_dict = {end_ts:map_data}

    elif incremental == 1: # 累计量
        global_max_count, spatial_dict, global_first_city = readAcumNews(stylenum, topic, start_ts, end_ts , during)  # 查询在一定时间范围内，某个topic的stylenum信息各个省市的数量

    map_data = info2map(spatial_dict, incremental)
    map_data['max_count'] = global_max_count
    map_data['first_city'] = global_first_city
    map_data['top_city_news'] = top_city_news

    return json.dumps(map_data)

@mod.route('/in_out_map_news/')
def in_out_map_news():
    topic = request.args.get('topic', '')
    during = request.args.get('pointInterval', 60 * 60) # 默认查询时间粒度为3600秒
    during = int(during)
    end_ts = request.args.get('end_ts', '')
    end_ts = long(end_ts)
    start_ts = request.args.get('start_ts', '')
    start_ts = long(start_ts)
    ts_arr = []
    results = []

    top_city_news = get_city_news(topic, start_ts, end_ts)
    # top_city_news = {city:[weibo1,weibo2...],...}

    items = db.session.query(CityRepostNews).filter(CityRepostNews.topic == topic).all()
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
        return json.dumps({'draw_line_data': draw_line_data, 'in_out_results': in_out_results, 'statistics_data': statistic_data, 'top_city_news': top_city_news})

        '''
        return json.dumps({'ts_arr':ts_arr, 'results':results, 'ts_series':ts_series, 'groups': groups, \
                'draw_circle_data':draw_circle_data, 'draw_line_data': draw_line_data, 'max_repost_num': max_repost_num, \
                'repost_series':repost_series, 'origin_series':origin_series, 'post_series':post_series, 'statistics_data':statistic_data})
        '''
    else:
        return json.dumps({'draw_line_data': [], 'in_out_results': [],'statistics_data': [], 'top_city_news': top_city_news})
