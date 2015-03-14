# -*- coding: utf-8 -*-
import json
import redis
import os
import time
import random
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from SSDB import SSDB
from case.extensions import db
from case.global_config import SSDB_HOST, SSDB_PORT
from case.model import TopicStatus, TopicIdentification, DegreeCentralityUser ,\
                       BetweenessCentralityUser, ClosenessCentralityUser ,\
                       DsTopicIdentification, TsRank, DsDegreeCentralityUser ,\
                       DsBetweenessCentralityUser, DsClosenessCentralityUser, TrendKeyUser
from case.time_utils import ts2datetime, datetime2ts, window2time
from case.global_config import xapian_search_user as user_search


def acquire_topic_id(name, start_ts, end_ts, module="identify"):
    item = db.session.query(TopicStatus).filter_by(topic=name, start=start_ts, end=end_ts, module=module).first()
    if not item: # 若item不存在TopicStatus说明是新插入的，进行插入-----完成通过前端用户提交的要计算的topic数据
        item = TopicStatus(module, -1, topic, start_ts, end_ts, int(time.time()))
        db.session.add(item)
        db.session.commit()
    return item.id


def acquire_topic_name(tid, module='identify'): # 将topic_id转化成对应的topic_name，以便映射到user
    item = db.session.query(TopicStatus).filter_by(id=tid).first()
    if not item:
        return None
    return item.topic


def acquire_user_by_id(uid):
    result = user_search.search_by_id(int(uid), fields=['name', 'location', 'followers_count', 'friends_count'])
    user = {}
    if result:
        user['name'] = result['name']
        user['location'] = result['location']
        user['count1'] = result['followers_count']
        user['count2'] = result['friends_count']
            
    return user


def user_status(uid):  # 暂时未做处理，原文件中涉及到knowledgelist，此处无
    return 1


def is_in_trash_list(uid):
    '''之后增加判断是否为垃圾用户的判断
    '''
    return False

REDIS_HOST = '219.224.135.48'
REDIS_PORT = 6379
USER_DOMAIN = 'user_domain'

def _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=0):
    return redis.StrictRedis(host, port, db)

r = _default_redis()

def uid2domain(user):
    domain_str = r.hget(USER_DOMAIN, str(user))
    if not domain_str:
        return 'other'

    domain_dict = json.loads(domain_str)
    domain = domain_dict['v3']

    return domain


def read_topic_rank_results(topic, top_n, method, date, window, domain):
    data = []
    count = 0
    items = db.session.query(TopicIdentification).filter_by(topic=topic, identifyMethod=method, \
                                                            identifyWindow=window, identifyDate=date).order_by(TopicIdentification.rank.asc())
    print items.count()

    if items.count():
        for item in items:
            if count >= top_n:
                break
            rank = item.rank
            uid = item.userId    
            item_domain = uid2domain(uid)
            if item_domain != domain and domain != "all":
                continue
            else:
                user = acquire_user_by_id_v2(uid)
                pr = item.pr
                item_dc = db.session.query(DegreeCentralityUser).filter(DegreeCentralityUser.topic==topic ,\
                                                                    DegreeCentralityUser.userid==uid).first()
                if item_dc:
                    dc = item_dc.dc
                else:
                    continue
                item_bc = db.session.query(BetweenessCentralityUser).filter(BetweenessCentralityUser.topic==topic ,\
                                                                        BetweenessCentralityUser.userid==uid).first()
                if item_bc:
                    bc = item_bc.bc
                else:
                    continue

                item_cc = db.session.query(ClosenessCentralityUser).filter(ClosenessCentralityUser.topic==topic ,\
                                                                       ClosenessCentralityUser.userid==uid).first()
                if item_cc:
                    cc = item_cc.cc
                else:
                    continue
                if not user:
                    name = u'未知'
                    location = u'未知'
                    count1 = u'未知'
                    count2 = u'未知'
                else:
                    name = user['name']
                    location = user['location']
                    count1 = user['count1']
                    count2 = user['count2']
                #read from external knowledge database
                #status = user_status(uid)
                row = (rank, uid, name, location, count1, count2, pr, dc, bc, cc, domain)
                count += 1
                data.append(row)
    return data


