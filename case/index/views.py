#-*- coding:utf-8 -*-


import json
import time
import datetime
from case.model import *
from case.extensions import db
from case.moodlens import pie as pieModule
import search as searchModule
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect, make_response


mod = Blueprint('case', __name__, url_prefix='/index')

#tag = ['九一八','钓鱼岛','历史',]
comment = ['历史是不能改变的',]

def get_default_timerange():
    return u'20130901-20130901'

def get_default_topic():
    return u'中国'

def get_default_pointInterval():
    return {'zh': u'1小时', 'en': 3600}

def get_pointIntervals():
    return [{'zh': u'15分钟', 'en': 900}, {'zh': u'1小时', 'en': 3600}, {'zh': u'1天', 'en': 3600 * 24}]

def get_gaishu_yaosus():
    return {'gaishu': u'概述分析', 'zhibiao': u'指标分析'}

def get_deep_yaosus():
    return {'time': u'时间分析' , 'area': u'空间分析', 'moodlens': u'情绪分析', 'network': u'网络分析', 'semantic': u'语义分析'}

default_timerange = get_default_timerange()
default_topic = get_default_topic()
default_pointInterval = get_default_pointInterval()
pointIntervals = get_pointIntervals()
gaishu_yaosus = get_gaishu_yaosus()
deep_yaosus = get_deep_yaosus()

@mod.route('/')
def loading():
    """舆情案例首页
    """
    return render_template('index/gl.html')

@mod.route('/detail/')
def detail():
    """原有概述首页
    """
    return render_template('index/detail.html')

@mod.route('/manage/')
def manage():
    """案例定制页面
    """
    return render_template('index/manage.html')

