# -*- coding: utf-8 -*-

import IP
import json
import os
import time
import datetime
import operator
import numpy as np
from sqlalchemy import func

try:
    from case.extensions import db
    from case.model import SentimentCount, SentimentKeywords, SentimentWeibos
    from case.global_config import xapian_search_user, emotions_kv
    from case.time_utils import datetime2ts
except Exception, e:
    print e
    print 'warning:not in web environment, /moodlens/utils111.py'


Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes

TOP_KEYWORDS_LIMIT = 50
TOP_WEIBOS_LIMIT = 50

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def deal_with(news_id):
    news_id = news_id.replace(':', '-')
    news_id = news_id.replace('/', '-')
    news_id = news_id.replace('.', '-')
    return news_id


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print '%r %2.2f sec' % (method.__name__, te - ts)
        return result
    return timed


def ts2HourlyTime(ts, interval):
    # interval 取 Minite、Hour

    ts = ts - ts % interval
    return ts


def read_count_results(sentiment, start_ts, over_ts, during=Hour):
    if during <= MinInterval:
        item_exist = SentimentCount.query.filter_by(ts=over_ts, \
                                                    sentiment=sentiment, \
                                                    range=MinInterval).first()
        if item_exist:
            return item_exist.count
        else:
            return 0
    else:
        count = db.session.query(func.sum(SentimentCount.count)).filter(SentimentCount.ts > start_ts, \
                                                                        SentimentCount.ts < over_ts, \
                                                                        SentimentCount.sentiment==sentiment, \
                                                                        SentimentCount.range==MinInterval)
        if count and count[0] and count[0][0]:
            return int(count[0][0])
        else:
            return 0


def read_kcount_results(sentiment, start_ts, over_ts, during=Hour):
    if during <= MinInterval:
        item_exist = SentimentKeywords.query.filter_by(ts=over_ts, \
                                                       sentiment=sentiment, \
                                                       range=MinInterval).first()
        if item_exist:
            return item_exist.kcount
        else:
            return {}
    else:
        kcounts_dict = {}
        kcounts = SentimentKeywords.query.filter(SentimentKeywords.ts>start_ts, \
                                                 SentimentKeywords.ts<over_ts, \
                                                 SentimentKeywords.sentiment==sentiment, \
                                                 SentimentKeywords.range==MinInterval).all()
        for kcount in kcounts:
            k_c = json.loads(kcount.kcount)
            for k, v in k_c:
                try:
                    kcounts_dict[k] += v
                except KeyError:
                    kcounts_dict[k] = v            

        return list(kcounts_dict)


def read_weibo_results(sentiment, start_ts, over_ts, during=Hour):
    if during <= MinInterval:
        weibos = []
        item_exist = TopWeibos.query.filter_by(ts=over_ts, \
                                               sentiment=sentiment, \
                                               range=MinInterval).all()
        for item in item_exist:
            weibos.extend(json.loads(item.weibos))

        return weibos

    else:
        weibos = TopWeibos.query.filter(TopWeibos.ts>start_ts, \
                                        TopWeibos.ts<over_ts, \
                                        TopWeibos.sentiment==sentiment, \
                                        TopWeibos.range==MinInterval).all()
        results = []
        for weibo in weibos:
            _weibo_list = json.loads(weibo.weibos)
            results.extend(_weibo_list)

        return list(results)


def read_range_weibos_results(start_ts, over_ts, during=Hour):
    over_ts = ts2HourlyTime(over_ts, MinInterval)
    interval = (over_ts - start_ts) / during
    
    emotion_dic = {}

    if during <= MinInterval:
        for k, v in emotions_kv.iteritems():
            weibos = read_weibo_results(v, over_ts=over_ts, during=during)
            emotion_dic[k] = weibos
    else:
        end_ts = over_ts
        start_ts = end_ts - during
        
        for k, v in emotions_kv.iteritems():
            weibos = read_weibo_results(v, start_ts=start_ts, over_ts=end_ts, during=during)
            emotion_dic[k] = weibos

    return emotion_dic


def read_range_kcount_results(start_ts, over_ts, during=Hour):
    over_ts = ts2HourlyTime(over_ts, MinInterval)
    interval = (over_ts - start_ts) / during
    
    emotion_dic = {}

    if during <= MinInterval:
        for k, v in emotions_kv.iteritems():
            kcount = read_kcount_results(v, over_ts=over_ts, during=during)
            emotion_dic[k] = kcount

    else:
        end_ts = over_ts
        start_ts = end_ts - during 
        
        for k, v in emotions_kv.iteritems():
            kcount = read_kcount_results(v, start_ts=start_ts, over_ts=end_ts, during=during)
            emotion_dic[k] = kcount

    return emotion_dic


