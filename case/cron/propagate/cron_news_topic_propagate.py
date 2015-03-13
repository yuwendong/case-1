# -*- coding: utf-8 -*-

import sys
import json
import pymongo

from config import MONGODB_HOST, MONGODB_PORT, db, mtype_kv_news
from xapian_case.utils import load_scws, cut

sys.path.append('../../')
from time_utils import datetime2ts, ts2HourlyTime
from global_utils import getWeiboById, getTopicByName
from model import PropagateCountNews, PropagateKeywordsNews, PropagateNews

Minute = 60
Fifteenminutes = 15 * 60
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24

N = 10 # top N设置---确定后放在配置文件中
TOP_KEYWORDS_LIMIT = 50
TOP_NEWS_LIMIT = 50

# RESP_ITER_KEYS = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'bmiddle_pic', 'geo', 'comments_count', 'sentiment', 'terms']
fields_list=['_id', 'url', 'timestamp', 'content168', 'relative_news', 'transmit_name', 'user_name', 'source_from_name', 'title', 'showurl']
SORT_FIELD = 'timestamp'

conn = pymongo.Connection(host=MONGODB_HOST, port=MONGODB_PORT)
mongodb = conn['news']

s = load_scws()

def cut_text(item):
    text = item['content168'].encode('utf-8')
    item['terms'] = cut(s, text, cx=False)
    return item

def get_filter_dict():
    fields_dict = {}
    for field in fields_list:
        fields_dict[field] = 1
    return fields_dict

def top_news_keywords(get_results, news_top=TOP_NEWS_LIMIT, keywords_top=TOP_KEYWORDS_LIMIT):
    kcount = {}
    count = 0
    news = []
    for r in get_results:
        count += 1
        news.append(r) # no terms

        item = cut_text(r)
        terms_list = item['terms']
        for keywords in terms_list:
            try:
                kcount[keywords] += 1
            except KeyError:
                kcount[keywords] = 1

    sorted_news = sorted(news, key=lambda k: k[SORT_FIELD], reverse=False)
    sorted_news = sorted_news[len(sorted_news)-news_top:]
    sorted_news.reverse()

    kcount = sorted(kcount.iteritems(), key=lambda (k,v):v, reverse=True)
    kcount = kcount[:keywords_top] # [(k,v),]
    return count, kcount, sorted_news

def save_pc_news_results(topic, mtype, results, during):
    ts, dcount = results
    item = PropagateCountNews(topic, during, ts, mtype, json.dumps({'other': dcount}))
    item_exist = db.session.query(PropagateCountNews).filter(PropagateCountNews.topic==topic, \
                                                         PropagateCountNews.range==during, \
                                                         PropagateCountNews.mtype==mtype, \
                                                         PropagateCountNews.end==ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()


def save_kc_news_results(topic, mtype, results, during, k_limit):
    ts, kcount = results
    item = PropagateKeywordsNews(topic, ts, during, mtype, k_limit, json.dumps(kcount))
    item_exist = db.session.query(PropagateKeywordsNews).filter(PropagateKeywordsNews.topic==topic, \
                                                            PropagateKeywordsNews.range==during, \
                                                            PropagateKeywordsNews.mtype==mtype, \
                                                            PropagateKeywordsNews.end==ts, \
                                                            PropagateKeywordsNews.limit==k_limit).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()


def save_ws_news_results(topic, mtype, results, during, n_limit):
    ts, top_ns = results
    item = PropagateNews(topic , ts, during, mtype, n_limit, json.dumps(top_ns))
    item_exist = db.session.query(PropagateNews).filter(PropagateNews.topic==topic, \
                                                          PropagateNews.range==during, \
                                                          PropagateNews.mtype==mtype, \
                                                          PropagateNews.end==ts, \
                                                          PropagateNews.limit==n_limit).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()

def propagateCronNewsTopic(topic, mongo_collection, start_ts, over_ts, sort_field=SORT_FIELD, \
    during=Fifteenminutes, n_limit=TOP_NEWS_LIMIT, k_limit=TOP_KEYWORDS_LIMIT):
    if topic and topic != '':
        start_ts = int(start_ts)
        over_ts = int(over_ts)
        over_ts = ts2HourlyTime(over_ts, during)
        interval = (over_ts - start_ts) / during

        for i in range(interval, 0, -1):
            begin_ts = over_ts - during * i
            end_ts = begin_ts + during
            # print begin_ts, end_ts, 'topic %s starts calculate' % topic.encode('utf-8')

            news = []
            news_count = []
            news_kcount = []

            query_dict = {
                'timestamp': {'$gte': begin_ts, '$lt': end_ts}
            }
            fields_dict = get_filter_dict()

            results_list = mongo_collection.find(query_dict, fields_dict)

            origin_forward_dict = {'origin':[], 'forward':[]}
            for weibo_result in results_list:
                if weibo_result['source_from_name'] and weibo_result['transmit_name']:
                    origin_forward_dict['forward'].append(weibo_result)
                elif weibo_result['source_from_name']:
                    origin_forward_dict['origin'].append(weibo_result)
                else:
                    continue

            for k, v_list in origin_forward_dict.iteritems():
                mtype = mtype_kv_news[k]
                count, kcount, top_ns = top_news_keywords(v_list, news_top=n_limit, keywords_top = k_limit)

                news = [end_ts, top_ns]
                news_count = [end_ts, count]
                news_kcount = [end_ts, kcount]

                save_ws_news_results(topic, mtype, news, during, n_limit)
                save_pc_news_results(topic, mtype, news_count, during)
                save_kc_news_results(topic, mtype, news_kcount, during, k_limit)

def get_dynamic_mongo(topic, start_ts, end_ts):
    topic_collection = mongodb.news_topic
    topic_news = topic_collection.find_one({'topic':topic})
    if not topic_news:
        print 'no this topic'
        return None
    else:
        print 'exists'
        topic_news_id = topic_news['_id']
        news_collection_name = 'post_' + str(topic_news_id)
        topic_news_collection = mongodb[news_collection_name]
    return topic_news_collection


if __name__ == '__main__':
    topic = sys.argv[1] # u'香港自由行' u'张灵甫遗骨疑似被埋羊圈' u'高校思想宣传' u'高校宣传思想工作' u'外滩踩踏' 'APEC' u'全军政治工作会议'
    start_date = sys.argv[2] # '2015-02-23'
    end_date = sys.argv[3] # '2015-03-02'

    start_ts = datetime2ts(start_date)
    end_ts = datetime2ts(end_date)

    duration = Fifteenminutes
    mongo_collection = get_dynamic_mongo(topic, start_ts, end_ts)

    print 'topic: ', topic.encode('utf8'), 'from %s to %s' % (start_ts, end_ts)
    propagateCronNewsTopic(topic, mongo_collection, start_ts, end_ts, during=duration)

