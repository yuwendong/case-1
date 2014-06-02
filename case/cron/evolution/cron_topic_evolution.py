# -*- coding: utf-8 -*-


import json
# from topics import _all_topics
from time_utils import datetime2ts, ts2HourlyTime
from xapian_weibo.utils import top_keywords, gen_mset_iter
from dynamic_xapian_weibo import getXapianWeiboByDate
from config import evolutions_kv, db
from model import EvolutionTopicCount, EvolutionTopicKeywords, EvolutionTopicTopWeibos


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
            evolution = k
            ts, count = v
            item = EvolutionTopicCount(query, during, ts, evolution, count)
            item_exist = db.session.query(EvolutionTopicCount).filter(EvolutionTopicCount.query==query, \
                                                                         EvolutionTopicCount.range==during, \
                                                                         EvolutionTopicCount.end==ts, \
                                                                         EvolutionTopicCount.evolution==evolution).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
        
        db.session.commit()

    if calc == 'kcount':
        for k, v in results.iteritems():
            evolution = k
            ts, kcount = v
            item = EvolutionTopicKeywords(query, during, klimit, ts, evolution, json.dumps(kcount))
            item_exist = db.session.query(EvolutionTopicKeywords).filter(EvolutionTopicKeywords.query==query, \
                                                                            EvolutionTopicKeywords.range==during, \
                                                                            EvolutionTopicKeywords.end==ts, \
                                                                            EvolutionTopicKeywords.limit==klimit, \
                                                                            EvolutionTopicKeywords.evolution==evolution).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
        
        db.session.commit()

    if calc == 'weibos':
        for k, v in results.iteritems():
            evolution = k
            ts, weibos = v
            item = EvolutionTopicTopWeibos(query, during, wlimit, ts, evolution, json.dumps(weibos))
            item_exist = db.session.query(EvolutionTopicTopWeibos).filter(EvolutionTopicTopWeibos.query==query, 
                                                                                   EvolutionTopicTopWeibos.range==during, 
                                                                                   EvolutionTopicTopWeibos.end==ts, 
                                                                                   EvolutionTopicTopWeibos.limit==wlimit, 
                                                                                   EvolutionTopicTopWeibos.evolution==evolution).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
        
        db.session.commit()


def evolutionCronTopic(topic, xapian_search_weibo, start_ts, over_ts, sort_field=SORT_FIELD, save_fields=RESP_ITER_KEYS, during=Fifteenminutes, w_limit=TOP_WEIBOS_LIMIT, k_limit=TOP_KEYWORDS_LIMIT):
    if topic and topic != '':
        start_ts = int(start_ts)
        over_ts = int(over_ts)

        over_ts = ts2HourlyTime(over_ts, during)
        interval = (over_ts - start_ts) / during

        topics = topic.strip().split(',')

        for i in range(interval, 0, -1):
            evolutions_count = {}
            evolutions_kcount = {}
            evolutions_weibo = {}

            begin_ts = over_ts - during * i
            end_ts = begin_ts + during
            print begin_ts, end_ts, 'topic %s starts calculate' % topic.encode('utf-8')

            all_query_dict = {}
            topics_list = []
            for topic in topics:
                topics_list.append({'text': topic})

            original_dict = {}
            original_dict['retweeted_mid'] = 0
            original_dict['$or'] = topics_list
            original_dict['timestamp'] = {'$gt': begin_ts, '$lt': end_ts}
            forward_dict = {}#不能用等号 等号相当于深复制
            forward_dict['$not'] = {'retweeted_mid': 0}
            forward_dict['$or'] = topics_list
            forward_dict['timestamp'] = {'$gt': begin_ts, '$lt': end_ts}
            comment_dict = {}
            comment_dict['$or'] = topics_list
            comment_dict['timestamp'] = {'$gt': begin_ts, '$lt': end_ts}
            all_query_dict[1] = original_dict
            all_query_dict[2] = forward_dict
            all_query_dict[3] = comment_dict

            for k, v in evolutions_kv.iteritems():
                query_dict = all_query_dict[v]

                scount = xapian_search_weibo.search(query=query_dict, count_only=True)
                mset = xapian_search_weibo.search(query=query_dict, sort_by=[sort_field], \
                                                  max_offset=w_limit, mset_direct=True)
                kcount = top_keywords(gen_mset_iter(xapian_search_weibo, mset, fields=['terms']), top=k_limit)
                top_ws = top_weibos(gen_mset_iter(xapian_search_weibo, mset, fields=save_fields), top=w_limit)

                evolutions_count[v] = [end_ts, scount]
                evolutions_kcount[v] = [end_ts, kcount]
                evolutions_weibo[v] = [end_ts, top_ws]

                print k, v, ', evolutions count: ', evolutions_count, ', evolution keywords length: ', len(kcount), ', evolution weibos length: ', len(top_ws)

            print '%s %s saved evolutions counts, keywords and weibos' % (begin_ts, end_ts)
            save_rt_results('count', topic, evolutions_count, during)
            save_rt_results('kcount', topic, evolutions_kcount, during, k_limit, w_limit)
            save_rt_results('weibos', topic, evolutions_weibo, during, k_limit, w_limit)


def cal_topic_evolution_by_date(topic, datestr, duration):
    start_ts = datetime2ts(datestr)
    end_ts = start_ts + Day
    xapian_search_weibo = getXapianWeiboByDate(datestr.replace('-', ''))
    if xapian_search_weibo:
        evolutionCronTopic(topic, xapian_search_weibo, start_ts=start_ts, over_ts=end_ts, during=duration)
   

def worker(topic, datestr):
    print 'topic: ', topic, 'datestr:', datestr, 'Fifteenminutes: '
    cal_topic_evolution_by_date(topic, datestr, Fifteenminutes)


# def _topics_names():
#     results = []
#     topics = _all_topics(True)
#     for topic in topics:
#         results.append(topic.topic)

#     return results


if __name__ == '__main__':
    datestr = '2013-09-18' 
    topic_example = u'九一八'
    worker(topic_example,datestr)


    '''
    datestr_list = ['2013-09-01', '2013-09-02', '2013-09-03', '2013-09-04', '2013-09-05']
    topics_list = _topics_names()
    for datestr in datestr_list:
        for topic in topics_list:
            worker(topic, datestr)
    '''