def read_range_count_results(start_ts, over_ts, during=Hour):
    over_ts = ts2HourlyTime(over_ts, MinInterval)
    interval = (over_ts - start_ts) / during
    
    emotion_dic = {}

    if during <= MinInterval:
        for k, v in emotions_kv.iteritems():
            count = read_count_results(v, over_ts=over_ts, during=during)
            emotion_dic[k] = [over_ts * 1000, count]
    else:
        end_ts = over_ts
        start_ts = end_ts - during 
        for k, v in emotions_kv.iteritems():
            count = read_count_results(v, start_ts=start_ts, over_ts=end_ts, during=during)
            emotion_dic[k] = [end_ts * 1000, count]

    return emotion_dic


def getUsernameByUid(uid):
    if not uid:
        return None
    user = xapian_search_user.search_by_id(int(uid), fields=['name'])
    if user:
        name = user['name']
        return name
    return None


def weiboinfo2url(uid, _mid):
    mid_str =  mid2str(_mid)
    return "http://weibo.com/{uid}/{mid}".format(uid=uid, mid=mid_str)

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
 
def base62_encode(num, alphabet=ALPHABET):
    """Encode a number in Base X
 
    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)
 
def base62_decode(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number
 
    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0
 
    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1
 
    return num

def url_to_mid(url):
    '''
    >>> url_to_mid('z0JH2lOMb')
    3501756485200075L
    >>> url_to_mid('z0Ijpwgk7')
    3501703397689247L
    >>> url_to_mid('z0IgABdSn')
    3501701648871479L
    >>> url_to_mid('z08AUBmUe')
    3500330408906190L
    >>> url_to_mid('z06qL6b28')
    3500247231472384L
    >>> url_to_mid('yCtxn8IXR')
    3491700092079471L
    >>> url_to_mid('yAt1n2xRa')
    3486913690606804L
    '''
    url = str(url)[::-1]
    size = len(url) / 4 if len(url) % 4 == 0 else len(url) / 4 + 1
    result = []
    for i in range(size):
        s = url[i * 4: (i + 1) * 4][::-1]
        s = str(base62_decode(str(s)))
        s_len = len(s)
        if i < size - 1 and s_len < 7:
            s = (7 - s_len) * '0' + s
        result.append(s)
    result.reverse()
    return int(''.join(result))


def mid_to_url(midint):
    '''
    >>> mid_to_url(3501756485200075)
    'z0JH2lOMb'
    >>> mid_to_url(3501703397689247)
    'z0Ijpwgk7'
    >>> mid_to_url(3501701648871479)
    'z0IgABdSn'
    >>> mid_to_url(3500330408906190)
    'z08AUBmUe'
    >>> mid_to_url(3500247231472384)
    'z06qL6b28'
    >>> mid_to_url(3491700092079471)
    'yCtxn8IXR'
    >>> mid_to_url(3486913690606804)
    'yAt1n2xRa'
    '''
    midint = str(midint)[::-1]
    size = len(midint) / 7 if len(midint) % 7 == 0 else len(midint) / 7 + 1
    result = []
    for i in range(size):
        s = midint[i * 7: (i + 1) * 7][::-1]
        s = base62_encode(int(s))
        s_len = len(s)
        if i < size - 1 and len(s) < 4:
            s = '0' * (4 - s_len) + s
        result.append(s)
    result.reverse()
    return ''.join(result)


def mid2str(mid):
    mid = str(mid)
    s1 = base62_encode(int(mid[:2]))
    s2 = base62_encode(int(mid[2:9]))
    s3 = base62_encode(int(mid[9:16]))
    return s1+s2+s3


def save_rt_results(calc, query, results, during, klimit=TOP_KEYWORDS_LIMIT, wlimit=TOP_WEIBOS_LIMIT):
    if calc == 'count':
        for k, v in results.iteritems():
            sentiment = k
            ts, count = v
            item = SentimentTopicCount(query, during, ts, sentiment, count)
            item_exist = SentimentTopicCount(query=query, range=during, end=ts, sentiment=sentiment).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
        
        db.session.commit()

    if calc == 'kcount':
        for k, v in results.iteritems():
            sentiment = k
            ts, kcount = v
            item = SentimentTopicKeywords(query, during, ts, sentiment, json.dumps(kcount))
            item_exist = SentimentTopicKeywords.query.filter_by(query=query, range=during, end=ts, limit=klimit, sentiment=sentiment).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
        
        db.session.commit()

    if calc == 'weibos':
        for k, v in results.iteritems():
            sentiment = k
            ts, weibos = v
            item = SentimentTopicTopWeibos(query, during, ts, sentiment, json.dumps(weibos))
            item_exist = SentimentTopicTopWeibos.query.filter_by(query=query, range=during, end=ts, limit=wlimit, sentiment=sentiment).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
        
        db.session.commit()

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


def IP2city(geo):
    try:
        city=IP.find(str(geo))
        if city:
            city=city.encode('utf-8')
        else:
            return None
    except Exception,e:
        return None

    return city

if __name__ == '__main__':
    print mid2str(3618955195344752)
    print mid_to_url(3617699454295114L)
    print IP2city('180.136.202.119')
