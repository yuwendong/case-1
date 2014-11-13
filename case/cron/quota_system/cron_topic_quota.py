# -*- coding: utf-8 -*-

import sys
import json
import csv
import redis
import time
import random
from config import db, emotions_kv #, REDIS_HOST, REDIS_PORT
from config import xapian_search_user as user_search
sys.path.append('../')
from time_utils import datetime2ts, ts2HourlyTime, ts2datetime
from dynamic_xapian_weibo import getXapianWeiboByDate, getXapianWeiboByDuration, getXapianWeiboByTopic
from model import TopicStatus, QuotaAttention, QuotaAttentionExp, QuotaGeoPenetration,\
                  QuotaQuickness, QuotaSentiment, QuotaDurationExp,\
                  QuotaDuration, QuotaSensitivity, QuotaMediaImportance,\
                  QuotaImportance, ClassSensitivity, WordSensitivity, PlaceSensitivity, CoverageExp, PersonSensitivity, QuotaIndex
# QuotaTotal该表未建，计算未知
from save_quota import save_attention_quota, save_duration_quota, save_sensitivity_quota, \
                       save_importance_quota, save_sentiment_quota, save_quickness_quota, \
                       save_geo_penetration, save_media_importance_quota, save_coverage_quota, save_person_sensitivity_quota
from quotaexp import save_exp # quotaexp 初始化经验值两张表
from sensitivity_word_origin import save_sensitivity
from getkeywords import get_keywords
from quota_importance_origin import origin_quota_importance
from compute_fquota import ComputeIndex
import sys
sys.path.append('../libsvm-3.17/python/')
from sta_ad import start as ystart

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

sensitivity_list = [1, 2, 3] # 分别表示类型敏感度，词汇敏感度， 地点敏感度

domain_list = ['folk', 'media', 'opinion_leader', 'oversea', 'other']
USER_DOMAIN = 'user_domain'
REDIS_HOST = '219.224.135.48'
REDIS_PORT = 6379
SET_NAME = 'ImporMedia'

province_dict = {'34':'安徽','11':'北京', '50':'重庆', '35':'福建', '62':'甘肃', '44':'广东', '45':'广西',\
                 '52':'贵州', '46':'海南', '13':'河北', '23':'黑龙江', '41':'河南', '42':'湖北', '43':'湖南',\
                 '15':'内蒙古', '32':'江苏', '36':'江西', '22':'吉林', '21':'辽宁', '64':'宁夏', '63':'青海',\
                 '14':'山西', '37':'山东', '31':'上海', '51':'四川', '12':'天津', '54':'西藏', '65':'新疆',\
                 '53':'云南', '33':'浙江', '61':'陕西', '71':'台湾', '81':'香港', '82':'澳门',\
                 '400':'海外', '100':'其他'}

def _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=0):

    return redis.StrictRedis(host, port, db)

r = _default_redis()

def get_nad(rlist):
    flag = '1234'
    data = start(rlist, flag)
    return len(data),data


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

def get_attentionexp(topic, start_ts, end_ts): # 从QuotaAttentionExp中获取exp
    item = db.session.query(QuotaAttentionExp).filter(QuotaAttentionExp.topic==topic ,\
                                                      QuotaAttentionExp.start_ts==start_ts ,\
                                                      QuotaAttentionExp.end_ts==end_ts).first()
    exp_list = json.loads(item.exp)
    return exp_list

def get_province(uid): 
    results = user_search.search_by_id(uid, fields=['province'])
    if results:
        province = results['province']
    else:
        province = None
    
    return province

def get_nad(rlist):
    flag = '1234'
    data = ystart(rlist, flag)
    return len(data),data



