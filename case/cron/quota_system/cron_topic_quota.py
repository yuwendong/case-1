# -*- coding: utf-8 -*-

import json
import csv
import redis
import time
import random
from config import db, emotions_kv #, REDIS_HOST, REDIS_PORT
from time_utils import datetime2ts, ts2HourlyTime, ts2datetime
from dynamic_xapian_weibo import getXapianWeiboByDate, getXapianWeiboByDuration
from model import TopicStatus, QuotaAttention, QuotaPenetration, QuotaQuickness, QuotaSentiment, \
                  QuotaDuration, QuotaSensitivity, QuotaImportance #, QuotaTotal
# QuotaTotal该表未建，计算未知
from save_quota import save_attention_quota, save_duration_quota, save_sensitivity_quota, \
                       save_importance_quota, save_sentiment_quota, save_quickness_quota, \
                       save_penetration_quota
'''
考虑到可能会出现一个话题会针对不同时间区间进行分析。这种情况在TopicStatus中设置为不同的topic， 所以此处在每一张表中也有start_ts,end_ts
ps1:指标体系中所有指标计算结束后，要修改TopicStatus中quota_system模块对应的标识
ps2：这里的话题起止时间通过topic_status中获得
'''


Minute = 60
Fifteenminutes = 15 * 60
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24

fields_list=['_id', 'user', 'retweeted_uid', 'retweeted_mid', 'text', 'timestamp', 'reposts_count', \
             'source', 'bmiddle_pic', 'geo', 'attitudes_count', 'comments_count', 'sentiment', 'topics',\
             'message_type', 'terms']

sensitivity_list = [1, 2, 3]

domain_list = ['folk', 'media', 'opinion_leader', 'oversea', 'other']
USER_DOMAIN = 'user_domain'
REDIS_HOST = '219.224.135.48'
REDIS_PORT = 6379



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


def quota_attention(topic, xapian_search_weibo, start_ts, end_ts, save_field=fields_list):
    if topic and topic != '':
        topics = topic.strip().split(',')
    query_dict = {
        'timestamp': {'$gt':start_ts, '$lt':end_ts},
        '$or': []
        }
    for topic in topics:
        query_dict['$or'].append({'text': topic}) # 'text' just be used to test---'topic' 
    print 'query_dict:', query_dict
    domaincount = {} # domaincount = {domain1:count, domain2,count,......}

    counts, weibo_results = xapian_search_weibo.search(query=query_dict, fields=fields_list) # 返回字段要进行精简
    domain_ts = {} # domain_ts = {domain1:{ts1:frequence1,ts2:frequence2,......},domain2:{...}}
    domain_uid = {} # domain_uid = {domain1:set(uid1,uid2,...),domain2:set(uid1,uid2...),...}
    for domain in domain_list:
        domain_ts[domain] = {}
        domain_uid[domain] = set()
    # 以上，给domain_ts,domain_uid做初始化    
    #print 'weibo_results:', weibo_results
    for weibo in weibo_results():
        uiddomain = uid2domain(weibo['user'])
        ts = weibo['timestamp']
        if uiddomain:
            try:
                domaincount[uiddomain] += 1
            except KeyError:
                domaincount[uiddomain] = 1
            try:
                domain_ts[uiddomain][ts] += 1
            except:
                domain_ts[uiddomain][ts] = 1
            domain_uid[uiddomain].add(weibo['user'])
        else:
            continue
    for domain in domain_list:
        count = domaincount[domain]
        expr = 100 # 这里需要经验值得计算，此处先作为常值
        attention = float(count) / float(expr)
        if attention > 1:
            attention = 1
            
        save_attention_quota(topic, start_ts, end_ts, domain, attention)
        print 'save attention success'
        # 考虑如何利用attention部分的检索结果，计算其他指标，减少检索次数，提高速度
        quota_quickness(topic, start_ts, end_ts, domain_ts, domaincount)
        print 'save quickness success'
        # 将quickness,penetration部分的检索和attention部分的检索结合
        quota_penetration(topic, start_ts, end_ts, domain_uid)
        print 'save penetration success'

def get_domain_set():
    domain_set = {} # domain_set = {domain1:set(id1,id2,.....), domain2:set(id1,id2,....),......}
    for domain in domain_list:
        reader = csv.reader(file(domain+'.csv', 'rb'))
        uid_set = set()
        for line in reader:
            uid_set.add(line[0])

        domain_set[domain] = uid_set

    return domain_set
            
        
