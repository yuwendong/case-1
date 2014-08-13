# -*- coding: utf-8 -*-

import json
import redis
import datetime
from xapian_case.utils import top_keywords, gen_mset_iter
from time_utils import datetime2ts, ts2HourlyTime
from dynamic_xapian_weibo import getXapianWeiboByDate, getXapianWeiboByDuration # 获取一定时间段内的微博
from config import mtype_kv, db
from model import PropagateCount, PropagateKeywords, PropagateWeibos #, AttentionCount, QuicknessCount  一定时间、话题、信息类型对应的{domain:count}


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

REDIS_HOST = '219.224.135.48'
REDIS_PORT = 6379
USER_DOMAIN = "user_domain"  # user domain hash,


def _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=0):
    return redis.StrictRedis(host, port, db)

r = _default_redis()


def uid2domain(user): 
    """将用户转化为对应的领域
    """

    # DOMAIN_V3_LIST = ['folk', 'media', 'opinion_leader', 'oversea', 'other']
    # DOMAIN_V3_ZH_LIST = [u'民众', u'媒体', u'意见领袖', u'境外', u'其他']

    domain_str = r.hget(USER_DOMAIN, str(user))
    if not domain_str:
        return 'other'

    domain_dict = json.loads(domain_str)
    domain = domain_dict['v3']

    return domain

def top_weibos(get_results, top=TOP_WEIBOS_LIMIT):
    weibos = []
    for r  in get_results():
        weibos.append(r)
    return weibos




'''
def TopNum(ts_list): # ts_list=[ts1,ts1,ts2...] >> ts_dict{ts1:count1, ts2:count2...}  >> sort_ts=[(ts1,count1),(ts2,count2)...]倒序排列
    ts_dict = {}
    topnum = 0
    for i in ts_list:
        try:
            ts_dict[i] += 1
        except KeyError:
            ts_dict[i] = 1
    sort_ts = sorted(ts_dict.iteritems(), key=lambda a:a[1], reverse=False)
    results = sort_ts[:10]
    print 'sort_ts_top10:', results
    topnum = sum([count for ts,count in results])
    print 'topnum:', topnum
    return topnum
'''

def save_pc_results(topic, results, during):
    for k, v in results.iteritems():
        mtype = k
        ts, dcount = v
        item = PropagateCount(topic, during, ts, mtype, json.dumps(dcount))
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
        item = PropagateKeywords(topic, ts, during, mtype, k_limit, json.dumps(kcount))
        item_exist = db.session.query(PropagateKeywords).filter(PropagateKeywords.topic==topic, \
                                                                PropagateKeywords.range==during, \
                                                                PropagateKeywords.end==ts, \
                                                                PropagateKeywords.mtype==mtype, \
                                                                PropagateKeywords.limit==k_limit).first()
        if item_exist:
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