def read_ds_topic_rank_results(topic, top_n, date, windowsize, domain, method):
    data = []
    count = 0
    items = db.session.query(DsTopicIdentification).filter_by(topic=topic, identifyWindow=windowsize ,\
                                                              identifyMethod=method, identifyDate=date).order_by(DsTopicIdentification.rank.asc())
    print 'len(items):', items.count()
    if not items.count():
        return None
    else:
        for item in items:
            if count >= top_n:
                break
            rank = item.rank
            uid = item.userId
            item_domain = uid2domain(uid)
            if item_domain != domain and domain != 'all':
                continue
            else:
                user = acquire_user_by_id_v2(uid)
                pr = float(item.pr)
 
                item_dc = db.session.query(DsDegreeCentralityUser).filter(DsDegreeCentralityUser.topic==topic ,\
                                                                          DsDegreeCentralityUser.date==date ,\
                                                                          DsDegreeCentralityUser.windowsize==windowsize ,\
                                                                          DsDegreeCentralityUser.userid==uid).first()
                if item_dc:
                    dc = item_dc.dc
                else:
                    continue

                item_bc = db.session.query(DsBetweenessCentralityUser).filter(DsBetweenessCentralityUser.topic==topic ,\
                                                                              DsBetweenessCentralityUser.date==date ,\
                                                                              DsBetweenessCentralityUser.windowsize==windowsize ,\
                                                                              DsBetweenessCentralityUser.userid==uid).first()
                if item_bc:
                    bc = item_bc.bc
                else:
                    continue
                item_cc = db.session.query(DsClosenessCentralityUser).filter(DsClosenessCentralityUser.topic==topic ,\
                                                                             DsClosenessCentralityUser.date==date ,\
                                                                             DsClosenessCentralityUser.windowsize==windowsize ,\
                                                                             DsClosenessCentralityUser.userid==uid).first()

                if item_cc:
                    cc = item_cc.cc
                else:
                    continue
                if not user:
                    name = u'未知'
                    location = u'未知'
                    count1 = u'未知'
                    count2 = u'未知'
                else:
                    name = user['name']
                    location = user['location']
                    count1 = user['count1']
                    count2 = user['count2']
            
                row = (rank, uid, name, location, count1, count2, pr, dc, bc, cc, domain)
                count += 1
                data.append(row)


    return data


def read_degree_centrality_rank(topic, top_n, date, window, domain):
    data = []
    count = 0
    items = db.session.query(DegreeCentralityUser).filter_by(topic=topic,  \
                                                            windowsize=window, date=date).order_by(DegreeCentralityUser.rank.asc())
    print 'items_count:', items.count()  
    if items.count():
        for item in items:
            if count >= top_n:
                break
            rank = item.rank
            uid = item.userid
            item_domain = uid2domain(uid)
            if item_domain != domain and domain != 'all':
                continue
            else:
                count += 1 
                user = acquire_user_by_id_v2(uid)
                dc = item.dc
                item_pr = db.session.query(TopicIdentification).filter(TopicIdentification.topic==topic ,\
                                                                       TopicIdentification.userId==uid).first()
                pr = item_pr.pr
                item_bc = db.session.query(BetweenessCentralityUser).filter(BetweenessCentralityUser.topic==topic ,\
                                                                            BetweenessCentralityUser.userid==uid).first()
                bc = item_bc.bc
                item_cc = db.session.query(ClosenessCentralityUser).filter(ClosenessCentralityUser.topic==topic ,\
                                                                           ClosenessCentralityUser.userid==uid).first()

                cc = item_cc.cc
                if not user:
                    name = u'未知'
                    location = u'未知'
                    count1 = u'未知'
                    count2 = u'未知'
                else:
                    name = user['name']
                    location = user['location']
                    count1 = user['count1']
                    count2 = user['count2']

                #read from external knowledge database
                #status = user_status(uid)
                row = (rank, uid, name, location, count1, count2, pr, dc, bc, cc, domain)
                data.append(row)

    return data
                

