#-*- coding:utf-8 -*-

import sys
import os
import json
import pymongo
from topics import _all_topics
from config import emotions_kv, db
sys.path.append('../')
from time_utils import datetime2ts, ts2HourlyTime
from xapian_case.xapian_backend import XapianSearch
from xapian_case.utils import top_keywords, gen_mset_iter
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

DB_NAME = '54api_weibo_v2' 
TB_NAME = 'master_timeline_weibo' 

mongoclient =  pymongo.MongoClient('219.224.135.46')
mongodb = mongoclient[DB_NAME] 
mongotable = mongodb[TB_NAME]


def getXapianWeiboByTopic(topic):
    stub_file = '/home/ubuntu3/huxiaoqian/case_test/data/stubpath/master_timeline_weibo_topic'
    print stub_file
    if os.path.exists(stub_file):
        print 'stub exist'
        xapian_search_weibo = XapianSearch(stub=stub_file, schema_version='5')
        return xapian_search_weibo
    else:
        print 'stub not exist'
        return None


def top_weibos(get_results, top=TOP_WEIBOS_LIMIT):
    weibos = []
    for r in get_results():
        weibo = mongotable.find_one({'_id': int(r['_id'])})
        if weibo:
            r['reposts_count'] = int(weibo['reposts_count'])
            r['comments_count'] = int(weibo['comments_count'])
        weibos.append(r)
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


def sentimentCronTopic(topic_keywords, xapian_search_weibo, start_ts, over_ts, sort_field=SORT_FIELD, save_fields=RESP_ITER_KEYS, during=Fifteenminutes, w_limit=TOP_WEIBOS_LIMIT, k_limit=TOP_KEYWORDS_LIMIT):
     if topic_keywords and topic_keywords != '':
        start_ts = int(start_ts)
        over_ts = int(over_ts)

        over_ts = ts2HourlyTime(over_ts, during)
        interval = (over_ts - start_ts) / during

        topics = topic_keywords.strip().split(',')

        for i in range(interval, 0, -1):
            emotions_count = {}
            emotions_kcount = {}
            emotions_weibo = {}
            emotions_rcount = {}

            begin_ts = over_ts - during * i
            end_ts = begin_ts + during
            print begin_ts, end_ts, 'topic %s starts calculate' % topic_keywords.encode('utf-8')
            
            topic_dict = []
            for topic in topics:
                topic_dict.append({'topics': topic})

            query_dict = {
                'timestamp': {'$gt': begin_ts, '$lt': end_ts},
                '$and': [
                    {'$or': [{'message_type': 1}, {'message_type': 3}]},
                    {'$or': topic_dict}
                ]
                #'topics':[u'中国', u'日本']
            }
            
            for k, v in emotions_kv.iteritems():
                query_dict['sentiment'] = v
                #scount ,results= xapian_search_weibo.search(query=query_dict, fields=['terms'])
                #print 'scount: ', scount
                count, results = xapian_search_weibo.search(query=query_dict, fields=save_fields)
                #kcount = top_keywords(gen_mset_iter(xapian_search_weibo, mset, fields=['terms']), top=k_limit)
                top_ws = top_weibos(results, top=w_limit)

                #emotions_count[v] = [end_ts, scount]
                #emotions_kcount[v] = [end_ts, kcount]
                emotions_weibo[v] = [end_ts, top_ws]
                #try:
                #    emotions_rcount[end_ts].append((v, scount))
                #except KeyError:
                #    emotions_rcount[end_ts] = [(v,scount)]

            #save_rt_results('count', topic, emotions_count, during)
            #print emotions_count
            #save_rt_results('kcount', topic, emotions_kcount, during, k_limit, w_limit)
            save_rt_results('weibos', topic_keywords, emotions_weibo, during, k_limit, w_limit)
            #print '*'*10
            #print emotions_rcount
            #save_rt_results('rcount', topic, emotions_rcount, during)

if __name__ == '__main__':
    for datestr in ['2013-09-02', '2013-09-03', '2013-09-04', '2013-09-05', '2013-09-06', '2013-09-07']:
        topic_keywords = u'东盟,博览会'
        print 'topic: ', topic_keywords.encode('utf8'), 'datestr:', datestr, 'Fifteenminutes: '
        
        start_ts = datetime2ts(datestr)
        end_ts = start_ts + Day
        datestr = datestr.replace('-', '')
        xapian_search_weibo = getXapianWeiboByTopic(topic_keywords)
        if xapian_search_weibo:
            sentimentCronTopic(topic_keywords, xapian_search_weibo, start_ts=start_ts, over_ts=end_ts, during=Fifteenminutes)
    
