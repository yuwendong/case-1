#-*- coding:utf-8 -*-
import os
import re
import time
import json
import simplejson as json
import counts as countsModule
import weibos as weibosModule
import keywords as keywordsModule
import ratio as ratioModule
import pie as pieModule

from case.model import *
from case.extensions import db
from utils import weiboinfo2url
from peak_detection import detect_peaks
from datetime import date, datetime
from xapian_case.utils import top_keywords
from case.global_config import DOMAIN_LIST, DOMAIN_ZH_LIST, emotions_kv
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect, make_response

mod = Blueprint('moodlens', __name__, url_prefix='/moodlens')


@mod.route('/topic')
def index():
    return render_template('moodlens/topic.html')

@mod.route('/weibo')
def weibo():
    return render_template('moodlens/weibo.html')



Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes

FIELDS2ID = {}
FIELDS2ZHNAME = {}
for key in DOMAIN_LIST:
    idx = DOMAIN_LIST.index(key)
    FIELDS2ID[key] = idx
    FIELDS2ZHNAME[key] = DOMAIN_ZH_LIST[idx]


def get_default_timerange():
    return u'9月 22日,2013 - 9月 22日,2013'


def get_default_field_dict():
    field_dict = {}
    for idx, field_en in enumerate(DOMAIN_LIST[9:20]):
        field_dict[field_en] = DOMAIN_ZH_LIST[idx+9]

    return field_dict


def get_default_field_name():
    return 'activer', u'活跃人士'


@mod.route('/', methods=['GET','POST'])
def index_():   #获取情绪拐点时要用到这个方法
    default_timerange = get_default_timerange()
    default_field_dict = get_default_field_dict()
    default_field_enname, default_field_zhname = get_default_field_name()
    if 'logged_in' in session and session['logged_in']:
        if session['user'] == 'admin':
            return render_template('moodlens/index.html', time_range=default_timerange, field_en=default_field_enname, \
                                   field_zh=default_field_zhname, field_dict=default_field_dict)
        else:
            pas = db.session.query(UserList).filter(UserList.username==session['user']).all()
            if pas != []:
                for pa in pas:
                    identy = pa.moodlens
                    if identy == 1:
                        return render_template('moodlens/index.html', time_range=default_timerange, field_en=default_field_enname, \
                                               field_zh=default_field_zhname, field_dict=default_field_dict)
                    else:
                        return redirect('/')
            return redirect('/')
    else:
        return redirect('/')

def _default_time_zone():
    '''默认时间段为最新一周
    '''

    end_ts = time.time()
    start_ts = end_ts - 7 * 24 * 3600

    return start_ts, end_ts


@mod.route('/data/', methods=['GET','POST'])
def data():
    """分类情感数据--绝对值
    """
    customized = request.args.get('customized', '1') # 该字段已舍弃
    query = request.args.get('query', None) # 输入topic
    if query:
        query = query.strip()
    during = request.args.get('during', 900) # 计算粒度，默认为15分钟
    during = int(during)
    ts = request.args.get('ts', '')
    ts = long(ts)
    begin_ts = ts - during
    end_ts = ts

    emotion = request.args.get('emotion', 'global') # 情绪类型

    results = {}

    search_method = 'topic'
    area = None
    search_func = getattr(countsModule, 'search_%s_counts' % search_method, None)
    if search_func:
        if emotion == 'global':
            for k, v in emotions_kv.iteritems():
                results[k] = search_func(end_ts, during, v, query=query, domain=area, customized=customized)
        else:
            results[emotion] = search_func(end_ts, during, emotions_kv[emotion], query=query, domain=area, customized=customized)
    else:
        return json.dumps('search function undefined')

    return json.dumps(results)

@mod.route('/ratio/', methods=['GET','POST'])
def ratio():
    """分类情感数据--相对值
    """
    query = request.args.get('query', None) # 查询话题topic
    if query:
        query = query.strip()
    during = request.args.get('during', 900) # 粒度
    during = int(during)
    ts = request.args.get('ts', '') # 结束时间点
    ts = long(ts)
    begin_ts = ts - during
    end_ts = ts

    emotion = request.args.get('emotion', 'happy')
    results = {}
    search_method = 'topic'
    area = None
    search_func = getattr(ratioModule, 'search_%s_ratio' % search_method, None)
    if search_func:
        results[emotion] = search_func(end_ts, during, emotions_kv[emotion], query=query, domain=area)
    else:
        return json.dumps('search function undefined')

    return json.dumps(results)

