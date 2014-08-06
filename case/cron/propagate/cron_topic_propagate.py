# -*- coding: utf-8 -*-

import json
import redis
import datetime
from time_utils import datetime2ts, ts2HourlyTime
from dynamic_xapian_weibo import getXapianWeiboByDate, getXapianWeiboByDuration # 获取一定时间段内的微博
from config import mtype_kv, db  
from model import PropagateCount, AttentionCount, QuicknessCount # 一定时间、话题、信息类型对应的{domain:count}


Minute = 60
Fifteenminutes = 15 * 60
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24

N = 10 # top N设置---确定后放在配置文件中

fields_list=['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', 'source', 'bmiddle_pic', 'geo', 'attitudes_count', 'comments_count', 'sentiment', 'topics', 'message_type', 'terms']

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
                        
                
def propagateCronTopic(topic, xapian_search_weibo, start_ts, over_ts, during=Fifteenminutes):
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
            # print begin_ts, end_ts, 'topic %s starts calculate' % topic.encode('utf-8')
            query_dict = {
                'timestamp': {'$gt': begin_ts, '$lt': end_ts},
                '$or': [],
            }
            for topic in topics:
                query_dict['$or'].append({'text': topic}) # 由于topic目前没有数据，所以测试阶段使用text中查询topic
            for k, v in mtype_kv.iteritems():
                query_dict['message_type'] = v
                domaincount ={}
                counts,weibo_results = xapian_search_weibo.search(query=query_dict, fields=fields_list) # weibo_results是在指定时间段、topic、message_type的微博匹配集
                for weibo_result in weibo_results():
                    uiddomain=uid2domain(weibo_result['user'])
                    if uiddomain:
                        try:
                            domaincount[uiddomain] += 1
                        except KeyError:
                            domaincount[uiddomain] = 1
                    else:
                        continue
               
                mtype_dcount[v] = [end_ts, domaincount]
                #print mtype_dcount[v]
                #print '%s %s saved message_type domain_count' % (begin_ts, end_ts)
                save_pc_results(topic, mtype_dcount, during) # PropagateCount表
                save_apc_results(topic, mtype_dcount, during) # APCount表
                    
            
def cal_topic_propagate_count_by_date(topic, datestr, duration):
    start_ts = datetime2ts(datestr)
    end_ts = start_ts + Day
    datestr = datestr.replace('-', '')
    xapian_search_weibo = getXapianWeiboByDate(datestr)
    if xapian_search_weibo:
        #propagateCronTopic(topic, xapian_search_weibo, start_ts=start_ts, over_ts=end_ts, during=duration) # 原始表、Attention&Penetration表
        quicknessCronTopic(topic, xapian_search_weibo, start_ts=start_ts, over_ts=end_ts, during=duration) # Quickness表
   

def worker(topic, datestr):
    print 'topic: ', topic.encode('utf8'), 'datestr:', datestr, 'Fifteenminutes: '
    cal_topic_propagate_count_by_date(topic, datestr, Fifteenminutes)


if __name__ == '__main__':
    datestr = '2013-09-01'
    topic = u"中国"
    worker(topic,datestr)