def quota_attention(topic, xapian_search_weibo, start_ts, end_ts, save_field=fields_list):
    print 'topic:', topic.encode('utf8')
    if topic and topic != '':
        topics = topic.strip().split(',')
    query_dict = {
        'timestamp': {'$gt':start_ts, '$lt':end_ts},
        '$and': []
        }
    for ctopic in topics:
        query_dict['$and'].append({'topics': ctopic}) # 'text' just be used to test---'topic' 
    print 'type(ctopic):', type(ctopic)
    print 'query_dict:', query_dict
    domaincount = {} # domaincount = {domain1:count, domain2,count,......}

    counts, weibo_results = xapian_search_weibo.search(query=query_dict, fields=fields_list) # 返回字段要进行精简
    print 'counts:', counts
    results_list = []
    if counts:
        for weibo_result in weibo_results():
            results_list.append([weibo_result['_id'], weibo_result['text'].encode('utf-8')])
        scount, data_wid = get_nad(results_list)
    else:
        data_wid = []
        scount = 0
    print 'scount_new:', scount
    domain_ts = {} # domain_ts = {domain1:{ts1:frequence1,ts2:frequence2,......},domain2:{...}}

    domain_uid = set() # domain_uid = set(uid1,uid2,...) 存放参与讨论的媒体集合 
    pset = {} # pset = {province1:set1(uid), province2:set2(uid)......}存放相同城市的数量统计,使用set排除了一个用户发布多条消息的情况
    for province in province_dict:
        pset[province] = set()
    
    #print 'pset:',pset

    for domain in domain_list:
        domain_ts[domain] = {}
        #domain_uid[domain] = set()
    # 以上，给domain_ts,domain_uid做初始化    
    #print 'weibo_results:', weibo_results
    domain_all_count = 0
    domain_all_ts = {}
    for weibo in weibo_results():
        if str(weibo['_id']) in data_wid:
            uiddomain = uid2domain(weibo['user'])
            ts = weibo['timestamp']
            # uid>>province>>ccount
            province = get_province(weibo['user'])
        
            if province:
                pset[province].add(weibo['user'])
            if uiddomain:
                try:
                    domaincount[uiddomain] += 1
                except KeyError:
                    domaincount[uiddomain] = 1
                try:
                    domain_ts[uiddomain][ts] += 1
                except:
                    domain_ts[uiddomain][ts] = 1
            domain_all_count += 1
            try:
                domain_all_ts[ts] += 1
            except:
                domain_all_ts[ts] = 1
                '''
                domain_uid[uiddomain].add(weibo['user'])
                '''
                if uiddomain=='media':
                    domain_uid.add(str(weibo['user'])) # 统计参与讨论的媒体组成的集合set类型
            else:
                continue
    '''
    exp_list = get_attentionexp(topic, start_ts, end_ts) # 获取经验值字典exp_list={domain:exp}
    for domain in domain_list:
        count = domaincount[domain]
        expr = exp_list[domain] # 此处建立一张经验值表，初始值进行给给定
        attention = float(count) / float(expr)
        if attention > 1:
            attention = 1
    '''        
        #save_attention_quota(topic, start_ts, end_ts, domain, attention)
        #print 'save attention success'
        # 考虑如何利用attention部分的检索结果，计算其他指标，减少检索次数，提高速度
    
    quota_quickness(topic, start_ts, end_ts, domain_all_ts, domain_all_count)
    print 'save quickness success'
        # 将quickness,penetration部分的检索和attention部分的检索结合
        #quota_penetration(topic, start_ts, end_ts, domain_uid)
        #print 'save penetration success'
    quota_media_importance(topic, start_ts, end_ts, domain_uid)
    print 'save media_attention success'
       
    #quota_geo_penetration(topic, start_ts, end_ts, pset) # 地域渗透度的计算
    #print 'save geo_penetration success'

def get_domain_set():
    domain_set = {} # domain_set = {domain1:set(id1,id2,.....), domain2:set(id1,id2,....),......}
    for domain in domain_list:
        reader = csv.reader(file(domain+'.csv', 'rb'))
        uid_set = set()
        for line in reader:
            uid_set.add(line[0])

        domain_set[domain] = uid_set

    return domain_set

def get_media_set(): # 从redis中的set表ImporMedia中读出重要media的uid，形成set
    media_set = set() # media_set = set(id1, id2, id3......)
    media_set = r.smembers(SET_NAME)
    print 'media_set:', media_set
    # print 'len(media_set):', len(media_set), type(media_set)
    return media_set

def get_weight_dict():
    item = db.session.query(GeoWeight).first() # 该表中实际只有一条数据
    weight_dict = json.loads(item.weight_dict)
    return weight_dict


