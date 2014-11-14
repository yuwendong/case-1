# -*- coding: utf-8 -*-

import sys
import json

from config import db
from xapian_case.utils import top_keywords, gen_mset_iter

sys.path.append('../../')
from ad_filter import ad_classifier
from global_config import emotions_kv
from time_utils import datetime2ts, ts2HourlyTime
from global_utils import getWeiboById, getTopicByName
from dynamic_xapian_weibo import getXapianWeiboByTopic
from model import SentimentCount, SentimentKeywords, SentimentWeibos, SentimentCountRatio

Minute = 60
Fifteenminutes = 15 * 60
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24

TOP_KEYWORDS_LIMIT = 50
TOP_WEIBOS_LIMIT = 50

RESP_ITER_KEYS = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'bmiddle_pic', 'geo', 'comments_count', 'sentiment', 'terms']
SORT_FIELD = 'reposts_count'


def top_weibos(get_results, top=TOP_WEIBOS_LIMIT):
    weibos = []
    for r in get_results():
        try:
            weibo = getWeiboById(r['_id'])
            if weibo:
                r['attitudes_count'] = int(weibo['attitudes_count'])
                r['reposts_count'] = int(weibo['reposts_count'])
                r['comments_count'] = int(weibo['comments_count'])
            weibos.append(r)
        except:
            pass
    sorted_weibos = sorted(weibos, key=lambda k: k[SORT_FIELD], reverse=False)
    sorted_weibos = sorted_weibos[len(sorted_weibos)-top:]
    sorted_weibos.reverse()

    return sorted_weibos


def save_rt_results(calc, query, results, during, klimit=TOP_KEYWORDS_LIMIT, wlimit=TOP_WEIBOS_LIMIT):
    if calc == 'count':
        for k, v in results.iteritems():
            sentiment = k
            ts, count = v
            item = SentimentCount(query, during, ts, sentiment, count)
            item_exist = db.session.query(SentimentCount).filter(SentimentCount.query==query, \
                                                                         SentimentCount.range==during, \
                                                                         SentimentCount.end==ts, \
                                                                         SentimentCount.sentiment==sentiment).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
        
        db.session.commit()

    if calc == 'kcount':
        for k, v in results.iteritems():
            sentiment = k
            ts, kcount = v
            item = SentimentKeywords(query, during, klimit, ts, sentiment, json.dumps(kcount))
            item_exist = db.session.query(SentimentKeywords).filter(SentimentKeywords.query==query, \
                                                                            SentimentKeywords.range==during, \
                                                                            SentimentKeywords.end==ts, \
                                                                            SentimentKeywords.limit==klimit, \
                                                                            SentimentKeywords.sentiment==sentiment).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
        
        db.session.commit()

    if calc == 'weibos':
        for k, v in results.iteritems():
            sentiment = k
            ts, weibos = v
            item = SentimentWeibos(query, during, wlimit, ts, sentiment, json.dumps(weibos))
            item_exist = db.session.query(SentimentWeibos).filter(SentimentWeibos.query==query, 
                                                                                   SentimentWeibos.range==during, 
                                                                                   SentimentWeibos.end==ts, 
                                                                                   SentimentWeibos.limit==wlimit, 
                                                                                   SentimentWeibos.sentiment==sentiment).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
        
        db.session.commit()

    if calc == 'rcount': # 相对比例
        for k, v in results.items():
            ts = k
            allcount = 0
            for i in range(len(emotions_kv)):
                allcount += v[i][1]
            for sentiment, count in results[ts]:
                item = SentimentCountRatio(query, ts, during, sentiment, count, allcount)
                item_exist = db.session.query(SentimentCountRatio).filter(SentimentCountRatio.query==query, \
                                                                           SentimentCountRatio.range==during, \
                                                                           SentimentCountRatio.end==ts, \
                                                                           SentimentCountRatio.sentiment==sentiment).first()

                if item_exist:
                    db.session.delete(item_exist)
                db.session.add(item)
            db.session.commit()


def sentimentCronTopic(topic, xapian_search_weibo, start_ts, over_ts, sort_field=SORT_FIELD, save_fields=RESP_ITER_KEYS, \
    during=Fifteenminutes, w_limit=TOP_WEIBOS_LIMIT, k_limit=TOP_KEYWORDS_LIMIT):
    if topic and topic != '':
        start_ts = int(start_ts)
        over_ts = int(over_ts)

        over_ts = ts2HourlyTime(over_ts, during)
        interval = (over_ts - start_ts) / during

        for i in range(interval, 0, -1):
            emotions_kcount = {}
            emotions_count = {}
            emotions_weibo = {}

            begin_ts = over_ts - during * i
            end_ts = begin_ts + during
            print begin_ts, end_ts, 'topic %s starts calculate' % topic.encode('utf-8')

            query_dict = {
                'timestamp': {'$gt': begin_ts, '$lt': end_ts},
                '$and': [
                    {'$or': [{'message_type': 1}, {'message_type': 3}]},
                ]
            }
            for k, v in emotions_kv.iteritems():
                query_dict['sentiment'] = v
                count, results = xapian_search_weibo.search(query=query_dict, fields=save_fields)

                mset = xapian_search_weibo.search(query=query_dict, sort_by=[sort_field], \
                                                  max_offset=w_limit, mset_direct=True)

                kcount = top_keywords(gen_mset_iter(xapian_search_weibo, mset, fields=['terms']), top=k_limit)
                top_ws = top_weibos(results, top=w_limit)

                emotions_count[v] = [end_ts, count]
                emotions_kcount[v] = [end_ts, kcount]
                emotions_weibo[v] = [end_ts, top_ws]

            save_rt_results('count', topic, emotions_count, during)
            save_rt_results('kcount', topic, emotions_kcount, during, k_limit, w_limit)
            save_rt_results('weibos', topic, emotions_weibo, during, k_limit, w_limit)  


if __name__ == '__main__':
    topic = u'全军政治工作会议'
    topic_id = getTopicByName(topic)['_id']

    start_ts = datetime2ts('2014-10-30')
    end_ts = datetime2ts('2014-11-15')
    duration = Fifteenminutes
    xapian_search_weibo = getXapianWeiboByTopic(topic_id)

    print 'topic: ', topic.encode('utf8'), 'from %s to %s' % (start_ts, end_ts)
    sentimentCronTopic(topic, xapian_search_weibo, start_ts=start_ts, over_ts=end_ts, during=duration)
