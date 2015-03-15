#-*- coding:utf-8 -*-

import json
import time
import datetime
from case.model import *
from case.extensions import db
from case.moodlens import pie as pieModule
from case.identify import utils as identifyModule
import search as searchModule
from case.time_utils import ts2datetime, ts2date
from xapian_case.xapian_backend import XapianSearch
from xapian_case.utils import cut, load_scws
from case.dynamic_xapian_weibo import getXapianWeiboByTopic
from case.global_config import XAPIAN_USER_DATA_PATH
from case.Database import Event, EventManager
from case.topic_manage import topics_name_start_end
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect, make_response

scws = load_scws()

mod = Blueprint('case', __name__, url_prefix='/index')

xapian_search_weibo = getXapianWeiboByTopic()

em = EventManager()

def acquire_user_by_id(uid):
    user_search = XapianSearch(path=XAPIAN_USER_DATA_PATH, name='master_timeline_user', schema_version=1)
    result = user_search.search_by_id(int(uid), fields=['name', 'location', 'followers_count', 'friends_count', 'profile_image_url'])
    user = {}

    if result:
        user['name'] = result['name']
        user['location'] = result['location']
        user['followers_count'] = result['followers_count']
        user['friends_count'] = result['friends_count']
        user['profile_image_url'] = result['profile_image_url']
    else:
        return None

    return user

def get_default_timerange():
    return u'20150123-20150202'

def get_default_topic():
    return u'张灵甫遗骨疑似被埋羊圈'

def get_default_pointInterval():
    return {'zh': u'1天', 'en': 3600 * 24}

def get_pointIntervals():
    return [{'zh': u'15分钟', 'en': 900}, {'zh': u'1小时', 'en': 3600}, {'zh': u'1天', 'en': 3600 * 24}]

def get_gaishu_yaosus():
    return {'yaosu': [('gaishu', u'概述分析')]}
    # return {'yaosu': (('gaishu', u'概述分析'), ('zhibiao', u'指标分析'))}

def get_deep_yaosus():
    return {'yaosu': (('time', u'时间分析'), ('area', u'地域分析'), \
                      ('moodlens', u'情绪分析'), ('network', u'网络分析'))}

default_timerange = get_default_timerange()
default_topic = get_default_topic()
default_pointInterval = get_default_pointInterval()
pointIntervals = get_pointIntervals()
gaishu_yaosus = get_gaishu_yaosus()
deep_yaosus = get_deep_yaosus()

@mod.route('/')
def loading():
    """舆情案例首页（前台）,用户可以查看相应的案例，进入相应案例的分析页面
    """
    topics_list = topics_name_start_end()
    return render_template('index/gl.html', topics_list=topics_list)


@mod.route('/manage/')
def manage():
    """案例定制页面（后台），用户可以新增案例，启动后台计算
    """
    return render_template('index/manage.html')


@mod.route('/user_weibo/')
def user_weibo():
    """微博列表页面
    """
    # 要素
    yaosu = 'moodlens'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    weibos = []
    tar_location = u'地域未知'
    tar_nickname = u'昵称未知'
    tar_profile_image_url = '#'
    tar_followers_count = u'粉丝数未知'
    tar_friends_count = u'关注数未知'
    tar_user_url = '#'
    uid = request.args.get('uid', None)

    if uid:
        count, results = xapian_search_weibo.search(query={'user': int(uid)}, sort_by=['timestamp'], \
            fields=['id', 'user', 'text', 'reposts_count', 'comments_count', 'geo', 'timestamp'])

        for r in results():
            r['weibo_url'] = 'http://weibo.com/'
            r['user_url'] = 'http://weibo.com/u/' + str(uid)
            r['created_at'] = ts2date(r['timestamp'])
            weibos.append(r)

        user_info = acquire_user_by_id(uid)
        if user_info:
            tar_name = user_info['name']
            tar_location = user_info['location']
            tar_profile_image_url = user_info['profile_image_url']
            tar_friends_count = user_info['friends_count']
            tar_followers_count = user_info['followers_count']
            tar_user_url = 'http://weibo.com/u/' + str(uid)

    return render_template('index/weibolist.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus, tar_location=tar_location, \
            tar_profile_image_url=tar_profile_image_url, \
            statuses=weibos, tar_name=tar_name, tar_friends_count=tar_friends_count, \
            tar_followers_count=tar_followers_count, tar_user_url=tar_user_url)

@mod.route('/moodlens/')
def moodlens():
    # 要素
    yaosu = 'moodlens'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/moodlens.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)


@mod.route('/semantic/')
def meaning():
    # 要素
    yaosu = 'semantic'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/yuyi.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/area/')
def area():
    # 要素
    yaosu = 'area'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/area.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/area_news/')
def area_news():
    # 要素
    yaosu = 'area'

    # 话题关键词
    topic = request.args.get('query', default_topic)
    # topic = u'全军政治工作会议'

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)
    # time_range = u'20141101-20141115'

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/area_news.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/time/')
def time():
    # 要素
    yaosu = 'time'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/time.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/time_news/')
def time_news():
    # 要素
    yaosu = 'time'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/time_news.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/eventriver/')
def eventriver():
    """event river数据
    """
    topic_name = request.args.get('query', default_topic) # 话题名
    sort = request.args.get('sort', 'tfidf') # weight, addweight, created_at, tfidf
    end_ts = request.args.get('ts', None)
    during = request.args.get('during', None)

    if end_ts:
        end_ts = int(end_ts)

    if during:
        during = int(during)
        start_ts = end_ts - during

    topicid = em.getEventIDByName(topic_name)
    event = Event(topicid)
    subeventlist, dates, total_weight = event.getEventRiverData(start_ts, end_ts, sort=sort)

    return json.dumps({"dates": dates, "name": topic_name, "type": "eventRiver", "weight": total_weight, "eventList": subeventlist})

@mod.route('/gaishu/')
def gaishu():
    # 要素
    yaosu = 'gaishu'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 事件标签
    event_label = cut(scws, topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/gaishu.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus, event_label=event_label)

@mod.route('/zhibiao/')
def zhibiao():
    # 要素
    yaosu = 'zhibiao'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/zhibiao.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/network/')
def topic():
    # 要素
    yaosu = 'network'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/network_direct_superior2.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/network1/')
def topic1():
    # 要素
    yaosu = 'network1'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/network_source.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/network_news/')
def network_news():
    yaosu = 'network_news'
    topic = request.args.get('query', default_topic)
    time_range = request.args.get('time_range', default_timerange)
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/network_news.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntegervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/network2/')
def topic2():
    # 要素
    yaosu = 'network2'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/network_direct_superior.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/alter_tag/',methods=['GET','POST'])
def alter_tag():
    tagname = request.form['tag']
    if tagname:
        tagname = tagname.strip()
    tag = []
    tag.append(tagname)
    return json.dumps(tag)