# quota_penetration弃用，改为两部分：重要媒体参与度与地域渗透度

def quota_geo_penetration(topic,start_ts, end_ts, pset): # 计算地域渗透度
    
    '''
    weight_dict = {(100000, 10000000):1, (80000, 100000):0.9, (60000, 80000):0.7, \
                   (40000, 600000):0.5, (20000, 40000):0.3, (10000,20000):0.1, (0,10000):0} 该值为默认值--所有话题均使用
    weight_dict = {(boundry_low, boundry_up):weight, } 权重和界限划分字典存在GeoWeight表，提供初始值，管理员根据具体情况在前端进行数据修改，更新
    '''
    # weight_dict = get_weight_dict()
    s=0
    pcount = {} # pcount = {province:count}
    ppenetration = {} # ppenetration = {weight:count}
    for province in province_dict:
        count = len(pset[province])
        pcount[province] = count
        '''
        for boundry in weight_dict:
            weight = weight_dict[boundry]
            if count>=boundry[0] and count<=boundry[1]:
                try:
                    ppenetration[weight] += 1
                except:
                    ppenetration[weight] = 1
        '''
    '''
    geopenetration = 0
    for weight in ppenetration:
        count = ppenetration[weight]
        geopenetration += weight * count
    '''    
    save_geo_penetration(topic, start_ts, end_ts, pcount)


def quota_media_importance(topic, start_ts, end_ts, domain_uid): # 计算重要媒体参与度 

# 建立重要媒体列表ImporMedia,某一话题中参与讨论的重要媒体数为L,参与讨论的所有媒体数为N,重要媒体参与度L/N
    media_set = domain_uid
    impor_media_set = get_media_set()
    print 'len(media_set):',len(media_set)
    print 'media_uid:', media_set 
    L = len(media_set & impor_media_set)
    N = len(media_set)
    print 'L,N:', L, N
    media_importance = float(L) / float(N)

    save_media_importance_quota(topic, start_ts, end_ts, media_importance) # 在save_quota中进行补充
    

def quota_quickness(topic, start_ts, end_ts, domain_all_ts, domain_all_count):
    '''
    for domain in domain_list:
        domain_allcount = domaincount[domain] # domain:allcount
        ts_dict = domain_ts[domain]
        sort_ts = sorted(ts_dict.iteritems(), key=lambda a:a[1], reverse=False)
        results = sort_ts[:10] # results = [(ts1, count1), (ts2,count2)......] 根据count逆序排列
        topnum =sum([count for ts, count in results])
        quickness = float(topnum) / float(domain_allcount)

        save_quickness_quota(topic, start_ts, end_ts, domain, quickness) 
    '''
    ts_dict = domain_all_ts
    sort_ts = sorted(ts_dict.iteritems(), key=lambda a:a[1], reverse=False)
    windowsize = (end_ts - start_ts) / Day
    rank = 10 * windowsize
    results =sort_ts[: rank]
    topnum = sum([count for ts,count in results])
    quickness_l = float(topnum) / float(domain_all_count)
    print 'quickness_l:', quickness_l
    quickness_exp = 0.0115 # waiting to recorrect
    quickness_quota = quickness_l / quickness_exp
    print 'quickness_quota:', quickness_quota
    if quickness_quota > 1:
        quickness_quota = 1
    save_quickness_quota(topic, start_ts, end_ts, 'all', quickness_quota)
    

def quota_sentiment(topic, xapian_search_weibo, start_ts, end_ts):
    if topic and topic != '':
        topics = topic.strip().split(',')
    query_dict = {
        'timestamp': {'$gt':start_ts, '$lt':end_ts},
        '$and':[],
        }
    for ctopic in topics:
        query_dict['$and'].append({'topics': ctopic}) # just test ---topics
    sentiment_count_dict = {}
    allcount = 0
    for k, v in emotions_kv.iteritems(): 
        query_dict['sentiment'] = v
        scount, weibo_results = xapian_search_weibo.search(query=query_dict, fields=fields_list)
        results_list = []
        if scount:
            for weibo_result in weibo_results():
                results_list.append([weibo_result['_id'], weibo_result['text'].encode('utf-8')])
            scount_new, data_wid = get_nad(results_list)
        else:
            scount_new = 0
        sentiment_count_dict[v] = scount_new
        allcount += scount_new
    print 'sentiment_count_dict:', sentiment_count_dict
    emotion_ratio_dict = {}
    emotion_ratio_dict['sad'] = float(sentiment_count_dict[3])/float(allcount)
    emotion_ratio_dict['angry'] = float(sentiment_count_dict[2]) / float(allcount)

    save_sentiment_quota(topic, start_ts, end_ts, emotion_ratio_dict) # 需要修改sentiment_quota表结构