def read_degree_centrality_rank(topic, top_n, date, window, domain):
    data = []
    count = 0
    items = db.session.query(DegreeCentralityUser).filter_by(topic=topic,  \
                                                            windowsize=window, date=date).order_by(DegreeCentralityUser.rank.asc())
    print 'items_count:', items.count()  
    if items.count():
        for item in items:
            if count >= top_n:
                break
            rank = item.rank
            uid = item.userid
            item_domain = uid2domain(uid)
            if item_domain != domain and domain != 'all':
                continue
            else:
                count += 1
                user = acquire_user_by_id_v2(uid)

                dc = item.dc
                item_pr = db.session.query(TopicIdentification).filter(TopicIdentification.topic==topic ,\
                                                                       TopicIdentification.userId==uid).first()
                pr = item_pr.pr
                item_bc = db.session.query(BetweenessCentralityUser).filter(BetweenessCentralityUser.topic==topic ,\
                                                                            BetweenessCentralityUser.userid==uid).first()
                bc = item_bc.bc

                item_cc = db.session.query(ClosenessCentralityUser).filter(ClosenessCentralityUser.topic==topic ,\
                                                                           ClosenessCentralityUser.userid==uid).first()
                cc = item_cc.cc
                if not user:
                    name = u'未知'
                    location = u'未知'
                    count1 = u'未知'
                    count2 = u'未知'
                else:
                    name = user['name']
                    location = user['location']
                    count1 = user['count1']
                    count2 = user['count2']
                #read from external knowledge database
                #status = user_status(uid)
                row = (rank, uid, name, location, count1, count2, pr, dc, bc, cc, domain)
                data.append(row)

    return data


def read_betweeness_centrality_rank(topic, top_n, date, windowsize, domain):
    data = []
    count = 0
    items = db.session.query(BetweenessCentralityUser).filter_by(topic=topic,  \
                                                            windowsize=windowsize, date=date).order_by(BetweenessCentralityUser.rank.asc())

    print 'items_count:', items.count()  
    if items.count():
        for item in items:
            if count >= top_n:
                break
            rank = item.rank
            uid = item.userid
            item_domain = uid2domain(uid)
            if item_domain != domain and domain != 'all':
                continue
            else:
                count += 1
                user = acquire_user_by_id_v2(uid)

                bc = item.bc
                item_pr = db.session.query(TopicIdentification).filter(TopicIdentification.topic==topic ,\
                                                                       TopicIdentification.userId==uid).first()
                pr = item_pr.pr
                item_dc = db.session.query(DegreeCentralityUser).filter(DegreeCentralityUser.topic==topic ,\
                                                                        DegreeCentralityUser.userid==uid).first()
                dc = item_dc.dc

                item_cc = db.session.query(ClosenessCentralityUser).filter(ClosenessCentralityUser.topic==topic ,\
                                                                           ClosenessCentralityUser.userid==uid).first()
                cc = item_cc.cc
                if not user:
                    name = u'未知'
                    location = u'未知'
                    count1 = u'未知'
                    count2 = u'未知'
                else:
                    name = user['name']
                    location = user['location']
                    count1 = user['count1']
                    count2 = user['count2']
                #read from external knowledge database
                #status = user_status(uid)
                row = (rank, uid, name, location, count1, count2, pr, dc, bc, cc, domain)
                data.append(row)
    return data


