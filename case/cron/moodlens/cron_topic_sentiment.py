# -*- coding: utf-8 -*-


import json
from topics import _all_topics
from time_utils import datetime2ts, ts2HourlyTime
from xapian_weibo.utils import top_keywords, gen_mset_iter
from dynamic_xapian_weibo import getXapianWeiboByDate, getXapianWeiboByDuration
from config import emotions_kv, db
from model import SentimentCount, SentimentKeywords, SentimentWeibos


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
        weibos.append(r)
    return weibos


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


def sentimentCronTopic(topic, xapian_search_weibo, start_ts, over_ts, sort_field=SORT_FIELD, save_fields=RESP_ITER_KEYS, during=Fifteenminutes, w_limit=TOP_WEIBOS_LIMIT, k_limit=TOP_KEYWORDS_LIMIT):
    if topic and topic != '':
        start_ts = int(start_ts)
        over_ts = int(over_ts)

        over_ts = ts2HourlyTime(over_ts, during)
        interval = (over_ts - start_ts) / during

        topics = topic.strip().split(',')

        for i in range(interval, 0, -1):
            emotions_count = {}
            emotions_kcount = {}
            emotions_weibo = {}

            begin_ts = over_ts - during * i
            end_ts = begin_ts + during
            print begin_ts, end_ts, 'topic %s starts calculate' % topic.encode('utf-8')

            query_dict = {
                'timestamp': {'$gt': begin_ts, '$lt': end_ts},
                '$or': []
            }

            for topic in topics:
                query_dict['$or'].append({'text': topic})

            for k, v in emotions_kv.iteritems():
                query_dict['sentiment'] = v
                scount = xapian_search_weibo.search(query=query_dict, count_only=True)
                mset = xapian_search_weibo.search(query=query_dict, sort_by=[sort_field], \
                                                  max_offset=w_limit, mset_direct=True)
                kcount = top_keywords(gen_mset_iter(xapian_search_weibo, mset, fields=['terms']), top=k_limit)
                top_ws = top_weibos(gen_mset_iter(xapian_search_weibo, mset, fields=save_fields), top=w_limit)

                emotions_count[v] = [end_ts, scount]
                emotions_kcount[v] = [end_ts, kcount]
                emotions_weibo[v] = [end_ts, top_ws]

                print k, v, ', emotions count: ', emotions_count, ', emotion keywords length: ', len(kcount), ', emotion weibos length: ', len(top_ws)

            print '%s %s saved emotions counts, keywords and weibos' % (begin_ts, end_ts)
            save_rt_results('count', topic, emotions_count, during)
            save_rt_results('kcount', topic, emotions_kcount, during, k_limit, w_limit)
            save_rt_results('weibos', topic, emotions_weibo, during, k_limit, w_limit)


def maintain_topic_sentiment(xapian_search_weibo, start_ts, end_ts):
	topics = _all_topics(iscustom=True)
	during = end_ts - start_ts

	for topic in topics:
		topicname = topic.topic
		results = sentimentRealTime(xapian_search_weibo, end_ts, during, method='topic', calc='all', query=topicname)


def cal_topic_sentiment_by_date(topic, datestr, duration):
    start_ts = datetime2ts(datestr)
    end_ts = start_ts + Day
    datestr = datestr.replace('-', '')
    xapian_search_weibo = getXapianWeiboByDate(datestr)
    if xapian_search_weibo:
        sentimentCronTopic(topic, xapian_search_weibo, start_ts=start_ts, over_ts=end_ts, during=duration)
   

def worker(topic, datestr):
    print 'topic: ', topic.encode('utf8'), 'datestr:', datestr, 'Fifteenminutes: '
    print 'step1--worker'
    cal_topic_sentiment_by_date(topic, datestr, Fifteenminutes)


def _topics_names():
    results = []
    topics = _all_topics(True)
    for topic in topics:
        results.append(topic.topic)

    return results


if __name__ == '__main__':
    datestr = '2013-09-18'
    # xapian_search_weibo = getXapianWeiboByDate(datestr)
    topic = u"九一八"
    worker(topic,datestr)

    
    # maintain topic
    #if xapian_search_weibo:
    #    maintain_topic_sentiment(xapian_search_weibo, start_ts, end_ts)