def get_durationexp(topic, start_ts, end_ts): # 从QuotaDurationExp获取exp
    item = db.session.query(QuotaDurationExp).filter(QuotaDurationExp.topic==topic ,\
                                                     QuotaDurationExp.start_ts==start_ts ,\
                                                     QuotaDurationExp.end_ts==end_ts).first()
    exp_duration = item.exp
    return exp_duration

def quota_duration(topic, start_ts, end_ts):
    during = end_ts - start_ts
    expr_duration = get_durationexp(topic, start_ts, end_ts) # 获取同类型话题的持续时间的经验值，需要一个方法。这里给做常值，建立一张表存储，可以通过管理员进行修改
    duration = float(during) / float(expr_duration)
    if duration > 1:
        duration = 1

    save_duration_quota(topic, start_ts, end_ts, duration)


def quota_sensitivity(topic, start_ts, end_ts):
    '''
    关键词中敏感词的个数L，关键词个数N，敏感度L/N
    敏感词set1, 关键词set2, min(1,len(set1&set2)/len(set2))
    '''
    limit = 50 
    keywords_set = get_keywords(topic, start_ts, end_ts, limit) # 获得前limit的keywords_set 
    class_result = db.session.query(ClassSensitivity).filter(ClassSensitivity.topic==topic ,\
                                                             ClassSensitivity.start_ts==start_ts ,\
                                                             ClassSensitivity.end_ts==end_ts).first()
    class_sensitivity_set = set(json.loads(class_result.words))
    L = len(class_sensitivity_set & keywords_set)
    ratio_class = float(L) / float(limit)
    classfication = 1
    if ratio_class < 1:
        save_sensitivity_quota(topic, start_ts, end_ts, classfication, ratio_class)
    else:
        ratio_class = 1
        save_sensitivity_quota(topic, start_ts, end_ts, classfication, ratio_class)
        
    word_result = db.session.query(WordSensitivity).filter(WordSensitivity.topic==topic ,\
                                                         WordSensitivity.start_ts==start_ts ,\
                                                         WordSensitivity.end_ts==end_ts).first()
    word_sensitivity_set = set(json.loads(word_result.words))
    L = len(word_sensitivity_set & keywords_set)
    ratio_word = float(L) / float(limit)
    classfication = 2
    if ratio_word < 1:
        save_sensitivity_quota(topic, start_ts, end_ts, classfication, ratio_word)
    else:
        ratio_class = 1
        save_sensitivity_quota(topic, start_ts, end_ts, classfication, ratio_word)
        
    place_result = db.session.query(PlaceSensitivity).filter(PlaceSensitivity.topic==topic ,\
                                                             PlaceSensitivity.start_ts==start_ts ,\
                                                             PlaceSensitivity.end_ts==end_ts).first()
    place_sensitivity_set = set(json.loads(place_result.words))
    L = len(place_sensitivity_set & keywords_set)
    ratio_place = float(L) / float(limit)
    classfication = 3
    if ratio_place < 1:
        save_sensitivity_quota(topic, start_ts, end_ts, classfication , ratio_place)
    else:
        ratio_class = 1
        save_sensitivity_quota(topic, start_ts, end_ts, classfication, ratio_place)
    
def quota_importance(topic, start_ts, end_ts): # 此处仅为给表进行初始化。实际使用时，将通过前端页面进行处理
    
    origin_quota_importance(topic, start_ts, end_ts)