@mod.route('/eva/')
def eva():
    """案例评价页面
    """
    return render_template('index/eva.html')

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

    return render_template('index/diyu.html', yaosu=yaosu, time_range=time_range, \
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

@mod.route('/time/')
def shijian():
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

    return render_template('index/shijian.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/gaishu/')
def gaishu():
        # 要素
    yaosu = 'gaishu'

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

    return render_template('index/gaishu.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

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

    return render_template('index/topic.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

# 以下为新增内容
@mod.route('/gaishu_data/', methods = ['GET', 'POST'])
def gaishu_topic():
    topic = request.args.get('query', u'中国')
    if topic:
        topic = topic.strip()

    results = {}

    tag = '九一八、政府'
    results['tag'] = tag

    event_time = '2013-09-01'
    results['event_time'] = event_time

    event_spot = '北京'
    results['event_spot'] = event_spot

    # event_summary = '近年来，日本政府在钓鱼岛问题上不断挑起事端，特别是今年以来姑息纵容右翼势力掀起“购岛”风波，以为自己出面“购岛”铺路搭桥。'
    # results['event_summary'] = event_summary

    begin = topic_search('begin', topic)
    results['begin'] = begin

    end = topic_search('end', topic)
    results['end'] = end

    user_count = topic_search('user_count', topic)
    results['user_count'] = user_count

    count = topic_search('count', topic)
    results['count'] = count

    area = topic_search('area',topic)
    results['area'] = area

    k_limit = 3
    results['k_limit'] = k_limit

    key_words = topic_search('key_words',topic)
    results['key_words'] = key_words

    opinion = topic_search('opinion',topic)
    results['opinion'] = opinion

    moodlens_pie = get_moodlens_pie(topic)
    results['moodlens_pie'] = moodlens_pie

    return json.dumps(results)

def get_moodlens_pie(topic = u'中国'):
    end_ts = time.mktime(datetime.datetime(2013,9,1,0,1,0).timetuple())
    during = 10

    results = {}
    results = pieModule.search_topic_pie(end_ts, during, query = topic)

    return results


def topic_search(item = 'count', topic = u'中国'):

    results = {}

    search_func = getattr(searchModule, 'search_%s' % item, None)

    if search_func:
        results = search_func(topic)
    else:
        return 'Search function undefined'

    return results

# 以下为原有内容

@mod.route("/network_data/", methods=["POST"])
def area_network():
    request_method = request.method
    if request_method == 'POST':
        gexf = None
        form = request.form

        with open("data.txt","r+") as fh:
            data=fh.readline().strip()
            gexf=json.loads(data)

        if not gexf:
            gexf = ''

        response = make_response(gexf)
        response.headers['Content-Type'] = 'text/xml'
        return response

    else:
        abort(404)

@mod.route('/show_tag_data/')
def show_tag():
    return json.dumps({'tag': tag})

@mod.route('/alter_tag/',methods=['GET','POST'])
def alter_tag():
    tagname = request.form['tag']
    if tagname:
        tagname = tagname.strip()
    tag = []
    tag.append(tagname)
    return json.dumps(tag)

@mod.route('/show_comment_data/')
def show_comment():
    return json.dumps({'comment': comment})


@mod.route('/alter_comment/',methods=['GET','POST'])
def alter_comment():
    commentname = request.form['comment']
    if commentname:
        commentname = commentname.strip()
    comment = []
    comment.append(commentname)
    return json.dumps(comment)

@mod.route('/show_lt_data/')
def show_lt_data():
    title = []
    content = []
    title = ['2012.9.19 天涯论坛：九一八事变起因 ','2012.9.21 猫扑：九一八是精心策划的阴谋',
    '2012.9.23 天涯论坛：九一八事变起因 ','2012.9.25 猫扑：九一八是精心策划的阴谋',
    '2012.9.28 天涯论坛：九一八事变起因 ','2012.10.1 猫扑：九一八是精心策划的阴谋',
    '2012.10.19 天涯论坛：九一八事变起因 ','2012.10.21 猫扑：九一八是精心策划的阴谋',
    '2012.10.25 天涯论坛：九一八事变起因 ',]
    content = ['1931年9月18日夜，盘踞在中国东北的日本关东军按照精心策划的阴谋，由铁道“守备队”炸毁沈阳柳条湖附近日本修筑的南满铁路路轨，并栽赃嫁祸于中国军队，（其实就是要找任何一个借口，开始侵略中国）日军就以此为借口，开始“名正言顺”“光明正大”地炮轰沈阳北大营，制造了震惊中外的“九一八事变”。','九一八事变是由日本蓄意制造并发动的侵华战争，是日本帝国主义侵华的开端。九一八事变也标志着世界反法西斯战争的起点，揭开了第二次世界大战东方战场的序幕。',
    '1931年9月18日夜，盘踞在中国东北的日本关东军按照精心策划的阴谋，由铁道“守备队”炸毁沈阳柳条湖附近日本修筑的南满铁路路轨，并栽赃嫁祸于中国军队，（其实就是要找任何一个借口，开始侵略中国）日军就以此为借口，开始“名正言顺”“光明正大”地炮轰沈阳北大营，制造了震惊中外的“九一八事变”。','九一八事变是由日本蓄意制造并发动的侵华战争，是日本帝国主义侵华的开端。九一八事变也标志着世界反法西斯战争的起点，揭开了第二次世界大战东方战场的序幕。',
    '1931年9月18日夜，盘踞在中国东北的日本关东军按照精心策划的阴谋，由铁道“守备队”炸毁沈阳柳条湖附近日本修筑的南满铁路路轨，并栽赃嫁祸于中国军队，（其实就是要找任何一个借口，开始侵略中国）日军就以此为借口，开始“名正言顺”“光明正大”地炮轰沈阳北大营，制造了震惊中外的“九一八事变”。','九一八事变是由日本蓄意制造并发动的侵华战争，是日本帝国主义侵华的开端。九一八事变也标志着世界反法西斯战争的起点，揭开了第二次世界大战东方战场的序幕。',
    '1931年9月18日夜，盘踞在中国东北的日本关东军按照精心策划的阴谋，由铁道“守备队”炸毁沈阳柳条湖附近日本修筑的南满铁路路轨，并栽赃嫁祸于中国军队，（其实就是要找任何一个借口，开始侵略中国）日军就以此为借口，开始“名正言顺”“光明正大”地炮轰沈阳北大营，制造了震惊中外的“九一八事变”。','九一八事变是由日本蓄意制造并发动的侵华战争，是日本帝国主义侵华的开端。九一八事变也标志着世界反法西斯战争的起点，揭开了第二次世界大战东方战场的序幕。',
    '1931年9月18日夜，盘踞在中国东北的日本关东军按照精心策划的阴谋，由铁道“守备队”炸毁沈阳柳条湖附近日本修筑的南满铁路路轨，并栽赃嫁祸于中国军队，（其实就是要找任何一个借口，开始侵略中国）日军就以此为借口，开始“名正言顺”“光明正大”地炮轰沈阳北大营，制造了震惊中外的“九一八事变”。','九一八事变是由日本蓄意制造并发动的侵华战争，是日本帝国主义侵华的开端。九一八事变也标志着世界反法西斯战争的起点，揭开了第二次世界大战东方战场的序幕。',]

    results = {'title': title,'content': content}
    return json.dumps(results)