def read_ds_degree_centrality_rank(topic, top_n, date, windowsize, domain):
    data = []
    count = 0
    items = db.session.query(DsDegreeCentralityUser).filter_by(topic=topic, windowsize=windowsize ,\
                                                               date=date).order_by(DsDegreeCentralityUser.rank.asc())
    print 'len(items):', items.count()
    if not items.count():
        return None
    else:
        for item in items:
            if count >= top_n:
                break
            uid = item.userid
            item_domain = uid2domain(uid)
            if item_domain != domain and domain != 'all':
                continue
            else:
                count += 1
                rank = item.rank
                dc = item.dc
                user = acquire_user_by_id_v2(uid)
                item_pr = db.session.query(DsTopicIdentification).filter(DsTopicIdentification.topic==topic ,\
                                                                         DsTopicIdentification.identifyDate==date ,\
                                                                         DsTopicIdentification.identifyWindow==windowsize ,\
                                                                         DsTopicIdentification.userId==uid).first()
                pr = float(item_pr.pr)
 
                item_dc = db.session.query(DsDegreeCentralityUser).filter(DsDegreeCentralityUser.topic==topic ,\
                                                                          DsDegreeCentralityUser.date==date ,\
                                                                          DsDegreeCentralityUser.windowsize==windowsize ,\
                                                                          DsDegreeCentralityUser.userid==uid).first()
                dc = item_dc.dc
                item_bc = db.session.query(DsBetweenessCentralityUser).filter(DsBetweenessCentralityUser.topic==topic ,\
                                                                              DsBetweenessCentralityUser.date==date ,\
                                                                              DsBetweenessCentralityUser.windowsize==windowsize ,\
                                                                              DsBetweenessCentralityUser.userid==uid).first()
                bc = item_bc.bc
                item_cc = db.session.query(DsClosenessCentralityUser).filter(DsClosenessCentralityUser.topic==topic ,\
                                                                             DsClosenessCentralityUser.date==date ,\
                                                                             DsClosenessCentralityUser.windowsize==windowsize ,\
                                                                             DsClosenessCentralityUser.userid==uid).first()
                cc =item_cc.cc
                if not user:
                    name = u'未知'
                    location = u'未知'
                    count1 = u'未知'
                    count2 = u'未知'
                else:
                    name = user['name']
                    location = user['location']
                    count1 = user['count1']
                    count2 = user['count2']

                row = (rank, uid, name, location , count1, count2, pr, dc, bc, cc, domain)

                data.append(row)

    return data

def read_betweeness_centrality_rank(topic, top_n, date, windowsize, domain):
    data = []
    count =0
    items = db.session.query(BetweenessCentralityUser).filter_by(topic=topic,  \
                                                            windowsize=windowsize, date=date).order_by(BetweenessCentralityUser.rank.asc())
    print 'items_count:', items.count()  
    if items.count():
        for item in items:
            if count >= top_n:
                break
            rank = item.rank
            uid = item.userid
            item_domain = uid2domain(uid)
            if item_domain != domain and domain != 'all':
                continue
            else:
                count += 1
                user = acquire_user_by_id_v2(uid)
                bc = item.bc
                item_pr = db.session.query(TopicIdentification).filter(TopicIdentification.topic==topic ,\
                                                                       TopicIdentification.userId==uid).first()
                pr = item_pr.pr
                item_dc = db.session.query(DegreeCentralityUser).filter(DegreeCentralityUser.topic==topic ,\
                                                                        DegreeCentralityUser.userid==uid).first()
                dc = item_dc.dc
                item_cc = db.session.query(ClosenessCentralityUser).filter(ClosenessCentralityUser.topic==topic ,\
                                                                           ClosenessCentralityUser.userid==uid).first()
                cc = item_cc.cc
                if not user:
                    name = u'未知'
                    location = u'未知'
                    count1 = u'未知'
                    count2 = u'未知'
                else:
                    name = user['name']
                    location = user['location']
                    count1 = user['count1']
                    count2 = user['count2']
                #read from external knowledge database
            
                row = (rank, uid, name, location, count1, count2, pr, dc, bc, cc, domain)
                data.append(row)
    return data

