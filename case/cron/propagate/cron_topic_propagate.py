# -*- coding: utf-8 -*-

import sys
import json

from config import db
from xapian_case.utils import top_keywords, gen_mset_iter

sys.path.append('../../')
from global_config import mtype_kv
from time_utils import datetime2ts, ts2HourlyTime
from global_utils import getWeiboById, getTopicByName
from dynamic_xapian_weibo import getXapianWeiboByTopic
from model import PropagateCount, PropagateKeywords, PropagateWeibos

Minute = 60
Fifteenminutes = 15 * 60
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24

N = 10 # top N设置---确定后放在配置文件中
TOP_KEYWORDS_LIMIT = 50
TOP_WEIBOS_LIMIT = 50

RESP_ITER_KEYS = ['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'bmiddle_pic', 'geo', 'comments_count', 'sentiment', 'terms']
fields_list=['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', 'comments_count', 'sentiment', 'topics', 'message_type', 'terms']
SORT_FIELD = 'reposts_count'


def top_weibos(get_results, top=TOP_WEIBOS_LIMIT):
    weibos = []
    for r in get_results():
        weibos.append(r)
        """
        try:
            weibo = getWeiboById(r['_id'])
            if weibo:
                r['attitudes_count'] = int(weibo['attitudes_count'])
                r['reposts_count'] = int(weibo['reposts_count'])
                r['comments_count'] = int(weibo['comments_count'])
            weibos.append(r)
        except:
            pass
        """
    sorted_weibos = sorted(weibos, key=lambda k: k[SORT_FIELD], reverse=False)
    sorted_weibos = sorted_weibos[len(sorted_weibos)-top:]
    sorted_weibos.reverse()

    return sorted_weibos


def save_pc_results(topic, results, during):
    for k, v in results.iteritems():
        mtype = k
        ts, dcount = v
        item = PropagateCount(topic, during, ts, mtype, json.dumps({'other': dcount}))
        item_exist = db.session.query(PropagateCount).filter(PropagateCount.topic==topic, \
                                                             PropagateCount.range==during, \
                                                             PropagateCount.end==ts, \
                                                             PropagateCount.mtype==mtype).first()
        if item_exist:
            db.session.delete(item_exist)
        db.session.add(item)
    db.session.commit()


def save_kc_results(topic, results, during, k_limit):
    for k, v in results.iteritems():
        mtype = k
        ts, kcount = v
        #print 'kcount:',kcount
        item = PropagateKeywords(topic, ts, during, mtype, k_limit, json.dumps(kcount))
        #print 'item:', item.kcount
        item_exist = db.session.query(PropagateKeywords).filter(PropagateKeywords.topic==topic, \
                                                                PropagateKeywords.range==during, \
                                                                PropagateKeywords.end==ts, \
                                                                PropagateKeywords.mtype==mtype, \
                                                                PropagateKeywords.limit==k_limit).first()
        if item_exist:
            #print 'item_exist:'
            db.session.delete(item_exist)
        db.session.add(item)
    db.session.commit()


def save_ws_results(topic, results, during, w_limit):
    for k ,v in results.iteritems():
        mtype = k
        ts, top_ws = v
        item = PropagateWeibos(topic , ts, during, mtype, w_limit, json.dumps(top_ws))
        item_exist = db.session.query(PropagateWeibos).filter(PropagateWeibos.topic==topic, \
                                                              PropagateWeibos.range==during, \
                                                              PropagateWeibos.end==ts, \
                                                              PropagateWeibos.mtype==mtype, \
                                                              PropagateWeibos.limit==w_limit).first()
        if item_exist:
            db.session.delete(item_exist)
        db.session.add(item)
    db.session.commit()


def propagateCronTopic(topic, xapian_search_weibo, start_ts, over_ts, sort_field=SORT_FIELD, \
    save_fields=RESP_ITER_KEYS, during=Fifteenminutes, w_limit=TOP_WEIBOS_LIMIT, k_limit=TOP_KEYWORDS_LIMIT):
    if topic and topic != '':
        start_ts = int(start_ts)
        over_ts = int(over_ts)
        over_ts = ts2HourlyTime(over_ts, during)
        interval = (over_ts - start_ts) / during

        for i in range(interval, 0, -1):
            begin_ts = over_ts - during * i
            end_ts = begin_ts + during
            print begin_ts, end_ts, 'topic %s starts calculate' % topic.encode('utf-8')
            
            mtype_count = {}
            mtype_kcount = {} # mtype_kcount={mtype:[terms]}
            mtype_weibo = {} # mtype_weibo={mtype:weibo}

            query_dict = {
                'timestamp': {'$gt': begin_ts, '$lt': end_ts}
            }

            for k, v in mtype_kv.iteritems():
                query_dict['message_type'] = v
                
                count, results = xapian_search_weibo.search(query=query_dict, fields=fields_list)

                # mset = xapian_search_weibo.search(query=query_dict, sort_by=[sort_field], \
                #                                  max_offset=w_limit, mset_direct=True)

                #kcount = top_keywords(gen_mset_iter(xapian_search_weibo, mset, fields=['terms']), top=k_limit)
                top_ws = top_weibos(results, top=w_limit)

                #mtype_count[v] = [end_ts, count]
                #mtype_kcount[v] = [end_ts, kcount]
                mtype_weibo[v] = [end_ts, top_ws]

            # save_pc_results(topic, mtype_count, during)
            # save_kc_results(topic, mtype_kcount, during, k_limit)
            save_ws_results(topic, mtype_weibo, during, w_limit)


if __name__ == '__main__':
    topic = u'外滩踩踏'
    topic_id = getTopicByName(topic)['_id']

    start_ts = datetime2ts('2014-12-31')
    end_ts = datetime2ts('2015-01-09')
    duration = Fifteenminutes
    xapian_search_weibo = getXapianWeiboByTopic(topic_id)

    print 'topic: ', topic.encode('utf8'), 'from %s to %s' % (start_ts, end_ts)
    propagateCronTopic(topic, xapian_search_weibo, start_ts, end_ts, during=duration)
