# -*- coding: utf-8 -*-
import json
import math
import operator
from case.extensions import db
from utils import weiboinfo2url, deal_with
from case.time_utils import datetime2ts, ts2date
from case.global_config import xapian_search_user as user_search
from case.model import PropagateCountNews, PropagateKeywordsNews, PropagateNews# , AttentionCount, QuicknessCount  需要查询的表
from read_quota import _json_loads, _top_weibos


Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes

TOP_KEYWORDS_LIMIT = 50
TOP_READ =50
TOP_WEIBOS_LIMIT = 50

expr = 100 # 经验值的计算
domain_list = ['folk', 'media', 'opinion_leader', 'oversea', 'other']

'''
def Merge_Acount(item): # 计算指标值 
    results = {}
    s = 0
    print 'item:',item
    for r in item:
        s += r.covernum

    results =float(s) / expr # 这里需要写一个方法，确定expr。先默认为100的常值
    return results

def Merge_Pcount(item):
    results = {}
    cover = 0
    total = 0
    for r in item:
        cover += r.covernum
        total += r.allnum
        
    results = float(cover) / total
    return results

def Merge_Qcount(item):
    results = {}
    top = 0
    total = 0
    # print 'item:',item
    for r in item:
        top += r.topnum
        total += r.allnum
        
    results = float(top) / total
    return results
'''

# domain_list = ['folk', 'media', 'opinion_leader', 'oversea', 'other']
def Merge_propagate(items):
    results = {}
    results['dcount'] = {'folk':0, 'media':0, 'opinion_leader':0, 'oversea':0, 'other':0}
    for item in items:
        results['topic'] = item.topic
        results['end'] = item.end
        for k in domain_list:
            try:
                dcount = json.loads(item.dcount)
                results['dcount'][k] += dcount[k]
            except KeyError:
                continue

    return results


def ReadPropagateNews(topic, end, during, mtype, unit=MinInterval):
    if during <= unit:
        upbound = int(math.ceil(end / (unit * 1.0)) * unit)
        item = db.session.query(PropagateCountNews).filter(PropagateCountNews.topic==topic, \
                                                       PropagateCountNews.end==upbound, \
                                                       PropagateCountNews.mtype==mtype, \
                                                       PropagateCountNews.range==unit).all()
    else:
        start = end - during
        upbound = int(math.ceil(end / (unit * 1.0)) * unit)
        lowbound = (start / unit) * unit
        item = db.session.query(PropagateCountNews).filter(PropagateCountNews.topic==topic, \
                                                       PropagateCountNews.range==unit, \
                                                       PropagateCountNews.mtype==mtype, \
                                                       PropagateCountNews.end<=upbound, \
                                                       PropagateCountNews.end>lowbound).all()
    if item:
        results = Merge_propagate(item)
    else:
        results = None

    return results

def ReadIncrement(topic, end, during, mtype, unit=MinInterval):
    items1 = ReadPropagate(topic, end, during, mtype)
    items2 = ReadPropagate(topic, end-during, during, mtype) # attent the exist of the end-during and end-during*2
    results = {}
    results['topic'] = topic
    results['end'] = end
    results['during'] = during
    results['mtype'] = mtype
    results['dincrement'] = {}
    total1=0
    total2=0
    for k in domain_list:
        try:
            results['dincrement'][k] = float(items1['dcount'][k]) / float(items2['dcount'][k]) - 1
            total1 += items1['dcount'][k]
            total2 += items2['dcount'][k]
        except:
            results['dincrement'][k] = None

    if total2 == 0:
        results['dincrement']['total'] = None
    else:
        results['dincrement']['total'] = float(total1) / float(total2) -1
    return results


def parseKcount(kcount):
    kcount_dict = {}
    kcount = json.loads(kcount)

    for k ,v in kcount:
        kcount_dict[k] = v

    return kcount_dict

def _top_keywords(kcount_dict, top=TOP_READ):
    results_dict = {}

    if kcount_dict != {}:
        results = sorted(kcount_dict.iteritems(), key=operator.itemgetter(1), reverse=False)
        results = results[len(results) - top:]

        for k, v in results:
            results_dict[k] = v

    return results_dict



def ReadPropagateKeywordsNews(topic, end_ts, during, mtype, limit=TOP_KEYWORDS_LIMIT, unit=MinInterval, top=TOP_READ):
    kcounts_dict = {}
    if during <= unit:
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        item = db.session.query(PropagateKeywordsNews).filter(PropagateKeywordsNews.end==upbound, \
                                                          PropagateKeywordsNews.topic==topic, \
                                                          PropagateKeywordsNews.mtype==mtype, \
                                                          PropagateKeywordsNews.range==unit, \
                                                          PropagateKeywordsNews.limit==limit).first()
        if item:
            kcounts_dict = parseKcount(item.kcount)

    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        items = db.session.query(PropagateKeywordsNews).filter(PropagateKeywordsNews.end>lowbound, \
                                                         PropagateKeywordsNews.end<=upbound, \
                                                         PropagateKeywordsNews.topic==topic, \
                                                         PropagateKeywordsNews.mtype==mtype, \
                                                         PropagateKeywordsNews.range==unit, \
                                                         PropagateKeywordsNews.limit==limit).all()
        for item in items:
            kcount_dict = parseKcount(item.kcount)
            for k, v in kcount_dict.iteritems():
                try:
                    kcounts_dict[k] += v
                except KeyError:
                    kcounts_dict[k] = v

    kcounts_dict = _top_keywords(kcounts_dict, top)

    return kcounts_dict

def getuserinfo(uid):
    user = acquire_user_by_id(uid)
    if not user:
        username = 'Unkonwn'
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

def parseNews(news):
    news_dict = {}
    news = _json_loads(news)

    if not news:
        return {}

    for weibo in news:
        try:
            _id = deal_with(weibo['_id'])
            replies = 1
            weibo['timestamp'] = ts2date(weibo['timestamp'])
            weibo['content168'] = weibo['content168']
            news_dict[_id] = [replies, weibo]
        except:
            continue

    return news_dict

def ReadPropagateWeibosNews(topic, end_ts, during, mtype, limit=TOP_WEIBOS_LIMIT, unit=MinInterval, top=TOP_READ):
    results_dict = {}
    if during <= unit:
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        item =db.session.query(PropagateNews).filter(PropagateNews.end==upbound, \
                                                       PropagateNews.topic==topic, \
                                                       PropagateNews.mtype==mtype, \
                                                       PropagateNews.range==unit, \
                                                       PropagateNews.limit==limit).first()
        if item:
            results_dict = parseNews(item.news)

    else:
        start_ts = end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        items = db.session.query(PropagateNews).filter(PropagateNews.end>lowbound, \
                                                         PropagateNews.end<=upbound, \
                                                         PropagateNews.topic==topic, \
                                                         PropagateNews.mtype==mtype, \
                                                         PropagateNews.range==unit, \
                                                         PropagateNews.limit==limit).all()
        for item in items:
            news_dict = parseNews(item.news)
            for k ,v in news_dict.iteritems():
                try:
                    results_dict[k][0] += v[0]
                    results_dict[k][1].append(v[1])
                except KeyError:
                    results_dict[k] = v
                    results_dict[k][0] = v[0]
                    results_dict[k][1] = [v[1]]

    results_dict = _top_weibos(results_dict, top)
    return results_dict