def read_ds_betweeness_centrality_rank(topic, top_n, date, windowsize, domain):
    data = []
    count = 0
    items = db.session.query(DsBetweenessCentralityUser).filter_by(topic=topic, windowsize=windowsize ,\
                                                                   date=date).order_by(DsBetweenessCentralityUser.rank.asc())
    print 'items_count:', items.count()
    if not items.count():
        return None
    else:
        for item in items:
            if count >= top_n:
                break
            uid = item.userid
            item_domain = uid2domain(uid)
            if item_domain != domain and domain != 'all':
                continue
            else:
                count += 1
                bc = item.bc
                rank = item.rank
                user = acquire_user_by_id_v2(uid)
                item_pr = db.session.query(DsTopicIdentification).filter(DsTopicIdentification.topic==topic ,\
                                                                         DsTopicIdentification.identifyDate==date ,\
                                                                         DsTopicIdentification.identifyWindow==windowsize ,\
                                                                         DsTopicIdentification.userId==uid).first()
                pr = float(item_pr.pr)
                item_dc = db.session.query(DsDegreeCentralityUser).filter(DsDegreeCentralityUser.topic==topic ,\
                                                                          DsDegreeCentralityUser.date==date ,\
                                                                          DsDegreeCentralityUser.windowsize==windowsize ,\
                                                                          DsDegreeCentralityUser.userid==uid).first()
                dc = item_dc.dc
                item_cc = db.session.query(DsClosenessCentralityUser).filter(DsDegreeCentralityUser.topic==topic ,\
                                                                             DsDegreeCentralityUser.date==date ,\
                                                                             DsDegreeCentralityUser.windowsize==windowsize ,\
                                                                             DsDegreeCentralityUser.userid==uid).first()
                cc = item_cc.cc
                if not user:
                    name = u'未知'
                    location = u'未知'
                    count1 = u'未知'
                    count2 = u'未知'
                else:
                    name = user['name']
                    location = user['location']
                    count1 = user['count1']
                    count2 = user['count2']

                row = (rank, uid, name, location, count1, count2, pr, dc, bc, cc, domain)
                data.append(row)

    return data

def read_closeness_centrality_rank(topic, top_n, date, windowsize, domain):
    data = []
    count = 0
    items = db.session.query(ClosenessCentralityUser).filter_by(topic=topic,  \
                                                            windowsize=windowsize, date=date).order_by(ClosenessCentralityUser.rank.asc())
    print 'items_count:', items.count()  
    if items.count():
        for item in items:
            if count >= top_n:
                break
            rank = item.rank
            uid = item.userid
            item_domain = uid2domain(uid)
            if item_domain != domain and domain != 'all':
                continue
            else:
                count += 1
                user = acquire_user_by_id_v2(uid)
                cc = item.cc
                item_pr = db.session.query(TopicIdentification).filter(TopicIdentification.topic==topic ,\
                                                                       TopicIdentification.userId==uid).first()
                pr = item_pr.pr
                item_dc = db.session.query(DegreeCentralityUser).filter(DegreeCentralityUser.topic==topic ,\
                                                                        DegreeCentralityUser.userid==uid).first()
                dc = item_dc.dc
                item_bc = db.session.query(BetweenessCentralityUser).filter(BetweenessCentralityUser.topic==topic ,\
                                                                            BetweenessCentralityUser.userid==uid).first()
                bc = item_bc.bc
                if not user:
                    name = u'未知'
                    location = u'未知'
                    count1 = u'未知'
                    count2 = u'未知'
                else:
                    name = user['name']
                    location = user['location']
                    count1 = user['count1']
                    count2 = user['count2']
                #read from external knowledge database
                #status = user_status(uid)
                row = (rank, uid, name, location, count1, count2, pr, dc, bc, cc, domain)
                data.append(row)

    return data