def quota_penetration(topic, start_ts, end_ts, domain_uid): # 另：地域渗透度已经在evolution中计算过了
    domain_set = get_domain_set()
    for domain in domain_list:
        uid_allset = domain_set[domain]
        uid_domain = domain_uid[domain]
        print 'uid_allset & uid_domain:',len(uid_allset & uid_domain)
        #print 'uid_domain:',len(uid_domain)
        penetration = float(len(uid_allset & uid_domain)) / float(len(uid_allset))

        save_penetration_quota(topic, start_ts, end_ts, domain, penetration)
    

def quota_quickness(topic, start_ts, end_ts, domain_ts, domaincount):
    for domain in domain_list:
        domain_allcount = domaincount[domain] # domain:allcount
        ts_dict = domain_ts[domain]
        sort_ts = sorted(ts_dict.iteritems(), key=lambda a:a[1], reverse=False)
        results = sort_ts[:10] # results = [(ts1, count1), (ts2,count2)......] 根据count逆序排列
        topnum =sum([count for ts, count in results])
        quickness = float(topnum) / float(domain_allcount)

        save_quickness_quota(topic, start_ts, end_ts, domain, quickness) 


def quota_sentiment(topic, xapian_search_weibo, start_ts, end_ts):
    if topic and topic != '':
        topics = topic.strip().split(',')
    query_dict = {
        'timestamp': {'$gt':start_ts, '$lt':end_ts},
        '$or':[],
        }
    for topic in topics:
        query_dict['$or'].append({'text': topic}) # just test ---topics
    sentiment_count_dict = {}
    allcount = 0
    for k, v in emotions_kv.iteritems(): 
        query_dict['sentiment'] = v
        scount, weibo_results = xapian_search_weibo.search(query=query_dict, fields=fields_list)
        sentiment_count_dict[v] = scount
        allcount += scount
    for k, v in sentiment_count_dict.iteritems():
        ratio = float(v) / float(allcount)
        save_sentiment_quota(topic, start_ts, end_ts, k, ratio)   


def quota_duration(topic, start_ts, end_ts):
    during = end_ts - start_ts
    expr_duration = 5 * Day # 获取同类型话题的持续时间的经验值，需要一个方法。这里给做常值
    duration = float(during) / float(expr_duration)
    if duration > 1:
        duration = 1

    save_duration_quota(topic, start_ts, end_ts, duration)


def quota_sensitivity(topic, start_ts, end_ts):
    for i in sensitivity_list:
        classfication = i
        score = random.randint(1,5) # score怎么算到的，需要一个方法。这里随机给在1~5分值
        save_sensitivity_quota(topic, start_ts, end_ts, classfication, score)

    
def quota_importance(topic, start_ts, end_ts):
    score = random.random() # 计算未明，先0~1的随机值
    save_importance_quota(topic, start_ts, end_ts, score)

'''该表未建，计算未知
def quota_total():
'''


def cal_topic_quotasystem_count_by_date(topic, start, end):
    #确定要查询Weibo的时间段
    start_date = ts2datetime(start)
    end_date = ts2datetime(end -1) # 若结束时间戳为2014:09:02 00:00:00,实际上还是算在9.1那一天中
    print 'start, end:', start_date, end_date
    windowsize = (end - start) / Day
    print 'windowsize:', windowsize
    if not start_date==end_date:
        windowsize += 1
    datestr_list = []
    for i in range(windowsize+1):
        time = start + i * Day
        time_date = ts2datetime(time)
        datestr_list.append(time_date.replace('-', ''))
    print 'datestr_list:', datestr_list
    xapian_search_weibo = getXapianWeiboByDuration(datestr_list) # 这里是根据时间段进行查询的
    if xapian_search_weibo:
        quota_attention(topic, xapian_search_weibo, start_ts=start, end_ts=end)
        quota_duration(topic, start_ts=start, end_ts=end)
        print 'save duration success'
        quota_sensitivity(topic, start_ts=start, end_ts=end)
        print 'save sensitivity success'
        quota_importance(topic, start_ts=start, end_ts=end)
        print 'save importance success'
        quota_sentiment(topic, xapian_search_weibo, start_ts=start, end_ts=end)
        print 'save sentiment success'
# 考虑怎么把使用数据相似性很高的合并在一起，减少检索的次数

def worker(topic, start, end):
    print 'topic: ', topic.encode('utf8'), 'start:', start, 'end:', end
    cal_topic_quotasystem_count_by_date(topic, start, end)


if __name__=='__main__':
    module = 'quota_sysytem'
    status = -1
    topic = u'中国'
    start = 1377965700
    end = 1378051200
    db_date = int(time.time()) # 入库时间
    #save_item = TopicStatus(module, status, topic, start, end, db_date)
    #db.session.add(save_item)
    #db.session.commit()
    worker(topic, start, end)