'''
def save_apc_results(topic, results, during): # 保存attention&penetration对应的表
    for k, v in results.iteritems():
        mtype = k
        ts, dcount = v # dcount由五个键值对组成
        allnum = 0
        for r in dcount:
            allnum +=dcount[r]
        for r in dcount:
            domain = r
            covernum = dcount[r]
            item = AttentionCount(topic, during, ts, mtype, domain, covernum, allnum)
            item_exist = db.session.query(AttentionCount).filter(AttentionCount.topic==topic, \
                                                                 AttentionCount.range==during, \
                                                                 AttentionCount.end==ts, \
                                                                 AttentionCount.mtype==mtype, \
                                                                 AttentionCount.domain==domain).first()
            if item_exist:
                db.session.delete(item_exist)
            db.session.add(item)
        db.session.commit()


def save_qc_results(topic, topnum, allnum, during, end, mtype, uiddomain): # 保存QuicknessCount
    item = QuicknessCount(topic, during, end, mtype, uiddomain, topnum, allnum)
    item_exist = db.session.query(QuicknessCount).filter(QuicknessCount.topic==topic, \
                                                            QuicknessCount.range==during, \
                                                            QuicknessCount.end==end, \
                                                            QuicknessCount.mtype==mtype, \
                                                            QuicknessCount.domain==uiddomain).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)
    db.session.commit()


def quicknessCronTopic(topic, xapian_search_weibo, start_ts, over_ts, during=Fifteenminutes):
     if topic and topic != '':
        start_ts = int(start_ts)
        over_ts = int(over_ts)
        over_ts = ts2HourlyTime(over_ts, during)
        interval = (over_ts - start_ts) / during
        query_dict = {'$or': [],}
        topics = topic.strip().split(',')
        query_dict['$or'].append({'topics': topic})
        for i in range(interval, 0, -1): # 一个15分钟，计算出一个quickness
            begin_ts = over_ts - during * i
            end_ts = begin_ts + during
            #second_countlist = [] # 长度为900的序列，每一秒钟的微博数
            for k, v in mtype_kv.iteritems():
                query_dict['message_type'] = v
                query_dict['timestamp'] = {'$gt': begin_ts, '$lt': end_ts}
                counts, weibo_results = xapian_search_weibo.search(query=query_dict, fields=fields_list) #15分钟内的微博匹配集
                domain_ts = {} # domain_ts={domain:[ts序列]}
                for weibo_result in weibo_results():
                    uiddomain = uid2domain(weibo_result['user'])
                    try:
                        domain_ts[uiddomain].append(weibo_result['timestamp'])
                    except KeyError:
                        domain_ts[uiddomain] = [weibo_result['timestamp']]

                for r in domain_ts:
                    ts_list = domain_ts[r] # ts_list=[ts1,ts2...]
                    allnum = len(ts_list)
                    topnum = TopNum(ts_list) # TopNum 计算top n点的和 
                    save_qc_results(topic, topnum, allnum, during, end_ts, v, r) # 存入Quickness表
                        
'''                
def propagateCronTopic(topic, xapian_search_weibo, start_ts, over_ts, sort_field=SORT_FIELD, save_fields=RESP_ITER_KEYS, during=Fifteenminutes, w_limit=TOP_WEIBOS_LIMIT, k_limit=TOP_KEYWORDS_LIMIT):
    if topic and topic != '':
        start_ts = int(start_ts)
        over_ts = int(over_ts)
        over_ts = ts2HourlyTime(over_ts, during)
        interval = (over_ts - start_ts) / during

        topics = topic.strip().split(',') 
        for i in range(interval, 0, -1):
            begin_ts = over_ts - during * i
            end_ts = begin_ts + during
            mtype_dcount = {} # mtype_dcount={mtype:{domain:count}}
            mtype_kcount = {} # mtype_kcount={mtype:[terms]}
            mtype_weibo = {} # mtype_weibo={mtype:weibo}
            print begin_ts, end_ts, 'topic %s starts calculate' % topic.encode('utf-8')
            query_dict = {
                'timestamp': {'$gt': begin_ts, '$lt': end_ts},
                '$or': [],
            }
            for topic in topics:
                query_dict['$or'].append({'topics': topic}) # 由于topic目前没有数据，所以测试阶段使用text中查询topic
            for k, v in mtype_kv.iteritems():
                query_dict['message_type'] = v
                #query_dict['message_type'] = 1
                domaincount ={}
                counts,weibo_results = xapian_search_weibo.search(query=query_dict, fields=fields_list) # weibo_results是在指定时间段、topic、message_type的微博匹配集
                mset = xapian_search_weibo.search(query=query_dict, sort_by=[sort_field], \
                                                  max_offset=w_limit, mset_direct=True)
                
                
                #counts,results = xapian_search_weibo.search(query=query_dict, fileds=fields_list, sort_by=[sort_field])  
                #for i in results():
                #    if i['reposts_count'] != 0:
                #        print '----', i
                
                kcount = top_keywords(gen_mset_iter(xapian_search_weibo, mset, fields=['terms']), top=k_limit)
                top_ws = top_weibos(gen_mset_iter(xapian_search_weibo, mset, fields=fields_list), top=w_limit)
                for weibo_result in weibo_results():
                    uiddomain=uid2domain(weibo_result['user'])
                    if uiddomain:
                        try:
                            domaincount[uiddomain] += 1
                        except KeyError:
                            domaincount[uiddomain] = 1
                    else:
                        continue
                
                mtype_kcount[v] = [end_ts, kcount]
                mtype_weibo[v] = [end_ts, top_ws]
                mtype_dcount[v] = [end_ts, domaincount]
                #print mtype_dcount[v]
                #print '%s %s saved message_type domain_count' % (begin_ts, end_ts)
                #save_pc_results(topic, mtype_dcount, during) # PropagateCount表
                #save_apc_results(topic, mtype_dcount, during) # APCount表
                save_kc_results(topic, mtype_kcount, during, k_limit)
                save_ws_results(topic, mtype_weibo, during, w_limit)


def cal_topic_propagate_count_by_date(topic, datestr, duration):
    start_ts = datetime2ts(datestr)
    end_ts = start_ts + Day
    datestr = datestr.replace('-', '')
    xapian_search_weibo = getXapianWeiboByDate(datestr)
    if xapian_search_weibo:
        propagateCronTopic(topic, xapian_search_weibo, start_ts=start_ts, over_ts=end_ts, during=duration) # 原始表、Attention&Penetration表
        #quicknessCronTopic(topic, xapian_search_weibo, start_ts=start_ts, over_ts=end_ts, during=duration) # Quickness表
        #propagate_keywords(topic, xapian_search_weibo, start_ts= start_ts, over_ts=end_ts, during=duration)

def worker(topic, datestr):
    print 'topic: ', topic.encode('utf8'), 'datestr:', datestr, 'Fifteenminutes: '
    cal_topic_propagate_count_by_date(topic, datestr, Fifteenminutes)


if __name__ == '__main__':
    datestr = '2013-09-01'
    topic = u"中国"
    worker(topic,datestr)
