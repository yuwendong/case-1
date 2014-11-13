# -*- coding: utf-8 -*-

import sys
import json
from topics import _all_topics
sys.path.append('../')
from time_utils import datetime2ts, ts2HourlyTime
from xapian_case.utils import top_keywords, gen_mset_iter
from dynamic_xapian_weibo import getXapianWeiboByDate, getXapianWeiboByDuration, getXapianWeiboByTopic
from config import emotions_kv, db
from model import SentimentCount, SentimentKeywords, SentimentWeibos, SentimentCountRatio
import sys
sys.path.append('../libsvm-3.17/python/')
from sta_ad import start

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

def get_nad(rlist):
    flag = '0520'
    data = start(rlist, flag)
    return len(data),data

def sentimentCronTopic(topic, xapian_search_weibo, start_ts, over_ts, sort_field=SORT_FIELD, save_fields=RESP_ITER_KEYS, during=Fifteenminutes, w_limit=TOP_WEIBOS_LIMIT, k_limit=TOP_KEYWORDS_LIMIT):
    if topic and topic != '':
        start_ts = int(start_ts)
        over_ts = int(over_ts)

        over_ts = ts2HourlyTime(over_ts, during)
        interval = (over_ts - start_ts) / during
        
        topics = topic.strip().split(',')
        #print 'topic:', topics
        for i in range(interval, 0, -1):
            emotions_count = {}
            emotions_kcount = {}
            emotions_weibo = {}
            emotions_rcount = {}

            begin_ts = over_ts - during * i
            end_ts = begin_ts + during
            print begin_ts, end_ts, 'topic %s starts calculate' % topic.encode('utf-8')
            '''
            query_dict = {
                'timestamp': {'$gt': begin_ts, '$lt': end_ts},
                '$or':[]
                #'topics':[u'中国', u'日本']
            }
            
            new_query_dict = {
                    'timestamp':{'$gt':begin_ts, '$lt':end_ts},
                    '$and':[{'$or':[]}, {'$or':[]}]
                    }
            '''
            query_dict = {
                'timestamp': {'$gt': begin_ts, '$lt': end_ts},
                'topics':[]
            }
            new_query_dict = {
                    'timestamp':{'$gt':begin_ts, '$lt':end_ts},
                    'topics': [],
                    '$or': []
                    }
            '''
            for c_topic in topics:
                query_dict['$or'].append({'topics': c_topic})
                new_query_dict['$and'][0]['$or'].append({'topics': c_topic})
            '''
            for c_topic in topics:
                query_dict['topics'].append(c_topic)
                new_query_dict['topics'].append(c_topic)
            #print 'query_dict:', query_dict
            for k, v in emotions_kv.iteritems():
                query_dict['sentiment'] = v
                new_query_dict['sentiment'] = v
                #print 'query_dict:', query_dict
                scount1 ,results1 = xapian_search_weibo.search(query=query_dict, fields=['_id', 'text'])
                print 'scount1: ',scount1
                results_list=[]
                if scount1:
                    for result in results1():
                        results_list.append([result['_id'], result['text'].encode('utf-8')])
                        #if scount1==1:
                            #print results_list
                    #print 'type(results_list):', type(results_list)
                    scount, data_wid = get_nad(results_list)
                    print 'scount_new', scount
                else:
                    scount = 0
                    data_wid = []
                for nad_wid in data_wid:
                    new_query_dict['$or'].append({'_id': nad_wid})
                #print 'new_query_dict:',new_query_dict
                mset = xapian_search_weibo.search(query=new_query_dict, sort_by=[sort_field], \
                                                             max_offset=w_limit, mset_direct=True)
                
                kcount = top_keywords(gen_mset_iter(xapian_search_weibo, mset, fields=['terms']), top=k_limit)
                top_ws = top_weibos(gen_mset_iter(xapian_search_weibo, mset, fields=save_fields), top=w_limit)

                emotions_count[v] = [end_ts, scount]
                emotions_kcount[v] = [end_ts, kcount]
                emotions_weibo[v] = [end_ts, top_ws]
                #try:
                #    emotions_rcount[end_ts].append((v, scount))
                #except KeyError:
                #    emotions_rcount[end_ts] = [(v,scount)]

            save_rt_results('count', topic, emotions_count, during)
            #print emotions_count
            save_rt_results('kcount', topic, emotions_kcount, during, k_limit, w_limit)
            save_rt_results('weibos', topic, emotions_weibo, during, k_limit, w_limit)
            #print '*'*10
            #print emotions_rcount
            #save_rt_results('rcount', topics, emotions_rcount, during)


def maintain_topic_sentiment(xapian_search_weibo, start_ts, end_ts):
	topics = _all_topics(iscustom=True)
	during = end_ts - start_ts

	for topic in topics:
		topicname = topic.topic
		results = sentimentRealTime(xapian_search_weibo, end_ts, during, method='topic', calc='all', query=topicname)


def cal_topic_sentiment_by_date(topic, datestr_list, duration):
    start_ts = datetime2ts(datestr_list[0])
    end_ts = datetime2ts(datestr_list[-1]) + Day
    datestrlist = []
    '''
    for datestr in datestr_list:
        datestr_new = datestr.replace('-', '')
        datestrlist.append(datestr_new)
    print 'datestrlist:', datestrlist
    xapian_search_weibo = getXapianWeiboByDuration(datestrlist)
    '''
    xapian_search_weibo = getXapianWeiboByTopic(topic)
    if xapian_search_weibo:
        sentimentCronTopic(topic, xapian_search_weibo, start_ts=start_ts, over_ts=end_ts, during=duration)
   

def worker(topic, datestr_list):
    print 'topic: ', topic.encode('utf8'), 'datestr:', datestr_list, 'Fifteenminutes: '
    cal_topic_sentiment_by_date(topic, datestr_list, Fifteenminutes)


def _topics_names():
    results = []
    topics = _all_topics(True)
    for topic in topics:
        results.append(topic.topic)

    return results


if __name__ == '__main__':
    datestr = '2013-09-07'
    datestr_list = ['2013-09-02', '2013-09-03', '2013-09-04',\
                    '2013-09-05', '2013-09-06', '2013-09-07']
    # xapian_search_weibo = getXapianWeiboByDate(datestr)
    topic = u'东盟,博览会'
    worker(topic,datestr_list)

    
    # maintain topic
    #if xapian_search_weibo:
    #    maintain_topic_sentiment(xapian_search_weibo, start_ts, end_ts)