def read_ds_closeness_centrality_rank(topic, top_n, date, windowsize, domain):
    data = []
    count  = 0
    items = db.session.query(DsClosenessCentralityUser).filter_by(topic=topic, date=date,\
                                                                  windowsize=windowsize).order_by(DsClosenessCentralityUser.rank.asc())
    print 'len(items):', items.count()
    if not items.count():
        return None
    else:
        for item in items:
            if count >= top_n:
                break
            uid = item.userid
            item_domain = uid2domain(uid)
            if item_domain != domain and domain != 'all':
                continue
            else:
                count += 1 
                rank = item.rank
                cc = item.cc
                user = acquire_user_by_id_v2(uid)
                item_pr = db.session.query(DsTopicIdentification).filter(DsTopicIdentification.topic==topic ,\
                                                                         DsTopicIdentification.identifyDate==date ,\
                                                                         DsTopicIdentification.identifyWindow==windowsize ,\
                                                                         DsTopicIdentification.userId==uid).first()
                pr = float(item_pr.pr)
                item_dc = db.session.query(DsDegreeCentralityUser).filter(DsDegreeCentralityUser.topic==topic ,\
                                                                          DsDegreeCentralityUser.date==date ,\
                                                                          DsDegreeCentralityUser.windowsize==windowsize ,\
                                                                          DsDegreeCentralityUser.userid==uid).first()
                dc = item_dc.dc
                item_bc = db.session.query(DsBetweenessCentralityUser).filter(DsBetweenessCentralityUser.topic==topic ,\
                                                                              DsBetweenessCentralityUser.date==date ,\
                                                                              DsBetweenessCentralityUser.windowsize==windowsize ,\
                                                                              DsBetweenessCentralityUser.userid==uid).first()
                bc = item_bc.bc
                if not user:
                    name = u'未知'
                    location = u'未知'
                    count1 = u'未知'
                    count2 = u'未知'
                else:
                    name = user['name']
                    location = user['location']
                    count1 = user['count1']
                    count2 = user['count2']
                row = (rank, uid, name, location, count1, count2, pr, dc, bc, cc, domain)
                data.append(row)

    return data
                

def acquire_user_by_id_v2(uid):
    result = user_search.search_by_id(int(uid), fields=['name', 'location', 'followers_count', 'friends_count'])
    user = {}
    if result:
        user['name'] = result['name']
        user['location'] = result['location']
        user['count1'] = result['followers_count']
        user['count2'] = result['friends_count']
            
    return user


def save_rank_results(sorted_uids, identifyRange, method, date, window, topicname):
    '''存放pagerank的计算结果
    '''
    data = []
    rank = 1
    count = 0
    exist_items = db.session.query(TopicIdentification).filter(TopicIdentification.topic==topicname, \
                                                               TopicIdentification.identifyWindow==window, \
                                                               TopicIdentification.identifyDate==date, \
                                                               TopicIdentification.identifyMethod==method).all()
    for item in exist_items:
        db.session.delete(item)
    db.session.commit()
    for uid in sorted_uids:
        user = acquire_user_by_id(uid)
        if not user:
            continue
        count = count + 1
        name = user['name']
        location = user['location']
        count1 = user['count1']
        count2 = user['count2']
        #read from external knowledge database
        status = user_status(uid)
        row = (rank, uid, name, location, count1, count2, status)
        data.append(row)
        if identifyRange == 'topic':
            item = TopicIdentification(topicname, rank, uid, date, window, method)
        else:
            break
        db.session.add(item)
        rank += 1
    db.session.commit()
    print 'done'
    return data