@mod.route('/pie/', methods=['GET', 'POST'])
def pie():
    '''饼图数据
    '''
    query = request.args.get('query', None)
    if query:
        query = query.strip()
    during = request.args.get('during', 1800)
    during = int(during)
    ts = request.args.get('ts', '')
    ts = long(ts)
    begin_ts = ts - during
    end_ts = ts

    emotion = request.args.get('emotion', 'global') # 情绪类型

    results = {}

    search_method = 'topic'
    area = None
    search_func = getattr(countsModule, 'search_%s_counts' % search_method, None)
    if search_func:
        if emotion == 'global':
            for k, v in emotions_kv.iteritems():
                results[k] = search_func(end_ts, during, v, query=query, domain=area)[1]
        else:
            results[emotion] = search_func(end_ts, during, emotions_kv[emotion], query=query, domain=area)[1]
    else:
        return json.dumps('search function undefined')

    return json.dumps(results)


@mod.route('/keywords_data/')
def keywords_data():
    """情绪关键词数据
    """

    customized = request.args.get('customized', '1')
    query = request.args.get('query', None)
    if query:
        query = query.strip()
    during = request.args.get('during', 24*3600)
    during = int(during)

    ts = request.args.get('ts', '')
    ts = long(ts)

    begin_ts = ts - during
    end_ts = ts
    limit = request.args.get('limit', 50)
    limit = int(limit)
    emotion = request.args.get('emotion', 'global')

    results = {}
    search_method = 'topic'
    area = None
    search_func = getattr(keywordsModule, 'search_%s_keywords' % search_method, None)

    if search_func:
        if emotion == 'global':
            keywords_data = {}
            for k, v in emotions_kv.iteritems():
                emotion_results = search_func(end_ts, during, v, query=query, domain=area, top=limit, customized=customized)    
                for keyword, count in emotion_results.iteritems():
                    try:
                        keywords_data[keyword] += count
                    except KeyError:
                        keywords_data[keyword] = count
            kcount_tuple = sorted(keywords_data.iteritems(), key=lambda (k, v): v, reverse=False)
            for k, v in kcount_tuple[len(kcount_tuple)-limit:]:
                results[k] = v
        else:
            results[emotion] = search_func(end_ts, during, emotions_kv[emotion], query=query, domain=area, top=limit, customized=customized)    
    else:
        return json.dumps('search function undefined')

    return json.dumps(results)

@mod.route('/weibos_data/')
def weibos_data():
    """关键微博
    """

    customized = request.args.get('customized', '1')
    query = request.args.get('query', None)
    if query:
        query = query.strip()
    during = request.args.get('during', 24*3600)
    during = int(during)
    emotion = request.args.get('emotion', 'global')
    ts = request.args.get('ts', '')
    ts = long(ts)
    begin_ts = ts - during
    end_ts = ts
    limit = request.args.get('limit', 50)
    limit = int(limit)

    results = {}
    search_method = 'topic'
    area = None
    search_func = getattr(weibosModule, 'search_%s_weibos' % search_method, None)

    if search_func:
        if emotion == 'global':
            for k, v in emotions_kv.iteritems():
                results[k] = search_func(end_ts, during, v, query=query, domain=area, limit=limit, customized=customized)
        else:
            results[emotion] = search_func(end_ts, during, emotions_kv[emotion], query=query, domain=area, limit=limit, customized=customized)
    else:
        return json.dumps('search function undefined')

    return json.dumps(results)


@mod.route('/emotionpeak/')
def getPeaks():
    '''获取情绪拐点数据
    '''

    customized = request.args.get('customized', '1')
    limit = request.args.get('limit', 10)
    query = request.args.get('query', None)
    if query:
        query = query.strip()
    during = request.args.get('during', 24 * 3600)
    during = int(during)
    emotion = request.args.get('emotion', 'happy')
    lis = request.args.get('lis', '')

    try:
        lis = [float(da) for da in lis.split(',')]
    except:
        lis = []
    if not lis or not len(lis):
        return 'Null Data'

    ts_lis = request.args.get('ts', '')
    ts_lis = [float(da) for da in ts_lis.split(',')]

    new_zeros = detect_peaks(lis)

    search_method = 'topic'
    area = None

    search_func = getattr(keywordsModule, 'search_%s_keywords' % search_method, None)

    if not search_func:
        return json.dumps('search function undefined')

    title_text = {'happy': [], 'angry': [], 'sad': [], 'news': []}
    title = {'happy': 'A', 'angry': 'B', 'sad': 'C', 'news': 'D'}

    time_lis = {}
    for idx, point_idx in enumerate(new_zeros):
        print idx, point_idx
        ts = ts_lis[point_idx]
        end_ts = ts

        v = emotions_kv[emotion]

        time_lis[idx] = {
            'ts': end_ts * 1000,
            'title': title[emotion] + str(idx),
        }

    return json.dumps(time_lis)