def quota_coverage(topic, xapian_search_topic, start_ts, end_ts):
    counts, results = xapian_search_topic.search(fields=['user'])
    user_set = set()
    for result in results():
        uid = result['user']
        user_set.add(uid)
    L = len(user_set)
    exp_item = db.session.query(CoverageExp).filter(CoverageExp.topic==topic ,\
                                               CoverageExp.start_ts==start_ts ,\
                                               CoverageExp.end_ts==end_ts).first()
    exp = exp_item.coverage_exp
    quota_coverage = float(L) / float(exp)
    if quota_coverage > 1:
        quota_coverage = 1
    save_coverage_quota(topic, start_ts, end_ts, quota_coverage)

def quota_person_sensitivity(topic, xapian_search_topic, start_ts, end_ts):
    person_result = db.session.query(PersonSensitivity).filter(PersonSensitivity.topic==topic ,\
                                                               PersonSensitivity.start_ts==start_ts ,\
                                                               PersonSensitivity.end_ts==end_ts).first()
    if person_result:
        sensitivity_person_set =set(json.loads(person_result.person))
    else:
        sensitivity_person_set = set()
    counts, results = xapian_search_topic.search(fields=['user'])
    user_set = set()
    for result in results():
        uid = result['user']
        user_set.add(uid)
    L = len(user_set & sensitivity_person_set)
    N = len(user_set)
    ps = float(L) / float(N)
    save_person_sensitivity_quota(topic, start_ts, end_ts, ps)

def cal_topic_quotasystem_count_by_date(topic, start, end):
    #确定要查询Weibo的时间段
    start_date = ts2datetime(start)
    end_date = ts2datetime(end) # 若结束时间戳为2014:09:02 00:00:00,实际上还是算在9.1那一天中
    print 'start, end:', start_date, end_date
    windowsize = (end - start) / Day
    print 'windowsize:', windowsize
    datestr_list = []
    for i in range(windowsize):
        time = start + i * Day
        time_date = ts2datetime(time)
        datestr_list.append(time_date.replace('-', ''))
    print 'datestr_list:', datestr_list
    xapian_search_weibo = getXapianWeiboByDuration(datestr_list) # 这里是根据时间段进行查询的
    xapian_search_topic = getXapianWeiboByTopic(topic) # 直接查topic建立的索引
    if xapian_search_weibo:
        print '******start_compute'
        quota_attention(topic, xapian_search_weibo, start_ts=start, end_ts=end)
        quota_duration(topic, start_ts=start, end_ts=end)
        print 'save duration success'
        quota_sensitivity(topic, start_ts=start, end_ts=end)
        print 'save sensitivity success'
        quota_importance(topic, start_ts=start, end_ts=end)
        print 'save importance success'
        quota_sentiment(topic, xapian_search_weibo, start_ts=start, end_ts=end)
        print 'save sentiment success'
        quota_coverage(topic, xapian_search_topic, start_ts=start, end_ts=end) # 覆盖度计算
        print 'save coverage success'
        quota_person_sensitivity(topic, xapian_search_topic, start_ts=start, end_ts=end) # 敏感人物参与度
        print 'save person_sensitivity success'
# 考虑怎么把使用数据相似性很高的合并在一起，减少检索的次数

def worker(topic, start, end):
    print 'topic: ', topic.encode('utf8'), 'start:', start, 'end:', end
    cal_topic_quotasystem_count_by_date(topic, start, end)


if __name__=='__main__':
    module = 'quota_sysytem'
    status = -1
    topic = u'东盟,博览会'
    start = datetime2ts('2013-09-02')
    end = datetime2ts('2013-09-05') + Day
    db_date = int(time.time()) # 入库时间
    
    save_item = TopicStatus(module, status, topic, start, end, db_date)
    db.session.add(save_item)
    db.session.commit()
    attention_exp = {'folk':100, 'media':100, 'other':100, 'opinion_leader':100, 'oversea':100} # 此处仅对经验值进行初始化，需要管理员根据具体情况进行修改
    duration_exp = 5 * Day
    coverage_exp = 3000
    save_exp(topic, start, end, attention_exp, duration_exp, coverage_exp) # 给关注度经验值和持续度经验值默认值
    save_sensitivity(topic, start, end) # 给类型敏感词表、词汇敏感词表、地点敏感词表进行初始化----三张表中均为每个话题一条记录
    worker(topic, start, end)
    
    ComputeIndex(topic, start, end)