def read_key_users(date, window, topicname, top_n=10):
    '''获取一个话题中的关键用户--即读取pagerank的计算结果
    '''
    items = db.session.query(TopicIdentification).filter_by(topic=topicname, identifyWindow=window, identifyDate=date).order_by(TopicIdentification.rank.asc()).limit(top_n)
    users = []
    if items.count():
        for item in items:
            uid = item.userId
            users.append(uid)
    return users


def _utf8_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, 'utf-8')


def save_gexf_results(topic, identifyDate, identifyWindow, identifyGexf):
    '''保存gexf图数据到SSDB
    '''
    #try:
    ssdb = SSDB(SSDB_HOST, SSDB_PORT)
    if ssdb:
        print 'ssdb yes'
    else:
        print 'ssdb no'
    key = _utf8_unicode(topic) + '_' + str(identifyDate) + '_' + str(identifyWindow)
    print 'key', key
    key = str(key)
    value = identifyGexf
    result = ssdb.request('set',[key,value])
    if result.code == 'ok':
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),'save success',  _utf8_unicode(topic), str(identifyDate), str(identifyWindow)
    else:
        print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'Gexf save into SSDB failed'

    #except Exception, e:
    #    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'SSDB ERROR'
        
def weiboinfo2url(uid, _mid):
    mid_str =  mid2str(_mid)
    return "http://weibo.com/{uid}/{mid}".format(uid=uid, mid=mid_str)

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
 
def base62_encode(num, alphabet=ALPHABET):
    """Encode a number in Base X
 
    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)
 
def base62_decode(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number
 
    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0
 
    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1
 
    return num

def url_to_mid(url):
    '''
    >>> url_to_mid('z0JH2lOMb')
    3501756485200075L
    >>> url_to_mid('z0Ijpwgk7')
    3501703397689247L
    >>> url_to_mid('z0IgABdSn')
    3501701648871479L
    >>> url_to_mid('z08AUBmUe')
    3500330408906190L
    >>> url_to_mid('z06qL6b28')
    3500247231472384L
    >>> url_to_mid('yCtxn8IXR')
    3491700092079471L
    >>> url_to_mid('yAt1n2xRa')
    3486913690606804L
    '''
    url = str(url)[::-1]
    size = len(url) / 4 if len(url) % 4 == 0 else len(url) / 4 + 1
    result = []
    for i in range(size):
        s = url[i * 4: (i + 1) * 4][::-1]
        s = str(base62_decode(str(s)))
        s_len = len(s)
        if i < size - 1 and s_len < 7:
            s = (7 - s_len) * '0' + s
        result.append(s)
    result.reverse()
    return int(''.join(result))


def mid_to_url(midint):
    '''
    >>> mid_to_url(3501756485200075)
    'z0JH2lOMb'
    >>> mid_to_url(3501703397689247)
    'z0Ijpwgk7'
    >>> mid_to_url(3501701648871479)
    'z0IgABdSn'
    >>> mid_to_url(3500330408906190)
    'z08AUBmUe'
    >>> mid_to_url(3500247231472384)
    'z06qL6b28'
    >>> mid_to_url(3491700092079471)
    'yCtxn8IXR'
    >>> mid_to_url(3486913690606804)
    'yAt1n2xRa'
    '''
    midint = str(midint)[::-1]
    size = len(midint) / 7 if len(midint) % 7 == 0 else len(midint) / 7 + 1
    result = []
    for i in range(size):
        s = midint[i * 7: (i + 1) * 7][::-1]
        s = base62_encode(int(s))
        s_len = len(s)
        if i < size - 1 and len(s) < 4:
            s = '0' * (4 - s_len) + s
        result.append(s)
    result.reverse()
    return ''.join(result)


def mid2str(mid):
    mid = str(mid)
    print 'mid:', mid
    s1 = base62_encode(int(mid[:2]))
    s2 = base62_encode(int(mid[2:9]))
    try:
        s3 = base62_encode(int(mid[9:16]))
    except:
        s3 = ''
    return s1+s2+s3
